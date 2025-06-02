#!/usr/bin/env python3
"""
NetSecSim Enhanced Professional Dashboard
Improved UI with better styling, animations, and features
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
    import matplotlib.patches as patches
    import numpy as np
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "networkx", "matplotlib", "numpy"])
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.patches as patches
    import numpy as np


class ModernButton(QPushButton):
    """Custom modern button with hover effects"""
    
    def __init__(self, text, color="#3498db", hover_color="#2980b9"):
        super().__init__(text)
        self.color = color
        self.hover_color = hover_color
        self.setMinimumHeight(45)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()
        
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {self.hover_color};
                transform: translateY(1px);
            }}
        """)


class StatusIndicator(QWidget):
    """Animated status indicator with pulsing effect"""
    
    def __init__(self, status="unknown"):
        super().__init__()
        self.status = status
        self.setFixedSize(20, 20)
        
    def set_status(self, status):
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = {
            "running": QColor(46, 204, 113),  # Green
            "stopped": QColor(149, 165, 166), # Gray
            "under_attack": QColor(231, 76, 60), # Red
            "unknown": QColor(149, 165, 166)
        }
        
        color = colors.get(self.status, colors["unknown"])
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawEllipse(2, 2, 16, 16)


class NetworkTopologyWidget(QWidget):
    """Enhanced network topology with better visualization"""
    
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(12, 8), facecolor='#2c3e50')
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.graph = nx.Graph()
        self.positions = {
            'as100': (-1, 0.5),
            'as200': (0, 0.5),
            'as300': (1, 0.5),
            'as400': (0, -0.5),
            'as500': (1, -0.5)
        }
        self.setup_graph()
        
    def setup_graph(self):
        containers = ['as100', 'as200', 'as300', 'as400', 'as500']
        for container in containers:
            self.graph.add_node(container, status='unknown', under_attack=False)
        
        edges = [('as100', 'as200'), ('as200', 'as300'), ('as200', 'as400'), ('as300', 'as500'), ('as400', 'as500')]
        for src, dst in edges:
            self.graph.add_edge(src, dst, status='unknown')
    
    def update_topology(self, container_data, bgp_data, attack_data=None):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='#34495e')
        
        for container, data in container_data.items():
            if container in self.graph.nodes:
                self.graph.nodes[container]['status'] = data.get('status', 'unknown')
                self.graph.nodes[container]['under_attack'] = data.get('under_attack', False)
        
        # Draw edges
        for edge in self.graph.edges():
            src, dst = edge
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[dst]
            
            src_bgp = bgp_data.get(src, {}).get('established', 0)
            dst_bgp = bgp_data.get(dst, {}).get('established', 0)
            
            if src_bgp > 0 and dst_bgp > 0:
                color = '#27ae60'
                linewidth = 4
                alpha = 0.8
            else:
                color = '#e74c3c'
                linewidth = 2
                alpha = 0.5
            
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, alpha=alpha)
        
        # Draw nodes
        for node in self.graph.nodes():
            x, y = self.positions[node]
            node_data = self.graph.nodes[node]
            
            if node_data['status'] == 'running':
                if node_data['under_attack']:
                    color = '#e74c3c'
                    size = 0.25
                else:
                    color = '#27ae60'
                    size = 0.2
            else:
                color = '#95a5a6'
                size = 0.15
            
            circle = plt.Circle((x, y), size, color=color, linewidth=3, zorder=2)
            ax.add_patch(circle)
            ax.text(x, y-size-0.15, node.upper(), ha='center', va='top', fontweight='bold', fontsize=12, color='white')
            
            bgp_sessions = bgp_data.get(node, {}).get('established', 0)
            routes = container_data.get(node, {}).get('routes', 0)
            status_text = f"BGP: {bgp_sessions}
Routes: {routes}"
            ax.text(x, y+size+0.1, status_text, ha='center', va='bottom', fontsize=10, color='#ecf0f1')
        
        if attack_data:
            for attack in attack_data:
                if attack['type'] == 'prefix_hijack':
                    ax.annotate('⚠️ HIJACK DETECTED!', xy=self.positions['as500'], xytext=(1.5, 0.8),
                              arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=3),
                              fontsize=14, color='#e74c3c', fontweight='bold', ha='center')
        
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, color='#bdc3c7')
        ax.set_facecolor('#34495e')
        ax.set_title('NetSecSim Network Topology - Real-time', fontsize=16, fontweight='bold', color='white', pad=20)
        self.canvas.draw()


class ContainerStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(320)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🖥️ Container Status")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        self.status_cards = {}
        containers = ['as100', 'as200', 'as300', 'as400', 'as500']
        
        for container in containers:
            card = self.create_status_card(container)
            main_layout.addWidget(card)
            
        main_layout.addStretch()
        self.setLayout(main_layout)
        
    def create_status_card(self, container):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 12px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        
        indicator = StatusIndicator()
        layout.addWidget(indicator)
        
        info_layout = QVBoxLayout()
        name_label = QLabel(container.upper())
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name_label)
        
        status_label = QLabel("UNKNOWN")
        bgp_label = QLabel("BGP: 0/0")
        info_layout.addWidget(status_label)
        info_layout.addWidget(bgp_label)
        
        layout.addLayout(info_layout)
        
        self.status_cards[container] = {
            'card': card,
            'indicator': indicator,
            'status': status_label,
            'bgp': bgp_label
        }
        
        return card
    
    def update_status(self, container_data, bgp_data):
        for container, widgets in self.status_cards.items():
            data = container_data.get(container, {})
            bgp = bgp_data.get(container, {})
            
            status = data.get('status', 'unknown')
            under_attack = data.get('under_attack', False)
            established = bgp.get('established', 0)
            neighbors = bgp.get('neighbors', 0)
            
            if under_attack:
                widgets['indicator'].set_status("under_attack")
            else:
                widgets['indicator'].set_status(status)
            
            if status == 'running':
                if under_attack:
                    widgets['status'].setText("🚨 UNDER ATTACK")
                    widgets['status'].setStyleSheet("color: #e74c3c; font-weight: bold;")
                else:
                    widgets['status'].setText("✅ ONLINE")
                    widgets['status'].setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                widgets['status'].setText("❌ OFFLINE")
                widgets['status'].setStyleSheet("color: #95a5a6;")
            
            widgets['bgp'].setText(f"BGP: {established}/{neighbors}")


class AttackControlWidget(QWidget):
    attack_launched = pyqtSignal(str)
    cleanup_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(320)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("⚔️ Attack Simulation")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.hijack_btn = ModernButton("🚨 Launch Prefix Hijack", "#e74c3c", "#c0392b")
        self.hijack_btn.clicked.connect(lambda: self.attack_launched.emit('hijack'))
        layout.addWidget(self.hijack_btn)
        
        self.poison_btn = ModernButton("☠️ Launch Route Poisoning", "#f39c12", "#e67e22")
        self.poison_btn.clicked.connect(lambda: self.attack_launched.emit('poison'))
        layout.addWidget(self.poison_btn)
        
        self.cleanup_btn = ModernButton("🧹 Clean Up Attacks", "#27ae60", "#229954")
        self.cleanup_btn.clicked.connect(self.cleanup_requested.emit)
        layout.addWidget(self.cleanup_btn)
        
        log_label = QLabel("📜 Attack Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(log_label)
        
        self.attack_log = QTextEdit()
        self.attack_log.setMaximumHeight(200)
        self.attack_log.setReadOnly(True)
        self.attack_log.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.attack_log)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def log_attack(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.attack_log.append(f"[{timestamp}] {message}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetSecSim Professional Dashboard v2.0")
        self.setMinimumSize(1600, 1000)
        self.resize(1800, 1200)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            }
            QWidget {
                background-color: #ecf0f1;
                border-radius: 8px;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.setup_ui()
        self.setup_data_thread()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        left_panel = QVBoxLayout()
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #bdc3c7;
            }
        """)
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(380)
        
        self.container_status = ContainerStatusWidget()
        left_panel.addWidget(self.container_status)
        
        self.attack_control = AttackControlWidget()
        self.attack_control.attack_launched.connect(self.launch_attack)
        self.attack_control.cleanup_requested.connect(self.cleanup_attacks)
        left_panel.addWidget(self.attack_control)
        
        main_layout.addWidget(left_widget)
        
        right_panel = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #bdc3c7;
            }
        """)
        right_widget.setLayout(right_panel)
        
        self.topology_widget = NetworkTopologyWidget()
        right_panel.addWidget(self.topology_widget)
        
        main_layout.addWidget(right_widget)
        
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("🚀 NetSecSim Dashboard v2.0 Ready")
        
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
        attack_count = len(attack_data)
        
        status_msg = f"🖥️ Containers: {online_count}/5 | ⚠️ Attacks: {attack_count} | 🕒 {datetime.now().strftime('%H:%M:%S')}"
        self.status_bar.showMessage(status_msg)
        
        if attack_count > 0:
            self.status_bar.setStyleSheet("QStatusBar { background-color: #e74c3c; color: white; }")
        else:
            self.status_bar.setStyleSheet("QStatusBar { background-color: #34495e; color: white; }")
    
    def launch_attack(self, attack_type):
        self.attack_control.log_attack(f"🚀 Launching {attack_type} attack...")
        
        reply = QMessageBox.question(self, 'Confirm Attack', 
                                   f'Launch {attack_type} attack?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            self.attack_control.log_attack("❌ Attack cancelled")
            return
        
        try:
            if attack_type == 'hijack':
                subprocess.run(['docker', 'exec', 'as500', 'vtysh', '-c', 
                               'configure terminal; router bgp 65500; network 8.8.8.0/24; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=30)
                self.attack_control.log_attack("✅ Prefix hijack launched")
                
            elif attack_type == 'poison':
                subprocess.run(['docker', 'exec', 'as400', 'vtysh', '-c', 
                               'configure terminal; router bgp 65400; neighbor 172.20.0.20 route-map POISON out; route-map POISON permit 10; set as-path prepend 65100 65200 65100; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=30)
                self.attack_control.log_attack("✅ Route poisoning launched")
                
        except Exception as e:
            self.attack_control.log_attack(f"❌ Error: {str(e)}")
    
    def cleanup_attacks(self):
        self.attack_control.log_attack("🧹 Cleaning up attacks...")
        
        try:
            containers = ['as100', 'as200', 'as300', 'as400', 'as500']
            for container in containers:
                subprocess.run(['docker', 'exec', container, 'vtysh', '-c', 
                               'configure terminal; router bgp 65' + container[2:] + '; no route-map POISON; no network 8.8.8.0/24; end; clear ip bgp * soft'], 
                               capture_output=True, text=True, timeout=10)
            
            self.attack_control.log_attack("✅ Cleanup complete")
                
        except Exception as e:
            self.attack_control.log_attack(f"❌ Cleanup error: {str(e)}")
    
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
            running_containers = result.stdout.strip().split('
') if result.stdout.strip() else []
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
                        lines = bgp_result.stdout.strip().split('
')
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
    app.setApplicationName("NetSecSim Professional Dashboard")
    app.setApplicationVersion("2.0")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
