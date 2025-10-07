"""
Statevector simulator for qubit-encoded quantum dynamics.

This module provides a statevector simulator that combines the qubit encoding
and Suzuki-Trotter decomposition to simulate spin-1 quantum dynamics using
qubit algorithms.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import qutip as qt

from .spin1_encoding import Spin1QubitEncoding
from .trotter_decomposition import SuzukiTrotterDecomposition
from .circuit_visualization import QuantumCircuit, decompose_trotter_circuit


class StatevectorSimulator:
    """
    Statevector simulator for spin-1 quantum dynamics using qubit encoding.
    
    This simulator takes a spin-1 Hamiltonian and initial state, encodes them
    into 2-qubit representation, and uses Suzuki-Trotter decomposition to
    evolve the state in time. It then decodes the results back to spin-1
    representation for analysis.
    
    Attributes
    ----------
    encoder : Spin1QubitEncoding
        The encoder for mapping spin-1 to qubits
    trotter : SuzukiTrotterDecomposition
        The Suzuki-Trotter decomposition engine
    order : int
        Order of Trotter decomposition
    """
    
    def __init__(self, trotter_order: int = 2):
        """
        Initialize the statevector simulator.
        
        Parameters
        ----------
        trotter_order : int, optional
            Order of Suzuki-Trotter decomposition (1, 2, or 4).
            Default is 2.
        """
        self.encoder = Spin1QubitEncoding()
        self.trotter = SuzukiTrotterDecomposition(order=trotter_order)
        self.order = trotter_order
    
    def simulate(self, 
                 hamiltonian: qt.Qobj,
                 initial_state: qt.Qobj,
                 times: np.ndarray,
                 observables: Optional[List[qt.Qobj]] = None) -> Dict:
        """
        Simulate spin-1 quantum dynamics using qubit encoding.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian operator
        initial_state : Qobj
            3x1 initial state vector for spin-1
        times : ndarray
            Array of time points at which to evaluate the state
        observables : list of Qobj, optional
            List of 3x3 spin-1 operators to measure. If None, measures
            Jx, Jy, Jz by default.
            
        Returns
        -------
        result : dict
            Dictionary containing:
            - 'times': time array
            - 'states': list of spin-1 states at each time
            - 'states_qubit': list of 2-qubit states at each time
            - 'expect': array of expectation values (n_times, n_observables)
            - 'populations': array of populations |⟨m|ψ(t)⟩|² (n_times, 3)
        """
        # Set default observables if not provided
        if observables is None:
            observables = [qt.jmat(1, 'x'), qt.jmat(1, 'y'), qt.jmat(1, 'z')]
        
        # Encode initial state
        psi0_qubit = self.encoder.encode_state(initial_state)
        
        # Decompose Hamiltonian into terms (for Trotter decomposition)
        # For a general Hamiltonian, we can decompose it into Jx, Jy, Jz components
        hamiltonian_terms_qubit = self._decompose_hamiltonian(hamiltonian)
        
        # Prepare arrays for results
        n_times = len(times)
        n_obs = len(observables)
        states_spin1 = []
        states_qubit = []
        expectations = np.zeros((n_times, n_obs))
        populations = np.zeros((n_times, 3))
        
        # Initial values
        current_state_qubit = psi0_qubit
        states_qubit.append(current_state_qubit)
        states_spin1.append(initial_state)
        
        # Compute initial expectation values
        for j, obs in enumerate(observables):
            expectations[0, j] = qt.expect(obs, initial_state)
        populations[0, :] = self._compute_populations(initial_state)
        
        # Time evolution
        for i in range(1, n_times):
            dt = times[i] - times[i-1]
            
            # Evolve one time step
            U = self.trotter.time_evolution_operator(hamiltonian_terms_qubit, dt)
            current_state_qubit = U * current_state_qubit
            
            # Normalize
            current_state_qubit = current_state_qubit / current_state_qubit.norm()
            
            # Decode back to spin-1
            current_state_spin1 = self.encoder.decode_state(current_state_qubit)
            
            # Store states
            states_qubit.append(current_state_qubit)
            states_spin1.append(current_state_spin1)
            
            # Compute expectation values
            for j, obs in enumerate(observables):
                expectations[i, j] = qt.expect(obs, current_state_spin1)
            populations[i, :] = self._compute_populations(current_state_spin1)
        
        result = {
            'times': times,
            'states': states_spin1,
            'states_qubit': states_qubit,
            'expect': expectations,
            'populations': populations
        }
        
        return result
    
    def _decompose_hamiltonian(self, hamiltonian: qt.Qobj) -> List[qt.Qobj]:
        """
        Decompose a spin-1 Hamiltonian into qubit operator terms.
        
        For Trotter decomposition, we need to express the Hamiltonian as
        a sum of terms. We decompose it into components along Jx, Jy, Jz.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian
            
        Returns
        -------
        hamiltonian_terms : list of Qobj
            List of 4x4 qubit Hamiltonian terms
        """
        # Get the spin-1 operators
        Jx_spin1 = qt.jmat(1, 'x')
        Jy_spin1 = qt.jmat(1, 'y')
        Jz_spin1 = qt.jmat(1, 'z')
        
        # Extract coefficients by computing Tr(H * Ji) / Tr(Ji^2)
        # This gives the component of H along each spin direction
        
        # For a more general approach, we encode the full Hamiltonian
        # and decompose it into terms that can be efficiently exponentiated
        
        # Encode the Hamiltonian
        H_qubit = self.encoder.encode_operator(hamiltonian)
        
        # For Trotter decomposition, we need to split into non-commuting parts
        # A simple approach: decompose into diagonal (Jz) and off-diagonal (Jx, Jy) parts
        
        # Get qubit operators
        Jx_qubit = self.encoder.encode_Jx()
        Jy_qubit = self.encoder.encode_Jy()
        Jz_qubit = self.encoder.encode_Jz()
        
        # Extract coefficients for each component
        # This is done by computing expectation values in the operator basis
        
        # For simplicity and rigor, we'll use the encoded Hamiltonian directly
        # and split it into Jz (diagonal) and Jx+Jy (off-diagonal) parts
        
        H_matrix = hamiltonian.data.to_array()
        
        # Diagonal part (Jz component)
        diag_elements = np.diag(np.diag(H_matrix))
        H_diag_spin1 = qt.Qobj(diag_elements)
        H_diag_qubit = self.encoder.encode_operator(H_diag_spin1)
        
        # Off-diagonal part
        offdiag_elements = H_matrix - diag_elements
        H_offdiag_spin1 = qt.Qobj(offdiag_elements)
        H_offdiag_qubit = self.encoder.encode_operator(H_offdiag_spin1)
        
        # Return terms for Trotter decomposition
        terms = []
        if np.max(np.abs(H_diag_qubit.data.to_array())) > 1e-14:
            terms.append(H_diag_qubit)
        if np.max(np.abs(H_offdiag_qubit.data.to_array())) > 1e-14:
            terms.append(H_offdiag_qubit)
        
        # If no terms, return full Hamiltonian as single term
        if len(terms) == 0:
            terms = [H_qubit]
        
        return terms
    
    def _compute_populations(self, state: qt.Qobj) -> np.ndarray:
        """
        Compute populations |⟨m|ψ⟩|² for m = +1, 0, -1.
        
        Parameters
        ----------
        state : Qobj
            3x1 spin-1 state vector
            
        Returns
        -------
        populations : ndarray
            Array [P(m=+1), P(m=0), P(m=-1)]
        """
        coeffs = state.data.to_array()
        pops = np.abs(coeffs.flatten()) ** 2
        return pops
    
    def compare_with_exact(self,
                          hamiltonian: qt.Qobj,
                          initial_state: qt.Qobj,
                          times: np.ndarray,
                          observables: Optional[List[qt.Qobj]] = None) -> Dict:
        """
        Compare qubit simulation with exact QuTiP solution.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian operator
        initial_state : Qobj
            3x1 initial state vector for spin-1
        times : ndarray
            Array of time points
        observables : list of Qobj, optional
            List of observables to measure
            
        Returns
        -------
        comparison : dict
            Dictionary containing:
            - 'qubit': results from qubit simulation
            - 'exact': results from exact QuTiP solver
            - 'errors': errors in expectation values and populations
        """
        # Set default observables
        if observables is None:
            observables = [qt.jmat(1, 'x'), qt.jmat(1, 'y'), qt.jmat(1, 'z')]
        
        # Run qubit simulation
        result_qubit = self.simulate(hamiltonian, initial_state, times, observables)
        
        # Run exact simulation using QuTiP
        # Note: We need to explicitly store states to compute populations
        result_exact = qt.sesolve(hamiltonian, initial_state, times, 
                                   e_ops=observables,
                                   options={'store_states': True})
        
        # Compute populations for exact solution
        populations_exact = np.zeros((len(times), 3))
        for i, t in enumerate(times):
            # Get exact state at time t
            if hasattr(result_exact.states[i], 'data'):
                state_t = result_exact.states[i]
                populations_exact[i, :] = self._compute_populations(state_t)
        
        # Compute errors
        expect_error = np.abs(result_qubit['expect'] - 
                             np.array(result_exact.expect).T)
        pop_error = np.abs(result_qubit['populations'] - populations_exact)
        
        comparison = {
            'qubit': result_qubit,
            'exact': {
                'times': times,
                'expect': np.array(result_exact.expect).T,
                'populations': populations_exact,
                'states': result_exact.states
            },
            'errors': {
                'expect': expect_error,
                'populations': pop_error,
                'max_expect_error': np.max(expect_error),
                'max_pop_error': np.max(pop_error),
                'mean_expect_error': np.mean(expect_error),
                'mean_pop_error': np.mean(pop_error)
            }
        }
        
        return comparison
    
    def get_circuit(self, hamiltonian: qt.Qobj, times: np.ndarray) -> QuantumCircuit:
        """
        Get the quantum circuit representation for simulating the given Hamiltonian.
        
        This method generates the quantum circuit that would be used to simulate
        the time evolution under the given Hamiltonian. The circuit represents
        the Suzuki-Trotter decomposition applied at each time step.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian operator
        times : ndarray
            Array of time points at which to evaluate the state
            
        Returns
        -------
        circuit : QuantumCircuit
            Quantum circuit representation of the simulation
        """
        # Decompose Hamiltonian into terms (same as in simulate)
        hamiltonian_terms_qubit = self._decompose_hamiltonian(hamiltonian)
        
        # Calculate time step
        if len(times) > 1:
            dt = times[1] - times[0]
            num_steps = len(times) - 1
        else:
            dt = 0.0
            num_steps = 0
        
        # Generate circuit for the Trotter decomposition
        circuit = decompose_trotter_circuit(
            hamiltonian_terms_qubit, 
            dt, 
            order=self.order,
            num_steps=min(num_steps, 5)  # Limit visualization to first 5 steps
        )
        
        return circuit
    
    def visualize_circuit(self, hamiltonian: qt.Qobj, times: np.ndarray, 
                         fig=None, ax=None, title: Optional[str] = None):
        """
        Visualize the quantum circuit for simulating the given Hamiltonian.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian operator
        times : ndarray
            Array of time points
        fig : matplotlib.figure.Figure, optional
            Figure to plot on
        ax : matplotlib.axes.Axes, optional
            Axes to plot on
        title : str, optional
            Title for the circuit diagram
            
        Returns
        -------
        fig : Figure
            The matplotlib figure
        ax : Axes
            The matplotlib axes
        circuit : QuantumCircuit
            The quantum circuit object
        """
        circuit = self.get_circuit(hamiltonian, times)
        
        if title is None:
            title = f"Suzuki-Trotter Circuit (Order {self.order})"
        
        fig, ax = circuit.visualize(fig=fig, ax=ax, title=title)
        
        return fig, ax, circuit
    
    def print_circuit(self, hamiltonian: qt.Qobj, times: np.ndarray) -> str:
        """
        Get a text representation of the quantum circuit.
        
        Parameters
        ----------
        hamiltonian : Qobj
            3x3 spin-1 Hamiltonian operator
        times : ndarray
            Array of time points
            
        Returns
        -------
        text : str
            Text representation of the circuit
        """
        circuit = self.get_circuit(hamiltonian, times)
        return circuit.to_text()
