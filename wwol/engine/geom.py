# -*- coding: utf-8 -*-
"""
Модуль для геометрических расчетов, проецирования и пр. (кроме функций, которые
непосредственно обрабатывают большие объемы данных)

Здесь часто используется термин коэффициенты проецировниая (a,b,с), которые
определены так:
  X'/ X = a * Y' + b
  Y'/ Y = c * X'/ X
где X', Y' - координаты на экране в пикселях относительно центра изображения,
             здесь Y' -- вверх
    X,  Y  - реальные координаты в метрах, на плоскости, относительно точки 
             пересечения плоскости с оптической осью (с прямой из центра
             изображения).
    размерности: [a] = 1/м, [b] = пкс/м, [c] - безразмерный, обычно a < 0.
    Не следует путать эти  X',Y' с обычными экранными координатами.

Здесь и далее слова "обычные экранные координаты" означают "как в bmp"
-- коорд. в пикселях от левого-верхнего угла, без преобразания изображения.
"""

import logging
from collections import namedtuple
from math import *
import scipy.optimize
from distutils.version import StrictVersion

ProjectingCoef = namedtuple('ProjectingCoef', ['a', 'b', 'c'])
IDENTICATL_PROJECTION = ProjectingCoef(0, 1, 1)


def set_abc(config):
    "Аргументы: config (Config) -- входной и выходной аргумент"
    l0_ = 180.0 / (config.angle_per_pixel * pi)
    tg_phi = tan(config.angle_to_vert * pi / 180.0)
    inv_cos_phi = sqrt(1 + tg_phi**2)
    l0 = config.camera_height * inv_cos_phi;
    a = -tg_phi / l0
    b = l0_ / l0
    c = 1.0 / inv_cos_phi;
    config.proj_coef = ProjectingCoef(a, b, c)
#    logging.debug("a = %0.6f, b = %0.3f, c = %0.3f", a, b, c)

DEFAULT_ANGLE_PER_PIXEL = 1


def set_simple_projection(meters_per_pixel, config):
    """
    Установить параметры проецирования, когда ось камеры перпендикулярна
    поверхности и задано отношение метры/пиксели.
    Аргменты:
        meters_pet_pixel (float)
        config (Config) : выходной аргумент (изменяется "по указателю")
    """
    config.angle_per_pixel = DEFAULT_ANGLE_PER_PIXEL
    config.camera_height = meters_per_pixel \
                           / (config.angle_per_pixel * pi / 180.0)
    config.angle_to_vert = 0
    set_abc(config)


def trapezoid_inside_rectangle(rect, proj_coef, img_size):
    """
    Находит трапецию в экранных координатах, удовлетворяющую условиям:
      -может являться результатом проецирования некоторой прямоугольной области
       на экран при заданных параметрах проецирования
      -вписана в заданный экранный прямоугольник (кроме особо кривых случаев)
    Аргументы:
        rect (tuple 4*int ~ (x1, y1, x2, y2) ): лево-верх и право-низ пр-ка,
                                                обычные экранные координаты
        proj_coef(ProjectingCoef): см. docstring модуля.
        img_size (tuple (int,int)): ширина / высота изображения
    Возвращает:
        tuple 8*int -- экранные углов трапеции, начиная с левого-верхнего угла
                       и по часовой стрелке.
    """
    x1_px, y1_px, x2_px, y2_px = rect
    a, b, c = proj_coef
    w, h = img_size
    default_res = (x1_px, y1_px, x2_px, y1_px, x2_px, y2_px, x1_px, y2_px)
    if (abs(a) < 1e-6) and (abs(c) < 1e-6):
        return default_res
    x1_px -= w/2
    x2_px -= w/2
    y1_px = h/2 - y1_px
    y2_px = h/2 - y2_px
    # -- ограничивающий пр-к на экране
    
    denom1 = 1.0 * a * y1_px + b
    denom2 = 1.0 * a * y2_px + b
    if (abs(denom1) < 1e-6) or (abs(denom2) < 1e-6):
        return default_res
    # определяем x1, x2 -- ограничения слева/справа в реальных коорд.
    # по верху (j=1) и по низу (j=2)
    x1_ar = [0, 0]
    x2_ar = [0, 0]
    for j in [1, 2]:
        denom = [denom1, denom2] [j-1]
        x1 = x1_px / denom
        x1_ar[j - 1] = x1
        x2 = x2_px / denom
        x2_ar[j - 1] = x2
    x1 = max(x1_ar)
    x2 = min(x2_ar)

    # формируем реузльтат
    conv_x = lambda xnm_px: int(round(xnm_px)) + w/2    
    xlt_px = conv_x(x1 * (a * y1_px + b))
    xrt_px = conv_x(x2 * (a * y1_px + b))
    xrb_px = conv_x(x2 * (a * y2_px + b))
    xlb_px = conv_x(x1 * (a * y2_px + b))
    ynt_px = h/2 - y1_px
    ynb_px = h/2 - y2_px
    return (xlt_px, ynt_px, xrt_px, ynt_px, xrb_px, ynb_px, xlb_px, ynb_px)
    
    # Для теста:
    # A=-0.259815
    # B=101.8474
    # C=0.1589
    # размеры экрана: FullHD
    # сдвиг ко всем коорд: 310, 58
    # дальше идут разные трапеции, нарисованные старой прогой:
    # 758,441,  1155,441,  1076,595,  494,595
    # 1041,615  1445,615,  1566,894,  886,894

    
def pixels_to_angle(coord, config, img_size, mode):
    """
    Возвращает угол от центра 
    Аргументы:
      coord (tuple (int,int)): координаты в пикселях от левевого-верхнего угла
      config (Config)
      img_size (tuple (int,int)): ширина / высота изображения
      mode ('v', 'h', 'f') : какой угол запрашивается
          - 'v' вертикальный (+ вверх)
          - 'h' горизонтальный (+ вправо)
          - 'f' полный (всегда неотрицательный)
    Возвращает:
      float: угол в градусах
    """
    # устраняем дисторсию
    norm = max(img_size[0], img_size[1]) / 2
    x_ = coord[0] - img_size[0]/2
    y_ = coord[1] - img_size[1]/2
    # r_ - нормированный радиус, с дисторсией    
    r_ = sqrt(x_**2 + y_**2) / norm
    k1, k2 = config.distortion_k1, config.distortion_k2
    poly = lambda r: r + k1 * r**3 + k2 * r**5 - r_
    poly_deriv = lambda r: 1 + 3 * k1 * r**2 + 5 * k2 * r**4
    poly_deriv2 = lambda r: 6 * k1 * r + 20 * k2 * r**3
    # r = l0 * tg_a - нормированный радиус, без дисторсии
    if k1 != 0.0 or k2 != 0.0:
        fprime2_kwarg = {'fprime2': poly_deriv2}
        if StrictVersion(scipy.__version__) < StrictVersion('0.11'):
            fprime2_kwarg = { }
        r = scipy.optimize.newton(poly, r_, fprime = poly_deriv,
                                  **fprime2_kwarg)
    else:
        r = r_
    # x, y - идеальные координаты, ненормированные, от центра и y вверх.
    x = 1.0 * x_ / r_ * r
    y = -1.0 * y_ / r_ * r
    
    d = None
    if mode == 'v': d = y
    if mode == 'h': d = x
    if mode == 'f': d = sqrt(x**2 + y**2)
    if d is None: 
        logging.debug('unknown mode in pixels_to_angle')
        d = 0
    angle = atan(d * config.angle_per_pixel * pi / 180.0) * 180.0 / pi
    return angle


def a2b(coord, config, img_size):
    """
    Пересчет из координат на изображении (пикселы) в координаты на
    спроецированной области (метры).
    Центр реальных кординат находится в центре активной области
    """
    x, y = a2b_scr_center(coord, config, img_size)
    aa = config.areas_list[config.active_area_num].coord
    xlb, ylb = a2b_scr_center((aa[0], aa[3]) , config, img_size)
    xrb, yrb = a2b_scr_center((aa[2], aa[3]) , config, img_size)
    xct, yct = a2b_scr_center((0.5*(aa[0]+aa[2]), aa[1]) , config, img_size)
    x = x - 0.5 * (xlb + xrb)
    y = y - 0.5 * (ylb + yct)
    return (x, y)


def a2b_scr_center(coord, config, img_size):
    "Аналогично a2b, но центр реальных кординат находится в центре экрана."
    a, b, c = config.proj_coef
    x_ = coord[0] - img_size[0]/2
    y_ = img_size[1]/2 - coord[1]
    x = (1.0 * x_) / (a * y_ + b)
    y = y_ / c / (a * y_ + b)
    return (x, y)
    

def b2a(coord, config, img_size):
    """
    Пересчет из координат спроецированной области (метры)
    в изображение (пикселы)
    """
    a, b, c = config.proj_coef
    x = coord[0]
    y = coord[1]
    x_ = b * x / (1.0 - a * c * y)
    y_ = b * c * y / (1.0 - a * c * y)
    return (int(round(x_ + img_size[0]/2)),
            int(round(img_size[1]/2 - y_)))
    
    
