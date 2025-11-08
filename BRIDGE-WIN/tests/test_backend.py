"""
Backend Testing Script

Simple script to test com0com backend integration.
Tests detection, port enumeration, and basic operations.

Usage: python test_backend.py
"""

from backend.com0com_manager import Com0comManager
from backend.virtual_ports import VirtualPortManager
from utils.logger import get_logger

logger = get_logger(__name__)


def test_com0com_detection():
    """Test com0com installation detection."""
    print("\n" + "="*60)
    print("TEST 1: com0com Detection")
    print("="*60)
    
    manager = Com0comManager()
    
    print(f"com0com installed: {manager.is_installed}")
    if manager.is_installed:
        print(f"setupc.exe path: {manager.setupc_path}")
    else:
        print("⚠ com0com is not installed on this system")
        print("  Download from: https://sourceforge.net/projects/com0com/")
    
    return manager.is_installed


def test_port_enumeration():
    """Test port enumeration."""
    print("\n" + "="*60)
    print("TEST 2: Port Enumeration")
    print("="*60)
    
    vpm = VirtualPortManager()
    
    # List all ports
    all_ports = vpm.get_all_ports()
    print(f"\nAll COM ports on system ({len(all_ports)}):")
    for port in all_ports:
        print(f"  - {port}")
    
    # List available port numbers
    available = vpm.get_available_port_numbers(1, 20)
    print(f"\nAvailable port numbers (1-20): {sorted(available)}")
    
    # Find next available pair
    pair = vpm.find_next_available_port_pair()
    if pair:
        print(f"\nNext available port pair: COM{pair[0]} <-> COM{pair[1]}")
    else:
        print("\n⚠ No available port pairs found")


def test_list_virtual_pairs():
    """Test listing existing virtual port pairs."""
    print("\n" + "="*60)
    print("TEST 3: List Virtual Port Pairs")
    print("="*60)
    
    vpm = VirtualPortManager()
    
    if not vpm.is_com0com_available():
        print("⚠ com0com not available - skipping test")
        return
    
    pairs = vpm.list_virtual_port_pairs()
    
    if pairs:
        print(f"\nFound {len(pairs)} virtual port pair(s):")
        for i, pair in enumerate(pairs, 1):
            print(f"\nPair {i}:")
            print(f"  Port A: {pair['port_a']}")
            print(f"  Params A: {pair['params_a']}")
            print(f"  Port B: {pair['port_b']}")
            print(f"  Params B: {pair['params_b']}")
    else:
        print("\nNo virtual port pairs currently installed")
        print("Use setupc.exe or the GUI to create port pairs")


def test_port_availability():
    """Test port availability checking."""
    print("\n" + "="*60)
    print("TEST 4: Port Availability Check")
    print("="*60)
    
    vpm = VirtualPortManager()
    
    test_ports = ['COM1', 'COM2', 'COM3', 'COM10', 'COM99']
    
    print("\nChecking port availability:")
    for port in test_ports:
        available = vpm.is_port_available(port)
        status = "✓ Available" if available else "✗ In use"
        print(f"  {port}: {status}")


def main():
    """Run all backend tests."""
    print("\n" + "="*60)
    print("BRIDGE-WIN Backend Integration Tests")
    print("="*60)
    
    # Test 1: Detection
    com0com_available = test_com0com_detection()
    
    # Test 2: Port enumeration
    test_port_enumeration()
    
    # Test 3: List virtual pairs (only if com0com is installed)
    if com0com_available:
        test_list_virtual_pairs()
    
    # Test 4: Port availability
    test_port_availability()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"com0com available: {com0com_available}")
    if com0com_available:
        print("✓ Backend integration is working")
        print("\nNext steps:")
        print("  1. Create GUI for port management (Phase 3)")
        print("  2. Add serial sniffing functionality (Phase 4)")
    else:
        print("⚠ Install com0com to enable full functionality")
        print("  Download: https://sourceforge.net/projects/com0com/")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()

