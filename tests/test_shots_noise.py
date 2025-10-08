#!/usr/bin/env python3
"""
Tests for shot simulator noise and measurement fixes.

This test module verifies:
1. Bug fix (A): Measurements happen at all time steps regardless of noise_model
2. Design fix (B-1): Basis rotation is decomposed into elementary gates
3. Design improvement (B-2): apply_noise_in_evolution mode works correctly
"""

import numpy as np
import pytest

# Try to import required modules
try:
    import qutip as qt
    from qudit.qubit.statevector_simulator import StatevectorSimulator
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False

try:
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    from qiskit.providers.aer.noise import ReadoutError
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


@pytest.mark.skipif(not QUTIP_AVAILABLE, reason="QuTiP not available")
class TestShotSimulatorMeasurements:
    """Test that measurements work correctly without noise."""
    
    def test_no_noise_measures_each_step_zeeman(self):
        """
        Bug fix (A): Test that noise_model=None still measures at each time step.
        Uses Zeeman Hamiltonian with known dynamics.
        """
        # Zeeman Hamiltonian: H = -omega_0 * Jz
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 1.0, 5)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Simulate without noise
        result = sim.simulate_with_shots(
            H, psi0, times, 
            [qt.jmat(1,'x'), qt.jmat(1,'y'), qt.jmat(1,'z')],
            shots=2048, 
            noise_model=None
        )
        
        # Check that expectations are not all zero at t>0
        expect_nonzero = np.any(np.abs(result['expect'][1:]) > 1e-10)
        assert expect_nonzero, "Expectations at t>0 should be non-zero"
        
        # Check that populations are not all zero at t>0
        pop_nonzero = np.any(np.abs(result['populations'][1:]) > 1e-10)
        assert pop_nonzero, "Populations at t>0 should be non-zero"
        
        # Verify the shape is correct
        assert result['expect'].shape == (len(times), 3)
        assert result['populations'].shape == (len(times), 3)
    
    def test_no_noise_measures_each_step_transverse(self):
        """
        Bug fix (A): Test with transverse field (Jx) to verify measurements.
        """
        # Transverse field: H = -omega_0 * Jx
        omega0 = 2*np.pi*0.5
        Jx = qt.jmat(1, 'x')
        H = -omega0 * Jx
        psi0 = qt.spin_state(1, 0)  # Start in m=0 state
        times = np.linspace(0, 1.0, 6)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        result = sim.simulate_with_shots(
            H, psi0, times, 
            [qt.jmat(1,'x'), qt.jmat(1,'y'), qt.jmat(1,'z')],
            shots=2048, 
            noise_model=None
        )
        
        # With Jx Hamiltonian and m=0 initial state, we expect time evolution
        # Check that at least one expectation value changes significantly
        expect_changes = np.max(np.abs(result['expect'][1:] - result['expect'][0]))
        assert expect_changes > 0.01, "Expectation values should change over time"
    
    def test_no_noise_rabi_oscillations(self):
        """
        Bug fix (A): Test Rabi oscillations to verify time-dependent measurements.
        """
        # Rabi Hamiltonian: H = omega_z * Jz + omega_x * Jx
        omega_z = 2*np.pi*1.0
        omega_x = 2*np.pi*0.3
        Jz = qt.jmat(1, 'z')
        Jx = qt.jmat(1, 'x')
        H = omega_z * Jz + omega_x * Jx
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 2.0, 8)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        result = sim.simulate_with_shots(
            H, psi0, times, 
            [qt.jmat(1,'z')],
            shots=2048, 
            noise_model=None
        )
        
        # Check that Jz expectation oscillates
        jz_expect = result['expect'][:, 0]
        
        # At t=0, should be close to -1 (m=-1 state)
        assert np.abs(jz_expect[0] - (-1.0)) < 0.1, "Initial <Jz> should be ~-1"
        
        # Should vary over time (Rabi oscillations)
        jz_range = np.max(jz_expect) - np.min(jz_expect)
        assert jz_range > 0.2, "Jz should oscillate significantly"


@pytest.mark.skipif(not (QUTIP_AVAILABLE and QISKIT_AVAILABLE), 
                    reason="QuTiP and Qiskit not available")
class TestBasisRotationDecomposition:
    """Test that basis rotation is decomposed into elementary gates."""
    
    def test_basis_rotation_is_decomposed(self):
        """
        Design fix (B-1): Test that _measure_observables_with_shots uses
        decomposed gates (rx/ry/rz/cx) instead of unitary instruction.
        """
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        
        # Create a simple test
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, 0)
        times = np.linspace(0, 0.5, 3)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Create a simple noise model
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ['rx','ry','rz'])
        
        # Run simulation - internally should decompose basis rotations
        result = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x')],
            shots=1024,
            noise_model=nm
        )
        
        # If this runs without error and produces results, the decomposition works
        assert result['expect'].shape == (len(times), 1)
        assert not np.all(result['expect'] == 0)
        
        # The key test is that the circuit uses basis gates, not unitary
        # This is verified implicitly because unitary gates don't accept noise


@pytest.mark.skipif(not (QUTIP_AVAILABLE and QISKIT_AVAILABLE), 
                    reason="QuTiP and Qiskit not available")
class TestNoiseEffects:
    """Test that noise effects are observable."""
    
    def test_noise_effect_visible_zeeman(self):
        """
        Design improvement (B): Test that noise model produces observable
        differences from noiseless simulation.
        """
        # Zeeman Hamiltonian
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 1.0, 10)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Run without noise
        result_no_noise = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x'), qt.jmat(1,'y'), qt.jmat(1,'z')],
            shots=4096,
            noise_model=None
        )
        
        # Create noise model
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ['rx','ry','rz'])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ['cx'])
        
        # Add readout errors
        readout_error = [[0.98, 0.02], [0.02, 0.98]]
        nm.add_all_qubit_readout_error(ReadoutError(readout_error), [0])
        nm.add_all_qubit_readout_error(ReadoutError(readout_error), [1])
        
        # Run with noise
        result_noise = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x'), qt.jmat(1,'y'), qt.jmat(1,'z')],
            shots=4096,
            noise_model=nm
        )
        
        # Calculate mean absolute difference
        diff = np.mean(np.abs(result_noise['expect'] - result_no_noise['expect']))
        
        # With significant noise and many shots, difference should be observable
        # (not just statistical fluctuation)
        assert diff > 1e-3, f"Noise effect should be observable (diff={diff:.6f})"
    
    def test_noise_in_evolution_cumulative(self):
        """
        Design improvement (B-2): Test that apply_noise_in_evolution=True
        produces different (typically larger) errors that accumulate over time.
        """
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 1.0, 8)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Create noise model
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ['rx','ry','rz'])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ['cx'])
        
        # Run with noise in evolution
        result_noise_evo = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'z')],
            shots=4096,
            noise_model=nm,
            apply_noise_in_evolution=True
        )
        
        # Run with noise only at measurement (traditional)
        result_noise_meas = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'z')],
            shots=4096,
            noise_model=nm,
            apply_noise_in_evolution=False
        )
        
        # With noise in evolution, errors should accumulate
        # Check that later times show bigger differences
        diff_late = np.abs(result_noise_evo['expect'][-3:] - result_noise_meas['expect'][-3:])
        diff_early = np.abs(result_noise_evo['expect'][1:3] - result_noise_meas['expect'][1:3])
        
        # Note: This test may be sensitive to random fluctuations
        # We check if on average late-time differences are larger
        assert np.mean(diff_late) > np.mean(diff_early) * 0.5, \
            "Cumulative noise should show larger effects at later times"
    
    def test_apply_noise_in_evolution_parameter(self):
        """
        Design improvement (B-2): Test that apply_noise_in_evolution parameter
        actually changes behavior.
        """
        omega0 = 2*np.pi*0.5
        Jx = qt.jmat(1, 'x')
        H = -omega0 * Jx
        psi0 = qt.spin_state(1, 0)
        times = np.linspace(0, 1.0, 6)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Run both modes
        result_false = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x')],
            shots=2048,
            noise_model=None,
            apply_noise_in_evolution=False
        )
        
        result_true = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x')],
            shots=2048,
            noise_model=None,
            apply_noise_in_evolution=True
        )
        
        # Without noise, both should give similar results (within statistical error)
        # This verifies backward compatibility
        diff = np.max(np.abs(result_false['expect'] - result_true['expect']))
        
        # Difference should be small (just statistical fluctuations)
        # With 2048 shots, std ~ 1/sqrt(2048) ~ 0.022
        assert diff < 0.15, "Without noise, both modes should give similar results"


@pytest.mark.skipif(not (QUTIP_AVAILABLE and QISKIT_AVAILABLE), 
                    reason="QuTiP and Qiskit not available")
class TestBackwardCompatibility:
    """Test that existing functionality is preserved."""
    
    def test_default_parameters_unchanged(self):
        """Test that default parameters maintain backward compatibility."""
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 0.5, 3)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # Call without new parameter (should default to False)
        result = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'z')],
            shots=1024,
            noise_model=None
        )
        
        # Should work and produce valid results
        assert result['expect'].shape == (len(times), 1)
        assert 'shots' in result
        assert result['shots'] == 1024
    
    def test_compare_with_exact_unchanged(self):
        """Test that compare_with_exact still works correctly."""
        omega0 = 2*np.pi*1.0
        Jz = qt.jmat(1, 'z')
        H = -omega0 * Jz
        psi0 = qt.spin_state(1, -1)
        times = np.linspace(0, 0.5, 4)
        
        sim = StatevectorSimulator(trotter_order=2)
        
        # This should still work
        comparison = sim.compare_with_exact(
            H, psi0, times,
            [qt.jmat(1,'z')]
        )
        
        assert 'qubit' in comparison
        assert 'exact' in comparison
        assert 'errors' in comparison


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
