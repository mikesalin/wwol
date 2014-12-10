# -*- coding: utf-8 -*-
"""
В этом модуле определен класс диалога 'Источник изображения'
"""

import wx

import wxfb_output

class SourceDlg(wxfb_output.SourceDlg):
    """
    Окно 'Источник изображения'
    Parent должен быть MainVideoFrame
    """        
    def close_func(self, event):
        """
        Нажали на кнопку закрыть (крестик).
        В этом случае окно просто прячется. По-настоящему закрыть окно можно
        только программно, методом Destroy().
        """
        self.Hide()
            
    def source_type_choice_func1(self, event):
        "Перключалка 'тип источника', уходим со страницы"
        pass
        
    def source_type_choice_func2(self, event):
        "Перключалка 'тип источника', приходим на страницу."
        self.hide_show_items()
    
    def hide_show_items(self):
        "Скрывает/показывает элементы, в зависимости от переключалок"        
        auto_sect = (self.source_type_choice.GetSelection()==0)        
        self.fps_text.Show(not auto_sect)
        self.fps_static_text.Show(not auto_sect)
        
        user_temp_path = (not auto_sect) or self.user_temp_path_check.GetValue()
        self.pic_path_text.Show(user_temp_path)
        self.pic_path_static_text.Show(user_temp_path)
        self.pic_path_comment_static_text.Show(user_temp_path)
        self.pic_path_browse_button.Show(user_temp_path)
        
        self.Layout()
    
    def user_temp_path_check_func(self, event):
        "Переключили галку 'Специальное место для временных файлов'"
        self.hide_show_items()        
        
