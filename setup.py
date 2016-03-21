# -*- coding: utf-8 -*-
"""
Данный модуль предназначен для 'компиляции' под виндой.
Не предназначен и ни разу не пробовался для создания пакетов и прочего.
"""

import sys
from distutils.core import setup
import shutil
import py2exe
from wwol.setup_.jsonschema_py2exe_workaround import JsonSchemaCollector
            
sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\"
                "Redist\\X86\\Microsoft.VC90.CRT")

setup(windows = ['start_from_here.py'],
      options = {'py2exe' : {'excludes' : ['Tkinter',
                                           'Tkconstants',
                                           'scipy.sparse'
                                          ]
                             }
                },
       cmdclass={"py2exe": JsonSchemaCollector},
       zipfile=None
)

more_files = ['swimmer_.exe', 'libfftw3-3.dll']
for fname in more_files:
    shutil.copyfile(fname, 'dist\\' + fname)