# -*- coding: utf-8 -*-
"Место для временных решений"

import logging
import wx
import numpy as np

from .engine import loading
from . import start

def main():
    "Усреднение распределения яркости по кадрам"
    logging.basicConfig(format="%(levelname)s: %(module)s: %(message)s",
      level=logging.DEBUG)
    start.init_essentials()
    
    VIDEO_FILENAME = "/mnt/common/GOPR0060.MP4"
    TEMP_PIC_PATH = "stuff/ffmpeg_out/p%04d.bmp"
    PACK_LEN = 256
    
    SRC_PIC_PATH = "/mnt/common/gopro_card2/G001%04d.jpg"
    
    START = 117
    FINISH = 300
    RES_PREFIX = "/mnt/common/c01_"
    
#    loader = loading.ffmpeg_loader(loading.make_ffmpeg_cmd(VIDEO_FILENAME,
#                                                           PACK_LEN,
#                                                           TEMP_PIC_PATH,
#                                                           25.0),
#                                   TEMPPIC_PATH,
#                                   PACK_LEN,
#                                   (START, FINISH),
#                                   25.0)
    loader = loading.image_loader(SRC_PIC_PATH, (START, FINISH))
    
    m = 0
    for img in loader:
        m += 1
        if m == 1:
            h, w = (img.GetHeight(), img.GetWidth())
            aver_grey = np.zeros((h, w))
        buf = img.GetDataBuffer()        
        cur_rgb_8bit = np.frombuffer(buf, np.uint8).reshape((h, w, 3))
        for n in range(0, 3):
            aver_grey += cur_rgb_8bit[:,:,n]
        if (m % PACK_LEN) == 1: print "Processed %d frames ..." % m
    
    img.SaveFile(RES_PREFIX + "live.bmp", wx.BITMAP_TYPE_BMP)
    
    aver_grey /= (3 * m)
    aver_grey_rbg_8bit = np.ndarray((h, w, 3), np.uint8)
    for n in range(0, 3):
        aver_grey_rbg_8bit[:,:,n] = aver_grey
    wr_buf = img.GetDataBuffer()
    np.frombuffer(wr_buf, np.uint8)[:] = aver_grey_rbg_8bit.reshape((w * h * 3,))
    img.SaveFile(RES_PREFIX + "aver.bmp", wx.BITMAP_TYPE_BMP)
    
    print "Total %d frames" % m
    loader.close()
    

if __name__ == '__main__':
    main()
