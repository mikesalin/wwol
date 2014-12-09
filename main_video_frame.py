# -*- coding: utf-8 -*-
"""
В этом модуле определен класс главного окна
"""

import logging
import os
import wx

import wxfb_output
import wwol_glob

class MainVideoFrame(wxfb_output.MainVideoFrame):
    """
    Главное окно
    """
    def __init__(self, parent):        
        wxfb_output.MainVideoFrame.__init__(self,parent) #initialize parent class
        
        self.time_hl.SetVisitedColour(self.time_hl.GetNormalColour())
        # .....
        
    def time_hl_func(self, event):
        """
        Нажали на строчку, отображающую текущее время.
        Отобразить диалог ввода времени для перехода.
        """
        logging.debug("here")


def main():
    logging.basicConfig(format="%(levelname)s: %(funcName)s: %(msg)s",
      level=logging.DEBUG)
    wwol_glob.app = wx.App()
    wwol_glob.main_video_frame = MainVideoFrame(None)
    wwol_glob.main_video_frame.Show(True)
    wwol_glob.app.MainLoop()

if __name__ == '__main__':
    main()

