# -*- coding: utf-8 -*-
"Создание и управление загрузчиками"

import wx

from ..common.my_encoding_tools import U
from . import loading
from . import configuration
IMG_SOURCE = configuration.IMG_SOURCE
FFMPEG_MANUAL_SOURCE = configuration.FFMPEG_MANUAL_SOURCE
FFMPEG_AUTO_SOURCE = configuration.FFMPEG_AUTO_SOURCE


def make_loader(config, gui_binding = None):
    """
    Создать загрузкик по конфигу.
    Аргументы:
      config (Config)
      gui_binding (MainVideoFrame или None): а. некоторым типы загрузчиков
                  могут выдавать информацию о процессе своей работы в окно;
                  б. для вывода сообщений об ошибках
    Возвращает: генератор, например, см. help(loading.image_loader)
                или None (если gui_binding != None, то выдаст MessageDialog)
    """
    if not config.source_set:
        _error2gui(gui_binding, "Сначала выберите видеофайл для обработки!")
        return None

    d = {IMG_SOURCE : _make_image_loader,
         FFMPEG_MANUAL_SOURCE : _make_ffmpeg_loader,
         FFMPEG_AUTO_SOURCE : _make_ffmpeg_loader}
    if not d.has_key(config.source_type):
        _error2gui(gui_binding, "Неизвестный тип загрузчика кадров")
        return None

    ldr = d[config.source_type](config, gui_binding)
    return ldr


def _make_image_loader(config, gui_binding = None):
    "Входные аргументы и возвращаемые значения как у make_loader"
    return loading.image_loader(config.pic_path, config.valid_frames_range())


def _make_ffmpeg_loader(config, gui_binding = None):
    "Входные аргументы и возвращаемые значения как у make_loader"
    if gui_binding is not None:
        splash_func = lambda: wx.CallAfter(gui_binding.hourglass)
    else:
        splash_func = None
    
    if config.source_type == FFMPEG_AUTO_SOURCE:
        loader_cmd = loading.make_ffmpeg_cmd(config.video_filename,
                                             config.pack_len,
                                             config.pic_path,
                                             config.fps)
        use_shell = False
    else:   # FFMPEG_MANUAL_SOURCE
        if config.user_checked_loader_cmd:
            loader_cmd = config.user_loader_cmd
            use_shell = config.user_use_shell
        else:
            _error2gui(gui_binding,
                       "Выбран ручной тип источника кадров. Из соображений "
                       "безопасности Вам следует сначала явным образом "
                       "посмотреть на команду, которая будет выполняться "
                       "на Вашем компьютере.\nНа вкладке 'Источник кадров' "
                       "нажмите 'Выбрать исходный файл', проверьте значение "
                       "в поле 'команда' и нажмите 'Ok'")
            return None
    
    loader = loading.ffmpeg_loader(loader_cmd,
                                   config.pic_path,
                                   config.pack_len,
                                   config.valid_frames_range(),
                                   config.fps,
                                   use_shell,
                                   on_start_lap = splash_func)
    return loader


def _error2gui(gui_binding, text):
    """
    Отбразить ошибку через ГУИ
    (или если его нет, то вывести в консоль)
    """
    if gui_binding is None:
        print("[ERROR] " + text)
        return
    dlg = wx.MessageDialog(gui_binding, U(text), '', wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

