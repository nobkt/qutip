#!/usr/bin/env python3
"""
Installation checker for Qudit tutorials.

This script checks if all required and optional packages are installed
for running the Qudit tutorials.
"""

import sys


def check_package(package_name, import_name=None):
    """
    Check if a package is installed and return its version.
    
    Parameters
    ----------
    package_name : str
        Display name of the package
    import_name : str, optional
        Actual module name to import (if different from package_name)
    
    Returns
    -------
    bool
        True if package is installed, False otherwise
    """
    if import_name is None:
        import_name = package_name.lower().replace('-', '_').replace(' ', '_')
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✓ {package_name:20s}: {version}")
        return True
    except ImportError:
        print(f"✗ {package_name:20s}: NOT INSTALLED")
        return False


def main():
    """Main function to check all packages."""
    print("Checking package installation for Qudit tutorials...")
    print("=" * 70)
    
    # Required packages
    required_packages = [
        ('NumPy', 'numpy'),
        ('SciPy', 'scipy'),
        ('Matplotlib', 'matplotlib'),
        ('QuTiP', 'qutip'),
        ('Jupyter', 'jupyter'),
    ]
    
    print("\nRequired packages:")
    print("-" * 70)
    required_results = [check_package(name, imp) for name, imp in required_packages]
    all_required = all(required_results)
    
    # Optional packages - Qiskit
    print("\nOptional packages (Qiskit - methods 3-5):")
    print("-" * 70)
    qiskit_packages = [
        ('Qiskit', 'qiskit'),
        ('Qiskit-Aer', 'qiskit_aer'),
    ]
    qiskit_results = [check_package(name, imp) for name, imp in qiskit_packages]
    qiskit_available = all(qiskit_results)
    
    # Optional packages - MQT
    print("\nOptional packages (MQT Qudits - methods 6-8):")
    print("-" * 70)
    mqt_packages = [
        ('MQT Qudits', 'mqt.qudits'),
    ]
    mqt_results = [check_package(name, imp) for name, imp in mqt_packages]
    mqt_available = all(mqt_results)
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if all_required:
        print("✓ All required packages are installed!")
        print("  You can run the basic tutorials.")
    else:
        print("✗ Some required packages are missing!")
        print("  Install with: pip install numpy scipy matplotlib qutip jupyter")
        print("\nMissing packages:")
        for (name, _), installed in zip(required_packages, required_results):
            if not installed:
                print(f"  - {name}")
    
    print()
    
    if qiskit_available:
        print("✓ Qiskit packages are installed")
        print("  Methods 3-5 (Qiskit simulations) are available")
    else:
        print("⚠ Qiskit packages are not fully installed")
        print("  Methods 3-5 will be skipped in zeeman_effect_comprehensive.ipynb")
        print("  Install with: pip install qiskit qiskit-aer")
    
    print()
    
    if mqt_available:
        print("✓ MQT Qudits is installed")
        print("  Methods 6-8 (MQT simulations) are available")
    else:
        print("⚠ MQT Qudits is not installed")
        print("  Methods 6-8 will be skipped in zeeman_effect_comprehensive.ipynb")
        print("  Install with: pip install mqt.qudits")
    
    print("\n" + "=" * 70)
    
    # Return code
    if all_required:
        print("\n✓ Installation check passed!")
        return 0
    else:
        print("\n✗ Installation check failed - required packages missing")
        return 1


if __name__ == '__main__':
    sys.exit(main())
