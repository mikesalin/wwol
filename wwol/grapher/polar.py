# -*- coding: utf-8 -*-
"Построение угловых зависимостей спектра"

from math import *
import cmath
from string import Template
import numpy as np

from . import draw_common

def calc_angular_spec(input_spec,
                      nfreq,
                      k_range_is_relative,
                      k_range):
    """
    Вычисление углового спектра на заданной частоте.
    Аргументы:
        input_spec (PowerSpec)
        nfreq (int): номер частоты
        k_range_is_relative (bool) : см. далее
        k_range(tuple (float, float) ) :
          - Если k_range_is_relative==False, то здесь задаются
            границы по K (Kmin, Kmax) внутри которых ведется интегрирование.
          - Если k_range_is_relative==True, то здесь задаются значения границ
            относительно дисперисонного K
    Возвращает:
        np.ndarray
        [:,0] угол (градусы)
        [:,1] спектр (квадрат, м^2/Гц)
    Прим.: дополнително сшлаживает по 3 точкам
    """
    if k_range_is_relative:
        dispers_kf = draw_common.get_dispers_kf()
        freq = input_spec.df * (nfreq + 1)
        dispers_k = dispers_kf(freq)
        kcirc_min = dispers_k * k_range[0]
        kcirc_max = dispers_k * k_range[1]
    else:
        kcirc_min = k_range[0]
        kcirc_max = k_range[1]
    
    dkx = input_spec.dkx
    dky = input_spec.dky
    data = input_spec.data[:,:,nfreq]
    kcirc_min2 = kcirc_min**2
    kcirc_max2 = kcirc_max**2
    nx0=data.shape[0] / 2
    ny0=data.shape[1] / 2
    
    Nphi=round( pi * (kcirc_max+kcirc_min) / max(dkx, dky) )
    a = np.zeros((Nphi,));
    nav = np.zeros((Nphi,));
    for ny in range(0, input_spec.data.shape[1]):
        for nx in range(0, input_spec.data.shape[0]):
            kx = dkx * (nx-nx0)
            ky = dky * (ny-ny0)
            k2 = kx**2 + ky**2
            if (k2 < kcirc_min2) or (k2 > kcirc_max2):
                continue
            
            phi = cmath.phase(kx + 1j * ky)
            if phi < 0: phi = phi + 2 * pi
            nphi= round(phi * Nphi * 0.5 / pi)
            if nphi == Nphi: nphi = 0
            
            a[nphi] += data[nx,ny]
            nav[nphi] += 1
    a = a / nav * dkx * dky
    
    b = np.ndarray((Nphi + 2,))
    b[1:-1] = a[:]
    b[0] = a[-1]
    b[-1] = a[0]
    c = np.correlate(b, np.ones((3,)), mode = 'same')
    a[:] = c[1:-1]
    
    res = np.vstack([np.arange(0, Nphi) * 360. / Nphi, a]).T
    return res
    

def draw_angular_spec(input_spec,
                      freq_list,
                      k_range_is_relative,
                      k_range,
                      polar,
                      dB,
                      norm_to_max,
                      created_files,
                      file_prefix):
    """
    Расчет и построение графика угловой зависимости спектра на неск. частотах.
    Аргументы:
        input_spec (PowerSpec)
        freq_list (list of floats) :   список частот
        k_range_is_relative, k_range:  см. help(cals_angular_spec)
        polar (bool):                  строить полярный график
        dB (bool):                     строить в полярном масштабе
        norm_to_max (bool):            нормировать каждую кривую на ее максимум
        created_files, file_prefix:    см. help(draw_conventions)
    Возвращает:
        см. help(draw_conventions)
    """
    if polar:
        script = _SCRIPT_ANGULAR['polar_head']
    else:
        script = _SCRIPT_ANGULAR['simple_head']
    script_tail = _SCRIPT_ANGULAR['tail']
    for j in range(0, len(freq_list)):
        freq = freq_list[j]
        nfreq = round(freq / input_spec.df) - 1
        nfreq = max(nfreq, 0)
        nfreq = min(nfreq, input_spec.data.shape[2] - 1)
        
        data_fobj, data_fname = draw_common.file4draw(
            created_files,
            file_prefix,
            'angular_%02d_f%03f.dat' % (j, freq * 100))
        data_fobj.close()
        
        data = calc_angular_spec(input_spec, nfreq, k_range_is_relative, k_range)
        if norm_to_max:
            max_val = data[:,1].max()
            if max_val > 1e-20:
                data[:,1] = data[:,1] / max_val
        np.savetxt(data_fname, data)
        
        legend = 'f = %0.3f Hz' % freq
        templ_str = _SCRIPT_ANGULAR[ ['line', 'line_dB'][dB] ]
        script += Template(templ_str).substitute(
            RE = ['', 're'][j > 0],
            FILENAME = data_fname,
            LEGEND = legend)
        script_tail += Template(_SCRIPT_ANGULAR['tail_line']).substitute(
            DPHI =  '%0.1f' % (data[1,0] - data[0,0]),
            LEGEND = legend)
        
    script += script_tail
    return script
    

_SCRIPT_ANGULAR = {
  'polar_head':"""
set polar
set angles degrees
set grid polar
unset xtics
unset ytics
set border 0
set size square  
  """,
  
  'simple_head':"""
set xlabel 'Angle (deg)'
  """,
  
  'line':"""
${RE}plot '$FILENAME' with lines\\
   title '$LEGEND'
  """,
  'line_dB':"""
${RE}plot '$FILENAME' using ($$1):(10*log10($$2 + 1e-10))\\
   with lines\\
   title '$LEGEND'
  """,

  
  'tail':"#INFO:\n",
  'tail_line':"#$LEGEND :  dphi = $DPHI deg\n"
}


def script_to_set_rlimits(rmin, rmax):
    return 'set rrange [%e:%e]\n' % (rmin, rmax)
    
    
