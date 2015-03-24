# -*- coding: utf-8 -*-
"Передача данных из конфига в низкоуровневые функции"

import logging
import wx

import loading
import configuration
IMG_SOURCE = configuration.IMG_SOURCE
FFMPEG_MANUAL_SOURCE = configuration.FFMPEG_MANUAL_SOURCE
FFMPEG_AUTO_SOURCE = configuration.FFMPEG_AUTO_SOURCE


def make_loader(config, gui_binding = None):
    """
    Создать загрузкик по конфигу.
    Аргументы:
      config (Config)
      gui_binding (MainVideoFrame или None): некоторым типы загрузчиков
                  могут выдавать информацию о процессе своей работы в окно.
    Возвращает: генератор, например, см. help(loading.image_loader) или None
    """
    d = {IMG_SOURCE : _make_image_loader,
         FFMPEG_MANUAL_SOURCE : _make_ffmpeg_loader,
         FFMPEG_AUTO_SOURCE : _make_ffmpeg_loader}
    if not d.has_key(config.source_type):
        logging.error("Unsupported source type")
        # + gui сообщение...
        return None
    return d[config.source_type](config, gui_binding)

def _make_image_loader(config, gui_binding = None):
    "См. описание make_loader"
    return loading.image_loader(config.pic_path, config.valid_frames_range())

def _make_ffmpeg_loader(config, gui_binding = None):
    "См. описание make_loader"
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
            logging.error("User should explicitly check the loader command, "
                          "which was manually set in config file.")
            # + gui сообщение...
            return None
    
    loader = loading.ffmpeg_loader(loader_cmd,
                                   config.pic_path,
                                   config.pack_len,
                                   config.valid_frames_range(),
                                   config.fps,
                                   use_shell,
                                   on_start_lap = splash_func)
    return loader
