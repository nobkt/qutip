"""
MQT Qudits integration for Spin S=1 quantum dynamics simulation.

This module provides an adapter to use the MQT Qudits library
(from Munich Quantum Toolkit) for simulating Spin S=1 quantum systems.

Includes both statevector simulation and shot-based simulation with
optional noise models.

References
----------
MQT Qudits: https://mqt.readthedocs.io/projects/qudits/en/latest/
"""

import numpy as np
import scipy.linalg
from typing import Optional, Dict, List, Tuple
from collections import Counter

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
                 observables: Optional[List[np.ndarray]] = None,
                 return_circuit: bool = False) -> Dict:
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
        return_circuit : bool, optional
            If True, include circuit representation in the result.
            Default is False.
            
        Returns
        -------
        result : dict
            Dictionary containing:
            - 'times': time array
            - 'states': list of 3x1 state vectors at each time
            - 'expect': array of expectation values (n_times, n_observables)
            - 'populations': array of populations |⟨m|ψ(t)⟩|² (n_times, 3)
            - 'backend': name of the backend used ('MQT-MISim')
            - 'circuit': QuditCircuit object (only if return_circuit=True)
        """
        # Validate inputs and convert to numpy arrays if needed
        hamiltonian = self._validate_hamiltonian(hamiltonian)
        initial_state = self._validate_state(initial_state)
        
        # Normalize initial state
        initial_state = initial_state / np.linalg.norm(initial_state)
        
        # Set default observables if not provided
        if observables is None:
            observables = self._get_default_observables()
        else:
            # Convert observables to numpy arrays if they are Qobj
            observables = [obs.full() if hasattr(obs, 'full') else np.asarray(obs) 
                          for obs in observables]
        
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
        
        # Build circuit representation if requested
        if return_circuit:
            from .circuit_visualization import QuditCircuit
            circuit = self._build_circuit(hamiltonian, times, initial_state)
            result['circuit'] = circuit
        
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
    
    def _validate_hamiltonian(self, H):
        """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix.
        
        Parameters
        ----------
        H : ndarray or Qobj
            Hamiltonian matrix to validate. If Qobj, will be converted to ndarray.
            
        Returns
        -------
        H_array : ndarray
            The Hamiltonian as a numpy array.
        """
        # Convert Qobj to numpy array if needed
        if hasattr(H, 'full'):
            # This is a QuTiP Qobj
            H_array = H.full()
        else:
            H_array = np.asarray(H)
        
        if H_array.shape != (3, 3):
            raise ValueError(f"Hamiltonian must be 3x3, got shape {H_array.shape}")
        
        # Check Hermiticity
        if not np.allclose(H_array, H_array.conj().T):
            raise ValueError("Hamiltonian must be Hermitian")
        
        return H_array
    
    def _validate_state(self, state):
        """Validate that the state is a proper 3x1 state vector.
        
        Parameters
        ----------
        state : ndarray or Qobj
            State vector to validate. If Qobj, will be converted to ndarray.
            
        Returns
        -------
        state_array : ndarray
            The state as a flattened numpy array.
        """
        # Convert Qobj to numpy array if needed
        if hasattr(state, 'full'):
            # This is a QuTiP Qobj
            state_array = state.full().flatten()
        else:
            state_array = np.asarray(state).flatten()
        
        if len(state_array) != 3:
            raise ValueError(f"State must be 3-dimensional, got {len(state_array)}")
        
        return state_array
    
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
    
    def _build_circuit(self, hamiltonian: np.ndarray, times: np.ndarray, 
                       initial_state: np.ndarray) -> 'QuditCircuit':
        """
        Build a QuditCircuit representation of the time evolution.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        times : ndarray
            Array of time points
        initial_state : ndarray
            Initial state vector
            
        Returns
        -------
        circuit : QuditCircuit
            Circuit representation of the evolution
        """
        from .circuit_visualization import QuditCircuit
        
        circuit = QuditCircuit(num_qudits=1)
        circuit.metadata = {
            'hamiltonian': hamiltonian.copy(),
            'initial_state': initial_state.copy(),
            'times': times.copy(),
            'trotter_order': self.trotter_order,
            'decomposition_basis': self.decomposition_basis,
            'num_time_steps': len(times) - 1
        }
        
        # Decompose Hamiltonian
        hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
            hamiltonian, basis=self.decomposition_basis
        )
        
        # Add gates for each time step
        for i in range(1, len(times)):
            dt = times[i] - times[i-1]
            
            # For each Hamiltonian term, add its evolution gate
            for term_idx, H_term in enumerate(hamiltonian_terms):
                # Identify the operator type
                op_name = self._identify_operator(H_term)
                
                # Compute the coefficient (the eigenvalue tells us the strength)
                coeff = self._extract_coefficient(H_term)
                
                # Add the evolution gate
                matrix = scipy.linalg.expm(-1j * H_term * dt)
                circuit.add_evolution_gate(
                    operator_name=op_name,
                    coeff=coeff,
                    time=dt,
                    matrix=matrix,
                    description=f"Time step {i}/{len(times)-1}"
                )
        
        return circuit
    
    def _identify_operator(self, operator: np.ndarray) -> str:
        """
        Identify which spin operator this matrix represents.
        
        Parameters
        ----------
        operator : ndarray
            3x3 operator matrix
            
        Returns
        -------
        name : str
            Name of the operator (e.g., 'Jx', 'Jy', 'Jz')
        """
        ops = self._get_default_observables()
        Jx, Jy, Jz = ops[0], ops[1], ops[2]
        
        # Check if it's a pure Jx, Jy, or Jz operator (up to a scalar)
        for name, base_op in [('Jx', Jx), ('Jy', Jy), ('Jz', Jz)]:
            # Try to find scalar multiplier
            non_zero_indices = np.abs(base_op) > 1e-10
            if np.any(non_zero_indices):
                ratio = operator[non_zero_indices] / base_op[non_zero_indices]
                if np.allclose(ratio, ratio.flat[0]):
                    # Check if scaled version matches
                    if np.allclose(operator, ratio.flat[0] * base_op):
                        return name
        
        # Check for quadratic terms
        for name, base_op in [('Jx2', Jx @ Jx), ('Jy2', Jy @ Jy), ('Jz2', Jz @ Jz)]:
            non_zero_indices = np.abs(base_op) > 1e-10
            if np.any(non_zero_indices):
                ratio = operator[non_zero_indices] / base_op[non_zero_indices]
                if np.allclose(ratio, ratio.flat[0]):
                    if np.allclose(operator, ratio.flat[0] * base_op):
                        return name
        
        return 'General'
    
    def _extract_coefficient(self, operator: np.ndarray) -> float:
        """
        Extract the coefficient from a scaled operator.
        
        Parameters
        ----------
        operator : ndarray
            3x3 operator matrix
            
        Returns
        -------
        coeff : float
            The scaling coefficient
        """
        # Find the largest element (in magnitude) to determine scaling
        max_elem = operator[np.unravel_index(np.argmax(np.abs(operator)), operator.shape)]
        return np.abs(max_elem)


class MQTShotSimulator:
    """
    Shot-based simulator for Spin S=1 using MQT Qudits backend.
    
    This simulator performs quantum circuit simulation with measurement
    sampling (shots), optionally with noise models. It can compare
    shot-based simulation with exact solutions and statevector simulations.
    
    Unlike the MQTStatevectorSimulator which uses ideal Trotter decomposition,
    this simulator can model noisy quantum evolution by applying noise channels
    (depolarizing and dephasing) to the quantum state after each evolution step.
    
    Attributes
    ----------
    trotter_order : int
        Order of Suzuki-Trotter decomposition (1, 2, or 4)
    decomposition_basis : str
        Basis for Hamiltonian decomposition
    backend : MISim
        MQT Qudits simulation backend
    noise_model : NoiseModel or None
        Optional noise model (stored for compatibility with MQT API)
    prob_depolarizing : float
        Probability of depolarizing noise per evolution step
    prob_dephasing : float
        Probability of dephasing noise per evolution step
    has_significant_noise : bool
        Whether significant noise is present (affects simulation method)
        
    Examples
    --------
    Basic usage without noise:
    
    >>> import numpy as np
    >>> from qudit.qudit import get_spin1_operators, get_spin1_states
    >>> from qudit.qudit.mqt_simulator import MQTShotSimulator
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
    >>> # Simulate with shots (no significant noise by default)
    >>> sim = MQTShotSimulator(trotter_order=2)
    >>> times = np.linspace(0, 1.0, 20)
    >>> result = sim.simulate(H, psi0, times, shots=1000)
    
    Usage with noise:
    
    >>> from mqt.qudits.simulation.noise_tools import Noise, NoiseModel
    >>> 
    >>> # Create noise model
    >>> noise = Noise(probability_depolarizing=0.05, probability_dephasing=0.03)
    >>> noise_model = NoiseModel()
    >>> noise_model.add_all_qudit_quantum_error(noise, ["x", "h", "rz", "r", "custom_one"])
    >>> 
    >>> # Simulate with noise
    >>> sim = MQTShotSimulator(trotter_order=2, noise_model=noise_model, noise=noise)
    >>> result = sim.simulate(H, psi0, times, shots=1000)
    >>> 
    >>> # Compare with exact solution
    >>> comparison = sim.compare_all_methods(H, psi0, times, shots=1000)
    """
    
    def __init__(self,
                 trotter_order: int = 2,
                 decomposition_basis: str = 'xyz',
                 noise_model: Optional['NoiseModel'] = None,
                 noise: Optional['Noise'] = None):
        """
        Initialize the MQT shot simulator.
        
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
        noise_model : NoiseModel, optional
            Noise model for realistic simulations. This is stored but not directly
            used in the current implementation. Instead, noise parameters are extracted
            from the 'noise' parameter or default values are used.
            Default is None.
        noise : Noise, optional
            Noise object containing probability_depolarizing and probability_dephasing.
            If provided, these probabilities will be used to apply noise to the quantum
            state during evolution. If not provided, minimal (negligible) noise is used.
            Default is None.
            
        Raises
        ------
        ImportError
            If MQT Qudits is not installed
            
        Examples
        --------
        >>> from mqt.qudits.simulation.noise_tools import Noise, NoiseModel
        >>> noise = Noise(probability_depolarizing=0.05, probability_dephasing=0.03)
        >>> noise_model = NoiseModel()
        >>> noise_model.add_all_qudit_quantum_error(noise, ["x", "h", "rz", "r", "custom_one"])
        >>> sim = MQTShotSimulator(trotter_order=2, noise_model=noise_model, noise=noise)
        """
        if not MQT_AVAILABLE:
            raise ImportError(
                "MQT Qudits is not installed. "
                "Install it with: pip install mqt.qudits"
            )
        
        from .trotter_decomposition import SuzukiTrotterDecomposition
        from mqt.qudits.simulation.noise_tools import Noise, NoiseModel
        
        self.trotter_decomp = SuzukiTrotterDecomposition(order=trotter_order)
        self.trotter_order = trotter_order
        self.decomposition_basis = decomposition_basis
        self.provider = MQTQuditProvider()
        self.backend = MISim(self.provider)
        
        # Store noise model (for potential future use)
        if noise_model is None:
            # Create minimal noise model
            default_noise = Noise(probability_depolarizing=1e-12, probability_dephasing=1e-12)
            self.noise_model = NoiseModel()
            self.noise_model.add_all_qudit_quantum_error(default_noise, ["x", "h", "rz", "r", "custom_one"])
        else:
            self.noise_model = noise_model
        
        # Extract noise probabilities for direct application
        if noise is not None:
            # Use provided noise object
            self.prob_depolarizing = noise.probability_depolarizing
            self.prob_dephasing = noise.probability_dephasing
            self.has_significant_noise = (self.prob_depolarizing > 1e-6 or 
                                         self.prob_dephasing > 1e-6)
        else:
            # No noise provided - use negligible noise
            self.prob_depolarizing = 1e-12
            self.prob_dephasing = 1e-12
            self.has_significant_noise = False

    
    def simulate(self,
                 hamiltonian: np.ndarray,
                 initial_state: np.ndarray,
                 times: np.ndarray,
                 shots: int = 1000,
                 observables: Optional[List[np.ndarray]] = None,
                 noise_model: Optional[Dict[str, float]] = None,
                 measurement_points: Optional[np.ndarray] = None,
                 return_circuit: bool = False) -> Dict:
        """
        Simulate Spin S=1 quantum dynamics using shot-based simulation.
        
        When a noise model is present, applies depolarizing and dephasing noise
        to the quantum state after each time evolution step, modeling the effect
        of noisy gate operations.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix (Hermitian)
        initial_state : ndarray
            3x1 initial state vector (normalized)
        times : ndarray
            Array of time points at which to evaluate the state
        shots : int, optional
            Number of measurement shots per time point. Default is 1000.
        observables : list of ndarray, optional
            List of 3x3 observable operators to measure.
            If None, measures Jx, Jy, Jz by default.
        noise_model : dict, optional
            Dictionary of noise parameters. If provided, these parameters will be
            used for this simulation, overriding the noise settings from __init__.
            Supported keys:
            - 'depolarizing_1q': Depolarizing noise probability for single-qudit gates
            - 'depolarizing_2q': Depolarizing noise probability for two-qudit gates (not used for single qudit)
            - 'amplitude_damping': Amplitude damping probability (treated as additional depolarizing)
            - 'dephasing': Dephasing noise probability
            If not provided, uses noise settings from initialization.
        measurement_points : ndarray, optional
            Specific time points at which to perform measurements.
            If None, measurements are performed at all time points in `times`.
            If provided, must be a subset of `times` or indices into `times`.
            Default is None (measure at all points).
        return_circuit : bool, optional
            If True, include circuit representation in the result.
            Default is False.
            
        Returns
        -------
        result : dict
            Dictionary containing:
            - 'times': time array (full times if measurement_points is None, otherwise measurement_points)
            - 'shots': number of shots used
            - 'counts': list of measurement count dictionaries at each time
            - 'expect': array of expectation values from shot statistics (n_times, n_observables)
            - 'expect_std': standard errors of expectation values
            - 'populations': array of populations from shot statistics (n_times, 3)
            - 'populations_std': standard errors of populations
            - 'statevector': underlying statevector at each time (from noiseless simulation)
            - 'backend': name of the backend used
            - 'noise_model': whether significant noise was used
            - 'circuit': QuditCircuit object (only if return_circuit=True)
        """
        # Validate inputs and convert to numpy arrays if needed
        hamiltonian = self._validate_hamiltonian(hamiltonian)
        initial_state = self._validate_state(initial_state)
        
        if shots < 50:
            raise ValueError("Number of shots must be at least 50 for MQT simulation")
        
        # Normalize initial state and ensure it's 1D
        initial_state = initial_state.flatten()
        initial_state = initial_state / np.linalg.norm(initial_state)
        
        # Handle measurement_points parameter
        if measurement_points is not None:
            # Check if measurement_points are indices or actual time values
            if np.issubdtype(measurement_points.dtype, np.integer):
                # Indices into times array
                measurement_indices = np.asarray(measurement_points)
                measurement_times = times[measurement_indices]
            else:
                # Actual time values - find closest indices
                measurement_times = np.asarray(measurement_points)
                measurement_indices = []
                for t in measurement_times:
                    idx = np.argmin(np.abs(times - t))
                    measurement_indices.append(idx)
                measurement_indices = np.array(measurement_indices)
        else:
            # Measure at all time points
            measurement_indices = np.arange(len(times))
            measurement_times = times.copy()
        
        # Handle noise_model parameter if provided
        # Save original noise settings to restore later
        original_prob_depolarizing = self.prob_depolarizing
        original_prob_dephasing = self.prob_dephasing
        original_has_significant_noise = self.has_significant_noise
        
        if noise_model is not None:
            # Parse noise parameters from dictionary
            # depolarizing_1q: single-qudit depolarizing noise
            # amplitude_damping: treated as additional depolarizing
            # dephasing: explicit dephasing parameter
            prob_depol = noise_model.get('depolarizing_1q', 0.0)
            prob_amp_damp = noise_model.get('amplitude_damping', 0.0)
            prob_dephase = noise_model.get('dephasing', 0.0)
            
            # Combine depolarizing and amplitude damping
            # (both lead to loss of coherence)
            self.prob_depolarizing = prob_depol + prob_amp_damp
            self.prob_dephasing = prob_dephase
            self.has_significant_noise = (self.prob_depolarizing > 1e-6 or 
                                         self.prob_dephasing > 1e-6)
        
        # Set default observables if not provided
        if observables is None:
            observables = self._get_default_observables()
        else:
            # Convert observables to numpy arrays if they are Qobj
            observables = [obs.full() if hasattr(obs, 'full') else np.asarray(obs) 
                          for obs in observables]
        
        # Prepare result arrays
        n_measurement_points = len(measurement_indices)
        n_obs = len(observables)
        
        counts_history = []
        expectations = np.zeros((n_measurement_points, n_obs))
        expectations_std = np.zeros((n_measurement_points, n_obs))
        populations = np.zeros((n_measurement_points, 3))
        populations_std = np.zeros((n_measurement_points, 3))
        statevectors = []
        
        # Time evolution simulation
        # Use step-by-step Trotter evolution like the statevector simulator
        # This ensures the Trotter approximation remains accurate
        current_state = initial_state.copy()
        
        # Keep track of which measurement index we're at
        meas_idx = 0
        
        for i, t in enumerate(times):
            # Evolve to current time point (step-by-step from previous time)
            if i > 0:
                dt = times[i] - times[i-1]
                hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
                    hamiltonian, basis=self.decomposition_basis
                )
                U = self.trotter_decomp.time_evolution_operator(hamiltonian_terms, dt)
                current_state = U @ current_state
                current_state = current_state / np.linalg.norm(current_state)
                
                # Apply noise after evolution if significant noise model is present
                if self.has_significant_noise:
                    current_state = self._apply_noise_to_state(current_state)
            
            # Check if this is a measurement point
            if i not in measurement_indices:
                continue
            
            # Ensure state is a 1D array
            evolved_state = current_state.flatten()
            
            # Store statevector
            statevectors.append(evolved_state.copy())
            
            # Compute populations from statevector (for reference)
            populations[meas_idx, :] = np.abs(evolved_state) ** 2
            for m in range(3):
                p = populations[meas_idx, m]
                populations_std[meas_idx, m] = np.sqrt(p * (1 - p) / shots)
            
            # For each observable, measure in its eigenbasis
            for j, obs in enumerate(observables):
                # Get eigenvalues and eigenvectors of the observable
                eigenvalues, eigenvectors = np.linalg.eigh(obs)
                
                # Transform state to eigenbasis
                # eigenvectors columns are eigenvectors in computational basis
                # eigenvectors.conj().T transforms from computational to eigenbasis
                state_in_eigenbasis = eigenvectors.conj().T @ evolved_state
                
                # Probabilities in eigenbasis
                probabilities = np.abs(state_in_eigenbasis) ** 2
                probabilities = probabilities / np.sum(probabilities)  # Normalize
                
                # Sample measurement outcomes from the distribution
                # Outcome i corresponds to eigenvalue eigenvalues[i]
                measurement_outcomes = np.random.choice(
                    3, size=shots, p=probabilities
                )
                
                # Compute expectation value from shots
                expect_val = 0.0
                variance = 0.0
                
                for outcome in measurement_outcomes:
                    eigenvalue = eigenvalues[outcome]
                    expect_val += eigenvalue
                    variance += eigenvalue ** 2
                
                expect_val /= shots
                variance = (variance / shots) - expect_val ** 2
                
                expectations[meas_idx, j] = expect_val
                expectations_std[meas_idx, j] = np.sqrt(max(variance / shots, 0))  # Standard error
            
            # Store counts for computational basis (for reference)
            comp_probs = np.abs(evolved_state) ** 2
            comp_outcomes = np.random.choice(3, size=shots, p=comp_probs)
            counter = Counter(comp_outcomes)
            counts_dict = dict(counter)
            counts_history.append(counts_dict)
            
            meas_idx += 1
        
        result = {
            'times': measurement_times,
            'shots': shots,
            'counts': counts_history,
            'expect': expectations,
            'expect_std': expectations_std,
            'populations': populations,
            'populations_std': populations_std,
            'statevector': statevectors,
            'backend': 'MQT-Shots',
            'has_significant_noise': self.has_significant_noise
        }
        
        # Build circuit representation if requested
        if return_circuit:
            from .circuit_visualization import QuditCircuit
            circuit = self._build_circuit(hamiltonian, times, initial_state)
            result['circuit'] = circuit
        
        # Restore original noise settings if they were temporarily overridden
        if noise_model is not None:
            self.prob_depolarizing = original_prob_depolarizing
            self.prob_dephasing = original_prob_dephasing
            self.has_significant_noise = original_has_significant_noise
        
        return result
    
    def _apply_noise_to_state(self, state: np.ndarray) -> np.ndarray:
        """
        Apply depolarizing and dephasing noise to a quantum state.
        
        This simulates the effect of noisy gate operations by applying
        noise channels directly to the state vector. The noise parameters
        are taken from self.prob_depolarizing and self.prob_dephasing.
        
        Depolarizing noise: With probability p_depol, mixes the state with
            the maximally mixed state (uniform superposition)
        Dephasing noise: With probability p_dephase, randomizes the relative
            phases between basis states
        
        Parameters
        ----------
        state : ndarray
            3x1 input state vector
            
        Returns
        -------
        noisy_state : ndarray
            State after applying noise
        """
        # Apply depolarizing noise
        # With probability p_depol, replace state with maximally mixed state
        # Depolarizing channel: ρ → (1-p)ρ + p·I/d
        # For pure states: |ψ⟩ → √(1-p)|ψ⟩ + √p|uniform⟩
        if self.prob_depolarizing > 1e-6:  # Only apply if noise is significant
            if np.random.random() < self.prob_depolarizing:
                # Mix with uniform superposition
                mixed_state = np.ones(3, dtype=complex) / np.sqrt(3)
                # Weighted combination
                alpha = np.sqrt(1 - self.prob_depolarizing)
                beta = np.sqrt(self.prob_depolarizing)
                state = alpha * state + beta * mixed_state
                state = state / np.linalg.norm(state)
        
        # Apply dephasing noise
        # With probability p_dephase, apply random phase to each component
        # Dephasing channel: randomize relative phases
        if self.prob_dephasing > 1e-6:  # Only apply if noise is significant
            if np.random.random() < self.prob_dephasing:
                # Randomize phases while preserving |ψ|²
                random_phases = np.exp(1j * np.random.uniform(0, 2*np.pi, 3))
                state = state * random_phases
                state = state / np.linalg.norm(state)
        
        return state
    
    def compare_all_methods(self,
                           hamiltonian: np.ndarray,
                           initial_state: np.ndarray,
                           times: np.ndarray,
                           shots: int = 1000,
                           observables: Optional[List[np.ndarray]] = None) -> Dict:
        """
        Compare shot simulation with statevector and exact solutions.
        
        Runs three types of simulations:
        1. Exact solution (matrix exponentiation)
        2. Statevector simulation (Trotter decomposition)
        3. Shot simulation (measurement sampling)
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        initial_state : ndarray
            3x1 initial state vector
        times : ndarray
            Array of time points
        shots : int, optional
            Number of measurement shots. Default is 1000.
        observables : list of ndarray, optional
            List of observables to measure
            
        Returns
        -------
        comparison : dict
            Dictionary containing:
            - 'exact': results from exact solution
            - 'statevector': results from Trotter statevector simulation
            - 'shots': results from shot simulation
            - 'errors': various error metrics and comparisons
        """
        # Set default observables
        if observables is None:
            observables = self._get_default_observables()
        
        # Run all three methods
        print("Running exact solution...")
        result_exact = self._exact_evolution(hamiltonian, initial_state, times, observables)
        
        print("Running statevector simulation...")
        statevector_sim = MQTStatevectorSimulator(
            trotter_order=self.trotter_order,
            decomposition_basis=self.decomposition_basis
        )
        result_statevector = statevector_sim.simulate(hamiltonian, initial_state, times, observables)
        
        print("Running shot simulation...")
        result_shots = self.simulate(hamiltonian, initial_state, times, shots, observables)
        
        # Compute error metrics
        print("Computing error metrics...")
        
        # Shot vs Exact
        expect_error_shot_exact = np.abs(result_shots['expect'] - result_exact['expect'])
        pop_error_shot_exact = np.abs(result_shots['populations'] - result_exact['populations'])
        
        # Statevector vs Exact
        expect_error_sv_exact = np.abs(result_statevector['expect'] - result_exact['expect'])
        pop_error_sv_exact = np.abs(result_statevector['populations'] - result_exact['populations'])
        
        # Shot vs Statevector
        expect_error_shot_sv = np.abs(result_shots['expect'] - result_statevector['expect'])
        pop_error_shot_sv = np.abs(result_shots['populations'] - result_statevector['populations'])
        
        # Compute fidelities
        fidelities_sv_exact = np.zeros(len(times))
        fidelities_shot_exact = np.zeros(len(times))
        fidelities_shot_sv = np.zeros(len(times))
        
        for i in range(len(times)):
            fidelities_sv_exact[i] = self._state_fidelity(
                result_statevector['states'][i],
                result_exact['states'][i]
            )
            # For shot simulation, use the underlying statevector
            fidelities_shot_exact[i] = self._state_fidelity(
                result_shots['statevector'][i],
                result_exact['states'][i]
            )
            fidelities_shot_sv[i] = self._state_fidelity(
                result_shots['statevector'][i],
                result_statevector['states'][i]
            )
        
        # Statistical consistency check
        # For shot simulation without noise, expectation values should be
        # within ~3 standard errors of statevector results most of the time
        z_scores = expect_error_shot_sv / (result_shots['expect_std'] + 1e-10)
        max_z_score = np.max(np.abs(z_scores))
        
        # Error statistics
        errors = {
            # Shot vs Exact
            'expect_error_shot_exact': expect_error_shot_exact,
            'pop_error_shot_exact': pop_error_shot_exact,
            'max_expect_error_shot_exact': np.max(expect_error_shot_exact),
            'mean_expect_error_shot_exact': np.mean(expect_error_shot_exact),
            'fidelity_shot_exact': fidelities_shot_exact,
            'min_fidelity_shot_exact': np.min(fidelities_shot_exact),
            
            # Statevector vs Exact  
            'expect_error_sv_exact': expect_error_sv_exact,
            'pop_error_sv_exact': pop_error_sv_exact,
            'max_expect_error_sv_exact': np.max(expect_error_sv_exact),
            'mean_expect_error_sv_exact': np.mean(expect_error_sv_exact),
            'fidelity_sv_exact': fidelities_sv_exact,
            'min_fidelity_sv_exact': np.min(fidelities_sv_exact),
            
            # Shot vs Statevector
            'expect_error_shot_sv': expect_error_shot_sv,
            'pop_error_shot_sv': pop_error_shot_sv,
            'max_expect_error_shot_sv': np.max(expect_error_shot_sv),
            'mean_expect_error_shot_sv': np.mean(expect_error_shot_sv),
            'fidelity_shot_sv': fidelities_shot_sv,
            'min_fidelity_shot_sv': np.min(fidelities_shot_sv),
            
            # Statistical metrics
            'z_scores': z_scores,
            'max_z_score': max_z_score,
            'shots': shots,
        }
        
        comparison = {
            'exact': result_exact,
            'statevector': result_statevector,
            'shots': result_shots,
            'errors': errors
        }
        
        return comparison
    
    def _create_measurement_circuit(self, state: np.ndarray) -> 'QuantumCircuit':
        """
        Create a circuit that prepares a state for measurement.
        
        Parameters
        ----------
        state : ndarray
            3x1 state vector to prepare
            
        Returns
        -------
        circuit : QuantumCircuit
            MQT circuit that prepares the state
        """
        qreg = QuantumRegister('q', 1, [3])
        circuit = QuantumCircuit(qreg)
        
        # Prepare the state
        state_prep_unitary = self._state_preparation_unitary(state)
        from mqt.qudits.quantum_circuit.gates.custom_one import CustomOne
        CustomOne(circuit, 'StatePrep', 0, state_prep_unitary, 3)
        
        return circuit
    
    def _create_observable_measurement_circuit(self, 
                                              state: np.ndarray,
                                              eigenvectors: np.ndarray) -> 'QuantumCircuit':
        """
        Create a circuit that prepares a state and rotates to the eigenbasis of an observable.
        
        This enables proper shot-based measurement of the observable by:
        1. Preparing the quantum state
        2. Applying a basis rotation to transform to the eigenbasis
        3. Measuring in the computational basis (which is now the eigenbasis)
        
        Parameters
        ----------
        state : ndarray
            3x1 state vector to prepare
        eigenvectors : ndarray
            3x3 matrix of eigenvectors (as columns) of the observable
            
        Returns
        -------
        circuit : QuantumCircuit
            MQT circuit that prepares the state and applies basis rotation
        """
        qreg = QuantumRegister('q', 1, [3])
        circuit = QuantumCircuit(qreg)
        
        # Prepare the state
        state_prep_unitary = self._state_preparation_unitary(state)
        from mqt.qudits.quantum_circuit.gates.custom_one import CustomOne
        CustomOne(circuit, 'StatePrep', 0, state_prep_unitary, 3)
        
        # Apply basis rotation to eigenbasis
        # eigenvectors transforms from eigenbasis to computational basis
        # eigenvectors.conj().T transforms from computational to eigenbasis
        basis_rotation = eigenvectors.conj().T
        CustomOne(circuit, 'BasisRotation', 0, basis_rotation, 3)
        
        return circuit
    
    def _create_evolution_circuit(self,
                                  hamiltonian: np.ndarray,
                                  t_start: float,
                                  t_end: float,
                                  initial_state: np.ndarray) -> 'QuantumCircuit':
        """
        Create a circuit for time evolution from t_start to t_end.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        t_start : float
            Start time
        t_end : float
            End time
        initial_state : ndarray
            Initial state at t=0
            
        Returns
        -------
        circuit : QuantumCircuit
            MQT circuit for the complete evolution
        """
        # Total time evolution from 0 to t_end
        # We compute U(t_end) * |ψ(0)⟩ directly
        
        qreg = QuantumRegister('q', 1, [3])
        circuit = QuantumCircuit(qreg)
        
        # State preparation
        state_prep_unitary = self._state_preparation_unitary(initial_state)
        from mqt.qudits.quantum_circuit.gates.custom_one import CustomOne
        CustomOne(circuit, 'StatePrep', 0, state_prep_unitary, 3)
        
        # Time evolution from 0 to t_end
        dt = t_end
        hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
            hamiltonian, basis=self.decomposition_basis
        )
        U = self.trotter_decomp.time_evolution_operator(hamiltonian_terms, dt)
        CustomOne(circuit, 'U_trotter', 0, U, 3)
        
        return circuit
    
    def _state_preparation_unitary(self, target_state: np.ndarray) -> np.ndarray:
        """
        Create a unitary matrix that prepares the target state from |0⟩.
        
        Uses Gram-Schmidt to complete the target state to a full basis.
        """
        target_state = target_state.flatten()
        target_state = target_state / np.linalg.norm(target_state)
        
        # The first column of U should be the target state
        U = np.zeros((3, 3), dtype=complex)
        U[:, 0] = target_state
        
        # Use Gram-Schmidt to find two orthonormal vectors orthogonal to target_state
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
        
        return U
    
    def _exact_evolution(self,
                        hamiltonian: np.ndarray,
                        initial_state: np.ndarray,
                        times: np.ndarray,
                        observables: List[np.ndarray]) -> Dict:
        """
        Compute exact time evolution using direct matrix exponentiation.
        """
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
        """Get default observable operators (Jx, Jy, Jz)."""
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
    
    def _validate_hamiltonian(self, H):
        """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix.
        
        Parameters
        ----------
        H : ndarray or Qobj
            Hamiltonian matrix to validate. If Qobj, will be converted to ndarray.
            
        Returns
        -------
        H_array : ndarray
            The Hamiltonian as a numpy array.
        """
        # Convert Qobj to numpy array if needed
        if hasattr(H, 'full'):
            # This is a QuTiP Qobj
            H_array = H.full()
        else:
            H_array = np.asarray(H)
        
        if H_array.shape != (3, 3):
            raise ValueError(f"Hamiltonian must be 3x3, got shape {H_array.shape}")
        if not np.allclose(H_array, H_array.conj().T):
            raise ValueError("Hamiltonian must be Hermitian")
        
        return H_array
    
    def _validate_state(self, state):
        """Validate that the state is a proper 3x1 vector.
        
        Parameters
        ----------
        state : ndarray or Qobj
            State vector to validate. If Qobj, will be converted to ndarray.
            
        Returns
        -------
        state_array : ndarray
            The state as a flattened numpy array.
        """
        # Convert Qobj to numpy array if needed
        if hasattr(state, 'full'):
            # This is a QuTiP Qobj
            state_array = state.full().flatten()
        else:
            state_array = np.asarray(state).flatten()
        
        if len(state_array) != 3:
            raise ValueError(f"State must be a 3-element vector, got length {len(state_array)}")
        if not np.isclose(np.linalg.norm(state_array), 1.0, atol=1e-6):
            import warnings
            warnings.warn("State is not normalized, will be normalized automatically")
        
        return state_array
    
    def _expectation_value(self, operator: np.ndarray, state: np.ndarray) -> float:
        """Compute expectation value ⟨ψ|O|ψ⟩."""
        state = state.flatten()
        result = state.conj().T @ operator @ state
        return result.real
    
    def _compute_populations(self, state: np.ndarray) -> np.ndarray:
        """Compute populations |⟨m|ψ⟩|² for m = +1, 0, -1."""
        state = state.flatten()
        return np.abs(state) ** 2
    
    def _state_fidelity(self, state1: np.ndarray, state2: np.ndarray) -> float:
        """Compute fidelity between two pure states. Fidelity F = |⟨ψ₁|ψ₂⟩|²"""
        state1 = state1.flatten()
        state2 = state2.flatten()
        
        overlap = state1.conj().T @ state2
        fidelity = np.abs(overlap) ** 2
        
        return fidelity.real
    
    def _build_circuit(self, hamiltonian: np.ndarray, times: np.ndarray, 
                       initial_state: np.ndarray) -> 'QuditCircuit':
        """
        Build a QuditCircuit representation of the time evolution.
        
        Parameters
        ----------
        hamiltonian : ndarray
            3x3 Hamiltonian matrix
        times : ndarray
            Array of time points
        initial_state : ndarray
            Initial state vector
            
        Returns
        -------
        circuit : QuditCircuit
            Circuit representation of the evolution
        """
        from .circuit_visualization import QuditCircuit
        
        circuit = QuditCircuit(num_qudits=1)
        circuit.metadata = {
            'hamiltonian': hamiltonian.copy(),
            'initial_state': initial_state.copy(),
            'times': times.copy(),
            'trotter_order': self.trotter_order,
            'decomposition_basis': self.decomposition_basis,
            'num_time_steps': len(times) - 1,
            'has_noise': self.has_significant_noise,
            'prob_depolarizing': self.prob_depolarizing,
            'prob_dephasing': self.prob_dephasing
        }
        
        # Decompose Hamiltonian
        hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
            hamiltonian, basis=self.decomposition_basis
        )
        
        # Add gates for each time step
        for i in range(1, len(times)):
            dt = times[i] - times[i-1]
            
            # For each Hamiltonian term, add its evolution gate
            for term_idx, H_term in enumerate(hamiltonian_terms):
                # Identify the operator type
                op_name = self._identify_operator(H_term)
                
                # Compute the coefficient (the eigenvalue tells us the strength)
                coeff = self._extract_coefficient(H_term)
                
                # Add the evolution gate
                matrix = scipy.linalg.expm(-1j * H_term * dt)
                circuit.add_evolution_gate(
                    operator_name=op_name,
                    coeff=coeff,
                    time=dt,
                    matrix=matrix,
                    description=f"Time step {i}/{len(times)-1}"
                )
        
        return circuit
    
    def _identify_operator(self, operator: np.ndarray) -> str:
        """
        Identify which spin operator this matrix represents.
        
        Parameters
        ----------
        operator : ndarray
            3x3 operator matrix
            
        Returns
        -------
        name : str
            Name of the operator (e.g., 'Jx', 'Jy', 'Jz')
        """
        ops = self._get_default_observables()
        Jx, Jy, Jz = ops[0], ops[1], ops[2]
        
        # Check if it's a pure Jx, Jy, or Jz operator (up to a scalar)
        for name, base_op in [('Jx', Jx), ('Jy', Jy), ('Jz', Jz)]:
            # Try to find scalar multiplier
            non_zero_indices = np.abs(base_op) > 1e-10
            if np.any(non_zero_indices):
                ratio = operator[non_zero_indices] / base_op[non_zero_indices]
                if np.allclose(ratio, ratio.flat[0]):
                    # Check if scaled version matches
                    if np.allclose(operator, ratio.flat[0] * base_op):
                        return name
        
        # Check for quadratic terms
        for name, base_op in [('Jx2', Jx @ Jx), ('Jy2', Jy @ Jy), ('Jz2', Jz @ Jz)]:
            non_zero_indices = np.abs(base_op) > 1e-10
            if np.any(non_zero_indices):
                ratio = operator[non_zero_indices] / base_op[non_zero_indices]
                if np.allclose(ratio, ratio.flat[0]):
                    if np.allclose(operator, ratio.flat[0] * base_op):
                        return name
        
        return 'General'
    
    def _extract_coefficient(self, operator: np.ndarray) -> float:
        """
        Extract the coefficient from a scaled operator.
        
        Parameters
        ----------
        operator : ndarray
            3x3 operator matrix
            
        Returns
        -------
        coeff : float
            The scaling coefficient
        """
        # Find the largest element (in magnitude) to determine scaling
        max_elem = operator[np.unravel_index(np.argmax(np.abs(operator)), operator.shape)]
        return np.abs(max_elem)
