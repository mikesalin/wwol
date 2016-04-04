swig -python transform_frame.i
cc -Wfatal-errors -fPIC -fopenmp -O3 transform_frame.c transform_frame_wrap.c \
    -I/usr/include/python2.7 -shared -o _transform_frame.so

