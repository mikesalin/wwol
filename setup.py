# -*- coding: utf-8 -*-

from distutils.core import setup, Extension
import sys
import os.path
import numpy as np

ON_WINDOWS = (sys.platform == 'win32')
WITH_PY2EXE = ON_WINDOWS
if (WITH_PY2EXE):
    import py2exe
    import wwol.setup_.py2exe_stuff
    py2exe_setup_kwargs = wwol.setup_.py2exe_stuff.setup_kwargs()
else:
    py2exe_setup_kwargs = { }

import wwol

C_PART_DIR = 'wwol/engine/c_part/'
numpy_include_dir = os.path.join(os.path.dirname(np.__file__), 'core\\include')

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
                    include_dirs = [ [],
                                     [numpy_include_dir]]
                                   [ON_WINDOWS],
                    extra_compile_args = [ ['-fopenmp', '-O3'],
                                           ['/MT', '/openmp']]
                                         [ON_WINDOWS],
# если под виндой возникают проблемы с загрузкой собраной библиотеки (особенно в VS2008),
#  то можно попробовать заменить '/openmp' на '/DNO_OPENMP_WORKAROUND'
                    libraries = [ ],
                    library_dirs = [ ],
                    extra_link_args = [ ['-fopenmp'],
                                        ['/SUBSYSTEM:WINDOWS,5.01', '/MANIFEST']]
                                      [ON_WINDOWS]
          )
      ],
      
      **py2exe_setup_kwargs
)

