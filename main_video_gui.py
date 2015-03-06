# -*- coding: utf-8 -*-
"""
В этом модуле определен класс главного окна
"""

import logging
import os
import threading
import math
import wx

import wxfb_output
import zoom_gui
import loading
import view
import configuration
import tester
import source_gui

class MainVideoFrame(wxfb_output.MainVideoFrame):
    """
    Главное окно.
    Данные, определенные здесь:
    .zoom_dlg (ZoomDlg или None)
    .active_dlg - диалог из меню управление, включенный в данный момент,
                  (не модальный, stay_on_top). None, если такового нет
    .viewer (Preview-like или None) - класс, кт. реализует переключение кадров
                                      и пр.; при ошибке сбрасывется в None
    .config
    .cur_frame_num -- номер кадра, здесь нумерация всегда с 0
    .prev_mouse_x
    .prev_mouse_y
    .a_panel (view.PanelParam, параметр size игнорируется)
    """
    def __init__(self, parent):        
        wxfb_output.MainVideoFrame.__init__(self,parent) #initialize parent class        
        
        #Данные:
        self.active_dlg = None
        self.zoom_dlg = None
        self.viewer = None
        self.config = configuration.Config()
        self.cur_frame_num = 0
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.a_panel = view.PanelParam()
        
        tester.def_all_tests(self)
        
        #Допиливаем интерфейс:
        self.my_gauge.Show(False)
        self.my_toolbar.Enabled = False
        
    def close_func(self, event):
        "Нажали на кнопку закрыть (крестик)."
        if self.active_dlg is not None:
            self.active_dlg.Destroy()
            self.active_dlg = None
        if self.zoom_dlg is not None:
            self.zoom_dlg.Destroy()
            self.zoom_dlg = None 
        self.close_viewer()
        event.Skip()
        
        #debug info:
        logging.debug("Theads, which are alive at exit:")
        lt = threading.enumerate()
        for t in lt:
            if not t.daemon:
                logging.debug("    " + t.name)                
    
    def close_viewer(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
    
    def test_menu_func(self, event):
        "Меню 'Тест'"
        self.default_test()
                
    def viewer_crushed(self, message):
        """
        Обработка ошибки, возникшей при текущей работе viever.Preview и т.п.
        message - string
        """
        msg_dlg = wx.MessageDialog(self, message, "", wx.ICON_ERROR)        
        msg_dlg.ShowModal()
        msg_dlg.Destroy()        
        self.close_viewer()
        #NB: сделать функцию для замечаний, пусть запускает всплывающую плашку
    
    def display_frame_num(self, num):
        """
        Вызывается после того, как выполнена отрисовка нового кадра и можно 
        переключить счетчик кадров.
        num -- то же, что и было передано в goto_frame
        Замечание: внутри программы считаем номера кадров с 0, а для
        пользователя - с единицы.
        """
        self.cur_frame_num = num
        label = self.frame_to_time_str(self.cur_frame_num) + " | " + \
                self.frame_to_time_str(self.config.frames_count)
        self.jump_time_tool = self.reset_tool_label(self.jump_time_tool, label)
        label = "%4d |%5d" % (self.cur_frame_num +1, self.config.frames_count)
        self.jump_frame_tool=self.reset_tool_label(self.jump_frame_tool, label)
        
        self.my_toolbar.EnableTool(self.prev_tool.GetId(), self.can_go_back())
        self.my_toolbar.EnableTool(self.next_tool.GetId(), self.can_go_fwd())
                                   
    def can_go_fwd(self):
        "Возвращает True, если можно перелистнуть на кадр вперед"
        return self.cur_frame_num + self.config.view_step \
            < self.config.frames_count
    def can_go_back(self):
        "Возвращает True, если можно перелистнуть на кадр назад"
        return self.cur_frame_num - self.config.view_step >= 0
        
    def frame_to_time_str(self, n):
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
    
    def reset_tool_label(self, tool, label):
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
    
    def prev_tool_func(self, event):
        "Нажали на кнопку со стерлкой назад"
        if self.viewer is None or not self.can_go_back():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num - self.config.view_step)
    def next_tool_func(self, event):
        "Нажали на кнопку со стрелкой вперед"
        if self.viewer is None or not self.can_go_fwd():
            logging.debug("suddenly not available")
            return
        self.viewer.goto_frame(self.cur_frame_num + self.config.view_step)

    def jump_frame_tool_func(self, event):
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

    def jump_time_tool_func(self, event):
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
                                 self.frame_to_time_str(self.cur_frame_num) )
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

    def zoom_tool_func(self, event):
        "Нажали на кнопку с луппой"
        if self.zoom_dlg is not None:
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
        self.rebind_mouse_events("a")
        self.rebind_mouse_events("b")
        self.rebind_mouse_wheel_event()
    
    def mouse_drag_a(self, event):
        """
        Обработчик событий мыши (EVT_MOUSE_EVENTS) для картинки A (a_bmp)
        в режиме манипуляций мышью.
        """
        if self.viewer is None: return
        if event.LeftDown():
            self.prev_mouse_x = event.GetX()
            self.prev_mouse_y = event.GetY()
        if event.Dragging() and event.LeftIsDown():
            dx = event.GetX() - self.prev_mouse_x
            dy = event.GetY() - self.prev_mouse_y
            self.a_panel.pos = (self.a_panel.pos[0] - dx,
                                self.a_panel.pos[1] - dy)
            self.viewer.update_view()
            self.prev_mouse_x = event.GetX()
            self.prev_mouse_y = event.GetY()

    def mouse_zoom_a(self, event):
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
        
        self.viewer.update_view()
        # NB: потом надо как-то разобраться с левой-правой картинкой
    
    def select_ab_side(self, side, choices):
        """
        Аргументы:
          side (string): "a" или "b"
          choices (list или tuple размера 2)
        Возвращает: choices[0] или choices[1]
        Исключения: ValueError, если side неправильный
        """
        control = None
        if (side == "a") or (side == "A"):
            return choices[0]
        if (side == "b") or (side == "B"):
            return choices[1]
        raise ValueError("side must be \"a\" or \"b\"")
    
    def rebind_mouse_events(self, side, func=None):
        """
        Изменить обработчик всех событий мыши, кроме кручения колесика, для 
        картинок (a_bmp или b_bmp).
        Аргументы:
          side - string, "a" или "b"
          func - callable(event) или None. Будет вызываться для всех событий
                 мыши, кроме кручения колесика. Если None, то включается
                 стандартный обработчик в зависимоти от того, нажата кнопка
                 с луппой или нет.
        Возвращает: ничего
        Исключения: ValueError, если side неправильный
        """
        (control, side_is_a) = self.select_ab_side(side,
                                                   ((self.a_bmp, True),
                                                    (self.b_bmp, False)))
        control.Unbind(wx.EVT_MOUSE_EVENTS)
        if func is None:
            if self.zoom_tool.IsToggled() and side_is_a:
                func = self.mouse_drag_a
        if func is not None:
            control.Bind(wx.EVT_MOUSE_EVENTS, func)
    
    def rebind_mouse_wheel_event(self, func = None):
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
                func = self.mouse_zoom_a
        if func is not None:
            self.Bind(wx.EVT_MOUSEWHEEL, func)

    def size_func(self, event):
        self.Layout()
        if self.viewer is not None:
            self.viewer.update_view()
        event.Skip()
    
    def enter_preview(self, auto_life_view):
        """
        Переход в режим Preview.
        Инициализация loader, viewer на основе self.config
        Аргуметы:
          auto_life_view (bool): если до этого был включен режим Life view, то
                                 попытаться перейти сразу в него.
        Возвращает: ничего
        """
        self.close_viewer()
        if (self.config.source_type != configuration.IMG_SOURCE):
            logging.error("Non supported yet!")
            return
        frt = (self.config.frames_range[0], 
               self.config.frames_range[0] + self.config.frames_count)
        loader = loading.image_loader(self.config.pic_path, frt)                                       
        self.viewer = view.Preview(self, loader, self.config.frames_range[0])
        self.my_toolbar.Enabled = True
        if self.cur_frame_num < self.config.frames_count \
           and self.cur_frame_num > 0:
            self.viewer.goto_frame(self.cur_frame_num)
            
    def config_source_menu_func(self, event):
        "Нажали меню Параметры -> Источник"
        dlg = source_gui.SourceDlg(self)
        dlg.ShowModal()


def main():
    logging.basicConfig(format="%(levelname)s: %(module)s: %(message)s",
      level=logging.DEBUG)
    app = wx.App()
    wx.Log_EnableLogging(False)
    main_video_frame = MainVideoFrame(None)
    main_video_frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()

