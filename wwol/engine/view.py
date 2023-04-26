# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
Модуль отрисовки кадров. Разделяется основной поток (где GUI) и рабочий поток,
где подготавливается отрисовка. Главный класс здесь -- это Preview
"""

import copy
import threading
import queue
import logging
import wx

from . import loading
from ..base_gui.mvf_aux_classes import Selection

__all__ = ["Preview", "PanelParam",
           "display_image", "panels_are_equal",
           "MARKER_SIZE", "LINE_WIDTH", "ACTIVE_COLOR", "BACKGROUND_COLOR"]


class ViewerWorkingThread(threading.Thread):
    """
    Берет элементы (задания) из очереди .task_queue (тип Queue), ожидает тип
    элементов callable, запускает каждый элемент на выполнение. Если элемент
    возвращает не None, то этот объект сохраняется в .exit_obj и работа
    заканчивается. Т.е. вернуть не None -- это механизм (а) закончить работу и
    (б) сообщить об ошибке.
    
    Рекомендуется в качестве остановочного объекта использовать определенные
    здесь int-ы:
    .NORMAL_STOP
    .FAIL_STOP
    
    Переменные:
    .task_queue (Queue): создается в __init__
    .exit_obj :          устанавливается в результате работы
    .unkn_err_callback (callable or None) : можно установить после
                                            инициализации и до запуска потока
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.task_queue = queue.Queue()
        self.exit_obj = None
        self.unkn_err_callback = None
    
    def run(self):
        "Код для испольнения в рабочем потоке"
        good_exit = False
        try:
            while True:
                task = self.task_queue.get()
                rv = task()
                if rv is not None:
                    good_exit = True
                    self.exit_obj = rv
                    return
        finally:
            if (not good_exit) and not (self.unkn_err_callback is None):
                self.unkn_err_callback()
    
    NORMAL_STOP = 1
    FAIL_STOP = 2


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

def panels_are_equal(x, y):
    return (x.pos == y.pos) and (x.zoom == y.zoom) and (x.pos == y.pos)


_UNKN_ERR_MSG = "Unknown error in the working thread"


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
    wx.CallAfter . Если висит задание, которое еще не начали выполнять, то оно
    вытесняется самым новым.
    
    Обработка ошибок в рабочем потоке:
    - вызывается self._report_error
    - тот вызывет main_video_frame.viewer_crushed() (через CallAfter)
    - рабочий поток останавливается
    - если рабочий поток встал, то дальнейшие вызовы .goto_frame() и
     .update_view() возрващают False.
     
    Данные:
    .main_video_frame -- тип MainVideoFrame
    .loader
    .working_thread
    .raw_img        -- для доступа извне есть get_raw_img
    .zoom_cache     -- см. одноименный параметр _resize_image
    .view_param_lock - следующие объектызащищены этим мьютексом:
      .a_panel      -- тип PanelParam
      .sel_data     -- тип Selection, копия main_video_frame.sel_data
      .raw_img_size -- (width, height), для доступа извне есть get_raw_img_size
    .first_call_to_goto_frame
    .frame_num_ofs
    """
    #NB: надо будет отдельно выделить базовый класс для большей наглядности
    
    def __init__(self,
                 main_video_frame,
                 loader,
                 frame_num_ofs = 0,
                 start_with_frame = 0,
                 loader_is_hot = False,):
        """
        Аргументы:
            main_video_frame (MainVideoFrame)
            loader: настроенный генератор, выдающий wx.Image,
                    например, image_loader
            frame_num_ofs (int): в loader будет передаваться
                                 логический_номер_кадра + frame_num_ofs
                                 ( см. help(loading.frame_numbering) )
            start_with_frame (int)
            loader_is_hot (bool): loader уже выдавал какие-то кадры ранее
        """
        self.main_video_frame = main_video_frame
        self.loader = loader
        self.frame_num_ofs = frame_num_ofs

        self.a_panel = PanelParam()
        self.sel_data = Selection()
        self.raw_img_size = (0, 0)
        
        self.working_thread = ViewerWorkingThread()
        self.working_thread.unkn_err_callback = self._report_error
        self.working_thread.start()
        self.view_param_lock = threading.Lock()
        
        self.first_call_to_goto_frame = not loader_is_hot
        self._take_view_param()
        if not self.is_processing():
            self.goto_frame(start_with_frame)
        
    def close(self, keep_loader = False):
        self._stop_working_thread()
        if self.loader is None:
            return None
        if keep_loader:
            retruned_loader_obj = self.loader
            self.loader = None
        else:
            retruned_loader_obj = None
            self.loader.close()
            self.loader = None
        return retruned_loader_obj
    
    def is_processing(self):
        return False
    
    def __del__(self):
        self.close() # двойной close() не ошибка
    
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
        except queue.Empty:
            pass
        self.working_thread.task_queue.put(task)
        return True
        
    def _stop_working_thread(self):
        if not self.working_thread.is_alive(): return
        close_flag = lambda: ViewerWorkingThread.NORMAL_STOP
        self._enqueue_task(close_flag)
        self.working_thread.join()
    
    def _report_error(self, message = _UNKN_ERR_MSG):
        """
        Выдать сообщение об ошибке в ГУИ из рабочего потока
        Иницировать закрытие обработчика
        """
        wx.CallAfter(self.main_video_frame.viewer_crushed, message)

    def goto_frame(self, num):
        """
        num -- int - номер кадра
        NB: теперь не принимаем goto_frame(None)
        """
        self._take_view_param()
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
        self.sel_data = copy.deepcopy(self.main_video_frame.sel_data)
        self.view_param_lock.release()
    
    def _report_loading_error(self, err):
        err_subtype = "LoadingError (not a subtype)"
        more_err_info = ""
        if isinstance(err, loading.FrameLoaddingFailed):
            err_subtype = "FrameLoaddingFailed"
            more_err_info = "File error."
        if isinstance(err, loading.BadFormatString):
            err_subtype = "BadFormatString"
        if isinstance(err, loading.NoData):
            err_subtype = "NoData"
            more_err_info = "No data to process."
        logging.debug("_goto_frame_act caught " + err_subtype)
        self._report_error("Error occurred while loading frames. %s" % more_err_info)
    
    def _goto_frame_act(self, num):
        """
        Вызывается из рабочего потока
        Аргументы:
          num -- int - номер кадра
        Возвращает:
          None -- все хорошо
          FAIL_STOP -- при ошибке
        """
        try:                
            if self.first_call_to_goto_frame:
                dummy = next(self.loader)  # пнуть, чтобы заработал
                self.first_call_to_goto_frame = False
            self.raw_img = self.loader.send(num + self.frame_num_ofs)
        except loading.LoadingError as err:
            # обработка ошибок:
            self._report_loading_error(err)
            return ViewerWorkingThread.FAIL_STOP
        self.zoom_cache = []
        
        self._update_view_act()        
        if num is None: num = 0
        wx.CallAfter(self.main_video_frame.display_frame_num, num)
        

    def _update_view_act(self):
        "Вызывается из рабочего потока"
        #забираем данные с конкурентным доступом
        self.view_param_lock.acquire()
        a_panel = copy.deepcopy(self.a_panel)
        sel_data = copy.deepcopy(self.sel_data)
        self.view_param_lock.release()
        
        #основной кусок работы
        decor_temp = self._decoration_before_resize(sel_data)
        points = decor_temp[-1]
        visible_points = []
        img = self._resize_image(self.raw_img,
                                 a_panel,
                                 self.zoom_cache,
                                 points,
                                 visible_points)
        sel_points, sel_lines = self._decoration_after_resize(
            sel_data,
            *decor_temp[:-1],
            points = points,
            visible_points = visible_points)
        
        #удаляем альфа-канал -- устранение бага с файлами старого эмулятора
        if img.HasAlpha():
            img2 = wx.ImageFromData(img.GetWidth(),
                                    img.GetHeight(),
                                    img.GetData())
            img = img2
        
        #сохраняем размеры для backtrace
        self.view_param_lock.acquire()
        self.raw_img_size = (self.raw_img.GetWidth(), self.raw_img.GetHeight())
        self.view_param_lock.release()
        
        #ставим функцию отрисовки в очередь в поток ГУИ
        wx.CallAfter(display_image,
                     self.main_video_frame,
                     self.main_video_frame.a_bmp,
                     img,
                     sel_points,
                     sel_lines)
    

    def _resize_image(self, img, panel, zoom_cache = [], points = [],
                      visible_points = []):
        """
        Масштабирование, сдвиг и обрезание картики img под параметры panel.
        Аргументы:
          img (wx.Image)
          panel (PanleParam)
          zoom_cache (list [wx.Image, float]): входной и выходной аргумент.
                     Масштабированная картинка (0ой элемент списка) для
                     предыдущего значения зума (1ый элемент списка).
          points (list [(int,int), ...]) : входной и выходной аргумент,
                     преобразование координат дискретных точек изображения,
                     список изменяется на месте.
          visible_points (list [bool, bool, ...]): выходной аргумент,
                     видимость точек из списка points.
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

        # позиция ЛВ угла картинки на чистом белом поле (ниже будет изменяться)
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
        
        #преобразуем дискретные точки
        visible_points[:] = []
        for j in range(0, len(points)):
            x, y = points[j]
            X = int(x * panel.zoom) - panel.pos[0]
            Y = int(y * panel.zoom) - panel.pos[1]
            points[j] = (X, Y)
            visible_points.append((X >=0) and (Y >= 0) and (X < dst_size_x) \
                                   and (Y < dst_size_y))
        
        return img
        

    def _decoration_before_resize(self, sel_data):
        """
        Работа с пометками поверх изображения.
        Эта функция вызывается из _update_view_act до _resize_image.
        Подготавливаем список пометок поверх изображения, которые нужно
        масштабировать вместе с этим изображением.
        Аргументы:
            sel_data(SelData): копия структуры из MainVideoFrame,
                               могут делаться некоторые изменения на месте
        Возвращает:
            (sel_points_count,
             sel_rects_count,
             edit_single_point,
             edit_single_rect,
             points)
        В массив points, который имеет вид [(int, int), ...], пихаем все
        по порядку:
            points_a
            sel_item, если это точка
              <sel_points_count позиций до сюда>
            (x1, y1) для rects_a[0]
            (x2, y2) для rects_a[0]
            (x1, y1) для rects_a[1]
            ...
            (x1, y1), (x2, y2) для sel_item, если это прямоугольник
              <sel_points_count + 2 * sel_rects_count позиций до сюда>
            4 точки для trpz[0]
            ....
        """
        points = sel_data.points_a
        edit_single_point = (sel_data.sel_item is not None) and\
            (sel_data.mode == Selection.SINGLE_POINT_A)
        if edit_single_point:
            points.append(sel_data.sel_item)
        sel_points_count = len(points)
        
        edit_single_rect = (sel_data.sel_item is not None) and\
            (sel_data.mode == Selection.SINGLE_RECT_A)
        if edit_single_rect:
            sel_data.rects_a.append(sel_data.sel_item)
        sel_rects_count = len(sel_data.rects_a)
        for rect in sel_data.rects_a:
            points.append((rect[0], rect[1]))
            points.append((rect[2], rect[3]))
        
        for trpz in sel_data.trpz:
            for j in range (0,4):
                points.append((trpz[2 * j], trpz[2* j + 1]))
        
        return (sel_points_count, sel_rects_count,
                edit_single_point, edit_single_rect,
                points)


    def _decoration_after_resize(self, sel_data,
                                 sel_points_count, sel_rects_count,
                                 edit_single_point, edit_single_rect,
                                 points, visible_points):
        """
        Работа с пометками поверх изображения.
        Эта функция вызывается из _update_view_act посел _resize_image.
        Переделываем список пометок поверх изображения.
        Аргументы:
            sel_data (SelData): копия структуры из MainVideoFrame
            sel_points_count (int) : выход _decoration_before_resize
            sel_rects_count (int):   --"--"--
            edit_single_point (bool):   --"--"--
            edit_single_rect (bool):   --"--"--
            points (list [(int,int), ... ] ) :
                                 --"--"--, пропущенный через _resize_image.
            visible_points (list [bool, bool, ...]) : выход _resize_image.
        Возвращает:
            (sel_points, sel_lines) -- по формату аргументов display_image
        """
        #-точки
        sel_points = []
        if edit_single_point or \
           sel_data.mode == Selection.MULTIPLE_POINTS_A:
            yellow_point = sel_points_count - 1
        else:
            yellow_point = - 1
        for j in range(0, sel_points_count):
            if visible_points[j]:
                clr = ["B", "A"] [yellow_point == j]
                sel_points.append((points[j][0], points[j][1], clr))
        #-прямоугольники
        sel_lines = []
        if edit_single_rect or \
           sel_data.mode == Selection.MULTIPLE_RECTS_A:
            yellow_rect = sel_rects_count - 1
        else:
            yellow_rect = - 1
        for j in range(0, sel_rects_count):
            n1 = sel_points_count + 2 * j
            n2 = n1 + 1
            if not (visible_points[n1] or visible_points[n2]): continue
            x1, y1 = points[n1]
            x2, y2 = points[n2]
            clr = ["B", "A"] [yellow_rect == j]
            sel_lines.extend([x1, y1, x2, y1, x2, y2, x1, y2, x1, y1, clr])
        #-трапеции
        for j in range(0, len(sel_data.trpz)):
            ofs = sel_points_count + 2 * sel_rects_count + 4 * j
            anyth_visible = False
            for k in range(0, 4):
                anyth_visible = anyth_visible or visible_points[ofs + k]
            if not anyth_visible: continue
            for k in range(0, 4):
                sel_lines.extend([points[ofs + k][0], points[ofs + k][1]])
            sel_lines.extend([points[ofs][0], points[ofs][1]])
            clr = ["B", "A"] [yellow_rect == j]
            sel_lines.append(clr + ':')
        #....
        return (sel_points, sel_lines)
    
    
    def backtrace_a(self, X, Y, force = False):
        """
        Преобразование "экранных" координат точки внутри панели "a"
        в координаты исходного изображения.
        Аргументы:
          X (int): "экранная" координата относительно угла панели "а"
          Y (iny)
          force (bool): см. ниже
        Возвращает:
          Если force == False:
            (x,y) -- (int, int)
            или None, если точка не попадает в область изображения.
          Если force == True:
            (x,y) -- всегда, даже если это нереальные координаты
        """
        self.view_param_lock.acquire()        
        x = int( (X + self.a_panel.pos[0]) / self.a_panel.zoom )
        y = int( (Y + self.a_panel.pos[1]) / self.a_panel.zoom )
        raw_img_size = self.raw_img_size
        self.view_param_lock.release()
        visible = (x >= 0) and (y >= 0) and (x < raw_img_size[0]) and \
                  (y < raw_img_size[1])
        if visible or force:
            return (x, y)
        else:
            return None
            
    def backtrace_rect_a(self, X1, Y1, X2, Y2):
        """
        Преобразование "экранного" прямоугольника внутри панели "a"
        в координаты исходного изображения.
        Аргументы:
          X1, Y1 (ints): лево-верх
          X2, Y2 (ints): право-низ (считаем, что углы принадлежат области)
        Возвращает:
          (x1, y1, x2, y2) или None
          Если результат преобразования полностью попадает внутрь изображения,
          то возвращает его.
          Если какая-то из точек вылезает за пределы, то обрезает по границе.
          Если вообще нет пересечения, то возвращает None
        """
        pt1 = self.backtrace_a(X1, Y1, True)
        pt2 = self.backtrace_a(X2, Y2, True)
        rect = wx.Rect(min(pt1[0], pt2[0]),
                       min(pt1[1], pt2[1]),
                       abs(pt1[0] - pt2[0]) + 1,
                       abs(pt1[1] - pt2[1]) + 1)
        self.view_param_lock.acquire()
        img_rect = wx.Rect(0, 0, self.raw_img_size[0], self.raw_img_size[1])
        self.view_param_lock.release()
        if rect.Intersects(img_rect):
            res_rect = rect.Intersect(img_rect)
            return (res_rect.GetTopLeft().x,
                    res_rect.GetTopLeft().y,
                    res_rect.GetBottomRight().x,
                    res_rect.GetBottomRight().y)
        else:
            return None
    
    def get_raw_img_size(self):
        """
        Возвращает размер исходного изображения (без масштабирования) в виде
        (int, int), т.е (ширина, высота). Возвращает (0, 0), если еще ни одно
        изображение не было загружено и размер неизвестен.
        """
        self.view_param_lock.acquire()
        rv = self.raw_img_size
        self.view_param_lock.release()
        return rv
        
    def get_raw_img(self):
        "Возвращает исходное изображение, кт. сейчас лежит в буфере, или None"
        q = queue.Queue()
        self._enqueue_task(lambda: q.put(self.raw_img.Copy()))
        try:
            res = q.get(block = True, timeout = 1)
        except queue.Empty:
            return None
        return res
    


MARKER_SIZE = 10
# MARKER_SIZE: размер маркера для обозначения выделенных точек:
# полуширина креста, 5..15 рисуется с точка по центру, >15 рисуется жирной линией
LINE_WIDTH = 2
ACTIVE_COLOR = 'yellow'
BACKGROUND_COLOR = 'red'

_MY_COLORS = {'A': ACTIVE_COLOR,
              'B': BACKGROUND_COLOR}
_MY_LINE_STYLES = {"-": wx.SOLID, ":": wx.SHORT_DASH}

def translate_color(color_str):
    """
    Аргументы: color_str(string): обозначение цвета, как оно заведено у нас:
                                  "A" -- active,
                                  "B" -- background,
                                  (будет дополнено).
    Возвращает: То, что понимает SetColour в wxPython.
                Если color_str имеет неправильное значение, то возвр. 'black'
    """
    res = None
    if color_str in _MY_COLORS: res = _MY_COLORS[color_str]
    if res is None:
        logging.debug("Unknown color: '%s'", color_str)
        res = 'black'
    return res

def display_image(dest_top, dest, img,
                  sel_points = [], sel_lines = [],
                  lock = None):
    """
    Последняя стадия отрисовки изображения, которая вызывается в ГУИ потоке.
    Выполняются операции с wx.Bitmap и wx.DC, которое не работают
    в параллельных потоках.
    Аргументы:
        dest_top (MainVideoFrame of None)
        dest (wx.StaitcBitmap): кладет сюда результат через .SetBitmap(..)
        img (wx.Image): изображение (уже под размер dest)
        sel_points (list of tuples (int, int, str) ~ [(X, Y, "color"),..] ):
            "выделенные" точки, которые нужно нанести поверх img.
            X,Y -- после масштабирования и сдвига,
            color -- см. tanslate_color .
        sel_lines (list -- [x1,y1,x2,y2,"color", x3,y3,x4,y4,"color2"...]):
            ломаные линии (без автозамыкания). Задаются как последовательность
            координат. Строковый параметр color (цвет) используется как
            разделитель -- он определяет цвет линии, введенной до него, и
            означает начало новой линии. Значение color -- см. tanslate_color
            + окончание определяет тип линии: "-" или ничего -- сплошная,
            ":" -- пунктир (как в Матлабе, но не до конца запилено)
        lock (Lock or None): опционально, мютекс который надо заблокировать,
            пока работаем со входными аргументами
    Возвращает: ничего
    """
    if lock is not None: lock.acquire()
    bmp = img.ConvertToBitmap()
    decorate_bitmap(bmp, sel_points, sel_lines)
    if lock is not None: lock.release()    

    dest.SetBitmap(bmp)
    if dest_top is not None:
        dest_top.image_updated()

   
def decorate_bitmap(bmp, sel_points, sel_lines):
    """
    Отрисовка пометок (точет, линий и пр...) на изображении.
    Вызывается функцией display_image.
    Аргументы:
        bmp (wx.Bitmap): изображение, изменяемое на месте.
        остальное: см. описание одноименных аргументов display_image
    """
    if len(sel_points) + len(sel_lines) == 0: return
    dc = wx.MemoryDC(bmp)
    
    #точки
    prev_color = ""
    center_circle = (MARKER_SIZE > 5 and MARKER_SIZE <= 15)
    for pt in sel_points:
        x0, y0, my_color = pt
        if prev_color != my_color:
            clr = translate_color(my_color)
            width = [1,3] [MARKER_SIZE > 15]
            dc.SetPen(wx.Pen(clr, width, wx.SOLID))
            if center_circle:
                dc.SetBrush(wx.Brush(clr))
        dc.DrawLine(x0 - MARKER_SIZE, y0, x0 + MARKER_SIZE, y0)
        dc.DrawLine(x0, y0 - MARKER_SIZE, x0, y0 + MARKER_SIZE)
        if center_circle: dc.DrawCircle(x0, y0, 3)
    
    #линии
    dc.SetBrush(wx.Brush('white', wx.TRANSPARENT))
    even_pos = True
    line = []
    for j in range(0, len(sel_lines)):
        cur_val = sel_lines[j]
        if isinstance(cur_val, str):
            #линия кончилась, рисуем
            if len(line) > 1 and len(cur_val) > 0:
                color_str = cur_val
                style_str = color_str[-1]
                if style_str in _MY_LINE_STYLES:
                    style = _MY_LINE_STYLES[style_str]
                    color_str = color_str[:-1]
                else:
                    style = wx.SOLID
                color = translate_color(color_str)
                dc.DrawLineList(line, wx.Pen(color, LINE_WIDTH, style))
            even_pos = True
            line = []
        else:
            #добавляем точку в линию
            even_pos = not even_pos
            if even_pos:
                pt = (sel_lines[j - 1], cur_val)
                if len(line) == 0:
                    line = [pt]
                elif len(line[0]) == 2:
                    line = [(line[0][0], line[0][1], pt[0], pt[1])]
                else:
                    line.append((line[-1][2], line[-1][3], pt[0], pt[1]))
    
    dc.SelectObject(wx.NullBitmap)


