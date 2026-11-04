# TTM2, TTM2.1, and TTM3

Native potential with a McUtils `SharedLibrary`/ctypes interface.

| Interface property | Convention |
| --- | --- |
| Coordinate units | Angstrom |
| Output units | Hartree; gradients in Hartree/Angstrom |
| Atom order | O,H,H for each water |
| Input shape | `(..., 3*nwaters, 3)` |

## Build and load

From this repository root, with a native compiler available:

```sh
make -j4 -C TTM/raw_source/TTM/libs/ttm PYTHON=/path/to/python
```

The build uses GNU Fortran. `FC=/path/to/gfortran` selects the compiler. All units
retain `-frecursive`, which keeps local workspace independent across calls.

Use this repository on `PYTHONPATH` alongside McUtils, then:

```python
from TTM import load_potential
potential = load_potential()
energy = potential.get_pot(coords=coords)
```

`load_potential(library=...)` accepts an explicit shared-library path. Loading and
symbol resolution finish before it returns. Inputs are checked, batch buffers
are allocated per call, and no evaluation changes the process working directory.
The same object can be shared across a `ThreadPoolExecutor`.

## Models and gradients

`imodel=2`, `21`, or `3` selects TTM2, TTM2.1, or TTM3. The default is `3`.
Model parameters belong to the current call, so models can be mixed concurrently.
The TTM2 selector now honors model 2 instead of forcing model 21 parameters.

```python
result = potential.get_pot_grad(coords=coords, imodel=21)
energy, gradient = result['energy'], result['grad']
```

`nwaters` is inferred from the last atom dimension; if supplied, it must match.
Cluster atoms are grouped as O,H,H per water. The interface converts them to the
native all-oxygen-before-hydrogen layout and converts gradients back.
Batch energy has the leading batch shape; gradients have the input shape.

The historical module entry points remain available with their native atom
ordering and kcal/mol output. This README describes the new Python interface.

## Validation

After building, with the repository on `PYTHONPATH`:

```sh
/path/to/python -m unittest discover -s tests -v
```

Tests include independent serial/reference values, scalar and batch layouts,
concurrent first evaluations, 2,048 calls across eight threads, and input/output
ownership. Where analytic gradients are available, finite differences check their
units and layout. `POTENTIAL_LIBRARY=/absolute/path/to/library.so` selects a
separate diagnostic build for the test suite.

`tests/native_checks.f90` enables IEEE invalid-operation, division-by-zero, and
overflow traps. Link it to the diagnostic object files built with bounds checks
and signaling-NaN initialization to exercise the native calculation directly.

TTM2 reference fixtures use the original serial routines with the hardcoded
model-21 selector corrected to honor the requested model.
