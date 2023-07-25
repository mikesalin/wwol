# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"В этом модуле определен класс главного окна: MainVideoFrame"

# Код требует рефакторинга: 
# 1. Оформить табы в отдельный класс

import logging
import os
import threading
from math import *
import copy
import sys
import string
import json
import numpy as np
import wx

from . import wxfb_output
from .mvf_aux_classes import *

from . import zoom_gui
from ..engine import loading
from ..engine import loading2
from ..engine import view
from ..engine import configuration
ConfigError = configuration.ConfigError
from . import source_gui
from ..common import embed_gui_images
from . import sel_gui
from ..engine import geom
from ..common.my_encoding_tools import *
from ..grapher.grapher_gui import GrapherMain
from .. import __version__ as ABOUT_VERSION
from .. import year as ABOUT_YEAR
from ..engine.processing import Processing
from . import points_gui

class MainVideoFrame(wxfb_output.MainVideoFrame):
    """
    Главное окно.
    
    Данные, определенные здесь:
    .zoom_dlg (ZoomDlg или None)
    .viewer (Preview-like или None) - класс, кт. реализует переключение кадров
                                      и пр.; при ошибке сбрасывется в None
    .config
    .cur_frame_num -- номер кадра, здесь нумерация всегда с 0
    .prev_mouse_x, _y, _x_b, _y_b
    .zomming_a
    .a_panel (view.PanelParam, параметр size игнорируется)
    .b_panel
    .sel_ok (bool)
    .sel_data (Selection)
    .sel_callback (callable)
    .sel_dlg (SelDlg или None)
    .rect_state (bool) -- True, когда зажали мышь и рисуем
    .rect_start_corner (tuple (int, int))
    .maintain_sel_trpz_flag (int): 0 - выкл, 1 - вкл, 2 - просьба обновить
                                   после отрисовки первого кадра
    .sel_dlg_to_be_shown (bool)
    .config_notebook_image_list (wx.ImageList)
    .json_editing_enabled (bool)
    .json_editing_sect (str)
    .is_first_frame_shown (bool): False, если после создания нового viewer-а
                                  не было отрисовано ни одного кадра (не вызвался
                                  dislay_frame_num). Или если viewer=None
    .project_changed (bool)
    .project_filename (str)
    .json_controls_suspend_state (tuple 3 x bool): хранить состояние Enabled
                                  некоторых элементов управления, которое было
                                  до start_selecting
    .is_closing (bool):  чтобы отменить отбработку некоторых событий (например, 
                         _config_notebook_changing_func) когда уже закрываемся
    .prev_power_spec_path (str)
    .default_scrshot_file_type (int)
    .default_scrshot_dir (str)
    .default_scrshot_jpeg_quality_s (str)
    .scrshot_tooltip_head (unicode)
    .express_spec_wnd
    .points_dlg (PointsDlg / None)
    .user_points (np.ndarray)  многоцелевой массив точек Nx2 или Nx4: x, y на A, x, y на B
    .temp_img_monitor (TempImagesMonitoringParam)
    
    .HOURGLASS (wx.Bitmap)
    .SOLID_WHITE_PEN (wx.Pen)
    .INVIS_BRUSH (wx.Brush)
    .ENABLED_WHEN_VIEWING_IDS (list)
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
        self.prev_mouse_x_b = 0
        self.prev_mouse_y_b = 0
        self.zooming_a = True
        self.a_panel = view.PanelParam()
        self.b_panel = view.PanelParam()
        self.sel_ok = False
        self.sel_data = Selection()
        self.sel_callback = None
        self.sel_dlg = None
        self.rect_state = False
        self.rect_start_corner = (0, 0)
        self.maintain_sel_trpz_flag = 0
        self.sel_dlg_to_be_shown = False
        self.json_editing_enabled = False
        self.json_editing_sect = ""
        self.is_first_frame_shown = False
        self.project_changed = False
        self.project_filename = ""
        self.is_closing = False
        self.prev_power_spec_path = ""
        self.default_scrshot_file_type = 0
        self.default_scrshot_dir = ''
        self.default_scrshot_jpeg_quality_s = '90'
        self.scrshot_tooltip_head = self.my_toolbar.GetToolShortHelp(
            self.scrshot_tool.GetId())
        self._update_scrshot_tooltip()
        self.express_spec_wnd = None
        self.points_dlg = None
        self.user_points = np.array([ ])
        self.temp_img_monitor = TempImagesMonitoringParam()
        
        self.HOURGLASS = embed_gui_images.get_hourglassBitmap()
        self.SOLID_WHITE_PEN = wx.Pen('white', view.LINE_WIDTH, wx.SOLID)
        self.INVIS_BRUSH = wx.Brush('white', wx.TRANSPARENT)
        
        #Допиливаем интерфейс:
        
        # картинки на кнопках:
        self.my_toolbar.SetToolNormalBitmap(self.menu_tool.GetId(),
                                            embed_gui_images.get_menu3Bitmap())
        self.my_toolbar.SetToolNormalBitmap(self.preview_tool.GetId(),
                                            embed_gui_images.get_playBitmap())
        self.my_toolbar.SetToolNormalBitmap(
            self.proc_tool.GetId(),
            embed_gui_images.get_double_playBitmap())
        self.my_toolbar.SetToolNormalBitmap(
            self.scrshot_tool.GetId(),
            embed_gui_images.get_scrshotBitmap())
        self.my_toolbar.SetToolNormalBitmap(self.view_step_tool.GetId(),
                                            embed_gui_images.get_stepBitmap())
        self.my_toolbar.SetToolNormalBitmap(self.points_tool.GetId(),
                                            embed_gui_images.get_pointsBitmap())

        # картинки на табах:
        tab_bmps = [embed_gui_images.get_videoBitmap(),
                      embed_gui_images.get_eyeBitmap(),
                      embed_gui_images.get_area2Bitmap(),
                      embed_gui_images.get_power_spec_buttonBitmap(),
                      embed_gui_images.get_scrshotBitmap(),
                      embed_gui_images.get_colorbarBitmap(),
                      embed_gui_images.get_filterBitmap()]
        self.config_notebook_image_list = wx.ImageList(20, 20)
        for bmp in tab_bmps:
           self.config_notebook_image_list.Add(bmp)
        self.config_notebook.SetImageList(self.config_notebook_image_list)
        for n_page in range(0, len(tab_bmps)):
            self.config_notebook.SetPageImage(n_page, n_page)
            self.config_notebook.SetPageText(n_page, "")
        
        self.ENABLED_WHEN_VIEWING_IDS = [t.GetId() for t in \
            [self.prev_tool, self.next_tool, self.jump_frame_tool,
             self.jump_time_tool, self.zoom_tool] ]
        for tid in self.ENABLED_WHEN_VIEWING_IDS:
            self.my_toolbar.EnableTool(tid, False)
        self.a_footer_static_text.SetLabel('')
        self.b_footer_static_text.SetLabel('')
        
        self._config_notebook_changed_func(None)

    def _close_all_dialogs(self):
        "Закрывает все диалоговые окна. Все новые окна нужно вписывать сюда."
        if self.zoom_dlg is not None:
            self.zoom_dlg.close_func(None)
            self.zoom_dlg = None
        if self.sel_dlg is not None:
            self.sel_ok = False
            self._finish_selecting()
        if self.points_dlg is not None:
            self.points_dlg.close_func(None)
    
    def _close_func(self, event):
        "Нажали на кнопку закрыть (крестик)."
        if not self._ensure_saved():
            event.Veto()
            return
        
        #"аккурантно" закрыть все окна графера
        for wnd in self.GetChildren():
            if isinstance(wnd, GrapherMain):
                logging.debug("Auto-close '" + wnd.GetTitle() + "'")
                if not wnd.Close():
                    event.Veto()
                    return
        
        event.Skip()
        self.is_closing = True
                
        self._close_all_dialogs()
        self._close_viewer()

        #debug info:
        logging.debug("Threads, which are alive at exit:")
        lt = threading.enumerate()
        for t in lt:
            if not t.daemon:
                logging.debug("    " + t.name)                
    
    def _close_viewer(self):
       "корректно убиваем класс .view"
       if self.viewer is not None:
           self.viewer.close()
           self.viewer = None
       self._viewer_stopped()
   
    def _viewer_stopped(self):
        """
        Изменение состояния ГУИ, когда закрыли/рухнул просмотрщик.
        Если Вы вызываете _close_viewer, то он вызовет _viewer_stoped автоматом
        """
        self._close_all_dialogs()
        for tid in self.ENABLED_WHEN_VIEWING_IDS:
            self.my_toolbar.EnableTool(tid, False)
        self.is_first_frame_shown = False
        self.sel_dlg_to_be_shown = False
        self.my_toolbar.ToggleTool(self.preview_tool.GetId(), False)
        self.my_toolbar.ToggleTool(self.proc_tool.GetId(), False)
        self.a_footer_static_text.SetLabel('')
        wx.CallAfter(lambda: self._clear_screen())
    
    def viewer_crushed(self, message):
        """
        Обработка ошибки, возникшей при текущей работе viever.Preview и т.п.
        message - string
        """
        self._close_viewer()
        msg_dlg = wx.MessageDialog(self, U(message), "", wx.ICON_ERROR)        
        msg_dlg.ShowModal()
        msg_dlg.Destroy()
        
    def display_warn(self, message):
        """
        Отображение замечаний с помощью всплывающей плашки.
        Длинные сообщения укорачиваются и полная версия помещается в tooltip.
        """
        #определяем макс. длину текста
        one_line_msg, dummy = limit_text_len(
            message, 100500, allow_multiline = False)
        ww = wx.ClientDC(self).GetPartialTextExtents(U(one_line_msg))
        try:
            max_width = self.GetSizeTuple()[0] - 150
            max_len = ww.index(next(w for w in ww if w > max_width))
        except StopIteration:
            max_len = len(U(one_line_msg))
        
        short_msg, has_long_version = limit_text_len(
            message, max_len, allow_multiline = False)
        if has_long_version:
            self.my_info_bar.SetToolTipString(U(message))
        else:
            self.my_info_bar.SetToolTip(None)

        self.my_info_bar.ShowMessage(U(short_msg))
    
    def display_frame_num(self, num):
        """
        Вызывается после того, как выполнена отрисовка нового кадра и можно 
        переключить счетчик кадров.
        num -- то же, что и было передано в goto_frame
        Примечание: внутри программы считаем номера кадров с 0, а для
        пользователя - с единицы.
        """
        self.cur_frame_num = num
        
        # подставить номер кадра в ГУИ, куда надо
        label = self._frame_to_time_str(self.cur_frame_num) + " | " + \
                self._frame_to_time_str(self.config.frames_count)
        self.jump_time_tool = self._reset_tool_label(self.jump_time_tool, label)
        label = "%4d |%5d" % (self.cur_frame_num +1, self.config.frames_count)
        self.jump_frame_tool=self._reset_tool_label(self.jump_frame_tool, label)
        
        # включить/выключить кнопки:
        self.my_toolbar.EnableTool(self.prev_tool.GetId(), self._can_go_back())
        self.my_toolbar.EnableTool(self.next_tool.GetId(), self._can_go_fwd())
        
        if self.is_first_frame_shown == False: self._first_frame_shown()
    
    def _first_frame_shown(self):
        """
        Некоторая инициализация при отрисовке первого кадра после создания
        нового viewer-а 
        """
        self.is_first_frame_shown = True
        
        prev_tool_id = self.prev_tool.GetId()
        next_tool_id = self.next_tool.GetId()
        for tool_id in self.ENABLED_WHEN_VIEWING_IDS:
            if tool_id in [prev_tool_id, next_tool_id]: continue
            self.my_toolbar.EnableTool(tool_id, True)
            
        if self.viewer is not None:
            wh = self.viewer.get_raw_img_size()
            a_footer_text = "Вход: %dx%d | %0.3f кадров/сек" \
                % ((self.viewer.get_raw_img_size()) + (self.config.fps,))
            self.a_footer_static_text.SetLabel(U(a_footer_text))

        if self.maintain_sel_trpz_flag == 2:  # было в image_updated
            self._maintain_sel_trpz_act()
            self.maintain_sel_trpz_flag = 1
            self._viewer_update_view()
    
    def image_updated(self):
        "Вызывается после перерисовки изображения (слева или справа)"
        if self.sel_dlg_to_be_shown:
            if self.sel_dlg is not None:
                self.sel_dlg.Show()
            self.sel_dlg_to_be_shown = False
                                   
    def _can_go_fwd(self):
        "Возвращает True, если можно перелистнуть на кадр вперед"
        return self.cur_frame_num + self.config.button_step \
            < self.config.frames_count
    def _can_go_back(self):
        "Возвращает True, если можно перелистнуть на кадр назад"
        return self.cur_frame_num - self.config.button_step >= 0
        
    def _frame_to_time_str(self, n):
        """
        Переводит номер кадра n в строку вида "мм:cc.мс"
        Использует self.config.fps
        Возвращает string        
        """
        t = n * 1.0 / self.config.fps
        mins = floor(t / 60.0)
        secs = t - mins*60
        txt = "%02.0f:%06.3f" % (mins, secs)
        return txt
    
    def _reset_tool_label(self, tool, label):
        """
        У стандартных средств wxPython какая-та проблема с простейшей функцией 
        -- поменять надпись на кнопке тулбара. Здесь идет своя реализация этой
        функциональности методом удалить и добавить новую кнопку
        Аргументы:
            tool (wx.ToolBarToolBase): то, что создается wxFormBuilder-ом
            new_label (string или None): если None, то сохраняет старую надпись
            new_bitmap (wx.Bitmap или None): если None, то сохраняет старое
        Возвращает:
            wx.ToolBarToolBase, новый объект
        """
        #http://stackoverflow.com/questions/4315643/changing-label-in-toolbar-using-wxpython
        tid = tool.GetId()
        bmp = tool.GetNormalBitmap()
        pos = self.my_toolbar.GetToolPos(tid)
        self.my_toolbar.DeleteTool(tid)
        new_tool = self.my_toolbar.InsertLabelTool(pos, tid, label, bmp)
        self.my_toolbar.Realize()
        return new_tool
    
    def _prev_tool_func(self, event):
        "Нажали на кнопку со стрелкой назад"
        if self.viewer is None or not self._can_go_back():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num - self.config.button_step)
    def _next_tool_func(self, event):
        "Нажали на кнопку со стрелкой вперед"
        if self.viewer is None or not self._can_go_fwd():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num + self.config.button_step)

    def _notify_bad_input_simply(self):
        dlg = wx.MessageDialog(self, "Invalid input value", "", wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()  

    def _jump_frame_tool_func(self, event):
        """
        Нажали на кнопку, где написан номер кадра.
        Запрашивается номер кадра, на который надо осуществить перход.
        """
        if self.viewer is None:
            logging.debug("suddenly not available")
            return        
        dlg = wx.TextEntryDialog(self, "Number of frame:", "",\
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
            self._notify_bad_input_simply()
            return      
        self.viewer.goto_frame(num - 1)

    def _jump_time_tool_func(self, event):
        """
        Нажали на кнопку, где написано текущее время.
        Запрашивается время, на которое надо осуществить переход.
        """
        if self.viewer is None:
            logging.debug("suddenly not available")
            return
        dlg = wx.TextEntryDialog(self,
                                 "Time position in a form of min:sec.ms :",
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
            self._notify_bad_input_simply()
            return      
        self.viewer.goto_frame(n)

    def _zoom_tool_func(self, event):
        "Нажали на кнопку с лупой"
        if self.zoom_dlg is not None:
            self.zoom_dlg.reset_parents_cursor()
            self.zoom_dlg.Destroy()
            self.zoom_dlg = None
        if self.zoom_tool.IsToggled():
            self.zoom_dlg = zoom_gui.ZoomDlg(self)
            self.zoom_dlg.ShowWithoutActivating()
            px, py = self.b_bmp.GetScreenPosition().Get()
            self.zoom_dlg.Move(wx.Point(px - 180, py))
        self._rebind_mouse_events()
        self._rebind_mouse_wheel_event()
        if self.sel_dlg is not None: self.sel_dlg.adjust()
        self.SetStatusText("")
    
    def _mouse_drag(self, event, side):
        """
        Обработчик событий мыши для картинок в режиме манипуляций мышью.
        """
        if self.viewer is None: return

        side_is_a = (side == "a")
        if side_is_a:
            prev_mouse_x = self.prev_mouse_x
            prev_mouse_y = self.prev_mouse_y
            panel = self.a_panel
        else:
            prev_mouse_x = self.prev_mouse_x_b
            prev_mouse_y = self.prev_mouse_y_b
            panel = self.b_panel

        if event.LeftDown():
            prev_mouse_x = event.GetX()
            prev_mouse_y = event.GetY()
            event.Skip()
        if event.Dragging() and event.LeftIsDown():
            dx = event.GetX() - prev_mouse_x
            dy = event.GetY() - prev_mouse_y
            panel.pos = (panel.pos[0] - dx,
                         panel.pos[1] - dy)
            self._viewer_update_view()
            prev_mouse_x = event.GetX()
            prev_mouse_y = event.GetY()
        self.zooming_a = side_is_a

        if side_is_a:
            self.prev_mouse_x = prev_mouse_x
            self.prev_mouse_y = prev_mouse_y
        else:
            self.prev_mouse_x_b = prev_mouse_x
            self.prev_mouse_y_b = prev_mouse_y

    
    def _mouse_drag_a(self, event):
        """
        Обработчик событий мыши (EVT_MOUSE_EVENTS) для картинки A (a_bmp)
        в режиме манипуляций мышью.
        """
        self._mouse_drag(event, "a")

    def _mouse_drag_b(self, event):
        self._mouse_drag(event, "b")
    
    def _mouse_zoom(self, event):
        """
        Обработчик событий колесика мыши (EVT_MOUSEWHEEL)
        в режиме манипуляций мышью.
        """
        ZOOM_STEP = 0.4142

        if self.zooming_a:
            panel = self.a_panel
        else:
            panel = self.b_panel
        mpos = event.GetPositionTuple()
        
        prev_zoom = panel.zoom
        new_zoom = prev_zoom * (1.0 + ZOOM_STEP)** \
          (1.0 * event.GetWheelRotation() / event.GetWheelDelta() )
        panel.zoom = new_zoom
        self.zoom_dlg.set_zoom_choice(["a", "b"][not self.zooming_a], new_zoom)

        new_pos = [0, 0]
        for n in range(0,2):
            new_pos[n] = int(round(-mpos[n] + (panel.pos[n] + mpos[n]) * 
                         new_zoom  / prev_zoom))
        panel.pos = (new_pos[0], new_pos[1])
        
        self._viewer_update_view()
    
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
    
    def _rebind_mouse_events(self):
        """
        Изменить обработчик событий мыши (кроме кручения колесика), для 
        картинок (a_bmp и b_bmp).
        """
        for side_is_a in [True, False]:
            control = [self.b_bmp, self.a_bmp] [side_is_a]
            control.Unbind(wx.EVT_MOUSE_EVENTS)
            func = None
            if func is None and self.zoom_tool.IsToggled():
                if side_is_a:
                    func = self._mouse_drag_a
                else:
                    func = self._mouse_drag_b
            if func is None and self.sel_data.mode != Selection.OFF:
                SEL_FUNCS = {Selection.SINGLE_POINT_A: (self._select_point_a, None),
                             Selection.MULTIPLE_POINTS_A: (self._select_point_a, None),
                             Selection.SINGLE_RECT_A: (self._select_rect_a, None),
                             Selection.MULTIPLE_RECTS_A: (self._select_rect_a, None),
                             Selection.SINGLE_POINT_B: (None, self._select_point_b),
                             Selection.MULTIPLE_POINTS_B: (None, self._select_point_b) }
                func = SEL_FUNCS[self.sel_data.mode][not side_is_a]
            if func is not None:
                control.Bind(wx.EVT_MOUSE_EVENTS, func)
    
    def _rebind_mouse_wheel_event(self, func = None):
        """
        Изменить обработчик событий вращения колесика мыши
        Аргументы:
          func - callable(event) или None. Будет вызываться при кручении
                 колесика где угодно на поле окна. Если None, то включается
                 стандартный обработчик в зависимости от того, нажата кнопка
                 с лупой или нет.
        Возвращает: ничего
        """
        self.Unbind(wx.EVT_MOUSEWHEEL)
        if func is None:
            if self.zoom_tool.IsToggled():
                func = self._mouse_zoom
        if func is not None:
            self.Bind(wx.EVT_MOUSEWHEEL, func)

    def _size_func(self, event):
        "Изменение размеров окна или передвижение разделителя"
        #self.Layout()
        wx.CallAfter(self._viewer_update_view)
        event.Skip()
    
    def _enter_preview_or_processing(self, mode, must_restart_loader):
        """
        Переход в режим обработки (если mode==2) или в предпросмотр
        (если mode==1) на основе self.config
        Если уже запущен какой-то режим и must_restart_loader==False,
        то сохраняется имеющийся loader
        Аргументы:
          mode (int): 0 -- сохранить, что есть;
                      1 -- предпросмотр;
                      2 -- обработка
          must_restart_loader(bool)
        Возвращает: ничего
        """
        logging.debug("_enter_preview_or_processing, begin with mode=%d, "
                      "must_restart_loader=%d, (self.viewer is not None)=%d,"
                      "isinstance(self.viewer, Processing)=%d",
                      mode,
                      int(must_restart_loader),
                      int(self.viewer is not None),
                      int(isinstance(self.viewer, Processing)))
        
        sel_dlg_to_be_shown = self.sel_dlg_to_be_shown
        start_frame = 0
        if (mode == 2) and self.config.overlap:
            start_frame = self.config.pack_len / 2 + 1
        if self.cur_frame_num < self.config.frames_count \
           and self.cur_frame_num > 0:
            start_frame = self.cur_frame_num
        if (mode == 0):
            if isinstance(self.viewer, Processing):
                mode = 2
            else:
                mode = 1
        
        if mode == 2:
            if not self._check_if_can_launch_processing():
                self.my_toolbar.ToggleTool(self.proc_tool.GetId(), False)
                return
        
        if must_restart_loader or (self.viewer is None):
            self._close_viewer()
            loader = loading2.make_loader(self.config, self)
            if loader is None: return # make_loader уже вывел сообщение
            loader_is_hot = False
        else:
            loader = self.viewer.close(keep_loader = True)
            self.viewer = None
            loader_is_hot = True

        logging.debug("_enter_preview_or_processing, creating object with mode=%d", mode)
        if mode == 1:
            what = view.Preview
        else:
            what = Processing
        self.sel_dlg_to_be_shown = sel_dlg_to_be_shown

        self.viewer = what(main_video_frame = self,
                           loader = loader,
                           frame_num_ofs = self.config.frames_range[0],
                           start_with_frame = start_frame,
                           loader_is_hot = loader_is_hot)

        self.my_toolbar.ToggleTool(self.preview_tool.GetId(), True)
        self.my_toolbar.ToggleTool(self.proc_tool.GetId(), (mode == 2))
    
    def _check_if_can_launch_processing(self):
        """
        Возвращает True, если можно включить обработку, и False иначе.
        Выводит окошко в случае ошибки или замечания.
        """
        ok, text = self.config.processing_check_list()
        if ok:
            if len(text) > 0:
                dlg = wx.MessageDialog(self,
                                       U(text + "\nLaunch processing?"),
                                       "",
                                       wx.YES_NO)
                rv = dlg.ShowModal()
                dlg.Destroy()
                ok = (rv == wx.ID_YES)
        else:
                dlg = wx.MessageDialog(self, U(text), "", wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
        return ok
    
    def enter_preview(self):
        "Переход в режим предпросмотра. Вызывает _enter_preview_or_processing."
        self._enter_preview_or_processing(mode = 1, must_restart_loader=False)
        
    def enter_processing(self):
        "Переход в режим обработки. Вызывает _enter_preview_or_processing."
        self._enter_preview_or_processing(mode = 2, must_restart_loader=False)

    def hourglass(self, side = 'a'):
        "Рисует песочные часы на картинке поверх всего, что там есть"
        if side == 'a':
            dest = self.a_bmp
        else:
            dest = self.b_bmp
        #dc = wx.ClientDC(dest)
        #dc.DrawBitmap(self.HOURGLASS, 10, 10, True)
        bmp = dest.GetBitmap()
        dc = wx.MemoryDC(bmp)
        dc.DrawBitmap(self.HOURGLASS, 10, 10, True)
        dc.SelectObject(wx.NullBitmap)
        dest.SetBitmap(bmp)

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

    def _select_point_b(self, event):
        """
        Обработка событий мыши в режиме выбора одной точки / нескольких точек
        на изображении 'b'.
        """
        event.Skip()
        if self.viewer is None: return
        if event.Moving():
            self.SetStatusText("%0.3f, %0.3f" %
                self.viewer.backtrace_b(event.GetX(), event.GetY(), True))
        if not event.LeftDown(): return
        rv = self.viewer.backtrace_b(event.GetX(), event.GetY())
        if rv is None: return
        if self.sel_data.mode == Selection.SINGLE_POINT_B:
            self.sel_data.sel_item = rv
        else:
            self.sel_data.points_b.append(rv)
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
           callback (callable): функция, которая будет вызвана по завершению
                                работы режима выделения.
           info (string): описание, которое будет видно в маленьком диалоговом
                         окне, пустая строка -- использовать стандартный текст.
        Перед вызовом данного метода требуется:
          - вызвать enter_preview() или выполнить аналогичные действия
          - указать изначальный выбор в self.sel_data (если нужно)
        Результат работы будет содержаться в sel.sel_data и self.sel_ok (True 
        -- пользователь нажал 'готово', False -- 'отмена')
        
        Деактивирует редактор свойств (слева в окне) на время работы режима
        выделения. Потом он автоматически включается обратно
        """
        if self.sel_data.mode != Selection.OFF:
            raise Exception("Already in selection mode !")
        if self.viewer is None:
            dlg = wx.MessageDialog(self,
                                   'The Preview mode should be turned on',
                                   '',
                                   wx.OK | wx.CANCEL)
            rv = dlg.ShowModal()
            dlg.Destroy()
            if rv == wx.ID_OK:
                self.enter_preview()
            if self.viewer is None: # или нажали Отмена, или Ок, но не пошло
                self.sel_ok = False
                if callback is not None: callback()
                return
        self.sel_data.mode = mode
        self.sel_callback = callback
        self.sel_ok = False
        self.rect_state = False
        #self.maintain_sel_trpz_flag = 0
        self.sel_dlg = sel_gui.SelDlg(self, info)
        px, py = self.b_bmp.GetScreenPosition().Get()
        self.sel_dlg.Move(wx.Point(px - 180, py + 200))
        self.sel_dlg_to_be_shown = True
        self._rebind_mouse_events()
        self._viewer_update_view()
        #заблокировать параметры проекта:
        self.config_notebook.Enabled = False
        self.json_controls_suspend_state = (self.json_text.Enabled,
                                           self.apply_json_button.Enabled,
                                           self.reset_json_button.Enabled,
                                           self.json_defaults_button.Enabled)
        self.json_text.Enabled = False
        self.apply_json_button.Enabled = False
        self.reset_json_button.Enabled = False
        self.json_defaults_button.Enabled = False
   
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
        self.cancel_maintain_sel_trpz()
        if self.sel_callback is not None:
            self.sel_callback()
            self.sel_callback = None
        # разблокировать параметры проекта:
        self.config_notebook.Enabled = True
        if self.json_controls_suspend_state is not None:
            self.json_text.Enabled, \
                self.apply_json_button.Enabled, \
                self.reset_json_button.Enabled, \
                self.json_defaults_button.Enabled \
                    = self.json_controls_suspend_state
            self.json_controls_suspend_state = None

    def maintain_sel_trpz(self):
        """
        Включает режим, поддержания .sel_data.trpz в соответствие с
        .sel_data.rects_a. Следует вызывать после .start_selecting .
        """
        self.maintain_sel_trpz_flag = 1
        self._maintain_sel_trpz_act()
    
    def cancel_maintain_sel_trpz(self):
        self.maintain_sel_trpz_flag = 0
        self.sel_data.trpz = []
        
    def _maintain_sel_trpz_act(self):
        """
        Приводит .sel_data.trpz в соответствие с .sel_data.rects_a, если
        включен такой режим ( см. .maintain_sel_trpz() ).
        Здесь выполняется однократное действие.
        """
        if self.maintain_sel_trpz_flag == 0:
           return
        img_size = (0, 0)
        if self.viewer is not None:
            img_size = self.viewer.get_raw_img_size()
        if img_size == (0, 0):
            self.sel_data.trpz[:] = []
            self.maintain_sel_trpz_flag = 2
            return
        rects = self.sel_data.rects_a
        if self.sel_data.mode == Selection.SINGLE_RECT_A and \
          (self.sel_data.sel_item is not None):
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
    
    def _menu_tool_func(self, event):
        "Нажали на кнопку вызова меню -- кнопка в углу панели инструментов"
        self.PopupMenu(self.corner_menu)
    
    def _enable_json_editing(self, sect_name, reset_defaults=False):
        """
        Настраивает .json_text и другие элементы для редактирования раздела
        sect_name из .config, т.е. для непосредственной правки json-кода.
        Если sect_name=="", то наоборот, отлючает такую функциональность.
        """
        self.json_editing_sect = sect_name
        if len(sect_name) == 0:
            self._disable_json_editing()
            return
        self.json_editing_enabled = True
        
        self.json_header_static_text.SetLabel(' "' + sect_name + '":{')
        self.json_footer_static_text.SetLabel(' }')
        
        if reset_defaults:
            config = configuration.Config()
        else:
            config = self.config
        s = json.dumps(config._save_to_dict()[sect_name],
                       ensure_ascii = False,
                       indent = 2,
                       sort_keys = True)
        #удаляем первую и последюю скобки { }
        n1 = s.find('{') + 1
        if len(s) > n1 and s[n1] == '\n': n1 = n1 + 1
        n2 = s.rfind('}')
        if n2 <0 : n2 = len(s)
        s = s[n1:n2]
        self.json_text.SetValue(s)
        self.json_text.Enabled = True

        self.apply_json_button.Enabled = False
        self.reset_json_button.Enabled = False
        self.json_defaults_button.Enabled = True

    def _disable_json_editing(self):
        """
        Выключает элементы управления, оносящиеся к ._enable_json_editing
        """
        self.json_editing_enabled = False
        self.json_header_static_text.SetLabel('')
        self.json_text.SetValue('')
        self.json_text.Enabled = False
        self.json_footer_static_text.SetLabel('')
        self.apply_json_button.Enabled = False
        self.reset_json_button.Enabled = False
        self.json_defaults_button.Enabled = False
    
    def _decorate_image_for_tab(self, state):
        """
        Какие-то действия по переирисовке изображения в соответвии
        со включенным табом. state = False -- очистка.
        """
        if self.json_editing_sect == "areas":
            if state:
                self._display_areas()
                
                self.active_area_static_text.Hide()
                self.active_area_choice.Hide()
                self.active_area_rename_button.Hide()
            else:
                self._hide_areas(call_update = True)
           
    def _config_notebook_changed_func(self, event):
        "Переключили вкладку настроек -- заполняем текстовое поле"
        SECT_NAMES = ["",
                      "geom",
                      "areas",
                      "misc_spectral_param",
                      "",
                      "view",
                      "filters",
                      "moving_window"]
        num = self.config_notebook.GetSelection()
        if len(SECT_NAMES) > num:
            sect_name = SECT_NAMES[num]
        else:
            sect_name = ""
        self._enable_json_editing(sect_name)
        self._decorate_image_for_tab(True)
    
    def _config_notebook_changing_func(self, event):
        "Переключили вкладку настроек -- пытаемся обновить конфиг"
        if self.is_closing:
            return
        ok, text = self._apply_json_button_func_act()
        if ok and (len(text) != 0):
            self.display_warn(text)
        if not ok:
            long_text = "There are invalid values on this panel.\n"\
                        "They have to be reset before we proceed\n\n"\
                        + text
            flags = wx.ICON_ERROR | wx.OK | wx.CANCEL
            dlg = wx.MessageDialog(self, U(long_text), '', flags)
            rv = dlg.ShowModal()
            if rv == wx.ID_OK: ok = True
            dlg.Destroy()
        if ok:
            self._decorate_image_for_tab(False)
        else:
            event.Veto()
    
    def _config_notebook_changing_func_bool(self):
        """
        Будет выполнена вся та работа, которая положена перед переключением
        вкладки, в т.ч. показ диалога об ошибках.
        Возвращает True, если бы из данного состояния разрешили переключить
        вкладку.
        """
        preudo_event = _PseudoEvent()
        self._config_notebook_changing_func(preudo_event)
        return not preudo_event.vetoed
    
    def _json_text_func(self, event):
        "Изменили текст настроек"
        self.apply_json_button.Enabled = True
        self.reset_json_button.Enabled = True

    def _apply_json_button_func(self, event):
        "Применить значения в json-тексте настроек (нажали кнопку)"
        ok, text = self._apply_json_button_func_act()
        if (not ok) or (len(text) > 0):
            msg_header = ["Invalid input values",
                          "Issues on input values"] [ok]
            msg_icon = [wx.ICON_ERROR, wx.ICON_EXCLAMATION] [ok]
            dlg = wx.MessageDialog(self, U(text), U(msg_header), msg_icon)
            dlg.ShowModal()
            dlg.Destroy()
        self._decorate_image_for_tab(True)
        if ok:
            self._enable_json_editing(self.json_editing_sect)

    def _apply_json_button_func_act(self):
        """
        Применить значения в json-тексте настроек (непосредственная работа)
        Возвращает tuple (bool, str):
            [0] False, если были ошибки
            [1] текст ошибки, если были ошибки, или текст замечаний иначе
        Если не было ошибок, то изменяет self.config
        """
        if not self.json_editing_enabled:
            return (True, '')
        s = '{' + self.json_header_static_text.GetLabel() + \
            clean_input_string(self.json_text.GetValue()) + \
            self.json_footer_static_text.GetLabel() + '}'
        try:
            new_config, warn_txt = configuration._load_config_more_options(
                s,
                fname_is_given = False,
                update_existing_config = copy.deepcopy(self.config),
                one_section = True)
        except ConfigError as err:
            return (False, str(err))

        self.config = new_config
        self.project_changed |= self.apply_json_button.Enabled
        
        if self.apply_json_button.Enabled and self._in_processing_mode():
            sect_name = self.json_header_static_text.GetLabel().encode('utf-8')
            sect_name = sect_name[(sect_name.find(b'"') + 1) :
                                  sect_name.rfind(b'"')]
            if self._check_restart_processing(sect_name):
                warn_txt += self._RESTART_PROCESSING_MSG

        self.apply_json_button.Enabled = False
        self.reset_json_button.Enabled = False
        return (True, warn_txt)

    _RESTART_PROCESSING_MSG = "Processing is restarted"
    
    def _check_restart_processing(self, sect_name):
        """
        Вызывается при изменении раздела 'sect_name' в конфиге.
        В зависимости от раздела обработка: а) перезапускается,
        б) минимально перерисовывается, в) не меняется.
        Возвражает True, если обработка была перезапущена.
        """
        if not self._in_processing_mode():
            return False
        RUINS_PROCESSING = ['geom', 'areas', 'misc_spectral_param', 'moving_window']
        if sect_name in RUINS_PROCESSING:
            self.enter_processing()
            return True
        if sect_name == 'filters':
            self.viewer.update_filters()
        if sect_name == 'view':
            self._viewer_update_view()
        return False

    def _reset_json_button_func(self, event):
        "Восстановить предыдущие значения в json-тексте настроек"
        self._enable_json_editing(self.json_editing_sect)
    
    def _json_defaults_button_func(self, event):
        "Восстановить стандартные значения в json-тексте настроек"
        self._enable_json_editing(self.json_editing_sect, reset_defaults=True)
        self.apply_json_button.Enabled = True
        self.reset_json_button.Enabled = True

    def _preview_tool_func(self, event):
        "Включили/выключили кнопку предпростмотра"
        if self.preview_tool.IsToggled():
            self.enter_preview()
        else:
            self._close_viewer()
            
    def _source_button_func(self, event):
        "Нажали на кнопку 'выбрать исходный файл'"
        self._close_all_dialogs()
        dlg = source_gui.SourceDlg(self)
        dlg.ShowModal()
    
    def _reset_config(self, new_config):
        "Изменить конфиг на new_config. Вызывается, например, при загрузке."
        self._close_viewer()
        self.config = new_config
        self.changed = False
        self._config_notebook_changed_func(None)
        self._clear_screen()
        
    def _clear_screen(self):
        "Делаем серую картинку"
        for dest in [self.a_bmp, self.b_bmp]:
            w, h = dest.GetSizeTuple()
            bmp = wx.EmptyBitmap(w, h)
            dc = wx.MemoryDC(bmp)
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWFRAME),
                wx.SOLID))
            dc.DrawRectangle(0, 0, w, h)
            dc.SelectObject(wx.NullBitmap)
            dest.SetBitmap(bmp)
    
    def _ensure_saved(self):
        """
        Если надо, то выдает запрос 'Сохранить изменения?' и т.д.. и сохраняет.
        Вызвает перед такими 'разрушающими' функциями как закрытие, загрузка
        нового проека и пр..
        Возвращает True во тех сценариях поведения, где можно прожожать работу
        'разрушающей' функции.
        """
        if not self._config_notebook_changing_func_bool():
            return False
        if not self.project_changed:
            return True
        
        dlg = wx.MessageDialog(self,
                               'Do you want to save changes in the current project?',
                               '',
                               wx.ICON_EXCLAMATION | wx.YES_NO | wx.CANCEL)
        rv = dlg.ShowModal()
        dlg.Destroy()
        
        if rv == wx.ID_CANCEL: return False
        if rv == wx.ID_NO: return True
        return self._save_menu_func_act()
    
    def _save_menu_func_act(self):
        """
        Меню 'Сохранить проект' -- непосредственное выполнение работы.
        Если нет имени, то делает 'сохранить как...'
        Возвращает: True, если удалось сохранить
                    False, если не удалось сохранить или если выдавлся диалог
                           и пользователь нажал 'Отмена'
        """
        self._apply_json_button_func_act()
        if len(self.project_filename) == 0:
            return self._save_as_menu_func_act()
        try:
            with open(U(self.project_filename), 'wt') as f:
                json.dump(self.config._save_to_dict(),
                          f,
                          ensure_ascii = False,
                          indent = 2)
        except IOError as err:
            logging.debug("Can't save to '%s': %s",
                          U(self.project_filename),
                          U(str(err)))
            dlg = wx.MessageDialog(self,
                                   U("Can't save project to file: '%s'" %
                                     self.project_filename),
                                   '',
                                   wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        self.project_changed = False
        return True
        
    def _save_as_menu_func_act(self):
        """
        Меню 'Сохранить проект как...'  -- непосредственное выполнение работы.
        Возвращает:  True, если удалось сохранить
                     False, если не удалось сохранить или нажали 'Отмена'
        """
        dlg = wx.FileDialog(self,
                            'Save project as',
                            '',
                            U(self.project_filename),
                            self._WWOL_FILE_WILDCARD,
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        rv = dlg.ShowModal()
        new_filename = clean_input_string(dlg.GetPath())
        dlg.Destroy()
        if rv != wx.ID_OK: return False
        self.project_filename = new_filename
        return self._save_menu_func_act()
    
    def _save_menu_func(self, event):
        "Меню 'Сохранить проект'"
        self._save_menu_func_act()
        
    def _save_as_menu_func(self, event):
        "Меню 'Сохранить проект как...'"
        self._save_as_menu_func_act()
    
    def _open_menu_func(self, event):
        "Меню 'Открыть проект...'"
        if not self._ensure_saved():
            return
        
        dlg = wx.FileDialog(self,
                            'Open project',
                            '',
                            U(self.project_filename),
                            self._WWOL_FILE_WILDCARD,
                            wx.FD_OPEN)
        rv = dlg.ShowModal()
        filename2open = clean_input_string(dlg.GetPath())
        dlg.Destroy()
        if rv != wx.ID_OK: return

        try:
            loaded_config, warn_txt = configuration.load_config(filename2open)
        except ConfigError as err:
            dlg = wx.MessageDialog(self,
                               U(str(err)),
                               'Error occurred while loading a project',
                               wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self._reset_config(loaded_config)

        if len(warn_txt) != 0:
            dlg = wx.MessageDialog(self,
                                   U(warn_txt),
                                   'Issues, concerning the loaded project',
                                   wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
        
        self.project_changed = False
        self.project_filename = filename2open
        if self.config.source_set:
            self.enter_preview()
    
    _WWOL_FILE_WILDCARD = U('WWOL projects (*.wwl)|*.wwl|All files (*.* , *)|*')

    def _simple_proj_button_func(self, event):
        "Нажали на кнопку 'Простая проекция'"
        # пытаемся получить из текущих настроек параметр метры/пиксели,
        # если он имеет смыл
        if not self._config_notebook_changing_func_bool():
            return
        prev_val = 1.0
        if self.config.angle_to_vert == 90.:
            prev_val = self.config.camera_height \
                       * self.config.angle_per_pixel / 180 * pi
        
        # выдаем диалог
        dlg = wx.TextEntryDialog(self,
                                 'Projection coefficient: meter / pixels',
                                 '',
                                 repr(prev_val))
        rv = dlg.ShowModal()
        str_val = dlg.GetValue()
        dlg.Destroy()
        if rv == wx.ID_CANCEL: return

        try:
            val = float(str_val)
            if val <= 0: raise ValueError()
        except ValueError:
            dlg = wx.MessageDialog(self, 'Invalid value', '', wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        geom.set_simple_projection(val, self.config)
        self._config_notebook_changed_func(None)
        self.project_changed = True
    
    def _load_cameras_list(self):
        """
        (Врямянка. Временно здесь. И временно выдает захардкоженные значения)
        Возвращает список калиброванных камер:
                # Здесь нужен список камер в формате:
        [
          { "name":"MyCamera",
            "param": {
              "angle_per_pixel": ..,
              "distortion_k1": .. ,
              "distortion_k2": ..
            }
          }
         ......
        ]
        """
        return [
          { "name":"GoPro Wide",
            "param": {
              "angle_per_pixel": 0.0644, 
              "distortion_k1": -0.26078, 
              "distortion_k2": 0.040517
            }
          },
          { "name":"GoPro Narrow",
            "param": {
              "angle_per_pixel":0.03,
              "distortion_k1": 0,
              "distortion_k2": 0
            },
          },
          { "name":"JVC Zoom x1",
            "param" : {
              "angle_per_pixel":0.02352,
              "distortion_k1": 0,
              "distortion_k2": 0
            },
          }
        ]
    
    def _camera_list_button_func(self, event):
        "Нажали на кнопку 'Камеры...'"
        if not self._config_notebook_changing_func_bool():
            return
        
        cameras = copy.deepcopy(self._load_cameras_list())
        cameras.sort(key = lambda a: a["name"].lower())
        IS_GUI_FUNCTION = "is_gui_function"
        #for j in range(0, len(cameras)):
        #    cameras[j]["is_gui_function"] = False
        cameras.append(
            {"name":"(Calibrate camera / edit list)",
             IS_GUI_FUNCTION:True})
                
        dlg = wx.SingleChoiceDialog(self,
                                    '',
                                    'Preconfigured cameras',
                                    [U(x["name"]) for x in cameras])
        dlg.SetSize((300,400))
        rv = dlg.ShowModal()
        sel = dlg.GetSelection()
        dlg.Destroy()
        if rv == wx.ID_CANCEL: return
        
        if IS_GUI_FUNCTION in cameras[sel] and \
          cameras[sel][IS_GUI_FUNCTION]:
            dlg = wx.MessageDialog(
                self,
                'This function is still under construction. Sorry (')
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.config.__dict__.update(cameras[sel]["param"])
        self.config.post_config("geom")
        self._config_notebook_changed_func(None)
        self.project_changed = True

    def _pick_horizont_button_func(self, event):
        "Нажали 'Указать горизонт в кадре'"
        if not self._config_notebook_changing_func_bool():
            return
        
        # проверяем отличается ли камера от стандартной
        if self.config.angle_per_pixel == geom.DEFAULT_ANGLE_PER_PIXEL:
            dlg = wx.MessageDialog(
                self,
                'Before performing this operation, you should set the camera '
                'resolution (value of angle_per_pixel set in degees/pixels). '
                'Are you sure the camera is set up correctly?',
#                'Перед выполнение данной операции следует настроить разрешение'
#                ' камеры (angle_per_pixel). Вы уверены, что камера настроена'
#                ' правильно?',
                '',
                wx.YES_NO | wx.ICON_EXCLAMATION)
            rv = dlg.ShowModal()
            dlg.Destroy()
            if rv == wx.ID_NO: return
        self.start_selecting(Selection.SINGLE_POINT_A,
                             self._pick_horizont_finish_func)
    
    def _pick_horizont_finish_func(self):
        """
        После 'Указать горизонт в кадре' пользователь выбрал точку
        и нажал 'готово'
        """
        coord = self.sel_data.sel_item
        self.sel_data.sel_item = None
        #self.sel_data.rects_a = []
        self._viewer_update_view()
        if not self.sel_ok: return
        
        self.config.angle_to_vert = 90 - geom.pixels_to_angle(
            coord, self.config, self.viewer.get_raw_img_size(), 'v')
        self._config_notebook_changed_func(None)
        self.config.post_config("geom")
        if self._check_restart_processing("geom"):
            self.display_warn(self._RESTART_PROCESSING_MSG)
    
    _DISPLAY_AREAS_DONT_CLEAN_RECTS = 1
    _DISPLAY_AREAS_DONT_CALL_UPDATE = 2
    
    def _display_areas(self, flags = 0):
        "Заполняет sel_data, так чтобы отобразились области обработки"
        do_clean = not bool(flags & self._DISPLAY_AREAS_DONT_CLEAN_RECTS)
        do_update = not bool(flags & self._DISPLAY_AREAS_DONT_CALL_UPDATE)
        if do_clean: self._hide_areas(call_update = False)
        for x in self.config.areas_list:
            self.sel_data.rects_a.append(x.coord)
        if do_update:
            self.maintain_sel_trpz()
            self._viewer_update_view()
    
    def _hide_areas(self, call_update):
        self.sel_data.rects_a = []
        self.sel_data.sel_item = None
        self.cancel_maintain_sel_trpz()
        if call_update: self._viewer_update_view()
        
    def _select_area_button_func(self, event):
        """
        На вкладке 'Зоны обработки' нажали 'Выбрать'.
        Поведение: изменяет активную зону или добавлет зону, если список пуст
        """
        if not self._config_notebook_changing_func_bool():
            return
        self._display_areas(self._DISPLAY_AREAS_DONT_CALL_UPDATE)
        if self.config.active_area_num >= 0:
            self.sel_data.sel_item = \
                self.sel_data.rects_a.pop(self.config.active_area_num)
        self.maintain_sel_trpz()
        self.start_selecting(Selection.SINGLE_RECT_A, self._select_area_finish)
    
    def _select_area_finish(self):
        "Закончили выделение зоны обработки"
        if self.sel_ok:
            if self.config.active_area_num < 0:
                self.config.add_area_by_coord(self.sel_data.sel_item)
            else:
                self.config.set_area_coord(self.config.active_area_num,
                                           self.sel_data.sel_item)
            self._config_notebook_changed_func(None)
            self.project_changed = True
            if self._check_restart_processing("areas"):
                self.display_warn(self._RESTART_PROCESSING_MSG)
        self._display_areas()

    def _select_multiple_areas_button_func(self, event):
        """
        На вкладке 'Зоны обработки' нажали 'Несколько зон'.
        Поведение: можно добавлять зоны или удалать по одной с конца
        """
        if not self._config_notebook_changing_func_bool():
            return
        self._display_areas(self._DISPLAY_AREAS_DONT_CALL_UPDATE)
        self.maintain_sel_trpz()
        self.start_selecting(Selection.MULTIPLE_RECTS_A,
                             self._select_multiple_areas_finish)
     
    def _select_multiple_areas_finish(self):
        "Закончили режим, когда можно выделять несколько зон"
        if self.sel_ok:
            total_len = len(self.sel_data.rects_a)
            for j in range(0, total_len):
                if j < len(self.config.areas_list):
                    self.config.set_area_coord(j, self.sel_data.rects_a[j])
                else:
                    self.config.add_area_by_coord(self.sel_data.rects_a[j])
            if total_len < len(self.config.areas_list):
                self.config.areas_list[total_len:] = []
            self.config_active_area_num = total_len - 1
            self.config.active_area_num2name()
            self._config_notebook_changed_func(None)
            self.project_changed = True
        self._display_areas()
    
    def _load_spec_button_func(self, event):
        "Нажали на кнопку/меню 'Открыть спектр'"
        grapher = GrapherMain(self)
        grapher.Show()
        wx.Yield()
        grapher.open_button_func(None)
        if grapher.my_spec.is_empty():
            grapher.Destroy()
    
    def _checkbox_like_radio(self, event):
        """
        Обработчик события нажатия на CheckBox, чтобы он вел себя как RadioBox
        Здесь забиты имена все CheckBox-ов, которые объединены в группы
        """
        GROUPS = [
            [self.left_scrshot_check, self.right_scrshot_check],
            [self.raw_scrshot_check, self.cur_view_scrshot_check],
            [self.single_scrshot_check, self.many_scrshot_check]
        ]
        
        this_group = None
        this_item = None
        for gr in GROUPS:
            for item in gr:
                if event.GetId() == item.GetId():
                    this_group = gr
                    this_item = item
                    break
        if this_group is None: return
        
        any_checked = False
        too_many_checked = False
        for ch in this_group:
            if ch.IsChecked():
                if any_checked:
                    too_many_checked = True
                any_checked = True
        
        if too_many_checked:
            for ch in this_group:
                ch.SetValue(False)
            this_item.SetValue(True)
        if not any_checked:
            for ch in this_group:
                if not (ch is this_item):
                    ch.SetValue(True)
                    break
        
        label = ''
        if self.left_scrshot_check.IsChecked():
            label = 'Raw image'
        else:
            label = 'Raw data'
        self.raw_scrshot_check.SetLabel(label)
        self._update_scrshot_tooltip()
    
    def _update_scrshot_tooltip(self):
        "Задает подпись к кнопке скриншот в зависимости от нажатых кнопок"
        CHECKS = [self.left_scrshot_check, self.right_scrshot_check,
                  self.raw_scrshot_check, self.cur_view_scrshot_check,
                  self.single_scrshot_check, self.many_scrshot_check]
        s = ''
        for ch in CHECKS:
            if ch.GetValue():
                if len(s) > 0:
                    s += ', '
                s += ch.GetLabelText()
        self.my_toolbar.SetToolShortHelp(
            self.scrshot_tool.GetId(),
            self.scrshot_tooltip_head + '\n[' + s + ']')
        
    def _scrshot_button_func(self, event):
        "Сделать скриншот -- нажали кнопку ОК на вкладке 'снимок экрана'"
        if self.single_scrshot_check.GetValue():
            self._make_single_scrshot()
        else:
            self._make_video_scrshot()
    
    def _make_single_scrshot(self):
        "Сделать скриншот, один кадр"
        bmp = None
        if self.cur_view_scrshot_check.GetValue():
            if self.left_scrshot_check.GetValue():
                bmp = self.a_bmp.GetBitmap()
            else:
                bmp = self.b_bmp.GetBitmap()
        else:
            if self.left_scrshot_check.GetValue():
                if self.viewer is not None:
                    img = self.viewer.get_raw_img()
                    if (img is not None) and (img.IsOk()):
                        bmp = img.ConvertToBitmap()
                        
            else:
                pass # не сделано
        if (bmp is None) or (not bmp.IsOk()):
            dlg = wx.MessageDialog(
                self, 
                "This kind of a screenshot is not implemented yet. WIP",
                '',
                wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.save_bitmap(bmp)
    
    def save_bitmap(self, bmp, default_fname = 'screenshot', parent_window = None):
        """
        Сохраняет изображения в файл.
        Предварительно выводит диалог для запроса имени файла.
        Хранит в self предыдущий путь, номер типа файла и качество JPEG.
        """
        if parent_window is None:
            parent_window = self
        # спрашиваем файл
        BMP_ID = 0
        PNG_ID = 1
        JPEG_ID= 2
        DUMMY_ID = 3
        exts = {BMP_ID: '.bmp', PNG_ID:'.png', JPEG_ID:'.jpg'}
        ft = self.default_scrshot_file_type
        dlg = wx.FileDialog(
            parent_window,
            message = 'Save image',
            defaultDir = U(self.default_scrshot_dir),
            defaultFile = U(default_fname) + exts[ft],
            wildcard = 'BMP|*.bmp|PNG|*.png|JPEG|*.jpg|All files (*.*)|*.*',
            style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg.SetFilterIndex(ft)
        rv = dlg.ShowModal()
        fname = dlg.GetPath()
        ft = dlg.GetFilterIndex()
        if ft == DUMMY_ID: ft = BMP_ID
        dlg.Destroy()
        if rv != wx.ID_OK:
            return
        self.default_scrshot_file_type = ft
        self.default_scrshot_dir = os.path.dirname(fname.encode('utf-8'))
        
        # расширение файла
        fname1, fname_ext = os.path.splitext(fname)
        if fname_ext.lower() != exts[ft]:
            dlg = wx.MessageDialog(parent_window,
                                   "Change the file's extension into '%s'?"
                                       % exts[ft],
                                   "",
                                   wx.YES_NO)
            rv = dlg.ShowModal()
            dlg.Destroy()
            if rv == wx.ID_YES:
                fname = fname1 + exts[ft]
        
        # сохраняем
        if ft == JPEG_ID:
            # надо спросить качество
            dlg = wx.TextEntryDialog(parent_window,
                                     "Set quality (0-100):",
                                     "",
                                     self.default_scrshot_jpeg_quality_s)
            rv = dlg.ShowModal()
            text_value = dlg.GetValue()
            dlg.Destroy()
            if rv != wx.ID_OK: return
            img = wx.ImageFromBitmap(bmp)
            img.SetOption('quality', text_value)
            self.default_scrshot_jpeg_quality_s = text_value
            save_ok = img.SaveFile(fname, wx.BITMAP_TYPE_JPEG)
        else:
            save_ok = bmp.SaveFile(fname,
                                   {BMP_ID: wx.BITMAP_TYPE_BMP,
                                    PNG_ID: wx.BITMAP_TYPE_PNG} [ft])
        if not save_ok:
            dlg = wx.MessageDialog(parent_window,
                                   "Can't save the image",
                                   "",
                                   wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    def _make_video_scrshot(self):
       if self.raw_scrshot_check.GetValue() and self.right_scrshot_check.GetValue():
           # единственный реализованный случай
            parent_window = self
            if not self._in_processing_mode():
                dlg = wx.MessageDialog(parent_window,
                                       "available only in processing mode",
                                       "",
                                       wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return

            # надо спросить с какого по какой кадр
            from_frame = -1
            to_frame = -1
            default_input = "%d %d" % (self.cur_frame_num + 1,
                                       self.cur_frame_num + self.config.pack_len)
            while from_frame < 1:
                dlg = wx.TextEntryDialog(
                    parent_window,
                    "Enter from and to frame numbers (inclusive):",
                    "",
                    default_input)
                rv = dlg.ShowModal()
                text_value = dlg.GetValue()
                dlg.Destroy()
                if rv != wx.ID_OK: return
                try:
                    (from_text, to_text) = text_value.split(' ')
                    from_frame = int(from_text)
                    if (from_frame < 0): raise ValueError()
                    to_frame = int(to_text)
                    if (to_frame <= from_frame): raise ValueError()
                except ValueError:
                    default_input = text_value

            # спрашиваем файл
            dlg = wx.FileDialog(
                parent_window,
                message = 'Save data',
                defaultDir = U(self.default_scrshot_dir),
                defaultFile = '',
                wildcard = 'BIN|*.bin|All files (*.*)|*.*',
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            rv = dlg.ShowModal()
            fname = dlg.GetPath()
            dlg.Destroy()
            if rv != wx.ID_OK:
                return
            self.default_scrshot_dir = os.path.dirname(fname.encode('utf-8'))
            
            # сохраняем
#            pd = wx.ProgressDialog(
#                'WWOL',
#                u"Writing data to disk",
#                100,
#                self,
#                wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME | wx.PD_AUTO_HIDE)
#            pd.Show()
            self.viewer.save_xyt_result(fname,
                                        from_frame - 1,
                                        to_frame - 1,
                                        None, None)
#                                        KillProgress(self,pd),
#                                        pd.Update)

    def _open_video_menu_func(self, event):
        "Меню 'Открыть видеофайл...'"
        if not self._ensure_saved():
            return
        
        dlg = wx.FileDialog(self,
                            'Open a video file',
                            '',
                            '',
                            'All files (*.*)|*.*',
                            wx.FD_OPEN)
        rv = dlg.ShowModal()
        filename2open = clean_input_string(dlg.GetPath())
        dlg.Destroy()
        if rv != wx.ID_OK: return

        new_config = configuration.Config()
        new_config.source_type = configuration.FFMPEG_AUTO_SOURCE
        new_config.video_filename = filename2open
        self._reset_config(new_config)
        self.project_changed = True
        self.project_filename = ''
        self._source_button_func(None)
            
    def _view_step_tool_func(self, event):
        val = -1
        text = str(self.config.button_step)
        first_query = True
        while val <= 0:
            msg_u = 'Set the step for changing frames, when you press the arrow buttons:'
            if not first_query:
                msg_u = 'Invalid input.\n' + msg_u
            first_query = False
            dlg = wx.TextEntryDialog(self, msg_u, '', text)
            rv = dlg.ShowModal()
            text = dlg.GetValue()
            dlg.Destroy()
            if rv != wx.ID_OK: return
            try:
                val = int(text)
            except ValueError:
                pass
        self.config.button_step = val

    def _about_menu_func(self, event):
        "Меню 'О программе'"
        dlg = wx.MessageDialog(self,
                               'WWOL: Wind-Wave Optical Lab\n'
                               'ver. %s\n'
                               '(c) Michael Salin, %d\n'
                               'mikesalin@gmail.com'                               
                               % (ABOUT_VERSION, ABOUT_YEAR),
                               'WWOL',
                               wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def _in_processing_mode(self):
        if self.viewer is not None:
            return self.viewer.is_processing()
        else:
            return False

    def _proc_tool_func(self, event):
        "Включили/выключили кнопку обработки"
        if self.proc_tool.IsToggled():
            self.enter_processing()
        else:
            self.enter_preview()
    
    def _express_spec_button_func(self, event):
        """
        Нажали на кнопку 'Экспрес (спектр) в текущем окне'
        Берет спектр по одной пачке кадров из Processing и запускает графер.
        """
        if not self._in_processing_mode():
            dlg = wx.MessageDialog(self, "Turn the Processing mode on first", "", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        interval = []
        power_spec = self.viewer.express_spectrum(interval)
        if power_spec is None:
            dlg = wx.MessageDialog(
                self,
                "Please, wait till we process atleast one pack of frames"
                "and then press this button again.",
                "",
                wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
##        if (self.express_spec_wnd is None) or \
##          (not self.express_spec_wnd.alive):
##               TODO баг
        if True:
            self.express_spec_wnd = GrapherMain(self)
            self.express_spec_wnd.Show()
        else:
            self.express_spec_wnd.Raise()
        self.express_spec_wnd.set_spec(power_spec)
        self.express_spec_wnd.proj_name = "Express spectrum %0.1f-%0.1f" \
            % (interval[0], interval[1])
        self.express_spec_wnd.update_title()
        self.express_spec_wnd.plot_button_func_act()


    def _aver_spec_button_func(self, event):
        "Нажали на кнопку 'Накопленный спектр'"
        dlg = wx.MessageDialog(self,
                              "Note that computing the averaged spectrum over "
                              "the entire time series is a time consuming "
                              "operation.\nPress 'OK' to begin.",
                              "",
                              wx.OK | wx.CANCEL)
        rv = dlg.ShowModal()
        dlg.Destroy()
        if rv != wx.ID_OK: return
        
        if not self._in_processing_mode():
            self._enter_preview_or_processing(2, False)
        if not self._in_processing_mode():
            return

        pd = wx.ProgressDialog(
            'WWOL',
            "Computing the averaged spectrum",
            100,
            self,
            wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_ESTIMATED_TIME
              | wx.PD_AUTO_HIDE)
        pd.Show()
        self.viewer.calc_average_spectrum(
            AverSpecFinish(self, pd),
            pd.Update)
    
    def _points_tool_func(self, event):
        "Нажали на кнопку 'точки' в тулбаре"
        if self.points_tool.IsToggled():
            if self.points_dlg is not None:
                logging.debug('Strange behavior in _points_tool_func (1)')
            self.points_dlg = points_gui.PointsDlg(self)
            self.points_dlg.Show()
        else:
            if self.points_dlg is not None:
                self.points_dlg.close_func()
            else:
                logging.debug('Strange behavior in _points_tool_func (2)')
    
    def _temp_images_monitoring_timer_func(self, func):
        "Срабатывание таймера. Считаем, сколько файлов уже создал ffmpeg"
        self.temp_img_monitor.lock.acquire()
        if self.temp_img_monitor.enabled:
            while os.access(U(self.temp_img_monitor.filename_pattern
                              % (self.temp_img_monitor.current + 10)), os.F_OK):
                self.temp_img_monitor.current += 10
            self.a_footer_static_text.SetLabel(
                "%d / %d" %
                (self.temp_img_monitor.current - self.temp_img_monitor.first + 1,
                self.temp_img_monitor.last - self.temp_img_monitor.first))
        else:
            lbl = self.a_footer_static_text.GetLabel()
            if (len(lbl) == 0) or (lbl[0] != "В"):
                self.a_footer_static_text.SetLabel("")
            self.temp_images_monitoring_timer.Stop()
        self.temp_img_monitor.lock.release()
    
    def start_temp_images_monitoring(self, filename_pattern, first, last):
        """
        Запускает таймер, который будет считать число файлов во временной папке
        и выводить на экран. Это потокобезопасная функция.
        """
        self.temp_img_monitor.lock.acquire()
        self.temp_img_monitor.filename_pattern = filename_pattern
        self.temp_img_monitor.first = first
        self.temp_img_monitor.last = last
        self.temp_img_monitor.current = first - 1
        self.temp_img_monitor.enabled = True
        self.temp_img_monitor.lock.release()
        wx.CallAfter(self.temp_images_monitoring_timer.Start, 500)

    def stop_temp_images_monitoring(self):
        "Это потокобезопасная функция."
        self.temp_img_monitor.lock.acquire()
        self.temp_img_monitor.enabled = False
        self.temp_img_monitor.lock.release()
    
    def _footer_static_text_dclick_act(self, obj):
        "выводит диалог с подписью этого контрола"
        dlg = wx.TextEntryDialog(self, "", "Label", obj.GetLabel())
        dlg.ShowModal()
        dlg.Destroy()
    
    def _a_footer_static_text_dclick(self, event):
        "При двойном щелчке выводит диалог со своим содержанием"
        self._footer_static_text_dclick_act(self.a_footer_static_text)
        
    def _b_footer_static_text_dclick(self, event):
        "При двойном щелчке выводит диалог со своим содержанием"
        self._footer_static_text_dclick_act(self.b_footer_static_text)
            

def print_hint():
    "Имена методов и MainVideoFrame, включая те, что начинаются с \'_\'"
    lst = list(MainVideoFrame.__dict__.keys())
    lst.sort()
    for s in lst:
        print(s)
    #Call in iterpreter:
    #  from wwol.base_gui import main_video_gui
    #  main_video_gui.print_hint()
    

