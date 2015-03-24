# -*- coding: utf-8 -*-
"Место для временных решений"

import logging
import wx
import numpy as np

import loading

def main():
    "Усреднение распределения яркости по кадрам"
    logging.basicConfig(format="%(levelname)s: %(module)s: %(message)s",
      level=logging.DEBUG)
    app = wx.App()
    
    #VIDEO_FILENAME = "/mnt/common/VPROC/00009.MTS"
    VIDEO_FILENAME = "/mnt/common/VPROC/GOPR0329.MP4"
    PIC_PATH = "stuff/ffmpeg_out/p%04d.bmp"
    PACK_LEN = 256
    TOTAL_FRAMES = 1536
    RES_PREFIX = "stuff/adhoc/clip2w_"
    
    loader = loading.ffmpeg_loader(loading.make_ffmpeg_cmd(VIDEO_FILENAME,
                                                           PACK_LEN,
                                                           PIC_PATH,
                                                           25.0),
                                   PIC_PATH,
                                   PACK_LEN,
                                   (0, TOTAL_FRAMES),
                                   25.0)
    
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
