# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"Объединяет все математические преобразования видео"

import threading
from math import *
import copy
from collections import namedtuple
import logging
import time
import os.path
import json
import numpy as np
import wx

from . import view
from . import geom
Preview = view.Preview
FAIL_STOP = view.ViewerWorkingThread.FAIL_STOP
from .c_part.transform_frame import transform_frame
from ..grapher import power_spec
from ..common.my_encoding_tools import U
from ..base_gui.mvf_aux_classes import Selection


class Processing(Preview):
    """
    Класс, который объединяет всю обработку видео.
    
     loader
       |   коррекция перспективы
       V
    [t, y, x]  self.first_array_tyx
       |   fft
       V
    [f, y, x]  second_array_fyx
       |   нормализация
       |   fft 2d
       V   уменьшаем размер до output_fft_size
    [f, ky,kx] third_array_fkk
       |   
       +--->  копия спектра  express_spectrum_  (если output_spec_mode == 0)
       + - - - - - - - - - - - - - - - - - - - - - - - - --> второй фильтр
       |   фильтры всякие
       |        
       +--->  копия спектра  express_spectrum_  (если output_spec_mode > 0)
       |
       |
      [ ]  third_array_fkk                                  array33_fkk
       |
       |  ifft        
       V
    [t, ky,kx]                                                 [  ]
    output1_array_tkk                                  output2_array_tkk
        |                                                       |
        |            ------ до сюда _begin_new_pack ------      |
        |                                                       |
        |              еще один, для соседней пачки             |
        |                             |                         |
    [t, ky,kx]                    [t, ky,kx]                   [  ]  [  ]
    preproc_pack1_flt1_tkk   preproc_pack2_flt1_tkk    preproc_pack1_flt2_tkk
           |                                           preproc_pack2_flt2_tkk
           |
           |  ifft 2d для конкретного кадра,
           |  с дополнением 0-ми до размера окна
           |  _update_right_view_act()
           V
         [y, x]                                                  [  ]
         
    full_size_frame_flt1_yx  полноразмерный массив      full_size_frame_flt2_yx
                             для текущего кадра, для текущего зума
                             (храним последний созданный массив,
                             чтобы быстро скролить)
                 
        img_ready       подготовлена для след. кадра
        img_showing     отрисовывается прям сейчас
          
    
    Переменные:
    .state_: PREINIT_STATE, RUNNING_STATE, DEAD_STATE
             доступ снаружи через state()
    .in_long_processing (bool)
    .state_lock
    .pack_len (int)
    .output_fft_size ( (int, int) ) : по пространству
    .first_array_tyx (np.ndarray dtype=np.complex128)
    .preproc_pack1_flt1_tkk
    .preproc_pack1_flt2_tkk
    .preproc_pack2_flt1_tkk
    .preproc_pack2_flt2_tkk
    .start_of_preproc_pack1
    .start_of_preproc_pack2
    .second_filter_enabled (bool)
    .transform_frame_args (_TransformFrameArgs)
    .lx(float) , .ly(float) : размер области в метрах, доступен в RUNNING_STATE
    .time_wnd (np.ndarray)
    .space_wnd_x (np.ndarray)
    .space_wnd_y (np.ndarray)
    .space_wnd_enabled (bool)
    .crop_output (bool)
    .express_spectrum_ (PowerSpec) :  квадрат спектра в 3D, сохраненный после
                                      последнего расчета; защищен state_lock;
                                      доступ через express_spectrum()
    .express_spectrum_interval ( list [int, int] )
    .output_spec_mode (int)
    .max_freq_of_output_spec
    .fps
    .overlap (bool)
    .frames_count
    .cur_frame_num (int)
    .prev_frame_num (int)
    .stop_update_view (bool)
    .b_panel (PanelParam)
    .full_size_ifft_in_kk (np.ndarray)
    .full_size_frame_flt1_yx (np.ndarray)
    .full_size_frame_flt2_yx (np.ndarray)
    .full_size_for_frame (int)
    .full_size_for_zoom (float)
    .img_ready (wx.Image)
    .img_ready_array_yxc (nd.array): имеет один буффер с img_ready
    .img_ready_for_frame (int)
    .img_ready_for_panel_params (PanelParam)
    .img_ready_footer_text (str)
    .img_showing (wx.Image)
    .img_showing_array_yxc (nd.array)
    .img_showing_lock
    .render_mode: копия из config, кт. поддержуватся актуальной в _take_view_param
                  защишено view_param_lock
    .filter1_color_lim
    .auto_color_lim
    .psd_norm  (float)        доступен в RUNNING_STAT
    .movie_norm  (float)      доступен в RUNNING_STAT
    .equalize_in_space (bool)
    .equalize_in_space_for_freqs ( sequence (float, float) )
    .output_scale_formula (4 floats) : px, qx, py, qy
                                       x'[пикселы] = px + qx * x [метры]
                                       защищено view_param_lock
    .moving_window_enabled (True/False)
    .moving_window_ref_rect (sequence):  x1, y1, x2, y2 в реальных координатах
    .moving_window_velocity (sequence):  vx, vy         в м/с
    .moving_window_ref_time (float) :    момент времени, когда окно занивает ref_rect
    .moving_window_hold (True / False):  компенсировать движение
    """
    PREINIT_STATE = 0
    RUNNING_STATE = 1
    DEAD_STATE = 2
    
    def __init__(self, *arg, **kwarg):
        "См. аргументы Preview.__init__"
        Preview.__init__(self, *arg, **kwarg)
        
        self.state_ = self.PREINIT_STATE
        self.in_long_processing = False
        self.state_lock = threading.Lock()
        
        config = self.main_video_frame.config
        self.pack_len = config.pack_len
        
        if config.active_area_num < 0:
            state_ = self.DEAD_STATE
            self._report_error("No processing area is selected")
            return
        aa = config.areas_list[config.active_area_num]
        self.first_array_tyx = np.ndarray((self.pack_len,
                                           aa.input_fft_size[1],
                                           aa.input_fft_size[0]),
                                          dtype = np.float64)
        temp_coord = [int(x) for x in aa.coord]
        # Аргументы для transform_frame, которые идут после массивов,
        # начиная с color depth
        self.transform_frame_args = _TransformFrameArgs(
            a = config.proj_coef.a,
            b = config.proj_coef.b,
            c = config.proj_coef.c,
            x1 = temp_coord[0],  # будет измененно после получения первого кадра
            y1 = temp_coord[1],
            x2 = temp_coord[2],
            y2 = temp_coord[3])
        
        self.lx = 1
        self.ly = 1
        
        # окна
        self.overlap = config.overlap
        if config.overlap or config.force_time_wnd_if_no_overlap:
            N = self.pack_len
            nnn = np.arange(0, N, dtype=np.float64)
            self.time_wnd = (0.5 - 0.5 * np.cos(2 * pi * nnn / N))
            self.time_wnd = self.time_wnd.reshape((N, 1, 1))
        else:
            self.time_wnd = np.ones((self.pack_len, 1, 1))
        sp_wnd_x_shp = (1, 1, aa.input_fft_size[0])
        sp_wnd_y_shp = (1, aa.input_fft_size[1], 1)
        if config.space_wnd:
            N = aa.input_fft_size[0]
            nnn = np.arange(0, N, dtype=np.float64)
            self.space_wnd_x = np.sin(nnn * pi / (N - 1))
            self.space_wnd_x = self.space_wnd_x.reshape(sp_wnd_x_shp)
            N = aa.input_fft_size[1]
            nnn = np.arange(0, N, dtype=np.float64)
            self.space_wnd_y = np.sin(nnn * pi / (N - 1))
            self.space_wnd_y = self.space_wnd_y.reshape(sp_wnd_y_shp)
            self.crop_output = True
        else:
            self.space_wnd_x = np.ones(sp_wnd_x_shp)
            self.space_wnd_y = np.ones(sp_wnd_y_shp)
            self.crop_output = False
        self.space_wnd_enabled = config.space_wnd
        # если moving_window_enbled, то space_wnd_x и _y быдут изменены
        # при первом вызове _apply_moving_window
        self.output_fft_size = aa.output_fft_size
        
        self.express_spectrum_ = power_spec.PowerSpec()
        self.express_spectrum_interval = [0, 1]
        self.output_spec_mode = config.output_spec_mode
        self.max_freq_of_output_spec = config.valid_max_freq()
        self.fps = config.fps
        self.frames_count = config.frames_count
        
        self.second_filter_enabled = False
        self.preproc_pack1_flt1_tkk = np.ndarray((1,1,1), dtype=np.complex128)
        self.preproc_pack1_flt2_tkk = np.ndarray((1,1,1), dtype=np.complex128)
        self.preproc_pack2_flt1_tkk = np.ndarray((1,1,1), dtype=np.complex128)
        self.preproc_pack2_flt2_tkk = np.ndarray((1,1,1), dtype=np.complex128)
        self.start_of_preproc_pack1 = -1
        self.start_of_preproc_pack2 = -1
        self.cur_frame_num = 0
        self.prev_frame_num = -1

        self.stop_update_view = False
        self.b_panel = view.PanelParam()
        self.full_size_ifft_in_kk = np.ndarray((1,1), dtype=np.complex128)
        self.full_size_frame_flt1_yx = np.ndarray((1,1))
        self.full_size_frame_flt2_yx = np.ndarray((1,1))
        self.full_size_for_frame = -1
        self.full_size_for_zoom = 1.0
        self.img_ready = wx.EmptyImage()
        self.img_showing = wx.EmptyImage()
        self.img_ready_array_yxc = np.ndarray((1,1,3), dtype=np.uint8)
        self.img_showing_array_yxc = np.ndarray((1,1,3), dtype=np.uint8)
            # полноценно иницилизируется в _update_right_view_act
        self.img_ready_for_frame = -1
        self.img_ready_for_panel_params = view.PanelParam()
        self.img_ready_footer_text = ''
        self.img_showing_lock = threading.Lock()

        # заданные здесь значения смысла особого не имеют, т.к. будут переписаны
        # из конфика при первом вызове take_view_param
        self.render_mode = 'filter1'
        self.filter1_color_lim = (-1.0, 1.0)
        self.auto_color_lim = False
        
        self.psd_norm = 1
        self.movie_norm = 1
        
        self.equalize_in_space = config.equalize_in_space
        self.equalize_in_space_for_freqs = config.equalize_in_space_for_freqs
        
        self.output_scale_formula = (0., 1., 0., 1.)

        self.moving_window_enabled = config.moving_window_enabled
        self.moving_window_ref_rect = copy.deepcopy(config.moving_window_ref_rect)
        self.moving_window_velocity = copy.deepcopy(config.moving_window_velocity)
        self.moving_window_ref_time = config.moving_window_ref_time
        self.moving_window_hold = config.moving_window_hold
        
        #.....
        
        self.goto_frame(kwarg['start_with_frame'])


    def is_processing(self):
        return True


    def state(self):
        self.state_lock.acquire()
        rv = self.state_
        self.state_lock.release()
        return rv
    
    
    def _set_dead_state(self):
        self.state_lock.acquire()
        self.state_ = self.DEAD_STATE
        self.state_lock.release()

    
    def _enqueue_task(self, task):
        "см. Preview"
        Preview._enqueue_task(self, task)
        if not self.working_thread.is_alive():
            self._set_dead_state()
   
    
    def _stop_working_thread(self):
        "см. Preview"
        Preview._stop_working_thread(self)
        self._set_dead_state()
    
    
    def _goto_frame_act(self, num):
        "Вызывается из рабочего потока; см. Preview"
        try:
            self.stop_update_view = True
            rv = Preview._goto_frame_act(self, num)
            # if rv is not None: raise GoToFrameFailed()
            if rv is not None: return rv  # признак ошибки
            
            if not self.overlap:
                self._check_and_call_begin_new_pack_no_overlap(num)
            else:            
                # Проверяем подготовлены ли у нас нужные пачки кадров,
                # чтобы num оказывался на перекрытии двух пачек
                half_pack_len = self.pack_len // 2
                back_pack_start = num - (num % half_pack_len)
                front_pack_start = back_pack_start - half_pack_len
                all_ok = (front_pack_start == self.start_of_preproc_pack1) and\
                    (self.start_of_preproc_pack1 >= 0)
                all_ok = (back_pack_start == self.start_of_preproc_pack2) and \
                    (self.start_of_preproc_pack2 >= 0) and all_ok
                if not all_ok:
                    logging.debug("_goto_frame_act: need to load more packs, "
                                  "front_pack_start %d, back_pack_start %d",
                                  front_pack_start, back_pack_start)
                    # может нужно поменять пачки местами
                    if (front_pack_start == self.start_of_preproc_pack2) or \
                        (back_pack_start == self.start_of_preproc_pack1):
                        temp = self.preproc_pack1_flt1_tkk
                        temp_s = self.start_of_preproc_pack1
                        self.preproc_pack1_flt1_tkk = self.preproc_pack2_flt1_tkk
                        self.start_of_preproc_pack1 = self.start_of_preproc_pack2
                        self.preproc_pack2_flt1_tkk = temp
                        self.start_of_preproc_pack2 = temp_s
                        temp = self.preproc_pack1_flt2_tkk
                        self.preproc_pack1_flt2_tkk = self.preproc_pack2_flt2_tkk
                        self.preproc_pack2_flt2_tkk = temp
                    # запускаем подготовку пачек
                    if (front_pack_start != self.start_of_preproc_pack1) or \
                        (self.start_of_preproc_pack1 < 0):
                        if (front_pack_start >= 0):
                            out1, out2 = self._begin_new_pack(front_pack_start)
                            self.preproc_pack1_flt1_tkk = out1
                            self.preproc_pack1_flt2_tkk = out2
                            self.start_of_preproc_pack1 = front_pack_start
                            front_pack_exists = True
                        else:
                            front_pack_exists = False
                    else:
                        front_pack_exists = True
                    if (back_pack_start != self.start_of_preproc_pack2) or \
                        (self.start_of_preproc_pack2 < 0):
                        if (back_pack_start + self.pack_len < 
                              self.frames_count):
                            out1, out2 = self._begin_new_pack(back_pack_start)
                            self.preproc_pack2_flt1_tkk = out1
                            self.preproc_pack2_flt2_tkk = out2
                            self.start_of_preproc_pack2 = back_pack_start
                            back_pack_exists = True
                        else:
                            back_pack_exists = False
                    else:
                        back_pack_exists = True
                    # Зануляем пачки, которые выходят за границы обработки
                    if not front_pack_exists:
                        self.preproc_pack1_flt1_tkk = np.zeros(
                            shape = self.preproc_pack2_flt1_tkk.shape,
                            dtype = np.complex128)
                        if self.second_filter_enabled:
                            self.preproc_pack1_flt2_tkk = np.zeros(
                                shape = self.preproc_pack2_flt2_tkk.shape,
                                dtype = np.complex128)
                        self.start_of_preproc_pack1 = front_pack_start
                    if not back_pack_exists:
                        self.preproc_pack2_flt1_tkk = np.zeros(
                            shape = self.preproc_pack1_flt1_tkk.shape,
                            dtype = np.complex128)
                        if self.second_filter_enabled:
                            self.preproc_pack2_flt2_tkk = np.zeros(
                                shape = self.preproc_pack1_flt2_tkk.shape,
                                dtype = np.complex128)
                        self.start_of_preproc_pack2 = back_pack_start
            
            self.cur_frame_num = num
            self.stop_update_view = False
            self._update_view_act()

        except GoToFrameFailed:
            self._set_dead_state()
            return FAIL_STOP
    

    def _check_and_call_begin_new_pack_no_overlap(self, num):
        logging.error('No overlap is not supported')
        pass  #TODO

    
    def _begin_new_pack(self, first_frame_in_pack):
        """
        Обработка в начале каждой пачки
        Аргументы:
          first_frame_in_pack -- номер первого кадра в пачке
        Возвращает: (ndarray, ndarray) или (ndarray, None)
        Исключения: GoToFrameFailed
        """
        logging.debug('_begin_new_pack, first_frame_in_pack = %d',
                      first_frame_in_pack)
        self.state_lock.acquire()
        self.in_long_processing = True
        first_frame = (self.state_ == self.PREINIT_STATE)
        self.state_lock.release()
        wx.CallAfter(self.main_video_frame.hourglass, 'b')
        
        # loader -> first_array_tyx
        logging.debug('size of first_array_tyx is %0.0fM' 
                       % (self.first_array_tyx.size * 8 * 1e-6))
        for n in range(0, self.pack_len):
            try:
                full_frame_num = n + first_frame_in_pack + self.frame_num_ofs
                img = self.loader.send(full_frame_num)
            except view.loading.LoadingError as err:
                self._report_loading_error(err)
                raise GoToFrameFailed()
         
            if first_frame:
                trpz = geom.trapezoid_inside_rectangle(
                    rect = self.transform_frame_args[3:],
                    proj_coef = self.transform_frame_args[0:3],
                    img_size = (img.GetWidth(), img.GetHeight()))
                trpz_fix = [int(x) for x in trpz]
                ttt = _TransformFrameArgs(
                    a = self.transform_frame_args.a,
                    b = self.transform_frame_args.b,
                    c = self.transform_frame_args.c,
                    x1 = trpz_fix[0],
                    y1 = trpz_fix[1],
                    x2 = trpz_fix[4],
                    y2 = trpz_fix[5])
                self.transform_frame_args = ttt

            buf = img.GetDataBuffer()
            shp = (img.GetHeight(), img.GetWidth(), 3)
            src_array = np.frombuffer(buf, np.uint8).reshape(shp)
            rv = transform_frame(self.first_array_tyx[n, :, :],
                                 src_array,
                                 *self.transform_frame_args)

            if first_frame:            
                first_frame = False
                self.lx = rv.Lx
                self.ly = rv.Ly
                rv = self._calc_norm_coefficients()
                self.psd_norm = rv[0]
                self.movie_norm = rv[1]
            
            if (n % 10) == 0:
                text = U("%d / %d (%0.0fM) loading and transform of the perspective view"
                         % (n,
                            self.pack_len,
                            self.first_array_tyx.size * 8 * 1e-6))
                wx.CallAfter(lambda:
                    self.main_video_frame.b_footer_static_text.SetLabel(text))
                
        logging.debug('all images are read into first_array_tyx')
        wx.CallAfter(lambda:
            self.main_video_frame.b_footer_static_text.SetLabel("FFT pass 1 of 2)"))
        
        # вычисляем средний уровень и вычитаем
        mean_level = np.mean(self.first_array_tyx[0, :, :])
        self.first_array_tyx -= mean_level
        
        # first_array_tyx -> second_array_fyx
        self.first_array_tyx *= self.time_wnd
        self._apply_moving_window(first_frame)
        second_array_fyx = np.fft.rfft(self.first_array_tyx, axis = 0)

        logging.debug('size of second_array_fyx is %0.0fM' 
                       % (second_array_fyx.size * 16 * 1e-6))

        wx.CallAfter(lambda:
            self.main_video_frame.b_footer_static_text.SetLabel("FFT pass 2 of 2"))

        if self.equalize_in_space:
            df = self.fps / (1.0 * self.pack_len)
            nf1 = round(self.equalize_in_space_for_freqs[0] / df)
            nf2 = round(self.equalize_in_space_for_freqs[1] / df)
            nf1 = max(nf1, 0)
            nf2 = min(nf2, second_array_fyx.shape[0] - 1)
#            my_std = np.std(self.first_array_tyx, 0)
            if nf2 - nf1 > 1:
               my_std2 =  np.sum(
                   np.abs(second_array_fyx[(nf1+1):nf2, :, :])**2,
                   0)
               my_std2 += np.abs(second_array_fyx[nf1, :, :])**2 * 0.5
               my_std2 += np.abs(second_array_fyx[nf2, :, :])**2 * 0.5
               my_std2 *= (1.0 / (nf2 - nf1 + 1))
               my_std2 = np.sqrt(my_std)
            else:
                logging.warning('bad values in equalize_in_space_for_freqs')
                my_std2 = np.ones((second_array_fyx.shape[1],
                                   second_array_fyx.shape[2]))
            mean_std2 = np.mean(my_std2)
            inv_std = np.sqrt(mean_std2 * my_std2) / (my_std2 + mean_std2 * 1e-3)
            for nf in range(0, second_array_fyx.shape[0]):
                second_array_fyx[nf, :, :] *= inv_std

        # second_array_fyx -> third_array_fkk
        if not self.moving_window_enabled:
            second_array_fyx *= self.space_wnd_x
            second_array_fyx *= self.space_wnd_y

        third_array_fkk_large = np.fft.fft2(second_array_fyx)

        del(second_array_fyx)
        logging.debug('size of third_array_fkk_large is %0.0fM' 
                       % (third_array_fkk_large.size * 16 * 1e-6))

        large_shape = third_array_fkk_large.shape
        output_fft_size = self.output_fft_size
        third_array_fkk = np.ndarray((large_shape[0],
                                      output_fft_size[1],
                                      output_fft_size[0]),
                                     dtype = np.complex_)
        to_x = [[output_fft_size[0] // 2, output_fft_size[0]],
                [0, output_fft_size[0] // 2]]
        to_y = [[output_fft_size[1] // 2, output_fft_size[1]],
                [0, output_fft_size[1] // 2]]
        from_x = [[0, output_fft_size[0] // 2],
                  [large_shape[2] - output_fft_size[0] // 2, large_shape[2]]]
        from_y = [[0, output_fft_size[1] // 2],
                  [large_shape[1] - output_fft_size[1] // 2, large_shape[1]]]
        for nx in range(0,2):
            for ny in range(0,2):
                third_array_fkk[:,
                                to_y[ny][0]:to_y[ny][1],
                                to_x[nx][0]:to_x[nx][1]] = \
                    third_array_fkk_large[:,
                                from_y[ny][0]:from_y[ny][1],
                                from_x[nx][0]:from_x[nx][1]]
        del(third_array_fkk_large)
        logging.debug('size of third_array_fkk is %0.0fM' 
                       % (third_array_fkk.size * 16 * 1e-6))

        if self.output_spec_mode == 0:
            t1 = (first_frame_in_pack + self.frame_num_ofs) / (self.fps * 1.0)
            t2 = t1 + self.pack_len / (self.fps * 1.0)
            self._set_express_spectrum(third_array_fkk, [t1, t2])
        
        # <<<< фильтрация 
        # еще будем хранить нефильтрованный массив, чтобы быстро менять параметры 
        # фильтра и сразу видеть результат в ГУИ
        array33_fkk = None  # array33_fkk создаем, если надо
        
        if self.output_spec_mode == 1:
            self._set_express_spectrum(third_array_fkk)
        if self.output_spec_mode == 2:
            if self.second_filter_enabled:
                self._set_express_spectrum(array33_fkk)
            else:
                self._report_error("You have not configured the second filter."
                                   "Nothing to display.")
                raise GoToFrameFailed()

        # ifft:  third_array_fkk -> output1_array_tkk,  
        #        array33_fkk -> output2_array_tkk
        shp = third_array_fkk.shape
        ifft_in_expand = np.ndarray((shp[0] * 2 - 2, shp[1], shp[2]),
                                        dtype = np.complex128)
        pipelines_count = [1, 2][self.second_filter_enabled]
        output1_array_tkk = None 
        output2_array_tkk = None
        for npipeline in range(0, pipelines_count):
            wx.CallAfter(lambda:
                self.main_video_frame.b_footer_static_text.SetLabel(
                    "FFT (%d)" % (npipeline+2)))
            if npipeline == 0:
                ifft_in = third_array_fkk
            else:
                ifft_in = array33_fkk
            ifft_in_expand[:, 0, :].fill(0.)
            ifft_in_expand[:, :, 0].fill(0.)
            ifft_in_expand[:shp[0], 1:, 1:] = ifft_in[:, 1:, 1:]
            ifft_in_expand[(shp[0]-1):, 1:, 1:] = \
                np.conj(ifft_in[:0:-1, :0:-1, :0:-1])

            ifft_out = np.fft.ifft(ifft_in_expand, axis = 0)

            if npipeline == 0:
                output1_array_tkk = ifft_out
            else:
                output2_array_tkk = ifft_out
        del(ifft_in_expand)

        self.state_lock.acquire()
        self.in_long_processing = False
        if self.state_ == self.PREINIT_STATE:
            self.state_ = self.RUNNING_STATE
        self.state_lock.release()
        logging.debug('_begin_new_pack is finished')
        wx.CallAfter(lambda:
            self.main_video_frame.b_footer_static_text.SetLabel(""))
        
        return (output1_array_tkk, output2_array_tkk)
        
    
    def _update_right_view_act(self, advance = False, advance_frame_num = 0):
        """
        Отрисоква одного обработанного кадра под текущий размер окна и зум
        Вызывается из рабочего потока.
        Если advance == True, то это мы заранее готовим следующий кадр, 
        без отрисовки в форме.
        """
        if self.state() != self.RUNNING_STATE:
            return  # NB можно крестик на экране нарисовать
                
        #забираем данные с конкурентным доступом
        self.view_param_lock.acquire()
        b_panel = copy.deepcopy(self.b_panel)
        render_mode = self.render_mode
        filter1_color_lim = self.filter1_color_lim
        auto_color_lim = self.auto_color_lim
        self.view_param_lock.release()

        # при зуме 1, одна точка выхода БПФ по x становится одним пикселем
        # h,w - размер всего развернутого полотна для отображения
        spec_shape = self.preproc_pack1_flt1_tkk.shape
        coef = self.ly / self.lx
        w = int( spec_shape[2] * b_panel.zoom )
        w = (w // 2) * 2
        h = int( w * coef)
        h = (h // 2) * 2
        
        if advance:
            cur_frame_num = advance_frame_num
        else:
            cur_frame_num = self.cur_frame_num
            # может быть мы уже заранее подготовили именно этот кадр
            if cur_frame_num == self.img_ready_for_frame and \
              view.panels_are_equal(self.img_ready_for_panel_param, b_panel):
                self._call_display_image_b()
                self._update_right_view_act_in_advance()
                return
        
        full_size_frame_is_actual = \
            (self.full_size_for_frame == cur_frame_num) and \
            (self.full_size_for_zoom == b_panel.zoom)
        if not full_size_frame_is_actual:
            # ifft по пространству
            if (self.full_size_ifft_in_kk.shape[0] != h) or \
              (self.full_size_ifft_in_kk.shape[1] != w):
                self.full_size_ifft_in_kk = np.ndarray((h, w),
                                                       dtype = np.complex128)
            self.full_size_ifft_in_kk.fill(0.)
            self.full_size_frame_flt1_yx = None
            self.full_size_frame_flt2_yx = None
            range_ky = min(h, spec_shape[1]) // 2
            range_kx = min(w, spec_shape[2]) // 2
            zero_kx_src = spec_shape[2] // 2
            zero_ky_src = spec_shape[1] // 2
            pipelines_count = [1,2][self.second_filter_enabled]
            for npipeline in range(0, pipelines_count):
                nt = cur_frame_num - self.start_of_preproc_pack1
                nt = int(nt) # <--- BUG
                src = [self.preproc_pack1_flt1_tkk,
                       self.preproc_pack1_flt2_tkk] [npipeline]
#                logging.debug(repr(nt) + ' ' + repr(zero_ky_src) + ' ' + repr(range_ky) + 
#                              ' ' + repr(zero_kx_src) + ' ' + repr(range_kx))   # DEBUG
                self.full_size_ifft_in_kk[
                        0 : range_ky,
                        0 : range_kx] =\
                    src[nt,
                        zero_ky_src : (zero_ky_src + range_ky),
                        zero_kx_src : (zero_kx_src + range_kx)]
                self.full_size_ifft_in_kk[
                        (h - range_ky) : h,
                        0 : range_kx] =\
                    src[nt,
                        (zero_ky_src - range_ky) : zero_ky_src,
                        zero_kx_src : (zero_kx_src + range_kx)]
                self.full_size_ifft_in_kk[
                        (h - range_ky) : h,
                        (w - range_kx) : w] =\
                    src[nt,
                        (zero_ky_src - range_ky) : zero_ky_src,
                        (zero_kx_src - range_kx) : zero_kx_src]
                self.full_size_ifft_in_kk[
                        0 : range_ky,
                        (w - range_kx) : w] =\
                    src[nt,
                        zero_ky_src : (zero_ky_src + range_ky),
                        (zero_kx_src - range_kx) : zero_kx_src]

                if self.overlap:
                    nt = cur_frame_num - self.start_of_preproc_pack2
                    nt = int(nt)  # <-- BUG 2
                    src = [self.preproc_pack2_flt1_tkk,
                           self.preproc_pack2_flt2_tkk] [npipeline]
                    self.full_size_ifft_in_kk[
                            0 : range_ky,
                            0 : range_kx] +=\
                        src[nt,
                            zero_ky_src : (zero_ky_src + range_ky),
                            zero_kx_src : (zero_kx_src + range_kx)]
                    self.full_size_ifft_in_kk[
                            (h - range_ky) : h,
                            0 : range_kx] +=\
                        src[nt,
                            (zero_ky_src - range_ky) : zero_ky_src,
                            zero_kx_src : (zero_kx_src + range_kx)]
                    self.full_size_ifft_in_kk[
                            (h - range_ky) : h,
                            (w - range_kx) : w] +=\
                        src[nt,
                            (zero_ky_src - range_ky) : zero_ky_src,
                            (zero_kx_src - range_kx) : zero_kx_src]
                    self.full_size_ifft_in_kk[
                            0 : range_ky,
                            (w - range_kx) : w] +=\
                        src[nt,
                            zero_ky_src : (zero_ky_src + range_ky),
                            (zero_kx_src - range_kx) : zero_kx_src]

                full_size_ifft_out_yx = np.fft.ifft2(self.full_size_ifft_in_kk).real
                full_size_ifft_out_yx *= \
                    self.movie_norm * full_size_ifft_out_yx.shape[0] * \
                    full_size_ifft_out_yx.shape[1]
                
                if npipeline == 0:
                    self.full_size_frame_flt1_yx = np.copy(full_size_ifft_out_yx)
                else:
                    self.full_size_frame_flt2_yx = np.copy(full_size_ifft_out_yx)
                full_size_ifft_out_yx = None
            self.full_size_for_frame = cur_frame_num
            self.full_size_for_zoom = b_panel.zoom

        # >>> огибающая как опция              --> на этапе с фильтрами
                
        # Рендер
        # привязка wx.Image к массиву
        ws, hs = b_panel.size
        old_shp = self.img_ready_array_yxc.shape
        if (old_shp[0] != hs) or (old_shp[1] != ws) or \
          (old_shp[0] * old_shp[1] == 1):
            self.img_ready_array_yxc = np.ndarray((hs, ws, 3), np.uint8)
            self.img_ready = wx.ImageFromBuffer(
                ws, hs, memoryview(self.img_ready_array_yxc))
        self.img_ready_array_yxc.fill(192)
        self.img_ready_footer_text = '%dx%d' % (w,h)

        auto_m = np.amin(self.full_size_frame_flt1_yx)  # диапазон данных
        auto_M = np.amax(self.full_size_frame_flt1_yx)
        m = 0  # колорбар
        M = 1
        data1_painted = False

        # Привязка полного массива к общему виду
        # позиция ЛВ угла картинки на чистом белом поле (ниже будет изменяться)
        pos_x = -b_panel.pos[0]
        pos_y = -b_panel.pos[1]
        # размер растянутой картинки
        src_size_x = w
        src_size_y = h
        # размер панели
        dst_size_x = b_panel.size[0]
        dst_size_y = b_panel.size[1]
        
        # для обрезки слева, сверху
        if pos_x < 0:
            crop_start_x = -pos_x            
            pos_x = 0
        else:
            crop_start_x = 0
        crop_size_x = src_size_x - crop_start_x
        if pos_y < 0:
            crop_start_y = -pos_y
            pos_y = 0
        else:
            crop_start_y = 0
        crop_size_y = src_size_y - crop_start_y
        # для обрезки справа, снизу
        if crop_size_x + pos_x > dst_size_x:
            crop_size_x = dst_size_x - pos_x
        if crop_size_y + pos_y > dst_size_y:
            crop_size_y = dst_size_y - pos_y
        
        empty_range = (crop_size_x <= 0 or crop_size_y <= 0 or 
                      crop_start_x > self.full_size_frame_flt1_yx.shape[1] or 
                      crop_start_y > self.full_size_frame_flt1_yx.shape[0])
        if not empty_range:
            dst_yxc = self.img_ready_array_yxc[pos_y : (pos_y + crop_size_y),
                                               pos_x : (pos_x + crop_size_x),
                                               :]
            
            if render_mode == "filter1":
                # простейшее отображение (и пока реализовано только оно)
                if auto_color_lim:
                    m = auto_m
                    M = auto_M
                else:
                    m, M = filter1_color_lim
                color_scale_coef =  1.0 / max(M-m, 1e-6)
                if crop_start_y == 0:
                    data_yx = self.full_size_frame_flt1_yx[
                        -crop_size_y:,
                        crop_start_x:(crop_start_x + crop_size_x)]
                else:
                    data_yx = self.full_size_frame_flt1_yx[
                        (-crop_start_y -crop_size_y):-crop_start_y,
                        crop_start_x:(crop_start_x + crop_size_x)]
                for ny in range(0, dst_yxc.shape[0]):
                    ny_src = data_yx.shape[0] - ny - 1;
                    dst_yxc[ny,:,0] = (data_yx[ny_src, :] - m) * 255 * color_scale_coef
                    nnn = np.nonzero(data_yx[ny_src, :] < m)
                    dst_yxc[ny, nnn, 0] = 0
                    nnn = np.nonzero(data_yx[ny_src, :] > M)
                    dst_yxc[ny, nnn, 0] = 255
                dst_yxc[:, :, 1] = dst_yxc[:, :, 0]
                dst_yxc[:, :, 2] = dst_yxc[:, :, 0]
                data1_painted = True
                
        # подпись
        nice_format = lambda lim1, lim2: ['%e', '%0.3f'] [
            max(abs(lim1), abs(lim2)) > 1e-3 ]
        self.img_ready_footer_text += (" | colorbar min,max: "
            + nice_format(m, M) + "," + nice_format(m,M) ) % (m, M)
        if data1_painted:
            self.img_ready_footer_text += (" | data1 min,max: " 
                + nice_format(auto_m, auto_M) + "," + nice_format(auto_m, auto_M)
                ) % (auto_m, auto_M)

        # self.ouput_scale_formula
        px = -b_panel.pos[0] + w/2
        qx = w * 1.0 / self.lx
        py = -b_panel.pos[1] + h/2
        qy = -qx
        self.view_param_lock.acquire()
        self.output_scale_formula = (px, qx, py, qy)
        self.view_param_lock.release()
        
        self.img_ready_for_frame = cur_frame_num
        self.img_ready_for_panel_param = copy.deepcopy(b_panel)
        if not advance:
            self._call_display_image_b()
            self._update_right_view_act_in_advance()

    
    def _call_display_image_b(self):
        """
        img_ready -> img_showing -> display_image
        После вызова в img_ready уже нет старых данных. И в него сразу можно
        писать новые данные, т.к. оно не используется ГУИ потком.
        """
        self.img_showing_lock.acquire()
        ttt = self.img_showing
        self.img_showing = self.img_ready
        self.img_ready = ttt
        ttt = self.img_showing_array_yxc
        self.img_showing_array_yxc = self.img_ready_array_yxc
        self.img_ready_array_yxc = ttt
        self.img_ready_for_frame = -1
        self.img_showing_lock.release()
        
        # отмеченные точки
        px, qx, py, qy = self.output_scale_formula
        if self.sel_data.mode == Selection.SINGLE_POINT_B:
            if self.sel_data.sel_item is None:
                sel_points = []
            else:
                pt = self.sel_item
                sel_points = [(round(px + qx * pt[0]),
                               round(py + qy * pt[1]),
                               "A")] 
        else:
            sel_points = list((round(px + qx * pt[0]),
                               round(py + qy * pt[1]),
                               "B")
                              for pt in self.sel_data.points_b )
            if (self.sel_data.mode == Selection.MULTIPLE_POINTS_B) \
              and (len(sel_points) > 0):
                last_pt = sel_points[-1]
                sel_points[-1] = (last_pt[0], last_pt[1], "A")
        
        wx.CallAfter(view.display_image,
                     self.main_video_frame,
                     self.main_video_frame.b_bmp,
                     self.img_showing,
                     sel_points = sel_points,
                     lock = self.img_showing_lock)
        
        text = U(self.img_ready_footer_text)
        wx.CallAfter(
            lambda:
                self.main_video_frame.b_footer_static_text.SetLabel(text))
        
        # >>>>
        # оси, шкалы    --> на этапе с маркерами
            
    
    def _update_right_view_act_in_advance(self):
        """
        Запускает _update_right_view_act на расчет следующего кадра, вперед.
        По своим признакам ситуацию, когда пользователь "ворочает" один кадр и
        не переходит на новый -- тогда расчет вперед не запускаем.
        """
        if self.prev_frame_num == self.cur_frame_num:
            return # скорее всего сйчас скролим один и тот же кадр
        next_frame =  2 * self.cur_frame_num - self.prev_frame_num
        min_valid = self.start_of_preproc_pack2
        max_valid = self.start_of_preproc_pack1 + \
            self.preproc_pack1_flt1_tkk.shape[0]
        if (next_frame < min_valid) or (next_frame >= max_valid):
            return
        self.prev_frame_num = self.cur_frame_num
        self._update_right_view_act(True, next_frame)
    
    
    def _take_view_param(self):
        """
        Вызывается из потока ГИУ. Забирает параметры из main_video_frame в этом
        потоке и сохраняет внутри для класса для использования рабочим потоком
        """
        Preview._take_view_param(self)

        self.view_param_lock.acquire()
        self.b_panel = copy.deepcopy(self.main_video_frame.b_panel)
        self.b_panel.size = self.main_video_frame.b_bmp.GetSizeTuple()
        
        config = self.main_video_frame.config
        self.render_mode = config.render_mode
        self.filter1_color_lim = config.filter1_color_lim
        self.auto_color_lim = config.auto_color_lim
        
        self.view_param_lock.release()

    
    def _update_view_act(self):
        if self.stop_update_view: return
        Preview._update_view_act(self)
        self._update_right_view_act()
 
    
    def express_spectrum(self, interval=[]):
        """
        Получить модуль квадрат спектра 3D (распределение спектральной
        плотности мощности), сохраненный после последнего расчета.
        Потокобезопасная функция.
        Аргументы:
          Interval ( list [t1, t2] ): выходной аргумент, через него выдается
                                      интервал времени по которому расчитан
                                      спектр.
        Возвращает тип PowerSpec или None, если нет данных
        """
        self.state_lock.acquire()
        if self.state_ == self.RUNNING_STATE:
            rv = copy.deepcopy(self.express_spectrum_)
            interval += self.express_spectrum_interval
        else:
            rv = None
        self.state_lock.release()
        return rv

    
    def _set_express_spectrum(self, complex_spec, interval):
        """
        Берет на вход комплексный спектр вида [f, ky, kx].
        Заполняет структуру self.express_spectrum_
        Записывает в self.express_spectrum_.data квадрат модуля в виде
        [kx, ky, f] с нормировкой и обрезанием по частоте.
        """
        df = self.fps / (1.0 * self.pack_len)
        dkx = 2*pi / self.lx
        dky = 2*pi / self.ly
        freq_count = int(round(self.max_freq_of_output_spec / df))
        freq_count = min(freq_count, complex_spec.shape[0] - 1)
        mod_square_spec = np.zeros((complex_spec.shape[2],
                                    complex_spec.shape[1],
                                    freq_count))
        ttt = complex_spec[1:(freq_count+1), -1:0:-1, -1:0:-1]
        mod_square_spec[1:, 1:, :] = np.swapaxes(ttt.real**2 + ttt.imag**2, 0, 2)
        mod_square_spec[0, 0, :] = np.abs(complex_spec[1:(freq_count+1), -1, -1])**2
        for nf in range(0, freq_count):
            mod_square_spec[0, 1:, nf] = np.abs(complex_spec[nf + 1, -1:0:-1, 0])**2
            mod_square_spec[1:, 0, nf] = np.abs(complex_spec[nf + 1, 0, -1:0:-1])**2
        mod_square_spec *= self.psd_norm
        
        logging.debug('size of express_spectrum_ is %0.0fM' 
                       % (mod_square_spec.size * 8 * 1e-6))
        
        self.state_lock.acquire()
        self.express_spectrum_.data = mod_square_spec
        self.express_spectrum_.df = df
        self.express_spectrum_.dkx = dkx
        self.express_spectrum_.dky = dky
        self.express_spectrum_interval = copy.deepcopy(interval)
        self.state_lock.release()
        
        
    def update_filters(self):
        """
        Вызывается извне, когда в конфиге поменялись фильтры
        """
        self.main_video_frame.hourglass('b')
        #....
        self.update_view()
    
    
    def _calc_norm_coefficients(self):
        """
        Расчитывае коэффициенты нормировки спектра
        Возрващает rv (tuple)
          rv[0]  psd_norm
          rv[1]  movie_norm
        """
        Nt, Ny_in, Nx_in  = self.first_array_tyx.shape
        han_norm = 2 * 1.5**(-0.5)
        sin_norm = sqrt(2.0)        
        psd_norm  = self.lx * self.ly /((pi * Nx_in * Ny_in)**2 * Nt * self.fps)
        config = self.main_video_frame.config
        if self.overlap or config.force_time_wnd_if_no_overlap:
            psd_norm *= han_norm**2
        if config.space_wnd:
            psd_norm *= sin_norm**4
        movie_norm = 1.0 / (Nx_in * Ny_in)
          # на самом деле, movie_norm -- это еще не все, есть еще в
          # _update_right_view_act
        return (psd_norm, movie_norm)
    
    
    def calc_average_spectrum(self,
                              finish_callback,
                              progress_callback,
                              wrap_callbacks = True,
                              _called_from_working_thread = False):
        """
        Вычисляет усредненный спектр по всему файлу.
        Аргументы:
          finish_calback (callable): по окончанию работы результат выдается
                                     так:
                                       finish_callback(power_spec)
                                     В случае ошибки или прерывания через
                                     progress_callback:
                                       finish_callback(None)
          progress_callback (callable): если не None, то периодически
                                        вызывается:
                                          progress_callback(val)
                                        где val = 0..99 .
                                        progress_callback должен возвращать True
                                        (или tuple, первый элемент которого True)
                                        Если progress_callback вернул False, то
                                        работа прерывается.
          wrap_callbacks (bool): если True, то все колбэки вызываются через
                                 wx.CallAfter; иначе - напрямую из раб потока
          _called_from_working_thread (bool)
        Возвращает:
          None
        Ставит задачу в очередь и мгновенно выходит
        (если не _called_from_working_thread).
        По окончанию работы результат выдается через finish_callback
        """
        if not _called_from_working_thread:
            self._enqueue_task(lambda: \
                self.calc_average_spectrum(finish_callback,
                                           progress_callback,
                                           wrap_callbacks,
                                           True))
            return
        try:
            continue_mutex = threading.Lock()
            continue_flag_keeper = []
            if wrap_callbacks:
                finish_callback_ = lambda arg: wx.CallAfter(finish_callback, arg)
            else:
                finish_callback_ = finish_callback

            step = self.pack_len
            if self.overlap: step = step // 2
            steps_count = (self.frames_count - self.pack_len) // step + 1
            if steps_count == 0:
                finish_callback_(None)
                return

            for j in range(0, steps_count):
                self._begin_new_pack(j * step)
                if j == 0:
                    aver_spec = copy.deepcopy(self.express_spectrum_)
                else:
                    aver_spec.data += self.express_spectrum_.data
                
                if progress_callback is not None:
                    progress = ((j + 1) * 100) / steps_count
                    progress = min(progress, 99)
                    if wrap_callbacks:
                        wx.CallAfter(_my_caller,
                                     progress_callback,
                                     [progress],
                                     continue_mutex,
                                     continue_flag_keeper)
                    else:
                        rv = progress_callback(progress)
                        continue_flag_keeper.append(rv)
                time.sleep(0.1)
                continue_mutex.acquire()
                continue_flag_keeper_ = copy.deepcopy(continue_flag_keeper)
                continue_mutex.release()
                for continue_flag in continue_flag_keeper_:
                    if hasattr(continue_flag, '__len__'):
                        continue_flag = continue_flag[0]
                    if not continue_flag:
                        finish_callback_(None)
                        return
                
                rv = Preview._goto_frame_act(self, j * step)  # для красоты
                if rv is not None:
                    raise GoToFrameFailed()
            
            aver_spec.data *= (1.0 / steps_count)
            finish_callback_(aver_spec)
            
        except Exception as err:
            logging.debug(str(err))
            finish_callback_(None)
            raise


    def save_xyt_result(self,
                        filename,
                        from_frame,
                        to_frame,
                        finish_callback,
                        progress_callback,
                        wrap_callbacks = True,
                        _called_from_working_thread = False):
        """
        Сохраняет зависимость из full_size_frame_flt1_yx последовательно
        по кадрам в файл
        Аргументы:
          finish_calback (callable): если не None, то вызывается в конце работы
                                     с аргументом: True - хорошо, False - ошибка
          прочие аргументы аналогично calc_average_spectrum
        """
        if not _called_from_working_thread:
            self._enqueue_task(lambda: \
                self.save_xyt_result(filename,
                                     from_frame,
                                     to_frame,
                                     finish_callback,
                                     progress_callback,
                                     wrap_callbacks,
                                     True))
            return
        if finish_callback is None:
            finish_callback = lambda succes: \
                logging.debug('save_xyt_result: ' + ['exit with error', 'done'][succes]) 
        if progress_callback is None:
            progress_callback=lambda v: logging.debug('save_xyt_result: %d%%' % v) 
        if wrap_callbacks:
            finish_callback_ = lambda val: wx.CallAfter(finish_callback, val)
            progress_callback_=lambda val: wx.CallAfter(progress_callback, val)
        else:
            finish_callback_ = finish_callback
            progress_callback_ = progress_callback
        f = None
        try:
            f = open(filename, 'wb')
            for nframe in range(from_frame, to_frame + 1):
                rv = self._goto_frame_act(nframe)
                if rv is not None:
                    raise rv
                f.write(memoryview(self.full_size_frame_flt1_yx))
                            
                if (nframe - from_frame) % 10 == 0:
                    progress = ((nframe - from_frame) * 100) / (to_frame - from_frame)
                    progress = min(progress, 99)
                    progress_callback_(progress)
            f.close()
            f = None
            
            # файл с описанием
            proj_path, proj_name1 = os.path.split(self.main_video_frame.project_filename)
            proj_name2 = proj_name1.split('.')
            proj_name = proj_name2[0]
            desc = {'project':proj_name,
                    'shape':[self.full_size_frame_flt1_yx.shape[0],
                             self.full_size_frame_flt1_yx.shape[1],
                             to_frame - from_frame + 1],
                    'dtype':repr(self.full_size_frame_flt1_yx.dtype),
                    'tags':['y','x','t'],
                    'from_to_frames':[from_frame + 1, to_frame + 1],
                    'physical_size':[self.ly,
                                     self.lx,
                                     (to_frame - from_frame + 1) / self.fps]
                   }
            f = open(filename + '.json', 'w')
            json.dump(desc, f, ensure_ascii = False, indent = 2)
            f.close()
#            logging.debug(repr(self.full_size_frame_flt1_yx.flags))
            
            progress_callback_(100)
            finish_callback_(True)

        except Exception as err:
            logging.debug(str(err))
            finish_callback_(False)
            self._report_noncritical_error("An error has occurred")
        if f is not None:
            f.close()
    
    
    def _report_noncritical_error(self, message):
        "Выдать сообщение об ошибке в ГУИ из рабочего потока"
        wx.CallAfter(self._report_noncritical_error_gui_thread, message)
        
    
    def _report_noncritical_error_gui_thread(self, message):
        msg_dlg = wx.MessageDialog(self.main_video_frame,
                                   U(message),
                                   "",
                                   wx.ICON_ERROR)        
        msg_dlg.ShowModal()
        msg_dlg.Destroy()

    
    
    def backtrace_b(self, X, Y, force = False):
        """
        Преобразование экранных координат точки внутри панели "b"
        в координаты на спроецированной плоскости, в метрах.
        Аргументы:
          X (int): экранная координата относительно угла панели "b"
          Y (iny)
          force (bool): см. ниже
        Возвращает:
          Если force == False:
            (x,y) -- (float, float)  метры
            или None, если точка не попадает в область изображения.
          Если force == True:
            (x,y) -- всегда, даже если это нереальные координаты
        """
        self.view_param_lock.acquire()
        px, qx, py, qy = self.output_scale_formula
        lx = self.lx
        ly = self.ly
        self.view_param_lock.release()

        x = (X - px) / qx
        y = (Y - py) / qy
        visible = (x >= -lx/2) and (y >= -ly/2) and (x < lx/2) and (y < ly/2)

        if visible or force:
            return (x, y)
        else:
            return None


    def _apply_moving_window(self, is_first_call):
        """
        Умножает first_array_tyx на текущие положения движущегося окна
        (если надо). И если это первый вызов, то расчитывает space_wnd_x и _y
        под нужный размер.
        """
        if not self.moving_window_enabled: return
        if is_first_call:
            self.space_wnd_x = self._initial_moving_window_wnd(
                self.space_wnd_x,
                self.moving_window_ref_rect[2] - self.moving_window_ref_rect[0],
                self.lx)
            self.space_wnd_y = self._initial_moving_window_wnd(
                self.space_wnd_y,
                self.moving_window_ref_rect[3] - self.moving_window_ref_rect[1],
                self.ly)
        
        #.....

    
    def _initial_moving_window_wnd(arr, wnd_len_m, full_len_m):
        full_size_pt = arr.size
        n = int(round(full_size_pt, wnd_len_m / full_len_m))
        if arr.size < n:
            if arr.shape[1] > arr.shape[2]:
                arr = np.ndarray((1,n,1))
            else:
                arr = np.ndarray((1,1,n))
        flarr = arr.flat;
        if space_wnd_enabled:
            nnn = np.arange(0, n, dtype=np.float64)
            flarr[:n] = np.sin(nnn * pi / (n - 1))
        else:
            flarr[:n] = 1.
        flarr[n:] = 0.
        return arr


    def _moving_window(nt, v, ref_begin, ref_end, full_len, full_size,
                       initial_cyclic_shift = 0):
        """
        Возвращает _MovingWindowTempStruct
        """
        cpos = (ref_begin + ref_end) * 0.5 \
            + v * (nt / self.fps - moving_window_ref_time) 
        cyclic_shift = initial_cyclic_shift        
        while cpos + cyclic_shift < -full_len * 0.5:            
            cyclic_shift += full_len
        while cpos + cyclic_shift > full_len * 0.5:            
            cyclic_shift -= full_len
        cpos += cyclic_shift
        
        wnd_half_len = (ref_end - ref_begin) * 0.5
        pixel_over_meter = full_size / full_len
        n1 = int(round( (cpos - wnd_half_len + full_len * 0.5) * pixel_over_meter ))
        n2 = int(round( (cpos + wnd_half_len + full_len * 0.5) * pixel_over_meter ))
        
        if (n1 >= 0) and (n2 < full_size):
            # самый простой случай: окно целиком в поле зрения
            return _MovingWindowTempStruct(
                src1_begin = 0,
                src1_end = n2-n1,
                dst1_begin = n1,
                dst1_end = n2,
                src2_begin = n2-n1,
                src2_end = n2-n1,
                dst2_begin = full_size,
                dst2_end = full_size,
                cylic_shift = cylic_shift)
        # .....

    
class GoToFrameFailed(Exception):
    pass


_TransformFrameArgs = namedtuple('_TransformFrameArgs',
                                 ['a',
                                  'b',
                                  'c',
                                  'x1',
                                  'y1',
                                  'x2',
                                  'y2'])


def _my_caller(func, args, mutex, lst):
    "Вызывает функцию. Захватывает мьютех. Добавляет результат к списку lst."
    val = func(*args)
    mutex.acquire()
    lst.append(val)
    mutex.release()


def _debug_dump_array_to_bmp_file(fname, data):
    # TODO: test this function
    dst_h = data.shape[0]
    dst_w = data.shape[1]
    dst_array_8bit = np.ndarray((dst_h, dst_w, 3), np.uint8)
    m = np.amin(data)
    M = np.amax(data)
    for n in range(0, 3):
        dst_array_8bit[:,:,n] = (data - m) * 255 / max(M-m, 1.0)
    img = wx.ImageFromBuffer(dst_w, dst_h, memoryview(dst_array_8bit))
    img.SaveFile(fname, wx.BITMAP_TYPE_BMP)

_MovingWindowTempStruct = namedtuple('MovingWindowTempStruct',
                                     ['src1_begin',
                                      'src1_end',
                                      'dst1_begin',
                                      'dst1_end',
                                      'src2_begin',
                                      'src2_end',
                                      'dst2_begin',
                                      'dst2_end',
                                      'cyclic_shift'])
