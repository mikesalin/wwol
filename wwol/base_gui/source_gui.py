# -*- coding: utf-8 -*-
"В этом модуле определен класс диалога 'Источник изображения'"

import copy
import logging
import os.path
import wx

from . import wxfb_output
from ..engine import configuration
ConfigError = configuration.ConfigError
from ..common.my_encoding_tools import clean_input_string, U
from ..engine import loading

class SourceDlg(wxfb_output.SourceDlg):
    """
    Окно 'Источник изображения'
    Parent должен быть MainVideoFrame
    При создании поля диалога инициализируются из parent.config.
    Результатом нажатия ОК (или Отмены после Применить) является изменение
    GetParent().config и вызов GetParent()._enter_preview_or_processing
    """

    SYSTEM_TEMP_PATH_CHOICE = 0
    USER_TEMP_PATH_CHOICE = 1
    
    def __init__(self, parent):
        wxfb_output.SourceDlg.__init__(self, parent) #initialize parent class
        self.config2form(parent.config)
        self.parent_config_changed = False
    
    def config2form(self, config):
        "Заполняет поля ввода в соответствии с config (тип Config)"
        self.source_type_choice.SetSelection(config.source_type)
        
        self.video_filename_text.SetValue(U(config.video_filename))
        #self.user_temp_path_check.SetValue(config.user_pic_path_in_auto_mode)
        if config.user_pic_path_in_auto_mode:
            self.temp_path_choice.SetSelection(self.USER_TEMP_PATH_CHOICE)
        else:
            self.temp_path_choice.SetSelection(self.SYSTEM_TEMP_PATH_CHOICE)
        self.loader_cmd_text.SetValue(U(config.user_loader_cmd))
        self.use_shell_check.SetValue(config.user_use_shell)
        
        self.pic_path_text.SetValue(U(config.user_pic_path))
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
        
        #user_temp_path = (not auto_sect) or self.user_temp_path_check.GetValue()
        user_temp_path = (not auto_sect) or \
          (self.temp_path_choice.GetSelection() == self.USER_TEMP_PATH_CHOICE)
        self.pic_path_text.Show(user_temp_path)
        self.pic_path_static_text.Show(user_temp_path)
        self.pic_path_comment_static_text.Show(user_temp_path)
        self.pic_path_browse_button.Show(user_temp_path)
        
        b = self.max_finish_check.GetValue()
        self.finish_text.Show(not b)
        self.max_finish_sttext.Show(b)
        
        self.Layout()
    
    def apply_button_func(self, event):
        "Нажали на кнопку применить"
        rv = self.apply_button_func_act()
        if not rv: return
        self.config2form(self.GetParent().config)
        self.parent_config_changed = True
            
    def apply_button_func_act(self):
        """
        Нажали на кнопку применить -- непосредственная работа.
        Возвращает True/Falsе в зависимости от того, удалось ли считать и
        обработать все поля
        """
        try:
            config = self.form2config()
            warn_txt = config.post_config('source')
        except ConfigError as err:
            msg_dlg = wx.MessageDialog(
                self,
                U("Can't read data with the given parameter values! %s" % err),
                "",
                wx.ICON_ERROR)
            msg_dlg.ShowModal()
            msg_dlg.Destroy()
            return False
        if warn_txt != "":
            msg_dlg = wx.MessageDialog(
                self,
                U("There are following issues, concerning the given values:\n\n%s"
                "\nApply these values for parameters?"
                    % warn_txt),
                "",
                wx.ICON_EXCLAMATION | wx.YES_NO)
            rv = msg_dlg.ShowModal()
            msg_dlg.Destroy()
            if rv == wx.ID_NO:
                self.config2form(config)
                return False
        
        mvf = self.GetParent() # MainVideoFrame
        mvf.config = config
        mvf.project_changed = True
        return True

    def ok_button_func(self, event):
        rv = self.apply_button_func_act()
        if not rv: return
        self.GetParent()._enter_preview_or_processing(
            mode = 0,
            must_restart_loader = True)
        self.Destroy()
    
    def close_func(self, event):
        event.Skip()
        if self.parent_config_changed:
            self.GetParent()._enter_preview_or_processing(
                mode = 0,
                must_restart_loader = True)
            self.parent_config_changed = False
    
    def form2config(self):
        """
        Считать значения из элементов управления окна.
        Возвращает: Config: локальная копия self.GetParent().config, где
                            изменены нужные поля.
        Исключения: ConfigError
        """
        config = copy.deepcopy(self.GetParent().config)
        
        config.source_type = self.source_type_choice.GetSelection()
        if config.source_type == configuration.FFMPEG_MANUAL_SOURCE:
            config.user_loader_cmd = clean_input_string(
                                     self.loader_cmd_text.GetValue())
            config.user_use_shell = self.use_shell_check.GetValue()
            config.user_checked_loader_cmd = True
        
        config.video_filename= clean_input_string(
                               self.video_filename_text.GetValue())
        config.user_pic_path = clean_input_string(
                               self.pic_path_text.GetValue())
        #config.user_pic_path_in_auto_mode = self.user_temp_path_check.GetValue()
        config.user_pic_path_in_auto_mode = \
            self.temp_path_choice.GetSelection() == self.USER_TEMP_PATH_CHOICE
        try:
            config.frames_range = (int(self.start_text.GetValue()), -1)
            if not self.max_finish_check.GetValue():
                config.frames_range = (config.frames_range[0],
                                      int(self.finish_text.GetValue()))                
            if config.need_fps():
                config.fps = float(self.fps_text.GetValue())
            config.pack_len = int(self.pack_len_text.GetValue())
        except ValueError:
            raise ConfigError("Check the numerical values.")
        config.overlap = self.overlap_check.GetValue()        
        
        #если требуется, то предупредить о начальном пропуске кадров
        if config.source_type == configuration.FFMPEG_AUTO_SOURCE:
             try:
                 param = loading.video_probe(config.video_filename)
                 true_start = round(param.start * param.fps)
                 if config.frames_range[0] < true_start:
                     msg_dlg = wx.MessageDialog(
                       self,
                       u"It seems like the video file contains empty frames "\
                       u"before the frame No. %d. Press OK to adjust the "\
                       u"processing limits." % true_start,
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
            u"Within this mode WWOL will call FFMPEG from time to time "
            u"(or any other defined program). "
            u"These calls are made, using the command, that is entered here. "
            u"After each call we expect to get a pack of frames within the "
            u"required time interval. \n"
            u"Thus the command contains the substitution parameters: \n"
            u"$START -- start of the interval in seconds\n"
            u"$PRESTART -- rough value of start, not greater than a true start\n"
            u"$SOFT_START -- offset so that START = PRESTART + SOFT_START\n"
            u"These call should generate a series of image files that satisfy "
            u"the template 'Path to images'",
            "",
            wx.ICON_INFORMATION)
        msg_dlg.ShowModal()
        msg_dlg.Destroy() 
    
    def auto_cmd_button_func(self, event):
        "Кпопка 'А' -- положить стандартное значение в поле 'команда'."
        video_filename= clean_input_string(
                        self.video_filename_text.GetValue())
        user_pic_path = clean_input_string(
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
        
    def _browse_video_file_func(self, event):
        "Нажали на кнопку '...' около имени файла"
        dlg = wx.FileDialog(self,
                    u'Choose a video file',
                    '',
                    self.video_filename_text.GetValue(),
                    u'*.*|*.*',
                    wx.FD_OPEN)
        rv = dlg.ShowModal()
        fname = clean_input_string(dlg.GetPath())
        dlg.Destroy()
        if rv == wx.ID_CANCEL: return
        self.video_filename_text.SetValue(U(fname))
    
    def _pic_path_browse_button_func(self, event):
        if self.source_type_choice.GetSelection() == 0:
            msg_u = u"Choose the path to temporary images"
        else:
            msg_u = u"Choose the path to images"
        dlg = wx.DirDialog(self,
                           msg_u,
                           os.path.dirname(self.pic_path_text.GetValue()))
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            dlg.Destroy()
            return
        self.pic_path_text.SetValue(dlg.GetPath())
        dlg.Destroy()
        

