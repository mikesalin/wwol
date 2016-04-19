# -*- coding: utf-8 -*-
"Общие функции для построения графиков через gnuplot"

import math
import os.path
import tempfile
import subprocess
import logging
import sys
import numpy as np

from ..common.my_encoding_tools import fname2quotes, U, local_encoding
from .. wwol_globals import VERBOSE

def draw_conventions():
  """
  (Это пустая функция, просто чтобы написать документацию.)
  Общие конвенции для функций типа draw...():
  
  Возращает основную часть текста скрипта для gnuplot-a .
  Он будет переработан и запущен функцией LaunchGnuPlot
  В конце скрита строчки с комментариями после "#INFO:" -- текст для поля инфо
  
  Функция сохраняет файлы с данными для графиков. Для текущего рисования 
  следует предавать file_prefix=None , тогда эти файлы будут называться и 
  размещаться, как положено для временных файлов в системе. Чтобы сохранить
  файлы скрипта и картинки для дальнейшего использования, будет разумно
  передать осмысленную строку в file_prefix .
  В обоих случаях имена созданных файлов как список строк возвращается через
  created_files , например, для подчистки временных файлов.
  
  dispers_curve (где эта опция доступна) может принимать значения 0, 1 и 2.
  Регулирует отображение дисперсионной зависимости:
  0 - выкл, 1-вкл, 2- с рукавами погрешности.
  """

def file4draw(created_files, file_prefix, file_suffix, mode="b"):
  """
  Возвращает пару (файловый объект, имя).
  Создает, открывает файл и вносит его в список.
  См. общие конвенции: help(draw_conventions)
  """
  if file_prefix is not None:
    fname = file_prefix + file_suffix
    fobj = open(U(fname), "w" + mode)
  else:
    mode_ = mode
    fobj = tempfile.NamedTemporaryFile(suffix=file_suffix, mode="w"+mode_)
    fobj.delete = False
    fname = fobj.name
  created_files.append(fname)
  return (fobj, fname)


def launch_gnu_plot(created_files, script_body, mode, file_prefix=None,
    limits=None, cleanup=True, size=None):
  """
  Дополняет script_body (тип str) header-ом и/или footer-ом и скармливает 
  его gnuplot. 
  mode: "console" -нарисовать график и оставить пользователя в консоле gnuplot
        "console+"-под линуксом открывает новый терминал и дальше как "console"
                   под виндой полностью идентично "console"
        "file" - нарисовать график в файл, молчаливый режим. Имя получившегося
                 файла будет возвращено как последний элемент в списке
                 created_files . Размер рисунка задается параметром size .
        "just_save_script"
  Возращает tuple: (exit_code, None) или (exit_code, output) 
  limits: tuple (xmin, xmax, ymin, ymax, color_min, color_max)
          Чтобы использоваться стандартные значения для какого-то из параметров,
          можно передать на его месте None или же использовать tuple меньшей
          длины.
  Если guplot не найден в системе, то Exception
  Если mode="file", то имя сгенерированного графического файла будет последним
                    в created_files. перенаправленный вывод возвращен в output
  См. общие конвенции: help(draw_conventions)
  
  ПРИМ.: не предусмотрена защита от внедрения 'shell' или чего-то в этом роде
         в текст скрипта.
  """
  s = script_body
  s = "set encoding utf8\n" + s
  #xrange
  s_modified=False
  if (limits is not None):
    letters=["x", "y", "cb"]
    for n in range(0,3):
      if len(limits)>=2*(n+1):
        xmin = limits[2*n]
        xmax = limits[2*n+1]
        if (xmin is not None) and (xmax is not None):
          s = s + "set %srange [%e:%e]\n" % (letters[n], xmin, xmax)
          s_modified=True
  if s_modified:
    s = s+"replot\n"
  #console mode
  ret_tup = None  #return tuple
  if (mode=="console" or mode=="console+"):
    if size is not None:
      s = ("set term %s size %d,%d\n" % ('GNUTERM', size[0], size[1])) + s
    fobj, fname = file4draw(created_files, file_prefix, ".txt", mode="t")
    fobj.close()  # почему-то под виндой работает только так: октр-закр-откр
    fobj = open(fname, "wt")
    fobj.write(local_encoding(s))
    fobj.write(
      "print '  -----===== Welcome to the console of GNUPLOT ! =====-----'\n")
    fobj.write("print \"  Type ' exit ' to exit\"\n")
    fobj.close()
    
    #выводим в консоль скрипт, удаляя лишнии переносы в конце
    if VERBOSE:
        print "  -----===== Script: =====-----"
        n_spaces = 0
        for ln in s.split("\n"):
          if ln.strip() == "":
            n_spaces += 1 
          else:
            if n_spaces > 0:
              print "\n"*(n_spaces-1)
            print ln
            n_spaces = 0
    
    # проверяем fname
    logging.debug('checking file: ' + fname)
    with open(U(fname), 'rt') as f_dbg:
        pass
    logging.debug('ok')
    
    if (mode=="console+") and (sys.platform == 'linux2'):
            TERM_NAMES = ['x-terminal-emulator', 'xgd-terminal']
            for n_name in range(0, len(TERM_NAMES)):
                try:
                    subprocess.call((TERM_NAMES[n_name],
                                     '-e',
                                     'gnuplot ' + fname2quotes(fname) + ' -'))
                    break
                except OSError:
                    if n_name == (len(TERM_NAMES) - 1):
                        err_text = "Can't launch terminal. Tried: "
                        for name in TERM_NAMES:
                            err_text += name + ' '
                        logging.debug(err_text)
                        raise
            ret_tup = (0, None)
    else:
      fname_ = local_encoding(fname)
      rv = subprocess.call(("gnuplot", fname_, "-"))
      ret_tup = (rv,None)
    
    if (cleanup):
      for fname in created_files:
        os.remove(fname)
      created_files[:]=[]
  #file mode
  if (mode=="file"):
    if size is None: size = (600,500)
    fobj, fname = file4draw(created_files, file_prefix, ".png");
    fobj.close()
    head = "set term pngcairo size %d,%d truecolor enhanced\n" % size
    set_output_line = "set output '%s'\n" % fname
      #вообще, первую картинку можно было отправить в /dev/null
    head = head + set_output_line
    s=head + s 
    s=s+ set_output_line + "replot\n"
    #запуск
    PIPE=subprocess.PIPE
    p = subprocess.Popen("gnuplot", stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (out1,out2) = p.communicate(local_encoding(s))
    ret_tup = (p.returncode, out1 + out2)
    if (cleanup):
      for fname in created_files[0:-1]:
        os.remove(fname)
      created_files[:]=created_files[-1:]
  #just_save_script
  if (mode=="just_save_script"):
    fobj, fname = file4draw(created_files, file_prefix, "gnuplot.txt", "t")
    fobj.write(local_encoding(s))
    fobj.close()
    ret_tup = (0, None)
  #common
  if (ret_tup is None):
    raise Exception("Неизвестный режим: mode="+mode)
  if (ret_tup[0]!=0):
    logging.debug( "gnuplot returned %d, ERROR ?!" % ret_tup[0] )
  return ret_tup
  
def get_dispers_kf():
  """
  Производит лямбда-функцию для расчета дисперсионки K(f)
  """
  return lambda f: (2*math.pi*f)**2/9.8

JET_COLORMAP_CMD = "set palette defined ( 0 \"#000090\","\
                                         "1 \"#000fff\","\
                                         "2 \"#0090ff\","\
                                         "3 \"#0fffee\","\
                                         "4 \"#90ff70\","\
                                         "5 \"#ffee00\","\
                                         "6 \"#ff7000\","\
                                         "7 \"#ee0000\","\
                                         "8 \"#7f0000\")\n"

