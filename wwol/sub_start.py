# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
When you do not need to start the whole WWOL. E.g. for using WWOL as a library
"""

import logging
import wx
from . import wwol_globals

def init_essentials():
    "Does what the module does"
    wwol_globals.app = wx.App()
#    wx.Log_EnableLogging(False)
    
    for text in wwol_globals.POSTPONED_LOG:
        if text[0] == 'W':
            logging.warning(text)
        else:
            logging.debug(text)
    wwol_globals.POSTPONED_LOG[:] = []

def main():
    init_essentials()
    

if __name__ == '__main__':
    main()