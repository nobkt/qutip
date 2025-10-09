# Shot Simulation API Documentation

## Overview

The `MQTShotSimulator` class provides shot-based quantum simulation with configurable noise models using the MQT Qudits backend. This enables realistic quantum measurement simulation that includes statistical fluctuations and hardware noise effects.

## Key Features

- **Shot-based measurement**: Samples measurement outcomes according to quantum probabilities
- **Noise models**: Supports depolarizing and dephasing noise
- **Statistical analysis**: Computes standard errors for shot-based estimates
- **Comprehensive comparison**: Side-by-side comparison of exact, statevector, and shot simulations
- **No heuristics**: Pure MQT Qudits backend with no fallback approximations

## Installation

Requires MQT Qudits:
```bash
pip install mqt.qudits
```

## Basic Usage

### Simple Shot Simulation

```python
import numpy as np
from qudit.qudit import get_spin1_operators, get_spin1_states
from qudit.qudit.mqt_simulator import MQTShotSimulator

# Get Spin-1 operators and states
ops = get_spin1_operators()
Jz = ops['Jz']
states = get_spin1_states()
psi0 = states['m1']

# Define Hamiltonian
H = -2 * np.pi * Jz  # Zeeman effect

# Create simulator
sim = MQTShotSimulator(trotter_order=2)

# Run simulation
times = np.linspace(0, 1.0, 50)
result = sim.simulate(H, psi0, times, shots=1000)

# Access results
print(f"Expectation values: {result['expect']}")
print(f"Standard errors: {result['expect_std']}")
print(f"Populations: {result['populations']}")
print(f"Measurement counts: {result['counts'][0]}")
```

### Shot Simulation with Noise

```python
from mqt.qudits.simulation.noise_tools import Noise, NoiseModel

# Create noise model
noise = Noise(
    probability_depolarizing=0.05,  # 5% depolarizing error
    probability_dephasing=0.03       # 3% dephasing error
)
noise_model = NoiseModel()
noise_model.add_all_qudit_quantum_error(
    noise, 
    ["x", "h", "rz", "r", "custom_one"]  # Apply to all gate types
)

# Create noisy simulator
sim_noisy = MQTShotSimulator(
    trotter_order=2,
    noise_model=noise_model
)

# Run simulation
result_noisy = sim_noisy.simulate(H, psi0, times, shots=1000)

# Compare with noiseless
print(f"Noiseless fidelity: {result['fidelity']}")
print(f"Noisy fidelity: {result_noisy['fidelity']}")
```

### Comprehensive Comparison

```python
# Compare all three methods: exact, statevector, and shot simulation
comparison = sim.compare_all_methods(H, psi0, times, shots=1000)

# Access different results
exact = comparison['exact']
statevector = comparison['statevector']
shots = comparison['shots']
errors = comparison['errors']

# Print error metrics
print(f"Shot vs Exact - Max error: {errors['max_expect_error_shot_exact']:.6e}")
print(f"Shot vs Exact - Min fidelity: {errors['min_fidelity_shot_exact']:.8f}")
print(f"Statevector vs Exact - Max error: {errors['max_expect_error_sv_exact']:.6e}")
print(f"Max Z-score: {errors['max_z_score']:.2f}")
```

## API Reference

### MQTShotSimulator Class

#### Constructor

```python
MQTShotSimulator(
    trotter_order: int = 2,
    decomposition_basis: str = 'xyz',
    noise_model: Optional[NoiseModel] = None
)
```

**Parameters:**
- `trotter_order` (int): Order of Suzuki-Trotter decomposition (1, 2, or 4). Default: 2
- `decomposition_basis` (str): Basis for Hamiltonian decomposition
  - `'xyz'`: Decompose into Jx, Jy, Jz components (default)
  - `'diag'`: Decompose into diagonal and off-diagonal parts
  - `'full'`: Use complete Gell-Mann basis
- `noise_model` (NoiseModel, optional): MQT noise model. If None, uses minimal noise (≈10^-12) to enable shot simulation

**Attributes:**
- `has_significant_noise` (bool): True if a significant noise model was provided
- `backend` (MISim): MQT Qudits simulation backend
- `noise_model` (NoiseModel): The noise model being used

#### Methods

##### simulate()

Perform shot-based quantum dynamics simulation.

```python
simulate(
    hamiltonian: np.ndarray,
    initial_state: np.ndarray,
    times: np.ndarray,
    shots: int = 1000,
    observables: Optional[List[np.ndarray]] = None
) -> Dict
```

**Parameters:**
- `hamiltonian` (ndarray): 3×3 Hermitian Hamiltonian matrix
- `initial_state` (ndarray): 3×1 initial state vector (will be normalized)
- `times` (ndarray): Time points at which to evaluate the system
- `shots` (int): Number of measurement shots per time point (≥50). Default: 1000
- `observables` (list of ndarray, optional): 3×3 observable operators. Default: [Jx, Jy, Jz]

**Returns:**
Dictionary containing:
- `'times'` (ndarray): Time array
- `'shots'` (int): Number of shots used
- `'counts'` (list of dict): Measurement counts at each time point
- `'expect'` (ndarray): Expectation values from shot statistics, shape (n_times, n_observables)
- `'expect_std'` (ndarray): Standard errors of expectation values
- `'populations'` (ndarray): Populations from shot statistics, shape (n_times, 3)
- `'populations_std'` (ndarray): Standard errors of populations
- `'statevector'` (list of ndarray): Underlying statevectors at each time
- `'backend'` (str): Backend identifier ('MQT-Shots')
- `'has_significant_noise'` (bool): Whether significant noise was used

**Example:**
```python
result = sim.simulate(H, psi0, times, shots=1000)
print(f"<Jx> = {result['expect'][0, 0]:.4f} ± {result['expect_std'][0, 0]:.4f}")
```

##### compare_all_methods()

Compare shot simulation with statevector and exact solutions.

```python
compare_all_methods(
    hamiltonian: np.ndarray,
    initial_state: np.ndarray,
    times: np.ndarray,
    shots: int = 1000,
    observables: Optional[List[np.ndarray]] = None
) -> Dict
```

**Parameters:** Same as `simulate()`

**Returns:**
Dictionary containing:
- `'exact'`: Results from exact matrix exponentiation
  - `'times'`, `'states'`, `'expect'`, `'populations'`, `'backend'`
- `'statevector'`: Results from Trotter statevector simulation
  - `'times'`, `'states'`, `'expect'`, `'populations'`, `'backend'`, `'trotter_order'`
- `'shots'`: Results from shot simulation (same format as `simulate()`)
- `'errors'`: Comprehensive error metrics
  - `'expect_error_shot_exact'`: Expectation value errors (shot vs exact)
  - `'pop_error_shot_exact'`: Population errors (shot vs exact)
  - `'max_expect_error_shot_exact'`: Maximum expectation error
  - `'mean_expect_error_shot_exact'`: Mean expectation error
  - `'fidelity_shot_exact'`: State fidelities (shot vs exact)
  - `'min_fidelity_shot_exact'`: Minimum fidelity
  - `'expect_error_sv_exact'`: Errors (statevector vs exact)
  - `'max_expect_error_sv_exact'`: Maximum error
  - `'mean_expect_error_sv_exact'`: Mean error
  - `'fidelity_sv_exact'`: Fidelities (statevector vs exact)
  - `'min_fidelity_sv_exact'`: Minimum fidelity
  - `'expect_error_shot_sv'`: Errors (shot vs statevector)
  - `'z_scores'`: Z-scores for statistical consistency
  - `'max_z_score'`: Maximum Z-score
  - `'shots'`: Number of shots used

**Example:**
```python
comparison = sim.compare_all_methods(H, psi0, times, shots=1000)
print(f"Statevector accuracy: {comparison['errors']['min_fidelity_sv_exact']:.8f}")
print(f"Shot accuracy: {comparison['errors']['min_fidelity_shot_exact']:.8f}")
print(f"Statistical consistency: Z-score = {comparison['errors']['max_z_score']:.2f}")
```

## Noise Models

### Creating Noise Models

```python
from mqt.qudits.simulation.noise_tools import Noise, NoiseModel

# Create noise with specific error rates
noise = Noise(
    probability_depolarizing=p_depol,  # Depolarizing probability
    probability_dephasing=p_dephase     # Dephasing probability
)

# Create noise model
noise_model = NoiseModel()

# Apply to all gates
noise_model.add_all_qudit_quantum_error(noise, ["x", "h", "rz", "r", "custom_one"])

# Or apply to specific gates only
noise_model.add_all_qudit_quantum_error(noise, ["x", "h"])
```

### Noise Types

**Depolarizing Noise:**
- Randomly replaces the state with a completely mixed state
- Probability `p_depol` per gate operation
- Models loss of quantum information

**Dephasing Noise:**
- Randomly applies phase errors to the state
- Probability `p_dephase` per gate operation
- Models loss of phase coherence

### Typical Noise Parameters

**High-quality quantum hardware:** p_depol ≈ 0.001, p_dephase ≈ 0.0005
**Medium-quality hardware:** p_depol ≈ 0.01, p_dephase ≈ 0.005
**Low-quality hardware:** p_depol ≈ 0.05, p_dephase ≈ 0.03

## Statistical Interpretation

### Standard Errors

Shot-based measurements provide standard errors calculated as:

For expectation values:
```
σ_<O> = sqrt((<O²> - <O>²) / N_shots)
```

For populations:
```
σ_P(m) = sqrt(P(m) * (1 - P(m)) / N_shots)
```

### Z-scores

Z-scores quantify statistical consistency:
```
Z = (measurement_shot - measurement_exact) / σ_shot
```

**Interpretation:**
- |Z| < 1: Good agreement (within 1σ)
- |Z| < 2: Reasonable agreement (within 2σ)
- |Z| < 3: Acceptable agreement (within 3σ)
- |Z| > 3: Possible systematic error or insufficient shots

### Required Number of Shots

For error ε in expectation values:
```
N_shots ≈ Var(<O>) / ε²
```

**Typical values:**
- ε = 0.01: N_shots ≈ 10,000
- ε = 0.03: N_shots ≈ 1,000
- ε = 0.1: N_shots ≈ 100

## Performance Considerations

### Computational Cost

- **Per shot**: O(n_gates × d³) where d=3 for qutrits
- **Total**: O(shots × n_times × n_gates × d³)

### Optimization Tips

1. **Start with fewer shots** (100-500) for initial testing
2. **Increase shots** for final results (1000-10000)
3. **Reduce time points** if simulation is too slow
4. **Use lower Trotter order** (1 or 2) if accuracy permits
5. **Limit noise to critical gates** to reduce overhead

### Memory Usage

Memory scales as O(shots × n_times × 3), typically manageable for:
- shots ≤ 10,000
- n_times ≤ 100

## Examples

### Example 1: Measuring Noise Impact

```python
import numpy as np
from qudit.qudit import get_spin1_operators, spin_coherent_state
from qudit.qudit.mqt_simulator import MQTShotSimulator
from mqt.qudits.simulation.noise_tools import Noise, NoiseModel

# Setup
ops = get_spin1_operators()
Jx, Jz = ops['Jx'], ops['Jz']
H = -2*np.pi*Jz - np.pi*Jx  # Transverse field

psi0 = spin_coherent_state(np.pi/4, 0)
times = np.linspace(0, 2.0, 50)

# Noiseless simulation
sim_clean = MQTShotSimulator(trotter_order=2)
result_clean = sim_clean.simulate(H, psi0, times, shots=1000)

# Noisy simulation
noise = Noise(probability_depolarizing=0.02, probability_dephasing=0.01)
noise_model = NoiseModel()
noise_model.add_all_qudit_quantum_error(noise, ["x", "h", "rz", "r", "custom_one"])
sim_noisy = MQTShotSimulator(trotter_order=2, noise_model=noise_model)
result_noisy = sim_noisy.simulate(H, psi0, times, shots=1000)

# Compare
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.errorbar(times, result_clean['expect'][:, 0], 
             yerr=result_clean['expect_std'][:, 0],
             label='Noiseless', capsize=3)
plt.errorbar(times, result_noisy['expect'][:, 0],
             yerr=result_noisy['expect_std'][:, 0],
             label='Noisy', capsize=3)
plt.xlabel('Time')
plt.ylabel('⟨Jx⟩')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
error = np.abs(result_noisy['expect'] - result_clean['expect'])
plt.semilogy(times, error[:, 0], label='|Δ⟨Jx⟩|')
plt.semilogy(times, error[:, 2], label='|Δ⟨Jz⟩|')
plt.xlabel('Time')
plt.ylabel('Absolute Error')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('noise_comparison.png', dpi=150)
print("Figure saved as 'noise_comparison.png'")
```

### Example 2: Statistical Convergence Study

```python
# Study how results converge with increasing shots
shot_counts = [100, 500, 1000, 5000, 10000]
errors = []

for shots in shot_counts:
    result = sim.simulate(H, psi0, times, shots=shots)
    # Compare to exact solution (computed once)
    if not errors:  # First iteration
        result_exact = sim._exact_evolution(H, psi0, times, sim._get_default_observables())
    
    error = np.mean(np.abs(result['expect'] - result_exact['expect']))
    errors.append(error)
    print(f"Shots: {shots:5d}, Mean error: {error:.6e}")

# Plot convergence
plt.figure(figsize=(8, 5))
plt.loglog(shot_counts, errors, 'o-', linewidth=2, markersize=8)
plt.xlabel('Number of Shots', fontsize=12)
plt.ylabel('Mean Absolute Error', fontsize=12)
plt.title('Convergence with Increasing Shots', fontsize=14)
plt.grid(True, alpha=0.3)
plt.savefig('shot_convergence.png', dpi=150)
```

## Troubleshooting

### Common Issues

**Issue:** "Number of shots must be at least 50 for MQT simulation"
- **Solution:** Increase `shots` parameter to ≥ 50

**Issue:** Shot simulation returns empty counts without noise model
- **Solution:** This is expected. MQT only simulates shots when a noise model is present. The simulator automatically creates a minimal noise model (≈10^-12) if none is provided.

**Issue:** Large Z-scores (|Z| > 3)
- **Solution:** Increase number of shots or check for systematic errors

**Issue:** Simulation is very slow
- **Solution:** Reduce number of time points, reduce shots, or use lower Trotter order

**Issue:** Results don't match exact solution
- **Solution:** Check if noise model is too strong, or increase Trotter order

### Validation

Always validate your shot simulations:

```python
# Check statistical consistency
comparison = sim.compare_all_methods(H, psi0, times, shots=1000)
max_z = comparison['errors']['max_z_score']

if max_z < 3:
    print("✓ Statistically consistent (max Z-score < 3)")
else:
    print(f"⚠ Large Z-score detected: {max_z:.2f}")
    print("  Consider increasing shots or checking for errors")

# Check fidelity
min_fid = comparison['errors']['min_fidelity_shot_exact']
if min_fid > 0.99:
    print(f"✓ High fidelity: {min_fid:.6f}")
else:
    print(f"⚠ Low fidelity: {min_fid:.6f}")
    print("  Check noise model or increase Trotter order")
```

## References

1. MQT Qudits Documentation: https://mqt.readthedocs.io/projects/qudits/en/latest/
2. Suzuki-Trotter decomposition theory (in notebook)
3. Quantum measurement theory and shot noise

## Version History

- v1.0.0 (2024): Initial implementation with MQT Qudits backend
  - Shot-based measurement sampling
  - Depolarizing and dephasing noise models
  - Comprehensive comparison methods
  - Statistical error analysis
