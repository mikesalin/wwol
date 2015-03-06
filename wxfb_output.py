# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Sep 17 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainVideoFrame
###########################################################################

class MainVideoFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"WWOL", pos = wx.DefaultPosition, size = wx.Size( 800,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.test_menu = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Тест\tF5", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.test_menu )
		
		self.m_menubar1.Append( self.m_menu1, u"Файл" ) 
		
		self.m_menu2 = wx.Menu()
		self.config_source_menu = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Источник...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.config_source_menu )
		
		self.m_menuItem4 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"Геометрия...", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu2.AppendItem( self.m_menuItem4 )
		
		self.m_menubar1.Append( self.m_menu2, u"Параметры" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		self.my_toolbar = self.CreateToolBar( wx.TB_HORIZONTAL|wx.TB_HORZ_TEXT, wx.ID_ANY ) 
		self.prev_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.next_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.jump_frame_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, u"кадр | кадров", wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.jump_time_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, u"мм:cc.мс | мм:сс.мс", wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.zoom_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_FIND, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, wx.EmptyString, wx.EmptyString, None ) 
		
		self.my_gauge = wx.Gauge( self.my_toolbar, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
		self.my_gauge.SetValue( 70 ) 
		self.my_toolbar.AddControl( self.my_gauge )
		self.my_toolbar.Realize() 
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_splitter1 = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_splitter1.Bind( wx.EVT_IDLE, self.m_splitter1OnIdle )
		
		self.m_panel1 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.a_bmp = wx.StaticBitmap( self.m_panel1, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.a_bmp, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel1.SetSizer( bSizer2 )
		self.m_panel1.Layout()
		bSizer2.Fit( self.m_panel1 )
		self.m_panel2 = wx.Panel( self.m_splitter1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.b_bmp = wx.StaticBitmap( self.m_panel2, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.b_bmp, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel2.SetSizer( bSizer3 )
		self.m_panel2.Layout()
		bSizer3.Fit( self.m_panel2 )
		self.m_splitter1.SplitVertically( self.m_panel1, self.m_panel2, 0 )
		bSizer1.Add( self.m_splitter1, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close_func )
		self.Bind( wx.EVT_SIZE, self.size_func )
		self.Bind( wx.EVT_MENU, self.test_menu_func, id = self.test_menu.GetId() )
		self.Bind( wx.EVT_MENU, self.config_source_menu_func, id = self.config_source_menu.GetId() )
		self.Bind( wx.EVT_TOOL, self.prev_tool_func, id = self.prev_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self.next_tool_func, id = self.next_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self.jump_frame_tool_func, id = self.jump_frame_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self.jump_time_tool_func, id = self.jump_time_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self.zoom_tool_func, id = self.zoom_tool.GetId() )
		self.m_splitter1.Bind( wx.EVT_SPLITTER_SASH_POS_CHANGED, self.size_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close_func( self, event ):
		event.Skip()
	
	def size_func( self, event ):
		event.Skip()
	
	def test_menu_func( self, event ):
		event.Skip()
	
	def config_source_menu_func( self, event ):
		event.Skip()
	
	def prev_tool_func( self, event ):
		event.Skip()
	
	def next_tool_func( self, event ):
		event.Skip()
	
	def jump_frame_tool_func( self, event ):
		event.Skip()
	
	def jump_time_tool_func( self, event ):
		event.Skip()
	
	def zoom_tool_func( self, event ):
		event.Skip()
	
	
	def m_splitter1OnIdle( self, event ):
		self.m_splitter1.SetSashPosition( 0 )
		self.m_splitter1.Unbind( wx.EVT_IDLE )
	

###########################################################################
## Class ZoomDlg
###########################################################################

class ZoomDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Масштаб", pos = wx.DefaultPosition, size = wx.Size( 220,140 ), style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer12 = wx.GridSizer( 0, 2, 0, 0 )
		
		zoom_a_choiceChoices = [ u"50%", u"100%", u"150%", u"200%" ]
		self.zoom_a_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, zoom_a_choiceChoices, 0 )
		self.zoom_a_choice.SetSelection( 0 )
		gSizer12.Add( self.zoom_a_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		zoom_b_choiceChoices = [ u"50%", u"100%", u"150%", u"200%" ]
		self.zoom_b_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, zoom_b_choiceChoices, 0 )
		self.zoom_b_choice.SetSelection( 0 )
		gSizer12.Add( self.zoom_b_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.reset_a_button = wx.Button( self, wx.ID_ANY, u"Сброс", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer12.Add( self.reset_a_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_button18 = wx.Button( self, wx.ID_ANY, u"Сброс", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer12.Add( self.m_button18, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer9.Add( gSizer12, 0, wx.EXPAND, 5 )
		
		self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, u"Включен режим манипуляций изобразением мышью.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( 200 )
		bSizer9.Add( self.m_staticText30, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer9 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close_func )
		self.zoom_a_choice.Bind( wx.EVT_CHOICE, self.zoom_a_choice_func )
		self.reset_a_button.Bind( wx.EVT_BUTTON, self.reset_a_button_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close_func( self, event ):
		event.Skip()
	
	def zoom_a_choice_func( self, event ):
		event.Skip()
	
	def reset_a_button_func( self, event ):
		event.Skip()
	

###########################################################################
## Class SourceDlg
###########################################################################

class SourceDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Источник изображения", pos = wx.DefaultPosition, size = wx.Size( 600,350 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.source_type_choice = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel7 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer2 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer2.AddGrowableCol( 1 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Видеофайл:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer2.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl1 = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_textCtrl1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button3 = wx.Button( self.m_panel7, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer2.Add( self.m_button3, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( fgSizer2, 1, wx.EXPAND, 5 )
		
		fgSizer9 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer9.AddGrowableCol( 0 )
		fgSizer9.SetFlexibleDirection( wx.BOTH )
		fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.user_temp_path_check = wx.CheckBox( self.m_panel7, wx.ID_ANY, u"Специальное место для временных файлов", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer9.Add( self.user_temp_path_check, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button14 = wx.Button( self.m_panel7, wx.ID_ANY, u"(i)", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer9.Add( self.m_button14, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		bSizer7.Add( fgSizer9, 1, wx.EXPAND, 5 )
		
		
		self.m_panel7.SetSizer( bSizer7 )
		self.m_panel7.Layout()
		bSizer7.Fit( self.m_panel7 )
		self.source_type_choice.AddPage( self.m_panel7, u"Ffmpeg, авто", True )
		self.m_panel8 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer21 = wx.FlexGridSizer( 0, 5, 0, 0 )
		fgSizer21.AddGrowableCol( 3 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText41 = wx.StaticText( self.m_panel8, wx.ID_ANY, u"Команда:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )
		fgSizer21.Add( self.m_staticText41, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_hyperlink4 = wx.HyperlinkCtrl( self.m_panel8, wx.ID_ANY, u"(?)", wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		fgSizer21.Add( self.m_hyperlink4, 0, wx.ALL, 5 )
		
		self.m_checkBox11 = wx.CheckBox( self.m_panel8, wx.ID_ANY, u"shell", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_checkBox11, 0, wx.ALL, 5 )
		
		self.m_textCtrl11 = wx.TextCtrl( self.m_panel8, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.m_textCtrl11, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button15 = wx.Button( self.m_panel8, wx.ID_ANY, u"A", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer21.Add( self.m_button15, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel8.SetSizer( fgSizer21 )
		self.m_panel8.Layout()
		fgSizer21.Fit( self.m_panel8 )
		self.source_type_choice.AddPage( self.m_panel8, u"Ffmpeg, ручная настройка", False )
		self.m_panel9 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.source_type_choice.AddPage( self.m_panel9, u"Папка с картинками", False )
		bSizer6.Add( self.source_type_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer8 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer8.AddGrowableCol( 1 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.pic_path_static_text = wx.StaticText( self, wx.ID_ANY, u"Путь к картинкам:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pic_path_static_text.Wrap( -1 )
		fgSizer8.Add( self.pic_path_static_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.pic_path_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.pic_path_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.pic_path_browse_button = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer8.Add( self.pic_path_browse_button, 0, wx.ALL, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.pic_path_comment_static_text = wx.StaticText( self, wx.ID_ANY, u"Шаблон вида:  my_path/img%04d.bmp", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pic_path_comment_static_text.Wrap( -1 )
		fgSizer8.Add( self.pic_path_comment_static_text, 0, wx.ALL, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"Диапазон кадров:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )
		fgSizer8.Add( self.m_staticText24, 0, wx.ALL, 5 )
		
		gSizer71 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.start_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer71.Add( self.start_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer10 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer10.AddGrowableCol( 0 )
		fgSizer10.AddGrowableCol( 1 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.finish_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer10.Add( self.finish_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.max_finish_sttext = wx.StaticText( self, wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.max_finish_sttext.Wrap( -1 )
		fgSizer10.Add( self.max_finish_sttext, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		gSizer71.Add( fgSizer10, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		
		fgSizer8.Add( gSizer71, 1, wx.EXPAND, 5 )
		
		self.max_finish_check = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.max_finish_check.SetValue(True) 
		fgSizer8.Add( self.max_finish_check, 0, wx.ALL, 5 )
		
		self.fps_static_text = wx.StaticText( self, wx.ID_ANY, u"FPS:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.fps_static_text.Wrap( -1 )
		fgSizer8.Add( self.fps_static_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		gSizer7 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.fps_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer7.Add( self.fps_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer8.Add( gSizer7, 1, wx.EXPAND, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Число кадров для Длина БПФ:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer8.Add( self.m_staticText25, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		gSizer5 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.pack_len_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.pack_len_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.overlap_check = wx.CheckBox( self, wx.ID_ANY, u"перекрытие 1/2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.overlap_check.SetValue(True) 
		gSizer5.Add( self.overlap_check, 0, wx.ALL, 5 )
		
		
		fgSizer8.Add( gSizer5, 1, wx.EXPAND, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		bSizer6.Add( fgSizer8, 1, wx.EXPAND, 5 )
		
		m_sdbSizer1 = wx.StdDialogButtonSizer()
		self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
		self.m_sdbSizer1Apply = wx.Button( self, wx.ID_APPLY )
		m_sdbSizer1.AddButton( self.m_sdbSizer1Apply )
		self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
		m_sdbSizer1.Realize();
		
		bSizer6.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer6 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close_func )
		self.source_type_choice.Bind( wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.source_type_choice_func2 )
		self.source_type_choice.Bind( wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.source_type_choice_func1 )
		self.user_temp_path_check.Bind( wx.EVT_CHECKBOX, self.hide_show_items )
		self.max_finish_check.Bind( wx.EVT_CHECKBOX, self.hide_show_items )
		self.m_sdbSizer1Apply.Bind( wx.EVT_BUTTON, self.apply_button_func )
		self.m_sdbSizer1OK.Bind( wx.EVT_BUTTON, self.ok_button_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close_func( self, event ):
		event.Skip()
	
	def source_type_choice_func2( self, event ):
		event.Skip()
	
	def source_type_choice_func1( self, event ):
		event.Skip()
	
	def hide_show_items( self, event ):
		event.Skip()
	
	
	def apply_button_func( self, event ):
		event.Skip()
	
	def ok_button_func( self, event ):
		event.Skip()
	

###########################################################################
## Class GeomDlg
###########################################################################

class GeomDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Геометрия", pos = wx.DefaultPosition, size = wx.Size( 400,400 ), style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer61 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText13 = wx.StaticText( self, wx.ID_ANY, u"Предварительное растяжение/сжатие:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		bSizer61.Add( self.m_staticText13, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		fgSizer6 = wx.FlexGridSizer( 0, 5, 0, 0 )
		fgSizer6.AddGrowableCol( 1 )
		fgSizer6.AddGrowableCol( 3 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText14 = wx.StaticText( self, wx.ID_ANY, u"x ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		fgSizer6.Add( self.m_staticText14, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl10 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl10, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText15 = wx.StaticText( self, wx.ID_ANY, u"y ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText15.Wrap( -1 )
		fgSizer6.Add( self.m_staticText15, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl111 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer6.Add( self.m_textCtrl111, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText221 = wx.StaticText( self, wx.ID_ANY, u"     ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText221.Wrap( -1 )
		fgSizer6.Add( self.m_staticText221, 0, wx.ALL, 5 )
		
		
		bSizer61.Add( fgSizer6, 0, wx.EXPAND, 5 )
		
		fgSizer10 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer10.AddGrowableCol( 0 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText16 = wx.StaticText( self, wx.ID_ANY, u"Область обработки:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )
		fgSizer10.Add( self.m_staticText16, 0, wx.ALL|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer61.Add( fgSizer10, 0, wx.EXPAND, 5 )
		
		fgSizer61 = wx.FlexGridSizer( 0, 5, 0, 0 )
		fgSizer61.AddGrowableCol( 1 )
		fgSizer61.AddGrowableCol( 3 )
		fgSizer61.SetFlexibleDirection( wx.BOTH )
		fgSizer61.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText141 = wx.StaticText( self, wx.ID_ANY, u"x1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText141.Wrap( -1 )
		fgSizer61.Add( self.m_staticText141, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl101 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.m_textCtrl101, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText152 = wx.StaticText( self, wx.ID_ANY, u"y1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText152.Wrap( -1 )
		fgSizer61.Add( self.m_staticText152, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl1111 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.m_textCtrl1111, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button14 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer61.Add( self.m_button14, 0, wx.ALL, 5 )
		
		self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, u"x2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )
		fgSizer61.Add( self.m_staticText21, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl16 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.m_textCtrl16, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, u"y2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText22.Wrap( -1 )
		fgSizer61.Add( self.m_staticText22, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl17 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer61.Add( self.m_textCtrl17, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer61.Add( fgSizer61, 0, wx.EXPAND, 5 )
		
		self.m_staticText231 = wx.StaticText( self, wx.ID_ANY, u"Коррекция преспективы:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText231.Wrap( -1 )
		bSizer61.Add( self.m_staticText231, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		fgSizer9 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer9.AddGrowableCol( 1 )
		fgSizer9.SetFlexibleDirection( wx.BOTH )
		fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText241 = wx.StaticText( self, wx.ID_ANY, u"1/2 верт. угла зрения [град]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText241.Wrap( -1 )
		fgSizer9.Add( self.m_staticText241, 0, wx.ALL, 5 )
		
		self.m_textCtrl18 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer9.Add( self.m_textCtrl18, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer9.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText251 = wx.StaticText( self, wx.ID_ANY, u"Высота [м]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText251.Wrap( -1 )
		fgSizer9.Add( self.m_staticText251, 0, wx.ALL, 5 )
		
		self.m_textCtrl19 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer9.Add( self.m_textCtrl19, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer9.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"Угол центр-горизонт [град]:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer9.Add( self.m_staticText26, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_textCtrl21 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer9.Add( self.m_textCtrl21, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button11 = wx.Button( self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_button11.SetToolTipString( u"Горизонт в кадре..." )
		
		fgSizer9.Add( self.m_button11, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer61.Add( fgSizer9, 0, wx.EXPAND, 5 )
		
		gSizer61 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.m_button12 = wx.Button( self, wx.ID_ANY, u"Задать коэффициентами...", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer61.Add( self.m_button12, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_button13 = wx.Button( self, wx.ID_ANY, u"1:1", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer61.Add( self.m_button13, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		bSizer61.Add( gSizer61, 0, wx.EXPAND, 5 )
		
		m_sdbSizer2 = wx.StdDialogButtonSizer()
		self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
		self.m_sdbSizer2Apply = wx.Button( self, wx.ID_APPLY )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Apply )
		self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
		m_sdbSizer2.Realize();
		
		bSizer61.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer61 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

