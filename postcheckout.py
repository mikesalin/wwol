# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
Getting some stuff ready after cloning the repository to a new clean folder
"""

#from wwol.setup_ import numpy_i_getter

import sys
import subprocess
from wwol.setup_ import make_images2_test_data, numpy_i_getter
from wwol.sub_start import init_essentials

def run_build_ext():
    call_cmd = [sys.executable, 'setup.py', 'build_ext', '--inplace']

    print('Going to build the extension')
    print('Emitting command:')
    print('    ' + ' '.join(call_cmd))
    print('NOTE: Windows users should run this step from the '
       'appropriate MS Visual C shell.')
    print(' ')

    subprocess.check_call(call_cmd)
    print('OK')

def main():
    numpy_i_getter.work()
    run_build_ext()
    init_essentials()
    make_images2_test_data.work()
    

if __name__ == '__main__':
    main()