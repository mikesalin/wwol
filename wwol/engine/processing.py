# -*- coding: utf-8 -*-
"Объединяет всю обработку видео"

import threading
from math import *
import copy
from collections import namedtuple
import logging
import numpy as np

from . import view
from . import geom
Preview = view.Preview
FAIL_STOP = view.ViewerWorkingThread.FAIL_STOP
from c_part.transform_frame import transform_frame
from ..grapher import power_spec

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
       |   fft
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
       |  ifft        еще один, для соседней пачки       
       V                   |
    [t, ky,kx]      [t, ky,kx]                                 [  ]  [  ]
    array41_tkk     array42_tkk                         array43_tkk  array44_tkk
           |                    ------ до сюда _begin_new_pack
           |  для конкретного кадра,
           |  с дополнением 0-ми до размера окна
           |  _update_right_view()
           V
         [y, x]                                                  [  ]
    
    Переменные:
    .state_: PREINIT_STATE, RUNNING_STATE, DEAD_STATE
             доступ снаруже через state()
    .in_long_processing (bool)
    .state_lock
    .pack_len (int)
    .output_ftt_size ( (int, int) ) : по пространству
    .first_array_tyx (np.ndarray)
    .transform_frame_args (_TransformFrameArgs)
    .lx(float) , .ly(float) : размер области в метрах, доступен в RUNNING_STATE
    .time_wnd (np.ndarray)
    .space_wnd_x (np.ndarray)
    .space_wnd_y (np.ndarray)
    .crop_output (bool)
    .express_spectrum_ (PowerSpec) :  квадрат спектра в 3D, сохраненный после
                                      последнего расчета; защищен state_lock;
                                      доступ через express_spectrum()
    .output_spec_mode (int)
    .max_freq_of_output_spec
    .fps
    """
    PREINIT_STATE = 0
    RUNNING_STATE = 1
    DEAD_STATE = 2
    
    def __init__(self, *arg, **kwarg):
        "См. аргументы Previe.__init__"
        Preview.__init__(self, *arg, **kwarg)
        
        self.state_ = self.PREINIT_STATE
        self.in_long_processing = False
        self.state_lock = threading.Lock()
        
        config = self.main_video_frame.config
        self.pack_len = config.pack_len
        
        if config.active_area_num < 0:
            state_ = self.DEAD_STATE
            self._report_error("Не выбрана зона обработки")
            return
        aa = config.areas_list[config.active_area_num]
        self.first_array_tyx = np.ndarray((self.pack_len,
                                           aa.input_fft_size[1],
                                           aa.input_fft_size[0]),
                                          dtype = np.float64)
        # Аргументы для transform_frame, которые идут после массивов,
        # начиная с color depth
        self.transform_frame_args = _TransformFrameArgs(
            a = config.proj_coef.a,
            b = config.proj_coef.b,
            c = config.proj_coef.c,
            x1 = aa.coord[0],  # будет измененно после получения первого кадра
            y1 = aa.coord[1],
            x2 = aa.coord[2],
            y2 = aa.coord[3])
        
        self.lx = 1
        self.ly = 1
        
        # окна
        if config.overlap or config.force_time_wnd_if_no_overlap:
            N = self.pack_len
            nnn = np.arange(0, N, dtype=np.float)
            self.time_wnd = 0.5 - 0.5 * np.cos(2 * pi * nnn / N)
            self.time_wnd = self.time_wnd.reshape((N, 1, 1))
        else:
            self.time_wnd = np.ones((self.pack_len, 1, 1))
        sp_wnd_x_shp = (1, 1, aa.input_fft_size[0])
        sp_wnd_y_shp = (1, aa.input_fft_size[1], 1)
        if config.space_wnd:
            N = aa.input_fft_size[0]
            nnn = np.arange(0, N, dtype=np.float)
            self.space_wnd_x = np.sin(nnn * pi / (N - 1))
            self.space_wnd_x = self.space_wnd_x.reshape(sp_wnd_x_shp)
            N = aa.input_fft_size[1]
            nnn = np.arange(0, N, dtype=np.float)
            self.space_wnd_y = np.sin(nnn * pi / (N - 1))
            self.space_wnd_y = self.space_wnd_y.reshape(sp_wnd_y_shp)
            self.crop_output = True
        else:
            self.space_wnd_x = np.ones(sp_wnd_x_shp)
            self.space_wnd_y = np.ones(sp_wnd_y_shp)
            self.crop_output = False
        self.output_fft_size = aa.output_fft_size
        
        self.express_spectrum_ = power_spec.PowerSpec()
        self.output_spec_mode = config.output_spec_mode
        self.max_freq_of_output_spec = config.valid_max_freq()
        self.fps = config.fps
        
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
            rv = Preview._goto_frame_act(self, num)
            if rv is not None: raise GoToFrameFailed()
            
            # DEBUG:
            if self.state() == self.PREINIT_STATE:
                self._begin_new_pack(num)

        except GoToFrameFailed:
            self._set_dead_state()
            return FAIL_STOP
    
    def _begin_new_pack(self, first_frame_in_pack):
        """
        Обработка в начале каждой пачки
        Аргументы:
          first_frame_in_pack -- номер первого кадра в пачке
        Исключения: GoToFrameFailed
        """
        logging.debug('_begin_new_pack, first_frame_in_pack = %d',
                      first_frame_in_pack)
        self.state_lock.acquire()
        self.in_long_processing = True
        first_frame = (self.state_ == self.PREINIT_STATE)
        self.state_lock.release()
        
        
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
                ttt = _TransformFrameArgs(
                    a = self.transform_frame_args.a,
                    b = self.transform_frame_args.b,
                    c = self.transform_frame_args.c,
                    x1 = trpz[0],
                    y1 = trpz[1],
                    x2 = trpz[4],
                    y2 = trpz[5])
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
        logging.debug('all images are read into first_array_tyx')
        
        # first_array_tyx -> second_array_fyx
        self.first_array_tyx *= self.time_wnd
        second_array_fyx = np.fft.rfft(self.first_array_tyx, axis = 0)
        # TODO: разобраться с нормировкой
        logging.debug('size of second_array_fyx is %0.0fM' 
                       % (second_array_fyx.size * 16 * 1e-6))

        
        # << здесь делать выравнивание яркости, вычитание фона...
        
        # second_array_fyx -> third_array_fkk
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
        to_x = [[output_fft_size[0] / 2, output_fft_size[0]],
                [0, output_fft_size[0] / 2]]
        to_y = [[output_fft_size[1] / 2, output_fft_size[1]],
                [0, output_fft_size[1] / 2]]
        from_x = [[0, output_fft_size[0] / 2],
                  [large_shape[2] - output_fft_size[0] / 2, large_shape[2]]]
        from_y = [[0, output_fft_size[1] / 2],
                  [large_shape[1] - output_fft_size[1] / 2, large_shape[1]]]
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
            self._set_express_spectrum(third_array_fkk)
        
        # <<<< фильтрация
        # third_array_fkk фильтруем на месте, array33_fkk создаем, если надо
        array33_fkk = None
        
        if self.output_spec_mode == 1:
            self._set_express_spectrum(third_array_fkk)
        if self.output_spec_mode == 2:
            if array33_fkk is not None:
                self._set_express_spectrum(array33_fkk)
            else:
                self._report_error("Запрошел спектр из второго фильтра, "
                                   "а фильтр не создан")
                raise GoToFrameFailed()

        # ifft  third_array_fkk -> array41_tkk,  array33_fkk -> array33_tkk
        # .....
        

        self.state_lock.acquire()
        self.in_long_processing = False
        if self.state_ == self.PREINIT_STATE:
            self.state_ = self.RUNNING_STATE
        self.state_lock.release()
        logging.debug('_begin_new_pack is finished')
        
    
    def _update_right_view(self):
        """
        Отрисоква одного обработанного кадра
        Вызывается из рабочего потока
        """
        pass

    
    def _update_both_views(self):
        self._update_view_act()
        self._update_right_view()
 
    
    def update_view(self):
        "Перерисовать. Вызов из потока ГУИ"
        self._take_view_param()
        return self._enqueue_task(self._update_both_views)
        
    
    def express_spectrum(self):
        """
        Получить модуль квадрат спектра 3D (распределение спектральной
        плотности мощности), сохраненный после последнего расчета.
        Потокобезопасная функция
        Возвращает тип PowerSpec или None, если нет данных
        """
        self.state_lock.acquire()
        if self.state_ == self.RUNNING_STATE:
            rv = copy.deepcopy(self.express_spectrum_)
        else:
            rv = None
        self.state_lock.release()
        return rv

    
    def _set_express_spectrum(self, complex_spec):
        """
        Берет на вход комплексный спектр вида [f, ky, kx].
        Заполняет структуру self.express_spectrum_
        Записывает в self.express_spectrum_.data квадрат модуля в виде
        [kx, ky, f] с нормировкой и обрезанием по частоте.
        """
        df = self.fps / (1.0 * self.pack_len)
        dkx = 2*pi / self.lx
        dky = 2*pi / self.lx
        freq_count = round(self.max_freq_of_output_spec / df)
        freq_count = min(freq_count, complex_spec.shape[0] - 1)
        mod_square_spec = np.swapaxes(
            np.abs( complex_spec[1:(freq_count+1), :, :] )**2,
            0,
            2)
        # TODO: опять таки нормировка
        
        logging.debug('size of express_spectrum_ is %0.0fM' 
                       % (mod_square_spec.size * 8 * 1e-6))
        
        self.state_lock.acquire()
        self.express_spectrum_.data = mod_square_spec
        self.express_spectrum_.df = df
        self.express_spectrum_.dkx = dkx
        self.express_spectrum_.dky = dky
        self.state_lock.release()
    
    
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


def _debug_dump_array_to_bmp_file(fname, data):
    import wx
    dst_h = data.shape[0]
    dst_w = data.shape[1]
    dst_array_8bit = np.ndarray((dst_h, dst_w, 3), np.uint8)
    m = np.amin(data)
    M = np.amax(data)
    for n in range(0, 3):
        dst_array_8bit[:,:,n] = (data - m) * 255 / max(M-m, 1.0)
    img = wx.ImageFromBuffer(dst_w, dst_h, np.getbuffer(dst_array_8bit))
    img.SaveFile(fname, wx.BITMAP_TYPE_BMP)


