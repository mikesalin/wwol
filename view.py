# -*- coding: utf-8 -*-
"""
Классы, которые выполняют отрисовку. Разделяется основной поток (где GUI) и 
рабочий поток, где подготавливается отрисовка.
Основные классы:
  PanelParam
  Preview
"""

import copy
import threading
import Queue
import logging
import wx

import loading

class ViewerWorkingThread(threading.Thread):
    """
    Берет элементы (задания) из очереди .task_queue (тип Queue), ожидает тип
    элементов callable, запускает каждый элемент на выполнение. Если элемент
    возвращает не None, то этот объект сохраняется в .exit_obj и работа
    заканчивается. Т.е. вернуть не None -- это механизм (а) закончить работу и
    (б) сообщить об ошибке.
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.task_queue = Queue.Queue()
        self.exit_obj = None
    
    def run(self):
        "Код для испольнения в рабочем потоке"
        while True:
            task = self.task_queue.get()
            rv = task()
            if rv is not None:
                self.exit_obj = rv
                return

class PanelParam:
    """
    Парамтеры для отрисовки картинки в окне
    .size - размер места для рисования (окна)
    .zoom
    .pos - точка на растянутой картинке, которая попадет в левый-верхний угол
    """
    def __init__(self):
        self.size = (0,0)
        self.zoom = 1
        self.pos = (0,0)

def display_image(dest, img):
    """
    Аргументы:
        dest - wx.StaitcBitmap
        img - wx.Image
    Вызывается в ГИУ-потоке. Есть мнение, что операции с wx.Bitmap не работают
    в параллельных потоках.
    """
    bmp = img.ConvertToBitmap()
    dest.SetBitmap(bmp)

class Preview:
    """
    Отрисовка в режиме PREVIEW -- просто рисуем исходные кадры на левый экран.
    
    Изменился loader -- пересоздать класс Preview
    Изменилась обработка (в дальнейшей реализации) -- пересоздать класс
    Переход на новый кадр -- .goto_frame(n)
    Изменились размеры экрана (или, в дальнейшей реализации -- тип отрисовки)
    -- .update_view()
    В конце работы вызывать .close()
    
    При закрытии/пересоздании класса можно сохранять работающий loader:
    loader_obj = .close(True). В противном случае loader будет остановлен.
    
    Методы .goto_frame и .view_was_changed вызываются из ГУИ-потока,
    отправляют задание в рабочий поток и возвращают управление.
    По мере выполнения задания результат отрисовывается в основном окне через
    wx.RunAfter . Если висит задание, которое еще не начали выполнять, то оно
    вытесняется самым новым.
    
    Обработка ошибок в рабочем потоке:
    - вызывается self._report_error
    - тот вызывет main_video_frame.viewer_crushed() (через RunAfter)
    - если рабочий поток встал, то дальнейшие вызовы .goto_frame() и
     .update_view() возрващают False.
     
    данные:
    .main_video_frame
    .config
    .loader
    .working_thread
    .raw_img
    .zoom_cache -- см. одноименный параметр _resize_image
    .view_param_lock
    .a_panel
    .first_call_goto_frame
    .frame_num_ofs
    """
    def __init__(self, main_video_frame, loader, frame_num_ofs = 0):
        """
        main_video_frame -- MainVideoFrame
        loader -- настроенный генератор, выдающий wx.Image,
                  например, image_loader
        frame_num_ofs -- в loader будет передаваться
                         логический_номер_кадра + frame_num_ofs
        """
        self.main_video_frame = main_video_frame
        self.loader = loader
        self.a_panel = PanelParam()
        self.frame_num_ofs = frame_num_ofs
        
        self.working_thread = ViewerWorkingThread()
        self.working_thread.start()
        self.view_param_lock = threading.Lock()
        
        self.first_call_goto_frame = True
        self._take_view_param()
        self.goto_frame(None)
        
    def close(self, keep_loader = False):
        self._stop_working_thread()
        if keep_loader:
            loader_obj = self.loader
            self.loader = None
        else:
            loader_obj = None
            self.loader.close()
        return loader_obj
    
    def _enqueue_task(self, task):
        """
        - Проверка не умер ли рабочий поток. Возвращает True - жив, False-нет.
        - Поддержка очереди на 1 элемент с вытеснением.        
        """
        if not self.working_thread.is_alive():
            logging.debug("You try to submit a task, but working thread is dead")
            return False        
        try:  #очистка очереди
            while True:
                self.working_thread.task_queue.get_nowait()
        except Queue.Empty:
            pass
        self.working_thread.task_queue.put(task)
        return True
        
    def _stop_working_thread(self):
        close_flag = lambda: 1
        self._enqueue_task(close_flag)
        self.working_thread.join()
    
    def _report_error(self, message, warn_only=False):
        wx.CallAfter(self.main_video_frame.viewer_crushed, message, warn_only)

    def goto_frame(self, num):
        "num -- int - номер кадра, или None - первый/следующий кадр"
        task = lambda: self._goto_frame_act(num)
        return self._enqueue_task(task)
        
    def update_view(self):
        self._take_view_param()
        return self._enqueue_task(self._update_view_act)
    
    #И дальше основные рабочие методы:
    def _take_view_param(self):
        """
        Вызывается из потока ГИУ. Забирает параметры из main_video_frame в этом
        потоке и сохраняет внутри для класса для использования рабочим потоком
        """
        self.view_param_lock.acquire()
        self.a_panel = copy.deepcopy(self.main_video_frame.a_panel)
        self.a_panel.size = self.main_video_frame.a_bmp.GetSizeTuple()
        self.view_param_lock.release()
    
    def _goto_frame_act(self, num):
        """
        Вызывается из рабочего потока
        num -- int - номер кадра, или None - первый/следующий кадр
        """
        if self.first_call_goto_frame and (num is not None):
            self._goto_frame_act(None)
        self.first_call_goto_frame = False
        
        try:                
            if num is None:
                self.raw_img = self.loader.next()
            else:
                self.raw_img = self.loader.send(num + self.frame_num_ofs)
        except loading.LoadingError:
            self._report_error("Ошибка при загрузке кадра.")
            return
        self.zoom_cache = []
        
        self._update_view_act()        
        if num is None: num = 0
        wx.CallAfter(self.main_video_frame.display_frame_num, num)
        

    def _update_view_act(self):
        "Вызывается из рабочего потока"
        self.view_param_lock.acquire()
        a_panel = self.a_panel
        self.view_param_lock.release()                        

        img = self._resize_image(self.raw_img, a_panel, self.zoom_cache)
        #удаляем альфа-канал -- устранение бага с файлами старого эмулятора
        if img.HasAlpha():
            img2 = wx.ImageFromData(img.GetWidth(),
                                    img.GetHeight(),
                                    img.GetData())
            img = img2
        
        wx.CallAfter(display_image, self.main_video_frame.a_bmp, img)
    

    def _resize_image(self, img, panel, zoom_cache = []):
        """
        Масштабирование, сдвиг и обрезание картики img под параметры panel.
        Аргументы:
          img (wx.Image)
          panel (PanleParam)
          zoom_cache (list [wx.Image, float]): входной и выходной параметр.
                     Масштабированная картинка (0ой элемент списка) для
                     предыдущего значения зума (1ый элемент списка).
        Возвращает:
          wx.Image (out-of-place transform)
        """
        # zoom
        if panel.zoom != 1:
            if (len(zoom_cache) == 2) and (zoom_cache[1] == panel.zoom):
                img = zoom_cache[0]
            else:
                raw_size = img.GetSize().Get()
                img = img.Scale(int( raw_size[0] * panel.zoom ),
                               int( raw_size[1] * panel.zoom ), 
                               wx.IMAGE_QUALITY_HIGH)
                zoom_cache[:] = [img, panel.zoom]

        # позиция ЛВ угла исходной картинке на чистом белом поле
        pos_x = -panel.pos[0]
        pos_y = -panel.pos[1]
        # размер растянутой картинки
        src_size_x = img.GetSize().GetWidth()
        src_size_y = img.GetSize().GetHeight()
        # размер панели
        dst_size_x = panel.size[0]
        dst_size_y = panel.size[1]
        
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
        # режем
        img = img.GetSubImage(wx.Rect(crop_start_x, crop_start_y,
                                      crop_size_x, crop_size_y) )
        
        #дополняем белым
        img.Resize((dst_size_x, dst_size_y), (pos_x, pos_y), 255, 255, 255)
        return img

