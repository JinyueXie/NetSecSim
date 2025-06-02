#!/usr/bin/env python3
import subprocess
import sys

def test_docker():
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        containers = result.stdout.strip().split('\n')
        print(f"Found containers: {containers}")
        return 'as1' in containers and 'as2' in containers
    except Exception as e:
        print(f"Docker test failed: {e}")
        return False

def test_bgp(container):
    try:
        result = subprocess.run(['docker', 'exec', '-t', container, 'vtysh', '-c', 'show ip bgp summary'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✓ BGP working on {container}")
            return True
        else:
            print(f"✗ BGP failed on {container}")
            return False
    except Exception as e:
        print(f"✗ BGP test failed on {container}: {e}")
        return False

def test_python_libs():
    try:
        import matplotlib
        print("✓ matplotlib imported")
    except ImportError:
        print("✗ matplotlib missing - run: sudo apt install python3-matplotlib")
        return False
    
    try:
        import networkx
        print("✓ networkx imported")
    except ImportError:
        print("✗ networkx missing - run: sudo apt install python3-networkx")
        return False
    
    return True

def main():
    print("NetSecSim System Test")
    print("====================")
    
    # Test Python libraries
    if not test_python_libs():
        print("Install missing packages first!")
        return
    
    # Test Docker
    if not test_docker():
        print("Docker containers not ready!")
        return
    
    # Test BGP
    bgp1_ok = test_bgp('as1')
    bgp2_ok = test_bgp('as2')
    
    if bgp1_ok and bgp2_ok:
        print("\n🎉 All systems ready! You can run the visualization now.")
    else:
        print("\n⚠️ BGP issues detected. Check your FRR configuration.")

if __name__ == "__main__":
    main()
