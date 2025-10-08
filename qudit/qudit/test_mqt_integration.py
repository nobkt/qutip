"""
Test script for MQT Qudits integration.

This script demonstrates and validates the MQT Qudits statevector simulator
for Spin S=1 quantum dynamics.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from qudit.qudit import (
    MQTStatevectorSimulator,
    get_spin1_operators,
    get_spin1_states,
    spin_coherent_state
)


def test_zeeman_effect():
    """Test MQT simulator with Zeeman effect (simple precession)."""
    print("\n" + "="*70)
    print("Test 1: Zeeman Effect (Precession around z-axis)")
    print("="*70)
    
    # Get operators
    ops = get_spin1_operators()
    Jz = ops['Jz']
    
    # Zeeman Hamiltonian: H = -ω₀ Jz
    omega0 = 2 * np.pi * 1.0  # Larmor frequency
    H = -omega0 * Jz
    
    # Start in |m=+1⟩ state
    states = get_spin1_states()
    psi0 = states['m1']
    
    # Create simulator
    sim = MQTStatevectorSimulator(trotter_order=2)
    
    # Simulate one period
    T = 2 * np.pi / omega0
    times = np.linspace(0, T, 50)
    
    # Compare with exact solution
    comparison = sim.compare_with_exact(H, psi0, times)
    
    # Check results
    mean_fidelity = comparison['errors']['mean_fidelity']
    max_error = comparison['errors']['max_expect_error']
    
    print(f"\nResults:")
    print(f"  Mean fidelity: {mean_fidelity:.8f}")
    print(f"  Max error:     {max_error:.6e}")
    
    assert mean_fidelity > 0.999, f"Fidelity too low: {mean_fidelity}"
    print("\n✓ Test passed: Excellent agreement with exact solution")
    
    return comparison


def test_transverse_field():
    """Test MQT simulator with transverse field (Rabi oscillations)."""
    print("\n" + "="*70)
    print("Test 2: Transverse Field (Rabi-like oscillations)")
    print("="*70)
    
    # Get operators
    ops = get_spin1_operators()
    Jx = ops['Jx']
    Jz = ops['Jz']
    
    # Hamiltonian with transverse field: H = -ω_z Jz - ω_x Jx
    omega_z = 2 * np.pi * 1.0
    omega_x = 2 * np.pi * 0.5
    H = -omega_z * Jz - omega_x * Jx
    
    # Start in coherent state pointing along x-direction
    psi0 = spin_coherent_state(np.pi/2, 0)
    
    # Create simulator with higher order for better accuracy
    sim = MQTStatevectorSimulator(trotter_order=2, decomposition_basis='xyz')
    
    # Simulate
    times = np.linspace(0, 2.0, 100)
    
    # Compare with exact solution
    comparison = sim.compare_with_exact(H, psi0, times)
    
    # Check results
    mean_fidelity = comparison['errors']['mean_fidelity']
    max_error = comparison['errors']['max_expect_error']
    
    print(f"\nResults:")
    print(f"  Mean fidelity: {mean_fidelity:.8f}")
    print(f"  Max error:     {max_error:.6e}")
    
    assert mean_fidelity > 0.999, f"Fidelity too low: {mean_fidelity}"
    print("\n✓ Test passed: Excellent agreement with exact solution")
    
    return comparison


def test_general_hamiltonian():
    """Test MQT simulator with a general Hamiltonian."""
    print("\n" + "="*70)
    print("Test 3: General Hamiltonian (all three components)")
    print("="*70)
    
    # Get operators
    ops = get_spin1_operators()
    Jx = ops['Jx']
    Jy = ops['Jy']
    Jz = ops['Jz']
    
    # General Hamiltonian: H = ω_x Jx + ω_y Jy + ω_z Jz
    omega_x = 2 * np.pi * 0.3
    omega_y = 2 * np.pi * 0.4
    omega_z = 2 * np.pi * 0.5
    H = omega_x * Jx + omega_y * Jy + omega_z * Jz
    
    # Start in a general coherent state
    psi0 = spin_coherent_state(np.pi/3, np.pi/4)
    
    # Create simulator
    sim = MQTStatevectorSimulator(trotter_order=2, decomposition_basis='xyz')
    
    # Simulate
    times = np.linspace(0, 5.0, 100)
    
    # Compare with exact solution
    comparison = sim.compare_with_exact(H, psi0, times)
    
    # Check results
    mean_fidelity = comparison['errors']['mean_fidelity']
    max_error = comparison['errors']['max_expect_error']
    
    print(f"\nResults:")
    print(f"  Mean fidelity: {mean_fidelity:.8f}")
    print(f"  Max error:     {max_error:.6e}")
    
    assert mean_fidelity > 0.999, f"Fidelity too low: {mean_fidelity}"
    print("\n✓ Test passed: Excellent agreement with exact solution")
    
    return comparison


def test_trotter_orders():
    """Compare different Trotter orders."""
    print("\n" + "="*70)
    print("Test 4: Comparison of Trotter Orders")
    print("="*70)
    
    # Get operators
    ops = get_spin1_operators()
    Jx = ops['Jx']
    Jz = ops['Jz']
    
    # Hamiltonian
    H = -2*np.pi * Jz - np.pi * Jx
    
    # Initial state
    psi0 = spin_coherent_state(np.pi/4, 0)
    
    # Times - use finer steps for better convergence
    times = np.linspace(0, 2.0, 100)
    
    # Test different orders
    orders = [1, 2]  # Skip order 4 for now as it needs special handling
    results = {}
    
    for order in orders:
        sim = MQTStatevectorSimulator(trotter_order=order, decomposition_basis='xyz')
        comparison = sim.compare_with_exact(H, psi0, times)
        results[order] = comparison
        
        print(f"\nTrotter order {order}:")
        print(f"  Mean fidelity: {comparison['errors']['mean_fidelity']:.8f}")
        print(f"  Max error:     {comparison['errors']['max_expect_error']:.6e}")
    
    # Higher orders should be more accurate
    assert results[2]['errors']['mean_fidelity'] >= results[1]['errors']['mean_fidelity']
    
    print("\n✓ Test passed: Higher Trotter orders show better accuracy")
    
    return results


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("MQT Qudits Integration Test Suite")
    print("="*70)
    
    try:
        # Run tests
        test_zeeman_effect()
        test_transverse_field()
        test_general_hamiltonian()
        test_trotter_orders()
        
        print("\n" + "="*70)
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nMQT Qudits integration is working correctly!")
        print("The simulator accurately reproduces exact quantum dynamics")
        print("using Suzuki-Trotter decomposition.\n")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
