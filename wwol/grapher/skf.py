# -*- coding: utf-8 -*-

import numpy as np
import math
from math import pi
import cmath

from .power_spec import *
from .draw_common import *
from .basic_plots import *

class KFSpec:
  """
  Спектральная плотность мощности в координатах (модуль k, частота f)
  .data -- ndarray, (k,f)
           Первый столбец и строка отвечают k=dk, f=df.
           Предпочтительно order='F'
  .dk, .df -- разрешение  
  """
  def __init__(self):
    self.data=None
    self.df=1
    self.dk=1

def calc_skf(skxy, phi0=-180, phi1=180, high_res=False):
  """
  Расчитывает спектральную протность можности в координатах k,f (KFSpec),
  интегрированную в пределах phi0..phi1 (градусы). Входной тип PowerSpec,
  выходной тип KFSpec.
  Если high_res==True то dk=min(dkx,dky) , что может привести к искажениям
  за счет недостатка исходных данных по другой координате.
  """
  #формирование массива результирующих точек по k для исходных (kx,ky)
  #-1 нет результирующей точки
  Nx, Ny, Nf = skxy.data.shape
  dk_var = (skxy.dkx, skxy.dky)
  kmax_var = (Nx*skxy.dkx, Ny*skxy.dky)
  if (high_res):
    dk = min(dk_var)
    kmax = max(kmax_var)
  else:
    dk = max(dk_var)
    kmax = min(kmax_var)
  Nk = int(kmax/dk)  
  my_map = np.ndarray((Nx,Ny),dtype=int,order='F')
  nx0 = Nx/2
  ny0 = Ny/2
  for ny in range (0, Ny):
    for nx in range (0, Nx):
      my_map[nx,ny] = -1
      kx = skxy.dkx*(nx-nx0)
      ky = skxy.dky*(ny-ny0)
      k=math.sqrt(kx*kx+ky*ky)
      nk = round(k/dk)-1
      if (nk < 0) or (nk >= Nk):
        continue
      phi=cmath.phase(kx+1j*ky)*180/pi
      if (phi<phi0):
        while phi<phi0:
          phi = phi + 360
      else:
        while phi>phi1:
          phi=phi-360
      if (phi<phi0 or phi>phi1):
        continue
      my_map[nx,ny] = nk
  #Формирование спектра с помощью my_map
  coef = skxy.dkx * skxy.dky / dk
  skf_data = np.zeros((Nk,Nf),order='F')
  for ny in range (0, Ny):
    for nx in range (0, Nx):
      nk = my_map[nx, ny]
      if (nk<0):
        continue
      skf_data[nk,:] += skxy.data[nx,ny,:] * coef
  out = KFSpec()
  out.data = skf_data
  out.df = skxy.df
  out.dk = dk
  return out
  
def draw_skf(spec, created_files, file_prefix=None, dispers_curve=0,\
            phi0=-180, phi1=180, high_res=False):
  """
  spec -- тип KFSpec или PowerSpec
  phi0, phi1 и high_res -- имеют смысл только, когда spec -- типа PowerSpec,
                           см. calc_skf
  См. общие конвенции: help(draw_conventions)
  TODO: limits
  """    
  dinam_range=40
  
  if isinstance(spec, PowerSpec):
    skf=calc_skf(spec, phi0, phi1, high_res)
  else:
    skf=spec
  
  # Пишем файл с данными
  data_fobj, data_fname = file4draw(created_files, file_prefix, "Skf.dat")
  data_fobj.close()
  Nk=skf.data.shape[0]
  Nf=skf.data.shape[1]
  output = np.ndarray( (Nf+1,Nk+1), dtype=np.float32 ) #gnuplot любит float32
  output[0,0] = Nk;
  output[1:,1:] = np.transpose( 10.0*np.log10(skf.data + 1e-10) );
  for nk in range(0,Nk):
    output[0,nk+1] = (nk+1)*skf.dk
  for nf in range(0,Nf):
    output[nf+1,0] = (nf+1)*skf.df
  output.tofile(data_fname)
  M = np.amax(output[1:,1:])
  #дисперсинка
  if (dispers_curve>0):
    dispers=np.ndarray((Nf,2), dtype=np.float32) #(k,f)
    dispers[:,1] = output[1:,0]
    dispers[:,0] = np.frompyfunc(get_dispers_kf(),1,1)(dispers[:,1])
    dispers_fobj, dispers_fname = file4draw(created_files, file_prefix,\
                                            "dispers.dat")
    dispers_fobj.close()
    dispers.tofile(dispers_fname)      
  # Сочиняем скрипт
  s = ""
  s = s+"plot '%s' binary with image\n" % data_fname
  s = s+"set cbrange [%0.3f:%0.3f]\n" % (M-dinam_range, M)
  s = s + JET_COLORMAP_CMD
  s = s+"unset key\n"
  s = s+"set xlabel 'wavenumber (rad/m)'\n"
  s = s+"set ylabel 'frequency (Hz)'\n"
  #скрипт для дисперсионки  
  if (dispers_curve>0):    
    dispers_file_desc="'%s' binary format='%%float32%%float32'"% dispers_fname
    if (dispers_curve==1):
      s = s+"set style line 1 lw 2 lc rgb 'white'\n"
      s = s+"replot %s with lines ls 1" % dispers_file_desc      
    if (dispers_curve==2):
      s = s+"set style line 1 lw 1 lc rgb 'white'\n"
      s = s+"replot %s using ($1):($2+%0.3e) with lines ls 1\n"\
            % (dispers_file_desc, skf.df/2)
      s = s+"replot %s using ($1):($2-%0.3e) with lines ls 1\n"\
            % (dispers_file_desc, skf.df/2)      
  else:  
    s = s+"replot\n";
  s += "#INFO\n#df = %0.3f [Hz]\n#dk = %0.3f [rad/m]\n" % (skf.df, skf.dk)
  
  return s
