# -*- coding: utf-8 -*-
"""
Функции для тестирования.
Ниже (если явно не указано иное) self -- тип main_video_gui
Новые тестовые функции нужно прописывать в def_all_tests .
То, что непосредственно будет выполняться по F5, указывается в default_test.
"""

import types

import configuration
import loading
import view

#IMG_PATHNAME = "stuff/data2/IMGP%d.JPG"
IMG_PATHNAME = "stuff/Out/pic%04d.bmp"
#VIDEO_FILENAME = "/mnt/common/VPROC/GOPR0330.MP4"
VIDEO_FILENAME = "/mnt/common/VPROC/00009.MTS"
PIC_PATH = "stuff/ffmpeg_out/p%04d.bmp"

def test01(self):
    "Открыть папку с картинками, перейти в режин Preview (все \"ручками\")"
    if self.viewer is not None: return
    self.config.frames_count = 200
    ofs = 0
    loader = loading.image_loader(IMG_PATHNAME,
                                 (ofs, self.config.frames_count+ofs))
    self.viewer = view.Preview(self, loader, ofs)
    self.my_toolbar.Enabled = True

def test02(self):
    "Открыть окно источник с забитыми параметрами для папки картинок"
    self.config.source_type = configuration.IMG_SOURCE
    self.config.user_pic_path = IMG_PATHNAME
    self.config_source_menu_func(None)

def test03(self):
    "Запустить fmpeg_loader, перейти в режин Preview (все \"ручками\")"
    cmd = "ffmpeg -ss $START -i " + VIDEO_FILENAME + " -an -ss $SOFT_START "\
          "-vframes 64 -r 25.0 -deinterlace -f image2 " + PIC_PATH
    FRAMES_COUNT = 64 * 3
    loader = loading.ffmpeg_loader(cmd, PIC_PATH, 64, (0, FRAMES_COUNT), 25.0)

    self.config.frames_count = FRAMES_COUNT
    self.config.view_step = 2
    self.viewer = view.Preview(self, loader, 0)
    self.my_toolbar.Enabled = True

def test04(self):
    "video_probe"
    loading.video_probe(VIDEO_FILENAME)

def default_test(self):
    "Выбор одного теста из списка (хардкод)"
    self.test04()
    
def def_all_tests(self):
    "Добавляет функции, определенные в этом модуле, в self"
    self.test_num = 0
    self.default_test = types.MethodType(default_test, self)
    self.test01 = types.MethodType(test01, self)
    self.test02 = types.MethodType(test02, self)
    self.test03 = types.MethodType(test03, self)
    self.test04 = types.MethodType(test04, self)

