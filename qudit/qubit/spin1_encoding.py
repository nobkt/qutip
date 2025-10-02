"""
Encoding of Spin S=1 (3-level system) into 2 qubits.

This module implements a rigorous mapping from a 3-dimensional Hilbert space
(spin S=1) to a 2-qubit (4-dimensional) Hilbert space. The encoding uses
a computational basis mapping:

    |m=+1⟩ → |00⟩
    |m= 0⟩ → |01⟩
    |m=-1⟩ → |10⟩
    |unused⟩ → |11⟩ (unused state)

The spin operators Jx, Jy, Jz are mapped to equivalent qubit operators
that preserve the commutation relations and act correctly on the
encoded subspace.
"""

import numpy as np
from typing import Tuple, List
import qutip as qt


class Spin1QubitEncoding:
    """
    Encodes Spin S=1 operators and states into a 2-qubit representation.
    
    This encoding maps the 3-dimensional spin-1 Hilbert space into a
    4-dimensional 2-qubit space, using only 3 of the 4 computational
    basis states. The encoding preserves the algebraic structure of
    the spin operators.
    
    Attributes
    ----------
    dim_qudit : int
        Dimension of the original system (3 for spin-1)
    num_qubits : int
        Number of qubits needed for encoding (2)
    """
    
    def __init__(self):
        """Initialize the Spin-1 to 2-qubit encoding."""
        self.dim_qudit = 3  # Spin-1 has 3 levels
        self.num_qubits = 2  # Need 2 qubits to encode 3 levels
        self.dim_hilbert = 2 ** self.num_qubits  # Total Hilbert space dimension
        
        # Pauli operators for each qubit
        self.I = qt.qeye(2)
        self.X = qt.sigmax()
        self.Y = qt.sigmay()
        self.Z = qt.sigmaz()
        
        # Create projection onto valid subspace
        self._create_projection_operators()
        
    def _create_projection_operators(self):
        """
        Create projection operators onto the valid 3-dimensional subspace.
        
        The projection operator P projects onto the subspace spanned by
        |00⟩, |01⟩, |10⟩, removing the unused |11⟩ state.
        """
        # Basis states in 2-qubit space
        self.state_00 = qt.tensor(qt.basis(2, 0), qt.basis(2, 0))  # |00⟩ ← |m=+1⟩
        self.state_01 = qt.tensor(qt.basis(2, 0), qt.basis(2, 1))  # |01⟩ ← |m= 0⟩
        self.state_10 = qt.tensor(qt.basis(2, 1), qt.basis(2, 0))  # |10⟩ ← |m=-1⟩
        self.state_11 = qt.tensor(qt.basis(2, 1), qt.basis(2, 1))  # |11⟩ ← unused
        
        # Projection onto valid subspace
        self.P = (self.state_00 * self.state_00.dag() +
                  self.state_01 * self.state_01.dag() +
                  self.state_10 * self.state_10.dag())
    
    def encode_state(self, spin1_state: qt.Qobj) -> qt.Qobj:
        """
        Encode a spin-1 state into 2-qubit representation.
        
        Parameters
        ----------
        spin1_state : Qobj
            A 3-dimensional state vector representing spin-1
            
        Returns
        -------
        qubit_state : Qobj
            Encoded 4-dimensional state vector in 2-qubit space
            
        Examples
        --------
        >>> encoder = Spin1QubitEncoding()
        >>> state_m1 = qt.spin_state(1, 1)  # |m=+1⟩
        >>> qubit_state = encoder.encode_state(state_m1)
        """
        if spin1_state.shape != (3, 1):
            raise ValueError(f"Expected 3x1 state vector, got {spin1_state.shape}")
        
        # Extract coefficients
        c_plus = spin1_state.data.to_array()[0, 0]
        c_zero = spin1_state.data.to_array()[1, 0]
        c_minus = spin1_state.data.to_array()[2, 0]
        
        # Encode into 2-qubit space
        qubit_state = (c_plus * self.state_00 +
                       c_zero * self.state_01 +
                       c_minus * self.state_10)
        
        return qubit_state
    
    def decode_state(self, qubit_state: qt.Qobj) -> qt.Qobj:
        """
        Decode a 2-qubit state back to spin-1 representation.
        
        Parameters
        ----------
        qubit_state : Qobj
            A 4-dimensional state vector in 2-qubit space
            
        Returns
        -------
        spin1_state : Qobj
            Decoded 3-dimensional state vector representing spin-1
        """
        if qubit_state.shape != (4, 1):
            raise ValueError(f"Expected 4x1 state vector, got {qubit_state.shape}")
        
        # Extract coefficients
        coeffs = qubit_state.data.to_array()
        c_plus = coeffs[0, 0]   # |00⟩ → |m=+1⟩
        c_zero = coeffs[1, 0]   # |01⟩ → |m= 0⟩
        c_minus = coeffs[2, 0]  # |10⟩ → |m=-1⟩
        
        # Reconstruct spin-1 state
        spin1_state = qt.Qobj([[c_plus], [c_zero], [c_minus]])
        
        # Normalize
        norm = spin1_state.norm()
        if norm > 1e-10:
            spin1_state = spin1_state / norm
        
        return spin1_state
    
    def encode_Jz(self) -> qt.Qobj:
        """
        Encode the Jz operator into 2-qubit representation.
        
        The Jz operator for spin-1 in the |m⟩ basis is:
        Jz = diag(1, 0, -1) in units of ℏ=1
        
        Returns
        -------
        Jz_qubit : Qobj
            Jz operator in 2-qubit representation
        """
        # Construct Jz in qubit basis
        # Jz|00⟩ = +1|00⟩
        # Jz|01⟩ =  0|01⟩
        # Jz|10⟩ = -1|10⟩
        # Jz|11⟩ =  0|11⟩ (by convention, unused state)
        
        Jz_matrix = np.array([
            [1.0,  0.0,  0.0,  0.0],
            [0.0,  0.0,  0.0,  0.0],
            [0.0,  0.0, -1.0,  0.0],
            [0.0,  0.0,  0.0,  0.0]
        ], dtype=complex)
        
        Jz_qubit = qt.Qobj(Jz_matrix, dims=[[2, 2], [2, 2]])
        
        return Jz_qubit
    
    def encode_Jp(self) -> qt.Qobj:
        """
        Encode the J+ (raising) operator into 2-qubit representation.
        
        The J+ operator for spin-1:
        J+|m=-1⟩ = √2|m=0⟩
        J+|m=0⟩  = √2|m=+1⟩
        J+|m=+1⟩ = 0
        
        Returns
        -------
        Jp_qubit : Qobj
            J+ operator in 2-qubit representation
        """
        sqrt2 = np.sqrt(2.0)
        
        # J+|10⟩ = √2|01⟩  (|m=-1⟩ → |m=0⟩)
        # J+|01⟩ = √2|00⟩  (|m=0⟩ → |m=+1⟩)
        # J+|00⟩ = 0       (|m=+1⟩ is maximum)
        
        Jp_matrix = np.array([
            [0.0, sqrt2,  0.0, 0.0],
            [0.0,   0.0, sqrt2, 0.0],
            [0.0,   0.0,   0.0, 0.0],
            [0.0,   0.0,   0.0, 0.0]
        ], dtype=complex)
        
        Jp_qubit = qt.Qobj(Jp_matrix, dims=[[2, 2], [2, 2]])
        
        return Jp_qubit
    
    def encode_Jm(self) -> qt.Qobj:
        """
        Encode the J- (lowering) operator into 2-qubit representation.
        
        The J- operator for spin-1:
        J-|m=+1⟩ = √2|m=0⟩
        J-|m=0⟩  = √2|m=-1⟩
        J-|m=-1⟩ = 0
        
        Returns
        -------
        Jm_qubit : Qobj
            J- operator in 2-qubit representation
        """
        sqrt2 = np.sqrt(2.0)
        
        # J-|00⟩ = √2|01⟩  (|m=+1⟩ → |m=0⟩)
        # J-|01⟩ = √2|10⟩  (|m=0⟩ → |m=-1⟩)
        # J-|10⟩ = 0       (|m=-1⟩ is minimum)
        
        Jm_matrix = np.array([
            [0.0,   0.0,   0.0, 0.0],
            [sqrt2, 0.0,   0.0, 0.0],
            [0.0, sqrt2,   0.0, 0.0],
            [0.0,   0.0,   0.0, 0.0]
        ], dtype=complex)
        
        Jm_qubit = qt.Qobj(Jm_matrix, dims=[[2, 2], [2, 2]])
        
        return Jm_qubit
    
    def encode_Jx(self) -> qt.Qobj:
        """
        Encode the Jx operator into 2-qubit representation.
        
        Jx = (J+ + J-) / 2
        
        Returns
        -------
        Jx_qubit : Qobj
            Jx operator in 2-qubit representation
        """
        Jp = self.encode_Jp()
        Jm = self.encode_Jm()
        Jx_qubit = (Jp + Jm) / 2.0
        
        return Jx_qubit
    
    def encode_Jy(self) -> qt.Qobj:
        """
        Encode the Jy operator into 2-qubit representation.
        
        Jy = (J+ - J-) / (2i)
        
        Returns
        -------
        Jy_qubit : Qobj
            Jy operator in 2-qubit representation
        """
        Jp = self.encode_Jp()
        Jm = self.encode_Jm()
        Jy_qubit = (Jp - Jm) / (2.0j)
        
        return Jy_qubit
    
    def encode_operator(self, spin1_operator: qt.Qobj) -> qt.Qobj:
        """
        Encode a general spin-1 operator into 2-qubit representation.
        
        This method works by expanding the operator in the basis of
        spin operators and mapping each component.
        
        Parameters
        ----------
        spin1_operator : Qobj
            A 3x3 operator in spin-1 space
            
        Returns
        -------
        qubit_operator : Qobj
            Encoded operator in 2-qubit space (4x4)
        """
        if spin1_operator.shape != (3, 3):
            raise ValueError(f"Expected 3x3 operator, got {spin1_operator.shape}")
        
        # Extract the 3x3 matrix
        op_matrix = spin1_operator.data.to_array()
        
        # Create 4x4 matrix by embedding into the valid subspace
        qubit_matrix = np.zeros((4, 4), dtype=complex)
        
        # Map the 3x3 operator to the |00⟩, |01⟩, |10⟩ subspace
        for i in range(3):
            for j in range(3):
                qubit_matrix[i, j] = op_matrix[i, j]
        
        qubit_operator = qt.Qobj(qubit_matrix, dims=[[2, 2], [2, 2]])
        
        return qubit_operator
    
    def verify_commutation_relations(self, tol: float = 1e-10) -> bool:
        """
        Verify that the encoded operators satisfy the angular momentum
        commutation relations: [Ji, Jj] = i*ε_ijk*Jk
        
        Parameters
        ----------
        tol : float
            Tolerance for numerical errors
            
        Returns
        -------
        valid : bool
            True if all commutation relations are satisfied
        """
        Jx = self.encode_Jx()
        Jy = self.encode_Jy()
        Jz = self.encode_Jz()
        
        # Check [Jx, Jy] = i*Jz (within the valid subspace)
        comm_xy = Jx * Jy - Jy * Jx
        expected_xy = 1j * Jz
        diff_xy = (comm_xy - expected_xy).data.to_array()
        error_xy = np.max(np.abs(diff_xy))
        
        # Check [Jy, Jz] = i*Jx
        comm_yz = Jy * Jz - Jz * Jy
        expected_yz = 1j * Jx
        diff_yz = (comm_yz - expected_yz).data.to_array()
        error_yz = np.max(np.abs(diff_yz))
        
        # Check [Jz, Jx] = i*Jy
        comm_zx = Jz * Jx - Jx * Jz
        expected_zx = 1j * Jy
        diff_zx = (comm_zx - expected_zx).data.to_array()
        error_zx = np.max(np.abs(diff_zx))
        
        max_error = max(error_xy, error_yz, error_zx)
        
        if max_error > tol:
            print(f"Commutation relation errors:")
            print(f"  [Jx, Jy] - i*Jz: {error_xy}")
            print(f"  [Jy, Jz] - i*Jx: {error_yz}")
            print(f"  [Jz, Jx] - i*Jy: {error_zx}")
            return False
        
        return True
