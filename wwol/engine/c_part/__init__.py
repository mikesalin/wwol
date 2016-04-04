# -*- coding: utf-8 -*-
"""
Модуль расширения на языке Си

transform_frame.transform_frame(*arg)
    Коррекция перспектривы.
    Аргументы:
        pdFrame (np.ndarray, 2d, dtype=np.float64): Выход [высота, ширина]
        pcImg (np.ndarray, 3d, dtype=np.uint8): Вход RGB [высота, ширина, цвет]
        color_depth (int): пока игнорируется
        A (float):  коэфициенты для проецирования, см. geom.py
        B (float)
        C (float)
        X1 (float): левый верхний и правый нижний угол трапеции
        Y1 (float)
        X2 (float)
        Y2 (float)
    Возвращает:
        TransformFrameOutputParam:
            flag (int): 0 - ок, 1 - вышел за пределы
            Lx (float): размер области обработки в метрах
            Ly (float)

    Заметьте, здесь X1, Y1, X2, Y2 -- углы трапеции, в то время как в в config
    -- это углы описанного прямоугольника.
"""
