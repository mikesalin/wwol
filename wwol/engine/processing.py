# -*- coding: utf-8 -*-
"Объединяет всю обработку видео"

import threading
from math import *
import numpy as np

import view
import geom
Preview = view.Preview
FAIL_STOP = view.ViewerWorkingThread.FAIL_STOP
from c_part.transform_frame import transform_frame

class Procsessing(Preview):
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
       +--->  копия спектра
       + - - - - - - - - - - - - - - - - - - - - - - - - --> второй фильтр
       |   фильтры всякие
       |               еще один, для соседней пачки               
       V  ifft          |
    [t, ky,kx]      [t, ky,kx]                                  [  ] [  ]
           |                    ------ до сюда _begin_new_pack
           |  для конкретного кадра,
           |  с дополнением 0-ми до размера окна
           |  _update_right_view()
           V
         [y, x]                                                  [  ]
    
    Переменные:
    .state: PREINIT_STATE, RUNNING_STATE, DEAD_STATE
    .in_long_processing (bool)
    .state_lock
    .pack_len (int)
    .output_ftt_size ( (int, int) ) : по пространству
    .first_array_tyx (np.ndarray)
    .transform_frame_args (list)
    .lx(float) , .ly(float) : размер области в метрах, доступен в RUNNING_STATE
    .time_wnd (np.ndarray)
    .space_wnd_x (np.ndarray)
    .space_wnd_y (np.ndarray)
    .crop_output (bool)
    """
    PREINIT_STATE = 0
    RUNNING_STATE = 1
    DEAD_STATE = 2
    
    def __init__(self, *arg):
        "См. аргументы Previe.__init__"
        Preview.__init__(self, *arg)
        
        self.state = self.PREINIT_STATE
        self.in_long_processing = False
        self.state_lock = threading.Lock()
        
        config = self.main_video_frame.config
        self.pack_len = config.pack_len
        
        if config.active_area_num < 0:
            state = self.DEAD_STATE
            self._report_error("Не выбрана зона обработки")
            return
        aa = config.areas_list[config.active_area_num]
        self.first_array_tyx = np.ndarray((self.pack_len,
                                           aa.input_fft_size[1],
                                           aa.input_fft_size[0]),
                                          dtype = np.float64)
        # Аргументы для transform_frame, которые идут после массивов,
        # начиная с color depth
        self.transform_frame_args = [
            1,
            config.proj_coef.a,
            config.proj_coef.b,
            config.proj_coef.c,
            aa.coord[0],  # будет измененно после получения первого кадра
            aa.coord[1],
            aa.coord[2],
            aa.coord[3],
        ]
        
        self.lx = 1
        self.ly = 1
        
        # окна
        if config.overlap or config.force_time_wnd_if_no_overlap:
            N = self.pack_len
            nnn = np.arange(0, N, dtype=np.float)
            self.time_wnd = 0.5 + 0.5 * np.cos(2 * pi * nnn / N)
            self.time_wnd = self.time_wnd.reshape((N, 1, 1))
        else:
            self.time_wnd = np.ones((self.pack_len, 1, 1))
        sp_wnd_x_shp = (1, 1, aa.input_fft_size[0])
        sp_wnd_y_shp = (1, aa.input_fft_size[1], 1)
        if config.space_wnd:
            N = aa.input_fft_size[0]
            nnn = np.arange(0, N, dtype=np.float)
            self.space_wnd_x = np.sin(nnn * pi / N)
            self.space_wnd_x = self.space_wnd_x.reshape(sp_wnd_x_shp)
            N = aa.input_fft_size[1]
            nnn = np.arange(0, N, dtype=np.float)
            self.space_wnd_y = np.sin(nnn * pi / N)
            self.space_wnd_y = self.space_wnd_x.reshape(sp_wnd_y_shp)
            self.crop_output = True
        else:
            self.space_wnd_x = np.ones(sp_wnd_x_shp)
            self.space_wnd_y = np.ones(sp_wnd_y_shp)
            self.crop_output = False
        self.output_fft_size = aa.output_fft_size


    def _set_dead_state(self):
        self.state_lock.acquire()
        self.state = self.DEAD_STATE
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
            
            # self._begin_new_pack( ... )
            
            #......

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
        self.state_lock.acquire()
        self.in_long_processing = True
        first_frame = (self.state == self.PREINIT_STATE)
        self.state_lock.release()
        
        # loader -> first_array_tyx
        for n in range(0, self.pack_len):
            try:
                full_frame_num = n + first_frame_in_pack + self.frame_num_ofs
                img = self.loader.send(full_frame_num)
            except view.loading.LoadingError as err:
                self._report_loading_error(err)
                raise GoToFrameFailed()
         
            if first_frame:
                trpz = geom.trapezoid_inside_rectangle(
                    rect = self.transform_frame_args[4:],
                    proj_coef = self.transform_frame_args[1:4],
                    img_size = (img.GetWidth(), img.GetHeight()))
                self.transform_frame_args[4:6] = trpz[0:2]
                self.transform_frame_args[6:8] = trpz[4:5]

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
        
        # first_array_tyx -> second_array_fyx
        self.first_array_tyx *= self.time_wnd
        second_array_fyx = np.fft.rfft(self.first_array_tyx, axis = 0)
        
        # << здесь делать выравнивание яркости, вычитание фона...
        
        # second_array_fyx -> third_array_fkk
        second_array_fyx *= self.space_wnd_x
        second_array_fyx *= self.space_wnd_y
        third_array_fkk_large = np.fft.fft2(second_array_fyx)

        del(second_array_fyx)
        large_shape = third_array_fkk_large.shape
        output_fft_size = self.output_fft_size
        third_array_fkk = np.ndarray((large_shape[0],
                                      output_fft_size[1],
                                      output_fft_size[0]))
        to_x = [[0, output_fft_size[0] / 2],
                [output_fft_size[0] / 2, output_fft_size[0]]]
        to_y = [[0, output_fft_size[1] / 2],
                [output_fft_size[1] / 2, output_fft_size[1]]]
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
        
        
        # <<<<

        self.state_lock.acquire()
        self.in_long_processing = False
        if self.state == self.PREINIT_STATE:
            self.state = self.RUNNING_STATE
        self.state_lock.release()
        
    
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
    
    
class GoToFrameFailed(Exception):
    pass
        
