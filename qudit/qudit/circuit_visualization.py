"""
Quantum circuit representation and visualization for qudit (3-level) quantum dynamics.

This module provides functionality to represent and visualize the quantum circuits
for Spin S=1 systems using native 3-level qudits (qutrits). This is a pure qudit
implementation without any qubit encoding.

Mathematical Foundation
-----------------------
For a Spin S=1 system, we work with 3-dimensional Hilbert space where the
computational basis states are |m⟩ with m ∈ {+1, 0, -1}.

Spin operators in this basis:
    Jz = ℏ * diag(1, 0, -1)
    J+ = ℏ√2 * (|1⟩⟨0| + |0⟩⟨-1|)
    J- = ℏ√2 * (|0⟩⟨1| + |-1⟩⟨0|)
    Jx = (J+ + J-)/2
    Jy = (J+ - J-)/(2i)

Time evolution operators for Hamiltonian H:
    U(t) = exp(-iHt/ℏ)

For Trotter decomposition with H = ∑ᵢ Hᵢ:
    U(Δt) ≈ ∏ᵢ exp(-iHᵢΔt/ℏ) + O(Δt²)  (first order)
    U(Δt) ≈ ∏ᵢ exp(-iHᵢΔt/2ℏ) ∏ᵢ₊₁ exp(-iHᵢΔt/2ℏ) + O(Δt³)  (second order)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches


class QuditGate:
    """
    Represents a single quantum gate operating on a 3-level qudit (qutrit).
    
    Attributes
    ----------
    name : str
        Name of the gate (e.g., 'Rx', 'Ry', 'Rz', 'U')
    qudits : list of int
        List of qudit indices this gate acts on (typically [0] for single-qudit)
    params : dict
        Parameters for the gate (e.g., rotation angles, evolution time)
    matrix : np.ndarray, optional
        The 3×3 unitary matrix representation of the gate
    description : str
        Detailed description of what the gate does mathematically
    """
    
    def __init__(self, name: str, qudits: List[int], params: Optional[Dict] = None,
                 matrix: Optional[np.ndarray] = None, description: str = ""):
        """
        Initialize a qudit gate.
        
        Parameters
        ----------
        name : str
            Name of the gate
        qudits : list of int
            Qudit indices the gate acts on
        params : dict, optional
            Parameters for the gate
        matrix : np.ndarray, optional
            3×3 unitary matrix representation
        description : str, optional
            Mathematical description of the gate
        """
        self.name = name
        self.qudits = qudits
        self.params = params or {}
        self.matrix = matrix
        self.description = description
    
    def __repr__(self):
        param_str = ""
        if self.params:
            param_str = f"({', '.join(f'{k}={v:.4f}' for k, v in self.params.items())})"
        qudit_str = ','.join(map(str, self.qudits))
        return f"{self.name}{param_str}[qutrit:{qudit_str}]"
    
    def get_mathematical_form(self) -> str:
        """
        Get a LaTeX-formatted mathematical representation of the gate.
        
        Returns
        -------
        formula : str
            LaTeX string representing the gate mathematically
        """
        if self.name.startswith('exp_Jx'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_x/\\hbar}}$"
        elif self.name.startswith('exp_Jy'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_y/\\hbar}}$"
        elif self.name.startswith('exp_Jz'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_z/\\hbar}}$"
        elif self.name.startswith('exp_Jx2'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_x^2/\\hbar}}$"
        elif self.name.startswith('exp_Jy2'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_y^2/\\hbar}}$"
        elif self.name.startswith('exp_Jz2'):
            theta = self.params.get('time', 0) * self.params.get('coeff', 1)
            return f"$e^{{-i({theta:.4f})J_z^2/\\hbar}}$"
        elif self.name.startswith('U'):
            if 'time' in self.params:
                return f"$U(t={self.params['time']:.4f})$"
            return "$U$"
        return self.name


class QuditCircuit:
    """
    Represents a quantum circuit for a 3-level qudit (qutrit) system.
    
    This class stores the structure of a Spin S=1 quantum circuit and provides
    methods for visualization and analysis. The circuit represents the time
    evolution decomposed using Suzuki-Trotter decomposition.
    
    Attributes
    ----------
    num_qudits : int
        Number of qudits in the circuit (typically 1 for single Spin S=1)
    gates : list of QuditGate
        List of gates in the circuit, in order of application
    metadata : dict
        Additional metadata (e.g., Hamiltonian info, Trotter order, time step)
    """
    
    def __init__(self, num_qudits: int = 1):
        """
        Initialize a qudit circuit.
        
        Parameters
        ----------
        num_qudits : int, default=1
            Number of qudits (typically 1 for single Spin S=1 particle)
        """
        self.num_qudits = num_qudits
        self.gates = []
        self.metadata = {}
    
    def add_gate(self, gate: QuditGate):
        """
        Add a gate to the circuit.
        
        Parameters
        ----------
        gate : QuditGate
            Gate to add to the circuit
        """
        # Validate qudit indices
        for q in gate.qudits:
            if q < 0 or q >= self.num_qudits:
                raise ValueError(f"Invalid qudit index {q} for {self.num_qudits}-qudit circuit")
        self.gates.append(gate)
    
    def add_evolution_gate(self, operator_name: str, coeff: float, time: float,
                          matrix: Optional[np.ndarray] = None, description: str = ""):
        """
        Add a time evolution gate exp(-i*coeff*O*time) for operator O.
        
        Parameters
        ----------
        operator_name : str
            Name of the operator (e.g., 'Jx', 'Jy', 'Jz', 'Jx2', 'Jy2', 'Jz2')
        coeff : float
            Coefficient multiplying the operator
        time : float
            Evolution time
        matrix : np.ndarray, optional
            3×3 unitary matrix for the gate
        description : str, optional
            Description of the physical meaning
        """
        gate_name = f"exp_{operator_name}"
        params = {'coeff': coeff, 'time': time, 'total': coeff * time}
        gate = QuditGate(gate_name, [0], params, matrix, description)
        self.add_gate(gate)
    
    def depth(self) -> int:
        """
        Calculate the circuit depth (number of gate layers).
        
        For single-qudit circuits, this is simply the number of gates.
        
        Returns
        -------
        depth : int
            Circuit depth
        """
        return len(self.gates)
    
    def get_gate_statistics(self) -> Dict[str, int]:
        """
        Get statistics on gate types used in the circuit.
        
        Returns
        -------
        stats : dict
            Dictionary mapping gate types to counts
        """
        stats = {}
        for gate in self.gates:
            base_name = gate.name.split('_')[0]
            stats[base_name] = stats.get(base_name, 0) + 1
        return stats
    
    def visualize(self, figsize: Tuple[int, int] = (14, 6),
                 show_math: bool = True, show_matrices: bool = False,
                 max_gates_per_row: int = 20) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a visual representation of the qudit circuit.
        
        Parameters
        ----------
        figsize : tuple, default=(14, 6)
            Figure size (width, height)
        show_math : bool, default=True
            Whether to show mathematical formulas for gates
        show_matrices : bool, default=False
            Whether to show the actual 3×3 matrices (verbose)
        max_gates_per_row : int, default=20
            Maximum number of gates to show per row before wrapping
        
        Returns
        -------
        fig : matplotlib.figure.Figure
            The figure object
        ax : matplotlib.axes.Axes
            The axes object
        """
        num_rows = (len(self.gates) + max_gates_per_row - 1) // max_gates_per_row
        
        fig, axes = plt.subplots(num_rows, 1, figsize=(figsize[0], figsize[1] * num_rows))
        if num_rows == 1:
            axes = [axes]
        
        for row_idx in range(num_rows):
            ax = axes[row_idx]
            start_idx = row_idx * max_gates_per_row
            end_idx = min(start_idx + max_gates_per_row, len(self.gates))
            row_gates = self.gates[start_idx:end_idx]
            
            self._draw_circuit_row(ax, row_gates, start_idx, show_math, show_matrices)
            
            # Add row label
            if num_rows > 1:
                ax.set_title(f'Circuit Section {row_idx + 1}/{num_rows} '
                           f'(Gates {start_idx + 1}-{end_idx})', 
                           fontsize=11, pad=10)
        
        plt.tight_layout()
        return fig, axes
    
    def _draw_circuit_row(self, ax: plt.Axes, gates: List[QuditGate], 
                         start_idx: int, show_math: bool, show_matrices: bool):
        """
        Draw a single row of the circuit.
        
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Axes to draw on
        gates : list of QuditGate
            Gates to draw in this row
        start_idx : int
            Starting index for gate numbering
        show_math : bool
            Whether to show mathematical formulas
        show_matrices : bool
            Whether to show matrices
        """
        # Set up the axes
        ax.set_xlim(-0.5, len(gates) + 0.5)
        ax.set_ylim(-0.5, self.num_qudits + 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Draw qudit lines
        for qudit_idx in range(self.num_qudits):
            y = qudit_idx
            ax.plot([-0.3, len(gates) + 0.3], [y, y], 'k-', linewidth=2, zorder=1)
            ax.text(-0.4, y, f'|S=1⟩', ha='right', va='center', fontsize=10, 
                   fontweight='bold')
        
        # Draw gates
        for i, gate in enumerate(gates):
            x = i
            y = gate.qudits[0]
            
            # Determine gate color based on operator type
            if 'Jx' in gate.name:
                color = '#FF6B6B'  # Red for x-rotation
                op_label = 'Jₓ'
            elif 'Jy' in gate.name:
                color = '#4ECDC4'  # Teal for y-rotation
                op_label = 'Jᵧ'
            elif 'Jz' in gate.name:
                color = '#95E1D3'  # Light teal for z-rotation
                op_label = 'Jᵤ'
            else:
                color = '#F3B61F'  # Yellow for general unitary
                op_label = 'U'
            
            # Draw gate box
            box_width = 0.7
            box_height = 0.7
            box = FancyBboxPatch(
                (x - box_width/2, y - box_height/2),
                box_width, box_height,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor='black',
                linewidth=2,
                zorder=2
            )
            ax.add_patch(box)
            
            # Add gate label
            if show_math:
                label = gate.get_mathematical_form()
                ax.text(x, y, label, ha='center', va='center',
                       fontsize=8, fontweight='bold', zorder=3)
            else:
                ax.text(x, y, op_label, ha='center', va='center',
                       fontsize=11, fontweight='bold', zorder=3)
            
            # Add gate number below
            ax.text(x, y - 0.5, f'#{start_idx + i + 1}',
                   ha='center', va='top', fontsize=7, color='gray')
            
            # Show matrix if requested (very verbose!)
            if show_matrices and gate.matrix is not None:
                matrix_str = self._format_matrix(gate.matrix)
                ax.text(x, y + 0.5, matrix_str, ha='center', va='bottom',
                       fontsize=5, family='monospace')
    
    def _format_matrix(self, matrix: np.ndarray, precision: int = 2) -> str:
        """Format a 3×3 matrix as a string."""
        if matrix is None:
            return ""
        
        lines = []
        for row in matrix:
            row_str = " ".join(f"{val:.{precision}f}" for val in row)
            lines.append(row_str)
        return "\n".join(lines)
    
    def to_text(self, show_details: bool = True) -> str:
        """
        Generate a text representation of the circuit.
        
        Parameters
        ----------
        show_details : bool, default=True
            Whether to include detailed mathematical descriptions
        
        Returns
        -------
        text : str
            Text representation
        """
        lines = []
        lines.append("=" * 70)
        lines.append("Qudit (Spin S=1) Quantum Circuit")
        lines.append("=" * 70)
        lines.append(f"Number of qudits: {self.num_qudits}")
        lines.append(f"Circuit depth: {self.depth()}")
        lines.append(f"Total gates: {len(self.gates)}")
        
        if self.metadata:
            lines.append("\nMetadata:")
            for key, val in self.metadata.items():
                lines.append(f"  {key}: {val}")
        
        lines.append("\nGate Statistics:")
        stats = self.get_gate_statistics()
        for gate_type, count in sorted(stats.items()):
            lines.append(f"  {gate_type}: {count}")
        
        if show_details and self.gates:
            lines.append("\nGate Sequence:")
            lines.append("-" * 70)
            for i, gate in enumerate(self.gates):
                lines.append(f"Gate {i+1}: {gate}")
                if gate.description:
                    lines.append(f"  Description: {gate.description}")
                lines.append(f"  Mathematical form: {gate.get_mathematical_form()}")
                if gate.matrix is not None:
                    lines.append(f"  Matrix shape: {gate.matrix.shape}")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def print_summary(self):
        """Print a summary of the circuit."""
        print(self.to_text(show_details=False))
    
    def print_detailed(self):
        """Print detailed information about the circuit."""
        print(self.to_text(show_details=True))


def visualize_state_evolution(states: List[np.ndarray], 
                              times: np.ndarray,
                              operators: Optional[Dict[str, np.ndarray]] = None,
                              figsize: Tuple[int, int] = (14, 8)) -> Tuple[plt.Figure, np.ndarray]:
    """
    Visualize the evolution of quantum states through the circuit.
    
    Parameters
    ----------
    states : list of np.ndarray
        List of quantum states (3-dimensional vectors)
    times : np.ndarray
        Time points corresponding to each state
    operators : dict, optional
        Dictionary of operators to compute expectation values
        (e.g., {'Jx': Jx_matrix, 'Jy': Jy_matrix, 'Jz': Jz_matrix})
    figsize : tuple, default=(14, 8)
        Figure size
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    axes : np.ndarray
        Array of axes objects
    """
    if operators is None:
        # Use default Spin-1 operators
        from .statevector_simulator import get_spin1_operators
        ops = get_spin1_operators()
        operators = {
            'Jx': ops['Jx'],
            'Jy': ops['Jy'],
            'Jz': ops['Jz']
        }
    
    num_plots = 2 + len(operators)  # populations + expectations
    fig, axes = plt.subplots(2, (num_plots + 1) // 2, figsize=figsize)
    axes = axes.flatten()
    
    # Plot 1: Population dynamics
    ax = axes[0]
    # Flatten states to 1D arrays for consistent handling
    populations = np.array([np.abs(state.flatten())**2 for state in states])
    ax.plot(times, populations[:, 0], 'r-', linewidth=2, label='|m=+1⟩')
    ax.plot(times, populations[:, 1], 'g-', linewidth=2, label='|m=0⟩')
    ax.plot(times, populations[:, 2], 'b-', linewidth=2, label='|m=-1⟩')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Population', fontsize=11)
    ax.set_title('State Populations', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Total probability (should be 1)
    ax = axes[1]
    total_prob = populations.sum(axis=1)
    ax.plot(times, total_prob, 'k-', linewidth=2)
    ax.axhline(1.0, color='r', linestyle='--', alpha=0.5, label='Expected')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Total Probability', fontsize=11)
    ax.set_title('Normalization Check', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.99, 1.01])
    
    # Plots 3+: Expectation values
    for i, (op_name, op_matrix) in enumerate(operators.items()):
        ax = axes[2 + i]
        expectations = np.array([
            np.real(np.conj(state.flatten()).T @ op_matrix @ state.flatten())
            for state in states
        ])
        ax.plot(times, expectations, linewidth=2)
        ax.set_xlabel('Time', fontsize=11)
        ax.set_ylabel(f'⟨{op_name}⟩', fontsize=11)
        ax.set_title(f'Expectation Value ⟨{op_name}⟩', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # Hide unused axes
    for i in range(num_plots, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    return fig, axes


def visualize_bloch_sphere_trajectory(states: List[np.ndarray],
                                     figsize: Tuple[int, int] = (10, 10),
                                     projection: str = '3d') -> Tuple[plt.Figure, plt.Axes]:
    """
    Visualize the trajectory of Spin S=1 states on a generalized Bloch sphere.
    
    For Spin S=1, we can visualize the expectation values (⟨Jx⟩, ⟨Jy⟩, ⟨Jz⟩)
    as a trajectory in 3D space.
    
    Parameters
    ----------
    states : list of np.ndarray
        List of quantum states (3-dimensional vectors)
    figsize : tuple, default=(10, 10)
        Figure size
    projection : str, default='3d'
        '3d' for 3D plot or '2d' for 2D projections
    
    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure object
    ax : matplotlib.axes.Axes
        The axes object
    """
    from .statevector_simulator import get_spin1_operators
    ops = get_spin1_operators()
    Jx, Jy, Jz = ops['Jx'], ops['Jy'], ops['Jz']
    
    # Compute expectation values
    x_vals = np.array([np.real(np.conj(state.flatten()).T @ Jx @ state.flatten()) for state in states])
    y_vals = np.array([np.real(np.conj(state.flatten()).T @ Jy @ state.flatten()) for state in states])
    z_vals = np.array([np.real(np.conj(state.flatten()).T @ Jz @ state.flatten()) for state in states])
    
    if projection == '3d':
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot trajectory
        ax.plot(x_vals, y_vals, z_vals, 'b-', linewidth=2, alpha=0.7)
        ax.scatter(x_vals[0], y_vals[0], z_vals[0], c='g', s=100, 
                  marker='o', label='Initial', zorder=5)
        ax.scatter(x_vals[-1], y_vals[-1], z_vals[-1], c='r', s=100,
                  marker='s', label='Final', zorder=5)
        
        # Draw axes
        max_val = 1.2
        ax.plot([-max_val, max_val], [0, 0], [0, 0], 'k-', alpha=0.3, linewidth=0.5)
        ax.plot([0, 0], [-max_val, max_val], [0, 0], 'k-', alpha=0.3, linewidth=0.5)
        ax.plot([0, 0], [0, 0], [-max_val, max_val], 'k-', alpha=0.3, linewidth=0.5)
        
        ax.set_xlabel('⟨Jₓ⟩', fontsize=12, fontweight='bold')
        ax.set_ylabel('⟨Jᵧ⟩', fontsize=12, fontweight='bold')
        ax.set_zlabel('⟨Jᵤ⟩', fontsize=12, fontweight='bold')
        ax.set_title('Spin S=1 State Trajectory\n(Generalized Bloch Sphere)',
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        
    else:  # 2D projections
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # XY projection
        axes[0].plot(x_vals, y_vals, 'b-', linewidth=2, alpha=0.7)
        axes[0].scatter(x_vals[0], y_vals[0], c='g', s=100, marker='o', label='Initial')
        axes[0].scatter(x_vals[-1], y_vals[-1], c='r', s=100, marker='s', label='Final')
        axes[0].set_xlabel('⟨Jₓ⟩', fontsize=11)
        axes[0].set_ylabel('⟨Jᵧ⟩', fontsize=11)
        axes[0].set_title('XY Projection', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        axes[0].set_aspect('equal')
        
        # XZ projection
        axes[1].plot(x_vals, z_vals, 'b-', linewidth=2, alpha=0.7)
        axes[1].scatter(x_vals[0], z_vals[0], c='g', s=100, marker='o', label='Initial')
        axes[1].scatter(x_vals[-1], z_vals[-1], c='r', s=100, marker='s', label='Final')
        axes[1].set_xlabel('⟨Jₓ⟩', fontsize=11)
        axes[1].set_ylabel('⟨Jᵤ⟩', fontsize=11)
        axes[1].set_title('XZ Projection', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
        axes[1].set_aspect('equal')
        
        # YZ projection
        axes[2].plot(y_vals, z_vals, 'b-', linewidth=2, alpha=0.7)
        axes[2].scatter(y_vals[0], z_vals[0], c='g', s=100, marker='o', label='Initial')
        axes[2].scatter(y_vals[-1], z_vals[-1], c='r', s=100, marker='s', label='Final')
        axes[2].set_xlabel('⟨Jᵧ⟩', fontsize=11)
        axes[2].set_ylabel('⟨Jᵤ⟩', fontsize=11)
        axes[2].set_title('YZ Projection', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend()
        axes[2].set_aspect('equal')
    
    plt.tight_layout()
    return fig, ax if projection == '3d' else axes


class CircuitVisualizer:
    """
    Visualizer for quantum circuits (compatibility class).
    
    This class provides a simple interface for circuit visualization.
    It wraps the QuditCircuit class and provides convenience methods
    for visualization.
    
    This class is provided for backwards compatibility with code that
    expects a CircuitVisualizer class. For new code, use QuditCircuit
    and the standalone visualization functions instead.
    
    Parameters
    ----------
    num_qudits : int, optional
        Number of qudits in the circuit. Default is 1.
        
    Examples
    --------
    >>> visualizer = CircuitVisualizer(num_qudits=1)
    >>> # Use visualizer methods here
    """
    
    def __init__(self, num_qudits: int = 1):
        """
        Initialize the circuit visualizer.
        
        Parameters
        ----------
        num_qudits : int, optional
            Number of qudits in the circuit. Default is 1.
        """
        self.num_qudits = num_qudits
        self.circuit = QuditCircuit(num_qudits=num_qudits)
    
    def __repr__(self):
        return f"CircuitVisualizer(num_qudits={self.num_qudits})"
    
    def __str__(self):
        return f"Circuit visualizer for {self.num_qudits} qudit(s)"
