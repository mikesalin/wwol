# -*- coding: utf-8 -*-
"""
Создать набор тестовых картинок.
Пока к функциям нет доступа из интрефейса. Вызывается через adhoc.py
"""

import os.path
from math import *
import numpy as np
import wx


def horizontal_lines(output_dir, num_frames,
                     wavelength, move_step,
                     full_w, full_h,
                     area_x0, area_y0,
                     area_w, area_h,
                     wnd):
    """
    Горизонтальные линии.
    В папке output_dir создается num_frames изображений: 00000.bmp, 00001.bmp
    На белом экране внутри области размером (area_w, area_h) с левым-верхним
    углом в (area_x0, area_y0) рисуются черные линии. Размер по вертикали
    "черное и белое" wavelength. Каждый кадр картина смещается на move_step вниз.
    Полный размер кадра (full_w, full_h).
    """
    screen_yxc = np.ndarray((full_h, full_w, 3), dtype=np.uint8)
    screen_yxc.fill(255)
    inv_area_h = 1.0 / area_h
    for nframe in range(0, num_frames):
        for y in range(0, area_h):
            color = ((y - nframe * move_step) % wavelength) > wavelength / 2
            if wnd:
                color_max = 255 * sin(y * inv_area_h * pi)
            else:
                color_max = 255
            color = int(color) * color_max
            screen_yxc[y + area_y0, area_x0 : (area_x0 + area_w), 0].fill(color)
        for n in range(1, 3):
            screen_yxc[:, :, n] = screen_yxc[:, :, 0]
        img = wx.ImageFromBuffer(full_w, full_h, np.getbuffer(screen_yxc))
        img.SaveFile(os.path.join(output_dir, "%05d.bmp" % nframe),
                     wx.BITMAP_TYPE_BMP)
        if (nframe % 10 == 0): print(nframe)


def main():
    pass
    

if __name__ == '__main__':
    main()
