"""
Statevector simulator for Spin S=1 quantum dynamics using Suzuki-Trotter decomposition.

This module implements a pure qudit-based statevector simulator for Spin S=1 systems.
It uses direct 3-level representation without any qubit encoding or approximations.
"""

import numpy as np
import scipy.linalg
from typing import Optional, Dict, List, Tuple


class StatevectorSimulator:
    """
    Statevector simulator for Spin S=1 quantum dynamics.
    
    This simulator evolves Spin S=1 states using Suzuki-Trotter decomposition
    of the time evolution operator. It operates directly on 3-dimensional
    qudit states without any encoding or approximations.
    
    The simulator integrates the time-dependent Schrödinger equation:
    iℏ ∂|ψ⟩/∂t = H|ψ⟩
    
    using Suzuki-Trotter decomposition to approximate the time evolution operator:
    U(dt) = exp(-iHdt/ℏ)
    
    Attributes
    ----------
    trotter_order : int
        Order of Suzuki-Trotter decomposition (1, 2, or 4)
    decomposition_basis : str
        Basis for Hamiltonian decomposition ('xyz', 'diag', or 'full')
    """
    
    def __init__(self, trotter_order: int = 2, decomposition_basis: str = 'diag'):
        """
        Initialize the statevector simulator.
        
        Parameters
        ----------
        trotter_order : int, optional
            Order of Suzuki-Trotter decomposition. Must be 1, 2, or 4.
            Default is 2 (second-order splitting).
        decomposition_basis : str, optional
            Basis for decomposing the Hamiltonian:
            - 'xyz': Decompose into Jx, Jy, Jz components
            - 'diag': Decompose into diagonal and off-diagonal parts
            - 'full': Use complete Gell-Mann basis
            Default is 'diag'.
        """
        from .trotter_decomposition import SuzukiTrotterDecomposition
        
        self.trotter_decomp = SuzukiTrotterDecomposition(order=trotter_order)
        self.trotter_order = trotter_order
        self.decomposition_basis = decomposition_basis
    
    def simulate(self,
                 hamiltonian: np.ndarray,
                 initial_state: np.ndarray,
                 times: np.ndarray,
                 observables: Optional[List[np.ndarray]] = None) -> Dict:
        """
        Simulate Spin S=1 quantum dynamics.
        
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
            - 'fidelity': fidelity with exact solution if available
        """
        # Validate inputs
        self._validate_hamiltonian(hamiltonian)
        self._validate_state(initial_state)
        
        # Normalize initial state
        initial_state = initial_state / np.linalg.norm(initial_state)
        
        # Set default observables if not provided
        if observables is None:
            observables = self._get_default_observables()
        
        # Decompose Hamiltonian for Trotter decomposition
        hamiltonian_terms = self.trotter_decomp.decompose_hamiltonian(
            hamiltonian, basis=self.decomposition_basis
        )
        
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
        for i in range(1, n_times):
            dt = times[i] - times[i-1]
            
            # Compute time evolution operator
            U = self.trotter_decomp.time_evolution_operator(hamiltonian_terms, dt)
            
            # Evolve state
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
        Compare Trotter simulation with exact solution.
        
        Computes both the Trotter-decomposed solution and the exact solution
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
            - 'trotter': results from Trotter simulation
            - 'exact': results from exact solution
            - 'errors': various error metrics
        """
        # Set default observables
        if observables is None:
            observables = self._get_default_observables()
        
        # Run Trotter simulation
        result_trotter = self.simulate(hamiltonian, initial_state, times, observables)
        
        # Compute exact solution
        result_exact = self._exact_evolution(hamiltonian, initial_state, times, observables)
        
        # Compute errors
        expect_error = np.abs(result_trotter['expect'] - result_exact['expect'])
        pop_error = np.abs(result_trotter['populations'] - result_exact['populations'])
        
        # Compute state fidelities
        fidelities = np.zeros(len(times))
        for i in range(len(times)):
            fidelities[i] = self._state_fidelity(
                result_trotter['states'][i],
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
            'trotter': result_trotter,
            'exact': result_exact,
            'errors': errors
        }
        
        return comparison
    
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
            'populations': populations
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
        
        # Check normalization (with tolerance)
        norm = np.linalg.norm(state)
        if not np.isclose(norm, 1.0, atol=1e-6):
            # We'll normalize it, but warn
            pass
    
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
        
        Returns
        -------
        populations : ndarray
            Array [P(m=+1), P(m=0), P(m=-1)]
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


def get_spin1_operators() -> Dict[str, np.ndarray]:
    """
    Get standard Spin S=1 operators.
    
    Returns
    -------
    operators : dict
        Dictionary containing:
        - 'Jx', 'Jy', 'Jz': Cartesian components
        - 'Jp', 'Jm': Raising and lowering operators
        - 'J2': Total angular momentum squared
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
    
    Jp = np.array([
        [0, np.sqrt(2), 0],
        [0, 0, np.sqrt(2)],
        [0, 0, 0]
    ], dtype=complex)
    
    Jm = np.array([
        [0, 0, 0],
        [np.sqrt(2), 0, 0],
        [0, np.sqrt(2), 0]
    ], dtype=complex)
    
    J2 = 2 * np.eye(3, dtype=complex)  # J²|j,m⟩ = j(j+1)|j,m⟩ = 2|1,m⟩
    
    return {
        'Jx': Jx,
        'Jy': Jy,
        'Jz': Jz,
        'Jp': Jp,
        'Jm': Jm,
        'J2': J2
    }


def get_spin1_states() -> Dict[str, np.ndarray]:
    """
    Get standard Spin S=1 basis states.
    
    Returns
    -------
    states : dict
        Dictionary containing:
        - 'm1': |1, +1⟩ state
        - 'm0': |1, 0⟩ state
        - 'm_1': |1, -1⟩ state
    """
    m1 = np.array([[1], [0], [0]], dtype=complex)    # |1, +1⟩
    m0 = np.array([[0], [1], [0]], dtype=complex)    # |1, 0⟩
    m_1 = np.array([[0], [0], [1]], dtype=complex)   # |1, -1⟩
    
    return {
        'm1': m1,
        'm0': m0,
        'm_1': m_1
    }


def spin_coherent_state(theta: float, phi: float) -> np.ndarray:
    """
    Generate a Spin S=1 coherent state.
    
    The coherent state pointing in direction (θ, φ) is given by:
    |θ, φ⟩ = exp(-iφJ_z) exp(-iθJ_y) |1, 1⟩
    
    Explicit form:
    |θ, φ⟩ = [cos²(θ/2) e^(-iφ), sin(θ)/√2, sin²(θ/2) e^(iφ)]ᵀ
    
    Parameters
    ----------
    theta : float
        Polar angle (0 to π)
    phi : float
        Azimuthal angle (0 to 2π)
        
    Returns
    -------
    state : ndarray
        3x1 coherent state vector
    """
    state = np.array([
        [np.cos(theta/2)**2 * np.exp(-1j*phi)],
        [np.sin(theta) / np.sqrt(2)],
        [np.sin(theta/2)**2 * np.exp(1j*phi)]
    ], dtype=complex)
    
    # Normalize (should already be normalized, but ensure it)
    state = state / np.linalg.norm(state)
    
    return state
