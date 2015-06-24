# -*- coding: utf-8 -*-
import numpy as np
import math
import copy
import logging

from . import power_spec
from .draw_common import get_dispers_kf
from .basic_plots import calc_sf

def apply_fmin(spec, fmin):
    """
    Ниже частоты fmin [Гц] притягиевает спектр к эталону (первому эталону)
    in-place преобразование
    """
    if len(spec.etalon)==0:
        logging.warning("Parameter 'fmin' is ignored when calibrating because "\
            "etalon is not provided")
        return
    et = spec.etalon[0]
    sf = calc_sf(spec)
    nfmin = int( math.ceil(fmin / spec.df) -1 )
    if nfmin <= 0: return
    nfmin = min(nfmin, spec.data.shape[2])
    
    for nf in range(0,nfmin):
        freq = (nf+1) * spec.df
        nf_et = np.searchsorted(et[:,0], freq)
        old_val = sf[nf,1] + 1e-10
        if nf_et > 0:
            f_et_up = et[nf_et, 0]
            f_et_low = et[nf_et - 1, 0]
            coef_0_at_low = (freq - f_et_low) / (f_et_up - f_et_low)
            coef_0_at_up = (f_et_up - freq) / (f_et_up - f_et_low)
            cor = (et[nf_et - 1, 1] * coef_0_at_up + \
                   et[nf_et, 1] * coef_0_at_low) / old_val
        else:
            cor = et[-1, 1] / old_val
        spec.data[:,:,nf] *= cor
    

def basic_transform(in_spec, a_dB, kmin, gamma, fmin):
    """
    Калибровка [ a*K/(K^2+Kmin'^2) ]^2
    Kmin' = max(Kdisp*gamma, Kmin)
    """
    out_spec = copy.deepcopy(in_spec)
    
    Nx = in_spec.data.shape[0]
    Ny = in_spec.data.shape[1]
    nx0 = Nx/2
    ny0 = Ny/2
    k2_arr = np.ndarray((Nx, Ny), order='F')
    a = 10.0**(a_dB*0.1)
    for ny in range (0, Ny):
        for nx in range (0, Nx):    
            kx = in_spec.dkx*(nx-nx0)
            ky = in_spec.dky*(ny-ny0)
            k2_arr[nx, ny] = kx*kx+ky*ky
        
    for nf in range(0, in_spec.data.shape[2]):
        freq = in_spec.df * (nf + 1)
        k_disp = get_dispers_kf()(freq)
        trf = a * k2_arr / (k2_arr + max(kmin, gamma*k_disp)**2 )**2
        out_spec.data[:,:,nf] =  trf * in_spec.data[:,:,nf]
    
    apply_fmin(out_spec, fmin)
    out_spec.calibr_details = [power_spec.STD_CALIBR_FLAG,
        a_dB, kmin, fmin, gamma];
    return out_spec
    
