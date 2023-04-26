# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
В этом модуле определен класс диалога масштабирования
"""
import logging
import wx

from . import wxfb_output
from ..common import embed_gui_images

class ZoomDlg(wxfb_output.ZoomDlg):
    """
    Маленькое окошечко с кнопками для масштабирования.
    Его присутсвие на экране означает, что в главном окне картинку можно
    перетаскивать мышью.
    Parent должен быть MainVideoFrame
    """
    def __init__(self, parent):        
        wxfb_output.ZoomDlg.__init__(self, parent)
        self.set_zoom_choice("a", parent.a_panel.zoom)
        self.set_zoom_choice("b", parent.b_panel.zoom)
        self.reset_parents_cursor(wx.StockCursor(wx.CURSOR_SIZING))
        self.a_to_corner_button.SetBitmapLabel(
            embed_gui_images.get_to_cornerBitmap())
        self.b_to_corner_button.SetBitmapLabel(
            embed_gui_images.get_to_cornerBitmap())
    
    def reset_parents_cursor(self, cursor = wx.NullCursor):
        "Выставляет курсор в родительский a_bmp и b_bmp"
        self.GetParent().a_bmp.SetCursor(cursor)
        self.GetParent().b_bmp.SetCursor(cursor)
        
    def close_func(self, event):
        """
        При закрытии окна нужно 'отжать' кнопку в родительском окне и удалить
        там ссылку на данное окно.
        """
        main_video_frame = self.GetParent()
        tid = main_video_frame.zoom_tool.GetId()
        main_video_frame.my_toolbar.ToggleTool(tid, False)
        main_video_frame._zoom_tool_func(None) #эта фукция уничтожит данное окно
    
    def set_zoom_choice(self, side, value):
        """
        Изменяет значение в переключалке зума.
        Аргументы:
          side (string): "a" или "b"
          value (float)
        """
        values = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0] # стандартные значения зума
        special_value = True
        for v in values:
            if abs(v - value) < 0.01:
               special_value = False
               break
        if special_value:
            values.append(value) # впихнули свое значение зума (если надо)

        values.sort()
        pos = 0
        for n in range(0, len(values)):
            # ищем, где нужно значение в сортированном массиве
            if abs(values[n] - value) < 0.01:
                pos = n
                break

        # заполняем wx.Choice
        ctrl = self.GetParent().select_ab_side(side,
                                              (self.zoom_a_choice,
                                               self.zoom_b_choice))
        ctrl.Clear()
        for v in values:
            ctrl.Append("%0.0f%%" % (v*100.0))
        ctrl.SetSelection(pos)
    
    def main_video_frame_panel(self, side):
        main_video_frame = self.GetParent()
        rv = main_video_frame.select_ab_side(side,
                                             [main_video_frame.a_panel,
                                              main_video_frame.b_panel])
        return rv
    
    def reset_button(self, side):
        """
        Нажатие на кнопку сброс: левую (side=="a") или правую (side=="b")
        Вызывается из обработчика события.
        """
        panel = self.main_video_frame_panel(side)
        panel.zoom = 1.0
        panel.pos = (0, 0)
        self.set_zoom_choice(side, 1.0)
        main_video_frame = self.GetParent()
        if main_video_frame.viewer is not None:
            main_video_frame.viewer.update_view()
    
    def reset_a_button_func(self, event):
        "Левая кнопка сброс"
        self.reset_button("a")

    def reset_b_button_func(self, event):
        "Правая кнопка сброс"
        self.reset_button("b")

    def zoom_choice(self, side):
        """
        Переключили зум левый (side=="a") или правый (side=="b")
        Вызывается из обработчика события.
        """
        mvf = self.GetParent() # MainVideoFrame
        if mvf.viewer is None: return
        if side == "a":
            choice = self.zoom_a_choice
        else:
            choice = self.zoom_b_choice
        s = choice.GetString(choice.GetSelection())
        self.main_video_frame_panel(side).zoom = float(s[:-1]) * 0.01
        mvf.viewer.update_view()
    
    def zoom_a_choice_func(self, event):
        "Переключили зум А"
        self.zoom_choice("a")

    def zoom_b_choice_func(self, event):
        "Переключили зум Б"
        self.zoom_choice("b")
   
    def to_corner_button(self, side):
        """
        Кнопка в угол: левая (side=="a") или правая (side=="b")
        Вызывается из обработчика события.
        """
        self.main_video_frame_panel(side).pos = (0, 0)
        mvf = self.GetParent()  #MainVideoFrame
        if mvf.viewer is not None:
             mvf.viewer.update_view()
    
    def a_to_corner_button_func(self, event):
        "Левая кнопка 'в угол'"
        self.to_corner_button("a")

    def b_to_corner_button_func(self, event):
        "Левая кнопка 'в угол'"
        self.to_corner_button("b")


