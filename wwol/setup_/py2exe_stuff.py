# -*- coding: utf-8 -*-
"Для сборки exe-шников под Windows с помощью py2exe"

# Для комплиляции с py2exe требуется модификация исходников библиотек Питона:
# Lib\site-packages\repoze.lru-0.6-py2.6.egg\repoze\__init__.py :
# import sys
# if not hasattr(sys, 'frozen'):
#     __import__('pkg_resources').declare_namespace(__name__)

import os
import sys
import shutil
import jsonschema
from py2exe.build_exe import py2exe as build_exe


sys.path.append("C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\"
                "Redist\\X86\\Microsoft.VC90.CRT")

def setup_kwargs():
    d = {'windows': ['start_wwol.py'],
         'options': {'py2exe' : {'excludes' : ['Tkinter',
                                               'Tkconstants',
                                               'scipy.sparse'
                                              ]
                                 }
                    },
         'cmdclass': {"py2exe": JsonSchemaCollector},
         'zipfile': None
    }
    return d


class JsonSchemaCollector(build_exe):
   """
   This class Adds jsonschema files draft3.json and draft4.json to
   the list of compiled files so it will be included in the zipfile.
   http://stackoverflow.com/questions/30942612/py2exe-not-recognizing-jsonschema
   """

   def copy_extensions(self, extensions):
        build_exe.copy_extensions(self, extensions)

        # Define the data path where the files reside.
        data_path = os.path.join(jsonschema.__path__[0], 'schemas')

        # Create the subdir where the json files are collected.
        media = os.path.join('jsonschema', 'schemas')
        full = os.path.join(self.collect_dir, media)
        self.mkpath(full)

        # Copy the json files to the collection dir. Also add the copied file
        # to the list of compiled files so it will be included in the zipfile.
        for name in os.listdir(data_path):
            file_name = os.path.join(data_path, name)
            self.copy_file(file_name, os.path.join(full, name))
            self.compiled_files.append(os.path.join(media, name))

            
