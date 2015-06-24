# -*- coding: utf-8 -*-
"Дополнительные, небольшие классы для нужд main_video_gui.MainVideoFrame"

class Selection:
    """
    Содержит данные по выделенным на изображении точкам и площадям.
    Когда речь идет о точках на изображении 'а', то координаты соответствуют
    пикселям исходного (не масштабированного и не сдвинутого) изображения.
    .mode = .OFF
            .SINGLE_POINT_A
            .MULTIPLE_POINTS_A
            .SINGLE_RECT_A
            .MULTIPLE_RECTS_A
    .points_a ( list of tuples (int,int) ~ [ (x, y), ... ] ):
        координаты точек, выделенных на изображении 'a'.
        В режиме mode = MULTIPLE_POINTS_A:
          в начале работы -- умолчательный выбор,
          в конце работы  -- результат выбора пользователя.
        В других режимах:
          просто точки для отображения.
    .rects_a ( list of tuples (4 * int) ~ [ (x1, y1, x2, y1), ... ] ):
        координаты верхнего-левого (x1,y1) и нижнего-правого (x2,y2) углов
        прямоугольника на изображении 'a'.
        В режиме mode = MULTIPLE_RECTS_A:
          в начале работы -- умолчательный выбор,
          в конце работы  -- результат выбора пользователя.
        В других режимах:
          просто точки для отображения.
    .sel_item (тип соответствует одному элементу points_a / rects_a....):
        выделенный элемент, когда требуется выделить только один элемент,
        актуально в режимах mode = SINGLE_...,
        в начале работы -- изначально выбранный элемент, который пользователь
                           может изменять (редактировать) или None
        в конце работы  -- результат выбора пользователя.
    .trpz (list of tuples, один элемент списка -- 
           выход geom.trapezoid_inside_rectangle):
        список трапеций, получающихся проецированием областей из rects_a.
        Длина списка может быть: 0, len(rects_a)  len(rects_a) + 1, где
        последний элемент относится к sel_item.
        Пользователю не нужно самому заполнять этот список -- нужно вызвать
        MainVideoFrame.maintain_sel_trpz() и класс будет сам отслеживать
        изменения rects_a и приводить trpz в соответствие.
    """
    OFF = 0
    SINGLE_POINT_A = 1
    MULTIPLE_POINTS_A = 2
    SINGLE_RECT_A = 3
    MULTIPLE_RECTS_A = 4
    
    def __init__(self):
        self.mode = self.OFF
        self.points_a = []
        self.rects_a = []
        self.sel_item = None
        self.trpz = []

class _PseudoEvent:
    """
    Класс, которые можно передавать в мои обработчики событий вместо wx.Event
    Данные:
      .vetoed
      .skipped
    """
    def __init__(self):
        self.vetoed = False
        self.skipped = False
    def Skip(self):
        self.skipped = True
    def Veto(self):
        self.vetoed = True
