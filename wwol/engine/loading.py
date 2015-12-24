# -*- coding: utf-8 -*-
"Модуль описывает классы для закрузки видеокадров."

import logging
import threading
import Queue
import os
from string import Template
import subprocess
import shlex
from collections import namedtuple
from datetime import datetime
import wx

from ..common.my_encoding_tools import fname2quotes, U, double_backslash

__all__ = ["image_loader", "ffmpeg_loader", "find_last_image",
           "LoadingError", "FrameLoaddingFailed", "BadFormatString", "NoData",
           "frame_numbering", "make_ffmpeg_cmd", "VideoProbeResult",
           "video_probe"]
           
def frame_numbering():
    """
    frame_numbering: (пустая функция, чтобы написать следующий doc-string)

    НУМЕРАЦИЯ КАДРОВ В ПРОГРАММЕ
    В главном окне используется так называемая рабочая нумерация -- с нуля,
    за ноль принят первый кадр из выбранного диапазона. Функции типа 
    view.Preview.goto_frame(n) принимают на вход рабочую нумерацию.

    Загрузчики -- метод .send(n) генераторов из модуля loader -- используют
    т.н. физическую нумерацию. Т.е. для image_loader -- этот тот номер, который
    стоит в имени файла. Для frame_numbering 0ой кадр -- это начало файла.
    
    Чтобы перевести рабочую нумерацию в физическую, конструктор класса
    view.Preview (и аналогичных классов) имеет параметр frame_num_ofs.
    """
    pass

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
class NoData(LoadingError):
    "Исключение, когда выходим из генератора, не найдя ни одного кадра"
    pass


class StopFlag:
    "Специальный входной тип для AsyncBmpLoader.task_queue"
    pass


def subs_frame_num(pic_path, frame_num):
    """
    Подставляет номер кадра в printf - строку форматирования. В случае
    возникновения исключения преобразует его в BadFormatString и дублирует
    информацию в лог.
    Аргументы:
      pic_path (string): содержит %d
      frame_num (int)
    Возвращает:
      string
    Исключения:
      BadFormatString
    """
    try:
        res = pic_path % frame_num
    except TypeError:
        logging.debug(U("Can't parse '%s'! "\
                        "Expected smth like 'file%%04d.bmp'." % pic_path))
        raise BadFormatString()
    return res

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
    def __init__(self, pic_path):
        "pic_path -- string, см. help(BmpLoader)"
        threading.Thread.__init__(self)
        self.pic_path = pic_path
        self.task_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
    
    def run(self):
        "Код для испольнения в другом потоке"
        while True:
            frame_num = self.task_queue.get()
            if (isinstance(frame_num, StopFlag)): return
            try:
                filename = subs_frame_num(self.pic_path, frame_num)
            except BadFormatString as e:
                self.result_queue.put( (frame_num, e) )
                continue
            img = wx.Image(filename)
            if not img.IsOk():
                logging.debug(U("Can't load '%s'!" % filename))
                img = FrameLoaddingFailed()
            self.result_queue.put( (frame_num, img) )


def image_loader(pic_path, numbers_range):
    """
    Загружает один-за-одним файлы простого графического формата. Генератор.
    Предварительно загружает следующий кадр во втором потоке
    Аргументы:
      pic_path -- string, имя файла в формате printf, которое содержит
                  %d (или, например, %04d) для подстановки номера.
      numbers_range -- tuple, (первый, последний+1)
    Yields: 
      wx.Image
    Может кидать исключения:
      FrameLoaddingFailed, BadFormatString, NoData, StopIteration
    Как генератор, имеет методы:
      .next() -- возвращает следующий кадр
      .send(n) -- переводит счетчик на кадр n, возвращет n-ый кадр                  
                  (нельзя вызывать send до первого next)
      .close()
    Замечание: Здесь номер кадра -- число, которое стоит в имени файла.
    ( См. help(loading.frame_numbering) )
    """
    async_loader = AsyncImageLoader(pic_path)
    async_loader.start()
    frame_num = numbers_range[0]
    preload_num = frame_num - 1
    preload_data = None
    fresh = True # еще ни разу не делали yeild
    preload_step = 1  # пытаемся угадать, с каким шагом запрашивают кадры
    try:
        while frame_num < numbers_range[1]:
            # есть ли у нас предзагруженный кадр?
            if preload_num == frame_num:
                data = preload_data  # есть -- используем его
            else:
                # нет -- запускаем на загрузку и ждем пока загрузится
                async_loader.task_queue.put(frame_num)
                (check_num, data) = async_loader.result_queue.get()
                if check_num != frame_num:
                    logging.debug("iternal error")
                    raise Exception("iternal error")
            if isinstance(data, Exception): raise data
            # перед выдачаей кадра запускаем предзагрузку следующего
            preload_num = frame_num + preload_step
            do_preload = preload_num >= numbers_range[0] and \
              preload_num < numbers_range[1]
            if do_preload:
                async_loader.task_queue.put(preload_num)
            fresh = False
            # и, наконец, выдем кадр:            
            next_frame_num = yield(data)
            # готовимся к следующей итерации
            if next_frame_num is None:
                next_frame_num = frame_num + 1
            preload_step = next_frame_num - frame_num
            frame_num = next_frame_num
            if do_preload:
                (preload_num, preload_data) = async_loader.result_queue.get()
            
    except GeneratorExit:
        pass
    finally:
        async_loader.task_queue.put(StopFlag())
        async_loader.join()
    if fresh: raise NoData()
    

def find_last_image(fname, start):
    """
    Определяет номера последней картинки в папке.
    Аргументы:
      fname (string):  имя файла с %d вместо номера
      start (int): номер начального кадра
    Возвращает: int: (номер_последней_картинки + 1) или
                     start, если нет ни одного файла
    """
    for step in (100, 10, 1):
        while os.access(subs_frame_num(fname, start + step), os.F_OK):
            start += step
    
    if os.access(fname % start, os.F_OK):
        return start + 1
    else:
        return start

    
def cleanup_files(pic_path, numbers_range):
    """
    Удаляет файлы с заданными номерами (при наличии)
    Аргументы:
      pic_path (string): содержит %d для номера.
      numbers_range (tuple (int, int)): певрый, последний + 1
    """
    warn_count = 0
    for j in range(numbers_range[0], numbers_range[1]):
        fname = subs_frame_num(pic_path, j)
        if os.access(fname, os.F_OK):
            try:
                os.remove(fname)
            except OSError:
                warn_count += 1
    if warn_count > 0:
        logging.debug("Can't cleanup %d file(s)", warn_count)


def make_ffmpeg_cmd_final(loader_cmd, exact_start, prestart):
    """
    Подставляет $START или %PRESTART и $SOFT_START в шаблон команды загрузчика.
    Вспомогательная функция для ffmpeg_loader, см. help(ffmpeg_loader).
    Аргументы:
      loader_cmd(string)
      exact_start(float)
      prestart(float)
    Возвращает:  string
    Исключения:  BadFormatString
    """
    soft_start = exact_start - prestart
    st = Template(loader_cmd)
    try:
        s = st.substitute(PRESTART = "%0.3f" % prestart,
                          SOFT_START = "%0.3f" % soft_start)
    except (KeyError, ValueError):
        try:
            s = st.substitute(START = "%0.3f" % exact_start)
        except (KeyError, ValueError):
            logging.debug(u"Can't substitute START or PRESTART and SOFT_START"
                            " to '%s'!", U(loader_cmd))
            raise BadFormatString()
    return s


def ffmpeg_loader(loader_cmd, pic_path, pack_len, frames_range, fps,
                  use_shell = False,
                  on_start_lap = None, on_finish_lap = None):
    """
    Запускает некоторую программу командой loader_cmd (обычно это ffmpeg,
    чтобы превратить видеофайл в пачку кадров) и загружает картинки,
    получившиеся в результате этого. Удаляет файлы картинок, когда они
    перестают быть нужны.
    Генератор.
    Аргументы:
      loader_cmd (string): шаблон команды, которую нужно выполнить, чтобы
                           получить пачку кадров, содержит поля подстановки:
        $START -- время начала очередного запрашиваемого фрагмента, сек        
        $PRESTART -- грубое значение времени начала.
        $SOFT_START -- добавка: START = PRESTART + SOFT_START .
        Должно присутсвовать: либо $START, либо $PRESTART и $SOFT_START.
      pic_path (string): где забрать кадры после работы команды, содержит %d .
      pack_len (int): число кадров, которое выдается после запуска команды
                      (далее -- дословно длина пачки).
      frames_range (tuple (int, int) ): (первый_кадр, последний_кадр + 1).
                                        Нумерация кадров идет с 0.
                                        ( См. help(loading.frame_numbering) )
     Необязательные аргументы:
      use_shell (True/False): выполнять ли loader_cmd в shell.
      on_start_lap, on_finish_lap (callable или None):
        будет вызываться перед и после окончания очередного выполнения команды.
        (Возможность сообщить о начале длительной операции в гуи.)
    Yields: 
      wx.Image
    Исключения:
      FrameLoaddingFailed, BadFormatString, StopIteration, NoData
    Методы .next, .send и .close работают аналогично img_loader .    
    
    Подробности реализации:
    Для ускорения доступа при листании кадров, до двух пачек кадров хранятся
    в виде картинок на диске. Они разделяются номерами внутри pic_path:
      1..pack_len (только вышли из ffmpeg) -->
      --> pack_len+1..2*pack_len (предыдущий) --> удаление
    Реальные номера начальных кадров -- start1 и start2, -1 - признак отсутствия
    данных. Как только запрашивается кадр, которого еще нет, подгружается целая
    пачка.
    """
    logging.debug("Initializing ffmpeg_loader...")
    start1 = -1 # см. doc-string
    start2 = -1
    img_loader_state = 0 # загрузчик картинок настроен на:
                         # 1 - первую пачку, 2 - вторую, 0 - вообще не настроен
    img_loader_ = None
    frame_num = frames_range[0] # текущий номер кадра
    in_pack = lambda n, start: \
        (start >= 0) and (n >= start) and (n < start + pack_len)
    fresh = True
    
    dummy_callable = lambda: None
    if on_start_lap is None: on_start_lap = dummy_callable
    if on_finish_lap is None: on_finish_lap = dummy_callable
    
    # большой цикл, пока не кончится видео или кто-то не прервет:
    try:
        while True:
            if not (in_pack(frame_num, start1) or in_pack(frame_num, start2)):
                # надо запускать ffmpeg
                try:
                    on_start_lap()
                    # - убиваем загрузчик
                    if img_loader_state != 0:
                        img_loader_.close()
                        img_loader_state = 0
                    
                    # - перекидываем файлы / освобождаем место
                    if start1 >= 0:
                        cleanup_files(pic_path,
                                      (pack_len + 1, 2 * pack_len + 1))
                        for j in range(1, pack_len + 1):
                            os.rename(subs_frame_num(pic_path, j),
                                      subs_frame_num(pic_path, j + pack_len))
                        start2 = start1
                        start1 = -1
                    else:
                        cleanup_files(pic_path, (1, pack_len + 1))
                    
                    # - формируем вызов и проверяем не хватит ли
                    start1 = (int(frame_num - frames_range[0]) \
                              / int(pack_len)) * pack_len + frames_range[0]
                    if (start1 + pack_len) > frames_range[1]:
                        logging.debug("ffmpeg_loader raises StopIteration or "
                            "NoData because start1(%d) + pack_len(%d)"
                            "> frames_range[1](%d), when frame_num=%d",
                             start1, pack_len, frames_range[1], frame_num)
                        if fresh:
                            raise NoData()
                        else:
                            raise StopIteration()
                    exact_start = start1 / (fps * 1.0)
                    SOFT_START_OFFSET = 10
                    prestart = max(exact_start - SOFT_START_OFFSET, 0.0)
                    s = make_ffmpeg_cmd_final(loader_cmd, exact_start, prestart)
                    logging.debug(
                      u"WWOL is going to get frames %d..%d using command: '%s'\n",
                      start1 + 1,
                      start1 + pack_len,
                      U(s))
                                        
                    # - поехали                    
                    if use_shell:
                        subprocess.check_call(s, shell = True)
                    else:
                        unshell = shlex.split(double_backslash(s))
                        if len(unshell) == 0: unshell = [""]
                        subprocess.check_call(unshell, shell = False)
                    on_finish_lap()
                        
                    # - проверяем, появились ли файлы в папке
                    if not (os.access(subs_frame_num(pic_path, 1), os.F_OK) and
                      os.access(subs_frame_num(pic_path, pack_len), os.F_OK)):
                        logging.debug("No files were created!")
                        raise FrameLoaddingFailed()
                except (OSError, subprocess.CalledProcessError) as e:
                    logging.debug(U(str(e)))
                    raise FrameLoaddingFailed()
            
            have_got_img = False
            if not ( (in_pack(frame_num, start1) and (img_loader_state == 1)) \
              or (in_pack(frame_num, start2) and (img_loader_state == 2)) ):
                # запускаем img_loader
                if img_loader_state != 0:
                    img_loader_.close()
                    img_loader_state = 0
                if in_pack(frame_num, start1):
                    img_loader_state_after = 1
                    nums_range = (1, pack_len + 1)
                else:
                    img_loader_state_after = 2
                    nums_range = (pack_len + 1, 2 * pack_len + 1)                
                img_loader_ = image_loader(pic_path, nums_range)
                img_loader_state = img_loader_state_after
                img = img_loader_.next()
                have_got_img = (frame_num == start1) or (frame_num == start2)
            
            # наконец, загружаем кадр:
            if not have_got_img:
                ofs = (-start1 + 1, -start2 + pack_len + 1)\
                    [in_pack(frame_num, start2)]
                try:
                    img = img_loader_.send(frame_num + ofs)
                except StopIteration:
                    logging.debug("slave img_loader_ has risen StopIteration")
                    raise FrameLoaddingFailed()
            fresh = False
            #logging.debug("yeilding frame_num = " + str(frame_num))
            next_frame_num = yield img
            if next_frame_num is None:
                frame_num += 1
            else:
                frame_num = next_frame_num

    except GeneratorExit:
        pass
    finally:
        if img_loader_state != 0:
            img_loader_.close()
            img_loader_state = 0
        cleanup_files(pic_path, (1, 2 * pack_len + 1))
    if fresh: raise NoData()


FFMPEG_CMD_TEMPLATE = "$FFMPEG -ss $PRESTART -i $VIDEO_FILENAME " \
                      "-an -ss $SOFT_START -vframes $PACK_LEN " \
                      "$FPS_OPT_ARG -deinterlace -f image2 $PIC_PATH"
FFMPEG_BIN_PATH = ""
FFMPEG_NAME = "ffmpeg"
FFPROBE_NAME = "ffprobe"


def make_ffmpeg_cmd(video_filename, pack_len, pic_path, force_out_fps):
    """
    Собирает команду для запуска FFMPEG, годную для ffmpeg_loader-а, оставляет
    $START, $PRESTART и $SOFT_START для make_ffmpeg_cmd_final
    Аргументы: ...
    Возвращает: string
    """
    if force_out_fps is None:
        fps_opt_arg = ""
    else:
        fps_opt_arg = "-r %0.3f" % force_out_fps
    if video_filename.find(' ') >= 0: video_filename = '"' + video_filename + '"'
    subs_dict = {"FFMPEG": FFMPEG_BIN_PATH + FFMPEG_NAME,
                 "VIDEO_FILENAME": fname2quotes(video_filename),
                 "PACK_LEN": str(pack_len),
                 "PIC_PATH": fname2quotes(pic_path),
                 "FPS_OPT_ARG": fps_opt_arg}
    return Template(FFMPEG_CMD_TEMPLATE).safe_substitute(**subs_dict)


VideoProbeResult = namedtuple('VideoProbeResult', ['start', 'dur', 'fps'])
    
    
def video_probe(filename):
    """
    Определить параметры видеофайла.
    Аргументы:
      filename (string): просто имя файла
    Возвращает:
      VideoProbeResult -- namedtuple:
         .start (float): сдвиг начала (сек),
         .dur (float): длительность (сек),
         .fps (float)
    Исключения:
      FrameLoaddingFailed
    Метод работы: вызываем ffprobe и разбирает текстовый вывод.
    """
    SEP = ","
    DURATION_KEYWORD = "Duration:"
    START_KEYWORD = "start:"
    FPS_KEYWORD_MAIN = "fps"
    FPS_KEYWORD_1 = "Stream"
    FPS_KEYWORD_2 = "Video:"
    
    cmd = FFMPEG_BIN_PATH + FFPROBE_NAME + " " + fname2quotes(filename)
    try:
#        txt = subprocess.check_output(shlex.split(cmd),
#                                      stderr=subprocess.STDOUT)
        # Python 2.6:
        pp = subprocess.Popen(shlex.split(double_backslash(cmd)),
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        txt, txt_err = pp.communicate()
        txt += txt_err
        if pp.returncode != 0:
            logging.debug(u"FFPROBE returned %d (non-zero), command was:\n%s",
                          pp.returncode, U(cmd))
            raise FrameLoaddingFailed()
    except OSError:
        logging.debug(u"OSError occured while executing: '%s'" % U(cmd))
        logging.debug("Can't launch FFPROBE!")
#    except subprocess.CalledProcessError as e:
#        logging.debug(u"FFPROBE returned %d (non-zero), details are below.\n"
#                      u"Command:\n  %s\nOutput:\n%s",
#                      e.returncode, U(cmd), U(e.output))
#        logging.debug("FFPROBE can't open video file!")
#        raise FrameLoaddingFailed()
    
    logging.debug('Parsing FFPROBE output:\n' + txt)
    lines = txt.split('\n')
    #Duration, start
    dur = -1
    try:
        for s in lines:
            pos = s.find(DURATION_KEYWORD)
            if pos >= 0:
                #s ~ 'Duration: 00:02:43.17, start: 1.040000, bitrate: 24005 kb/s'
                #Duartion
                s = s[(pos + len(DURATION_KEYWORD)):]
                pos = s.find(SEP)
                if pos < 0: raise FrameLoaddingFailed()
                try:
                    dd = datetime.strptime(s[:pos].strip(), '%H:%M:%S.%f')
                except ValueError as e:
                    logging.debug(U(str(e)))
                    raise FrameLoaddingFailed()
                dur = dd.hour * 3600.0 + dd.minute * 60.0 + dd.second \
                      + dd.microsecond * 1e-6
                #Start
                pos = s.find(START_KEYWORD)
                if pos < 0: raise FrameLoaddingFailed()
                s = s[(pos + len(START_KEYWORD)):]
                pos = s.find(SEP)
                if pos < 0: raise FrameLoaddingFailed()
                try:
                    start = float(s[:pos].strip())
                except ValueError as e:
                    logging.debug(U(str(e)))
                    raise FrameLoaddingFailed()
                
                break
        if dur <= 0: raise FrameLoaddingFailed()
    except FrameLoaddingFailed as e:
        logging.debug("Error while parsing FFPROBE output, 'Duration' section")
        raise e
    logging.debug("Got start %0.4f and duartion %0.4f", start, dur)

    # fps:
    fps = -1
    try:
        for s in lines:
            if s.find(FPS_KEYWORD_1) >= 0 and s.find(FPS_KEYWORD_2) >=0:
                #s ~ 'Stream #0:0[0x1011]: Video: h264 (High) <...> , 25 fps, <...>'
                pos2 = s.find(FPS_KEYWORD_MAIN)
                pos1 = s[:pos2].rfind(SEP)
                if pos1 < 0 or pos2 < 0: raise FrameLoaddingFailed()
                try:
                    fps = float(s[pos1 + len(SEP) : pos2].strip())
                except ValueError as e:
                    logging.debug(U(str(e)))
                    raise FrameLoaddingFailed()
                break
        if fps <= 0: raise FrameLoaddingFailed()
    except FrameLoaddingFailed as e:
        logging.error("Error while parsing FFPROBE output, "
                      "'Stream' section, fps value")
        raise e
    logging.debug("Got fps %0.4f", fps)
    
    return VideoProbeResult(start, dur, fps)


# Просто оставлю это здесь
# ffmpeg ... -vcodec pgm(?) -f image2pipe

