"""
Unit tests for Qobj validation in MQT simulators.

These tests verify that the validation methods correctly handle both
numpy arrays and QuTiP Qobj inputs.
"""
import numpy as np
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import QuTiP
import qutip as qt


class MockMQTSimulator:
    """Mock class to test validation methods without requiring MQT."""
    
    def _validate_hamiltonian(self, H):
        """Validate that the Hamiltonian is a proper 3x3 Hermitian matrix.
        
        This is a copy of the actual validation method for testing purposes.
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
        
        This is a copy of the actual validation method for testing purposes.
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


class TestQobjValidation(unittest.TestCase):
    """Test validation methods with both Qobj and numpy array inputs."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sim = MockMQTSimulator()
        
    def test_validate_hamiltonian_with_qobj(self):
        """Test that Qobj Hamiltonian is properly converted."""
        # Create Hamiltonian using QuTiP
        Jz = qt.jmat(1, 'z')
        H_qobj = -2.0 * np.pi * Jz
        
        # Validate
        H_array = self.sim._validate_hamiltonian(H_qobj)
        
        # Check type and shape
        self.assertIsInstance(H_array, np.ndarray)
        self.assertEqual(H_array.shape, (3, 3))
        
        # Check hermiticity
        self.assertTrue(np.allclose(H_array, H_array.conj().T))
        
    def test_validate_hamiltonian_with_array(self):
        """Test that numpy array Hamiltonian is properly handled."""
        # Create Hamiltonian as numpy array
        H_array_in = np.array([[1, 0, 0],
                                [0, 0, 0],
                                [0, 0, -1]], dtype=complex)
        
        # Validate
        H_array = self.sim._validate_hamiltonian(H_array_in)
        
        # Check type and shape
        self.assertIsInstance(H_array, np.ndarray)
        self.assertEqual(H_array.shape, (3, 3))
        
    def test_validate_state_with_qobj(self):
        """Test that Qobj state is properly converted."""
        # Create state using QuTiP
        psi_qobj = qt.basis(3, 0)
        
        # Validate
        psi_array = self.sim._validate_state(psi_qobj)
        
        # Check type and shape
        self.assertIsInstance(psi_array, np.ndarray)
        self.assertEqual(len(psi_array), 3)
        
        # Check normalization
        self.assertAlmostEqual(np.linalg.norm(psi_array), 1.0)
        
    def test_validate_state_with_array(self):
        """Test that numpy array state is properly handled."""
        # Create state as numpy array
        psi_array_in = np.array([1, 0, 0], dtype=complex)
        
        # Validate
        psi_array = self.sim._validate_state(psi_array_in)
        
        # Check type and shape
        self.assertIsInstance(psi_array, np.ndarray)
        self.assertEqual(len(psi_array), 3)
        
    def test_validate_superposition_state(self):
        """Test with a superposition state."""
        # Create superposition using QuTiP
        psi_qobj = (qt.basis(3, 0) + qt.basis(3, 1)).unit()
        
        # Validate
        psi_array = self.sim._validate_state(psi_qobj)
        
        # Check type and shape
        self.assertIsInstance(psi_array, np.ndarray)
        self.assertEqual(len(psi_array), 3)
        
        # Check normalization
        self.assertAlmostEqual(np.linalg.norm(psi_array), 1.0)
        
        # Check expected values
        expected = np.array([1/np.sqrt(2), 1/np.sqrt(2), 0])
        np.testing.assert_allclose(np.abs(psi_array), np.abs(expected))
        
    def test_validate_hamiltonian_non_hermitian_raises_error(self):
        """Test that non-Hermitian Hamiltonian raises an error."""
        # Create non-Hermitian matrix
        H_bad = np.array([[1, 1, 0],
                         [0, 0, 0],
                         [0, 0, -1]], dtype=complex)
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.sim._validate_hamiltonian(H_bad)
        
        self.assertIn("Hermitian", str(context.exception))
        
    def test_validate_state_wrong_dimension_raises_error(self):
        """Test that wrong dimension state raises an error."""
        # Create wrong dimension state
        psi_bad = np.array([1, 0], dtype=complex)
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.sim._validate_state(psi_bad)
        
        self.assertIn("3-dimensional", str(context.exception))
        
    def test_hamiltonian_does_not_have_T_attribute(self):
        """Test that we're not using .T on Qobj (which would cause AttributeError)."""
        # Create Qobj
        H_qobj = qt.jmat(1, 'z')
        
        # Verify Qobj doesn't have .T attribute
        self.assertFalse(hasattr(H_qobj, 'T'))
        
        # But it should have .full() method
        self.assertTrue(hasattr(H_qobj, 'full'))
        
        # Validation should work without error
        H_array = self.sim._validate_hamiltonian(H_qobj)
        self.assertIsInstance(H_array, np.ndarray)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
