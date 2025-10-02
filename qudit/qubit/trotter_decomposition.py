"""
Suzuki-Trotter decomposition for time evolution of quantum systems.

This module implements various orders of Suzuki-Trotter product formulas
for approximating the exponential of a sum of operators:

exp(-i*H*dt) where H = H1 + H2 + ... + Hn

The decomposition allows efficient simulation by breaking down complex
evolution into simpler exponentials.
"""

import numpy as np
from typing import List, Callable
import qutip as qt


class SuzukiTrotterDecomposition:
    """
    Implements Suzuki-Trotter product formulas for quantum time evolution.
    
    The Suzuki-Trotter decomposition approximates:
    exp(-i*(H1 + H2 + ... + Hn)*dt) 
    
    using products of simpler exponentials exp(-i*Hi*dt).
    
    Attributes
    ----------
    order : int
        Order of the Suzuki-Trotter decomposition (1, 2, or 4)
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Suzuki-Trotter decomposition.
        
        Parameters
        ----------
        order : int, optional
            Order of the decomposition. Higher orders give better accuracy
            but require more exponentials. Supported orders: 1, 2, 4.
            Default is 2.
        """
        if order not in [1, 2, 4]:
            raise ValueError(f"Order must be 1, 2, or 4, got {order}")
        
        self.order = order
    
    def first_order_step(self, hamiltonian_terms: List[qt.Qobj], dt: float) -> qt.Qobj:
        """
        First-order Trotter decomposition (Lie-Trotter splitting).
        
        exp(-i*(H1 + H2 + ... + Hn)*dt) ≈ exp(-i*H1*dt) * exp(-i*H2*dt) * ... * exp(-i*Hn*dt)
        
        Error: O(dt^2)
        
        Parameters
        ----------
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        dt : float
            Time step
            
        Returns
        -------
        U : Qobj
            Time evolution operator for one time step
        """
        n = len(hamiltonian_terms)
        if n == 0:
            raise ValueError("At least one Hamiltonian term required")
        
        # Get dimensions from first operator
        dims = hamiltonian_terms[0].dims
        
        # Start with identity
        U = qt.qeye(dims[0])
        
        # Apply exponentials in sequence
        for H_i in hamiltonian_terms:
            U = (-1j * H_i * dt).expm() * U
        
        return U
    
    def second_order_step(self, hamiltonian_terms: List[qt.Qobj], dt: float) -> qt.Qobj:
        """
        Second-order Trotter decomposition (Strang splitting).
        
        exp(-i*(H1 + H2)*dt) ≈ exp(-i*H1*dt/2) * exp(-i*H2*dt) * exp(-i*H1*dt/2)
        
        For n terms, applies symmetric splitting:
        exp(-i*H1*dt/2) * exp(-i*H2*dt/2) * ... * exp(-i*Hn*dt) * ... * exp(-i*H2*dt/2) * exp(-i*H1*dt/2)
        
        Error: O(dt^3)
        
        Parameters
        ----------
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        dt : float
            Time step
            
        Returns
        -------
        U : Qobj
            Time evolution operator for one time step
        """
        n = len(hamiltonian_terms)
        if n == 0:
            raise ValueError("At least one Hamiltonian term required")
        
        dims = hamiltonian_terms[0].dims
        U = qt.qeye(dims[0])
        
        # Forward sweep (half steps for all but last)
        for i in range(n - 1):
            U = (-1j * hamiltonian_terms[i] * dt / 2.0).expm() * U
        
        # Full step for last term
        U = (-1j * hamiltonian_terms[n - 1] * dt).expm() * U
        
        # Backward sweep (half steps in reverse order)
        for i in range(n - 2, -1, -1):
            U = (-1j * hamiltonian_terms[i] * dt / 2.0).expm() * U
        
        return U
    
    def fourth_order_step(self, hamiltonian_terms: List[qt.Qobj], dt: float) -> qt.Qobj:
        """
        Fourth-order Suzuki-Trotter decomposition.
        
        Uses the Yoshida decomposition with coefficients that cancel
        error terms up to O(dt^5).
        
        S4(dt) = S2(p*dt) * S2(p*dt) * S2((1-4p)*dt) * S2(p*dt) * S2(p*dt)
        
        where p = 1/(4 - 4^(1/3)) and S2 is the second-order method.
        
        Error: O(dt^5)
        
        Parameters
        ----------
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        dt : float
            Time step
            
        Returns
        -------
        U : Qobj
            Time evolution operator for one time step
        """
        # Yoshida coefficients for 4th order
        p = 1.0 / (4.0 - 4.0 ** (1.0/3.0))
        
        # Apply composition of second-order steps
        U1 = self.second_order_step(hamiltonian_terms, p * dt)
        U2 = self.second_order_step(hamiltonian_terms, p * dt)
        U3 = self.second_order_step(hamiltonian_terms, (1.0 - 4.0 * p) * dt)
        U4 = self.second_order_step(hamiltonian_terms, p * dt)
        U5 = self.second_order_step(hamiltonian_terms, p * dt)
        
        U = U5 * U4 * U3 * U2 * U1
        
        return U
    
    def time_evolution_operator(self, hamiltonian_terms: List[qt.Qobj], dt: float) -> qt.Qobj:
        """
        Compute the time evolution operator for one time step.
        
        Parameters
        ----------
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        dt : float
            Time step
            
        Returns
        -------
        U : Qobj
            Time evolution operator exp(-i*H*dt) approximated using
            Suzuki-Trotter decomposition
        """
        if self.order == 1:
            return self.first_order_step(hamiltonian_terms, dt)
        elif self.order == 2:
            return self.second_order_step(hamiltonian_terms, dt)
        elif self.order == 4:
            return self.fourth_order_step(hamiltonian_terms, dt)
        else:
            raise ValueError(f"Unsupported order: {self.order}")
    
    def evolve_state(self, state: qt.Qobj, hamiltonian_terms: List[qt.Qobj], 
                     t_final: float, dt: float) -> List[qt.Qobj]:
        """
        Evolve a quantum state from t=0 to t=t_final.
        
        Parameters
        ----------
        state : Qobj
            Initial state vector
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        t_final : float
            Final time
        dt : float
            Time step for Trotter decomposition
            
        Returns
        -------
        states : list of Qobj
            List of state vectors at each time step
        """
        # Number of steps
        n_steps = int(np.ceil(t_final / dt))
        dt_actual = t_final / n_steps
        
        # Initialize state list
        states = [state]
        current_state = state
        
        # Evolve
        for _ in range(n_steps):
            U = self.time_evolution_operator(hamiltonian_terms, dt_actual)
            current_state = U * current_state
            # Normalize to prevent numerical drift
            current_state = current_state / current_state.norm()
            states.append(current_state)
        
        return states
    
    def compute_expectation_values(self, state: qt.Qobj, 
                                   hamiltonian_terms: List[qt.Qobj],
                                   observables: List[qt.Qobj],
                                   t_final: float, dt: float) -> np.ndarray:
        """
        Compute expectation values of observables during time evolution.
        
        Parameters
        ----------
        state : Qobj
            Initial state vector
        hamiltonian_terms : list of Qobj
            List of Hamiltonian terms [H1, H2, ..., Hn]
        observables : list of Qobj
            List of observables to measure
        t_final : float
            Final time
        dt : float
            Time step
            
        Returns
        -------
        expectations : ndarray
            Array of shape (n_steps+1, n_observables) containing
            expectation values at each time step
        """
        states = self.evolve_state(state, hamiltonian_terms, t_final, dt)
        
        n_steps = len(states)
        n_obs = len(observables)
        expectations = np.zeros((n_steps, n_obs))
        
        for i, psi in enumerate(states):
            for j, obs in enumerate(observables):
                expectations[i, j] = qt.expect(obs, psi)
        
        return expectations
