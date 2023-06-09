# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
В этом модуле определен диалог для выделения чего-либо на картинке мышью.
"""
import wx

from . import wxfb_output
from .mvf_aux_classes import Selection
from ..common.my_encoding_tools import U

class SelDlg(wxfb_output.SelDlg):
    """
    Диалог для выделения чего-либо на картинке мышью: окно, которое висит
    на экране при выборе точек / прямоугольников / чего-то еще и содержит
    кнопки 'Готово', 'Удалить (последнюю)' и 'Отмена'.
    
    Может изменять parent.sel_data и parent.sel_ok . При нажатии 'Готово'
    / 'Отмена' или при эквивалентных действиях вызывает
    parent._finish_selecting() .
    
    .basic_info
    """

    def __init__(self, parent, info):
        "Ожидается, что parent имеет тип MainVideoFrame."
        wxfb_output.SelDlg.__init__(self, parent)
        if len(info) == 0:
            DEFAULT_INFOS = \
              {Selection.SINGLE_POINT_A:
                 "Select a point on the left image and press DONE",
               Selection.MULTIPLE_POINTS_A:
                 "Select points on the left image and press DONE",
               Selection.SINGLE_RECT_A:
                 "Select a rectangle on the left image and press DONE",
               Selection.MULTIPLE_RECTS_A:
                 "Select one or more rectangles on the left image and press DONE",
               Selection.SINGLE_POINT_B:
                 "Select a point on the right image and press DONE",
               Selection.MULTIPLE_POINTS_B:
                 "Select points on the right image and press DONE",
               }
            self.basic_info = DEFAULT_INFOS[parent.sel_data.mode]
        else:
            self.basic_info = info
        self.adjust()
    
    def _active_list(self):
        """
        Возвращает актуальный список из sel_data, если включен режим выделения
        нескольких элементов, иначе None.
        """
        sel_data = self.GetParent().sel_data
        LISTS_BY_MODES = {Selection.MULTIPLE_POINTS_A: sel_data.points_a,
                          Selection.MULTIPLE_RECTS_A: sel_data.rects_a,
                          Selection.MULTIPLE_POINTS_B: sel_data.points_b}
        if sel_data.mode in LISTS_BY_MODES:
            return LISTS_BY_MODES[sel_data.mode]
        else:
            return None
    
    def working_with_a(self):
        mode = self.GetParent().sel_data.mode
        return (mode == Selection.MULTIPLE_POINTS_A) or \
            (mode == Selection.MULTIPLE_RECTS_A) or \
            (mode == Selection.SINGLE_POINT_A)
    
    def adjust(self):
        """
        Элементы окна настраиваются в зависимости от parent.sel_data
        и активности/неактивности режима масштабиования
        """
        parent = self.GetParent()
        if parent.zoom_dlg is not None:
            # мышь передана в управлении зуму
            INFO_IF_BLOCKED = "Close the 'Zoom and movement' window before " \
                              "you can proceed here"
            self.info_static_text.SetLabel(U(INFO_IF_BLOCKED))
        else:
            self.info_static_text.SetLabel(U(self.basic_info))
            bmp = [parent.b_bmp, parent.a_bmp] [self.working_with_a()]
            bmp.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        sel_data = parent.sel_data
        al = self._active_list()
        if al is None:
            have_selection = sel_data.sel_item is not None
        else:
            have_selection = len(al) > 0
        self.done_button.Enabled = have_selection
        self.del_button.Enabled = have_selection
        self.Layout()
    
    def _del_button_func(self, event):
        "Нажали на кнопку удалить"
        parent = self.GetParent()
        al = self._active_list()
        if al is None:
            parent.sel_data.sel_item = None
        else:
            al.pop()
        self.adjust()
        parent._maintain_sel_trpz_act()
        if parent.viewer is not None: parent.viewer.update_view()
    
    def _done_cancel_button_func(self, done):
        """
        Вызывается из _done_button_func (done = True) и 
        _cancel_button_func (done = False)
        """
        parent = self.GetParent()
        for ctrl in [parent.a_bmp, parent.b_bmp]:
            ctrl.SetCursor(wx.NullCursor)
        parent.sel_ok = done
        parent._finish_selecting() # данная функция убьет это окно
    
    def _done_button_func(self, event):
        "Нажали на кнопку 'готово'"
        self._done_cancel_button_func(True)
    
    def _cancel_button_func(self, event):
        """
        Нажали на кнопку 'Отмена' или закрываем окно через крестик (хотя сейчас
        этого крестика нет)
        """
        self._done_cancel_button_func(False)
       
       
