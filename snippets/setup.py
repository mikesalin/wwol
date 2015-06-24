# -*- coding: utf-8 -*-
"""
Данный модуль предназначен для 'компиляции' графера как отдельного приложения
по виндой. Не тестировался для создания пакетов и прочего.
"""

import sys
from distutils.core import setup
import py2exe

sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\"
                "Redist\\X86\\Microsoft.VC90.CRT")

setup(windows = ['grapher_gui.py'],
      options = {'py2exe' : {'excludes' : ['Tkinter',
                                           'Tkconstants'
                                          ]
                             }
      }
)
