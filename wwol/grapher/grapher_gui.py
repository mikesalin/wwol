# -*- coding: utf-8 -*-
import logging
import os
import wx

from . import grapher_fb
from . import power_spec
from . import draw_common
from . import basic_plots
from . import skf
from . import calibr
from ..common import embed_gui_images

class GrapherMain(grapher_fb.GrapherMainFB):
    """
    Главное окно
    .my_spec - хранящийся спектр, PowerSpec
    .cur_draw_func(created_files, mode, size) - функциональный
               объект, реализующий вызов launch_gnu_plot с нужными параметрами
               для отрисовки текущего графика.
               Для описания параметров -- см. launch_gnu_plot
               Создается в plot_button_func_act на основании значений из гуи.
               None, если отрисовка не готова.
    .cleanup_files
    .warn_gnuplot_code
    .common_info
    .graph_info
    .gnuplot_save_default_dir
    .proj_name
    .view_ctrl - хранит значения полей на вкладке вид при переключении между
                 графиками. List of tuples (xlim_check, xmin, xmax,
                                            ylim_check, ymin, ymax,
                                            clim_check, cmin, cmax)
                 Каждый тапл в списке -- для своего типа графика.
                 Если длина списка меньше нужной или какой-то элемент None,
                 то следует исползовать стандратные значения
    .last_swh_freq_str
    .transf_result_frame
    .AFTER_RESIZE_TIMER_INTERVAL
    """
    #constructor
    def __init__(self, parent):        
        grapher_fb.GrapherMainFB.__init__(self,parent) #initialize parent class
        self.enable_controls(False)
        #Переменные:
        self.my_spec = power_spec.PowerSpec()
        self.cur_draw_func = None
        self.cleanup_files = []
        self.warn_gnuplot_code = True
        self.common_info = ""
        self.graph_info = ""
        self.gnuplot_save_default_dir = ""
        self.proj_name = "test"
        self.view_ctrl = []
        self.last_swh_freq_str = "0"
        self.transf_result_frame = None
        self.AFTER_RESIZE_TIMER_INTERVAL = 500
        #Допиливаем интрефейс:
        self.extra_menu_button.SetBitmap(embed_gui_images.get_menu3Bitmap())
        self.angle_tip_bitmap.SetBitmap(embed_gui_images.get_phi_hintBitmap())
        self.do_filtering_button.Enabled = False
    
    def clone_window(self, new_spec = None, new_proj_name = None):
        """
        Создает копию окна с новым спектром.
        Аргументы:
          new_spec - PowerSpec или None.
                     При None используется стандартное занчение sefl.my_spec.
          proj_name - str или None.
                      При None используется некоторое стандартное занчение
        Возвращает:
          объект окна, тип GrapherMain
        """
        fr = GrapherMain(None)
        if new_spec is None:
            new_spec = self.my_spec
        cur_freq = (self.freq_choice.GetSelection() + 1) * self.my_spec.df
        fr.set_spec(new_spec, cur_freq)
        
        fr.gnuplot_save_default_dir = self.gnuplot_save_default_dir
        if new_proj_name is None:
          fr.proj_name = "transformed " + self.proj_name
        else:
          fr.proj_name = new_proj_name
        fr.SetTitle(fr.proj_name + " - " + str( fr.GetTitle() ))
        self.grtype_choice_func1(None) # обновили self.view_ctrl ...
        fr.view_ctrl = self.view_ctrl        
        fr.last_swh_freq_str = self.last_swh_freq_str
                
        fr.grtype_choice.SetSelection(self.grtype_choice.GetSelection())
        fr.grtype_choice_func2(None) # ... применили fr.view_ctrl
        fr.gnuplot_header_text.SetValue( self.gnuplot_header_text.GetValue() )
        fr.gnuplot_footer_text.SetValue( self.gnuplot_footer_text.GetValue() )
        fr.angle1_text.SetValue( self.angle1_text.GetValue() )
        fr.angle2_text.SetValue( self.angle2_text.GetValue() )
        fr.section_choice.SetSelection(self.section_choice.GetSelection())
        
        fr.enable_controls()
        fr.Show()
        fr.Layout()
        wx.Yield()
        pos = self.GetPositionTuple()
        fr.MoveXY(pos[0]+50, pos[1]+50)
        fr.plot_button_func_act()
        
        return fr            
    
    def set_spec(self, new_spec, default_freq = 1.0):
        """
        Минимальный набор функций, чтобы изменить спектр, хранящийся в окне
        Аргументы:
          new_spec - PowerSpec
          default_freq - float, частоты которую включить во freq_choice
        Возвращает: ничего
        """
        self.my_spec = new_spec
        self.fill_freq_choice()
        sel = int(round(default_freq/self.my_spec.df - 1))
        sel = max(sel, 0)
        sel = min(sel, self.my_spec.data.shape[2]-1)
        self.freq_choice.SetSelection(sel)
        
        #параметры калибровки
        self.fill_etalon_list()
        cal_det = self.my_spec.calibr_details
        if (cal_det is not None) and (cal_det[0] == power_spec.STD_CALIBR_FLAG):
            en = False
            self.transf_a_text.SetValue("%0.1f" % cal_det[1])
            self.transf_kmin_text.SetValue("%0.3f" % cal_det[2])
            self.transf_fmin_text.SetValue("%0.3f" % cal_det[3])
            self.transf_gamma_text.SetValue("%0.3f" % cal_det[4])
        else:
            en = True
            self.transf_kmin_text.SetValue("%0.3f" % \
                (self.my_spec.dkx + self.my_spec.dky))
            self.transf_a_text.SetValue("0")
            self.transf_fmin_text.SetValue("0")
            self.transf_gamma_text.SetValue("0.25")
        self.do_filtering_button.Enabled = en
        self.transf_a_text.Enabled = en
        self.transf_kmin_text.Enabled = en
        self.transf_fmin_text.Enabled = en
        self.transf_gamma_text.Enabled = en

    def enable_controls(self, val=True):
        """
        Включает/выключает элементы, которые не должны работать пока нет спектра
        val = True/False
        """
        self.save_button.Enabled = val
        self.plot_button.Enabled = val
        self.clone_button.Enabled = val
        self.find_freq_text.Enabled = val
        self.gnuplot_save_button.Enable(val)
        self.gnuplot_session_button.Enabled = val
        self.swh_menu.Enable(val)
        self.screenshot_menu.Enable(val)
        
    def fill_freq_choice(self):
        """
        Заполняет freq_choice в соответсвии с self.my_spec .
        Возращает: ничего
        """
        self.freq_choice.Clear()
        for nf in range(0, self.my_spec.data.shape[2]):
            freq = self.my_spec.df * (nf+1)
            self.freq_choice.Append( "%0.3f" % freq )
        
    def fill_etalon_list(self):
        """
        Ставит флаг, есть ли эталон
        (Раньше заполнял список, т.к. подразумевалось много эталонов)
        """
        n_et = len(self.my_spec.etalon) 
        if n_et == 0:
            ttt = ("Эталонная зависимость отсутсвует", 'red')
        if n_et == 1:
            ttt = ("Эталонная зависимость присутствует", 'green')
        if n_et == 2:
            ttt = ("Присутствует %d эталонов" % n_et , 'green')
        if (self.my_spec.calibr_details is not None) and \
          (self.my_spec.calibr_details[0] == power_spec.STD_CALIBR_FLAG):
            ttt = ("Уже калиброван" , 'black')
        self.etalon_static_text.SetLabelText(unicode(ttt[0], 'utf-8'))
        self.etalon_static_text.SetForegroundColour(ttt[1])
    
    def open_button_func(self, event):
        "Нажатие Открыть (open_button)"
        dlg = wx.DirDialog(self, u"Выберите папку со спектром")
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            dlg.Destroy()
            return
        path = dlg.GetPath()
        dlg.Destroy()
        self.open_button_func_act(path)
        
    def open_button_func_act(self, path):
        """        
        Вторая часть функции для кнопки "открыть".
        Непосредственно загрузка спектра.
        """
        self.SetStatusText(u"Загрузка...")
        self.screen_bitmap.SetBitmap(embed_gui_images._hourglass.GetBitmap())
        wx.Yield()
        try:
            loaded_spec = power_spec.load_text_spec(path)            
        except:
            logging.error("Can't load spectrum from " + path)
            dlg = wx.MessageDialog(self, u"Ошибка при загрузке спектра", "",\
                                   wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText("")
            self.screen_bitmap.SetBitmap(wx.NullBitmap)
            return
        #сброс:
        self.cur_script = None
        self.common_info = ""
        self.info_text.SetValue("")
        
        self.set_spec(loaded_spec)
        
        #заполнение остальный полей управления
        self.xlim_check.SetValue(False)
        self.ylim_check.SetValue(False)
        self.clim_check.SetValue(False)
        self.gnuplot_header_text.SetValue("")
        self.gnuplot_footer_text.SetValue("")
        self.common_info = ""
        self.SetStatusText("")
        self.screen_bitmap.SetBitmap(wx.NullBitmap)
        self.enable_controls(True) #(1ая загрузка переводит все в раб. сост.)
        
        self.plot_button_func_act()
    
    def plot_button_func(self, event):
        """
        Нажали на кнопку Построить
        """
        self.plot_button_func_act()
    
    def plot_button_func_act(self, do_show=True, file_prefix=None):
        """
        Вторая часть функции для кнопки "Построить". Также если есть
        необходимость программно нажать на "Построить", то нужно вызывать
        данную функцию.
        Считывает данные из полей ввода.
        Если file_prefix=None, то промежуточные файлы пишутся во временную папку
        (file_prefix=None). Если file_prefix!=None, то промежуточные файлы пишутся
        с началом имени file_prefix.
        Результатом успешной работы является:
           cur_draw_func
           текст в info_text
           вызов show_cur_graph (если do_show=True)
        При ошибке:           
           cur_draw_func=None (признак ошибки)
           если ошибка ввода, то вызывает report_bad_input
           если file_prefix!=None и IOError, то IOError идет дальше
        """
        self.SetStatusText(u"Обработка...")
        #сброс:
        self.cleanup_files_func()
        self.cur_draw_func = None
        self.warn_gnuplot_code = True
        s = None # скрипт, None в конце - признак неверного ввода
        is_linear = False
        self.graph_info = ""
        cleanup_files_ = self.cleanup_files
            
        #основа
        try:
            if self.grtype_choice.GetSelection()==0:
                #Skxy            
                s = basic_plots.draw_skxy(self.my_spec, cleanup_files_,\
                    file_prefix, nfreq=self.freq_choice.GetSelection(),\
                    dispers_curve=self.theor_choice.GetSelection())
            if self.grtype_choice.GetSelection()==1:
                #Skf
                angles_text = (self.angle1_text.GetValue(),\
                               self.angle2_text.GetValue())
                try:
                    angles = (float(angles_text[0]), float(angles_text[1]))
                except ValueError:
                    angles = None
                if angles[0] >= angles[1]:
                    angles = None
                if angles is not None:
                    prev_bmp = self.screen_bitmap.GetBitmap()
                    self.screen_bitmap.SetBitmap(
                        embed_gui_images._hourglass.GetBitmap())
                    wx.Yield()
                    
                    s = skf.draw_skf(self.my_spec, cleanup_files_,
                        file_prefix,\
                        dispers_curve=self.theor_choice.GetSelection(),\
                        phi0=angles[0], phi1=angles[1],\
                        high_res=self.high_res_check.GetValue())

                    self.screen_bitmap.SetBitmap(prev_bmp)
            if self.grtype_choice.GetSelection()==2:
                #Sf
                s = basic_plots.draw_sf(self.my_spec, cleanup_files_, file_prefix)
                is_linear = True
        except IOError:
            self.SetStatusText("")
            if file_prefix is None:
                logging.error("Can't write temp files!")
                return
            else:
                logging.error("Can't save files with prefix " + file_prefix)
                raise

        #границы по осям
        limits_on_off = [self.xlim_check.GetValue(), self.xlim_check.GetValue(),\
            self.ylim_check.GetValue(), self.ylim_check.GetValue(),\
            self.clim_check.GetValue(), self.clim_check.GetValue()]
        if (is_linear):
            limits_on_off[4] = False
            limits_on_off[5] = False
        limits_text = [self.xmin_text.GetValue(), self.xmax_text.GetValue(),\
            self.ymin_text.GetValue(), self.ymax_text.GetValue(),\
            self.cmin_text.GetValue(), self.cmax_text.GetValue()]
        limits_list = []
        for n in range(0,6):
            val = None
            if limits_on_off[n]:
                try:
                    val = float(limits_text[n])
                except ValueError:
                    s = None
            limits_list.append(val)
        limits = tuple(limits_list)
        
        if s is None:
            self.report_bad_input()
            self.SetStatusText("")
            return
          
        #достаем info
        s_lines_list = s.split("\n")
        in_info_section = False
        for ln in s_lines_list:
            ln = ln.strip()
            if in_info_section:
                if (len(ln) >0) and (ln[0] == "#"):
                    self.graph_info = self.graph_info + ln[1:] + "\n"
            else:
                if ln=="#INFO:":
                    in_info_section = True
        self.info_text.SetValue(self.graph_info + self.common_info)
        
        user_header = self.gnuplot_header_text.GetValue()
        if isinstance(user_header, unicode):
            user_header = user_header.encode('utf-8')
        user_footer = self.gnuplot_footer_text.GetValue()
        if isinstance(user_footer, unicode):
            user_footer = user_footer.encode('utf-8')
        s = user_header + "\n" + s + "\n" + user_footer + "\n"
        
        self.cur_draw_func = lambda created_files, mode, size:\
            draw_common.launch_gnu_plot(created_files, s, mode, file_prefix, limits,\
                False, size)        
        self.SetStatusText("")
        if do_show:
            self.show_cur_graph()    
    
    def show_cur_graph(self):
        """
        Рисует график на основании cur_draw_func, с учетом текущего размера поля.
        Конечный этап работы plot_button_func, on_size_func, ...
        """        
        if self.cur_draw_func is None:
            self.SetStatusText(u"Отображение не готово")
            self.screen_bitmap.SetBitmap(wx.EmptyBitmap(1,1))
            return
        
        #size_wx = self.screen_bitmap.GetSize()
        #size = (size_wx.GetWidth(), size_wx.GetHeight())
        size = self.screen_panel.GetSizeTuple()
        self.gnuplot_output_text.SetValue("") # сброс     
        self.SetStatusText(u"Запуск gnuplot...")        
        try:
            rv = self.cur_draw_func(self.cleanup_files, "file", size)
        except OSError:
            #совсем фейл
            logging.error("Can't run gnuplot")
            fail_text = u"Не удалось запустить gnuplot"
            self.cur_draw_func = None # значит это был плохой скрипт
            self.gnuplot_output_text.SetValue(fail_text)
            dlg = wx.MessageDialog(self, fail_text, "", wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.SetStatusText("")
            return
                
        if rv[1] is not None:            
            self.gnuplot_output_text.SetValue(rv[1])
        if (rv[0]!=0) and self.warn_gnuplot_code:
            #полу-фейл
            self.section_choice.SetSelection(1)
            self.gnuplot_notebook.SetSelection(0)
            msg_text = u"Gnuplot вернул %d, проверте текстовый вывод" % rv[0]
            dlg = wx.MessageDialog(self, msg_text, "", wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.warn_gnuplot_code = False
        
        self.SetStatusText(u"Получение рисунка из gnuplot...")
        img_fname = self.cleanup_files[-1]
        #проверить размер файла -- не 0?        
        try:
            sz = os.path.getsize(img_fname)
            if (sz==0):
                raise OSError               
            bmp = wx.Bitmap(img_fname)
            bmp_ok = bmp.IsOk()
        except OSError:
            bmp_ok = False
            
        if not bmp_ok:
            self.cur_draw_func = None # значит это был плохой скрипт              
            if rv[0]==0:
                #очень странный фейл
                logging.error("No image file was generated!")
                dlg = wx.MessageDialog(self, u"Ошибка взаимодействия с "\
                   u"gnuplot: не удалось загрузить файл", "", wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            self.SetStatusText("")
            return
        self.screen_bitmap.SetBitmap(bmp)
        self.SetStatusText("")
    
    def splitter_func(self, event):
        "претащили разделитель"
        self.show_cur_graph()
        event.Skip()
        
    def size_func(self, event):
        "Изменили размеры окна"
        event.Skip()
        self.Layout()
        #self.show_cur_graph()
        if self.after_resize_timer.IsRunning():
            self.after_resize_timer.Stop()
        self.after_resize_timer.Start(self.AFTER_RESIZE_TIMER_INTERVAL,
                                      True)
        self.enable_controls(False)
        
    
    def after_resize_timer_func(self, event):
        """
        Выполнение перерисовки по таймеру, через малый интервал после изменения
        размеров окна.
        """
        if self.my_spec.data is not None:
            self.enable_controls()
        self.show_cur_graph()
    
    def find_freq_text_func(self, event):
        """
        Когда нажали enter в строчке около списка частот.
        Поиск ближайшей частоты в списке.
        """
        try:
            input_freq = float(self.find_freq_text.GetValue())
        except ValueError:
            self.report_bad_input()
            return
        sel = int(round( (input_freq/self.my_spec.df) - 1 ))
        sel = max(sel, 0)
        sel = min(sel, self.my_spec.data.shape[2]-1)
        self.freq_choice.SetSelection(sel)
        self.find_freq_text.SetValue("")
                    
    def report_bad_input(self):
        logging.warning("Bad input")
        dlg = wx.MessageDialog(self, u"Неверный ввод", "", wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()
    
    def freq_choice_func(self, event):
        "Когда выбрана другая частота"       
        pass
       
    def on_close_func(self, event):
        "При зактрытии"
        self.SetStatusText(u"Закрываемся...")
        self.cleanup_files_func()
        event.Skip()
    
    def cleanup_files_func(self):
        "Удаляет файлы из списка cleanup"
        for fname in self.cleanup_files:
            if os.access(fname, os.F_OK):
                try:
                    os.remove(fname)
                except OSError:
                    logging.warning("Can't remove " + fname)            
        self.cleanup_files = []
    
    def gnuplot_session_button_func(self, event):
        """
        Нажали кнопку Интерактивная сессия (кнопка с луппой)
        """
        #NB: в wxPython3 ecnm диалог с кнопкой "не показвать больше".
        self.plot_button_func_act(do_show=False)        
        if self.cur_draw_func is None: return
                
        size_wx = self.screen_bitmap.GetSize()
        size = (size_wx.GetWidth(), size_wx.GetHeight())
        
        self.Hide()
        wx.Yield()                
        try:
            self.cur_draw_func(self.cleanup_files, "console", size)
        except OSError:
            pass   #ругнется следующий вызов
        self.Show()
        self.show_cur_graph() #обновляем
    
    def gnuplot_save_button_func(self, event):
        """
        Нажали пункт меню Сохранить скрипт + данные
        """
        dlg = wx.FileDialog(self,
                            u"Начало имени файла",
                            self.gnuplot_save_default_dir,
                            self.proj_name + "_",
                            "*.*|*.*",
                            wx.FD_SAVE)
        rv = dlg.ShowModal()
        if rv != wx.ID_OK:
            dlg.Destroy()
            return
        file_prefix = dlg.GetPath()
        self.gnuplot_save_default_dir = os.path.dirname(file_prefix)
        try:
            old_cwd = os.getcwd()
            os.chdir(self.gnuplot_save_default_dir)
            rel_file_prefix = os.path.relpath(file_prefix, self.gnuplot_save_default_dir)
            self.plot_button_func_act(False, rel_file_prefix)
            if self.cur_draw_func is not None:
                self.cur_draw_func(self.cleanup_files, "just_save_script", None)
            os.chdir(old_cwd)
            if self.cur_draw_func is None:
                return
        except OSError, IOError:
            logging.error("Can't save files!")
            dlg = wx.MessageDialog(self, u"Ошибка записи", "", wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
        saved_files = self.cleanup_files
        if len(saved_files)>0:
            logging.info("Files were saved to folder: " +\
                self.gnuplot_save_default_dir)
            logging.info("Data:")
            for s in saved_files[:-1]:
                logging.info(s)
            logging.info("Script for gnuplot: " + saved_files[-1])
        saved_files[:] = []
        
    def grtype_choice_func1(self, event):
        "Переключение типа графика, уход со вкладки."
        t = (self.xlim_check.GetValue(),
             self.xmin_text.GetValue(),
             self.xmax_text.GetValue(),
             self.ylim_check.GetValue(),
             self.ymin_text.GetValue(),
             self.ymax_text.GetValue(),
             self.clim_check.GetValue(),
             self.cmin_text.GetValue(),
             self.cmax_text.GetValue())
        n = self.grtype_choice.GetSelection()
        while len(self.view_ctrl) < n+1:
           self.view_ctrl.append(None)
        self.view_ctrl[n] = t
    
    def grtype_choice_func2(self, event):
        "Переключение типа графика, приход на новую вкладку."
        n = self.grtype_choice.GetSelection()
        if (len(self.view_ctrl) > n) and ( self.view_ctrl[n] is not None):
            t = self.view_ctrl[n]
        else:
            t = (False, "", "", False, "", "", False, "", "")
        self.xlim_check.SetValue(t[0])
        self.xmin_text.SetValue(t[1])
        self.xmax_text.SetValue(t[2])
        self.ylim_check.SetValue(t[3])
        self.ymin_text.SetValue(t[4])
        self.ymax_text.SetValue(t[5])
        self.clim_check.SetValue(t[6])
        self.cmin_text.SetValue(t[7])
        self.cmax_text.SetValue(t[8])
    
    def swh_menu_func(self, event):
      """
      Нажали на меню "Расчет SWH"
      Собственно, расчет существенной высоты волн (SWH) выше некоторой частоты.
      Эта "некоторая частота" запрашивается.
      Резульатт выводится в Инфо
      """
      
      dlg = wx.TextEntryDialog(self, u"Начальная частота [Гц]:", u"Расчет SWH",
                               self.last_swh_freq_str)
      rv = dlg.ShowModal()
      if rv != wx.ID_OK: return
      start_freq_str = dlg.GetValue()
      try:
        start_freq = float(start_freq_str)
      except ValueError:
        self.report_bad_input()
        return
      self.last_swh_freq_str = start_freq_str
      
      res_text = ""
      swh_list = basic_plots.calc_swh(self.my_spec, start_freq)
      res_text += "SWH, f>%0.3fГц, [м]: %0.3f" % (start_freq, swh_list[0])
      if len(swh_list) == 2:
          res_text += ", для эталона: %0.3f" % swh_list[1]
      if len(swh_list) > 2:
          res_text += ", для эталонов: "
          not_first = False
          for val in swh_list[1:]:
              if not_first:
                  res_text += "; "
              not_first = True
              res_text += "%0.3f" % val
      
      self.graph_info = res_text + "\n" + self.graph_info
      self.info_text.SetValue(unicode(
          self.graph_info + self.common_info, 'utf-8'))
      self.section_choice.SetSelection(0)

    def do_filtering_button_func(self, event):
        "Кнопка готово на вкладке калибровки."
        new_spec = self.do_filtering_with_basic()
        
        if self.transf_overwrite_check.GetValue() and \
          (self.transf_result_frame is not None):
            self.transf_result_frame.set_spec(new_spec)
            self.transf_result_frame.plot_button_func_act()
            self.transf_result_frame.Raise()
        else:
            self.transf_result_frame = self.clone_window(new_spec)
    
    def do_filtering_with_basic(self):
       """
       Для кнопки 'выполнить' на вкладке калибровки
       Возвращает:
           PowerSpec
           или None в случае ошибки (причем, об этой ошибке уже сообщили)
       Вызывается из do_filtering_button_func.
       """
       try:
           a_dB = float(self.transf_a_text.GetValue())
           kmin = float(self.transf_kmin_text.GetValue())
           gamma = float(self.transf_gamma_text.GetValue())
           fmin = float(self.transf_fmin_text.GetValue())
       except ValueError:
           self.report_bad_input()
           return None
       return calibr.basic_transform(self.my_spec, a_dB, kmin, gamma, fmin)

    def clone_button_func(self, event):
        "Нажали кнопку дублировать окно (клонировать)"
        self.clone_window(self.my_spec)
  
    def save_button_func(self, event):
        "Нажали кнопку сохранить"
        dlg = wx.DirDialog(self, u"Выберите папку для ЗАПИСИ спектра")
        res = dlg.ShowModal()
        if res != wx.ID_OK:
            dlg.Destroy()
            return
        path = dlg.GetPath()
        dlg.Destroy()
        
        self.SetStatusText(u"Запись на диск...")
        wx.Yield()
        try:
            power_spec.save_text_spec(path, self.my_spec)            
        except Exception as err:
            logging.error("Can't save spectrum to:\n%s\n%s" % (path, str(err)))
            dlg = wx.MessageDialog(self, u"Ошибка при сохранении спектра", "",\
                                   wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        self.SetStatusText("")
    
    def extra_menu_button_func(self, event):
        self.PopupMenu(self.extra_menu)

    def screenshot_menu_func(self, event):
        bmp = self.screen_bitmap.GetBitmap()
        if not bmp.IsOk(): return
        dlg = wx.FileDialog(
            self,
            message = u'Сохранить изображение',
            wildcard = u'BMP-файлы (*.bmp)|*.bmp|Все файлы (*.*)|*.*',
            style = wx.FD_SAVE)
        rv = dlg.ShowModal()
        fname = ''
        if rv != wx.ID_OK:
            dlg.Destroy()
            return
        fname = dlg.GetPath()
        dlg.Destroy()
        rv = bmp.SaveFile(fname, wx.BITMAP_TYPE_BMP)
        if not rv:
            dlg = wx.MessageDialog(self, u"Не могу сохранить изображение", "",\
                                   wx.ICON_ERROR)

def main():
    logging.basicConfig(format="%(levelname)s: %(funcName)s: %(msg)s",
      level=logging.INFO)
    app = wx.App()
    frame = GrapherMain(None)
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
