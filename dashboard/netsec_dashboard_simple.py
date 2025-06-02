#!/usr/bin/env python3
"""
NetSecSim Simple Professional Dashboard
Clean, working version with enhanced UI
"""

import sys
import subprocess
import time
from datetime import datetime

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
except ImportError:
    print("Installing PyQt6...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6"])
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import networkx as nx
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "networkx"])
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import networkx as nx


class TopologyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.positions = {
            'as100': (0, 1),
            'as200': (1, 1),
            'as300': (2, 1),
            'as400': (1, 0),
            'as500': (2, 0)
        }
    
    def update_topology(self, container_data, bgp_data, attacks):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f8f9fa')
        
        # Draw connections
        connections = [
            ('as100', 'as200'), ('as200', 'as300'),
            ('as200', 'as400'), ('as300', 'as500')
        ]
        
        for src, dst in connections:
            x1, y1 = self.positions[src]
            x2, y2 = self.positions[dst]
            
            src_status = container_data.get(src, {}).get('status') == 'running'
            dst_status = container_data.get(dst, {}).get('status') == 'running'
            
            if src_status and dst_status:
                color = 'green'
                width = 3
            else:
                color = 'red'
                width = 1
            
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=0.7)
        
        # Draw nodes
        for node, (x, y) in self.positions.items():
            data = container_data.get(node, {})
            status = data.get('status', 'unknown')
            under_attack = data.get('under_attack', False)
            
            if status == 'running':
                color = 'red' if under_attack else 'lightgreen'
                size = 300 if under_attack else 200
            else:
                color = 'lightgray'
                size = 100
            
            ax.scatter(x, y, s=size, c=color, edgecolors='black', linewidth=2, zorder=3)
            ax.text(x, y-0.2, node.upper(), ha='center', fontweight='bold', fontsize=10)
            
            # Status info
            routes = data.get('routes', 0)
            bgp_sessions = bgp_data.get(node, {}).get('established', 0)
            ax.text(x, y+0.2, f'BGP: {bgp_sessions}\nRoutes: {routes}', 
                   ha='center', fontsize=8, va='bottom')
        
        # Attack indicators
        if attacks:
            ax.text(2.5, 0.5, '⚠️ ATTACK\nDETECTED!', 
                   fontsize=12, color='red', fontweight='bold', ha='center')
        
        ax.set_xlim(-0.5, 2.5)
        ax.set_ylim(-0.5, 1.5)
        ax.set_title('NetSecSim Network Topology', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()


class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        title = QLabel("🖥️ Container Status")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.status_labels = {}
        
        for container in ['as100', 'as200', 'as300', 'as400', 'as500']:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 2px;
                }
            """)
            
            frame_layout = QHBoxLayout()
            
            status_dot = QLabel("●")
            status_dot.setStyleSheet("color: gray; font-size: 16px;")
            
            name_label = QLabel(container.upper())
            name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            
            status_text = QLabel("UNKNOWN")
            bgp_text = QLabel("BGP: 0/0")
            
            frame_layout.addWidget(status_dot)
            frame_layout.addWidget(name_label)
            frame_layout.addStretch()
            frame_layout.addWidget(status_text)
            frame_layout.addWidget(bgp_text)
            
            frame.setLayout(frame_layout)
            layout.addWidget(frame)
            
            self.status_labels[container] = {
                'dot': status_dot,
                'status': status_text,
                'bgp': bgp_text,
                'frame': frame
            }
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_status(self, container_data, bgp_data):
        for container, widgets in self.status_labels.items():
            data = container_data.get(container, {})
            bgp = bgp_data.get(container, {})
            
            status = data.get('status', 'unknown')
            under_attack = data.get('under_attack', False)
            established = bgp.get('established', 0)
            neighbors = bgp.get('neighbors', 0)
            
            if status == 'running':
                if under_attack:
                    widgets['dot'].setStyleSheet("color: red; font-size: 16px;")
                    widgets['status'].setText("UNDER ATTACK")
                    widgets['status'].setStyleSheet("color: red; font-weight: bold;")
                    widgets['frame'].setStyleSheet(widgets['frame'].styleSheet() + 
                                                  "QFrame { border: 2px solid red; }")
                else:
                    widgets['dot'].setStyleSheet("color: green; font-size: 16px;")
                    widgets['status'].setText("ONLINE")
                    widgets['status'].setStyleSheet("color: green; font-weight: bold;")
            else:
                widgets['dot'].setStyleSheet("color: gray; font-size: 16px;")
                widgets['status'].setText("OFFLINE")
                widgets['status'].setStyleSheet("color: gray;")
            
            widgets['bgp'].setText(f"BGP: {established}/{neighbors}")


class AttackWidget(QWidget):
    attack_requested = pyqtSignal(str)
    cleanup_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        title = QLabel("⚔️ Attack Simulation")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        hijack_btn = QPushButton("🚨 Launch Prefix Hijack")
        hijack_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        hijack_btn.clicked.connect(lambda: self.attack_requested.emit('hijack'))
        layout.addWidget(hijack_btn)
        
        poison_btn = QPushButton("☠️ Launch Route Poisoning")
        poison_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        poison_btn.clicked.connect(lambda: self.attack_requested.emit('poison'))
        layout.addWidget(poison_btn)
        
        cleanup_btn = QPushButton("🧹 Clean Up Attacks")
        cleanup_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        cleanup_btn.clicked.connect(self.cleanup_requested.emit)
        layout.addWidget(cleanup_btn)
        
        # Attack log
        log_label = QLabel("📜 Attack Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        log_label.setStyleSheet("color: #2c3e50; margin-top: 15px;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NetSecSim Professional Dashboard v2.0")
        self.setMinimumSize(1400, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
        
        self.setup_ui()
        self.setup_timer()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        # Left panel
        left_panel = QWidget()
        left_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
            }
        """)
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        self.status_widget = StatusWidget()
        left_layout.addWidget(self.status_widget)
        
        self.attack_widget = AttackWidget()
        self.attack_widget.attack_requested.connect(self.launch_attack)
        self.attack_widget.cleanup_requested.connect(self.cleanup_attacks)
        left_layout.addWidget(self.attack_widget)
        
        main_layout.addWidget(left_panel)
        
        # Right panel
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
            }
        """)
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        self.topology_widget = TopologyWidget()
        right_layout.addWidget(self.topology_widget)
        
        main_layout.addWidget(right_panel)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #34495e;
                color: white;
                font-weight: bold;
            }
        """)
        self.status_bar.showMessage("🚀 NetSecSim Dashboard Ready")
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(3000)  # Update every 3 seconds
        self.update_data()  # Initial update
    
    def update_data(self):
        try:
            # Get container status
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True, timeout=5)
            running_containers = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            container_data = {}
            bgp_data = {}
            attacks = []
            
            for container in ['as100', 'as200', 'as300', 'as400', 'as500']:
                container_data[container] = {
                    'status': 'running' if container in running_containers else 'stopped',
                    'routes': 0,
                    'under_attack': False
                }
                
                if container in running_containers:
                    # Get BGP data
                    try:
                        bgp_result = subprocess.run([
                            'docker', 'exec', container, 'vtysh', '-c', 'show ip bgp summary'
                        ], capture_output=True, text=True, timeout=3)
                        
                        if bgp_result.returncode == 0:
                            lines = bgp_result.stdout.strip().split('\n')
                            neighbors = established = 0
                            
                            for line in lines:
                                if '.' in line and len(line.split()) >= 8:
                                    parts = line.split()
                                    if len(parts) >= 10 and parts[0].count('.') == 3:
                                        neighbors += 1
                                        if "(Policy)" not in line:
                                            established += 1
                            
                            bgp_data[container] = {
                                'neighbors': neighbors,
                                'established': established
                            }
                    except:
                        bgp_data[container] = {'neighbors': 0, 'established': 0}
                    
                    # Check for attacks
                    try:
                        route_result = subprocess.run([
                            'docker', 'exec', container, 'vtysh', '-c', 'show ip bgp'
                        ], capture_output=True, text=True, timeout=3)
                        
                        if route_result.returncode == 0:
                            route_output = route_result.stdout
                            container_data[container]['routes'] = route_output.count('*>')
                            
                            if '8.8.8.0/24' in route_output and container != 'as300':
                                container_data[container]['under_attack'] = True
                                attacks.append({
                                    'type': 'prefix_hijack',
                                    'target': container
                                })
                    except:
                        pass
            
            # Update widgets
            self.status_widget.update_status(container_data, bgp_data)
            self.topology_widget.update_topology(container_data, bgp_data, attacks)
            
            # Update status bar
            online = sum(1 for data in container_data.values() if data['status'] == 'running')
            total_routes = sum(data['routes'] for data in container_data.values())
            attack_count = len(attacks)
            
            status_msg = f"🖥️ Containers: {online}/5 | 🛣️ Routes: {total_routes} | ⚠️ Attacks: {attack_count}"
            self.status_bar.showMessage(status_msg)
            
        except Exception as e:
            print(f"Update error: {e}")
    
    def launch_attack(self, attack_type):
        self.attack_widget.log_message(f"Launching {attack_type} attack...")
        
        reply = QMessageBox.question(self, 'Confirm Attack', 
                                   f'Launch {attack_type} attack?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if attack_type == 'hijack':
                    subprocess.run(['docker', 'exec', 'as500', 'vtysh', '-c', 
                                   'configure terminal; router bgp 65500; network 8.8.8.0/24; end; clear ip bgp * soft'], 
                                   timeout=20)
                    self.attack_widget.log_message("✅ Prefix hijack launched")
                    
                elif attack_type == 'poison':
                    subprocess.run(['docker', 'exec', 'as400', 'vtysh', '-c', 
                                   'configure terminal; router bgp 65400; neighbor 172.20.0.20 route-map POISON out; route-map POISON permit 10; set as-path prepend 65100 65200 65100; end; clear ip bgp * soft'], 
                                   timeout=20)
                    self.attack_widget.log_message("✅ Route poisoning launched")
                    
            except Exception as e:
                self.attack_widget.log_message(f"❌ Attack failed: {e}")
        else:
            self.attack_widget.log_message("❌ Attack cancelled")
    
    def cleanup_attacks(self):
        self.attack_widget.log_message("🧹 Cleaning up attacks...")
        
        try:
            for container in ['as100', 'as200', 'as300', 'as400', 'as500']:
                subprocess.run(['docker', 'exec', container, 'vtysh', '-c', 
                               f'configure terminal; router bgp 65{container[2:]}; no route-map POISON; no network 8.8.8.0/24; end; clear ip bgp * soft'], 
                               timeout=10)
            
            self.attack_widget.log_message("✅ Cleanup complete")
        except Exception as e:
            self.attack_widget.log_message(f"❌ Cleanup failed: {e}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NetSecSim Dashboard")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
