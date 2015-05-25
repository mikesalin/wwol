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
    self._config_source_menu_func(None)

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

def test05(self):
    "выбор и отрисовка выделенных точек -- вручную"
    self.sel_data.points_a = [(100, 50), (20, 75)]
    self.sel_data.mode = self.sel_data.SINGLE_POINT_A
    self.test02()
    self._rebind_mouse_events("a")

def test06(self):
    "выбор и отрисовка выделенных точек"
    #self.test02()
    
    self.config.video_filename = VIDEO_FILENAME
    self._config_source_menu_func(None)
    
    self.sel_data.rects_a = [(500, 500, 600, 600)]
    self.start_selecting(self.sel_data.MULTIPLE_RECTS_A, None)
    self.config.proj_coef = (-0.259815, 101.8474, 0.1589)
    self.maintain_sel_trpz()

def test07(self):
    "загрузка конфига"
    (config, warn_text) = \
        configuration.load_config("test_configs/video1.json")
    self.config = config
    self.enter_preview()

def def_all_tests(self):
    "Добавляет функции, определенные в этом модуле, в self"
    self.test_num = 0
    self.test01 = types.MethodType(test01, self)
    self.test02 = types.MethodType(test02, self)
    self.test03 = types.MethodType(test03, self)
    self.test04 = types.MethodType(test04, self)
    self.test05 = types.MethodType(test05, self)
    self.test06 = types.MethodType(test06, self)
    self.test07 = types.MethodType(test07, self)
    self.default_test = self.test07

