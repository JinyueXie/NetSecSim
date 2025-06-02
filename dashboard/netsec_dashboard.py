#!/usr/bin/env python3
"""
NetSecSim Qt-based Professional Dashboard
Real-time network security simulation monitoring and control interface
"""

import sys
import json
import subprocess
import threading
import time
from datetime import datetime
from collections import deque
import signal

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCharts import *
except ImportError:
    print("Installing PyQt6 and dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6", "PyQt6-Charts"])
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCharts import *

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "networkx", "matplotlib"])
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure


class NetworkTopologyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.graph = nx.Graph()
        self.positions = {
            'as100': (0, 1),
            'as200': (1, 1), 
            'as300': (2, 1),
            'as400': (1, 0),
            'as500': (2, 0)
        }
        self.setup_graph()
        
    def setup_graph(self):
        containers = ['as100', 'as200', 'as300', 'as400', 'as500']
        for container in containers:
            self.graph.add_node(container, status='unknown', under_attack=False)
        
        edges = [('as100', 'as200'), ('as200', 'as300'), ('as200', 'as400'), ('as300', 'as500')]
        for src, dst in edges:
            self.graph.add_edge(src, dst, status='unknown')
    
    def update_topology(self, container_data, bgp_data, attack_data=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        for container, data in container_data.items():
            if container in self.graph.nodes:
                self.graph.nodes[container]['status'] = data.get('status', 'unknown')
                self.graph.nodes[container]['under_attack'] = data.get('under_attack', False)
        
        for edge in self.graph.edges():
            src, dst = edge
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[dst]
            
            edge_color = 'green' if (bgp_data.get(src, {}).get('established', 0) > 0 and 
                                   bgp_data.get(dst, {}).get('established', 0) > 0) else 'red'
            linewidth = 3 if edge_color == 'green' else 1
            
            ax.plot([x1, x2], [y1, y2], color=edge_color, linewidth=linewidth, alpha=0.7)
        
        for node in self.graph.nodes():
            x, y = self.positions[node]
            node_data = self.graph.nodes[node]
            
            if node_data['status'] == 'running':
                color = 'red' if node_data['under_attack'] else 'lightgreen'
                edgecolor = 'darkred' if node_data['under_attack'] else 'green'
            else:
                color = 'lightgray'
                edgecolor = 'gray'
            
            circle = plt.Circle((x, y), 0.15, color=color, ec=edgecolor, linewidth=3)
            ax.add_patch(circle)
            ax.text(x, y-0.25, node.upper(), ha='center', va='top', fontweight='bold')
            
            bgp_sessions = bgp_data.get(node, {}).get('established', 0)
            routes = container_data.get(node, {}).get('routes', 0)
            status_text = f"BGP: {bgp_sessions}\nRoutes: {routes}"
            ax.text(x, y+0.25, status_text, ha='center', va='bottom', fontsize=8,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        if attack_data:
            for attack in attack_data:
                if attack['type'] == 'prefix_hijack':
                    ax.annotate('HIJACK!', xy=self.positions['as500'], xytext=(2.5, 0.5),
                              arrowprops=dict(arrowstyle='->', color='red', lw=3),
                              fontsize=12, color='red', fontweight='bold')
        
        ax.set_xlim(-0.5, 2.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_title('NetSecSim Network Topology', fontsize=14, fontweight='bold')
        self.canvas.draw()


class ContainerStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        title = QLabel("Container Status")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout.addWidget(title)
        
        self.status_labels = {}
        containers = ['as100', 'as200', 'as300', 'as400', 'as500']
        
        for container in containers:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame_layout = QHBoxLayout()
            
            indicator = QLabel("●")
            indicator.setStyleSheet("color: gray; font-size: 16px;")
            
            name_label = QLabel(container.upper())
            name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            
            status_label = QLabel("UNKNOWN")
            bgp_label = QLabel("BGP: 0/0")
            bgp_label.setStyleSheet("color: #666;")
            
            frame_layout.addWidget(indicator)
            frame_layout.addWidget(name_label)
            frame_layout.addWidget(status_label)
            frame_layout.addStretch()
            frame_layout.addWidget(bgp_label)
            
            frame.setLayout(frame_layout)
            self.layout.addWidget(frame)
            
            self.status_labels[container] = {
                'indicator': indicator,
                'status': status_label,
                'bgp': bgp_label,
                'frame': frame
            }
        
        self.layout.addStretch()
    
    def update_status(self, container_data, bgp_data):
        for container, widgets in self.status_labels.items():
            data = container_data.get(container, {})
            bgp = bgp_data.get(container, {})
            
            status = data.get('status', 'unknown')
            under_attack = data.get('under_attack', False)
            established = bgp.get('established', 0)
            neighbors = bgp.get('neighbors', 0)
            
            if status == 'running':
                color = "red" if under_attack else "green"
                widgets['indicator'].setStyleSheet(f"color: {color}; font-size: 16px;")
                widgets['status'].setText("ONLINE" if not under_attack else "UNDER ATTACK")
                widgets['status'].setStyleSheet("color: red;" if under_attack else "color: green;")
            else:
                widgets['indicator'].setStyleSheet("color: gray; font-size: 16px;")
                widgets['status'].setText("OFFLINE")
                widgets['status'].setStyleSheet("color: gray;")
            
            widgets['bgp'].setText(f"BGP: {established}/{neighbors}")
            
            if under_attack:
                widgets['frame'].setStyleSheet("QFrame { border: 2px solid red; background-color: #ffe6e6; }")
            else:
                widgets['frame'].setStyleSheet("QFrame { border: 1px solid #ccc; }")


class AttackControlWidget(QWidget):
    attack_launched = pyqtSignal(str)
    cleanup_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        title = QLabel("Attack Simulation")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.layout.addWidget(title)
        
        self.hijack_btn = QPushButton("🚨 Launch Prefix Hijack")
        self.hijack_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; padding: 10px; }")
        self.hijack_btn.clicked.connect(lambda: self.attack_launched.emit('hijack'))
        
        self.poison_btn = QPushButton("☠️ Launch Route Poisoning")
        self.poison_btn.setStyleSheet("QPushButton { background-color: #ff8e53; color: white; font-weight: bold; padding: 10px; }")
        self.poison_btn.clicked.connect(lambda: self.attack_launched.emit('poison'))
        
        self.cleanup_btn = QPushButton("🧹 Clean Up Attacks")
        self.cleanup_btn.setStyleSheet("QPushButton { background-color: #4ecdc4; color: white; font-weight: bold; padding: 10px; }")
        self.cleanup_btn.clicked.connect(self.cleanup_requested.emit)
        
        self.layout.addWidget(self.hijack_btn)
        self.layout.addWidget(self.poison_btn)
        self.layout.addWidget(self.cleanup_btn)
        
        self.attack_log = QTextEdit()
        self.attack_log.setMaximumHeight(150)
        self.attack_log.setReadOnly(True)
        self.layout.addWidget(QLabel("Attack Log:"))
        self.layout.addWidget(self.attack_log)
        
        self.layout.addStretch()
    
    def log_attack(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.attack_log.append(f"[{timestamp}] {message}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetSecSim Professional Dashboard")
        self.resize(1400, 900)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QWidget { background-color: white; border-radius: 5px; }
            QLabel { color: #333; }
            QPushButton { border: none; border-radius: 5px; padding: 8px 16px; font-weight: bold; }
            QPushButton:hover { opacity: 0.8; }
            QFrame { border: 1px solid #ddd; border-radius: 5px; margin: 2px; padding: 5px; }
        """)
        
        self.setup_ui()
        self.setup_data_thread()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        left_panel = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(300)
        
        self.container_status = ContainerStatusWidget()
        left_panel.addWidget(self.container_status)
        
        self.attack_control = AttackControlWidget()
        self.attack_control.attack_launched.connect(self.launch_attack)
        self.attack_control.cleanup_requested.connect(self.cleanup_attacks)
        left_panel.addWidget(self.attack_control)
        
        main_layout.addWidget(left_widget)
        
        right_panel = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        self.topology_widget = NetworkTopologyWidget()
        right_panel.addWidget(self.topology_widget)
        
        main_layout.addWidget(right_widget)
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("NetSecSim Dashboard Ready")
        
    def setup_data_thread(self):
        self.data_thread = DataCollectionThread()
        self.data_thread.data_updated.connect(self.update_dashboard)
        self.data_thread.start()
    
    def update_dashboard(self, data):
        container_data = data.get('containers', {})
        bgp_data = data.get('bgp_sessions', {})
        attack_data = data.get('attacks', [])
        
        self.container_status.update_status(container_data, bgp_data)
        self.topology_widget.update_topology(container_data, bgp_data, attack_data)
        
        online_count = sum(1 for data in container_data.values() if data.get('status') == 'running')
        self.status_bar.showMessage(f"Containers: {online_count}/5 online | Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    def launch_attack(self, attack_type):
        self.attack_control.log_attack(f"Launching {attack_type} attack...")
        
        try:
            if attack_type == 'hijack':
                subprocess.run(['docker', 'exec', 'as500', 'vtysh', '-c', 
                               'configure terminal; router bgp 65500; network 8.8.8.0/24; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=30)
                self.attack_control.log_attack("✅ Prefix hijack attack launched")
            elif attack_type == 'poison':
                subprocess.run(['docker', 'exec', 'as400', 'vtysh', '-c', 
                               'configure terminal; router bgp 65400; neighbor 172.20.0.20 route-map POISON out; route-map POISON permit 10; set as-path prepend 65100 65200 65100; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=30)
                self.attack_control.log_attack("✅ Route poisoning attack launched")
                
        except Exception as e:
            self.attack_control.log_attack(f"❌ Error launching {attack_type}: {str(e)}")
    
    def cleanup_attacks(self):
        self.attack_control.log_attack("Cleaning up all attacks...")
        
        try:
            containers = ['as100', 'as200', 'as300', 'as400', 'as500']
            for container in containers:
                subprocess.run(['docker', 'exec', container, 'vtysh', '-c', 
                               'configure terminal; router bgp 65' + container[2:] + '; no route-map POISON; no network 8.8.8.0/24; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=10)
            
            self.attack_control.log_attack("✅ All attacks cleaned up successfully")
                
        except Exception as e:
            self.attack_control.log_attack(f"❌ Error during cleanup: {str(e)}")
    
    def closeEvent(self, event):
        if hasattr(self, 'data_thread'):
            self.data_thread.stop()
            self.data_thread.wait()
        event.accept()


class DataCollectionThread(QThread):
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            try:
                data = self.collect_network_data()
                self.data_updated.emit(data)
                time.sleep(2)
            except Exception as e:
                print(f"Data collection error: {e}")
                time.sleep(5)
    
    def collect_network_data(self):
        containers = ['as100', 'as200', 'as300', 'as400', 'as500']
        data = {
            'timestamp': datetime.now().isoformat(),
            'containers': {},
            'bgp_sessions': {},
            'attacks': []
        }
        
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True, timeout=5)
            running_containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
        except:
            running_containers = []
        
        for container in containers:
            container_data = {
                'status': 'running' if container in running_containers else 'stopped',
                'routes': 0,
                'under_attack': False
            }
            
            if container in running_containers:
                try:
                    bgp_result = subprocess.run([
                        'docker', 'exec', container, 'vtysh', '-c', 'show ip bgp summary'
                    ], capture_output=True, text=True, timeout=5)
                    
                    if bgp_result.returncode == 0:
                        lines = bgp_result.stdout.strip().split('\n')
                        neighbor_count = 0
                        established_count = 0
                        
                        for line in lines:
                            if line.strip() and '.' in line and len(line.split()) >= 8:
                                parts = line.split()
                                if len(parts) >= 10 and parts[0].count('.') == 3:
                                    neighbor_count += 1
                                    if "(Policy)" not in line:
                                        established_count += 1
                        
                        data['bgp_sessions'][container] = {
                            'neighbors': neighbor_count,
                            'established': established_count
                        }
                except:
                    data['bgp_sessions'][container] = {'neighbors': 0, 'established': 0}
                
                try:
                    route_result = subprocess.run([
                        'docker', 'exec', container, 'vtysh', '-c', 'show ip bgp'
                    ], capture_output=True, text=True, timeout=5)
                    
                    if route_result.returncode == 0:
                        route_output = route_result.stdout
                        container_data['routes'] = route_output.count('*>')
                        
                        if '8.8.8.0/24' in route_output and container != 'as300':
                            container_data['under_attack'] = True
                            data['attacks'].append({
                                'type': 'prefix_hijack',
                                'target': container,
                                'network': '8.8.8.0/24'
                            })
                except:
                    pass
            
            data['containers'][container] = container_data
        
        return data
    
    def stop(self):
        self.running = False


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NetSecSim Dashboard")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("NetSecSim Project")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
