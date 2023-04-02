WIND-WAVES OPTIC LAB  (WWOL)

This software is for processing video of waves on a sea surface in any of common
format in order to compute a 3D wind waves spectrum.

PREREQUISITES:
    python 3 ( + developer package)
    numpy    ( + get numpy.i, check below how to do it)
    scipy
    wxPython
    wxFormBuilder (not needed if you won't edit GUI)
    Json Schema
    swig
    py2exe (windows only)
    ffmpeg  (this is a standalone application)
    gnuplot (this is a standalone application)

INSTALLATION AND RUNNING:
  The most general way:  
    1) Install prerequisites from the list above and according to your OS way

    2) Precompile:
        python3 setup.py build_ext --inplace

    NOTE: a) Windows users should run from the appropriate MS Visual C shell;
          b) somtimes you call just 'python' instead of 'python3'
             it depends on how you have configured your OS
    
    3) Run & enjoy:
        python3 start_wwol.py        
  
  MacOS:
    Refer to snippets/macos_install.txt
  
  Windows users:
    Download built .exe from here:
    (link is comming soon)
    Don't forget to install ffmpeg and gnuplot before running our .exe

WINDOWS, building exe:
    From MS Visual C shell do:
    python3 setup.py py2exe

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
    1) WINDOWS USERS:
      * check that ffmpeg's bin folder was added to your PATH
        otherwise edit variable 'FFMPEG_BIN_PATH' in 'wwol/engine/loading.py'
        to put the full path into it;           
      * check that gnuplot's binary folder was added to your PATH
        (no override for this)
        
    2) GETTING numpy.i:
        Short story:
          Run this script, in most cases it will succeed:
          python3 get_numpy_i_now.py

        Long story:
          According to this peice of documentation:
          https://numpy.org/doc/stable/reference/swig.interface-file.html
          the desired file 'numpy.i' is located in the numpy folder, 
          'tools/swig/' subfolder. 
          However it may be excluded from your installation.
          In this case you should download it from the Internet repo.
          Anyway, a copy of 'numpy.i' should appear in 'wol/engine/c_part/'

    3) Linux users: check if your distro provides 'ffmpeg' or 'avconv'
       In case of using 'avconf', make '.wwol.config' file in your home folder
       and put the following text in it:
    {
      "ffmpeg":{
        "FFMPEG_BIN_PATH":"",
        "FFMPEG_NAME":"avconv",
        "FFPROBE_NAME":"avprobe"
      }
    }
    

QUESTIONS:
    mikesalin@gmail.com
    mikesalin@ipfran.ru
    Mike Salin
    
    
