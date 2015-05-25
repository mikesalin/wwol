# -*- coding: utf-8 -*-
"""
В этом модуле определен класс главного окна (NB: пока главного)
"""

import logging
import os
import threading
import math
import copy
import wx

import wxfb_output
import zoom_gui
import loading
import view
import configuration
import tester
import source_gui
import assembling
import embed_gui_images
import sel_gui
import geom

class MainVideoFrame(wxfb_output.MainVideoFrame):
    """
    Главное окно.
    
    Данные, определенные здесь:
    .zoom_dlg (ZoomDlg или None)
    .viewer (Preview-like или None) - класс, кт. реализует переключение кадров
                                      и пр.; при ошибке сбрасывется в None
    .config
    .cur_frame_num -- номер кадра, здесь нумерация всегда с 0
    .prev_mouse_x
    .prev_mouse_y
    .a_panel (view.PanelParam, параметр size игнорируется)
    .sel_ok (bool)
    .sel_data (Selection)
    .sel_callback (callable)
    .sel_dlg (SelDlg или None)
    .rect_state (bool) -- True, когда зажали мышь и рисуем
    .rect_start_corner (tuple (int, int))
    .maintain_sel_trpz_flag (int): 0 - выкл, 1 - вкл, 2 - просьба обновить
                                   после отрисовки первого кадра
    .sel_dlg_to_be_shown
    
    .HOURGLASS (wx.Bitmap)
    .SOLID_WHITE_PEN (wx.Pen)
    .INVIS_BRUSH (wx.Brush)
    """
    def __init__(self, parent):
        wxfb_output.MainVideoFrame.__init__(self,parent) #initialize parent class        
        
        #Данные:
        self.zoom_dlg = None
        self.viewer = None
        self.config = configuration.Config()
        self.cur_frame_num = 0
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.a_panel = view.PanelParam()
        self.sel_ok = False
        self.sel_data = Selection()
        self.sel_callback = None
        self.sel_dlg = None
        self.rect_state = False
        self.rect_start_corner = (0, 0)
        self.maintain_sel_trpz_flag = 0
        self.sel_dlg_to_be_shown = False
        
        self.HOURGLASS = embed_gui_images.get_hourglassBitmap()
        self.SOLID_WHITE_PEN = wx.Pen('white', view.LINE_WIDTH, wx.SOLID)
        self.INVIS_BRUSH = wx.Brush('white', wx.TRANSPARENT)
        
        tester.def_all_tests(self)
        
        #Допиливаем интерфейс:
        self.my_gauge.Show(False)
        self.my_toolbar.Enabled = False
        
    def _close_all_dialogs(self):
        "Закрывает все диалоговые окна. Все новые окна нужно вписивать сюда."
        if self.zoom_dlg is not None:
            self.zoom_dlg.close_func(None)
            self.zoom_dlg = None
        if self.sel_dlg is not None:
            self.sel_ok = False
            self._finish_selecting()
    
    def _close_func(self, event):
        "Нажали на кнопку закрыть (крестик)."
        self._close_all_dialogs()
        self._close_viewer()
        event.Skip()
        #debug info:
        logging.debug("Theads, which are alive at exit:")
        lt = threading.enumerate()
        for t in lt:
            if not t.daemon:
                logging.debug("    " + t.name)                
    
    def _close_viewer(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
    
    def _test_menu_func(self, event):
        "Меню 'Тест'"
        self.default_test()
                
    def viewer_crushed(self, message):
        """
        Обработка ошибки, возникшей при текущей работе viever.Preview и т.п.
        message - string
        """
        self._close_all_dialogs()
        msg_dlg = wx.MessageDialog(self, message, "", wx.ICON_ERROR)        
        msg_dlg.ShowModal()
        msg_dlg.Destroy()
        self._close_viewer()
        #NB: сделать функцию для замечаний, пусть запускает всплывающую плашку
        #NB(2): в след. версии -- закрыть окно
    
    def display_frame_num(self, num):
        """
        Вызывается после того, как выполнена отрисовка нового кадра и можно 
        переключить счетчик кадров.
        num -- то же, что и было передано в goto_frame
        Замечание: внутри программы считаем номера кадров с 0, а для
        пользователя - с единицы.
        """
        self.cur_frame_num = num
        label = self._frame_to_time_str(self.cur_frame_num) + " | " + \
                self._frame_to_time_str(self.config.frames_count)
        self.jump_time_tool = self._reset_tool_label(self.jump_time_tool, label)
        label = "%4d |%5d" % (self.cur_frame_num +1, self.config.frames_count)
        self.jump_frame_tool=self._reset_tool_label(self.jump_frame_tool, label)
        
        self.my_toolbar.EnableTool(self.prev_tool.GetId(), self._can_go_back())
        self.my_toolbar.EnableTool(self.next_tool.GetId(), self._can_go_fwd())
    
    def image_updated(self):
        "Вызывается после перерисовки изображения (слева или справа)"
        if self.sel_dlg_to_be_shown:
            if self.sel_dlg is not None:
                self.sel_dlg.Show()
            self.sel_dlg_to_be_shown = False
        if self.maintain_sel_trpz_flag == 2:
            self._maintain_sel_trpz_act()
            self.maintain_sel_trpz_flag = 1
            self._viewer_update_view()
                                   
    def _can_go_fwd(self):
        "Возвращает True, если можно перелистнуть на кадр вперед"
        return self.cur_frame_num + self.config.view_step \
            < self.config.frames_count
    def _can_go_back(self):
        "Возвращает True, если можно перелистнуть на кадр назад"
        return self.cur_frame_num - self.config.view_step >= 0
        
    def _frame_to_time_str(self, n):
        """
        Переводит номер кадра n в строку вида "мм:cc.мс"
        Использует self.config.fps
        Возвращает string        
        """
        t = n * 1.0 / self.config.fps
        mins = math.floor(t / 60.0)
        secs = t - mins*60
        txt = "%02.0f:%06.3f" % (mins, secs)
        return txt
    
    def _reset_tool_label(self, tool, label):
        """
        У стандартных средств wxPython какая-та проблема с простейшей функцией 
        -- поменять надпись на кнопке тулбара. Здесь идет своя реализация этой
        функции методом удалить и добавить новый
        Аргументы:
            tool -- wx.ToolBarToolBase, то, что создается wxFormBuilder-ом
            label --string
        Возвращает:
            wx.ToolBarToolBase, новый объект
        """
        #http://stackoverflow.com/questions/4315643/changing-label-in-toolbar-using-wxpython
        tid = tool.GetId()
        bmp = tool.GetBitmap()
        pos = self.my_toolbar.GetToolPos(tid)
        self.my_toolbar.DeleteTool(tid)
        new_tool = self.my_toolbar.InsertLabelTool(pos, tid, label, bmp)
        self.my_toolbar.Realize()
        return new_tool
    
    def _prev_tool_func(self, event):
        "Нажали на кнопку со стерлкой назад"
        if self.viewer is None or not self._can_go_back():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num - self.config.view_step)
    def _next_tool_func(self, event):
        "Нажали на кнопку со стрелкой вперед"
        if self.viewer is None or not self._can_go_fwd():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num + self.config.view_step)

    def _jump_frame_tool_func(self, event):
        """
        Нажали на кнопку, где написан номер кадра.
        Запрашивается номер кадра, на который надо осуществить перход.
        """
        if self.viewer is None:
            logging.debug("suddenly not available")
            return        
        dlg = wx.TextEntryDialog(self, "Номер кадра для перехода:", "",\
                                 "%d" % (self.cur_frame_num+1) )
        code = dlg.ShowModal()
        txt_res = dlg.GetValue()
        dlg.Destroy()
        if (code != wx.ID_OK): return        
        try:
            num = int(txt_res)
            if (num < 1) or (num > self.config.frames_count):
                raise ValueError
        except ValueError:
            logging.warning("Bad input")
            dlg = wx.MessageDialog(self, "Неверный ввод", "", wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()  
            return      
        self.viewer.goto_frame(num - 1)

    def _jump_time_tool_func(self, event):
        """
        Нажали на кнопку, где написано текущее время.
        Запршивается время, на которое надо осуществить перход.
        """
        if self.viewer is None:
            logging.debug("suddenly not available")
            return
        dlg = wx.TextEntryDialog(self,
                                 "Время для перехода в формате мин:сек.мс :",
                                 "",
                                 self._frame_to_time_str(self.cur_frame_num) )
        code = dlg.ShowModal()
        txt_res = dlg.GetValue()
        dlg.Destroy()
        if (code != wx.ID_OK): return        
        mm_ss = txt_res.split(":") # mm- минуты, cc - секунды с дробной частью
        success = False
        if (len(mm_ss) == 2):
            mm_txt = mm_ss[0]
            ss_txt = mm_ss[1]
            success = True
        if (len(mm_ss) == 1):
            mm_txt = "0"
            ss_txt = mm_ss[0]
            success = True
        if success:
            try:
                mm = int(mm_txt)
                ss = float(ss_txt)                
            except ValueError:
                success = False
        if success:
            t = mm * 60 + ss
            n = int(round (t * self.config.fps))
            if (n < 0) or (n >= self.config.frames_count):
                success = False
        if not success:
            logging.warning("Bad input")
            dlg = wx.MessageDialog(self, "Неверный ввод", "", wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()  
            return      
        self.viewer.goto_frame(n)

    def _zoom_tool_func(self, event):
        "Нажали на кнопку с луппой"
        if self.zoom_dlg is not None:
            self.zoom_dlg.reset_parents_cursor()
            self.zoom_dlg.Destroy()
            self.zoom_dlg = None
        if self.zoom_tool.IsToggled():
            self.zoom_dlg = zoom_gui.ZoomDlg(self)
            self.zoom_dlg.Show() #wxPython3: ShowWithoutActivating
            bar_pos = self.my_toolbar.GetScreenPosition()
            tool_index = self.my_toolbar.GetToolPos(self.zoom_tool.GetId())
            tool_size = self.my_toolbar.GetToolSize()
            ofs = 200
            pos = (bar_pos[0] + tool_size[0] * tool_index + ofs,
                   bar_pos[1] + tool_size[1])
            self.zoom_dlg.Move(pos)
        self._rebind_mouse_events("a")
        self._rebind_mouse_events("b")
        self._rebind_mouse_wheel_event()
        if self.sel_dlg is not None: self.sel_dlg.adjust()
        self.SetStatusText("")
    
    def _mouse_drag_a(self, event):
        """
        Обработчик событий мыши (EVT_MOUSE_EVENTS) для картинки A (a_bmp)
        в режиме манипуляций мышью.
        """
        if self.viewer is None: return
        if event.LeftDown():
            self.prev_mouse_x = event.GetX()
            self.prev_mouse_y = event.GetY()
            event.Skip()
        if event.Dragging() and event.LeftIsDown():
            dx = event.GetX() - self.prev_mouse_x
            dy = event.GetY() - self.prev_mouse_y
            self.a_panel.pos = (self.a_panel.pos[0] - dx,
                                self.a_panel.pos[1] - dy)
            self._viewer_update_view()
            self.prev_mouse_x = event.GetX()
            self.prev_mouse_y = event.GetY()

    def _mouse_zoom_a(self, event):
        """
        Обработчик событий колесика мыши (EVT_MOUSEWHEEL)
        в режиме манипуляций мышью.
        """
        ZOOM_STEP = 0.4142
        prev_zoom = self.a_panel.zoom
        new_zoom = prev_zoom * (1.0 + ZOOM_STEP)** \
          (1.0 * event.GetWheelRotation() / event.GetWheelDelta() )
        self.a_panel.zoom = new_zoom
        self.zoom_dlg.set_zoom_choice("a", new_zoom)

        mpos = event.GetPositionTuple()
        new_pos = [0, 0]
        for n in range(0,2):
            new_pos[n] = -mpos[n] + (self.a_panel.pos[n] + mpos[n]) * \
                                  new_zoom  / prev_zoom
        self.a_panel.pos = (new_pos[0], new_pos[1])
        
        self._viewer_update_view()
        # NB: потом надо как-то разобраться с левой-правой картинкой
    
    def select_ab_side(self, side, choices, *arg):
        """
        Аргументы:
          side (string): "a" или "b"
          choices (list или tuple размера 2)
          или есть 2ой варинат синтаксиса:  select_ab_side(side, if_a, if_b)
        Возвращает: choices[0] или choices[1]
        Исключения: ValueError, если side неправильный
        """
        if len(arg) > 0:
            choices = (choices, arg[0])
        if (side == "a") or (side == "A"):
            return choices[0]
        if (side == "b") or (side == "B"):
            return choices[1]
        raise ValueError("side must be \"a\" or \"b\"")
    
    def _rebind_mouse_events(self, side = None, func = None):
        """
        Изменить обработчик всех событий мыши, кроме кручения колесика, для 
        картинок (a_bmp или b_bmp).
        Аргументы:
          side - string, "a" или "b";  если None, то последовательно "a" и "b"
          func - callable(event). Будет вызываться для всех событий
                 мыши, кроме кручения колесика. Если None, то включается
                 стандартный обработчик для текущего состояния окна.
        Возвращает: ничего
        Исключения: ValueError, если side неправильный
        """
        if side is None :
            self._rebind_mouse_events("a", func)
            self._rebind_mouse_events("b", func)
            return
        (control, side_is_a) = self.select_ab_side(
            side, ((self.a_bmp, True), (self.b_bmp, False)))
        control.Unbind(wx.EVT_MOUSE_EVENTS)
        if side_is_a:
            if func is None and self.zoom_tool.IsToggled():
                func = self._mouse_drag_a
            if func is None and self.sel_data.mode != Selection.OFF:
                SEL_FUNCS = {Selection.SINGLE_POINT_A: self._select_point_a,
                             Selection.MULTIPLE_POINTS_A: self._select_point_a,
                             Selection.SINGLE_RECT_A: self._select_rect_a,
                             Selection.MULTIPLE_RECTS_A: self._select_rect_a }
                func = SEL_FUNCS[self.sel_data.mode]
        if func is not None:
            control.Bind(wx.EVT_MOUSE_EVENTS, func)
    
    def _rebind_mouse_wheel_event(self, func = None):
        """
        Изменить обработчик событий вращения колесика мыши
        Аргументы:
          func - callable(event) или None. Будет вызываться при кручении
                 колесика где угодно на поле окна. Если None, то включается
                 стандартный обработчик в зависимоти от того, нажата кнопка
                 с луппой или нет.
        Возвращает: ничего
        """
        self.Unbind(wx.EVT_MOUSEWHEEL)
        if func is None:
            if self.zoom_tool.IsToggled():
                func = self._mouse_zoom_a
        if func is not None:
            self.Bind(wx.EVT_MOUSEWHEEL, func)

    def _size_func(self, event):
        self.Layout()
        self._viewer_update_view()
        event.Skip()
    
    def enter_preview(self):
        """
        Переход в режим Preview.
        Инициализацирует loader и viewer на основе self.config
        Возвращает: ничего
        """
        self._close_viewer()
        loader = assembling.make_loader(self.config, self)
        if loader is None:
            self.viewer_crushed("Не удалось запустить просмотр")
            return
        self.viewer = view.Preview(self, loader, self.config.frames_range[0])
        self.my_toolbar.Enabled = True
        if self.cur_frame_num < self.config.frames_count \
           and self.cur_frame_num > 0:
            self.viewer.goto_frame(self.cur_frame_num)
            
    def _config_source_menu_func(self, event):
        "Нажали меню Параметры -> Источник"
        self._close_all_dialogs()
        dlg = source_gui.SourceDlg(self)
        dlg.ShowModal()
    
    def hourglass(self):
        """
        Рисует песочные часы на левой картинке поверх всего, что там есть.
        Это состояние не сохраняется после перерисовки окна.
        """
        dc = wx.ClientDC(self.a_bmp)
        dc.DrawBitmap(self.HOURGLASS, 10, 10, True)

    def _select_point_a(self, event):
        """
        Обработка событий мыши в режиме выбора одной точки / нескольких точек
        на изображении 'a'.
        """
        event.Skip()
        if self.viewer is None: return
        if event.Moving():
            self.SetStatusText("%d, %d" %
                self.viewer.backtrace_a(event.GetX(), event.GetY(), True))
        if not event.LeftDown(): return
        rv = self.viewer.backtrace_a(event.GetX(), event.GetY())
        if rv is None: return
        if self.sel_data.mode == Selection.SINGLE_POINT_A:
            self.sel_data.sel_item = rv
        else:
            self.sel_data.points_a.append(rv)
        self.sel_dlg.adjust()
        self._viewer_update_view()
    
    def _select_rect_a(self, event):
        "Обработка событий мыши в режиме выбора прямоугольника(ов) на 'a'."
        x1 = event.GetX()
        y1 = event.GetY()
        if event.LeftDown():
            self.rect_start_corner = (x1, y1)
            self.prev_mouse_x = x1
            self.prev_mouse_y = y1
            self.rect_state = True
            event.Skip()
        if event.Dragging() and self.rect_state:
            self._redraw_rect("a", x1, y1)
            x0_, y0_ = self.viewer.backtrace_a(self.rect_start_corner[0],
                                               self.rect_start_corner[1],
                                               True)
            x1_, y1_ = self.viewer.backtrace_a(x1, y1, True)
            self.SetStatusText(
                "%d, %d -- %d, %d  (%d x %d)" %
               (x0_, y0_, x1_, y1_, abs(x1_ - x0_) + 1, abs(y1_ - y0_) + 1))
            self.prev_mouse_x = x1
            self.prev_mouse_y = y1
        if event.LeftUp() and self.rect_state:
            self.rect_state = False
            self._redraw_rect("a")
            self.SetStatusText("")
            # кладем в список:
            if self.viewer is None: return
            res = self.viewer.backtrace_rect_a(self.rect_start_corner[0],
                                               self.rect_start_corner[1],
                                               x1, y1)
            if res is None: return
            if self.sel_data.mode == Selection.SINGLE_RECT_A:
                self.sel_data.sel_item = res
            else:
                self.sel_data.rects_a.append(res)
            self.sel_dlg.adjust()
            self._maintain_sel_trpz_act()
            self._viewer_update_view()
        if event.Moving():
            if self.rect_state:
                self.rect_state = False
                self._redraw_rect("a")
            self.SetStatusText("%d, %d" %
                self.viewer.backtrace_a(x1, y1, True))
    
    def _redraw_rect(self, side, x1 = None, y1 = None):
        """
        Рисует прямоугольники XOR-ом на a_bmp/b_bmp:
          1. от rect_start_corner до prev_mouse_x,y
          2. от rect_start_corner до x1,y1 (если x1 не None)
        """
        OFFSET = 6
        rect_list = []
        xy_list = [(self.prev_mouse_x, self.prev_mouse_y)]
        if x1 is not None:
            xy_list.append((x1, y1))
        for xy in xy_list:
            xx = [self.rect_start_corner[0], xy[0]]
            x0 = min(xx)
            w = max(xx) - x0
            yy = [self.rect_start_corner[1], xy[1]]
            y0 = min(yy)
            h = max(yy) - y0
            if w > 1 and h > 1:
                rect_list.append((x0 + OFFSET, y0 + OFFSET, w, h))

        st_bmp = self.select_ab_side(side, self.a_bmp, self.b_bmp)
        dc = wx.ClientDC(st_bmp)
          #bmp = st_bmp.GetBitmap()  -- способ обойтись без OFFSET
          #dc = wx.MemoryDC(bmp)
        lf = dc.GetLogicalFunction()
        dc.SetLogicalFunction(wx.XOR)
        dc.DrawRectangleList(rect_list, self.SOLID_WHITE_PEN, self.INVIS_BRUSH)
        dc.SetLogicalFunction(lf)
          #dc.SelectObject(wx.NullBitmap)
          #st_bmp.SetBitmap(bmp)

    def start_selecting(self, mode, callback, info = ""):
        """
        Включает режим выделения чего-либо (точек, прямоугольников, ...) мышью.
        Аргументы:
           mode: новое значение для Selection.mode
           callback (callable): функция, котороя будет вызвана по завершению
                                работы режима выделения.
           info (string): описание, которое будет видно в маленьком диалоговом
                         окне, пустая строка -- использовать стандартный текст.
        Перед вызовом данного метода требуется:
          - вызвать enter_preview() или выполнить аналогичные действия
          - указать изначальный выбор в self.sel_data (если нужно)
        Результат работы будет содержаться в sel.sel_data и self.sel_ok (True 
        -- пользователь нажал 'готово', False -- 'отмена')
        """
        if self.sel_data.mode != Selection.OFF:
            logging.debug("Already in selection mode !")
            return
        if self.viewer is None:
            return
            # NB: предложить запустить Предпростмотр
        self.sel_data.mode = mode
        self.sel_callback = callback
        self.sel_ok = False
        self.rect_state = False
        self.maintain_sel_trpz_flag = 0
        self.sel_dlg = sel_gui.SelDlg(self, info)
        self.sel_dlg.Move(self.b_bmp.GetScreenPosition())
        self.sel_dlg_to_be_shown = True
        self._rebind_mouse_events()
        self._viewer_update_view()
   
    def _finish_selecting(self):
        """
        Вызывается при выходе из режима выделения.
        Предполагаетя, что причина выхода -- через 'готово' или через 'отмену'
        -- уже должна сидеть в self.sel_ok .
        """
        if self.sel_dlg is not None:
            self.sel_dlg.Destroy()
            self.sel_dlg = None
        self.sel_data.mode = Selection.OFF
        self._rebind_mouse_events()
        self._viewer_update_view()
        self.SetStatusText("")
        self.maintain_sel_trpz_flag = 0
        if self.sel_callback is not None:
            self.sel_callback()
            self.sel_callback = None
        
    def maintain_sel_trpz(self):
        """
        Включает режим, поддержания .sel_data.trpz в соответствие с
        .sel_data.rects_a. Следует вызывать после .start_selecting .
        """
        self.maintain_sel_trpz_flag = 1
        self._maintain_sel_trpz_act()
        
    def _maintain_sel_trpz_act(self):
        """
        Приводит .sel_data.trpz в соответствие с .sel_data.rects_a, если
        включен такой режим ( см. .maintain_sel_trpz() ).
        Здесь выполняется однократное действие.
        """
        if self.maintain_sel_trpz_flag == 0: return
        img_size = (0, 0)
        if self.viewer is not None:
            img_size = self.viewer.get_raw_img_size()
        if img_size == (0, 0):
            self.sel_data.trpz[:] = []
            self.maintain_sel_trpz_flag = 2
            return
        rects = self.sel_data.rects_a
        if self.sel_data.mode == Selection.SINGLE_RECT_A:
            rects = copy.deepcopy(rects)
            rects.append(self.sel_data.sel_item)
        self.sel_data.trpz = list(
            geom.trapezoid_inside_rectangle(rect,
                                            self.config.proj_coef,
                                            img_size) for rect in rects)
    
    def _viewer_update_view(self):
        "Перерисовка. Вызов .viewer.update_view с проверкой на None"
        if self.viewer is not None:
            self.viewer.update_view()


class Selection:
    """
    Содержит данные по выделенным на изображении точкам и площадям.
    Когда речь идет о точках на изображении 'а', то координаты соответствуют
    пикселям исходного (не масштабированного и не сдвинутого) изображения.
    .mode = .OFF
            .SINGLE_POINT_A
            .MULTIPLE_POINTS_A
            .SINGLE_RECT_A
            .MULTIPLE_RECTS_A
    .points_a ( list of tuples (int,int) ~ [ (x, y), ... ] ):
        координаты точек, выделенных на изображении 'a'.
        В режиме mode = MULTIPLE_POINTS_A:
          в начале работы -- умолчательный выбор,
          в конце работы  -- результат выбора пользователя.
        В других режимах:
          просто точки для отображения.
    .rects_a ( list of tuples (4 * int) ~ [ (x1, y1, x2, y1), ... ] ):
        координаты верхнего-левого (x1,y1) и нижнего-правого (x2,y2) углов
        прямоугольника на изображении 'a'.
        В режиме mode = MULTIPLE_RECTS_A:
          в начале работы -- умолчательный выбор,
          в конце работы  -- результат выбора пользователя.
        В других режимах:
          просто точки для отображения.
    .sel_item (тип соответствует одному элементу points_a / rects_a....):
        выделенный элемент, когда требуется выделить только один элемент,
        актуально в режимах mode = SINGLE_...,
        в начале работы -- изначально выбранный элемент, который пользователь
                           может изменять (редактировать) или None
        в конце работы  -- результат выбора пользователя.
    .trpz (list of tuples, один элемент списка -- 
           выход geom.trapezoid_inside_rectangle):
        список трапеций, получающихся проецированием областей из rects_a.
        Длина списка может быть: 0, len(rects_a)  len(rects_a) + 1, где
        последний элемент относится к sel_item.
        Пользователю не нужно самому заполнять этот список -- нужно вызвать
        MainVideoFrame.maintain_sel_trpz() и класс будет сам отслеживать
        изменения rects_a и приводить trpz в соответствие.
    """
    OFF = 0
    SINGLE_POINT_A = 1
    MULTIPLE_POINTS_A = 2
    SINGLE_RECT_A = 3
    MULTIPLE_RECTS_A = 4
    
    def __init__(self):
        self.mode = self.OFF
        self.points_a = []
        self.rects_a = []
        self.sel_item = None
        self.trpz = []


def main():
    logging.basicConfig(format="%(levelname)s: %(module)s: %(message)s",
      level=logging.DEBUG)
    logging.debug('Using wxPython version ' + wx.version())
    app = wx.App()
    wx.Log_EnableLogging(False)
    main_video_frame = MainVideoFrame(None)
    main_video_frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()

