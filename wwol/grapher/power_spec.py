# -*- coding: utf-8 -*-
"""
Базовые функции для работы с трехмерной спектральной плотностью мощности:
определение класса, чтение, запись.
"""
import numpy as np
import os.path
import logging

class PowerSpec:
  """
  Трехмерная спектральная плотность мощности в координатах Kx, Ky, f
  .data -- ndarray, 3хмерный массив (kx,ky,f)
           Ноль по kx,ky -- [Nx/2, Ny/2, :], где Nx=data.shape[0] итд
           Первая частота, [:,:,0] отвечает f=df
           Предпочтительно order='F'
  .etalon -- список ndarray, двумерных массивов 
             etalon[:,0]-частота, etalon[:,1]-квадрат амплитуды
  .etalon_tag -- список строк
  .dkx, .dky, .df -- разрешение
  .calibr_details -- None (не делалась калибровка)
                     или [flag, A, Kmin, fmin, gamma]
                                (данные последней калибровки)
  """
  def __init__(self):
    self.data = None
    self.etalon = []
    self.etalon_tag = []
    self.dkx=1
    self.dxy=1
    self.df=1
    self.calibr_details = None
  
  def is_empty(self):
    return self.data is None

STD_CALIBR_FLAG = -3
_DESC2_FNAME = "descr2.txt"
_ETALON_FNAME = "etalon.txt"

def load_text_spec(dir_name):
  """
  Загрузка 3D спектра из (старого) текстового формата
  
  Текстовый формат хранения спектра. Папка содержит:
    Skxy_###.txt
    .....
    [etalon.txt]
    descr2.txt
  SKXY_###.txt: 
     Skxy_100.txt  - 1.00 Гц
     формат файла - текстовая таблица: СПМ 
     S( nx(верт) , ny(гор) ) 
     kx=dkx*(nx-nx0);  ky=dky*(ny-ny0);
     nx0=Nx/2; ny0=Ny/2; - считая от 0
     (после считывания в память - транспонируем)
  ETALON.TXT: формат файла - текстовая таблица: частота, уровень(дБ)
  DESCR2.TXT:
     dkx dkxy df Nf 0|-3 [ A Kmin Fmin gamma ]
  """
  desc2_file = os.path.join(dir_name, _DESC2_FNAME)
  with open(desc2_file, 'rt') as f:
    s = f.readline()
  param = s.split()
  df=float(param[2])
  #Пробуем загрузить первый файл, чтобы узнать размер
  fname = "Skxy_%03d.txt" % int( round(df*100) )
  fname = os.path.join(dir_name,fname)
  Skxy_1st = np.loadtxt(fname)
  Nkx = Skxy_1st.shape[0]
  Nky = Skxy_1st.shape[1]
  Nf = int(param[3])
  logging.debug("Loading spectrum from text files")
  logging.debug("Nkx=%d  Nky=%d  Nf=%d" % (Nkx, Nky, Nf))
  res = PowerSpec()
  res.data = np.ndarray((Nkx,Nky,Nf),order='F');
  res.dkx = float(param[0])
  res.dky = float(param[1])
  res.df=df
  
  calibr_flag = int(param[4])
  if calibr_flag == STD_CALIBR_FLAG:
    res.calibr_details = [calibr_flag] + list(float(s) for s in param[5:])
  
  res.data[:,:,0] = Skxy_1st
  for nf in range(1,Nf):
    # fname = "Skxy_%03d.txt" % int( round( df*(nf+1)*100 ))
    fname = "Skxy_%03.0f.txt" % ( df*(nf+1)*100 )
    fname = os.path.join(dir_name,fname)
    Skxy = np.loadtxt(fname)
    res.data[:,:,nf] = Skxy
  
  try:
    et = np.loadtxt(os.path.join(dir_name, _ETALON_FNAME), unpack=True)
    et = et.T
    et[:,1] = np.power(10.0, et[:,1]*0.1)
    res.etalon = [et]
    res.etalon_tag = ["etalon"]
    logging.debug("etalon: provided")
  except IOError:
    pass
    logging.debug("etalon: not provided")
    
  return res


def save_text_spec(dir_name, spec):
  """
  Запись 3D спектра в текстовый формат (описание формата дано в load_text_spec)
  Аргументы:
    dir_name (str)
    spec (PowerSpec)
  Возвращает: ничего
  (пока) не предусмотрено создание самой директории 
  """
  desc2_file = os.path.join(dir_name, _DESC2_FNAME)
  Nf = spec.data.shape[2]
  if spec.calibr_details is not None:
      extras = " %d %0.3f %0.6f %0.6f %0.6f" % tuple(spec.calibr_details)
  else:
      extras = " 0"
  with open(desc2_file, 'wt') as f:
    f.write("%0.6f %0.6f %0.10f %d %s\n" % \
        (spec.dkx, spec.dky, spec.df, Nf, extras))
  for nf in range(0, Nf):
    fname = "Skxy_%03d.txt" % int( round( spec.df*(nf+1)*100 ))
    fname = os.path.join(dir_name, fname)
    np.savetxt(fname, spec.data[:, :, nf], fmt = '%.6e')
  if len(spec.etalon) > 0:
    np.savetxt(os.path.join(dir_name, _ETALON_FNAME),
               spec.etalon[0],
               fmt = '%.3f')
  
  
