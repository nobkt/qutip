"""
Qudit module for Spin S=1 quantum dynamics simulation.

This module provides pure qudit-based (3-level) implementations for simulating
Spin S=1 quantum systems using Suzuki-Trotter decomposition. No qubit encoding
or heuristic approximations are used.

The module includes:
- Suzuki-Trotter decomposition for time evolution
- Statevector simulator for quantum dynamics
- Utility functions for Spin S=1 operators and states

Examples
--------
Basic usage:

    >>> import numpy as np
    >>> from qudit.qudit import StatevectorSimulator, get_spin1_operators, get_spin1_states
    >>> 
    >>> # Get Spin-1 operators
    >>> ops = get_spin1_operators()
    >>> Jx, Jy, Jz = ops['Jx'], ops['Jy'], ops['Jz']
    >>> 
    >>> # Define a Hamiltonian (e.g., Zeeman effect)
    >>> omega = 2 * np.pi * 1.0  # Larmor frequency
    >>> H = -omega * Jz
    >>> 
    >>> # Get initial state
    >>> states = get_spin1_states()
    >>> psi0 = states['m1']  # Start in |1, +1⟩
    >>> 
    >>> # Create simulator
    >>> sim = StatevectorSimulator(trotter_order=2)
    >>> 
    >>> # Run simulation
    >>> times = np.linspace(0, 10, 100)
    >>> result = sim.simulate(H, psi0, times)
    >>> 
    >>> # Access results
    >>> populations = result['populations']
    >>> expectations = result['expect']  # <Jx>, <Jy>, <Jz>
"""

from .trotter_decomposition import SuzukiTrotterDecomposition
from .statevector_simulator import (
    StatevectorSimulator,
    get_spin1_operators,
    get_spin1_states,
    spin_coherent_state
)
from .circuit_visualization import (
    QuditCircuit,
    QuditGate,
    visualize_state_evolution,
    visualize_bloch_sphere_trajectory
)

# Try to import MQT simulator (optional dependency)
try:
    from .mqt_simulator import MQTSimulator, MQTStatevectorSimulator, MQTShotSimulator
    _MQT_AVAILABLE = True
except ImportError:
    _MQT_AVAILABLE = False
    MQTSimulator = None
    MQTStatevectorSimulator = None
    MQTShotSimulator = None

# Try to import MQT circuit converter (optional dependency)
try:
    from .mqt_circuit_converter import MQTCircuitConverter, convert_hamiltonian_to_mqt_circuit
    _MQT_CIRCUIT_AVAILABLE = True
except ImportError:
    _MQT_CIRCUIT_AVAILABLE = False
    MQTCircuitConverter = None
    convert_hamiltonian_to_mqt_circuit = None

__all__ = [
    'SuzukiTrotterDecomposition',
    'StatevectorSimulator',
    'get_spin1_operators',
    'get_spin1_states',
    'spin_coherent_state',
    'QuditCircuit',
    'QuditGate',
    'visualize_state_evolution',
    'visualize_bloch_sphere_trajectory'
]

# Add MQT simulator if available
if _MQT_AVAILABLE:
    __all__.extend(['MQTSimulator', 'MQTStatevectorSimulator', 'MQTShotSimulator'])

# Add MQT circuit converter if available
if _MQT_CIRCUIT_AVAILABLE:
    __all__.extend(['MQTCircuitConverter', 'convert_hamiltonian_to_mqt_circuit'])

__version__ = '1.0.0'
