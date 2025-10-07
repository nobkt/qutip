# Verification Checklist for spin1_qubit_simulation.ipynb

This document provides a step-by-step checklist for verifying that the Qiskit integration fix resolves the discrepancy issue in the spin1_qubit_simulation notebook.

## Prerequisites

Before running the notebook:

- [ ] QuTiP is installed: `pip install qutip`
- [ ] Qiskit is installed: `pip install qiskit`
- [ ] NumPy is installed: `pip install numpy`
- [ ] Matplotlib is installed: `pip install matplotlib`
- [ ] Jupyter is installed: `pip install jupyter`

## Step-by-Step Verification

### 1. Environment Setup

```bash
cd /path/to/qutip
jupyter notebook qudit/tutorials/spin1_qubit_simulation.ipynb
```

- [ ] Notebook opens successfully
- [ ] All import statements execute without errors

### 2. Example 1: Zeeman Effect

Run the cells for Example 1 (Zeeman Effect: H = ω Jz).

**Expected behavior:**
- [ ] All three simulations complete (Exact, Trotter, Qiskit)
- [ ] Population plots show three overlapping curves
- [ ] Error metrics are printed

**Expected error values:**
- [ ] Qiskit vs Exact: `max_error < 1e-4` (should be very small, ~10⁻⁶ or less)
- [ ] Qiskit vs Trotter: `max_error < 1e-4` (should be nearly identical)
- [ ] Trotter vs Exact: `max_error ~ 1e-6` (2nd order Trotter approximation)

**Before fix** (for reference):
- ❌ Qiskit vs Exact: `max_error > 0.1` (complete mismatch)
- ❌ Qiskit vs Trotter: `max_error > 0.1` (complete mismatch)

### 3. Example 2: Transverse Field Precession

Run the cells for Example 2 (H = ω Jx).

**Expected behavior:**
- [ ] All three simulations complete
- [ ] Population plots show three overlapping curves
- [ ] Error metrics are printed

**Expected error values:**
- [ ] Qiskit vs Exact: `max_error < 1e-4`
- [ ] Qiskit vs Trotter: `max_error < 1e-4`
- [ ] Trotter vs Exact: `max_error ~ 1e-6`

### 4. Example 3: Rabi Oscillations

Run the cells for Example 3 (H = ω₀ Jz + Ω (J₊ + J₋)).

**Expected behavior:**
- [ ] All three simulations complete
- [ ] Population plots show three overlapping curves
- [ ] Error metrics are printed

**Expected error values:**
- [ ] Qiskit vs Exact: `max_error < 1e-4`
- [ ] Qiskit vs Trotter: `max_error < 1e-4`
- [ ] Trotter vs Exact: `max_error ~ 1e-6`

### 5. Visual Inspection

For each example:

- [ ] **Exact solution curve** (solid line) is visible
- [ ] **Trotter solution curve** (dashed line) overlaps with exact
- [ ] **Qiskit solution curve** (dotted line) overlaps with both
- [ ] Error plots show errors in the range 10⁻⁴ to 10⁻⁷
- [ ] No sudden jumps or discontinuities in any plot

### 6. Quantum Circuit Visualization

If the notebook includes circuit visualization:

- [ ] Circuits render correctly
- [ ] Gate sequences are visible
- [ ] Circuit depth and gate count are reported

## Troubleshooting

### If tests fail:

1. **Import errors:**
   - Verify all dependencies are installed
   - Check Python version (should be 3.9+)

2. **Qiskit errors:**
   - Verify Qiskit version: `pip show qiskit`
   - Should be version 2.0 or later

3. **Large errors persist:**
   - Check that the fix was correctly applied
   - Verify file `qudit/qubit/statevector_simulator.py` contains:
     - Line 468: `perm = np.array([0, 2, 1, 3])`
     - Line 501: `U_matrix_qiskit = U_matrix[np.ix_(perm, perm)]`
     - Line 523: `qc.compose(transpiled, qubits=[0, 1], inplace=True)`
     - Line 531: `inv_perm = np.array([0, 2, 1, 3])`

4. **Numerical issues:**
   - Try reducing time step size
   - Try increasing Trotter order
   - Check for overflow/underflow warnings

## Success Criteria

The fix is working correctly if:

✅ All three examples run without errors  
✅ Error metrics show Qiskit matches Exact within ~10⁻⁴ to 10⁻⁶  
✅ Error metrics show Qiskit matches Trotter within ~10⁻⁴ to 10⁻⁷  
✅ Visual plots show all three methods producing overlapping curves  
✅ No warnings or exceptions are raised during execution

## Reporting Issues

If the verification fails, please report:

1. Python version: `python --version`
2. QuTiP version: `import qutip; print(qutip.__version__)`
3. Qiskit version: `import qiskit; print(qiskit.__version__)`
4. NumPy version: `import numpy; print(numpy.__version__)`
5. Specific error message or traceback
6. Screenshot of problematic plots
7. Actual vs expected error values

---

**Last Updated**: 2025  
**Related Documents**:
- `SPIN1_QISKIT_ISSUE_ANALYSIS.md` - Detailed technical analysis
- `SPIN1_QISKIT_FIX_SUMMARY.md` - Executive summary
- `SPIN1_VISUAL_EXPLANATION.md` - Visual diagrams and flow charts
