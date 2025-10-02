# Quantum Circuit Visualization for Spin-1 Qubit Simulator

This module provides quantum circuit visualization functionality for the qubit-encoded spin-1 quantum dynamics simulator. It allows you to visualize the actual quantum circuits used by the Suzuki-Trotter decomposition during simulation.

## Overview

The circuit visualization shows exactly how the time evolution operator exp(-iH*t) is decomposed into a sequence of quantum gates using the Suzuki-Trotter method. This provides insight into:

- The structure of the quantum algorithm
- How different Trotter orders affect circuit complexity
- The decomposition of Hamiltonians into gate sequences
- The relationship between time steps and circuit depth

## Features

- **Rigorous representation**: No heuristics or approximations - circuits exactly represent the mathematical operations performed
- **Multiple formats**: Both graphical (matplotlib) and text-based output
- **Trotter order support**: Visualizes 1st, 2nd, and 4th order Suzuki-Trotter decompositions
- **Automatic decomposition**: Handles any spin-1 Hamiltonian automatically

## Usage

### Basic Example

```python
import numpy as np
import matplotlib.pyplot as plt
import qutip as qt
from qudit.qubit import StatevectorSimulator

# Initialize simulator with 2nd order Trotter decomposition
simulator = StatevectorSimulator(trotter_order=2)

# Define a Hamiltonian
Jz = qt.jmat(1, 'z')
H = 2 * np.pi * Jz

# Define time array
times = np.linspace(0, 1.0, 20)

# Get circuit representation
circuit = simulator.get_circuit(H, times)
print(f"Number of gates: {len(circuit.gates)}")
print(f"Circuit depth: {circuit.depth()}")

# Visualize the circuit
fig, ax, circuit = simulator.visualize_circuit(
    H, times,
    title="Quantum Circuit for Zeeman Effect"
)
plt.show()

# Get text representation
text = simulator.print_circuit(H, times)
print(text)
```

### In Tutorial Notebook

The tutorial notebook `qudit/tutorials/spin1_qubit_simulation.ipynb` includes circuit visualizations for all examples:

1. **Simple Hamiltonian**: Shows basic circuit structure
2. **Zeeman Effect**: Diagonal Hamiltonian (Jz only)
3. **Transverse Field**: Mixed Hamiltonian (Jz + Jx)
4. **Rabi Oscillation**: Complex Hamiltonian with raising/lowering operators

## API Reference

### StatevectorSimulator Methods

#### `get_circuit(hamiltonian, times)`

Returns a `QuantumCircuit` object representing the Trotter decomposition.

**Parameters:**
- `hamiltonian` (Qobj): 3×3 spin-1 Hamiltonian operator
- `times` (ndarray): Array of time points

**Returns:**
- `circuit` (QuantumCircuit): Circuit representation

#### `visualize_circuit(hamiltonian, times, fig=None, ax=None, title=None)`

Creates a matplotlib visualization of the quantum circuit.

**Parameters:**
- `hamiltonian` (Qobj): 3×3 spin-1 Hamiltonian operator
- `times` (ndarray): Array of time points
- `fig` (Figure, optional): Matplotlib figure to plot on
- `ax` (Axes, optional): Matplotlib axes to plot on
- `title` (str, optional): Title for the circuit diagram

**Returns:**
- `fig` (Figure): Matplotlib figure
- `ax` (Axes): Matplotlib axes
- `circuit` (QuantumCircuit): The circuit object

#### `print_circuit(hamiltonian, times)`

Returns a text representation of the circuit.

**Parameters:**
- `hamiltonian` (Qobj): 3×3 spin-1 Hamiltonian operator
- `times` (ndarray): Array of time points

**Returns:**
- `text` (str): Text representation of the circuit

### QuantumCircuit Class

The `QuantumCircuit` class stores the structure of a quantum circuit.

**Attributes:**
- `num_qubits` (int): Number of qubits (always 2 for spin-1 encoding)
- `gates` (list): List of `CircuitGate` objects
- `metadata` (dict): Additional information about the circuit

**Methods:**
- `depth()`: Returns the circuit depth
- `to_text()`: Returns text representation
- `visualize(fig, ax, title)`: Creates matplotlib visualization

## Circuit Structure

### Gate Representation

Each gate in the circuit represents a time evolution operator:

```
U(H_i)(time=dt) = exp(-i * H_i * dt)
```

where `H_i` is a term in the Hamiltonian decomposition.

### Trotter Decomposition Orders

**1st Order (Lie-Trotter):**
```
exp(-i(H₁ + H₂)dt) ≈ exp(-iH₁dt) exp(-iH₂dt)
```
- Simplest structure
- Error: O(dt²)
- Fewest gates

**2nd Order (Strang Splitting):**
```
exp(-i(H₁ + H₂)dt) ≈ exp(-iH₁dt/2) exp(-iH₂dt) exp(-iH₁dt/2)
```
- Symmetric structure
- Error: O(dt³)
- Better accuracy with moderate gate count

**4th Order (Yoshida):**
```
Composition of 2nd order steps with Yoshida coefficients
```
- Most complex structure
- Error: O(dt⁵)
- Highest accuracy but most gates

### Hamiltonian Decomposition

The simulator automatically decomposes the Hamiltonian into terms:

1. **Diagonal part** (Jz component)
2. **Off-diagonal part** (Jx, Jy components)

Each part is represented as a separate gate in the circuit.

## Examples

See the following for complete examples:

- `qudit/tutorials/spin1_qubit_simulation.ipynb`: Full tutorial with circuit visualizations
- `/tmp/test_circuit_viz.py`: Basic testing script
- `/tmp/test_notebook_context.py`: Notebook-style examples
- `/tmp/create_examples.py`: Comprehensive demonstration

## Implementation Details

### No Heuristics

The circuit visualization is **completely rigorous** with no approximations or heuristics:

- Gates exactly represent the mathematical operations performed
- Time parameters match the actual time steps used
- Decomposition follows the Suzuki-Trotter formulas precisely
- Circuit structure directly corresponds to the simulation algorithm

### Limitations

- Circuits show only the first 5 time steps to keep visualization manageable
- Japanese text in titles may not render with all fonts (functionality unaffected)
- Each gate U represents a general 2-qubit unitary that could be further decomposed into elementary gates (not implemented)

## References

1. Suzuki, M. (1976). "Generalized Trotter's formula and systematic approximants of exponential operators and inner derivations with applications to many-body problems"
2. Trotter, H. F. (1959). "On the product of semi-groups of operators"
3. Childs, A. M., et al. (2018). "Toward the first quantum simulation with quantum speedup"

## See Also

- `spin1_encoding.py`: Spin-1 to qubit encoding
- `trotter_decomposition.py`: Suzuki-Trotter implementation
- `statevector_simulator.py`: Main simulator class
