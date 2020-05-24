import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport abs
from libc.stdlib cimport rand


ctypedef np.uint8_t DTYPE_t
ctypedef np.uint32_t DTYPE32_t


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def draw2(np.ndarray[DTYPE_t, ndim=3] data, int c, int max_x, int max_y):
    cdef int x, y
    cdef int ic = c
    cdef np.ndarray[DTYPE_t, ndim=3] h = data
    cdef int cmax_y = max_y, cmax_x = max_x
    for y in range(cmax_y):
        for x in range(cmax_x):
            h[y, x, 0] = 0
            h[y, x, 1] = 0
            h[y, x, 2] = y / (ic + 1)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def drawUp(np.ndarray[DTYPE_t, ndim=3] data, int c, int max_x, int max_y):
    cdef int x, y
    cdef int ic = c
    cdef np.ndarray[DTYPE_t, ndim=3] h = data
    cdef int cmax_y = max_y, cmax_x = max_x
    # Copy top to bottom
    for x in range(0, cmax_x):
        h[cmax_y - 2, x, 0] = h[0, x, 0]
        h[cmax_y - 2, x, 1] = h[0, x, 1]
        h[cmax_y - 2, x, 2] = h[0, x, 2]
    for y in range(1, cmax_y - 1):
        for x in range(0, cmax_x):
            h[y - 1, x, 0] = h[y, x, 0]
            h[y - 1, x, 1] = h[y, x, 1]            
            h[y - 1, x, 2] = h[y, x, 2]    
            

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def desenhaflamas(np.ndarray[DTYPE_t, ndim=2] data, 
                  int c, int max_x, int max_y, 
                  np.ndarray[DTYPE32_t, ndim=2] fogo):
    cdef int x, y
    cdef int ic = c
    cdef np.ndarray[DTYPE_t, ndim=2] d = data
    cdef np.ndarray[DTYPE32_t, ndim=2] f = fogo
    cdef int cmax_y = max_y, cmax_x = max_x

    for x in range(cmax_x):
        f[cmax_y - 1, x] = abs(32768 + rand()) % 2048

    for y in range(1, cmax_y - 2):
        for x in range(0, cmax_x):
            f[y, x] = ((f[(y + 1) % cmax_y, x] +
                        f[(y + 1) % cmax_y, (x - 1) % cmax_x] +
                        f[(y + 1)% cmax_y, (x + 1) % cmax_x] +
                        f[(y + 2)% cmax_y, x]) * 32) / 129
    for y in range(max_y):
        for x in range(max_x):
            d[y, x] = f[y, x] % 256