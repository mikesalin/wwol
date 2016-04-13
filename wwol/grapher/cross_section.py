# -*- coding: utf-8 -*-
"Построение сечений двумерных графиков"

from string import Template
import numpy as np

from . import draw_common


class LastPlotted2D:
    """
    Данные, которые использовались для построения последнего двумерного графика.
    Нужен для построения сечений.
    .valid(bool)
    .data(np.ndarray): двумерный массив, в том виде, который нужен gnuplot для
                       plot image binary with image
                       Первая строка и столбец -- это шапка, они содержат
                       координаты по осям
    .x_label(str)
    .y_label(str)
    .x_short_name(str)
    .y_short_name(str)
    """
    def __init__(self):
        self.valid = False
        self.data = np.ndarray((1,1), dtype=np.float32)
        self.x_label = ''
        self.y_label = ''
        self.x_short_name = ''
        self.y_short_name = ''
    def reset(self):
        self.valid = False
        self.data = np.ndarray((1,1), dtype=np.float32)


def draw_section_along_x_or_y(last_plotted_2d,
                              direction,
                              values_of_const_variable,
                              created_files,
                              file_prefix=None):
    """
    Строит горизонтальное или вертикальное сечение двумерного графика,
    который был построен неосредственно перед этим.
    Использует глобальный объект draw_common.last_plotted_2d()
    Аргументы:
        last_plotted_2d (LastPlotted2D)
        direction (str): 'x' или 'y' -- вдоль какой координаты сечение
        values_of_const_variable (list of floats / float):
                         значение(ия) второй переменной.
        created_files : см. help(draw_conventions)
        file_prefix
    Пишет файл, возвращает скрипт... все как help(draw_conventions)
    Если не было предыдущего графика, то возвращает пустую строку
    """
    if not last_plotted_2d.valid:
        return ''
    along_x = (direction == 'x')
    if (not along_x) and (direction != 'y'):
        raise Exception('Invalid value of direction arg')
    vals = values_of_const_variable
    if isinstance(vals, float):
        vals = [vals]
    lines_count = len(vals)
    
    if along_x:
        coords_along = last_plotted_2d.data[0, 1:]
        coords_across = last_plotted_2d.data[1:, 0]
        footer = last_plotted_2d.x_label
        legend_name = last_plotted_2d.y_short_name
    else:
        coords_along = last_plotted_2d.data[1:, 0]
        coords_across = last_plotted_2d.data[0, 1:]
        footer = last_plotted_2d.y_label
        legend_name = last_plotted_2d.x_short_name

    output = np.ndarray((coords_along.size, lines_count + 1))
    output[:, 0] = coords_along
    for j in range(0, lines_count):
        pos = np.argmin(np.abs(coords_across - vals[j]))
        if along_x:
            output[:, j + 1] = last_plotted_2d.data[pos + 1, 1:]
        else:
            output[:, j + 1] = last_plotted_2d.data[1:, pos + 1]
        
    # пишем файл
    data_fobj, data_fname = draw_common.file4draw(
        created_files, file_prefix, 'sect.dat')
    data_fobj.close()
    np.savetxt(data_fname, output)
    
    #делаем скрипт
    s = ""
    subs_dict = {
      'FILENAME':data_fname,
      'X_LABEL':footer,
      'LEGEND_NAME':legend_name
    }
    s += Template(_SCRIPT_SECTION['head']).substitute(**subs_dict)
    for j in range(0, lines_count):
        subs_dict['COL'] = j + 2
        subs_dict['LEGEND_VALUE'] = vals[j]
        subs_dict['RE'] = ['re', ''][j == 0]
        s += Template(_SCRIPT_SECTION['line']).substitute(**subs_dict)
    s += Template(_SCRIPT_SECTION['tail']).substitute(**subs_dict)
    
    return s


_SCRIPT_SECTION = {
  'head':"""
fname = '$FILENAME'
set xlabel '$X_LABEL'
set ylabel 'Level (dB)'
  """,
  
  'line':"""
${RE}plot fname using 1:$COL \\
   with lines\\
   title '$LEGEND_NAME=$LEGEND_VALUE'
  """,
  
  'tail':""
}
