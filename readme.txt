This software is for processing video of waves on a sea surface in any of common
format in order to compute a 3D wind waves spectum.

PREREQUISITES:
    python 2.7  ( + dev package)
    numpy   ( + get numpy.i, check below how to do it)
    scipy
    wxPython
    wxFormBuilder (not needed if you won't edit GUI)
    Json Schema
    swig
    py2exe (windows only)
    ffmpeg (standalone application)
    gnuplot (standalone application)

LINUX & WINDOWS, running from sources:
    1) Precompile:
        python setup.py build_ext --inplace

        NOTE: windows users should run from the appropriate MS Visual C shell
    
    2) Run & enjoy:
        python start_wwol.py        

WINDOWS, building exe:
    From MS Visual C shell do:
    python setup.py py2exe

HOW TO USE:
    1) The following 'video lesson' is the only form docs that we have:
       (coming soon)
       
    2) Data files, used in samples, are located in:
       (coming soon)
       They are kept separately in order to conserve light weight of the git repo.
    
    3) Underlying theory is explained in arXiv:1303.5248 
           https://arxiv.org/abs/1303.5248
           https://doi.org/10.48550/arXiv.1303.5248
       If you find WWOL helpful for your research, please cite the above paper
       or it's official journal version:
           Radiophysics and Quantum Electronics. 58(2015), No.2, P.114-123 
           https://doi.org/10.1007/s11141-015-9586-1
    
POSSIBLE ISSUES: 
    1) WINDOW USERS:
      * check that ffmpeg's bin folder was added to your PATH
        otherwize edit variable 'FFMPEG_BIN_PATH' in 'wwol/engine/loading.py'
        to put the full path into it;           
      * check that gnuplot's binary folder was added to your PATH
        (no override for this)
        
    2) GETTING numpy.i:
        python wwol/setup_/numpy_i_getter.py
        mv numpy.i wwol/engine/c_part/
    
    3) Linux users: does your distro provides 'ffmpeg' or 'avconv' ?
       In case of using 'avconf', make '.wwol.config' file in your home folder
       and put the following text in it:
    {
      "ffmpeg":{
        "FFMPEG_BIN_PATH":"",
        "FFMPEG_NAME":"avconv",
        "FFPROBE_NAME":"avprobe"
      }
    }
    
    4) No compatibility with python3 was tested. Sorry to say.

QUESTIONS:
    mikesalin@gmail.com
    Mike Salin
    
