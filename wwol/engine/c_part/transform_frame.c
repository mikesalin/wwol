// TRANSFORM_FRAME_C : оберкта над частью старой программы -- функция коррекции
// перспективы

#include <math.h>
#include <malloc.h>

#include "transform_frame.h"

#define true 1
#define false 0

/* TRANSFORM_FRAME: коррекция перспектривы
Эта функция имеет Питоновскую обертку, сделанную SWIG-ом.
Обертка описана (будет описана) в __init__.py */

TransformFrameOutputParam transform_frame(
    double* pdFrame,            // Выход
    int Ny_in,                  // Размер выходного массива
    int Nx_in,                  // ( _in потому что он вход для Фурье)
    const unsigned char *pcImg, // Вход в формате RGB
    int H,                      // Размер входного массива
    int W,
    int color_dim,              // пока поддерживается только color_dim=3 (RGB)
    double A,                   // коэфициенты для проецирования
    double B,
    double C,
    int X1,                     // левый верхний и...
    int Y1,
    int X2,                     // ...правый нижний угол трапеции
    int Y2) {

// заметьте  здесь X1, Y1, X2, Y2 -- углы трапеции,
// в config -- углы описанного прямоугольник
                     
/*Transform in quasi-math form:
1) original frame (WxH) -> orig. *resize  (2*W2c x 2*H2c)  [deprecated]
2) trapec X1,Y1 x X2,Y2 -> Lx x Ly in meters (virtualy)
3) Lx x Ly -> Nx x Ny discreet
*/

TransformFrameOutputParam rv;
rv.flags = 0;

//calculated once
const double pMyTask_resizex = 1.0, pMyTask_resizey = 1.0;
double inv_resizex=1.0/pMyTask_resizex, inv_resizey=1.0/pMyTask_resizey;
int H2=H/2, W2=W/2;
double H2c=H2*pMyTask_resizey, W2c=W2*pMyTask_resizex;
double Lx, Ly; // physical size of X1,Y1 x X2,Y2 in meters
Lx=(X2-W2c)/(A* (H2c-Y2) + B ) - (X1-W2c)/(A* (H2c-Y1) + B );
Ly=fabs( (H2c-Y2)/(C*(A* (H2c-Y2) + B )) - (H2c-Y1)/(C*(A* (H2c-Y1) + B )) );
double Lx_Nx=Lx/(1.0*Nx_in), Ly_Ny=Ly/(1.0*Ny_in);
rv.Lx = Lx;
rv.Ly = Ly;
//left-top corner of area in meters 
double xm1=(X1-W2c)/(A* (H2c-Y1) + B ) , ym1=(H2c-Y1)/(C*(A* (H2c-Y1) + B ));
double dnorm=1.0/sqrt(3.0);

//веса, размер массивов с запасом
int NThr;
#pragma omp parallel
 {
  #pragma omp master
    {NThr=omp_get_num_threads();   }
 }
double *pdWX_buf=(double*)malloc(Nx_in*8*NThr),
   *pdWY_buf=(double*)malloc(Ny_in*8*NThr);
double *pdWX, *pdWY; 
int nOutOfBounds_glob=0;

//loop by new coordinates
int nx,ny; 
#pragma omp parallel default(shared) private(nx,ny,pdWX,pdWY)
{
pdWX=pdWX_buf+ omp_get_thread_num()*Nx_in;
pdWY=pdWY_buf+ omp_get_thread_num()*Ny_in;
#pragma omp for
for (ny=0; ny<Ny_in; ny++) 
  {
  //calculationg source area Y (we assume it is rect):
   int Ysrc[2], ppp; double Qy[2], y_ppp[2]; //Qy - дробные части
   for (ppp=0; ppp<2; ppp++)
     {//nx,ny -> meters      
      double y=((double)ny-0.5+ppp)*Ly_Ny+ym1-Ly;      
      //meter -> resized pixels
      double y_=y*B*C/(1.0-C*A*y); y_ppp[ppp]=y_;
      //resized pixels -> orig. pixels
      double a=H2 - y_*inv_resizey;
      double af=floor(a);
      Qy[ppp]=a-af;
      Ysrc[ppp]=af; 
     }             
   
   int bOutOfBounds = false;
   if (Ysrc[0]>=H) {Ysrc[0]=H-1; bOutOfBounds=true;}   
   if (Ysrc[1]<0) {Ysrc[1]=0; bOutOfBounds=true;}
   if ( bOutOfBounds ) 
     {
      #pragma omp atomic
      nOutOfBounds_glob|=1;
     }
  
  //веса для крайник точек
   if( Ysrc[1]<=Ysrc[0] )
     {int ry=Ysrc[0]-Ysrc[1]+1;
      pdWY[0]=1-Qy[1]; pdWY[ry-1]=Qy[0];       
      for (ppp=1; ppp<=ry-2; ppp++) pdWY[ppp]=1.0;
     } 
     
  //цикл по X
  for (nx=0; nx<Nx_in; nx++)
  {//dest: rect nx+/-0.5, ny+/-0.5   

   //calculationg source area X:
   int Xsrc[2];  double Qx[2];
   for (ppp=0; ppp<2; ppp++)
     {//nx,ny -> meters      
      double x=((double)nx-0.5+ppp)*Lx_Nx+xm1;
      //meter -> resized pixels
      double x_=x*(A*y_ppp[ppp]+B);            
      //resized pixels -> orig. pixels
      double a=W2 + x_*inv_resizex;
      double af=floor(a);
      Qx[ppp]=a-af;
      Xsrc[ppp]=af;      
     }             
   
   int bOutOfBounds=false;
   if (Xsrc[0]<0) {Xsrc[0]=0; Qx[0]=0; bOutOfBounds=true;}
   if (Xsrc[1]>=W) {Xsrc[1]=W-1; Qx[1]=1; bOutOfBounds=true;};
   if ( bOutOfBounds ) 
     {
      #pragma omp atomic
      nOutOfBounds_glob|=1;
     }
   
   //веса для крайник точек
   if( (Xsrc[0]<=Xsrc[1]) && (Ysrc[1]<=Ysrc[0]) )
     {int rx=Xsrc[1]-Xsrc[0]+1; //чилсо используемых элементов в pdWx
      pdWX[0]=1-Qx[0]; pdWX[rx-1]=Qx[1];  
      for (ppp=1; ppp<=rx-2; ppp++) pdWX[ppp]=1.0; 
     } 
              
   //Summ in this area (after, it should be weighted)
   int X,Y;  double U=0, S=0;
   for (Y=Ysrc[1]; Y<=Ysrc[0]; Y++)   
     {
      int ofs=Y*W;
      for (X=Xsrc[0]; X<=Xsrc[1]; X++) 
        {                       
         int ofs_=3*(ofs+X);
         int rr=pcImg[ofs_], gg=pcImg[ofs_+1], bb=pcImg[ofs_+2];
         double W = pdWX[X-Xsrc[0]]*pdWY[Y-Ysrc[1]]; //*...
         U += ( (int)(rr+gg+bb) )*W;
         S+=W;
        }
     }        
   pdFrame[ny*Nx_in+nx]=(S>1e-6)?( U/S ):(0); 
  }//nx 
 }//ny
} //par

free(pdWX_buf); free(pdWY_buf);

if (nOutOfBounds_glob > 0)
  rv.flags |= 1;

return rv;
} 



