# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

ID_JUMP_FRAME_TOOL = 1000
ID_JUMP_TIME_TOOL = 1001

###########################################################################
## Class MainVideoFrame
###########################################################################

class MainVideoFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"WWOL", pos = wx.DefaultPosition, size = wx.Size( 800,500 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.my_toolbar = self.CreateToolBar( wx.TB_HORIZONTAL|wx.TB_HORZ_TEXT, wx.ID_ANY ) 
		self.menu_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_LIST_VIEW, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Menu", wx.EmptyString, None ) 
		
		self.preview_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, u"Preview", wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, wx.EmptyString, wx.EmptyString, None ) 
		
		self.proc_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, u"Process", wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, wx.EmptyString, wx.EmptyString, None ) 
		
		self.view_step_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Frame change step", wx.EmptyString, None ) 
		
		self.prev_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_GO_BACK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Назад", wx.EmptyString, None ) 
		
		self.next_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_GO_FORWARD, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Next", wx.EmptyString, None ) 
		
		self.jump_frame_tool = self.my_toolbar.AddLabelTool( ID_JUMP_FRAME_TOOL, u"frame | total", wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Jump to frame...", wx.EmptyString, None ) 
		
		self.jump_time_tool = self.my_toolbar.AddLabelTool( ID_JUMP_TIME_TOOL, u"mm:ss.ms |mm:ss.ms", wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Jump to time...", wx.EmptyString, None ) 
		
		self.zoom_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_FIND, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, u"Zoom / move image", wx.EmptyString, None ) 
		
		self.scrshot_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_NORMAL, u"Screenshot", wx.EmptyString, None ) 
		
		self.points_tool = self.my_toolbar.AddLabelTool( wx.ID_ANY, wx.EmptyString, wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_TOOLBAR ), wx.NullBitmap, wx.ITEM_CHECK, u"Measure points coordinates", wx.EmptyString, None ) 
		
		self.my_toolbar.Realize() 
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.my_info_bar = wx.InfoBar( self )
		self.my_info_bar.SetShowHideEffects( wx.SHOW_EFFECT_NONE, wx.SHOW_EFFECT_NONE )
		self.my_info_bar.SetEffectDuration( 500 )
		bSizer1.Add( self.my_info_bar, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.props_images_splitter = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_NO_XP_THEME )
		self.props_images_splitter.SetSashSize( 5 )
		self.props_images_splitter.Bind( wx.EVT_IDLE, self.props_images_splitterOnIdle )
		self.props_images_splitter.SetMinimumPaneSize( 20 )
		
		self.m_panel6 = wx.Panel( self.props_images_splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer9 = wx.FlexGridSizer( 4, 1, 0, 0 )
		fgSizer9.AddGrowableCol( 0 )
		fgSizer9.AddGrowableRow( 2 )
		fgSizer9.SetFlexibleDirection( wx.BOTH )
		fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.config_notebook = wx.Notebook( self.m_panel6, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel10 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer121 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText241 = wx.StaticText( self.m_panel10, wx.ID_ANY, u"Video data source", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText241.Wrap( -1 )
		self.m_staticText241.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer121.Add( self.m_staticText241, 0, wx.ALL, 5 )
		
		self.source_button = wx.Button( self.m_panel10, wx.ID_ANY, u"Configure...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.source_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer121.Add( self.source_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel10.SetSizer( bSizer121 )
		self.m_panel10.Layout()
		bSizer121.Fit( self.m_panel10 )
		self.config_notebook.AddPage( self.m_panel10, u"Src", True )
		self.m_panel11 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer13 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText24 = wx.StaticText( self.m_panel11, wx.ID_ANY, u"Projection", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )
		self.m_staticText24.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer13.Add( self.m_staticText24, 0, wx.ALL, 5 )
		
		self.camera_list_button = wx.Button( self.m_panel11, wx.ID_ANY, u"Select camera...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.camera_list_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer13.Add( self.camera_list_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.pick_horizont_button = wx.Button( self.m_panel11, wx.ID_ANY, u"Pick horizont", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pick_horizont_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer13.Add( self.pick_horizont_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		gSizer6 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.simple_proj_button = wx.Button( self.m_panel11, wx.ID_ANY, u"simple projection", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer6.Add( self.simple_proj_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer13.Add( gSizer6, 0, wx.EXPAND, 5 )
		
		
		self.m_panel11.SetSizer( bSizer13 )
		self.m_panel11.Layout()
		bSizer13.Fit( self.m_panel11 )
		self.config_notebook.AddPage( self.m_panel11, u"P", False )
		self.m_panel111 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer131 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText30 = wx.StaticText( self.m_panel111, wx.ID_ANY, u"Processing areas", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )
		self.m_staticText30.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer131.Add( self.m_staticText30, 0, wx.ALL, 5 )
		
		self.select_area_button = wx.Button( self.m_panel111, wx.ID_ANY, u"Select", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.select_area_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer131.Add( self.select_area_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.select_multiple_areas_button = wx.Button( self.m_panel111, wx.ID_ANY, u"Select several", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer131.Add( self.select_multiple_areas_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer11 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer11.AddGrowableCol( 1 )
		fgSizer11.SetFlexibleDirection( wx.BOTH )
		fgSizer11.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.active_area_static_text = wx.StaticText( self.m_panel111, wx.ID_ANY, u"Active:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.active_area_static_text.Wrap( -1 )
		fgSizer11.Add( self.active_area_static_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		active_area_choiceChoices = []
		self.active_area_choice = wx.Choice( self.m_panel111, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, active_area_choiceChoices, 0 )
		self.active_area_choice.SetSelection( 0 )
		fgSizer11.Add( self.active_area_choice, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.active_area_rename_button = wx.BitmapButton( self.m_panel111, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_MISSING_IMAGE, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		fgSizer11.Add( self.active_area_rename_button, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		bSizer131.Add( fgSizer11, 1, wx.EXPAND, 5 )
		
		
		self.m_panel111.SetSizer( bSizer131 )
		self.m_panel111.Layout()
		bSizer131.Fit( self.m_panel111 )
		self.config_notebook.AddPage( self.m_panel111, u"A", False )
		self.m_panel12 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText31 = wx.StaticText( self.m_panel12, wx.ID_ANY, u"Spectrum", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )
		self.m_staticText31.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer15.Add( self.m_staticText31, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.express_spec_button = wx.Button( self.m_panel12, wx.ID_ANY, u"Express spec for frame pack", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.express_spec_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer15.Add( self.express_spec_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.aver_spec_button = wx.Button( self.m_panel12, wx.ID_ANY, u"Time averaged spectrum...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer15.Add( self.aver_spec_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel12.SetSizer( bSizer15 )
		self.m_panel12.Layout()
		bSizer15.Fit( self.m_panel12 )
		self.config_notebook.AddPage( self.m_panel12, u"S", False )
		self.m_panel13 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer151 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer13 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer13.AddGrowableCol( 1 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText32 = wx.StaticText( self.m_panel13, wx.ID_ANY, u"Screenshot options", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )
		self.m_staticText32.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizer13.Add( self.m_staticText32, 0, wx.ALL, 5 )
		
		self.scrshot_button = wx.Button( self.m_panel13, wx.ID_ANY, u"do it", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer13.Add( self.scrshot_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		bSizer151.Add( fgSizer13, 0, wx.EXPAND, 5 )
		
		fgSizer14 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer14.AddGrowableCol( 0 )
		fgSizer14.AddGrowableCol( 1 )
		fgSizer14.SetFlexibleDirection( wx.BOTH )
		fgSizer14.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.left_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Left", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.left_scrshot_check.SetValue(True) 
		fgSizer14.Add( self.left_scrshot_check, 0, wx.ALL, 5 )
		
		self.right_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Right", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer14.Add( self.right_scrshot_check, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.raw_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Raw image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.raw_scrshot_check.SetValue(True) 
		fgSizer14.Add( self.raw_scrshot_check, 0, wx.ALL, 5 )
		
		self.cur_view_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"View", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer14.Add( self.cur_view_scrshot_check, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.single_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Single", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.single_scrshot_check.SetValue(True) 
		fgSizer14.Add( self.single_scrshot_check, 0, wx.ALL, 5 )
		
		self.many_scrshot_check = wx.CheckBox( self.m_panel13, wx.ID_ANY, u"Time series", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		fgSizer14.Add( self.many_scrshot_check, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		bSizer151.Add( fgSizer14, 0, 0, 5 )
		
		
		self.m_panel13.SetSizer( bSizer151 )
		self.m_panel13.Layout()
		bSizer151.Fit( self.m_panel13 )
		self.config_notebook.AddPage( self.m_panel13, u"Sc", False )
		self.m_panel131 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer152 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText34 = wx.StaticText( self.m_panel131, wx.ID_ANY, u"View", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText34.Wrap( -1 )
		self.m_staticText34.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer152.Add( self.m_staticText34, 0, wx.ALL, 5 )
		
		
		self.m_panel131.SetSizer( bSizer152 )
		self.m_panel131.Layout()
		bSizer152.Fit( self.m_panel131 )
		self.config_notebook.AddPage( self.m_panel131, u"V", False )
		self.m_panel14 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer16 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText35 = wx.StaticText( self.m_panel14, wx.ID_ANY, u"Filter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )
		self.m_staticText35.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer16.Add( self.m_staticText35, 0, wx.ALL, 5 )
		
		self.m_staticText28 = wx.StaticText( self.m_panel14, wx.ID_ANY, u"Under construction...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )
		bSizer16.Add( self.m_staticText28, 0, wx.ALL, 5 )
		
		
		self.m_panel14.SetSizer( bSizer16 )
		self.m_panel14.Layout()
		bSizer16.Fit( self.m_panel14 )
		self.config_notebook.AddPage( self.m_panel14, u"F", False )
		self.m_panel15 = wx.Panel( self.config_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText27 = wx.StaticText( self.m_panel15, wx.ID_ANY, u"Moving processing area", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )
		self.m_staticText27.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer17.Add( self.m_staticText27, 0, wx.ALL, 5 )
		
		self.m_staticText29 = wx.StaticText( self.m_panel15, wx.ID_ANY, u"under construction...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )
		bSizer17.Add( self.m_staticText29, 0, wx.ALL, 5 )
		
		
		self.m_panel15.SetSizer( bSizer17 )
		self.m_panel15.Layout()
		bSizer17.Fit( self.m_panel15 )
		self.config_notebook.AddPage( self.m_panel15, u"M", False )
		
		fgSizer9.Add( self.config_notebook, 1, wx.EXPAND |wx.ALL, 2 )
		
		self.json_header_static_text = wx.StaticText( self.m_panel6, wx.ID_ANY, u"\"section\":{", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.json_header_static_text.Wrap( -1 )
		fgSizer9.Add( self.json_header_static_text, 0, wx.ALL|wx.ALIGN_BOTTOM, 2 )
		
		self.json_text = wx.TextCtrl( self.m_panel6, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		self.json_text.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 75, 90, 90, False, wx.EmptyString ) )
		
		fgSizer9.Add( self.json_text, 1, wx.ALL|wx.EXPAND, 2 )
		
		fgSizer10 = wx.FlexGridSizer( 1, 4, 0, 0 )
		fgSizer10.AddGrowableCol( 0 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.json_footer_static_text = wx.StaticText( self.m_panel6, wx.ID_ANY, u"}", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.json_footer_static_text.Wrap( -1 )
		fgSizer10.Add( self.json_footer_static_text, 0, wx.ALL, 2 )
		
		self.apply_json_button = wx.BitmapButton( self.m_panel6, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_TICK_MARK, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.apply_json_button.SetToolTipString( u"Apply" )
		
		fgSizer10.Add( self.apply_json_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.reset_json_button = wx.BitmapButton( self.m_panel6, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_UNDO, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.reset_json_button.SetToolTipString( u"Undo" )
		
		fgSizer10.Add( self.reset_json_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		self.json_defaults_button = wx.BitmapButton( self.m_panel6, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_HOME, wx.ART_MENU ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.json_defaults_button.SetToolTipString( u"Reset defaults" )
		
		fgSizer10.Add( self.json_defaults_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		
		fgSizer9.Add( fgSizer10, 1, wx.EXPAND, 5 )
		
		
		self.m_panel6.SetSizer( fgSizer9 )
		self.m_panel6.Layout()
		fgSizer9.Fit( self.m_panel6 )
		self.m_panel7 = wx.Panel( self.props_images_splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer9 = wx.BoxSizer( wx.VERTICAL )
		
		self.ab_splitter = wx.SplitterWindow( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D|wx.SP_NO_XP_THEME )
		self.ab_splitter.SetSashSize( 5 )
		self.ab_splitter.Bind( wx.EVT_IDLE, self.ab_splitterOnIdle )
		self.ab_splitter.SetMinimumPaneSize( 20 )
		
		self.a_window_panel = wx.Panel( self.ab_splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.a_bmp = wx.StaticBitmap( self.a_window_panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.a_bmp, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.a_footer_static_text = wx.StaticText( self.a_window_panel, wx.ID_ANY, u"A: input", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.a_footer_static_text.Wrap( -1 )
		self.a_footer_static_text.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 75, 90, 90, False, wx.EmptyString ) )
		
		bSizer2.Add( self.a_footer_static_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.a_window_panel.SetSizer( bSizer2 )
		self.a_window_panel.Layout()
		bSizer2.Fit( self.a_window_panel )
		self.m_panel2 = wx.Panel( self.ab_splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.b_bmp = wx.StaticBitmap( self.m_panel2, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.b_bmp, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.b_footer_static_text = wx.StaticText( self.m_panel2, wx.ID_ANY, u"B: output", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.b_footer_static_text.Wrap( -1 )
		self.b_footer_static_text.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 75, 90, 90, False, wx.EmptyString ) )
		
		bSizer3.Add( self.b_footer_static_text, 0, wx.ALL, 5 )
		
		
		self.m_panel2.SetSizer( bSizer3 )
		self.m_panel2.Layout()
		bSizer3.Fit( self.m_panel2 )
		self.ab_splitter.SplitVertically( self.a_window_panel, self.m_panel2, 350 )
		bSizer9.Add( self.ab_splitter, 1, wx.EXPAND, 5 )
		
		
		self.m_panel7.SetSizer( bSizer9 )
		self.m_panel7.Layout()
		bSizer9.Fit( self.m_panel7 )
		self.props_images_splitter.SplitVertically( self.m_panel6, self.m_panel7, 250 )
		bSizer1.Add( self.props_images_splitter, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.corner_menu = wx.Menu()
		self.open_menu_top = wx.Menu()
		self.open_menu = wx.MenuItem( self.open_menu_top, wx.ID_ANY, u"Open project...", wx.EmptyString, wx.ITEM_NORMAL )
		self.open_menu.SetBitmap( wx.NullBitmap )
		self.open_menu_top.AppendItem( self.open_menu )
		
		self.open_video_menu = wx.MenuItem( self.open_menu_top, wx.ID_ANY, u"Open video file...", wx.EmptyString, wx.ITEM_NORMAL )
		self.open_menu_top.AppendItem( self.open_video_menu )
		
		self.open_spec_menu = wx.MenuItem( self.open_menu_top, wx.ID_ANY, u"Open spectrum...", wx.EmptyString, wx.ITEM_NORMAL )
		self.open_menu_top.AppendItem( self.open_spec_menu )
		
		self.corner_menu.AppendSubMenu( self.open_menu_top, u"Open" )
		
		self.save_menu = wx.MenuItem( self.corner_menu, wx.ID_ANY, u"Save project", wx.EmptyString, wx.ITEM_NORMAL )
		self.save_menu.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE, wx.ART_MENU ) )
		self.corner_menu.AppendItem( self.save_menu )
		
		self.save_as_menu = wx.MenuItem( self.corner_menu, wx.ID_ANY, u"Save project as...", wx.EmptyString, wx.ITEM_NORMAL )
		self.save_as_menu.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE_AS, wx.ART_MENU ) )
		self.corner_menu.AppendItem( self.save_as_menu )
		
		self.corner_menu.AppendSeparator()
		
		self.about_menu = wx.MenuItem( self.corner_menu, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.corner_menu.AppendItem( self.about_menu )
		
		self.links_menu = wx.MenuItem( self.corner_menu, wx.ID_ANY, u"Userful links", wx.EmptyString, wx.ITEM_NORMAL )
		self.corner_menu.AppendItem( self.links_menu )
		
		self.Bind( wx.EVT_RIGHT_DOWN, self.MainVideoFrameOnContextMenu ) 
		
		self.temp_images_monitoring_timer = wx.Timer()
		self.temp_images_monitoring_timer.SetOwner( self, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self._close_func )
		self.Bind( wx.EVT_SIZE, self._size_func )
		self.Bind( wx.EVT_TOOL, self._menu_tool_func, id = self.menu_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._preview_tool_func, id = self.preview_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._proc_tool_func, id = self.proc_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._view_step_tool_func, id = self.view_step_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._prev_tool_func, id = self.prev_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._next_tool_func, id = self.next_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._jump_frame_tool_func, id = self.jump_frame_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._jump_time_tool_func, id = self.jump_time_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._zoom_tool_func, id = self.zoom_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._scrshot_button_func, id = self.scrshot_tool.GetId() )
		self.Bind( wx.EVT_TOOL, self._points_tool_func, id = self.points_tool.GetId() )
		self.config_notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self._config_notebook_changed_func )
		self.config_notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGING, self._config_notebook_changing_func )
		self.source_button.Bind( wx.EVT_BUTTON, self._source_button_func )
		self.camera_list_button.Bind( wx.EVT_BUTTON, self._camera_list_button_func )
		self.pick_horizont_button.Bind( wx.EVT_BUTTON, self._pick_horizont_button_func )
		self.simple_proj_button.Bind( wx.EVT_BUTTON, self._simple_proj_button_func )
		self.select_area_button.Bind( wx.EVT_BUTTON, self._select_area_button_func )
		self.select_multiple_areas_button.Bind( wx.EVT_BUTTON, self._select_multiple_areas_button_func )
		self.express_spec_button.Bind( wx.EVT_BUTTON, self._express_spec_button_func )
		self.aver_spec_button.Bind( wx.EVT_BUTTON, self._aver_spec_button_func )
		self.scrshot_button.Bind( wx.EVT_BUTTON, self._scrshot_button_func )
		self.left_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.right_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.raw_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.cur_view_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.single_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.many_scrshot_check.Bind( wx.EVT_CHECKBOX, self._checkbox_like_radio )
		self.json_text.Bind( wx.EVT_TEXT, self._json_text_func )
		self.apply_json_button.Bind( wx.EVT_BUTTON, self._apply_json_button_func )
		self.reset_json_button.Bind( wx.EVT_BUTTON, self._reset_json_button_func )
		self.json_defaults_button.Bind( wx.EVT_BUTTON, self._json_defaults_button_func )
		self.ab_splitter.Bind( wx.EVT_SPLITTER_SASH_POS_CHANGED, self._size_func )
		self.a_footer_static_text.Bind( wx.EVT_LEFT_DCLICK, self._a_footer_static_text_dclick )
		self.b_footer_static_text.Bind( wx.EVT_LEFT_DCLICK, self._b_footer_static_text_dclick )
		self.Bind( wx.EVT_MENU, self._open_menu_func, id = self.open_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._open_video_menu_func, id = self.open_video_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._load_spec_button_func, id = self.open_spec_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._save_menu_func, id = self.save_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._save_as_menu_func, id = self.save_as_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._about_menu_func, id = self.about_menu.GetId() )
		self.Bind( wx.EVT_MENU, self._links_menu_func, id = self.links_menu.GetId() )
		self.Bind( wx.EVT_TIMER, self._temp_images_monitoring_timer_func, id=wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def _close_func( self, event ):
		event.Skip()
	
	def _size_func( self, event ):
		event.Skip()
	
	def _menu_tool_func( self, event ):
		event.Skip()
	
	def _preview_tool_func( self, event ):
		event.Skip()
	
	def _proc_tool_func( self, event ):
		event.Skip()
	
	def _view_step_tool_func( self, event ):
		event.Skip()
	
	def _prev_tool_func( self, event ):
		event.Skip()
	
	def _next_tool_func( self, event ):
		event.Skip()
	
	def _jump_frame_tool_func( self, event ):
		event.Skip()
	
	def _jump_time_tool_func( self, event ):
		event.Skip()
	
	def _zoom_tool_func( self, event ):
		event.Skip()
	
	def _scrshot_button_func( self, event ):
		event.Skip()
	
	def _points_tool_func( self, event ):
		event.Skip()
	
	def _config_notebook_changed_func( self, event ):
		event.Skip()
	
	def _config_notebook_changing_func( self, event ):
		event.Skip()
	
	def _source_button_func( self, event ):
		event.Skip()
	
	def _camera_list_button_func( self, event ):
		event.Skip()
	
	def _pick_horizont_button_func( self, event ):
		event.Skip()
	
	def _simple_proj_button_func( self, event ):
		event.Skip()
	
	def _select_area_button_func( self, event ):
		event.Skip()
	
	def _select_multiple_areas_button_func( self, event ):
		event.Skip()
	
	def _express_spec_button_func( self, event ):
		event.Skip()
	
	def _aver_spec_button_func( self, event ):
		event.Skip()
	
	
	def _checkbox_like_radio( self, event ):
		event.Skip()
	
	
	
	
	
	
	def _json_text_func( self, event ):
		event.Skip()
	
	def _apply_json_button_func( self, event ):
		event.Skip()
	
	def _reset_json_button_func( self, event ):
		event.Skip()
	
	def _json_defaults_button_func( self, event ):
		event.Skip()
	
	
	def _a_footer_static_text_dclick( self, event ):
		event.Skip()
	
	def _b_footer_static_text_dclick( self, event ):
		event.Skip()
	
	def _open_menu_func( self, event ):
		event.Skip()
	
	def _open_video_menu_func( self, event ):
		event.Skip()
	
	def _load_spec_button_func( self, event ):
		event.Skip()
	
	def _save_menu_func( self, event ):
		event.Skip()
	
	def _save_as_menu_func( self, event ):
		event.Skip()
	
	def _about_menu_func( self, event ):
		event.Skip()
	
	def _links_menu_func( self, event ):
		event.Skip()
	
	def _temp_images_monitoring_timer_func( self, event ):
		event.Skip()
	
	def props_images_splitterOnIdle( self, event ):
		self.props_images_splitter.SetSashPosition( 250 )
		self.props_images_splitter.Unbind( wx.EVT_IDLE )
	
	def ab_splitterOnIdle( self, event ):
		self.ab_splitter.SetSashPosition( 350 )
		self.ab_splitter.Unbind( wx.EVT_IDLE )
	
	def MainVideoFrameOnContextMenu( self, event ):
		self.PopupMenu( self.corner_menu, event.GetPosition() )
		

###########################################################################
## Class ZoomDlg
###########################################################################

class ZoomDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Zoom and movement", pos = wx.DefaultPosition, size = wx.Size( 200,200 ), style = wx.DEFAULT_DIALOG_STYLE )
		
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
		
		
		bSizer9.Add( gSizer12, 0, wx.EXPAND, 5 )
		
		fgSizer13 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer13.AddGrowableCol( 1 )
		fgSizer13.SetFlexibleDirection( wx.BOTH )
		fgSizer13.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.es = wx.Button( self, wx.ID_ANY, u"1:1", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.es.SetToolTipString( u"Do for left panel" )
		
		fgSizer13.Add( self.es, 0, wx.ALL, 5 )
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Сброс", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer13.Add( self.m_staticText25, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_button15 = wx.Button( self, wx.ID_ANY, u"1:1", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.m_button15.SetToolTipString( u"Do for the right panel" )
		
		fgSizer13.Add( self.m_button15, 0, wx.ALL, 5 )
		
		self.a_to_corner_button = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.a_to_corner_button.SetToolTipString( u"Do for left panel" )
		
		fgSizer13.Add( self.a_to_corner_button, 0, wx.ALL, 5 )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"Move to corner", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer13.Add( self.m_staticText26, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.b_to_corner_button = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_GO_UP, wx.ART_BUTTON ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.b_to_corner_button.SetToolTipString( u"Do for the right panel" )
		
		fgSizer13.Add( self.b_to_corner_button, 0, wx.ALL, 5 )
		
		
		bSizer9.Add( fgSizer13, 1, wx.EXPAND, 5 )
		
		self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, u"Use the mouse to move and zoom the image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( 180 )
		bSizer9.Add( self.m_staticText30, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		self.SetSizer( bSizer9 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close_func )
		self.zoom_a_choice.Bind( wx.EVT_CHOICE, self.zoom_a_choice_func )
		self.zoom_b_choice.Bind( wx.EVT_CHOICE, self.zoom_b_choice_func )
		self.es.Bind( wx.EVT_BUTTON, self.reset_a_button_func )
		self.m_button15.Bind( wx.EVT_BUTTON, self.reset_b_button_func )
		self.a_to_corner_button.Bind( wx.EVT_BUTTON, self.a_to_corner_button_func )
		self.b_to_corner_button.Bind( wx.EVT_BUTTON, self.b_to_corner_button_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close_func( self, event ):
		event.Skip()
	
	def zoom_a_choice_func( self, event ):
		event.Skip()
	
	def zoom_b_choice_func( self, event ):
		event.Skip()
	
	def reset_a_button_func( self, event ):
		event.Skip()
	
	def reset_b_button_func( self, event ):
		event.Skip()
	
	def a_to_corner_button_func( self, event ):
		event.Skip()
	
	def b_to_corner_button_func( self, event ):
		event.Skip()
	

###########################################################################
## Class SelDlg
###########################################################################

class SelDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 180,250 ), style = wx.CAPTION )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer8 = wx.BoxSizer( wx.VERTICAL )
		
		self.info_static_text = wx.StaticText( self, wx.ID_ANY, u"Select...", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
		self.info_static_text.Wrap( 180 )
		bSizer8.Add( self.info_static_text, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		self.done_button = wx.Button( self, wx.ID_ANY, u"DONE", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		self.done_button.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		bSizer8.Add( self.done_button, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.del_button = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		bSizer8.Add( self.del_button, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		
		self.cancel_button = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		bSizer8.Add( self.cancel_button, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT|wx.LEFT, 5 )
		
		
		self.SetSizer( bSizer8 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self._cancel_button_func )
		self.done_button.Bind( wx.EVT_BUTTON, self._done_button_func )
		self.del_button.Bind( wx.EVT_BUTTON, self._del_button_func )
		self.cancel_button.Bind( wx.EVT_BUTTON, self._cancel_button_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def _cancel_button_func( self, event ):
		event.Skip()
	
	def _done_button_func( self, event ):
		event.Skip()
	
	def _del_button_func( self, event ):
		event.Skip()
	
	

###########################################################################
## Class SourceDlg
###########################################################################

class SourceDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Video data source", pos = wx.DefaultPosition, size = wx.Size( 620,400 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer6 = wx.BoxSizer( wx.VERTICAL )
		
		self.source_type_choice = wx.Choicebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.CHB_DEFAULT )
		self.m_panel7 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer2 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer2.AddGrowableCol( 1 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText4 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Video file:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )
		fgSizer2.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.video_filename_text = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.video_filename_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.browse_video_file = wx.Button( self.m_panel7, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer2.Add( self.browse_video_file, 0, wx.ALL, 5 )
		
		self.m_staticText33 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Temp files:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )
		fgSizer2.Add( self.m_staticText33, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		temp_path_choiceChoices = [ u"keep them in the standart system folder", u"keep them in a folder, given below as a 'Path to images'" ]
		self.temp_path_choice = wx.Choice( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, temp_path_choiceChoices, 0 )
		self.temp_path_choice.SetSelection( 0 )
		fgSizer2.Add( self.temp_path_choice, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer7.Add( fgSizer2, 1, wx.EXPAND, 5 )
		
		
		self.m_panel7.SetSizer( bSizer7 )
		self.m_panel7.Layout()
		bSizer7.Fit( self.m_panel7 )
		self.source_type_choice.AddPage( self.m_panel7, u"Use ffmpeg with defaul parameters", True )
		self.m_panel8 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		fgSizer21 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer21.AddGrowableCol( 1 )
		fgSizer21.SetFlexibleDirection( wx.BOTH )
		fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText41 = wx.StaticText( self.m_panel8, wx.ID_ANY, u"Command line:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText41.Wrap( -1 )
		fgSizer21.Add( self.m_staticText41, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.loader_cmd_text = wx.TextCtrl( self.m_panel8, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer21.Add( self.loader_cmd_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.auto_cmd_button = wx.Button( self.m_panel8, wx.ID_ANY, u"A", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.auto_cmd_button.SetToolTipString( u"Fill in default values" )
		
		fgSizer21.Add( self.auto_cmd_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		fgSizer21.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		gSizer72 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.loader_cmd_help = wx.HyperlinkCtrl( self.m_panel8, wx.ID_ANY, u"Help", wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
		gSizer72.Add( self.loader_cmd_help, 0, wx.ALL, 5 )
		
		self.use_shell_check = wx.CheckBox( self.m_panel8, wx.ID_ANY, u"shell", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer72.Add( self.use_shell_check, 0, wx.ALL, 5 )
		
		
		fgSizer21.Add( gSizer72, 1, wx.EXPAND, 5 )
		
		
		self.m_panel8.SetSizer( fgSizer21 )
		self.m_panel8.Layout()
		fgSizer21.Fit( self.m_panel8 )
		self.source_type_choice.AddPage( self.m_panel8, u"Use ffmpeg with a custom command line", False )
		self.m_panel9 = wx.Panel( self.source_type_choice, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.source_type_choice.AddPage( self.m_panel9, u"We have just a folder with images", False )
		bSizer6.Add( self.source_type_choice, 0, wx.ALL|wx.EXPAND, 5 )
		
		fgSizer8 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer8.AddGrowableCol( 1 )
		fgSizer8.SetFlexibleDirection( wx.BOTH )
		fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.pic_path_static_text = wx.StaticText( self, wx.ID_ANY, u"Path to images:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pic_path_static_text.Wrap( -1 )
		fgSizer8.Add( self.pic_path_static_text, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.pic_path_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer8.Add( self.pic_path_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.pic_path_browse_button = wx.Button( self, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		fgSizer8.Add( self.pic_path_browse_button, 0, wx.ALL, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.pic_path_comment_static_text = wx.StaticText( self, wx.ID_ANY, u"Give a template in the form of:  my_path/img%04d.bmp", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pic_path_comment_static_text.Wrap( -1 )
		fgSizer8.Add( self.pic_path_comment_static_text, 0, wx.ALL, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"Frames range:", wx.DefaultPosition, wx.DefaultSize, 0 )
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
		
		self.max_finish_sttext = wx.StaticText( self, wx.ID_ANY, u"--> Max", wx.DefaultPosition, wx.DefaultSize, 0 )
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
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Frame pack length:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		fgSizer8.Add( self.m_staticText25, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		gSizer5 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.pack_len_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer5.Add( self.pack_len_text, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.overlap_check = wx.CheckBox( self, wx.ID_ANY, u"overlap 1/2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.overlap_check.SetValue(True) 
		gSizer5.Add( self.overlap_check, 0, wx.ALL, 5 )
		
		
		fgSizer8.Add( gSizer5, 1, wx.EXPAND, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		fgSizer8.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_staticText35 = wx.StaticText( self, wx.ID_ANY, u"This parameter defines the size of the Fourier transform over time as well.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText35.Wrap( -1 )
		fgSizer8.Add( self.m_staticText35, 0, wx.ALL, 5 )
		
		
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
		self.browse_video_file.Bind( wx.EVT_BUTTON, self._browse_video_file_func )
		self.temp_path_choice.Bind( wx.EVT_CHOICE, self.hide_show_items )
		self.auto_cmd_button.Bind( wx.EVT_BUTTON, self.auto_cmd_button_func )
		self.loader_cmd_help.Bind( wx.EVT_HYPERLINK, self.loader_cmd_help_func )
		self.pic_path_browse_button.Bind( wx.EVT_BUTTON, self._pic_path_browse_button_func )
		self.max_finish_check.Bind( wx.EVT_CHECKBOX, self.hide_show_items )
		self.m_sdbSizer1Apply.Bind( wx.EVT_BUTTON, self.apply_button_func )
		self.m_sdbSizer1Cancel.Bind( wx.EVT_BUTTON, self.close_func )
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
	
	def _browse_video_file_func( self, event ):
		event.Skip()
	
	def hide_show_items( self, event ):
		event.Skip()
	
	def auto_cmd_button_func( self, event ):
		event.Skip()
	
	def loader_cmd_help_func( self, event ):
		event.Skip()
	
	def _pic_path_browse_button_func( self, event ):
		event.Skip()
	
	
	def apply_button_func( self, event ):
		event.Skip()
	
	
	def ok_button_func( self, event ):
		event.Skip()
	

###########################################################################
## Class PointsDlg
###########################################################################

class PointsDlg ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Points", pos = wx.DefaultPosition, size = wx.Size( 250,500 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		self.coords_text = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.TE_MULTILINE )
		bSizer17.Add( self.coords_text, 1, wx.ALL|wx.EXPAND, 5 )
		
		gSizer8 = wx.GridSizer( 0, 2, 0, 0 )
		
		self.a2b_button = wx.Button( self, wx.ID_ANY, u"A -> B", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.a2b_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.b2a_button = wx.Button( self, wx.ID_ANY, u"A <- B", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.b2a_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.sel_a_button = wx.Button( self, wx.ID_ANY, u"Select on A", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.sel_a_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.sel_b_button = wx.Button( self, wx.ID_ANY, u"Select on В", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.sel_b_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_button23 = wx.Button( self, wx.ID_ANY, u"Compute...", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.m_button23, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.close_button = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		gSizer8.Add( self.close_button, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer17.Add( gSizer8, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer17 )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.close_func )
		self.a2b_button.Bind( wx.EVT_BUTTON, self._a2b_button_func )
		self.b2a_button.Bind( wx.EVT_BUTTON, self._b2a_button_func )
		self.sel_a_button.Bind( wx.EVT_BUTTON, self._sel_a_button_func )
		self.sel_b_button.Bind( wx.EVT_BUTTON, self._sel_b_button_func )
		self.close_button.Bind( wx.EVT_BUTTON, self.close_func )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def close_func( self, event ):
		event.Skip()
	
	def _a2b_button_func( self, event ):
		event.Skip()
	
	def _b2a_button_func( self, event ):
		event.Skip()
	
	def _sel_a_button_func( self, event ):
		event.Skip()
	
	def _sel_b_button_func( self, event ):
		event.Skip()
	
	

