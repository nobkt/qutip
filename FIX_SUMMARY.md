# Fix Summary: MQT Simulator AttributeError with Qobj Inputs

## Problem Statement
When running the notebook `qudit/tutorials/zeeman_effect_comprehensive.ipynb`, the following error occurred:

```python
AttributeError: 'Qobj' object has no attribute 'T'
```

This happened in the `_validate_hamiltonian` method at line 465 of `mqt_simulator.py`:

```python
if not np.allclose(H, H.conj().T):  # Qobj doesn't have .T attribute!
    raise ValueError("Hamiltonian must be Hermitian")
```

## Root Cause
The notebook passes QuTiP `Qobj` objects to the MQT simulators:
- `H_zeeman` is a `Qobj` created by `qt.jmat(1, 'z')`
- `psi0` is a `Qobj` created by `qt.basis()`

However, the MQT simulator validation methods expected `np.ndarray` and tried to use `.T` (NumPy's transpose attribute) which doesn't exist on `Qobj` objects.

QuTiP `Qobj` uses `.trans()` method for transpose, not `.T` attribute.

## Solution
Modified the validation methods to:
1. Detect if input is a `Qobj` using duck typing: `hasattr(obj, 'full')`
2. Convert `Qobj` to `np.ndarray` using `.full()` method
3. Perform validation on the numpy array which has `.T` attribute
4. Return the converted numpy array

### Code Changes

**Before:**
```python
def _validate_hamiltonian(self, H: np.ndarray):
    """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix."""
    if H.shape != (3, 3):
        raise ValueError(f"Hamiltonian must be 3x3, got shape {H.shape}")
    
    # Check Hermiticity
    if not np.allclose(H, H.conj().T):  # <-- FAILS for Qobj
        raise ValueError("Hamiltonian must be Hermitian")
```

**After:**
```python
def _validate_hamiltonian(self, H):
    """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix.
    
    Parameters
    ----------
    H : ndarray or Qobj
        Hamiltonian matrix to validate. If Qobj, will be converted to ndarray.
        
    Returns
    -------
    H_array : ndarray
        The Hamiltonian as a numpy array.
    """
    # Convert Qobj to numpy array if needed
    if hasattr(H, 'full'):
        # This is a QuTiP Qobj
        H_array = H.full()
    else:
        H_array = np.asarray(H)
    
    if H_array.shape != (3, 3):
        raise ValueError(f"Hamiltonian must be 3x3, got shape {H_array.shape}")
    
    # Check Hermiticity - now works because numpy arrays have .T
    if not np.allclose(H_array, H_array.conj().T):
        raise ValueError("Hamiltonian must be Hermitian")
    
    return H_array
```

Similar changes were made to:
- `MQTStatevectorSimulator._validate_hamiltonian()`
- `MQTStatevectorSimulator._validate_state()`
- `MQTStatevectorSimulator.simulate()` - to use returned converted values and handle observable conversion
- `MQTShotSimulator._validate_hamiltonian()`
- `MQTShotSimulator._validate_state()`
- `MQTShotSimulator.simulate()` - to use returned converted values and handle observable conversion

## Benefits
1. **No AttributeError**: Qobj objects are properly converted before attempting to use `.T`
2. **Backward Compatible**: Still works with numpy array inputs
3. **No Dependencies**: Doesn't require importing QuTiP in the MQT module
4. **No Heuristics**: Uses standard duck typing pattern
5. **Clean API**: Users can pass either Qobj or numpy arrays seamlessly

## Testing
Created `test_qobj_validation.py` with comprehensive unit tests:
- Tests validation with Qobj inputs
- Tests validation with numpy array inputs
- Tests superposition states
- Tests error cases (non-Hermitian, wrong dimensions)
- Tests that `.T` attribute doesn't exist on Qobj (verifying the original issue)

## Files Modified
1. `qudit/qudit/mqt_simulator.py` - Core fix in validation methods
2. `qudit/qudit/test_qobj_validation.py` - New test file

## Usage Example
```python
import qutip as qt
import numpy as np
from qudit.qudit import MQTStatevectorSimulator

# Create Hamiltonian and state using QuTiP
omega_L = 2 * np.pi * 1.0
Jz = qt.jmat(1, 'z')
H_zeeman = -omega_L * Jz  # Qobj
psi0 = (qt.basis(3, 0) + qt.basis(3, 1)).unit()  # Qobj

# Create simulator
sim = MQTStatevectorSimulator(trotter_order=2)

# Simulate - now works with Qobj inputs!
times = np.linspace(0, 1.0, 10)
result = sim.simulate(H_zeeman, psi0, times)  # No more AttributeError!
```

## Technical Details
The fix uses duck typing (`hasattr(obj, 'full')`) rather than `isinstance` checks because:
1. Avoids importing QuTiP as a dependency
2. More Pythonic and flexible
3. Works with any object that implements `.full()` method
4. Follows the "ask forgiveness, not permission" Python philosophy

The `.full()` method is the standard way QuTiP Qobj objects provide their numpy array representation, making this a robust and maintainable solution.
