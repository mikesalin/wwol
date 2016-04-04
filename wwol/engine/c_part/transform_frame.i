%module transform_frame
%{
#define SWIG_FILE_WITH_INIT
#include "transform_frame.h"
%}

%include "numpy.i"
%init %{
import_array();
%}

%apply (unsigned char *IN_ARRAY3, int DIM1, int DIM2, int DIM3) {(const unsigned char *pcImg, int H, int W, int color_depth)}
%apply (double* INPLACE_ARRAY2, int DIM1, int DIM2) {(double* pdFrame, int Ny_in, int Nx_in)}

%include "transform_frame.h"

