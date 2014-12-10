# -*- coding: utf-8 -*-
"""
Определят класс для парамтеров проекта
"""

class Config:
    "Параметры проекта. См. код __init__"
    def __init__(self):
        self.frames_count = 0
        self.fps = 25
        self.step = 1 # шаг для кнопот назад/вперед
        
