# -*- coding: utf-8 -*-
"""
В этом модуле определен класс диалога масштабирования
"""

import wxfb_output
import logging

class ZoomDlg(wxfb_output.ZoomDlg):
    """
    Маленькое окошечко с кнопками для масштабирования.
    Его присутсвие на экране означает, что в главном окне картинку можно
    перетаскивать мышью.
    Parent должен быть MainVideoFrame
    """
    def close_func(self, event):
        """
        При закрытии окна нужно 'отжать' кнопку в родительском окне и удалить
        там ссылку на данное окно.
        """
        main_video_frame = self.GetParent()
        tid = main_video_frame.zoom_tool.GetId()
        main_video_frame.my_toolbar.ToggleTool(tid, False)
        main_video_frame.zoom_tool_func(None) #эта фукция уничтожит данное окно
    
    def set_zoom_choice(self, side, value):
        """
        Изменяет значение в переключалке зума.
        Аргументы:
          side (string): "a" или "b"
          value (float)
        """
        values = [0.5, 1.0, 1.5, 2.0] # стандартные значения зума
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
        
    
    def reset_a_button_func(self, event):
        "Левая кнопка сброс"
        main_video_frame = self.GetParent()
        main_video_frame.a_panel.zoom = 1.0
        main_video_frame.a_panel.pos = (0, 0)
        self.set_zoom_choice("a", 1.0)
        if main_video_frame.viewer is not None:
            main_video_frame.viewer.update_view()
    
    def zoom_a_choice_func(self, event):
        "Переключили зум А"
        mvf = self.GetParent() # MainVideoFrame
        if mvf.viewer is None: return
        s = self.zoom_a_choice.GetString(self.zoom_a_choice.GetSelection())
        mvf.a_panel.zoom = float(s[:-1]) * 0.01
        mvf.viewer.update_view()



