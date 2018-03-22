# -*- coding: utf-8 -*-
"В этом модуле класс окна для снятия точек с картинки: PointsDlg"

from StringIO import StringIO
import numpy as np
import wx

from . import wxfb_output
from .mvf_aux_classes import Selection
from ..common import my_encoding_tools as et
from ..engine import geom


class PointsDlg(wxfb_output.PointsDlg):
    """
    Диалог для снятия точек с картинки
    """
    def __init__(self, parent):
        wxfb_output.PointsDlg.__init__(self, parent)
        self._update_buttons()        
        self._data2sel(parent.user_points)
        self._data2text(parent.user_points)
        if parent.user_points.size == 0:
            self.coords_text.SetValue(self._COORDS_TEXT_WELCOME)

    
    _COORDS_TEXT_WELCOME = ""
    
    
    def _update_buttons(self):
        parent = self.GetParent()
        proc = parent._in_processing_mode()
        self.b2a_button.Enable(proc)
        self.sel_b_button.Enable(proc)
        if proc:
            self.a2b_button.SetLabel("A -> В")
        else:
            self.a2b_button.SetLabel(u"Apply")

    
    def _data2text(self, data):
        fakefile = StringIO()
        fmt = '%0.3f'
        if data.size > 0:
            for j in range(0, data.shape[1]):
                if j == 0: fmt = '%d'
                if j == 1: fmt += ' %d'
                if j > 1: fmt += ' %0.3f'
        np.savetxt(fakefile, data, fmt)
        self.coords_text.SetValue(fakefile.getvalue())


    def _data2sel(self, data):
        if data is None: data = np.array([ ])
        parent = self.GetParent()
        sel_data = parent.sel_data
        sel_data.points_a = [ ]
        sel_data.points_b = [ ]
        for j in range(0, data.shape[0]):
            sel_data.points_a.append( (data[j, 0], data[j, 1]) )
        if len(data.shape) == 2 and data.shape[1] >= 4:
            for j in range(0, data.shape[0]):
                sel_data.points_b.append( (data[j, 2], data[j, 3]) )
        parent._viewer_update_view()

        
    def _text2data(self, quiet):
        s = et.clean_input_string(self.coords_text.GetValue())
        if len(s) == 0:
            return np.ndarray((0,2))
        fakefile = StringIO(s)
        try:
            data = np.loadtxt(fakefile)
            if not np.all(np.isfinite(data)):
                raise ValueError("nan / inf")
        except ValueError as err:
            if not quiet:
                dlg = wx.MessageDialog(self,
                                       et.U(str(err)),
                                       "Invalid input values",
                                       wx.ICON_EXCLAMATION | wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            return None
        if (len(data.shape) == 1) and (data.size > 0):
            data = np.reshape(data, (1, data.size))
        if (len(data.shape) != 2) or (data.shape[1] != 2 and data.shape[1] != 4):
            print(data.shape)
            if not quiet:
                dlg = wx.MessageDialog(
                    self,
                    u"A table with 2 or 4 columns is expected",
                    "",
                    wx.ICON_EXCLAMATION | wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            return None
        return data

    
    def _a2b(self, data_in):
        parent = self.GetParent()
        if (data_in is None) or (data_in.size == 0):
            return np.array([ ])
        if not parent._in_processing_mode():
            data2 = np.ndarray((data_in.shape[0], 2))
            data2[:, :] = data_in[:, :2]
            return data2
        data_out = np.ndarray((data_in.shape[0], 4))
        for j in range(0, data_in.shape[0]):
            data_out[j, :2] = data_in[j, :2]
            data_out[j, 2:4] = geom.a2b((data_in[j, 0],  data_in[j, 1]),
                                        parent.config,
                                        parent.viewer.get_raw_img_size())
        return data_out


    def _b2a(self, data_in):
        parent = self.GetParent()
        data_out = np.copy(data_in)
        for j in range(0, data_in.shape[0]):
            data_out[j, :2] = geom.b2a((data_in[j, 2],  data_in[j, 3]),
                                        parent.config,
                                        parent.viewer.get_raw_img_size())
            data_out[j, 2:4] = data_in[j, 2:4]
        return data_out

    
    def close_func(self, event):
        "Закрытие окна"
        parent = self.GetParent()
        data = self._text2data(quiet = True)
        if data is not None:
            parent.user_points = data

        parent.my_toolbar.ToggleTool(parent.points_tool.GetId(), False)
        parent.points_dlg = None

        sel_data = parent.sel_data
        sel_data.points_a = [ ]
        sel_data.points_b = [ ]
        parent._viewer_update_view()

        self.Destroy()

        
    def _a2b_button_func(self, event):
        self._update_buttons()
        data = self._text2data(quiet = False)
        if data is None: return
        data = self._a2b(data)
        self._data2sel(data)
        self._data2text(data)
    

    def _b2a_button_func(self, event):
        self._update_buttons()
        data = self._text2data(quiet = False)
        if data is None: return
        data = self._b2a(data)
        self._data2sel(data)
        self._data2text(data)    


    def _sel_a_button_func(self, event):
        self._sel_ab_button_func(side_is_a = True)
        
        
    def _sel_b_button_func(self, event):
        self._sel_ab_button_func(side_is_a = False)
    
    
    def _sel_ab_button_func(self, side_is_a):
        self._update_buttons()
        data = self._text2data(quiet = True)
        if data is None:
            if self.coords_text.GetValue() != self._COORDS_TEXT_WELCOME:
                dlg = wx.MessageDialog(self,
                                       u"Can't parse the existing table." 
                                       u"Reset input?",
                                       "",
                                       wx.ICON_EXCLAMATION | wx.YES_NO)
                rv = dlg.ShowModal()                
                dlg.Destroy()
                if rv == wx.ID_NO: return

        self._data2sel(data)
        parent = self.GetParent()
        sel_data = parent.sel_data
        if side_is_a:
            sel_data.points_b = [ ]
        else:
            sel_data.points_a = [ ]
        self.Hide()
        if side_is_a:
            parent.start_selecting(Selection.MULTIPLE_POINTS_A,
                                   self.finish_sel_a)
        else:
            parent.start_selecting(Selection.MULTIPLE_POINTS_B,
                                   self.finish_sel_b)
            
        
    def finish_sel_a(self):
        self.Show()
        parent = self.GetParent()
        sel_data = parent.sel_data
        if not parent.sel_ok:
            data = self._text2data(quiet = True)
            self._data2sel(data)
            return
        data = np.array(sel_data.points_a)
        data = self._a2b(data)
        self._data2text(data)
        self._data2sel(data)
        

    def finish_sel_b(self):
        self.Show()
        parent = self.GetParent()
        sel_data = parent.sel_data
        if not parent.sel_ok:
            data = self._text2data(quiet = True)
            self._data2sel(data)
            return
        data23 = np.array(sel_data.points_b)
        data = np.ndarray((data23.shape[0], 4))
        data[:, 2:] = data23
        data = self._b2a(data)
        self._data2text(data)
        self._data2sel(data)

        
