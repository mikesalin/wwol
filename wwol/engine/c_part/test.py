# -*- coding: utf-8 -*-
"Тестирование си-шного модуля"

import numpy as np
import wx

from transform_frame import transform_frame

def main():
    app = wx.App()
    src_img = wx.EmptyImage(1960, 1080, clear=False)
    #src_img = wx.Image('../../../stuff/gopro42_frame.bmp')
    h, w = (src_img.GetHeight(), src_img.GetWidth())
    buf = src_img.GetDataBuffer()        
    src_array = np.frombuffer(buf, np.uint8).reshape((h, w, 3))
    
    dst_w, dst_h = (1024, 512)
    dst_array = np.zeros((dst_h, dst_w))
    
    rv = transform_frame(dst_array,
                         src_array,
                         -0.123717914826,
                         136.41852265,
                         0.5,
#                         646,       # осн.
#                         308,
#                         1656,
#                         848)
                         716,      # near
                         614,
                         1374,
                         1061)
    
    dst_array_8bit = np.ndarray((dst_h, dst_w, 3), np.uint8)
    m = np.amin(dst_array)
    M = np.amax(dst_array)
    for n in range(0, 3):
        dst_array_8bit[:,:,n] = (dst_array - m) * 255 / max(M-m, 1.0)
    img = wx.ImageFromBuffer(dst_w, dst_h, np.getbuffer(dst_array_8bit))
    img.SaveFile('test_result.bmp', wx.BITMAP_TYPE_BMP)

if __name__ == '__main__':
    main()
