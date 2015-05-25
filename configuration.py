# -*- coding: utf-8 -*-
"""
Определят класс для парамтеров проекта
"""

import logging
import tempfile
import json
import jsonschema

import loading
import geom
import misc

class ConfigError(Exception):
    "Класс исключений, связанных с неправильным вводом параметров проекта"
    pass

FFMPEG_AUTO_SOURCE = 0
FFMPEG_MANUAL_SOURCE = 1
IMG_SOURCE = 2

class Config:
    """
    Параметры проекта.
    
    Ниже идет список переменных с условным делением на категории.
    Тэг [RT] означает run-time, не для сохранения в файл.
    
    source:
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
    
    geom:
      .proj_coef(geom.ProjectingCoef)  [RT]
    
    view:
      .view_step
      
    """
    def __init__(self):
        # source:
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
        # geom
        self.proj_coef = geom.IDENTICATL_PROJECTING
        # view:
        self.view_step = 1
    
    def need_user_pic_path(self):
        return (not self.source_type == FFMPEG_AUTO_SOURCE) or \
            self.user_pic_path_in_auto_mode
        #NB: True -> флаг 'специальная папка"

    def need_fps(self):
        return not (self.source_type == FFMPEG_AUTO_SOURCE)
    
    def post_config(self):
        """
        Некоторая проверка диапазона значений и определение ран-тайм параметров
        конфига. Проблемы в настройках делятся на два типа -- ошибки, в случае
        которых выдаются исключения, и замечания, которые скорее всего приведут
        к ошибкам позднее, но из-за них сейчас не стоит блокировать работу.
        Возвращает: str -- текст замечаний, каждое с новой строки
                    пустая строка -- все ОК
        Исключения: ConfigError
        """
        warn_txt = ""
        warn_txt += self.post_config_src()
        return warn_txt 
        
    def post_config_src(self):
        "См. doc-string post_config. Здесь идет работа в части source"
        # проверка диапазонов значений
        warn_txt = ""
        
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
                warn_txt += "'Путь к картинкам' должен содержать '%d'.\n"
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
            
        if self.source_type == FFMPEG_AUTO_SOURCE:
            try:
                param = loading.video_probe(self.video_filename)
                self.fps = param.fps
                video_probe_frames_count = \
                    int(param.dur * param.fps) - self.frames_range[0]
            except loading.FrameLoaddingFailed:
                warn_txt += "Не могу открыть файл / определить " \
                            "параметры файла: " + self.video_filename + "\n"
                self.fps = 25.0
                video_probe_frames_count = 0

        if self.frames_range[1] == -1:
            self.frames_count = -1
            if self.source_type == IMG_SOURCE:
                try:
                    self.frames_count = loading.find_last_image(
                        self.pic_path, self.frames_range[0]) \
                        - self.frames_range[0]
                except loading.BadFormatString:
                    pass
            if self.source_type == FFMPEG_AUTO_SOURCE:
                self.frames_count = video_probe_frames_count
            if self.frames_count == 0:
                warn_txt += "Нет кадров.\n"
            if self.frames_count < 0:
                warn_txt += "Не могу определить максимальный номер кадра.\n"
                self.frames_count = 0
        else:
            self.frames_count = self.frames_range[1] - self.frames_range[0]
        #для ffmpeg_loader-а число кадров должно быть кратно длине пачки
        if self.source_type == FFMPEG_AUTO_SOURCE or \
          self.source_type == FFMPEG_MANUAL_SOURCE:
            self.frames_count = int(self.frames_count)
            self.pack_len = int(self.pack_len)
            self.frames_count = (self.frames_count / self.pack_len) \
                                * self.pack_len
        return warn_txt
    
    def valid_frames_range(self):
        """
        Тоже, что и self.frames_range, только в возращаемом tuple второй член
        всегда является действительным номером кадра.
        Вызывать после post_config
        """
        return (self.frames_range[0],
                self.frames_range[0] + self.frames_count)


SCHEMA = {
    "title":"Root object for WWOL project configuration file",
    "type":"object",
    "additionalProperties":False,
    "properties": {
        "comment":{"type":"array"},
        "source": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "source_type":{"type":"integer"},
                "user_pic_path":{"type":"string"},
                "user_pic_path_in_auto_mode":{"type":"boolean"},
                "frames_range":{
                    "type":"array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": {"type":"integer"}
                },
                "fps":{"type":"number"},
                "pack_len":{"type":"integer"},
                "overlap":{"type":"boolean"},
                "user_loader_cmd":{"type":"string"},
                "user_use_shell":{"type":"boolean"},
                "video_filename":{"type":"string"}
            } #end of source[proprties]
        }, #end of source
        "geom": {
            "type":"object",
            "additionalProperties":False,
            "properties":{}
        }, #end of geom
        "view": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "view_step":{"type":"integer"}
            } #end of view[proprties]
        } #end of view
    }
}
#NB: диапазоны большинства числовых значений проверяются в post_config,
#    поэтому из не стали указывать в схеме

def load_config(fname):
    """
    Загружает праметры проекта из файла.
    Формат фала json, файл должен содержать объект вида:
    
        {
          "comment":[ ],
          "source":{
            "key":value,
            .....
          },
          "geom":{ ... },
          "view":{ ... }
        }
        
    Свойства объектов соответствуют одноименным членам класса Config (кроме
    членом Config-а, отмеченных как [RT]). Никакой параметр не является
    обязательным. Лишние параметры не допускаются. Свойство comment может
    содержать список любых элементов, удовлетворяющих формату json.
    
    Более конкретно -- входной файл проверяется на соответствие объявленной
    здесь SСHEMA.
    
    Возвращает:
        tuple(Config, str)
        здесь str - текст замечаний или пустая строка, если их нет.
    Исключения:
        ConfigError
    """
    # Чтение файла и первичное декодирование
    try:
        with open(fname, 'rt') as f:
            data = json.load(f)
    except IOError:
        logging.error('IOError in load_config!')
        raise ConfigError("Не могу открыть файл параметров проекта (0): "
                          + str(fname))
    except ValueError as err:
        logging.error('Json parser failed, details: ' + str(err))
        raise ConfigError("Файл параметров проекта имеет неверный формат (1)")
    data = misc.unicode2str_recursively(data)
    
    # Вторичная проверка входа:
    try:
        jsonschema.validate(data, SCHEMA)
    except jsonschema.ValidationError as err:
        MAX_ERR_TXT_LEN = 200
        err_txt = str(err)
        if len(unicode(err_txt, 'utf-8')) > MAX_ERR_TXT_LEN:
            err_txt = unicode(err_txt, 'utf-8')
            err_txt = err_txt[0:MAX_ERR_TXT_LEN] + u' .....'
            err_txt = err_txt.encode('utf-8')
        logging.error('Jsonschema validator failed, details: ' + err_txt)
        raise ConfigError("Файл параметров проекта имеет неверный формат (2)")
    
    # Записываем в структуру:
    SKIP_SECT = ["comment"]
    config = Config()
    for s in data.iterkeys():
        if s in SKIP_SECT: continue
        if not isinstance(data[s], dict):
            raise ConfigError("Внутренняя ошибка при загрузке параметров (3)")
        config.__dict__.update(data[s])
    
    # Последняя проверка и "причесывание"
    warn_txt = config.post_config()
    return (config, warn_txt)

