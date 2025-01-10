# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#

from distutils.core import setup, Extension
import sys
import os.path
import numpy as np

ON_WINDOWS = (sys.platform == 'win32')
ON_APPLE = (sys.platform == 'darwin')
#WITH_PY2EXE = ON_WINDOWS
WITH_PY2EXE = False
if (WITH_PY2EXE):
    import py2exe
    import wwol.setup_.py2exe_stuff
    py2exe_setup_kwargs = wwol.setup_.py2exe_stuff.setup_kwargs()
else:
    py2exe_setup_kwargs = { }

import wwol

C_PART_DIR = 'wwol/engine/c_part/'
#numpy_include_dir = os.path.join(os.path.dirname(np.__file__), 'core\\include')
my_extra_compile_args = ['-fopenmp', '-O3']
my_extra_link_args = ['-fopenmp']
if ON_WINDOWS: 
    my_extra_compile_args = ['/MT', '/openmp']
    my_extra_link_args = ['/SUBSYSTEM:WINDOWS,5.01', '/MANIFEST']
if ON_APPLE: 
    my_extra_compile_args = ['-DNO_OPENMP_WORKAROUND', '-O3']
    my_extra_link_args = []

setup(name = 'WWOL',
      version = wwol.__version__,
      description = 'Wind-Wave Optical Lab',
      author = 'Mike Salin',
      author_email = 'msalin@gmail.com',
      
      ext_package = 'wwol.engine.c_part',
      ext_modules = [
          Extension('_transform_frame',
                    [ C_PART_DIR + 'transform_frame.cpp',
                      C_PART_DIR + 'transform_frame.i' ],
                    include_dirs = [np.get_include()],
                    extra_compile_args = my_extra_compile_args,
# если под виндой возникают проблемы с загрузкой собраной библиотеки (особенно в VS2008),
#  то можно попробовать заменить '/openmp' на '/DNO_OPENMP_WORKAROUND'
                    libraries = [ ],
                    library_dirs = [ ],
                    extra_link_args = my_extra_link_args
          )
      ],
      
      **py2exe_setup_kwargs
)


# The `setup.py py2exe` command line interface is deprecated and
#  will be removed in the next major release.
# Please adapt your code to use the new `py2exe.freeze` API.
# https://github.com/py2exe/py2exe/blob/master/docs/py2exe.freeze.md
