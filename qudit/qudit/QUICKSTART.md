# Quick Start Guide: Spin S=1 Qudit Dynamics

## 5-Minute Quick Start

### 1. Import the module

```python
import numpy as np
from qudit.qudit import (
    StatevectorSimulator,
    get_spin1_operators,
    get_spin1_states,
    spin_coherent_state
)
```

### 2. Get operators and states

```python
# Get Spin-1 operators
ops = get_spin1_operators()
Jx = ops['Jx']
Jy = ops['Jy']
Jz = ops['Jz']

# Get basis states
states = get_spin1_states()
psi_plus = states['m1']    # |1, +1⟩
psi_zero = states['m0']    # |1, 0⟩
psi_minus = states['m_1']  # |1, -1⟩
```

### 3. Define a Hamiltonian

```python
# Example: Zeeman Hamiltonian H = -ω₀*Jz
omega0 = 2 * np.pi * 1.0  # 1 Hz
H = -omega0 * Jz
```

### 4. Set initial state

```python
# Option 1: Use basis state
psi0 = psi_plus

# Option 2: Use coherent state
psi0 = spin_coherent_state(theta=np.pi/2, phi=0)  # pointing along +x

# Option 3: Superposition
psi0 = (psi_plus + psi_minus) / np.sqrt(2)
```

### 5. Run simulation

```python
# Time points
times = np.linspace(0, 2.0, 200)

# Create simulator
sim = StatevectorSimulator(trotter_order=2)

# Simulate
result = sim.simulate(H, psi0, times)
```

### 6. Access results

```python
# Get populations P(m) = |⟨m|ψ(t)⟩|²
populations = result['populations']  # shape: (n_times, 3)
P_plus = populations[:, 0]   # P(m=+1)
P_zero = populations[:, 1]   # P(m=0)
P_minus = populations[:, 2]  # P(m=-1)

# Get expectation values
expectations = result['expect']  # shape: (n_times, 3)
Jx_exp = expectations[:, 0]  # ⟨Jx⟩
Jy_exp = expectations[:, 1]  # ⟨Jy⟩
Jz_exp = expectations[:, 2]  # ⟨Jz⟩

# Get states
states_t = result['states']  # List of state vectors
psi_final = states_t[-1]     # Final state
```

### 7. Compare with exact solution

```python
comparison = sim.compare_with_exact(H, psi0, times)

# Check accuracy
fidelity = comparison['errors']['min_fidelity']
print(f"Minimum fidelity: {fidelity:.10f}")

# Get exact results
exact_pops = comparison['exact']['populations']
exact_expect = comparison['exact']['expect']
```

### 8. Plot results

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Plot expectation values
ax1.plot(times, Jx_exp, label='⟨Jx⟩')
ax1.plot(times, Jy_exp, label='⟨Jy⟩')
ax1.plot(times, Jz_exp, label='⟨Jz⟩')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Expectation Value')
ax1.legend()
ax1.grid(True)

# Plot populations
ax2.plot(times, P_plus, label='P(m=+1)')
ax2.plot(times, P_zero, label='P(m=0)')
ax2.plot(times, P_minus, label='P(m=-1)')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Population')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()
```

## Common Examples

### Zeeman Effect (Spin Precession)

```python
# Hamiltonian: H = -ω₀*Jz
omega0 = 2 * np.pi * 1.0
H = -omega0 * Jz

# Initial: coherent state along x
psi0 = spin_coherent_state(np.pi/2, 0)

# Result: precession around z-axis
```

### Rabi Oscillations

```python
# Hamiltonian: H = ω₀*Jz + Ω*Jx
omega0 = 2 * np.pi * 5.0  # Detuning
Omega = 2 * np.pi * 1.0   # Rabi frequency
H = omega0 * Jz + Omega * Jx

# Initial: ground state
psi0 = states['m_1']

# Result: oscillations between levels
```

### Quadratic Zeeman

```python
# Hamiltonian: H = -ω₀*Jz + α*Jz²
omega0 = 2 * np.pi * 2.0
alpha = 2 * np.pi * 0.5
Jz2 = Jz @ Jz
H = -omega0 * Jz + alpha * Jz2

# Initial: superposition
psi0 = (states['m1'] + states['m_1']) / np.sqrt(2)

# Result: complex dynamics with beating
```

## Advanced Features

### Custom Observables

```python
# Define custom observables to measure
Jz2 = Jz @ Jz
Jx2 = Jx @ Jx
observables = [Jx, Jy, Jz, Jz2, Jx2]

result = sim.simulate(H, psi0, times, observables=observables)
# result['expect'] will have 5 columns
```

### Different Trotter Orders

```python
# First order (faster, less accurate)
sim1 = StatevectorSimulator(trotter_order=1)

# Second order (good balance)
sim2 = StatevectorSimulator(trotter_order=2)

# Fourth order (most accurate)
sim4 = StatevectorSimulator(trotter_order=4)
```

### Hamiltonian Decomposition Basis

```python
# Diagonal/off-diagonal split (default, good for most cases)
sim = StatevectorSimulator(decomposition_basis='diag')

# Jx, Jy, Jz decomposition (for special Hamiltonians)
sim = StatevectorSimulator(decomposition_basis='xyz')

# Complete Gell-Mann basis (most general)
sim = StatevectorSimulator(decomposition_basis='full')
```

## Troubleshooting

### Low Fidelity

If fidelity is below 0.999:
```python
# Solution 1: Increase time resolution
times = np.linspace(0, t_final, 1000)  # More points

# Solution 2: Use higher order
sim = StatevectorSimulator(trotter_order=4)

# Solution 3: Change decomposition basis
sim = StatevectorSimulator(decomposition_basis='xyz')
```

### Numerical Instability

States are automatically normalized, but if you see warnings:
```python
# Check Hermiticity of Hamiltonian
is_hermitian = np.allclose(H, H.conj().T)
print(f"H is Hermitian: {is_hermitian}")

# Check eigenvalues are real
eigenvalues = np.linalg.eigvalsh(H)
print(f"Eigenvalues: {eigenvalues}")
```

## Performance Tips

1. **Time step size**: For dt ~ 0.01, order 2 is usually sufficient
2. **Order selection**: Use order 4 only for very high precision needs
3. **Decomposition basis**: 'diag' is fastest for most Hamiltonians
4. **Store only needed results**: Don't request observables you won't use

## Next Steps

- Read the full tutorial: `qudit/tutorials/spin1_qudit_dynamics.ipynb`
- Check the API reference: `qudit/qudit/README.md`
- See theory details: `qudit/doc/spin1_quantum_dynamics.md`
- Read implementation notes: `qudit/qudit/IMPLEMENTATION_SUMMARY.md`

## Getting Help

If something doesn't work:
1. Check that inputs are correct (3x3 matrix, 3x1 vector)
2. Verify Hamiltonian is Hermitian
3. Verify initial state is normalized
4. Try different Trotter orders
5. Compare with exact solution

## Example: Complete Workflow

```python
import numpy as np
import matplotlib.pyplot as plt
from qudit.qudit import StatevectorSimulator, get_spin1_operators, spin_coherent_state

# Setup
ops = get_spin1_operators()
H = -2*np.pi * ops['Jz']  # 1 Hz precession
psi0 = spin_coherent_state(np.pi/2, 0)  # x-axis
times = np.linspace(0, 2, 200)  # 2 periods

# Simulate
sim = StatevectorSimulator(trotter_order=2)
comparison = sim.compare_with_exact(H, psi0, times)

# Check accuracy
print(f"Fidelity: {comparison['errors']['min_fidelity']:.10f}")

# Plot
exact = comparison['exact']
plt.figure(figsize=(10, 4))
plt.subplot(121)
plt.plot(times, exact['expect'][:, 0], label='⟨Jx⟩')
plt.plot(times, exact['expect'][:, 1], label='⟨Jy⟩')
plt.plot(times, exact['expect'][:, 2], label='⟨Jz⟩')
plt.xlabel('Time (s)')
plt.ylabel('Expectation Value')
plt.legend()
plt.grid(True)

plt.subplot(122)
plt.plot(times, exact['populations'][:, 0], label='P(+1)')
plt.plot(times, exact['populations'][:, 1], label='P(0)')
plt.plot(times, exact['populations'][:, 2], label='P(-1)')
plt.xlabel('Time (s)')
plt.ylabel('Population')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
```

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**License**: BSD 3-Clause
