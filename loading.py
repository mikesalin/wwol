# -*- coding: utf-8 -*-
"""
Модуль описывает классы для закрузки видеокадров.
Основные функции/классы:
  image_loader
  ...
"""

import logging
import threading
import Queue
import wx

class LoadingError(Exception):
    "Базовый класс для исключений загрузчика"
    pass
class FrameLoaddingFailed(LoadingError):
    "Исключение, когда не удалось загрузить кадр."
    pass
class BadFormatString(LoadingError):
    """
    Исключение, когда задан неверный шаблон для prinf.
    (TypeError: not enough arguments for format string,
    TypeError: not all arguments converted during string formatting, ...)
    """
    pass

class StopFlag:
    "Специальный входной тип для AsyncBmpLoader.task_queue"
    pass

class AsyncImageLoader(threading.Thread):
    """
    Асинхронная загрузка файлы простого графического формата.
    Вспомогательный класс для BmpLoader. Использование:
    - передать шаблон имени файла в конструкторе
    - класть номера кадров (тип int) в .task_queue
    - брать результат из .result_queue, тип результата (int, X), где:
      - int - номер запрошенного кадра
      - X - это:
        - wx.Image, если все ОК
        - FrameLoaddingFailed, BadFormatString - флаг ошибки
    - положить StopFlag() в .task_queue, прежде чем делать .join()    
    """
    def __init__(self, filename_pattern):
        "filename_pattern -- string, см. help(BmpLoader)"
        threading.Thread.__init__(self)
        self.filename_pattern = filename_pattern
        self.task_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
    
    def run(self):
        "Код для испольнения в другом потоке"
        while True:
            frame_num = self.task_queue.get()
            if (isinstance(frame_num, StopFlag)): return
            try:
                filename = self.filename_pattern % frame_num
            except TypeError:
                logging.error("Can't parse '%s'! "\
                              "Expected smth like 'file%%04d.bmp'." % \
                               self.filename_pattern)
                self.result_queue.put( (frame_num, BadFormatString()) )
                continue
            img = wx.Image(filename)
            if not img.IsOk():
                logging.error("Can't load '%s'!" % filename)
                img = FrameLoaddingFailed()
            self.result_queue.put( (frame_num, img) )

def image_loader(filename_pattern, numbers_range, step=1):
    """
    Загружает один-за-одним файлы простого графического формата. Генератор.
    Предварительно загружает следующий кадр во втором потоке
    Аргументы:
      filename_pattern -- string, имя файла в формате printf, которое содержит
                          %d (или, например, %04d) для подстановки номера.
      numbers_range -- tuple, (первый, последний+1)
      step -- int, шаг для .next() и для предзагрузки следующего кадра
    Yield: 
      wx.Image
    Может кидать исключения:
      FrameLoaddingFailed, BadFormatString, StopIteration
    Как генератор, имеет методы:
      .next() -- возвращает следующий кадр
      .send(n) -- переводит счетчик на кадр n, возвращет n-ый кадр                  
                  (нельзя вызывать send до первого next)
      .close()
    Замечание: в высокоуровневых классах используются логические номера кадров,
    которые всегда идут с 0. Здесь номер -- число, которое стоит в имени файла
    """
    async_loader = AsyncImageLoader(filename_pattern)
    async_loader.start()
    frame_num = numbers_range[0]
    preload_num = frame_num - 1
    preload_data = None
    try:
        while frame_num < numbers_range[1]:
            if preload_num == frame_num:
                data = preload_data
            else:
                async_loader.task_queue.put(frame_num)
                (check_num, data) = async_loader.result_queue.get()
                #NB: может зависнуть при необработанном исключении в потоке
                if check_num != frame_num:
                    logging.error("iternal error")
                    raise Exception("iternal error")
            if isinstance(data, Exception): raise data
            preload_num = frame_num + step
            if preload_num < numbers_range[1]:
                async_loader.task_queue.put(preload_num)
#                 async_loader.result_queue.put( (-1, None) ) 
#                 - выкл пердзагр для тестов
            frame_num = yield(data)
            if frame_num is None: frame_num = preload_num
            if preload_num < numbers_range[1]:
                (preload_num, preload_data) = async_loader.result_queue.get()
    except GeneratorExit:
        pass
    finally:
        async_loader.task_queue.put(StopFlag())
        async_loader.join()
    
    



