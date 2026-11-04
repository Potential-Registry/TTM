"""TTM through McUtils ctypes: Angstrom, Hartree, Hartree/Angstrom."""
import ctypes
from pathlib import Path
import numpy as np
from McUtils.Extensions import SharedLibrary, SharedLibraryFunction

__all__ = ['load_potential']
HARTREE_TO_KCAL = 627.5094740631


def _validate(kw):
    coords=np.asarray(kw['coords'],dtype=np.float64)
    if coords.ndim < 2 or coords.shape[-1]!=3 or coords.shape[-2]%3 or coords.shape[-2]==0:
        raise ValueError('coords must have shape (..., 3*nwaters, 3), in O,H,H order per water')
    nwaters=coords.shape[-2]//3
    requested=kw['nwaters']
    if requested is not None and (not isinstance(requested,(int,np.integer)) or requested!=nwaters):
        raise ValueError('nwaters must match the coordinate atom count')
    if not np.isfinite(coords).all():
        raise ValueError('coords must be finite')
    for i in range(coords.shape[-2]):
        for j in range(i):
            if np.any(np.sum((coords[...,i,:]-coords[...,j,:])**2,axis=-1)==0):
                raise ValueError('atoms must have distinct positions')
    ngeom=coords.size//(9*nwaters)
    if max(nwaters,ngeom)>np.iinfo(np.int32).max:
        raise ValueError('input exceeds the C interface integer range')
    kw['nwaters']=int(nwaters)
    kw['ngeom']=ngeom
    kw['coords']=np.ascontiguousarray(coords)
    kw['energy']=np.empty(coords.shape[:-2] or (1,),dtype=np.float64)
    if 'grad' in kw:
        kw['grad']=np.empty(coords.shape,dtype=np.float64)
    return kw


def _prepare(kw):
    kw=_validate(kw)
    if kw['imodel'] not in (2,21,3):
        raise ValueError('imodel must be 2 (TTM2), 21 (TTM2.1), or 3 (TTM3)')
    if not isinstance(kw['imodel'],(int,np.integer)):
        raise ValueError('imodel must be an integer')
    # The native TTM routines expect all O sites before all H sites.
    coords=kw['coords']; nw=kw['nwaters']
    waters=coords.reshape(coords.shape[:-2]+(nw,3,3))
    grouped=np.concatenate([waters[...,0,:],waters[...,1:,:].reshape(coords.shape[:-2]+(2*nw,3))],axis=-2)
    kw['coords']=np.ascontiguousarray(grouped)
    return kw


def _energy(result,kw):
    energy=kw['energy']/HARTREE_TO_KCAL
    return float(energy[0]) if kw['coords'].ndim==2 else energy


def _gradient(result,kw):
    grad=kw['grad']; nw=SharedLibraryFunction.uncast(kw['nwaters'])
    waters=np.empty(grad.shape[:-2]+(nw,3,3),dtype=np.float64)
    waters[...,0,:]=grad[...,:nw,:]
    waters[...,1:,:]=grad[...,nw:,:].reshape(grad.shape[:-2]+(nw,2,3))
    return {'energy':_energy(result,kw),'grad':waters.reshape(grad.shape)/HARTREE_TO_KCAL}


def load_potential(library=None):
    if library is None:
        library=Path(__file__).parent/'raw_source/TTM/libs/libttm.so'
    handle=ctypes.CDLL(str(Path(library).resolve()))
    def spec(handler):
        return dict(name='ttm_potential',nwaters=int,ngeom=int,coords=[float],grad=[float],energy=[float],imodel=int,
            return_type=None,defaults=dict(nwaters=None,ngeom=0,grad=None,energy=None,imodel=3),
            prep_args=_prepare,return_handler=handler)
    potential=SharedLibrary(handle,get_pot=spec(_energy),get_pot_grad=spec(_gradient))
    potential.get_pot.initialize()
    potential.get_pot_grad.initialize()
    return potential
