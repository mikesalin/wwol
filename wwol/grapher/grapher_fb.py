# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep 17 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

from ..common import embed_gui_images

###########################################################################
## Class GrapherMainFB
###########################################################################

class GrapherMainFB ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Grapher", pos = wx.DefaultPosition, size = wx.Size( 800,550 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		
		self.m_panel5 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer5 = wx.FlexGridSizer( 0, 6, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.plot_button = wx.Button( self.m_panel5, wx.ID_ANY, u"Построить", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.plot_button.SetDefault() 
		fgSizer5.Add( self.plot_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.clone_button = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_COPY, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.clone_button.SetToolTipString( u"Дублировать окно" )
		
		fgSizer5.Add( self.clone_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.open_button = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.open_button.SetToolTipString( u"Открыть..." )
		
		fgSizer5.Add( self.open_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.save_button = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.save_button.SetToolTipString( u"Сохранить..." )
		
		fgSizer5.Add( self.save_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.gnuplot_session_button = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FIND, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.gnuplot_session_button.SetToolTipString( u"Интерактивный режим" )
		
		fgSizer5.Add( self.gnuplot_session_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.extra_menu_button = wx.BitmapButton( self.m_panel5, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_LIST_VIEW, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer5.Add( self.extra_menu_button, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer3.Add( fgSizer5, 0, wx.EXPAND, 5 )
		
		self.section_choice = wx.Notebook( self.m_panel5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel3 = wx.Panel( self.section_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText10 = wx.StaticText( self.m_panel3, wx.ID_ANY, u"Тип графика:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		bSizer5.Add( self.m_staticText10, 0, wx.ALL, 5 )
		
		self.grtype_choice = wx.Choicebook( self.m_panel3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel41 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer1 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer1.AddGrowableCol( 1 )
		fgSizer1.AddGrowableCol( 2 )
		fgSizer1.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText2 = wx.StaticText( self.m_panel41, wx.ID_ANY, u"Частота [Гц]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		fgSizer1.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		freq_choiceChoices = []
		self.freq_choice = wx.Choice( self.m_panel41, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, freq_choiceChoices, 0 )
		self.freq_choice.SetSelection( 0 )
		fgSizer1.Add( self.freq_choice, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.find_freq_text = wx.TextCtrl( self.m_panel41, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
		fgSizer1.Add( self.find_freq_text, 0, wx.ALL, 5 )
		
		
		self.m_panel41.SetSizer( fgSizer1 )
		self.m_panel41.Layout()
		fgSizer1.Fit( self.m_panel41 )
		self.grtype_choice.AddPage( self.m_panel41, u"S(Kx,Ky)", False )
		self.m_panel51 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer10 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer2 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer2.AddGrowableCol( 1 )
		fgSizer2.AddGrowableCol( 2 )
		fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText3 = wx.StaticText( self.m_panel51, wx.ID_ANY, u"Угол [град]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		fgSizer2.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.angle1_text = wx.TextCtrl( self.m_panel51, wx.ID_ANY, u"-180", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.angle1_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.angle2_text = wx.TextCtrl( self.m_panel51, wx.ID_ANY, u"180", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.angle2_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.angle_tip_bitmap = wx.StaticBitmap( self.m_panel51, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.angle_tip_bitmap, 0, wx.ALL, 5 )
		
		
		bSizer10.Add( fgSizer2, 0, wx.EXPAND, 5 )
		
		self.high_res_check = wx.CheckBox( self.m_panel51, wx.ID_ANY, u"Увеличить разрешение", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer10.Add( self.high_res_check, 0, wx.ALL, 5 )
		
		
		self.m_panel51.SetSizer( bSizer10 )
		self.m_panel51.Layout()
		bSizer10.Fit( self.m_panel51 )
		self.grtype_choice.AddPage( self.m_panel51, u"S(K,f)", False )
		self.m_panel6 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.grtype_choice.AddPage( self.m_panel6, u"S(f)", True )
		self.m_panel13 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer101 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer21 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer21.AddGrowableCol( 1 )
		fgSizer21.AddGrowableCol( 2 )
		fgSizer21.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText31 = wx.StaticText( self.m_panel13, wx.ID_ANY, u"Угол [град]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )
		fgSizer21.Add( self.m_staticText31, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.angle1_text1 = wx.TextCtrl( self.m_panel13, wx.ID_ANY, u"-180", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.angle1_text1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.angle2_text1 = wx.TextCtrl( self.m_panel13, wx.ID_ANY, u"180", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.angle2_text1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.angle_tip_bitmap1 = wx.StaticBitmap( self.m_panel13, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TIP, wx.ART_TOOLBAR ), wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.angle_tip_bitmap1, 0, wx.ALL, 5 )
		
		
		bSizer101.Add( fgSizer21, 1, wx.EXPAND, 5 )
		
		self.high_res_check1 = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Увеличить разрешение", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer101.Add( self.high_res_check1, 0, wx.ALL, 5 )
		
		
		self.m_panel13.SetSizer( bSizer101 )
		self.m_panel13.Layout()
		bSizer101.Fit( self.m_panel13 )
		self.grtype_choice.AddPage( self.m_panel13, u"S(K)", False )
		self.m_panel131 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer12 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer8 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer8.AddGrowableCol( 1 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		sect_dir_choiceChoices = [ u"вдоль x, когда y =", u"вдоль y, когда x =" ]
		self.sect_dir_choice = wx.Choice( self.m_panel131, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, sect_dir_choiceChoices, 0 )
		self.sect_dir_choice.SetSelection( 0 )
		fgSizer8.Add( self.sect_dir_choice, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.sect_vals_text = wx.TextCtrl( self.m_panel131, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.sect_vals_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		bSizer12.Add( fgSizer8, 0, wx.EXPAND, 5 )
		
		self.m_staticText141 = wx.StaticText( self.m_panel131, wx.ID_ANY, u"Список через пробел", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText141.Wrap( -1 )
		bSizer12.Add( self.m_staticText141, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		self.m_panel131.SetSizer( bSizer12 )
		self.m_panel131.Layout()
		bSizer12.Fit( self.m_panel131 )
		self.grtype_choice.AddPage( self.m_panel131, u"Сечение", False )
		self.panel14 = wx.Panel( self.grtype_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer13 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer14 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer14.AddGrowableCol( 1 )
		fgSizer14.SetFlexibleDirection( wx.BOTH )
		fgSizer14.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText19 = wx.StaticText( self.panel14, wx.ID_ANY, u"Список частот:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )
		fgSizer14.Add( self.m_staticText19, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.freqs_for_polar_text = wx.TextCtrl( self.panel14, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.freqs_for_polar_text.SetToolTipString( u"Список частот через пробел" )
		
		fgSizer14.Add( self.freqs_for_polar_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.set_that_freq_button = wx.Button( self.panel14, wx.ID_ANY, u"<= 1.000", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer14.Add( self.set_that_freq_button, 0, wx.ALL, 5 )
		
		
		bSizer13.Add( fgSizer14, 1, wx.EXPAND, 5 )
		
		self.m_staticText16 = wx.StaticText( self.panel14, wx.ID_ANY, u"Границы  интегрирования по K:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )
		bSizer13.Add( self.m_staticText16, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )
		
		gSizer4 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.k_range_min_text = wx.TextCtrl( self.panel14, wx.ID_ANY, u"0.5", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.k_range_min_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.k_range_max_text = wx.TextCtrl( self.panel14, wx.ID_ANY, u"1.5", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer4.Add( self.k_range_max_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer13.Add( gSizer4, 1, wx.EXPAND, 5 )
		
		self.k_range_is_relative_check = wx.CheckBox( self.panel14, wx.ID_ANY, u"Относительно дисперионного K", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.k_range_is_relative_check.SetValue(True) 
		bSizer13.Add( self.k_range_is_relative_check, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		gSizer51 = wx.GridSizer( 0, 3, 0, 0 )
		
		self.polar_check = wx.CheckBox( self.panel14, wx.ID_ANY, u"Полярный", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.polar_check.SetValue(True) 
		gSizer51.Add( self.polar_check, 0, wx.ALL, 5 )
		
		self.polar_in_dB_check = wx.CheckBox( self.panel14, wx.ID_ANY, u"дБ", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer51.Add( self.polar_in_dB_check, 0, wx.ALL, 5 )
		
		self.polar_norm_check = wx.CheckBox( self.panel14, wx.ID_ANY, u"Нормировка", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer51.Add( self.polar_norm_check, 0, wx.ALL, 5 )
		
		
		bSizer13.Add( gSizer51, 1, wx.EXPAND, 5 )
		
		
		self.panel14.SetSizer( bSizer13 )
		self.panel14.Layout()
		bSizer13.Fit( self.panel14 )
		self.grtype_choice.AddPage( self.panel14, u"Угловая зависимость", False )
		bSizer5.Add( self.grtype_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText1 = wx.StaticText( self.m_panel3, wx.ID_ANY, u"Инфо:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		bSizer5.Add( self.m_staticText1, 0, wx.ALL, 5 )
		
		self.info_text = wx.TextCtrl( self.m_panel3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer5.Add( self.info_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel3.SetSizer( bSizer5 )
		self.m_panel3.Layout()
		bSizer5.Fit( self.m_panel3 )
		self.section_choice.AddPage( self.m_panel3, u"Главная", True )
		self.m_panel7 = wx.Panel( self.section_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer3.AddGrowableCol( 1 )
		fgSizer3.SetFlexibleDirection( wx.BOTH )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		
		fgSizer3.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText14 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Границы по осям:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		fgSizer3.Add( self.m_staticText14, 0, wx.ALL, 5 )
		
		self.xlim_check = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer3.Add( self.xlim_check, 0, wx.ALL, 5 )
		
		gSizer5 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.xmin_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.xmin_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.xmax_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.xmax_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer3.Add( gSizer5, 1, wx.EXPAND, 5 )
		
		self.ylim_check = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer3.Add( self.ylim_check, 0, wx.ALL, 5 )
		
		gSizer6 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.ymin_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer6.Add( self.ymin_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.ymax_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer6.Add( self.ymax_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer3.Add( gSizer6, 1, wx.EXPAND, 5 )
		
		self.clim_check = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"цв", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer3.Add( self.clim_check, 0, wx.ALL, 5 )
		
		gSizer7 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.cmin_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer7.Add( self.cmin_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.cmax_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer7.Add( self.cmax_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer3.Add( gSizer7, 1, wx.EXPAND, 5 )
		
		self.m_staticText8 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"теор", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		fgSizer3.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		theor_choiceChoices = [ u"0", u"1", u"2" ]
		self.theor_choice = wx.Choice( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, theor_choiceChoices, 0 )
		self.theor_choice.SetSelection( 0 )
		fgSizer3.Add( self.theor_choice, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer6.Add( fgSizer3, 0, wx.EXPAND, 5 )
		
		self.m_staticText81 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Скрипт Gnuplot:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText81.Wrap( -1 )
		bSizer6.Add( self.m_staticText81, 0, wx.ALL, 5 )
		
		self.gnuplot_notebook = wx.Notebook( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel12 = wx.Panel( self.gnuplot_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.gnuplot_output_text = wx.TextCtrl( self.m_panel12, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		bSizer8.Add( self.gnuplot_output_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel12.SetSizer( bSizer8 )
		self.m_panel12.Layout()
		bSizer8.Fit( self.m_panel12 )
		self.gnuplot_notebook.AddPage( self.m_panel12, u"Вывод", True )
		self.m_panel10 = wx.Panel( self.gnuplot_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer61 = wx.BoxSizer( wx.VERTICAL )
		
		self.gnuplot_header_text = wx.TextCtrl( self.m_panel10, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer61.Add( self.gnuplot_header_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel10.SetSizer( bSizer61 )
		self.m_panel10.Layout()
		bSizer61.Fit( self.m_panel10 )
		self.gnuplot_notebook.AddPage( self.m_panel10, u"Верх", False )
		self.m_panel11 = wx.Panel( self.gnuplot_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.gnuplot_footer_text = wx.TextCtrl( self.m_panel11, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		bSizer7.Add( self.gnuplot_footer_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel11.SetSizer( bSizer7 )
		self.m_panel11.Layout()
		bSizer7.Fit( self.m_panel11 )
		self.gnuplot_notebook.AddPage( self.m_panel11, u"Низ", False )
		
		bSizer6.Add( self.gnuplot_notebook, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.m_panel7.SetSizer( bSizer6 )
		self.m_panel7.Layout()
		bSizer6.Fit( self.m_panel7 )
		self.section_choice.AddPage( self.m_panel7, u"Вид", False )
		self.m_panel9 = wx.Panel( self.section_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer11 = wx.BoxSizer( wx.VERTICAL )
		
		self.etalon_static_text = wx.StaticText( self.m_panel9, wx.ID_ANY, u"Эталонная зависимость присутствует", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.etalon_static_text.Wrap( -1 )
		bSizer11.Add( self.etalon_static_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		fgSizer7 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer7.AddGrowableCol( 1 )
		fgSizer7.SetFlexibleDirection( wx.BOTH )
		fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText102 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"A [дБ]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText102.Wrap( -1 )
		fgSizer7.Add( self.m_staticText102, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.transf_a_text = wx.TextCtrl( self.m_panel9, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.transf_a_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText111 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"Kmin [рад/м]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText111.Wrap( -1 )
		fgSizer7.Add( self.m_staticText111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.transf_kmin_text = wx.TextCtrl( self.m_panel9, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.transf_kmin_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText12 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"gamma:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		fgSizer7.Add( self.m_staticText12, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.transf_gamma_text = wx.TextCtrl( self.m_panel9, wx.ID_ANY, u"0.25", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.transf_gamma_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText131 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"fmin [Гц]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText131.Wrap( -1 )
		fgSizer7.Add( self.m_staticText131, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.transf_fmin_text = wx.TextCtrl( self.m_panel9, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer7.Add( self.transf_fmin_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer11.Add( fgSizer7, 0, wx.EXPAND, 5 )
		
		fgSizer61 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer61.AddGrowableCol( 0 )
		fgSizer61.AddGrowableCol( 1 )
		fgSizer61.SetFlexibleDirection( wx.BOTH )
		fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.transf_overwrite_check = wx.CheckBox( self.m_panel9, wx.ID_ANY, u"Поверх пред. результата", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.transf_overwrite_check, 0, wx.ALL, 5 )
		
		self.do_filtering_button = wx.Button( self.m_panel9, wx.ID_ANY, u"Выполнить", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.do_filtering_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		bSizer11.Add( fgSizer61, 0, wx.EXPAND, 5 )
		
		
		self.m_panel9.SetSizer( bSizer11 )
		self.m_panel9.Layout()
		bSizer11.Fit( self.m_panel9 )
		self.section_choice.AddPage( self.m_panel9, u"Калибровка", False )
		
		bSizer3.Add( self.section_choice, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.m_panel5.SetSizer( bSizer3 )
		self.m_panel5.Layout()
		bSizer3.Fit( self.m_panel5 )
		self.screen_panel = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.screen_bitmap = wx.StaticBitmap( self.screen_panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.screen_bitmap, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.screen_panel.SetSizer( bSizer2 )
		self.screen_panel.Layout()
		bSizer2.Fit( self.screen_panel )
		self.m_splitter1.SplitVertically( self.m_panel5, self.screen_panel, 400 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.status_bar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.extra_menu = wx.Menu()
		self.screenshot_menu = wx.MenuItem( self.extra_menu, wx.ID_ANY, u"Сохранить изображение как есть...", wx.EmptyString, wx.ITEM_NORMAL )
		self.screenshot_menu.SetBitmap( embed_gui_images.get_scrshotBitmap() )
#		self.screenshot_menu.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_MENU ) )
		self.extra_menu.AppendItem( self.screenshot_menu )
		
		self.gnuplot_save_button = wx.MenuItem( self.extra_menu, wx.ID_ANY, u"Экспорт графика: скрипт + данные...", wx.EmptyString, wx.ITEM_NORMAL )
		self.gnuplot_save_button.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_MENU ) )
		self.extra_menu.AppendItem( self.gnuplot_save_button )
		
		self.swh_menu = wx.MenuItem( self.extra_menu, wx.ID_ANY, u"Расчет SHW...", wx.EmptyString, wx.ITEM_NORMAL )
		self.extra_menu.AppendItem( self.swh_menu )
		
		self.Bind( wx.EVT_RIGHT_DOWN, self.GrapherMainFBOnContextMenu ) 
		
		self.after_resize_timer = wx.Timer()
		self.after_resize_timer.SetOwner( self, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.on_close_func )
		self.Bind( wx.EVT_SIZE, self.size_func )
		self.m_splitter1.Bind( wx.EVT_SPLITTER_SASH_POS_CHANGED, self.splitter_func )
		self.plot_button.Bind( wx.EVT_BUTTON, self.plot_button_func )
		self.clone_button.Bind( wx.EVT_BUTTON, self.clone_button_func )
		self.open_button.Bind( wx.EVT_BUTTON, self.open_button_func )
		self.save_button.Bind( wx.EVT_BUTTON, self.save_button_func )
		self.gnuplot_session_button.Bind( wx.EVT_BUTTON, self.gnuplot_session_button_func )
		self.extra_menu_button.Bind( wx.EVT_BUTTON, self.extra_menu_button_func )
		self.grtype_choice.Bind( wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.grtype_choice_func2 )
		self.grtype_choice.Bind( wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.grtype_choice_func1 )
		self.freq_choice.Bind( wx.EVT_CHOICE, self.freq_choice_func )
		self.find_freq_text.Bind( wx.EVT_TEXT_ENTER, self.find_freq_text_func )
		self.set_that_freq_button.Bind( wx.EVT_BUTTON, self._set_that_freq_button_func )
		self.do_filtering_button.Bind( wx.EVT_BUTTON, self.do_filtering_button_func )
		self.Bind( wx.EVT_MENU, self.screenshot_menu_func, id = self.screenshot_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.gnuplot_save_button_func, id = self.gnuplot_save_button.GetId() )
		self.Bind( wx.EVT_MENU, self.swh_menu_func, id = self.swh_menu.GetId() )
		self.Bind( wx.EVT_TIMER, self.after_resize_timer_func, id=wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def on_close_func( self, event ):
		event.Skip()
	
	def size_func( self, event ):
		event.Skip()
	
	def splitter_func( self, event ):
		event.Skip()
	
	def plot_button_func( self, event ):
		event.Skip()
	
	def clone_button_func( self, event ):
		event.Skip()
	
	def open_button_func( self, event ):
		event.Skip()
	
	def save_button_func( self, event ):
		event.Skip()
	
	def gnuplot_session_button_func( self, event ):
		event.Skip()
	
	def extra_menu_button_func( self, event ):
		event.Skip()
	
	def grtype_choice_func2( self, event ):
		event.Skip()
	
	def grtype_choice_func1( self, event ):
		event.Skip()
	
	def freq_choice_func( self, event ):
		event.Skip()
	
	def find_freq_text_func( self, event ):
		event.Skip()
	
	def _set_that_freq_button_func( self, event ):
		event.Skip()
	
	def do_filtering_button_func( self, event ):
		event.Skip()
	
	def screenshot_menu_func( self, event ):
		event.Skip()
	
	def gnuplot_save_button_func( self, event ):
		event.Skip()
	
	def swh_menu_func( self, event ):
		event.Skip()
	
	def after_resize_timer_func( self, event ):
		event.Skip()
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 400 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	
	def GrapherMainFBOnContextMenu( self, event ):
		self.PopupMenu( self.extra_menu, event.GetPosition() )
		

