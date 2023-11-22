# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
В этом модуле определена функция 'main', которая инициализирует необходимые
библиотеки и показывает главное окно. Эта функция выполняется, когда вы
вызываете:
  pyhton start.py
  
Если вам нужен какой-то специфический сценарий работы и вы хотите использовать
WWOL наподобие библиотеки, то вам необходимо вызвать функцию
'init_essentials' из модуля 'sub_start'
"""

import sys
import os
import logging
import locale

import wx

from . import wwol_globals, sub_start
from .base_gui import main_video_gui

def main():
    "снициализирует необходимые библиотеки и показывает главное окно"
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

    sub_start.init_essentials()

    wwol_globals.main_video_frame = main_video_gui.MainVideoFrame(None)
    wwol_globals.main_video_frame.Show(True)
    wwol_globals.app.MainLoop()

init_essentials = sub_start.init_essentials  # preserve old style

if __name__ == '__main__':
    main()

