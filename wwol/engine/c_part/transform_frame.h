// TRANSFORM_FRAME_H : оберкта над частью старой программы -- функция коррекции
// перспективы

#ifndef TRANSFORM_FRAME_H
#define TRANSFORM_FRAME_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct TransformFrameOutputParam {
  unsigned int flags;    // 0 - ок, 1 - вышел за пределы
  double Lx, Ly;         // размер области в метрах
} TransformFrameOutputParam;


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
    int Y2);

#ifdef __cplusplus
}
#endif

#endif
