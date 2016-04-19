# -*- coding: utf-8 -*-
"Взаимодействие со старой версий программы (swimmer)"

import ConfigParser
from string import Template
import tempfile
import subprocess
import StringIO
import logging
import sys
import os

import wx

from . import configuration
IMG_SOURCE = configuration.IMG_SOURCE
FFMPEG_MANUAL_SOURCE = configuration.FFMPEG_MANUAL_SOURCE
FFMPEG_AUTO_SOURCE = configuration.FFMPEG_AUTO_SOURCE
from . import geom
from ..common.my_encoding_tools import \
    U, fname2quotes, double_backslash, local_encoding
from .loading2 import _error2gui


def _my_legacy_task(config, img_size, fileobj, result_dir):
    """
    Записывает файл парамтеров для старой версии программы
    Аргументы:
      config (Config)
      img_size (tuple (int, int))
      fileobj (file-like): куда записать
      result_dir (str): куда записать в результате спектр
    config.power_spec_check_list должен возвращать True как первый параметр
    """
    mytask= { }
    
    mytask['resizex'] = 1
    mytask['resizey'] = 1
    
    mytask['A'] = config.proj_coef.a
    mytask['B'] = config.proj_coef.b
    mytask['C'] = config.proj_coef.c
    
    aa = config.areas_list[config.active_area_num]
    trpz = geom.trapezoid_inside_rectangle(aa.coord,
                                           config.proj_coef,
                                           img_size)
    mytask['X1'] = trpz[0]
    mytask['Y1'] = trpz[1]
    mytask['X2'] = trpz[4]
    mytask['Y2'] = trpz[5]
    
    mytask['Nx_in'] = aa.input_fft_size[0]
    mytask['Ny_in'] = aa.input_fft_size[1]
    mytask['Nx_out'] = aa.output_fft_size[0]
    mytask['Ny_out'] = aa.output_fft_size[1]
    mytask['Nt'] = config.pack_len
    vfr = config.valid_frames_range()
    mytask['Ntotal'] = vfr[1] - vfr[0]
    mytask['fps'] = config.fps
    mytask['Fmax'] = config.valid_max_freq()
    
    if (config.source_type == IMG_SOURCE):
        mytask['OSL'] = 1
    if (config.source_type == FFMPEG_AUTO_SOURCE):
        mytask['OSL'] = 0
        mytask['FfmpegDef'] = 1
        mytask['FfmpegIn'] = config.video_filename
    if (config.source_type == FFMPEG_MANUAL_SOURCE):
        mytask['FfmpegDef'] = 0
        t = Template(config.user_loader_cmd)
        s = t.safe_substitute(START = '%0.2f', PRESTART = '%0.2f')
        pack_len_str = str(config.pack_len)
        pos = s.find(pack_len_str)
        if pos > 0:
            s = s[0:pos] + '%d' + s[(pos + len(pack_len_str)) :]
        mytask['FfmpegCmd'] = s
    mytask['FrameDir'] = config.pic_path
    mytask['ResultDir'] = result_dir

    if sys.platform == 'win32':
        PROBLEM_KEYS = ['FrameDir', 'ResultDir', 'FfmpegCmd', 'FfmpegIn']
        for key in PROBLEM_KEYS:
            if mytask.has_key(key):
                mytask[key] = double_backslash(mytask[key])
    
    MYTASK_STR = "mytask"
    cp = ConfigParser.ConfigParser()
    cp.add_section(MYTASK_STR)
    for key_str in mytask.keys():
        cp.set(MYTASK_STR, key_str, mytask[key_str])
    cp.write(fileobj)
    
    debug_dump = StringIO.StringIO()
    cp.write(debug_dump)
    logging.debug("Content of mytask:\n%s", debug_dump.getvalue())


if sys.platform == 'win32':
    SWIMMER = 'swimmer_.exe'
else:
    SWIMMER = './swimmer_'


def legacy_spectrum(mvf):
    """
    Вычисление спектра через запуск старой програнны swimmer
    Аргументы:
      mvf (MainVideoFrame)
    В случае ошибки выдается сообщение в диалоговом окне и возращает False
    В случае успеха возращает True и mvf.prev_power_spec_path будет указывать
    на расчитанный спектр
    """
    # спрашиваем место для спектра и настройки
    dlg = wx.DirDialog(mvf,
                       u"Выберите папку для записи спектра",
                       mvf.prev_power_spec_path)
    res = dlg.ShowModal()
    if res != wx.ID_OK:
        dlg.Destroy()
        return False
    result_dir = dlg.GetPath().encode('utf-8')
    dlg.Destroy()
    
    dlg = wx.FileDialog(
        mvf,
        message = u'Cохранить промежуточный файл настроек (mytask)',
        defaultDir = U(os.path.dirname(mvf.project_filename)),
        defaultFile = 'mytask.ini',
        wildcard = '*.ini|*.ini|*.*|*.*',
        style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    res = dlg.ShowModal()
    if res != wx.ID_OK:
        dlg.Destroy()
        return False
    fname = dlg.GetPath().encode('utf-8')
    dlg.Destroy()
    
    # пишем скрипт
    if (mvf.viewer is None) or (mvf.viewer.get_raw_img_size == (0, 0)):
        _error2gui(mvf, "Запустите предпростмотр")
        return False
    img_size = mvf.viewer.get_raw_img_size()
    mvf._close_viewer()
#    fobj = tempfile.NamedTemporaryFile(prefix = 'mytask', mode = 'wt')
#    fname = fobj.name
#    fobj.close()
    with open(U(fname), 'wt') as fobj:
        try:
            _my_legacy_task(mvf.config, img_size, fobj, result_dir)
        except IOError as err:
            _error2gui(mvf, "Ошибка чтения записи:\n" + str(err))
            return False
  
    # запускаем
    if sys.platform == 'win32':
        mvf.Hide()
        wx.Yield()
        try:
            tt1 = (SWIMMER, fname)
            tt2 = (local_encoding(tt[0]), local_encoding(tt[1]))
            swimmer_exit_code = subprocess.call(tt2)
        except OSError:
            mvf.Show()
            _error2gui(mvf, "Не могу запустить " + SWIMMER)
            return False

        mvf.Show()
    else:
        script_fname = os.path.join(os.environ['HOME'], '.run_swimmer.sh')
        with open(U(script_fname), 'wt') as fobj:
            fobj.write(fname2quotes(os.path.abspath(SWIMMER)))
            fobj.write(' ' + fname2quotes(fname) + '\n')
            fobj.write('read -p \" *** Process complete. Press [Enter]. ***\"\n')
            fobj.write('rm ' + fname2quotes(script_fname) + '\n')
            script_fname = fobj.name
            fobj.close()
        os.chmod(script_fname, 0o777)
        
        TERM_NAMES = ['x-terminal-emulator', 'xgd-terminal']
        for n_name in range(0, len(TERM_NAMES)):
            try:
                subprocess.call((TERM_NAMES[n_name],
                                 '-e',
                                 script_fname))
                break
            except OSError:
                if n_name == (len(TERM_NAMES) - 1):
                    err_text = "Can't launch terminal. Tried: "
                    _error2gui(mvf, err_text)
                    return False
        swimmer_exit_code = 0
        #os.remove(script_fname)
        # к сожалению, здесь он не ждет конца работы программы

    if swimmer_exit_code == 0:
        mvf.prev_power_spec_path = result_dir
        return True
    else:
        _error2gui(mvf, "Что-то пошло не так")
        return False
    
