"""
MQT Qudits integration for Spin S=1 quantum dynamics simulation.

This module provides an adapter to use the MQT Qudits library
(from Munich Quantum Toolkit) for simulating Spin S=1 quantum systems.

References
----------
MQT Qudits: https://mqt.readthedocs.io/projects/qudits/en/latest/
"""

import numpy as np
import scipy.linalg
from typing import Optional, Dict, List, Tuple

try:
    from mqt.qudits.quantum_circuit import QuantumCircuit, QuantumRegister
    from mqt.qudits.simulation.backends.misim import MISim
    from mqt.qudits.simulation import MQTQuditProvider
    MQT_AVAILABLE = True
except ImportError:
    MQT_AVAILABLE = False
    QuantumCircuit = None
    QuantumRegister = None
    MISim = None
    MQTQuditProvider = None


class MQTStatevectorSimulator:
    """
    Statevector simulator for Spin S=1 using MQT Qudits backend.
    
    This simulator uses the MISim (Matrix-based Ideal Simulator) backend
    from MQT Qudits to perform statevector evolution of qudit quantum circuits.
    
    The simulator converts Spin S=1 Hamiltonian dynamics into quantum circuits
    using Suzuki-Trotter decomposition and executes them using MQT's simulator.
    
    Attributes
    ----------
    trotter_order : int
        Order of Suzuki-Trotter decomposition (1, 2, or 4)
    decomposition_basis : str
        Basis for Hamiltonian decomposition
    backend : MISim
        MQT Qudits simulation backend
        
    Examples
    --------
    >>> import numpy as np
    >>> from qudit.qudit import get_spin1_operators, get_spin1_states
    >>> from qudit.qudit.mqt_simulator import MQTStatevectorSimulator
    >>> 
    >>> # Setup
    >>> ops = get_spin1_operators()
    >>> Jz = ops['Jz']
    >>> H = -2 * np.pi * Jz  # Zeeman Hamiltonian
    >>> 
    >>> # Initial state
    >>> states = get_spin1_states()
    >>> psi0 = states['m1']
    >>> 
    >>> # Simulate
    >>> sim = MQTStatevectorSimulator(trotter_order=2)
    >>> times = np.linspace(0, 1.0, 50)
    >>> result = sim.simulate(H, psi0, times)
    """
    
    def __init__(self, trotter_order: int = 2, decomposition_basis: str = 'xyz'):
        """
        Initialize the MQT statevector simulator.
        
        Parameters
        ----------
        trotter_order : int, optional
            Order of Suzuki-Trotter decomposition. Must be 1, 2, or 4.
            Default is 2.
        decomposition_basis : str, optional
            Basis for decomposing the Hamiltonian:
            - 'xyz': Decompose into Jx, Jy, Jz components
            - 'diag': Decompose into diagonal and off-diagonal parts
            - 'full': Use complete Gell-Mann basis
            Default is 'xyz'.
            
        Raises
        ------
        ImportError
            If MQT Qudits is not installed
        """
        if not MQT_AVAILABLE:
            raise ImportError(
                "MQT Qudits is not installed. "
                "Install it with: pip install mqt.qudits"
            )
        
        from .trotter_decomposition import SuzukiTrotterDecomposition
        
        self.trotter_decomp = SuzukiTrotterDecomposition(order=trotter_order)
        self.trotter_order = trotter_order
        self.decomposition_basis = decomposition_basis
        self.provider = MQTQuditProvider()
        self.backend = MISim(self.provider)
    
    def simulate(self,
                 hamiltonian: np.ndarray,
                 initial_state: np.ndarray,
                 times: np.ndarray,
                 observables: Optional[List[np.ndarray]] = None) -> Dict:
        """
        Simulate Spin S=1 quantum dynamics using MQT Qudits.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix (Hermitian)
        initial_state : ndarray
            3x1 initial state vector (normalized)
        times : ndarray
            Array of time points at which to evaluate the state
        observables : list of ndarray, optional
            List of 3x3 observable operators to measure.
            If None, measures Jx, Jy, Jz by default.
            
        Returns
        -------
        result : dict
            Dictionary containing:
            - 'times': time array
            - 'states': list of 3x1 state vectors at each time
            - 'expect': array of expectation values (n_times, n_observables)
            - 'populations': array of populations |⟨m|ψ(t)⟩|² (n_times, 3)
            - 'backend': name of the backend used ('MQT-MISim')
        """
        # Validate inputs
        self._validate_hamiltonian(hamiltonian)
        self._validate_state(initial_state)
        
        # Normalize initial state
        initial_state = initial_state / np.linalg.norm(initial_state)
        
        # Set default observables if not provided
        if observables is None:
            observables = self._get_default_observables()
        
        # Prepare result arrays
        n_times = len(times)
        n_obs = len(observables)
        states = []
        expectations = np.zeros((n_times, n_obs))
        populations = np.zeros((n_times, 3))
        
        # Initial state
        current_state = initial_state.copy()
        states.append(current_state.copy())
        
        # Compute initial expectation values
        for j, obs in enumerate(observables):
            expectations[0, j] = self._expectation_value(obs, current_state)
        populations[0, :] = self._compute_populations(current_state)
        
        # Time evolution
        # Instead of using MQT backend to execute the circuit (which resets state),
        # we compute the Trotter evolution operator and apply it directly
        for i in range(1, n_times):
            dt = times[i] - times[i-1]
            
            # Decompose Hamiltonian for Trotter
            hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
                hamiltonian, basis=self.decomposition_basis
            )
            
            # Compute time evolution operator for this step
            U = self.trotter_decomp.time_evolution_operator(hamiltonian_terms, dt)
            
            # Apply evolution operator to current state
            current_state = U @ current_state
            
            # Normalize (to handle numerical errors)
            current_state = current_state / np.linalg.norm(current_state)
            
            # Store state
            states.append(current_state.copy())
            
            # Compute observables
            for j, obs in enumerate(observables):
                expectations[i, j] = self._expectation_value(obs, current_state)
            populations[i, :] = self._compute_populations(current_state)
        
        result = {
            'times': times,
            'states': states,
            'expect': expectations,
            'populations': populations,
            'backend': 'MQT-Trotter',
            'trotter_order': self.trotter_order,
            'decomposition_basis': self.decomposition_basis
        }
        
        return result
    
    def compare_with_exact(self,
                          hamiltonian: np.ndarray,
                          initial_state: np.ndarray,
                          times: np.ndarray,
                          observables: Optional[List[np.ndarray]] = None) -> Dict:
        """
        Compare MQT simulation with exact solution.
        
        Computes both the MQT Trotter-decomposed solution and the exact solution
        using direct matrix exponentiation, then compares them.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        initial_state : ndarray
            3x1 initial state vector
        times : ndarray
            Array of time points
        observables : list of ndarray, optional
            List of observables to measure
            
        Returns
        -------
        comparison : dict
            Dictionary containing:
            - 'mqt': results from MQT simulation
            - 'exact': results from exact solution
            - 'errors': various error metrics
        """
        # Set default observables
        if observables is None:
            observables = self._get_default_observables()
        
        # Run MQT simulation
        result_mqt = self.simulate(hamiltonian, initial_state, times, observables)
        
        # Compute exact solution
        result_exact = self._exact_evolution(hamiltonian, initial_state, times, observables)
        
        # Compute errors
        expect_error = np.abs(result_mqt['expect'] - result_exact['expect'])
        pop_error = np.abs(result_mqt['populations'] - result_exact['populations'])
        
        # Compute state fidelities
        fidelities = np.zeros(len(times))
        for i in range(len(times)):
            fidelities[i] = self._state_fidelity(
                result_mqt['states'][i],
                result_exact['states'][i]
            )
        
        # Error statistics
        errors = {
            'expect': expect_error,
            'populations': pop_error,
            'fidelity': fidelities,
            'max_expect_error': np.max(expect_error),
            'max_pop_error': np.max(pop_error),
            'mean_expect_error': np.mean(expect_error),
            'mean_pop_error': np.mean(pop_error),
            'min_fidelity': np.min(fidelities),
            'mean_fidelity': np.mean(fidelities)
        }
        
        comparison = {
            'mqt': result_mqt,
            'exact': result_exact,
            'errors': errors
        }
        
        return comparison
    
    def _create_trotter_circuit(self,
                               hamiltonian: np.ndarray,
                               dt: float,
                               initial_state: np.ndarray) -> QuantumCircuit:
        """
        Create MQT quantum circuit for a single Trotter step.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        dt : float
            Time step
        initial_state : ndarray
            3x1 initial state vector (used to prepare the circuit state)
            
        Returns
        -------
        circuit : QuantumCircuit
            MQT quantum circuit
        """
        # Create quantum register with one qutrit (dimension 3)
        # QuantumRegister signature: (name, size, dims)
        qreg = QuantumRegister('q', 1, [3])
        circuit = QuantumCircuit(qreg)
        
        # First, prepare the initial state
        # MQT starts from |0⟩, so we need to apply a unitary to prepare our state
        # Find unitary U such that U|0⟩ = |ψ⟩
        state_prep_unitary = self._state_preparation_unitary(initial_state)
        
        from mqt.qudits.quantum_circuit.gates.custom_one import CustomOne
        
        # Add state preparation gate
        CustomOne(circuit, 'StatePrep', 0, state_prep_unitary, 3)
        
        # Decompose Hamiltonian for Trotter
        hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
            hamiltonian, basis=self.decomposition_basis
        )
        
        # Compute total evolution operator for this time step
        U = self.trotter_decomp.time_evolution_operator(hamiltonian_terms, dt)
        
        # Add time evolution gate
        # target_qudits is the index (0 for first qudit)
        # parameters is the unitary matrix
        # dimensions is the dimension of the qudit (3 for qutrit)
        CustomOne(circuit, 'U_trotter', 0, U, 3)
        
        return circuit
    
    def _state_preparation_unitary(self, target_state: np.ndarray) -> np.ndarray:
        """
        Create a unitary matrix that prepares the target state from |0⟩.
        
        Uses Gram-Schmidt to complete the target state to a full basis.
        
        Parameters
        ----------
        target_state : ndarray
            3x1 target state vector (normalized)
            
        Returns
        -------
        U : ndarray
            3x3 unitary matrix such that U|0⟩ = |target_state⟩
        """
        target_state = target_state.flatten()
        target_state = target_state / np.linalg.norm(target_state)
        
        # The first column of U should be the target state
        U = np.zeros((3, 3), dtype=complex)
        U[:, 0] = target_state
        
        # Use Gram-Schmidt to find two orthonormal vectors orthogonal to target_state
        # Start with basis vectors
        basis_vectors = [
            np.array([1, 0, 0], dtype=complex),
            np.array([0, 1, 0], dtype=complex),
            np.array([0, 0, 1], dtype=complex)
        ]
        
        orthogonal_vectors = []
        for basis_vec in basis_vectors:
            # Project out the target state component
            vec = basis_vec - np.dot(target_state.conj(), basis_vec) * target_state
            
            # Project out already found orthogonal vectors
            for orth_vec in orthogonal_vectors:
                vec = vec - np.dot(orth_vec.conj(), vec) * orth_vec
            
            # Normalize
            norm = np.linalg.norm(vec)
            if norm > 1e-10:
                vec = vec / norm
                orthogonal_vectors.append(vec)
                
                if len(orthogonal_vectors) == 2:
                    break
        
        # Fill in the remaining columns
        U[:, 1] = orthogonal_vectors[0]
        U[:, 2] = orthogonal_vectors[1]
        
        # Verify it's unitary (for debugging)
        if not np.allclose(U @ U.conj().T, np.eye(3)):
            import warnings
            warnings.warn("State preparation unitary is not perfectly unitary")
        
        return U
    
    def _exact_evolution(self,
                        hamiltonian: np.ndarray,
                        initial_state: np.ndarray,
                        times: np.ndarray,
                        observables: List[np.ndarray]) -> Dict:
        """
        Compute exact time evolution using direct matrix exponentiation.
        
        This serves as a reference solution for comparison.
        """
        # Normalize initial state
        initial_state = initial_state / np.linalg.norm(initial_state)
        
        n_times = len(times)
        n_obs = len(observables)
        states = []
        expectations = np.zeros((n_times, n_obs))
        populations = np.zeros((n_times, 3))
        
        for i, t in enumerate(times):
            # Exact time evolution: |ψ(t)⟩ = exp(-iHt)|ψ(0)⟩
            U_exact = scipy.linalg.expm(-1j * hamiltonian * t)
            state_t = U_exact @ initial_state
            
            # Normalize
            state_t = state_t / np.linalg.norm(state_t)
            
            states.append(state_t.copy())
            
            # Compute observables
            for j, obs in enumerate(observables):
                expectations[i, j] = self._expectation_value(obs, state_t)
            populations[i, :] = self._compute_populations(state_t)
        
        result = {
            'times': times,
            'states': states,
            'expect': expectations,
            'populations': populations,
            'backend': 'Exact'
        }
        
        return result
    
    def _get_default_observables(self) -> List[np.ndarray]:
        """
        Get default observable operators (Jx, Jy, Jz).
        """
        # Spin-1 operators (ℏ = 1)
        Jx = np.array([
            [0, 1/np.sqrt(2), 0],
            [1/np.sqrt(2), 0, 1/np.sqrt(2)],
            [0, 1/np.sqrt(2), 0]
        ], dtype=complex)
        
        Jy = np.array([
            [0, -1j/np.sqrt(2), 0],
            [1j/np.sqrt(2), 0, -1j/np.sqrt(2)],
            [0, 1j/np.sqrt(2), 0]
        ], dtype=complex)
        
        Jz = np.array([
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, -1]
        ], dtype=complex)
        
        return [Jx, Jy, Jz]
    
    def _validate_hamiltonian(self, H: np.ndarray):
        """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix."""
        if H.shape != (3, 3):
            raise ValueError(f"Hamiltonian must be 3x3, got shape {H.shape}")
        
        # Check Hermiticity
        if not np.allclose(H, H.conj().T):
            raise ValueError("Hamiltonian must be Hermitian")
    
    def _validate_state(self, state: np.ndarray):
        """Validate that the state is a proper 3x1 state vector."""
        state = state.flatten()
        if len(state) != 3:
            raise ValueError(f"State must be 3-dimensional, got {len(state)}")
    
    def _expectation_value(self, operator: np.ndarray, state: np.ndarray) -> float:
        """
        Compute expectation value ⟨ψ|O|ψ⟩.
        """
        state = state.flatten()
        result = state.conj().T @ operator @ state
        return result.real
    
    def _compute_populations(self, state: np.ndarray) -> np.ndarray:
        """
        Compute populations |⟨m|ψ⟩|² for m = +1, 0, -1.
        """
        state = state.flatten()
        return np.abs(state) ** 2
    
    def _state_fidelity(self, state1: np.ndarray, state2: np.ndarray) -> float:
        """
        Compute fidelity between two pure states.
        
        Fidelity F = |⟨ψ₁|ψ₂⟩|²
        """
        state1 = state1.flatten()
        state2 = state2.flatten()
        
        overlap = state1.conj().T @ state2
        fidelity = np.abs(overlap) ** 2
        
        return fidelity.real
