#!/usr/bin/env python3
"""
NetSecSim Topology Visualizer - Simplified for Ubuntu system packages
"""

import subprocess
import json
import re
import time
from datetime import datetime
import sys

# Check if we can import required packages
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    print("✓ matplotlib imported successfully")
except ImportError as e:
    print(f"✗ matplotlib import failed: {e}")
    print("Run: sudo apt install python3-matplotlib")
    sys.exit(1)

try:
    import networkx as nx
    print("✓ networkx imported successfully") 
except ImportError as e:
    print(f"✗ networkx import failed: {e}")
    print("Run: sudo apt install python3-networkx")
    sys.exit(1)

class SimpleTopologyVisualizer:
    def __init__(self):
        self.containers = ['as1', 'as2']
        self.as_mapping = {
            'as1': {'asn': 65001, 'ip': '10.1.0.2'},
            'as2': {'asn': 65002, 'ip': '10.1.0.3'}
        }
        
    def get_bgp_status(self, container):
        """Get BGP status from container"""
        try:
            result = subprocess.run(
                ['docker', 'exec', '-t', container, 'vtysh', '-c', 'show ip bgp summary'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"BGP command failed for {container}")
                return None
        except Exception as e:
            print(f"Error getting BGP status from {container}: {e}")
            return None
    
    def get_bgp_routes(self, container):
        """Get BGP routes from container"""
        try:
            result = subprocess.run(
                ['docker', 'exec', '-t', container, 'vtysh', '-c', 'show ip bgp'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"BGP routes command failed for {container}")
                return None
        except Exception as e:
            print(f"Error getting BGP routes from {container}: {e}")
            return None
    
    def create_simple_topology(self, output_file='topology.png'):
        """Create a simple topology visualization"""
        print("Creating topology visualization...")
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        # AS positions
        as1_pos = (1, 2)
        as2_pos = (4, 2)
        
        # Draw AS nodes
        circle1 = plt.Circle(as1_pos, 0.5, color='lightblue', alpha=0.7)
        circle2 = plt.Circle(as2_pos, 0.5, color='lightgreen', alpha=0.7)
        ax.add_patch(circle1)
        ax.add_patch(circle2)
        
        # Add AS labels
        ax.text(as1_pos[0], as1_pos[1], 'AS1\n65001\n10.1.0.2', ha='center', va='center', fontsize=10, weight='bold')
        ax.text(as2_pos[0], as2_pos[1], 'AS2\n65002\n10.1.0.3', ha='center', va='center', fontsize=10, weight='bold')
        
        # Draw connection
        ax.plot([as1_pos[0]+0.5, as2_pos[0]-0.5], [as1_pos[1], as2_pos[1]], 'k-', linewidth=2)
        ax.text(2.5, 2.2, 'BGP Session', ha='center', va='bottom', fontsize=9)
        
        # Check BGP status
        bgp1_ok = self.get_bgp_status('as1') is not None
        bgp2_ok = self.get_bgp_status('as2') is not None
        
        if bgp1_ok and bgp2_ok:
            status_color = 'green'
            status_text = 'BGP: ESTABLISHED'
        else:
            status_color = 'red'  
            status_text = 'BGP: DOWN'
            
        ax.text(2.5, 1.5, status_text, ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor=status_color, alpha=0.7),
                fontsize=12, weight='bold', color='white')
        
        # Set limits and styling
        ax.set_xlim(0, 5)
        ax.set_ylim(1, 3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add title
        plt.title(f'NetSecSim BGP Topology\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                 fontsize=14, weight='bold')
        
        # Save
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✓ Topology saved to {output_file}")
        
        plt.close()
        return output_file
    
    def analyze_bgp(self):
        """Analyze current BGP state"""
        print("\n=== BGP Analysis ===")
        
        for container in self.containers:
            print(f"\n{container.upper()} (AS{self.as_mapping[container]['asn']}):")
            print("-" * 30)
            
            # BGP Summary
            summary = self.get_bgp_status(container)
            if summary:
                lines = summary.split('\n')
                for line in lines:
                    if 'neighbor' in line.lower() or 'established' in line.lower() or '10.1.0.' in line:
                        print(f"  {line.strip()}")
            
            # BGP Routes  
            routes = self.get_bgp_routes(container)
            if routes:
                print("  Routes:")
                lines = routes.split('\n')
                for line in lines:
                    if line.strip().startswith('*'):
                        print(f"    {line.strip()}")

def main():
    print("NetSecSim Simple Topology Visualizer")
    print("===================================")
    
    visualizer = SimpleTopologyVisualizer()
    
    # Create topology
    topo_file = visualizer.create_simple_topology('current_topology.png')
    
    # Analyze BGP
    visualizer.analyze_bgp()
    
    print(f"\n✓ Complete! Check {topo_file} for the topology diagram.")

if __name__ == "__main__":
    main()
