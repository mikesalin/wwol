# -*- coding: utf-8 -*-
"В этом модуле определен класс диалога 'Источник изображения'"

import copy
import wx

import wxfb_output
import configuration
ConfigError = configuration.ConfigError

class SourceDlg(wxfb_output.SourceDlg):
    """
    Окно 'Источник изображения'
    Parent должен быть MainVideoFrame
    При создании поля диалога инициализируются из parent.config.
    Результатом нажатия ОК/Применить является изменение GetParent().config и
    вызов GetParent().enter_preview
    """ 
    def __init__(self, parent):        
        wxfb_output.SourceDlg.__init__(self, parent) #initialize parent class
        config = parent.config
        self.source_type_choice.SetSelection(config.source_type)
        
        self.pic_path_text.SetValue(config.user_pic_path)
        self.start_text.SetValue("%d" % config.frames_range[0])
        if config.frames_range[1] == -1:
            s = ""
        else:
            s = "%d" % config.frames_range[1]
        self.finish_text.SetValue(s)
        self.max_finish_check.SetValue(config.frames_range[1] == -1)
        self.fps_text.SetValue(repr(config.fps))
        self.pack_len_text.SetValue("%d" % config.pack_len)
        self.overlap_check.SetValue(config.overlap)
        
        self.hide_show_items()
    
    def close_func(self, event):
        event.Skip()
            
    def source_type_choice_func1(self, event):
        "Перключалка 'тип источника', уходим со страницы"
        pass
        
    def source_type_choice_func2(self, event):
        "Перключалка 'тип источника', приходим на страницу."
        self.hide_show_items()
    
    def hide_show_items(self, event = None):
        "Скрывает/показывает элементы, в зависимости от переключалок."
        auto_sect = (self.source_type_choice.GetSelection()==0)        
        self.fps_text.Show(not auto_sect)
        self.fps_static_text.Show(not auto_sect)
        
        user_temp_path = (not auto_sect) or self.user_temp_path_check.GetValue()
        self.pic_path_text.Show(user_temp_path)
        self.pic_path_static_text.Show(user_temp_path)
        self.pic_path_comment_static_text.Show(user_temp_path)
        self.pic_path_browse_button.Show(user_temp_path)
        
        b = self.max_finish_check.GetValue()
        self.finish_text.Show(not b)
        self.max_finish_sttext.Show(b)
        
        self.Layout()
            
    def apply_button_func(self, event):
        """
        Нажали на кнопку применить.
        event is not None: ничего не возвращает
        event is None: (признак того, что функция вызвана программно) возвращает
                       True/Falsе в зависимости от того, удалось ли считать и
                       обработать все поля
        """
        try:
            config = self.form_to_config()
            config.post_config()
        except ConfigError as err:
            msg_dlg = wx.MessageDialog(self,
                                       "Неправильный ввод настроек! %s" % err,
                                       "",
                                       wx.ICON_ERROR)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()            
            if event is None:
                return False
            else:
                return
        
        mvf = self.GetParent() # MainVideoFrame
        mvf.config = config
        mvf.enter_preview(True)
        if event is None:
            return True
        else:
            return
    
    def ok_button_func(self, event):
        if self.apply_button_func(None):
            self.Destroy()    
    
    def form_to_config(self):
        """
        Считать значения из элементов управления окна.
        Возвращает: Config: локальная копия self.GetParent().config, где
                            изменены нужные поля.
        Исключения: ConfigError
        """
        config = copy.deepcopy(self.GetParent().config)
        config.source_type = self.source_type_choice.GetSelection()        
        
        if config.need_user_pic_path():
            config.user_pic_path = self.pic_path_text.GetValue()
        try:
            config.frames_range = (int(self.start_text.GetValue()), -1)
            if not self.max_finish_check.GetValue():
                config.frames_range = (config.frames_range[0],
                                      int(self.finish_text.GetValue()))                
            if config.need_fps():
                config.fps = float(self.fps_text.GetValue())
            config.pack_len = int(self.pack_len_text.GetValue())
        except ValueError:
            raise ConfigError("Проверьте числовые значения.")
        config.overlap = self.overlap_check.GetValue()
        
        return config
        
        
