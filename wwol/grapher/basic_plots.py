# -*- coding: utf-8 -*-

from .draw_common import *
from .power_spec import *
import math

def draw_skxy(power_spec, created_files, file_prefix=None,
    freq=None, nfreq=None, dispers_curve=0, last_plotted_2d = None):
  """
  Рисование сечения спектра в координатах (kx,ky).
  Частота задается или в Гц (freq) или по номеру (nfreq)
  Возращает текст скрипта. См. общие конвенции: help(draw_conventions)
  """ 
  dinam_range=40  
  # Определяем частоту
  if (nfreq is None) and (freq is None):
    raise Exception("Частота должна быть как-то определена: freq | nfreq")
  if nfreq is None:
    nfreq = round(freq/power_spec.df)-1    
  if (nfreq<0) or (nfreq>=power_spec.data.shape[2]):
    if nfreq is None:
      raise Exception("Частота freq=%0.3f недоступна" % freq)
    else:
      raise Exception("Частота № nfreq=%d недоступна" % nfreq)
  if freq is None:
    freq = power_spec.df*(nfreq+1)
  
  # Пишем файл с данными
  data_fobj, data_fname = file4draw(created_files, file_prefix, "Skxy.dat")
  data_fobj.close()
  Nx=power_spec.data.shape[0]
  Ny=power_spec.data.shape[1]
  output = np.ndarray( (Nx+1,Ny+1), dtype=np.float32 ) #gnuplot любит float32
  output[1:,1:] = 10.0*np.log10(power_spec.data[:,:,nfreq] + 1e-10);
  for nx in range(0,Nx):
    output[nx+1,0] = (nx-Nx/2)*power_spec.dkx
  for ny in range(0,Ny):
    output[0,ny+1] = (ny-Ny/2)*power_spec.dky
  output = output.T
  output[0,0] = Nx
  output.tofile(data_fname)
  M = np.amax(output[1:,1:])
  
  #единичный круг, чтобы рисовать дисперсионку
  phi=np.linspace(0, 2*np.pi, 361).astype('float32')
  phi_fobj, phi_fname = file4draw(created_files, file_prefix, "_phi.dat")
  phi_fobj.close()
  phi.tofile(phi_fname)
  dispers_kf = get_dispers_kf()
  
  # Сочиняем скрипт
  s = ""
  s = s+"plot '%s' binary with image\n" % data_fname
  s = s+"set cbrange [%0.3f:%0.3f]\n" % (M-dinam_range, M) 
  s = s + JET_COLORMAP_CMD
  s = s+"unset key\n"
  s = s+"set size ratio -1\n"
  #дисперсионные круги
  if (dispers_curve>0):
    Kd_list=[]
    if (dispers_curve==1):
      Kd_list=[ dispers_kf(freq) ]
    if (dispers_curve==2):
      Kd_list=[ dispers_kf(freq - power_spec.df*0.5),\
        dispers_kf(freq + power_spec.df*0.5) ]
    n=0
    for Kd in Kd_list:
      var_name = "Kd%d" % n
      n=n+1
      s = s+"%s=%e\n" % (var_name, Kd)
      s = s+"replot '%s' binary format='%%float32' using " % phi_fname
      s = s+"(%s*cos($1)):(%s*sin($1)) with lines ls 1\n" % (var_name,var_name)
    s = s+"set style line 1 lw 2 lc rgb 'white'\n"
  x_label = 'Kx (rad/m)'
  y_label = 'Ky (rad/m)'
  s = s + "set xlabel '%s'\nset ylabel '%s'\n" % (x_label, y_label)
  s = s + "replot\n"
  #info
  s += "#INFO:\n#dkx = %0.3f [rad/m]\n#dky = %0.3f [rad/m]\n" % \
       (power_spec.dkx, power_spec.dky)

  if last_plotted_2d is not None:
      last_plotted_2d.valid = True
      last_plotted_2d.data = output
      last_plotted_2d.x_label = x_label
      last_plotted_2d.y_label = y_label
      last_plotted_2d.x_short_name = 'Kx'
      last_plotted_2d.y_short_name = 'Ky'

  return s


def calc_sf(power_spec):
  """
  Расчитать частотный спектр по трехмерному.
  Возвращает двумерный массив, [:,0]-частота, [:,1]-квадрат амплитуды
  """
  Nf = power_spec.data.shape[2]
  sf = np.zeros((Nf,2))
  sf[:,1] = np.sum(np.sum(power_spec.data, 0), 0) * power_spec.dkx * power_spec.dky
  sf[:,0] = (np.arange(Nf)+1) * power_spec.df
  return sf


def draw_sf(power_spec, created_files, file_prefix=None, cut_etalon=True):
  sf=calc_sf(power_spec)
  funcs = [sf] + power_spec.etalon
  titles = ["processed video spectrum"] + power_spec.etalon_tag
  s=""
  s = s + "set xlabel 'frequency (Hz)'\nset ylabel 'level (dB)'\n"
  for n in range(0, len(funcs)):
    data_fobj, data_fname = file4draw(created_files, file_prefix, "sf%d.dat"%n)
    data_fobj.close()
    data = np.copy(funcs[n])
    data[:,1] = 10.0*np.log10(abs(data[:,1]) + 1e-8)
    if (cut_etalon and n>0):
      data=data[data[:,0]<=sf[-1,0] , :]
    np.savetxt(data_fname, data)
    if (n>0):
      s=s+"re"
    s=s+"plot '%s' with lines title '%s'\n" % (data_fname, titles[n])
  s += "#INFO:\n#df = %0.3f [Hz]\n" % power_spec.df
  return s

def calc_swh(spec, from_freq=0):
  """
  Расчет существенной высоты волн (4*std) выше частоты freq
  Аргументы:
    spec - PowerSpec или ndarray (как выходные данные calc_sf)
    from_freq - float
  Возвращает:
    Если spec - PowerSpec, то список float, 0ой элемент для data,
    1ый и последующее для etalon
    Если spec - ndarray (типа calc_sf) один float
  """
  if isinstance(spec, np.ndarray):
      sf = spec      
      df = np.ndarray( (sf.shape[0],) )
      df[0] = 0
      df[1:] = sf[1:, 0] - sf[0:-1, 0]      
      n = np.argmax(sf[:,0] >= from_freq)
      return 4 * math.sqrt( np.sum( sf[n:, 1] * df[n:] )  )
  res = calc_swh( calc_sf(spec), from_freq )  
  res = [res]  
  for et in spec.etalon:
      res.append( calc_swh(et, from_freq) )
  return res
  
  
