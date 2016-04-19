# -*- coding: utf-8 -*-
"""
В этом модуле определена функция 'main', которая инициализирует необходимые
библиотеки и показывает главное окно. Эта функция выполняется, когда вы
вызываете:
  pyhton start.py
  
Если вам нужен какой-то специфический сценарий работы и вы хотите использовать
WWOL наподобие библиотеки, то вам необходимо вызвать функцию
'init_essentials'.
"""

import sys
import os
import logging
import locale


if not hasattr(sys, 'frozen'):
    import wxversion
    try:
        wxversion.ensureMinimal('3')
    except wxversion.AlreadyImportedError:
        logging.warning("You'd better import start module first")
import wx

from . import wwol_globals
from .base_gui import main_video_gui
from .common import my_encoding_tools


def init_essentials():
    "см. описание модуля"
    wwol_globals.app = wx.App()
    wx.Log_EnableLogging(False)
    my_encoding_tools._local_encoding = locale.getpreferredencoding()
   

def main():
    "см. описание модуля"
    if wwol_globals.VERBOSE:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR
    logging.basicConfig(format="%(levelname)s: %(module)s: %(message)s",
                        level=log_level)
    logging.debug('Using wxPython version ' + wx.version())
    
    p = os.path.dirname(sys.argv[0])
    if len(p) > 0:
        os.chdir(p)

    init_essentials()

    wwol_globals.main_video_frame = main_video_gui.MainVideoFrame(None)
    wwol_globals.main_video_frame.Show(True)
    wwol_globals.app.MainLoop()


if __name__ == '__main__':
    main()

