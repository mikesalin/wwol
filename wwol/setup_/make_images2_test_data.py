# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
Makes data for the test 'images2.wwl'
The data is a set of .bmp files with running down strips.
Destination folder for data files is 'stuff/images2_test'
"""

import os
from ..utils import calibrator

def work():
    print('Going to populate the test dirrectory')
    DEST_DIR = 'stuff/images2_test/'
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    calibrator.horizontal_lines(
        output_dir=DEST_DIR, num_frames=300,
        wavelength=40, move_step=1.6,
        full_w=300, full_h=200,
        area_x0=0, area_y0=0,
        area_w=300, area_h=200,
        wnd=False)

def main():
    pass

if __name__ == '__main__':
    main()