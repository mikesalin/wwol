# -*- coding: utf-8 -*-
"""
Данный модуль предназначен для 'компиляции' под виндой.
Не предназначен и ни разу не пробовался для создания пакетов и прочего.
"""

import sys
from distutils.core import setup
import py2exe
from jsonschema_py2exe_workaround import JsonSchemaCollector
            
sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\"
                "Redist\\X86\\Microsoft.VC90.CRT")

setup(windows = ['start_from_here.py'],
      options = {'py2exe' : {'excludes' : ['Tkinter',
                                           'Tkconstants'
                                          ]
                             }
                },
       cmdclass={"py2exe": JsonSchemaCollector},
       zipfile=None
)

# см.
#http://stackoverflow.com/questions/30942612/py2exe-not-recognizing-jsonschema