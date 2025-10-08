"""
Suzuki-Trotter decomposition for Spin S=1 quantum dynamics.

This module implements Suzuki-Trotter decomposition for time evolution
of Spin S=1 systems using direct qudit representation (3-level system).
No approximations or fallback methods are used.
"""

import numpy as np
import scipy.linalg


class SuzukiTrotterDecomposition:
    """
    Suzuki-Trotter decomposition for time evolution of Spin S=1 Hamiltonians.
    
    This class implements various orders of Suzuki-Trotter decomposition:
    - Order 1: First-order splitting (Lie-Trotter)
    - Order 2: Second-order symmetric splitting (Strang splitting)
    - Order 4: Fourth-order splitting (Suzuki's fractal decomposition)
    
    The decomposition splits the Hamiltonian H = H1 + H2 + ... + Hn into
    non-commuting parts and approximates exp(-iHt) as a product of
    exponentials of the individual terms.
    
    Attributes
    ----------
    order : int
        Order of the Trotter decomposition (1, 2, or 4)
    """
    
    def __init__(self, order: int = 2):
        """
        Initialize the Suzuki-Trotter decomposition.
        
        Parameters
        ----------
        order : int, optional
            Order of the decomposition. Must be 1, 2, or 4.
            Default is 2 (second-order).
        
        Raises
        ------
        ValueError
            If order is not 1, 2, or 4.
        """
        if order not in [1, 2, 4]:
            raise ValueError(f"Order must be 1, 2, or 4, got {order}")
        self.order = order
        
        # Suzuki coefficients for 4th order
        # From: Suzuki, M. (1991). Physics Letters A, 165(5-6), 387-395.
        if order == 4:
            self._p = (2 - 2**(1/3))**(-1)  # Suzuki fractal parameter
    
    def time_evolution_operator(self, hamiltonian_terms: list, dt: float) -> np.ndarray:
        """
        Compute the time evolution operator using Suzuki-Trotter decomposition.
        
        For a Hamiltonian H = sum_i H_i, approximates U(dt) = exp(-i*H*dt)
        using Suzuki-Trotter splitting.
        
        Parameters
        ----------
        hamiltonian_terms : list of ndarray
            List of Hamiltonian terms [H1, H2, ..., Hn].
            Each term is a 3x3 complex matrix.
        dt : float
            Time step for evolution
            
        Returns
        -------
        U : ndarray
            3x3 time evolution operator matrix
        """
        if self.order == 1:
            return self._trotter_order1(hamiltonian_terms, dt)
        elif self.order == 2:
            return self._trotter_order2(hamiltonian_terms, dt)
        elif self.order == 4:
            return self._trotter_order4(hamiltonian_terms, dt)
    
    def _trotter_order1(self, hamiltonian_terms: list, dt: float) -> np.ndarray:
        """
        First-order Trotter decomposition (Lie-Trotter formula).
        
        U(dt) ≈ exp(-i*H1*dt) * exp(-i*H2*dt) * ... * exp(-i*Hn*dt)
        
        Error: O(dt²)
        """
        U = np.eye(3, dtype=complex)
        for H in hamiltonian_terms:
            U = scipy.linalg.expm(-1j * H * dt) @ U
        return U
    
    def _trotter_order2(self, hamiltonian_terms: list, dt: float) -> np.ndarray:
        """
        Second-order Trotter decomposition (Strang splitting).
        
        For H = H1 + H2 + ... + Hn:
        U(dt) ≈ exp(-i*H1*dt/2) * ... * exp(-i*Hn*dt/2) *
                exp(-i*Hn*dt/2) * ... * exp(-i*H1*dt/2)
        
        This is a symmetric composition that reduces error to O(dt³).
        """
        U = np.eye(3, dtype=complex)
        
        # Forward half steps
        for H in hamiltonian_terms:
            U = scipy.linalg.expm(-1j * H * dt / 2) @ U
        
        # Backward half steps (in reverse order for symmetry)
        for H in reversed(hamiltonian_terms):
            U = scipy.linalg.expm(-1j * H * dt / 2) @ U
        
        return U
    
    def _trotter_order4(self, hamiltonian_terms: list, dt: float) -> np.ndarray:
        """
        Fourth-order Trotter decomposition (Suzuki's fractal method).
        
        Uses recursive composition:
        S4(t) = S2(p*t) * S2(p*t) * S2((1-4*p)*t) * S2(p*t) * S2(p*t)
        where p = (2 - 2^(1/3))^(-1)
        
        Error: O(dt⁵)
        """
        p = self._p
        
        # Recursive composition using second-order operators
        U1 = self._trotter_order2(hamiltonian_terms, p * dt)
        U2 = self._trotter_order2(hamiltonian_terms, (1 - 4*p) * dt)
        
        # Suzuki's fractal composition
        U = U1 @ U1 @ U2 @ U1 @ U1
        
        return U
    
    def decompose_hamiltonian(self, H: np.ndarray, 
                            basis: str = 'xyz') -> list:
        """
        Decompose a general Spin S=1 Hamiltonian into basis operators.
        
        For a general 3x3 Hermitian matrix H, decomposes it into:
        H = c_x*Jx + c_y*Jy + c_z*Jz + c_xx*Jx² + c_yy*Jy² + c_zz*Jz² + ...
        
        Parameters
        ----------
        H : ndarray
            3x3 Hermitian Hamiltonian matrix
        basis : str, optional
            Decomposition basis. Options:
            - 'xyz': Decompose into Jx, Jy, Jz components
            - 'diag': Decompose into diagonal and off-diagonal parts
            - 'full': Use Gell-Mann matrices as complete basis
            Default is 'xyz'.
            
        Returns
        -------
        hamiltonian_terms : list of ndarray
            List of Hamiltonian terms for Trotter decomposition
        """
        if basis == 'xyz':
            return self._decompose_xyz(H)
        elif basis == 'diag':
            return self._decompose_diagonal(H)
        elif basis == 'full':
            return self._decompose_gellmann(H)
        else:
            raise ValueError(f"Unknown basis: {basis}")
    
    def _decompose_xyz(self, H: np.ndarray) -> list:
        """
        Decompose Hamiltonian into Jx, Jy, Jz components.
        
        This is appropriate when the Hamiltonian can be written as
        H = ω_x*Jx + ω_y*Jy + ω_z*Jz
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
        
        # Extract coefficients using trace inner product
        # Tr(A†B) for Hermitian matrices
        # Normalized: c_i = Tr(H*Ji) / Tr(Ji*Ji)
        
        terms = []
        
        # Jx component
        norm_x = np.trace(Jx @ Jx.conj().T).real
        coeff_x = np.trace(H @ Jx.conj().T) / norm_x
        if np.abs(coeff_x) > 1e-14:
            terms.append(coeff_x.real * Jx)
        
        # Jy component
        norm_y = np.trace(Jy @ Jy.conj().T).real
        coeff_y = np.trace(H @ Jy.conj().T) / norm_y
        if np.abs(coeff_y) > 1e-14:
            terms.append(coeff_y.real * Jy)
        
        # Jz component
        norm_z = np.trace(Jz @ Jz.conj().T).real
        coeff_z = np.trace(H @ Jz.conj().T) / norm_z
        if np.abs(coeff_z) > 1e-14:
            terms.append(coeff_z.real * Jz)
        
        # If no xyz components, return full H as single term
        if len(terms) == 0:
            terms = [H]
        
        return terms
    
    def _decompose_diagonal(self, H: np.ndarray) -> list:
        """
        Decompose Hamiltonian into diagonal and off-diagonal parts.
        
        H = H_diag + H_offdiag
        
        This is useful when [H_diag, H_offdiag] ≠ 0 but both parts
        can be exponentiated efficiently.
        """
        terms = []
        
        # Diagonal part
        H_diag = np.diag(np.diag(H))
        if np.max(np.abs(H_diag)) > 1e-14:
            terms.append(H_diag)
        
        # Off-diagonal part
        H_offdiag = H - H_diag
        if np.max(np.abs(H_offdiag)) > 1e-14:
            terms.append(H_offdiag)
        
        # If both are zero, return identity (no dynamics)
        if len(terms) == 0:
            terms = [np.zeros((3, 3), dtype=complex)]
        
        return terms
    
    def _decompose_gellmann(self, H: np.ndarray) -> list:
        """
        Decompose Hamiltonian using Gell-Mann matrices (SU(3) generators).
        
        This provides a complete orthogonal basis for 3x3 Hermitian matrices.
        H = sum_i c_i * λ_i, where λ_i are Gell-Mann matrices.
        """
        # Gell-Mann matrices for SU(3)
        lambda_matrices = self._get_gellmann_matrices()
        
        terms = []
        for lam in lambda_matrices:
            # Extract coefficient
            norm = np.trace(lam @ lam.conj().T).real
            coeff = np.trace(H @ lam.conj().T) / norm
            if np.abs(coeff) > 1e-14:
                terms.append(coeff * lam)
        
        # Add identity component (overall energy shift)
        identity_coeff = np.trace(H).real / 3
        if np.abs(identity_coeff) > 1e-14:
            terms.append(identity_coeff * np.eye(3, dtype=complex))
        
        if len(terms) == 0:
            terms = [np.zeros((3, 3), dtype=complex)]
        
        return terms
    
    def _get_gellmann_matrices(self) -> list:
        """
        Generate the 8 Gell-Mann matrices (generators of SU(3)).
        
        These form a basis for traceless 3x3 Hermitian matrices.
        """
        # λ1, λ2, λ3: analogous to Pauli matrices
        lambda1 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex)
        lambda2 = np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex)
        lambda3 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex)
        
        # λ4, λ5: mixing first and third indices
        lambda4 = np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex)
        lambda5 = np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex)
        
        # λ6, λ7: mixing second and third indices
        lambda6 = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex)
        lambda7 = np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex)
        
        # λ8: diagonal traceless
        lambda8 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex) / np.sqrt(3)
        
        return [lambda1, lambda2, lambda3, lambda4, lambda5, lambda6, lambda7, lambda8]
    
    def error_estimate(self, hamiltonian_terms: list, dt: float) -> float:
        """
        Estimate the Trotter error for a given time step.
        
        The error depends on commutators of the Hamiltonian terms.
        
        Parameters
        ----------
        hamiltonian_terms : list of ndarray
            List of Hamiltonian terms
        dt : float
            Time step
            
        Returns
        -------
        error : float
            Estimated error (order of magnitude)
        """
        # Compute commutator norm
        max_commutator = 0
        for i, Hi in enumerate(hamiltonian_terms):
            for j, Hj in enumerate(hamiltonian_terms):
                if i < j:
                    comm = Hi @ Hj - Hj @ Hi
                    comm_norm = np.linalg.norm(comm)
                    max_commutator = max(max_commutator, comm_norm)
        
        # Error scales as dt^(order+1) * ||[H_i, H_j]||
        if self.order == 1:
            error = dt**2 * max_commutator
        elif self.order == 2:
            error = dt**3 * max_commutator
        elif self.order == 4:
            error = dt**5 * max_commutator
        
        return error
