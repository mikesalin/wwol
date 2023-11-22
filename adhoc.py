# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"Место для временных решений."

from wwol import sub_start
from wwol.utils import calibrator


def main():
    sub_start.init_essentials()
    
    calibrator.horizontal_lines(output_dir='/mnt/common/bmp_out', num_frames=16,
                                wavelength=10, move_step=2,
                                full_w=1920, full_h=1080,
                                area_x0=358, area_y0=238,
                                area_w=1542-358, area_h=200,
                                wnd = True)
    

if __name__ == '__main__':
    main()
