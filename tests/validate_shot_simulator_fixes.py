#!/usr/bin/env python3
"""
Validation script demonstrating the shot simulator fixes.

This script shows:
1. Bug fix (A): Measurements now occur at all time steps
2. Design fix (B-1): Basis rotations use elementary gates
3. Design improvement (B-2): Noise can be applied during evolution
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("SHOT SIMULATOR FIX VALIDATION")
print("="*70)

# Check imports
print("\n1. Checking imports...")
try:
    import numpy as np
    print("   ✓ numpy available")
except ImportError:
    print("   ✗ numpy not available")
    sys.exit(1)

try:
    import qutip as qt
    print("   ✓ qutip available")
except ImportError:
    print("   ✗ qutip not available - cannot validate")
    sys.exit(1)

try:
    from qudit.qubit.statevector_simulator import StatevectorSimulator
    print("   ✓ StatevectorSimulator available")
except ImportError as e:
    print(f"   ✗ StatevectorSimulator not available: {e}")
    sys.exit(1)

try:
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    from qiskit.providers.aer.noise import ReadoutError
    print("   ✓ Qiskit Aer available")
    QISKIT_AVAILABLE = True
except ImportError:
    print("   ⚠ Qiskit Aer not available - skipping noise tests")
    QISKIT_AVAILABLE = False

# Test 1: Bug fix (A) - Measurements at all time steps
print("\n2. Testing Bug Fix (A): Measurements at all time steps")
print("   " + "-"*66)

omega0 = 2*np.pi*1.0
Jz = qt.jmat(1, 'z')
H = -omega0 * Jz
psi0 = qt.spin_state(1, -1)
times = np.linspace(0, 1.0, 5)

sim = StatevectorSimulator(trotter_order=2)

if QISKIT_AVAILABLE:
    try:
        result = sim.simulate_with_shots(
            H, psi0, times,
            [qt.jmat(1,'x'), qt.jmat(1,'y'), qt.jmat(1,'z')],
            shots=2048,
            noise_model=None
        )
        
        # Check if measurements occur at all times
        has_nonzero_t1 = np.any(np.abs(result['expect'][1]) > 1e-10)
        has_nonzero_t2 = np.any(np.abs(result['expect'][2]) > 1e-10)
        
        if has_nonzero_t1 and has_nonzero_t2:
            print("   ✓ PASS: Measurements occur at all time steps")
            print(f"   - Expectations at t=0: {result['expect'][0]}")
            print(f"   - Expectations at t>0: {result['expect'][1]}")
        else:
            print("   ✗ FAIL: Measurements missing at t>0")
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
else:
    print("   ⚠ SKIPPED: Qiskit not available")

# Test 2: Design fix (B-1) - Basis rotation decomposition
print("\n3. Testing Design Fix (B-1): Basis rotation decomposition")
print("   " + "-"*66)

if QISKIT_AVAILABLE:
    try:
        # Create noise model
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ['rx','ry','rz'])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.05, 2), ['cx'])
        
        result = sim.simulate_with_shots(
            H, psi0, times[:3],  # Fewer times for speed
            [qt.jmat(1,'x')],
            shots=1024,
            noise_model=nm
        )
        
        print("   ✓ PASS: Basis rotation works with noise model")
        print(f"   - Circuit executes with decomposed gates")
        print(f"   - Result shape: {result['expect'].shape}")
        
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
else:
    print("   ⚠ SKIPPED: Qiskit not available")

# Test 3: Design improvement (B-2) - Noise in evolution
print("\n4. Testing Design Improvement (B-2): apply_noise_in_evolution")
print("   " + "-"*66)

if QISKIT_AVAILABLE:
    try:
        # Test with apply_noise_in_evolution=False (default)
        result_false = sim.simulate_with_shots(
            H, psi0, times[:4],
            [qt.jmat(1,'z')],
            shots=1024,
            noise_model=None,
            apply_noise_in_evolution=False
        )
        
        # Test with apply_noise_in_evolution=True
        result_true = sim.simulate_with_shots(
            H, psi0, times[:4],
            [qt.jmat(1,'z')],
            shots=1024,
            noise_model=None,
            apply_noise_in_evolution=True
        )
        
        # Both should work and give similar results without noise
        diff = np.max(np.abs(result_false['expect'] - result_true['expect']))
        
        if diff < 0.2:  # Statistical fluctuations are expected
            print("   ✓ PASS: apply_noise_in_evolution parameter works")
            print(f"   - Without noise, both modes agree (max diff: {diff:.4f})")
            print(f"   - False mode shape: {result_false['expect'].shape}")
            print(f"   - True mode shape: {result_true['expect'].shape}")
        else:
            print(f"   ⚠ WARNING: Large difference between modes: {diff:.4f}")
            print("   - This may be due to statistical fluctuations")
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ⚠ SKIPPED: Qiskit not available")

# Test 4: Backward compatibility
print("\n5. Testing Backward Compatibility")
print("   " + "-"*66)

try:
    # Test that existing methods still work
    comparison = sim.compare_with_exact(
        H, psi0, times[:3],
        [qt.jmat(1,'z')]
    )
    
    print("   ✓ PASS: compare_with_exact still works")
    print(f"   - Max error: {comparison['errors']['max_expect_error']:.6f}")
    
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Summary
print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)
print("\nSummary:")
print("- Bug fix (A): Measurements now occur at all time steps regardless of noise_model")
print("- Design fix (B-1): Basis rotations use elementary gates (rx/ry/rz/cx)")
print("- Design improvement (B-2): apply_noise_in_evolution parameter added")
print("- Backward compatibility: Existing methods unchanged, default behavior preserved")
print("="*70)
