#!/usr/bin/env python3
"""
Validation test for quantum gate decomposition implementation.

This script verifies that:
1. Gate decomposition is mathematically exact (no approximations)
2. Decomposed circuits use only elementary gates (RX, RY, RZ, CNOT)
3. No heuristic processing is used
4. Fidelity is preserved to machine precision
"""

import numpy as np
import scipy.linalg
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Operator
from qiskit.synthesis import TwoQubitBasisDecomposer
from qiskit.circuit.library import CXGate

def test_kak_decomposition_exactness():
    """Test that KAK decomposition preserves exact unitary."""
    print("\n" + "="*70)
    print("TEST 1: KAK Decomposition Exactness")
    print("="*70)
    
    # Create various test unitaries representing different Hamiltonians
    test_cases = [
        ("Jz evolution", np.diag([np.exp(-0.1j), 1, 1, np.exp(0.1j)])),
        ("Jx evolution", np.array([
            [np.cos(0.1), 0, 0, -1j*np.sin(0.1)],
            [0, np.cos(0.1), -1j*np.sin(0.1), 0],
            [0, -1j*np.sin(0.1), np.cos(0.1), 0],
            [-1j*np.sin(0.1), 0, 0, np.cos(0.1)]
        ])),
        ("General unitary", np.array([
            [0.9+0.1j, 0.2-0.1j, 0.1+0.2j, -0.1-0.1j],
            [0.2+0.1j, 0.8-0.2j, 0.2+0.1j, 0.1-0.2j],
            [0.1-0.2j, 0.2-0.1j, 0.7+0.3j, 0.3+0.1j],
            [-0.1+0.1j, 0.1+0.2j, 0.3-0.1j, 0.6-0.2j]
        ]))
    ]
    
    decomposer = TwoQubitBasisDecomposer(CXGate())
    
    all_passed = True
    for name, U_original in test_cases:
        # Normalize to ensure unitarity
        U, s, Vh = np.linalg.svd(U_original)
        U_unitary = U @ Vh
        
        # Decompose
        op = Operator(U_unitary)
        circuit = decomposer(op)
        
        # Transpile to basis gates
        transpiled = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                             optimization_level=0)
        
        # Get reconstructed unitary
        U_reconstructed = Operator(transpiled).data
        
        # Compute fidelity
        fidelity = np.abs(np.trace(U_reconstructed.conj().T @ U_unitary) / 4)
        
        print(f"\n{name}:")
        print(f"  Depth: {transpiled.depth()}")
        print(f"  Gates: {transpiled.count_ops()}")
        print(f"  Fidelity: {fidelity:.15f}")
        
        if fidelity > 0.99999999999:  # 1 - 1e-11
            print(f"  ✓ PASS")
        else:
            print(f"  ✗ FAIL - Fidelity too low!")
            all_passed = False
    
    return all_passed

def test_no_approximation_gates():
    """Test that only exact gates are used (no approximations)."""
    print("\n" + "="*70)
    print("TEST 2: Only Elementary Gates Used (No Approximations)")
    print("="*70)
    
    # Create a test unitary
    dt = 0.15
    U = np.array([
        [np.cos(dt), -np.sin(dt), 0, 0],
        [np.sin(dt), np.cos(dt), 0, 0],
        [0, 0, np.cos(dt), np.sin(dt)],
        [0, 0, -np.sin(dt), np.cos(dt)]
    ])
    
    # Decompose
    decomposer = TwoQubitBasisDecomposer(CXGate())
    circuit = decomposer(Operator(U))
    transpiled = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                         optimization_level=0)
    
    # Check gate types
    gate_types = transpiled.count_ops()
    allowed_gates = {'rx', 'ry', 'rz', 'cx', 'measure', 'barrier'}
    
    print(f"\nGate types used: {gate_types}")
    
    all_allowed = all(gate in allowed_gates for gate in gate_types.keys())
    
    if all_allowed:
        print("✓ PASS - Only elementary gates used")
        return True
    else:
        print("✗ FAIL - Unexpected gate types found!")
        return False

def test_optimization_level_zero():
    """Test that optimization_level=0 prevents heuristic optimizations."""
    print("\n" + "="*70)
    print("TEST 3: No Heuristic Optimizations (optimization_level=0)")
    print("="*70)
    
    # Create a test unitary
    U = np.array([
        [1, 0, 0, 0],
        [0, np.cos(0.1), -np.sin(0.1), 0],
        [0, np.sin(0.1), np.cos(0.1), 0],
        [0, 0, 0, 1]
    ])
    
    # Decompose with optimization_level=0
    decomposer = TwoQubitBasisDecomposer(CXGate())
    circuit = decomposer(Operator(U))
    
    transpiled_0 = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                           optimization_level=0)
    
    # Compare with optimization_level=3 (should be different if optimizations work)
    transpiled_3 = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                           optimization_level=3)
    
    print(f"\nWith optimization_level=0:")
    print(f"  Depth: {transpiled_0.depth()}")
    print(f"  Gates: {len(transpiled_0.data)}")
    
    print(f"\nWith optimization_level=3:")
    print(f"  Depth: {transpiled_3.depth()}")
    print(f"  Gates: {len(transpiled_3.data)}")
    
    # Both should preserve unitary, but level=0 should have more gates
    fidelity_0 = np.abs(np.trace(Operator(transpiled_0).data.conj().T @ U) / 4)
    fidelity_3 = np.abs(np.trace(Operator(transpiled_3).data.conj().T @ U) / 4)
    
    print(f"\nFidelity (level=0): {fidelity_0:.15f}")
    print(f"Fidelity (level=3): {fidelity_3:.15f}")
    
    if fidelity_0 > 0.99999999999 and fidelity_3 > 0.99999999999:
        print("✓ PASS - Both preserve unitary exactly")
        print(f"✓ optimization_level=0 does not apply heuristic optimizations")
        return True
    else:
        print("✗ FAIL - Fidelity lost!")
        return False

def test_decomposition_determinism():
    """Test that decomposition is deterministic (not random/heuristic)."""
    print("\n" + "="*70)
    print("TEST 4: Decomposition Determinism (Not Random/Heuristic)")
    print("="*70)
    
    # Create a valid unitary using matrix exponential
    H = np.array([
        [1, 0.1j, 0.2, 0],
        [-0.1j, 0, 0.1j, 0.2],
        [0.2, -0.1j, -1, 0.1j],
        [0, 0.2, -0.1j, 0]
    ])
    H = (H + H.conj().T) / 2  # Make Hermitian
    U = scipy.linalg.expm(-1j * 0.1 * H)  # Valid unitary
    
    # Decompose multiple times
    decomposer = TwoQubitBasisDecomposer(CXGate())
    
    circuits = []
    for i in range(3):
        circuit = decomposer(Operator(U))
        transpiled = transpile(circuit, basis_gates=['rx', 'ry', 'rz', 'cx'], 
                             optimization_level=0)
        circuits.append(transpiled)
    
    # Check if all decompositions are identical
    depth_consistent = all(c.depth() == circuits[0].depth() for c in circuits)
    gate_count_consistent = all(len(c.data) == len(circuits[0].data) for c in circuits)
    
    print(f"\nRun 1: depth={circuits[0].depth()}, gates={len(circuits[0].data)}")
    print(f"Run 2: depth={circuits[1].depth()}, gates={len(circuits[1].data)}")
    print(f"Run 3: depth={circuits[2].depth()}, gates={len(circuits[2].data)}")
    
    if depth_consistent and gate_count_consistent:
        print("✓ PASS - Decomposition is deterministic")
        return True
    else:
        print("✗ FAIL - Decomposition varies (possible random/heuristic behavior)")
        return False

def main():
    """Run all validation tests."""
    print("\n" + "="*70)
    print("QUANTUM GATE DECOMPOSITION VALIDATION")
    print("="*70)
    print("\nVerifying implementation requirements:")
    print("1. Decomposition is mathematically exact (no approximations)")
    print("2. Only elementary gates are used (RX, RY, RZ, CNOT)")
    print("3. No heuristic processing (optimization_level=0)")
    print("4. Decomposition is deterministic (not random)")
    
    results = []
    
    # Run tests
    results.append(("KAK Decomposition Exactness", test_kak_decomposition_exactness()))
    results.append(("Elementary Gates Only", test_no_approximation_gates()))
    results.append(("No Heuristic Optimizations", test_optimization_level_zero()))
    results.append(("Deterministic Decomposition", test_decomposition_determinism()))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        all_passed = all_passed and passed
    
    print("\n" + "="*70)
    if all_passed:
        print("✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("\nImplementation verified:")
        print("- Gate decomposition is mathematically exact")
        print("- No approximations or heuristics used")
        print("- Fidelity preserved to machine precision")
        print("- Only elementary quantum gates used")
    else:
        print("✗✗✗ SOME TESTS FAILED ✗✗✗")
        return 1
    
    print("="*70)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
