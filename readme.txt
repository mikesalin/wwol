PREREQUISITES:
    python 2.7  (or 2.6, + dev package)
    numpy   ( + get numpy.i or see note bellow)
    scipy
    wxPython
    wxFormBuilder (not needed if you won't edit GUI)
    Json Schema
    swig
    py2exe (windows only)
    ffmpeg (standalone application)
    gnuplot (standalone application)

LINUX & WINDOWS, running from sources:
    python setup.py build_ext --inplace
    python start_wwol.py    
    
    NOTE: on windows run from the appropriate MS Visual C shell

WINDOWS, building exe:
    (from MS Visual C shell)
    python setup.py py2exe
    
GETTING numpy.i:
    python wwol/setup_/numpy_i_getter.py
    mv numpy.i wwol/engine/c_part/
    
    
