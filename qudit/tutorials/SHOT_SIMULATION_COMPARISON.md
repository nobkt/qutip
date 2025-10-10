
# Visual Comparison: Before vs After

## Before Fix (Incorrect)

### Shot-Based Simulation Flow:
```
Time t=0 ──────────────────────────────────────────────────────────────> Time t=T

Exact Math:                    Initialize Final State:
U = exp(-iHt) ───────────────> qc.initialize(U*psi0) ───> Measure
[Matrix Exponentiation]        [Direct State Setting]    [Get Counts]
                               NO QUANTUM GATES!

Circuit:
     ┌──────────────────────┐┌─┐   
q_0: ┤0  Initialize(final)  ├┤M├
     │   state directly     │└╥┘┌─┐
q_1: ┤1  (cheating!)        ├─╫─┤M├
     └──────────────────────┘ ║ └╥┘
```

**Problem**: No actual quantum gates! Just initialize the answer.

---

## After Fix (Correct)

### Shot-Based Simulation Flow:
```
Time t=0 ──────> Step 1 ──────> Step 2 ──────> ... ──────> Time t=T

Initialize:      Apply Gates:    Apply Gates:              Measure:
qc.initialize    qc.compose      qc.compose                qc.measure
(psi0)          (qc_step)       (qc_step)                 [Get Counts]
                [RX,RY,RZ,CX]   [RX,RY,RZ,CX]

Circuit for N steps:
     ┌────────────┐┌─────┐┌─────┐┌─────┐     ┌─────┐┌─────┐┌─────┐     ┌─┐
q_0: ┤ Initialize ├┤ Rz  ├┤ Rx  ├┤ Rz  ├──■──┤ Rz  ├┤ Rx  ├┤ Rz  ├──■──┤M├
     ├────────────┤├─────┤├─────┤├─────┤┌─┴─┐├─────┤├─────┤├─────┤┌─┴─┐└╥┘
q_1: ┤ Initialize ├┤ Rz  ├┤ Rx  ├┤ Rz  ├┤ X ├┤ Rz  ├┤ Rx  ├┤ Rz  ├┤ X ├─╫─┤M├
     └────────────┘└─────┘└─────┘└─────┘└───┘└─────┘└─────┘└─────┘└───┘ ║ └╥┘
           │            Step 1 Gates               Step 2 Gates            │
           └─────────────────────────────────────────────────────────────┘
```

**Benefit**: Uses actual quantum gates that could run on hardware!

---

## Key Code Changes

### Before (Wrong):
```python
# Compute exact evolution
t = times[t_idx]
U = (-1j * H_zeeman * t).expm()  # ← Exact matrix exponentiation
psi_t = U * psi0                 # ← Get final state mathematically

# Just initialize the answer
psi_t_qubit = encoder.encode_state(psi_t)
qc.initialize(psi_t_qubit)       # ← CHEAT: Set state directly
qc.measure([0, 1], [0, 1])
```

### After (Correct):
```python
# Decompose one time step into gates
dt = times[1] - times[0]
U_step = (-1j * H_zeeman_qubit * dt).expm()  # One step only

# Convert to quantum gates using KAK decomposition
decomposer = TwoQubitBasisDecomposer(CXGate())
qc_step = decomposer(Operator(U_step))
qc_step = transpile(qc_step, basis_gates=['rx', 'ry', 'rz', 'cx'])

# Build circuit by composing steps
qc.initialize(psi0_qubit)        # ← Start from initial state
for step in range(t_idx):
    qc.compose(qc_step)          # ← Apply gates step by step
qc.measure([0, 1], [0, 1])
```

---

## Impact on Results

### Circuit Complexity:
- **Before**: Depth=2, Size=3 (initialize + 2 measurements)
- **After**: Depth=17, Size=32 (many RX, RY, RZ, CX gates)

### Noise Application:
- **Before**: Noise could only affect measurement (meaningless!)
- **After**: Noise affects every gate during evolution (realistic!)

### Scientific Validity:
- **Before**: Not a real quantum simulation (exact math + sampling)
- **After**: Proper quantum simulation with gate-based evolution
