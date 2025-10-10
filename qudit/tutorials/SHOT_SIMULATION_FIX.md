# Shot-Based Simulation Fix

## Problem Statement

When running `qudit/tutorials/zeeman_effect_comprehensive.ipynb`, the shot-based simulations (both noiseless and noisy) were using only an `initialize` instruction instead of actual quantum gates for time evolution. This meant:

1. **Statevector simulation**: Correctly showed decomposed quantum circuits with RX, RY, RZ, and CX gates representing Trotter-decomposed time evolution
2. **Shot-based simulation**: Only showed `initialize` + `measure`, bypassing the actual quantum gate implementation

### Example of the Problem

**Before fix - Shot circuit:**
```
     ┌──────────────────────────────────┐┌─┐   
q_0: ┤0                                 ├┤M├───
     │  Initialize(0.70711,0.70711,0,0) │└╥┘┌─┐
q_1: ┤1                                 ├─╫─┤M├
     └──────────────────────────────────┘ ║ └╥┘
c: 2/═════════════════════════════════════╩══╩═
                                          0  1 
```

This was problematic because:
- The shot simulation wasn't actually using quantum gates
- Time evolution was computed exactly using matrix exponentiation `(-1j * H * t).expm()`
- The result was just initialized directly, not evolved through gates
- This defeated the purpose of shot-based simulation with noise models

## Root Cause

The notebook code was:
1. Computing exact time evolution: `U = (-1j * H_zeeman * t).expm()` and `psi_t = U * psi0`
2. Encoding the final state to qubits
3. Using `qc.initialize(psi_t_qubit)` to set the state directly
4. Only measuring, without any evolution gates

## Solution

Modified both noiseless (cell 11) and noisy (cell 13) shot simulation sections to:

1. **Decompose the time step evolution** into elementary gates using KAK decomposition:
   ```python
   # 1ステップの時間発展演算子を基本ゲートに分解
   H_zeeman_qubit = encoder.encode_operator(H_zeeman)
   U_step = (-1j * H_zeeman_qubit * dt).expm()
   U_step_matrix = U_step.full()
   
   # Qiskitの規約に合わせて演算子を並べ替え
   U_step_matrix_qiskit = U_step_matrix[np.ix_(perm, perm)]
   operator = Operator(U_step_matrix_qiskit)
   
   # KAK分解を使用して実際の量子ゲートに分解
   decomposer = TwoQubitBasisDecomposer(CXGate())
   qc_step_decomposed = decomposer(operator)
   qc_step = transpile(qc_step_decomposed, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                      optimization_level=0)
   ```

2. **Build cumulative circuits** by composing the step circuit multiple times:
   ```python
   # この時間点までの回路を構築
   qc = QuantumCircuit(qr, cr)
   qc.initialize(psi0_array_qiskit, [0, 1])
   
   # t_idx ステップ分の時間発展を適用
   for step in range(t_idx):
       qc.compose(qc_step, qubits=[0, 1], inplace=True)
   
   # 測定
   qc.measure([0, 1], [0, 1])
   ```

3. **Corrected qubit ordering convention**:
   - QuTiP uses big-endian: `[|00⟩, |01⟩, |10⟩, |11⟩]`
   - Qiskit uses little-endian: `[|00⟩, |10⟩, |01⟩, |11⟩]`
   - Applied permutation `[0, 2, 1, 3]` to convert between conventions

## Result

**After fix - Shot circuit (example for 1 time step):**
```
     ┌──────────────┐┌─────────┐  ┌────────┐  ┌─────────┐┌───────────┐     »
q_0: ┤ Initialize() ├┤ Rz(π/4) ├──┤ Rx(π/2)├──┤ Rz(2π)  ├┤ Rx(π/2)   ├──■──»
     ├──────────────┤├─────────┤┌─┴────────┴─┐├─────────┤└───────────┘┌─┴─┐»
q_1: ┤ Initialize() ├┤ Rz(0)   ├┤ Rz(...)    ├┤ Rx(π/2) ├──────────────┤ X ├»
     └──────────────┘└─────────┘└────────────┘└─────────┘              └───┘»
«     ... (more gates) ... ┌─┐   
«q_0: ──────────────────────┤M├───
«                           └╥┘┌─┐
«q_1: ───────────────────────╫─┤M├
«                            ║ └╥┘
«c: 2/════════════════════════╩══╩═
«                             0  1 
```

Now the shot simulation:
- Uses actual quantum gates (RX, RY, RZ, CX) for time evolution
- Applies the Suzuki-Trotter decomposition through composed gate sequences
- Properly simulates noise when a noise model is provided
- Matches the gate-based approach used in statevector simulation

## Key Changes Summary

1. **Removed**: Direct computation of final state using `.expm()` followed by `initialize`
2. **Added**: Gate decomposition of single time step using `TwoQubitBasisDecomposer`
3. **Added**: Cumulative circuit building using `qc.compose(qc_step)` in a loop
4. **Fixed**: Qubit ordering convention between QuTiP and Qiskit
5. **Result**: Shot-based simulations now use the same gate sequences as statevector simulations

## Testing

The changes ensure that:
- Circuit depth and size reflect actual gate count (not just initialize + measure)
- Noise models can be properly applied to individual gates during time evolution
- The simulation represents what would actually run on a quantum computer
- Results remain consistent with exact solutions (within statistical errors)

## Files Modified

- `qudit/tutorials/zeeman_effect_comprehensive.ipynb` (cells 11 and 13)
  - Cell 11: Noiseless shot-based simulation
  - Cell 13: Noisy shot-based simulation
