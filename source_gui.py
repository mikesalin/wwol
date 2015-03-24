# -*- coding: utf-8 -*-
"В этом модуле определен класс диалога 'Источник изображения'"

import copy
import logging
import wx

import wxfb_output
import configuration
ConfigError = configuration.ConfigError
import misc
import loading

class SourceDlg(wxfb_output.SourceDlg):
    """
    Окно 'Источник изображения'
    Parent должен быть MainVideoFrame
    При создании поля диалога инициализируются из parent.config.
    Результатом нажатия ОК/Применить является изменение GetParent().config и
    вызов GetParent().enter_preview
    
    NB, в след версии будет: инициализируется из данного config-а; при нажатии
    ОК/Применить и если нет ошибок ввода то данный config будет изменен
    "по указателю"
    """ 
    def __init__(self, parent):
        wxfb_output.SourceDlg.__init__(self, parent) #initialize parent class
        self.config_to_form(parent.config)
    
    def config_to_form(self, config):
        "Заполняет поля ввода в соответствии с config (тип Config)"
        self.source_type_choice.SetSelection(config.source_type)
        
        self.video_filename_text.SetValue(config.video_filename)
        self.user_temp_path_check.SetValue(config.user_pic_path_in_auto_mode)
        self.loader_cmd_text.SetValue(config.user_loader_cmd)
        self.use_shell_check.SetValue(config.user_use_shell)
        
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
            self.config_to_form(config)
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
        if config.source_type == configuration.FFMPEG_MANUAL_SOURCE:
            config.user_loader_cmd = misc.clean_input_string(
                                     self.loader_cmd_text.GetValue())
            config.user_use_shell = self.use_shell_check.GetValue()
            config.user_checked_loader_cmd = True
            if self.max_finish_check.GetValue():
                raise ConfigError("Опция 'Диапазон кадров->Макс' не работает "
                                  "в данном режиме. Вам нужно явно указать "
                                  "число кадров в файле.")
        
        config.video_filename= misc.clean_input_string(
                               self.video_filename_text.GetValue())
        config.user_pic_path = misc.clean_input_string(
                               self.pic_path_text.GetValue())
        config.user_pic_path_in_auto_mode= self.user_temp_path_check.GetValue()
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
        
        #если требуется, то предупредить о начальном пропуске кадров
        if config.source_type == configuration.FFMPEG_AUTO_SOURCE:
             try:
                 param = loading.video_probe(config.video_filename)
                 true_start = round(param.start * param.fps)
                 if config.frames_range[0] < true_start:
                     msg_dlg = wx.MessageDialog(
                       self,
                       "Рекомендуется начинать обработку с кадра № %d, поскольку "
                       "в начале записи содержатся пустые кадры." % true_start,
                       "",
                       wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL)
                     res = msg_dlg.ShowModal()
                     msg_dlg.Destroy()
                     if res == wx.ID_OK:
                         config.frames_range = (true_start, config.frames_range[1])
             except loading.FrameLoaddingFailed:
                 pass  # эта ошибка снова выскочит в дургом месте
        return config
    
    def loader_cmd_help_func(self, event):
        "Нажали на знак вопроса около поля 'команда' -- отобразить подсказку"
        msg_dlg = wx.MessageDialog(
            self,
            "В данном режиме WWOL будет время от времени запускать FFMPEG "
            "(или в общем случае любую другую программу) с помощью указанной "
            "Вами команды, чтобы получить фрагмент видеозаписи в виде пачки "
            "файлов графического формата, которая "
            "может содержать параметры подстановки:\n"
            "$START -- время начала очередного запрашиваемого фрагмента (сек),"
            "\n$PRESTART -- грубое значение времени начала.\n"
            "$SOFT_START -- добавка: START = PRESTART + SOFT_START "
            "(грубый-точный поиск начала).\n"
            "Эта команда должна сгенерировать файлы с именем, соответствующим "
            "полю 'Путь к картинкам', в количестве 'Число кадров для БПФ'. "
            "Если стоит галка 'shell', то команда будет вызываться через "
            "shell. \n"
            "Кнопка 'A' выдаст Вам стандартный вид команды, которую бы "
            "использовал WWOL в режиме 'ffmpeg (авто)'.",
            "",
            wx.ICON_INFORMATION)
        msg_dlg.ShowModal()
        msg_dlg.Destroy() 
    
    def auto_cmd_button_func(self, event):
        "Кпопка 'А' -- положить стандартное значение в поле 'команда'."
        video_filename= misc.clean_input_string(
                        self.video_filename_text.GetValue())
        user_pic_path = misc.clean_input_string(
                        self.pic_path_text.GetValue())
        ok = True
        try:
            fps = float(self.fps_text.GetValue())
            pack_len = int(self.pack_len_text.GetValue())
        except ValueError:
            ok = False
        
        if not ok:        
            logging.debug("Can't make auto command from current settings. "
                          "Using previous settings.")
            config = self.GetParent().config
            video_filename = config.video_filename
            user_pic_path = config.user_pic_path
            fps = config.fps
            pack_len = config.pack_len
            
        res = loading.make_ffmpeg_cmd(video_filename,
                                      pack_len,
                                      user_pic_path,
                                      fps)
        self.loader_cmd_text.SetValue(res)
        self.use_shell_check.SetValue(False)
        
