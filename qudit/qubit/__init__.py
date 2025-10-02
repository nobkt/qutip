"""
Qubit-based simulation of qudits (d>2 dimensional quantum systems).

This module provides qubit algorithms for simulating higher-dimensional quantum
systems using Suzuki-Trotter decomposition and statevector simulation.
"""

from .spin1_encoding import Spin1QubitEncoding
from .statevector_simulator import StatevectorSimulator
from .trotter_decomposition import SuzukiTrotterDecomposition
from .circuit_visualization import QuantumCircuit, CircuitGate, decompose_trotter_circuit

__all__ = [
    'Spin1QubitEncoding',
    'StatevectorSimulator',
    'SuzukiTrotterDecomposition',
    'QuantumCircuit',
    'CircuitGate',
    'decompose_trotter_circuit',
]
