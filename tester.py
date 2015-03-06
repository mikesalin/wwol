# -*- coding: utf-8 -*-
"""
Функции для тестирования.
Ниже (если явно не указано иное) self -- тип main_video_gui
"""

import types

import configuration
import loading
import view

#IMG_PATHNAME = "stuff/data2/IMGP%d.JPG"
IMG_PATHNAME = "stuff/Out/pic%04d.bmp"

def test01(self):
    "Открыть папку с картинками, перейти в режин Preview"
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

def default_test(self):
    "Выбор одного теста из списка (хардкод)"    
    self.test02()

def def_all_tests(self):
    "Добавляет функции, определенные в этом модуле, в self"    
    self.default_test = types.MethodType(default_test, self)
    self.test01 = types.MethodType(test01, self)
    self.test02 = types.MethodType(test02, self)


