# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#
"""
Определят класс для парамтеров проекта
"""

from math import *
import logging
import tempfile
from collections import namedtuple
import json
import jsonschema

from . import loading
from . import geom
from ..common import my_encoding_tools
U = my_encoding_tools.U

class ConfigError(Exception):
    "Класс исключений, связанных с неправильным вводом параметров проекта"
    pass

FFMPEG_AUTO_SOURCE = 0
FFMPEG_MANUAL_SOURCE = 1
IMG_SOURCE = 2

# Добавление нового раздела в конфиг:
# 1. В данном модуле
# 1.1. описать в doc-string Config
# 1.2. добавить в Config.__init__
# 1.3. добавить в SCHEMA
# 1.4. дописать Config._post_config_new_section
# 1.5. доваить в Config.post_config, SUBROUTINES
# 2. Привязка к гуи, модуль main_video_gui:
# 2.1. добавить вкладку
# 2.2. назанчить ей картинку в main_video_gui.__init__ tab_bmps
# 2.3. назаначить ей имя секции в main_video_gui._config_notebook_changed_func
#      SECT_NAMES

class Config:
    """
    Класс, содержащий параметры проекта.
    
    Ниже идет список переменных с условным делением на категории.
    Тэг [RT] означает run-time, не для сохранения в файл.
    
    source:
      .source_set (bool):  [RT], True, если хотя бы раз успешно делали
                           _post_config_src
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
      .angle_per_pixel:  угол в градусах, соответсвующий 1 пикселю около
                         оптической оси (более точно это tan * 180 / pi)
      .camera_height:    (метры)
      .angle_to_vert:    угол оси камеры к вертикали в градусах
      .distortion_k1
      .distortion_k2
    areas:
      .active_area (str): или имя секции из areas_list или 'last'
      .active_area_num [RT]: может принимать значение -1, когда не выбрано
      .areas_list (list of ProcessingArea-s):  может содержать [RT] элементы
      .auto_set_fft_sizes (bool)
    misc_spectral_param:  изменение требует перезапуск обработки
      .max_freq_of_output_spec (float): макс частота для сохранения спектра,
                                    <=0 -- использовать умолчательное значение,
                                    см. также valid_max_freq
      .force_time_wnd_if_no_overlap (bool): Если True, то оконная функция
                      по времени будет применяться всегда. Если False, то
                      действует стандартное поведение: окно включено,
                      когда включено перекрытие.
      .space_wnd (bool): применить окно по координатам x и y
      .equalize_in_space(bool) : выровнять дисперсию яркости внутри кадра,
                                 дисперсию измерять в полосе
                                 equalize_in_space_for_freqs
      .equalize_in_space_for_freqs( sequence (float, float) )
    moving_window:   движущееся окно
      .moving_window_enabled (True/False)
      .moving_window_ref_rect (sequence):  x1, y1, x2, y2 в реальных координатах
      .moving_window_velocity (sequence):  vx, vy         в м/с
      .moving_window_ref_time (float) :    момент времени, когда окно занивает ref_rect
      .moving_window_hold (True / False):  компенсировать движение
          если True, то на обработанном изображении эта область будет неподвижна
          если False, то на обработанном изображении будет виден движущийся
                   ограничивающий прямоугольник
    filters:
      .output_spec_mode(int): выходной спектр получается из сигнала:
                         0 исходного
                         1 обработанного набором фильтров 1
                         2 обработанного набором фильтров 2
    view:       измененяется без перезапуска processing
      .button_step
      .render_mode (str):  'filter1', ....
      .filter1_color_lim (tuple (float, float))
      .auto_color_lim (bool)

      ...
    """
    def __init__(self):
        # source:
        self.source_set = False
        self.source_type = FFMPEG_AUTO_SOURCE
        self.pic_path = ""
        self.user_pic_path = ""
        self.user_pic_path_in_auto_mode = False
        self.frames_count = 0
        self.frames_range = (0,-1)
        self.fps = 25
        self.pack_len = 256
        self.overlap = True
        self.user_loader_cmd = ""
        self.user_use_shell = False
        self.loader_cmd = ""
        self.user_checked_loader_cmd = False
        self.video_filename = ""
        # geom
        self.proj_coef = geom.ProjectingCoef(0, 0, 0)
        self.angle_per_pixel = 0
        self.camera_height = 0
        self.angle_to_vert = 0
        self.distortion_k1 = 0
        self.distortion_k2 = 0
        geom.set_simple_projection(1.0, self)
        # areas
        self.active_area = 'last'
        self.active_area_num = -1
        self.areas_list = []
        self.auto_set_fft_sizes = True
        # misc_spectral_param:
        self.max_freq_of_output_spec = 0
        self.force_time_wnd_if_no_overlap = False
        self.space_wnd = True
        self.equalize_in_space = False
        self.equalize_in_space_for_freqs = [1, 2]
        # filters
        self.output_spec_mode = 0
        # view
        self.button_step = 1
        self.render_mode = 'filter1'
        self.filter1_color_lim = (-1.0, 1.0)
        self.auto_color_lim = True
        # moving_window
        self.moving_window_enabled = False
        self.moving_window_ref_rect = (1., 1., 2., 2.)
        self.moving_window_velocity = (0., 0.)
        self.moving_window_ref_time = 0.
        self.moving_window_hold = False
    
    def need_user_pic_path(self):
        return (not self.source_type == FFMPEG_AUTO_SOURCE) or \
            self.user_pic_path_in_auto_mode

    def need_fps(self):
        return not (self.source_type == FFMPEG_AUTO_SOURCE)
    
    def post_config(self, modified_sections = 'all'):
        """
        Некоторая проверка диапазона значений и определение ран-тайм параметров
        конфига.
        Аргументы:
            modified_sections (list of str or str): сообщить данной функци,
               какие секции конфига изменились, чтобы работать только с ними.
               Если надо обработать весь конфиг, то передается 'all'.
        Возвращает: str -- текст замечаний, каждое с новой строки.
                    Если возвращена пустая строка, то все ОК
        Исключения: ConfigError
        Проблемы в настройках делятся на два типа -- ошибки, в случае которых
        выдаются исключения, и замечания, которые скорее всего приведут
        к ошибкам позднее, но из-за них сейчас не стоит блокировать работу.
        """
        SUBROUTINES = {'source':self._post_config_source,
                       'view':self._post_config_view,
                       'geom':self._post_config_geom,
                       'areas':self._post_config_areas,
                       'misc_spectral_param':self._post_config_misc_spectral_param,
                       'filters':self._post_config_filters,
                       'moving_window':self._post_config_moving_window}

        if isinstance(modified_sections, str):
            modified_sections = [modified_sections]
        warn_txt = ""

        if 'all' in modified_sections:
            for sr in list(SUBROUTINES.values()):
                warn_txt += sr()
        else:
            for ms in modified_sections:
                warn_txt += SUBROUTINES[ms]()
        
        return warn_txt 
        
    def _post_config_source(self):
        "См. post_config. Здесь идет работа в части source"
        # проверка диапазонов значений
        warn_txt = ""
        
        known_source_types = [FFMPEG_AUTO_SOURCE,
                              FFMPEG_MANUAL_SOURCE,
                              IMG_SOURCE]
        if not self.source_type in known_source_types:
            raise ConfigError("Unknown type of loader")
        if not ( (self.frames_range[0] >= 0) and \
                 (self.frames_range[1] == -1 or
                  self.frames_range[1] > self.frames_range[0]) and \
                 (self.fps > 0) and (self.pack_len > 0) ):
            raise ConfigError("Numerical values limits")
        
        # заполнение run_time - значений:
        if self.need_user_pic_path():
            try:
                dummy = self.user_pic_path % 11
            except TypeError as ValueError:
                warn_txt += "'Path to images' should contatin '%d'.\n"
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
            temp_fname_templ = temp_fname[:pos] + "%04d" \
                               + temp_fname[pos + len(SAMPLE_NUM) :]
            self.pic_path = temp_fname_templ
            logging.debug(U("Temporary picture path is set to: " + temp_fname_templ))
            
        if self.source_type == FFMPEG_AUTO_SOURCE:
            any_except = False
            try:
                if len(self.video_filename) == 0: raise _ZeroFileNameLen()
                param = loading.video_probe(self.video_filename)
                self.fps = param.fps
                video_probe_frames_count = \
                    int(param.dur * param.fps) - self.frames_range[0]
            except loading.FrameLoaddingFailed:
                warn_txt += "Can't open video file: " \
                            + self.video_filename + "\n"
                any_except = True
            except _ZeroFileNameLen:
                warn_txt += "No video file is set"
                any_except = True
            if any_except:
                self.fps = 25.0
                video_probe_frames_count = 0

        if self.frames_range[1] == -1:
            self.frames_count = -1
            if self.source_type == FFMPEG_AUTO_SOURCE:
                self.frames_count = video_probe_frames_count
            if self.source_type == FFMPEG_MANUAL_SOURCE:
                raise ConfigError(
                    "In custom mode you should explicitly set the total number "
                    "of frames in the file.")
            if self.source_type == IMG_SOURCE:
                try:
                    self.frames_count = loading.find_last_image(
                        self.pic_path, self.frames_range[0]) \
                        - self.frames_range[0]
                except loading.BadFormatString:
                    pass
                if self.frames_count == 0:
                    warn_txt += "Can't open file: %s \n" % \
                        loading.subs_frame_num(self.pic_path,
                                               self.frames_range[0])
        else:
            self.frames_count = self.frames_range[1] - self.frames_range[0]
        #для ffmpeg_loader-а число кадров должно быть кратно длине пачки
        if self.source_type == FFMPEG_AUTO_SOURCE or \
          self.source_type == FFMPEG_MANUAL_SOURCE:
            self.frames_count = int(self.frames_count)
            self.pack_len = int(self.pack_len)
            self.frames_count = (self.frames_count // self.pack_len) \
                                * self.pack_len
        if self.overlap:
            self.pack_len = (int(self.pack_len) // 2) * 2
        
        self.source_set = True
        return warn_txt

    def _post_config_view(self):
        "См. post_config. Здесь идет работа в части view"
        return ''

    def _post_config_geom(self):
        "См. post_config. Здесь идет работа в части geom"
        geom.set_abc(self)
        return ''
    
    def _post_config_areas(self):
        "См. post_config. Здесь идет работа в части списка областей обработки"
        warn_txt = ''
        # dict -> tuple
        areas_list_in_tuples = []
        for j in range(0, len(self.areas_list)):
            a = self.areas_list[j]
            d = {'name':("area%d" % j),
                 'coord':[64, 64, 128, 128],
                 'input_fft_size':(64,64),
                 'output_fft_size':(64,64)}
            d.update(a)
            areas_list_in_tuples.append(ProcessingArea(**d))
        self.areas_list = areas_list_in_tuples
        
        # проверка имен
        b_warn = False
        RESERVED_NAMES = ['last']
        existing_names = []
        for j in range(0, len(self.areas_list)):
            a = self.areas_list[j]
            a_name = a.name
            if (a_name in existing_names) or (a_name in RESERVED_NAMES):
                b_warn = True
                a_name = _unique_name(existing_names, 'area')
                ad = a._asdict()
                ad['name'] = a_name
                self.areas_list[j] = ProcessingArea(**ad)
            existing_names.append(a_name)
        if b_warn:
            warn_txt += 'Areas names were changed and made unique.\n'
        
        #находим active
        if self.active_area == 'last':
            self.active_area_num = len(self.areas_list) - 1
        else:
            try:
                self.active_area_num = existing_names.index(self.active_area)
            except ValueError:
                self.active_area = 'last'
                self.active_area_num = len(self.areas_list) - 1
                warn_txt += 'Active area is changed. It used to be an nonexistent name\n'
                
        if self.auto_set_fft_sizes:
            for j in range(0, len(self.areas_list)):
                a = self.areas_list[j]
                ad = a._asdict()
                set_default_fft_size_to(ad)
                self.areas_list[j] = ProcessingArea(**ad)
        
        return warn_txt
    
    def _post_config_misc_spectral_param(self):
        "Проверяем секцию конфига 'misc_spectral_param', см. также 'post_config'"
        if self.equalize_in_space_for_freqs[0] >= self.equalize_in_space_for_freqs[1]:
            raise ConfigError('equalize_in_space_for_freqs')
        return ''

    def _post_config_filters(self):
        "Проверяем секцию конфига 'misc_spectral_param', см. также 'post_config'"
        return ''

    def _post_config_moving_window(self):
        "Проверяем секцию конфига 'moving_window', см. также 'post_config'"
        return ''
    
    def valid_frames_range(self):
        """
        Тоже, что и self.frames_range, только в возращаемом tuple второй член
        всегда является действительным номером кадра.
        Вызывать после post_config
        """
        return (self.frames_range[0],
                self.frames_range[0] + self.frames_count)
    
    def _save_to_dict(self):
        """
        Запись всех не-ран-тайм полей в словарь, совместимый по формату
        с файлом проекта (см. load_config).
        Возвращает: dict
        """
        res = {}
        for sect_name in list(SCHEMA["properties"].keys()):
            sect_shema = SCHEMA["properties"][sect_name]
            if sect_shema["type"] != "object": continue
            res[sect_name] = {}
            sect = res[sect_name]
            for key_name in list(sect_shema["properties"].keys()):
                sect[key_name] = self.__dict__[key_name]
        
        res["areas"]["areas_list"] = [a._asdict() for a in self.areas_list]
        
        return res
        
    def add_area_by_coord(self, coord):
        ad = {'name':_unique_name([a.name for a in self.areas_list], 'area'),
              'coord':coord}
        set_default_fft_size_to(ad)
        self.areas_list.append(ProcessingArea(**ad))
        if self.active_area_num < 0:
            self.active_area_num = len(self.areas_list) - 1
    
    def set_area_coord(self, num, coord):
        a = self.areas_list[num]
        ad = a._asdict()
        ad['coord'] = coord
        if self.auto_set_fft_sizes:
            set_default_fft_size_to(ad)
        self.areas_list[num] = ProcessingArea(**ad)
    
    def active_area_num2name(self):
        if (self.active_area_num == -1) \
          or (self.active_area_num == len(self.areas_list) - 1):
            self.active_area = 'last'
        else:
            self.active_area = self.areas_list[self.active_area_num].name
    
    def processing_check_list(self):
        """
        Проверяет все ли готово для обработки.
        Возвращает: (ready_flag, issues_text) : (bool, str)
        """
        ready_flag = True
        issues_text = ""

        if not self.source_set:
            ready_flag = False
            issues_text += "- Configure a video data source\n"

        geom_is_dummy = True
        u = self.proj_coef
        v = geom.IDENTICATL_PROJECTION
        cmp_ = lambda x,y: abs(x - y) < 1e-6
        geom_is_dummy = cmp_(u.a, v.a) and cmp_(u.b, v.b) and cmp_(u.c, v.c)
        if geom_is_dummy:
            issues_text += "- Define the geometry (camera and angle)\n"
        
        if self.active_area_num < 0:
            ready_flag = False
            issues_text += "- Select the area to be processed\n"
        
        return (ready_flag, issues_text)
    
    def valid_max_freq(self):
        if self.max_freq_of_output_spec > 0:
            return self.max_freq_of_output_spec
        else:
            return self.fps * 0.5



def _schema_for_tuple(type_, size):
    "Возвращает json-схему (dict) для массива int-ов строго заданного размера"
    return {"type":"array",
            "minItems": size,
            "maxItems": size,
            "items": {"type":type_} }


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
                "frames_range":_schema_for_tuple("integer", 2),
                "fps":{"type":"number"},
                "pack_len":{"type":"integer"},
                "overlap":{"type":"boolean"},
                "user_loader_cmd":{"type":"string"},
                "user_use_shell":{"type":"boolean"},
                "video_filename":{"type":"string"}
            } #end of source["properties"]
        }, #end of source
        "geom": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "angle_per_pixel":{"type":"number"},
                "camera_height":{"type":"number"},
                "angle_to_vert":{"type":"number"},
                "distortion_k1":{"type":"number"},
                "distortion_k2":{"type":"number"}
            } #end of geom["properties"]
        }, #end of geom
        "areas": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "active_area":{"type":"string"},
                "areas_list":{
                    "type":"array",
                    "items":{
                        "type":"object",
                        "additionalProperties":False,
                        "properties":{
                            "name":{"type":"string"},
                            "coord":_schema_for_tuple("integer", 4),
                            "input_fft_size":_schema_for_tuple("integer", 2),
                            "output_fft_size":_schema_for_tuple("integer", 2)
                        }
                    } #end of areas["properties"]["areas_list"]["items"]
                }, #end of areas["properties"]["areas_list"]
                "auto_set_fft_sizes":{"type":"boolean"}
            } #end of areas["properties"]
        }, #end of areas
        "misc_spectral_param": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "max_freq_of_output_spec":{"type":"number"},
                "force_time_wnd_if_no_overlap":{"type":"boolean"},
                "space_wnd":{"type":"boolean"},
                "equalize_in_space":{"type":"boolean"},
                "equalize_in_space_for_freqs":_schema_for_tuple("number", 2)
            }
        },
        "filters": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "output_spec_mode":{"type":"integer",
                                    "maximum":2,
                                    "minimum":0}
             }
        },
        "view": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "button_step":{"type":"integer"},
                "render_mode":{"type":"string"},
                "filter1_color_lim":_schema_for_tuple("number", 2),
                "auto_color_lim":{"type":"boolean"}
            }
        },
        "moving_window": {
            "type":"object",
            "additionalProperties":False,
            "properties":{
                "moving_window_enabled":{"type":"boolean"},
                "moving_window_ref_rect":_schema_for_tuple("number", 4),
                "moving_window_velocity":_schema_for_tuple("number", 2),
                "moving_window_ref_time":{"type":"number"},
                "moving_window_hold":{"type":"boolean"}
            }
        }
    }
}
#NB: диапазоны большинства числовых значений проверяются в post_config,
#    поэтому их не стали указывать в схеме

def load_config(fname):
    """
    Загружает параметры проекта из файла.
    Формат файла -- см. _load_config_more_options
    Возвращает:
        tuple(Config, str)
        здесь str - текст замечаний или пустая строка, если их нет.
    """
    return _load_config_more_options(fname)

def _load_config_more_options(text,
                             fname_is_given = True,
                             update_existing_config = None,
                             one_section = False):
    """
    Загружает параметры проекта.
    Здесь дано больше опций по сравнению с load_config(fname) .
    Аргументы:
        text (string) : имя файла (если fname_is_given==True)
                        или текст в формате json (если fname_is_given==False).
        fname_is_given (bool) : см. выше
        update_existing_config (Config / None) : параметры, данные в text будут
            дополнять (изменять на месте) конфиг, переданный аргументом 
            update_existing_config (если он не None).
            Переданный класс изменяется на месте и он же возвращается.
            Стандартное поведение: update_existing_config==None и
            для незаполненных параметров берутся стандартные значения.
        one_section (bool) : если True, то: а) выдает ошибку, если в text
                             более одной или ни одной секции и
                             б) выполяет post_config только для это секции
    Возвращает:
        tuple(Config, str)
        здесь str - текст замечаний или пустая строка, если их нет.
    Исключения:
        ConfigError
    
    Формат входного файл Json, файл имеет вид:
    {
      "comment":[ ],
      "source":{
       "source_type":2,
       "user_pic_path":"stuff/Out/pic%04d.bmp",
       "frames_range":[0, -1],
      ......
      }
    ......
    }
    И так далее заполняем свойствами, одноименными членам класса Config,
    с разделением на категории. Пропускаем члены Config-а, отмеченные как [RT].
    
    Никакой параметр не является обязательным. Лишние параметры не допускаются.
    Специальное поле comment может  содержать список любых элементов,
    удовлетворяющих формату json.
    
    Более конкретно -- входной файл проверяется на соответствие объявленной
    здесь SСHEMA.
    """
    # Чтение файла и первичное декодирование
    try:
        if fname_is_given:
            fname = text
            with open(U(fname), 'rt') as f:
                data = json.load(f)
        else:
            data = json.loads(text)
    except IOError:
        logging.debug('IOError in load_config!')
        raise ConfigError("Не могу открыть файл проекта: " + str(fname))
    except ValueError as err:
        logging.debug(U('Json parser failed. SEE DETAILS:\n' + str(err) +
                      '\nSEE FAILED JSON CODE:\n' + repr(text)))
        raise ConfigError("Project has to be coded in the JSON format. Details: " + str(err))
    data = my_encoding_tools.unicode2str_recursively(data)
    
    # Вторичная проверка входа:
    try:
        jsonschema.validate(data, SCHEMA)
    except jsonschema.ValidationError as err:
        err_txt, dummy = my_encoding_tools.limit_text_len(
            str(err), max_len = 150, allow_multiline = True)
        logging.debug('Jsonschema validator failed. SEE DETAILS:\n' + str(err)
                      + '\nSEE FAILED JSON CODE:\n' + text)
        raise ConfigError("Invalid structure of the project. Details: "
                          + err_txt)
    if one_section and (len(list(data.keys())) != 1):
        logging.error('allow_only_one_section check failed')
        raise ConfigError("You are using our editor in a wrong way!")
    
    # Записываем в структуру:
    if update_existing_config is None:
        config = Config()
    else:
        config = update_existing_config
    SKIP_SECT = ["comment"]
    for s in list(data.keys()):
        if s in SKIP_SECT: continue
        if not isinstance(data[s], dict):
            raise ConfigError("Internal error while loading project")
        config.__dict__.update(data[s])
    
    # Последняя проверка и "причесывание":
    if one_section:
        post_config_arg = list(data.keys())[0]
    else:
        post_config_arg = 'all'
    warn_txt = config.post_config(post_config_arg)
    return (config, warn_txt)

    
class _ZeroFileNameLen(Exception):
    pass


ProcessingArea = namedtuple('ProcessingArea',  ['name',
                                                'coord',
                                                'input_fft_size',
                                                'output_fft_size'])
#    Параметры области обработки
#    .name               (string)
#    .coord              ( tuple (x1,y1,x2,y2) )
#    .input_fft_size     ( tuple (Nx,Ny) )   [RT], если auto_set_fft_sizes==True
#    .output_fft_size    ( tuple (Nx,Ny) )   [RT], если  --"--"--


def _unique_name(existing_names, prefix):
    """
    'Придумывает' уникальное имя, не совпадающее ни с одним из existing_names
    и начинающееся с prefix
    Аргументы:
      existing_names (list of str)
      prefix (str)
    Возвращает:
      str
    """
    n = 1
    s = ''
    while True:
        s = prefix + str(n)
        if not (s in existing_names):
            break
        n += 1
    return s
    
    
def _round_log2(x):
    if abs(x) <= 1:
        return 4
    else:
        return 2**int(round( log(abs(x) * 1.0) / log(2.0) ))

    
def set_default_fft_size_to(d):
    """
    Устанавливает умолчательный размер Фурье для ProcessingArea
    Аргументы:
        d(dict): ключи соответвуют свойствам ProcessingArea,
                 входной и выходной аргумент
    Возвращает: ничего
    """
    coord = d['coord']
    nx = _round_log2(coord[2] - coord[0])
    ny = _round_log2(coord[3] - coord[1])
    d['input_fft_size'] = (nx // 2, ny // 2)
    d['output_fft_size'] = (nx // 4, ny // 4)
    
