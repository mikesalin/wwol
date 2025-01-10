# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Mikhail Salin. Contacts: mikesalin@gmail.com
# All rights reserved.
#

from py2exe import freeze

freeze(console = [{'script':'rec_wwol_with_menu.py'}],
       windows=[ ],
       data_files=None,
       zipfile='library.zip',
       options = { #'excludes' : ['Tkinter', 'Tkconstants']
                  },
       version_info={}
       )

# https://stackoverflow.com/questions/68492789/how-to-resolve-winerror-87-running-py2exe-on-win-10
# https://github.com/py2exe/py2exe/issues/76
# https://github.com/pyinstaller/pyinstaller/issues/2162
# On Window 10 I experienced problems acquiring video when ffmpeg was launched
# from wwol_rec_act script, being launched from command line i.e. like 
#     python wwol_rec_act.py
# Same problems with the frozen version of this. So don’t use this script.
# Launching interpreter, writing 'import...' manually and so on, and so for
# worked fine.


