# -*- coding: utf-8 -*-
"""
Определят класс для парамтеров проекта
"""

import logging
import tempfile

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
    .user_pic_path_in_auto_mode (bool)
    .frames_count:  [RT]
    .frames_range:  первый, последний+1;
                    frames_range[1]=-1 -- автоопределение максимума
                    Здесь используется нумерация загрузчика, в обработке 
                    будет использоваться другая нумерация и frames_range[0]
                    примется за 0-ой кадр.
    .fps
    .pack_len
    .overlap
    .user_loader_cmd
    .user_use_shell
    .user_checked_loader_cmd: [RT] поскольку некая исполняемая строчка,
                              считанная из файла, потенциально опасна, то
                              мы не разрешаем ее выполнять, пока ее явно не
                              утвердили, т.е. пока не установили:
                              user_checked_loader_cmd = True
    .video_filename
    Отображение:
    .view_step
    """
    def __init__(self):
        # Источник:
        self.source_type = FFMPEG_AUTO_SOURCE
        self.pic_path = ""
        self.user_pic_path = ""
        self.user_pic_path_in_auto_mode = False
        self.frames_count = 0
        self.frames_range = (0,-1)
        self.fps = 25
        self.pack_len = 128
        self.overlap = True
        self.user_loader_cmd = ""
        self.user_use_shell = False
        self.loader_cmd = ""
        self.user_checked_loader_cmd = False
        self.video_filename = ""
        
        # Отображение:
        self.view_step = 1
    
    def need_user_pic_path(self):
        return (not self.source_type == FFMPEG_AUTO_SOURCE) or \
            self.user_pic_path_in_auto_mode
        #NB: True -> флаг 'специальная папка"

    def need_fps(self):
        return not (self.source_type == FFMPEG_AUTO_SOURCE)
    
    def post_config(self):
        """
        Проверяет диапазон значений. Доопределяет ран-тайм параметры конфига.
        Исключения: ConfigError
        """
        # проверка диапазонов значений
        known_source_types = [FFMPEG_AUTO_SOURCE,
                              FFMPEG_MANUAL_SOURCE,
                              IMG_SOURCE]
        if not self.source_type in known_source_types:
            raise ConfigError("Не поддерживаемый тип загрузчика")
        if not ( (self.frames_range[0] >= 0) and \
                 (self.frames_range[1] == -1 or
                  self.frames_range[1] > self.frames_range[0]) and \
                 (self.fps > 0) and (self.pack_len > 0) ):
            raise ConfigError("Диапазон числовых значений.")
        
        # заполнение run_time - значений:
        if self.need_user_pic_path():
            try:
                dummy = self.user_pic_path % 11
            except TypeError:
                logging.error("Bad pic path: " + self.user_pic_path)
                raise ConfigError("'Путь к картинкам' должен содержать '%d'.")
            self.pic_path = self.user_pic_path
        else:
            #временная папка
            SAMPLE_NUM = "0001"
            IMG_EXT = ".bmp"
            fobj = tempfile.NamedTemporaryFile(suffix = SAMPLE_NUM + IMG_EXT,
                                               mode="wb")
            temp_fname = fobj.name
            fobj.close()
            pos = temp_fname.find(SAMPLE_NUM)
            temp_fname_templ = temp_fname[:pos] + "%d" \
                               + temp_fname[pos + len(SAMPLE_NUM) :]
            self.pic_path = temp_fname_templ
            logging.debug("Temporary picture path is set to: " + temp_fname_templ)
            
        if self.frames_range[1] == -1:
            self.frames_count = -1
            if self.source_type == IMG_SOURCE:
                self.frames_count = loading.find_last_image( \
                  self.pic_path, self.frames_range[0]) - self.frames_range[0]
            if self.source_type == FFMPEG_AUTO_SOURCE:
                try:
                    param = loading.video_probe(self.video_filename)
                except loading.FrameLoaddingFailed:
                    raise ConfigError("Не могу открыть файл / определить "
                        "парамтеры файла: " + self.video_filename)
                self.fps = param.fps
                self.frames_count = int(param.dur * param.fps) \
                                    - self.frames_range[0]
            if self.frames_count < 0:
                raise ConfigError("Не могу определить верхнюю границу "
                                  "диапазона кадров.")
        else:
            self.frames_count = self.frames_range[1] - self.frames_range[0]
        #для ffmpeg_loader-а число кадров должно быть кратно длине пачки
        if self.source_type == FFMPEG_AUTO_SOURCE or \
          self.source_type == FFMPEG_MANUAL_SOURCE:
            self.frames_count = int(self.frames_count)
            self.pack_len = int(self.pack_len)
            self.frames_count = (self.frames_count / self.pack_len) \
                                * self.pack_len
        
    def valid_frames_range(self):
        """
        Тоже, что и self.frames_range, только второй аргумент -- всегда 
        действительный номер кадра. (Работает поле post_config)
        """
        return (self.frames_range[0],
                self.frames_range[0] + self.frames_count)


