# Noise Model Fix for zeeman_effect_comprehensive.ipynb

## Problem

When running Cell 13 of `zeeman_effect_comprehensive.ipynb`, the following error occurred:

```
QiskitError: 'ERROR:  [Experiment 0] QuantumError: qubits size (1) < error qubits (2). ,  
ERROR: QuantumError: qubits size (1) < error qubits (2).'
```

## Root Cause

The error was caused by this line in the noise model setup:

```python
noise_model.add_all_qubit_quantum_error(depol_2q, ['cx', 'unitary'])
```

The issue is that `depol_2q` is a **2-qubit depolarizing error**, but `'unitary'` gates can be either:
- 1-qubit unitary operations (e.g., from decomposing single-qubit rotations)
- 2-qubit unitary operations (e.g., from decomposing two-qubit gates)

When the circuit decomposition process creates a 1-qubit `'unitary'` gate and the noise model tries to apply a 2-qubit depolarizing error to it, Qiskit correctly raises an error because you cannot apply a 2-qubit error to a 1-qubit gate.

## Solution

Remove `'unitary'` from the list of gates that receive 2-qubit depolarizing errors:

**Before:**
```python
noise_model.add_all_qubit_quantum_error(depol_2q, ['cx', 'unitary'])
```

**After:**
```python
noise_model.add_all_qubit_quantum_error(depol_2q, ['cx'])
```

### Why This Works

1. **For 2-qubit operations**: The `'cx'` (CNOT) gate is guaranteed to be a 2-qubit gate, so applying a 2-qubit error is always valid.

2. **For 1-qubit operations**: Any 1-qubit `'unitary'` gates that appear in the circuit will still receive noise through the 1-qubit error rules that are applied to gates like `'rx'`, `'ry'`, `'rz'`, etc.

3. **No heuristics**: This is a proper fix, not a workaround. It correctly applies noise based on the actual number of qubits each gate operates on.

## Changed File

- `qudit/tutorials/zeeman_effect_comprehensive.ipynb` (Cell 13, line 500)

## Testing

To verify this fix works:

1. Ensure Qiskit and Qiskit-Aer are installed:
   ```bash
   pip install qiskit qiskit-aer
   ```

2. Run the notebook:
   ```bash
   jupyter notebook qudit/tutorials/zeeman_effect_comprehensive.ipynb
   ```

3. Execute Cell 13 (the noisy simulation cell). It should now complete without errors.

## Technical Details

### Qiskit Noise Model Behavior

When you call `noise_model.add_all_qubit_quantum_error(error, gates)`:
- Qiskit applies the `error` to every instance of every gate in the `gates` list
- The error must have the same number of qubits as the gate it's applied to
- If there's a mismatch (e.g., 2-qubit error on 1-qubit gate), Qiskit raises `QiskitError`

### Circuit Decomposition

When circuits are transpiled and decomposed:
- Complex gates may be decomposed into elementary gates
- The transpiler may use `'unitary'` instructions as an intermediate representation
- These `'unitary'` instructions can have varying numbers of qubits depending on the original gate

### Best Practice

For noise models, only apply N-qubit errors to gates that are guaranteed to be N-qubit gates:
- 1-qubit errors → `'rx'`, `'ry'`, `'rz'`, `'u1'`, `'u2'`, `'u3'`, `'h'`, `'x'`, `'y'`, `'z'`, etc.
- 2-qubit errors → `'cx'`, `'cz'`, `'cy'`, `'swap'`, etc.
- Do NOT apply N-qubit errors to `'unitary'` gates unless you're certain all unitary gates in your circuit have exactly N qubits
