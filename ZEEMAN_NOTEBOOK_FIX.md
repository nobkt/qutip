# Fix for zeeman_effect_comprehensive.ipynb Duplicate Key Error

## Problem

When executing `qudit/tutorials/zeeman_effect_comprehensive.ipynb`, the following error occurred:

```
Simulation failed and returned the following error message:
ERROR: Failed to load circuits: Duplicate key "statevector" in save instruction.
...
QiskitError: 'You have to select a circuit or schedule when there is more than one available'
```

The error occurred at line 107 in Cell 6:
```python
sv = sv_job.result().get_statevector()
```

## Root Cause

The issue was caused by calling `transpile()` on quantum circuits that contain `save_statevector()` instructions before running them on the `StatevectorSimulator`.

The problematic pattern was:
```python
qc_sv.save_statevector()
sv_sim = QiskitStatevectorSim()
sv_job = sv_sim.run(transpile(qc_sv, sv_sim))  # ← This causes the error
sv = sv_job.result().get_statevector()
```

When `transpile()` processes a circuit with `save_statevector()`, it can:
1. Duplicate the save instruction
2. Create multiple save instructions with the same default label "statevector"
3. Cause conflicts when retrieving the saved statevector

## Solution

Remove the `transpile()` call when running circuits with `save_statevector()` on the `StatevectorSimulator`. The simulator can directly execute these circuits without transpilation.

**Before:**
```python
sv_job = sv_sim.run(transpile(qc_sv, sv_sim))
```

**After:**
```python
sv_job = sv_sim.run(qc_sv)
```

## Changes Made

Fixed 2 locations in the notebook:
1. **Cell 5** (Qiskit Shot noiseless simulation): Line 106
2. **Cell 6** (Qiskit Shot noisy simulation): Line 118

Both cells had the same pattern where statevectors were retrieved for calculating expectation values of Jx and Jy operators.

## Why This Works

The `StatevectorSimulator` doesn't require transpilation for basic operations:
- It can execute circuits with `save_statevector()` directly
- Transpilation is mainly needed for:
  - Mapping to hardware constraints
  - Converting to basis gate sets
  - Optimizing circuit depth
  
Since the `StatevectorSimulator` is a simulator and doesn't have hardware constraints, transpilation is not necessary and can interfere with save instructions.

## Testing

After the fix, the notebook should execute without the "Duplicate key" error. The simulation results remain unchanged because we're just removing an unnecessary transpilation step that was causing issues.
