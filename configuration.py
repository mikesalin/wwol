# -*- coding: utf-8 -*-
"""
Определят класс для парамтеров проекта
"""

import loading

class ConfigError(Exception):
    """
    Класс исключений, возникающих при формировании объекта Config по данным,
    введенным в окно.
    """
    pass

FFMPEG_AUTO_SOURCE = 0
FFMPEG_MANUAL_SOURCE = 1
IMG_SOURCE = 2

class Config:
    """
    Параметры проекта.
    * [RT] - run-time, не для сохранения в файл
    Источник:
    .source_type:  FFMPEG_AUTO_SOURCE, FFMPEG_MANUAL_SOURCE, IMG_SOURCE
    .pic_path: [RT] Имя файла 1го кадра изображения, %d вместо 
               номера, реалное рабочее значение, равное либо 
               user_pic_path, либо временной папке.              
    .user_pic_path:  значение pic_path, введенное в окошко
    .frames_count:  [RT]
    .frames_range:  первый, последний+1;
                    frames_range[1]=-1 -- автоопределение максимума
                    Здесь используется нумерация загрузчика, в обработке 
                    будет использоваться другая нумерация и frames_range[0]
                    примется за 0-ой кадр.
    .fps
    .pack_len
    .overlap        
    Отображение:
    .view_step
    """
    def __init__(self):
        # Источник:
        self.source_type = FFMPEG_AUTO_SOURCE
        self.pic_path = ""
        self.user_pic_path = ""
        self.frames_count = 0
        self.frames_range = (0,-1)
        self.fps = 25
        self.pack_len = 512
        self.overlap = True
        
        # Отображение:
        self.view_step = 1
    
    def need_user_pic_path(self):
        return not (self.source_type == FFMPEG_AUTO_SOURCE and True)
        #NB: True -> флаг 'специальная папка"

    def need_fps(self):
        return not (self.source_type == FFMPEG_AUTO_SOURCE)
    
    def post_config(self):
        """
        Проверяет диапазон значений. Доопределяет ран-тайм параметры конфига.
        Исключения: ConfigError
        """
        if not ( (self.frames_range[0] >= 0) and \
                 (self.frames_range[1] == -1 or
                  self.frames_range[1] > self.frames_range[0]) and \
                 (self.fps > 0) and (self.pack_len > 0) ):
            raise ConfigError("Диапазон числовых значений.")        
        try:
            dummy = self.user_pic_path % 11
        except TypeError:
            raise ConfigError("'Путь к картинкам' должен содержать '%d'.")
        
        if self.source_type != IMG_SOURCE:
            raise ConfigError("Не поддерживаемый тип загрузчика")
        if self.need_user_pic_path():
            self.pic_path = self.user_pic_path
        else:
            pass #TODO: временная папка 
        if self.frames_range[1] == -1:        
            self.frames_count = loading.find_last_image(self.pic_path,
                                                        self.frames_range[0]) \
                                - self.frames_range[0]
        else:
            self.frames_count = self.frames_range[1] - self.frames_range[0]

