#!/usr/bin/env python3
"""
NetSecSim Enhanced Professional Dashboard
Modern UI with Apple-inspired design, animations, and professional aesthetics
"""

import sys
import json
import subprocess
import threading
import time
from PyQt5 import QtGui
from datetime import datetime
from collections import deque
import signal
from PyQt5.QtWidgets import QMainWindow, QApplication
import random
import math
import os
from PyQt6.QtGui import QIcon

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCharts import *
except ImportError:
    print("Installing PyQt6...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyQt6", "PyQt6-Charts"])
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtCharts import *

# Modern Color Palette (Apple-inspired)
class NetSecColors:
    BACKGROUND = "#f5f6fa"
    PANEL_BG = "#ffffff"
    PRIMARY_BLUE = "#007AFF"
    SUCCESS_GREEN = "#2ecc71"
    WARNING_ORANGE = "#f39c12"
    DANGER_RED = "#e74c3c"
    TEXT_PRIMARY = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"
    BORDER_LIGHT = "#ecf0f1"
    SHADOW = "rgba(0, 0, 0, 0.1)"

class ModernButton(QPushButton):
    """Custom button with modern styling and hover effects"""
    
    def __init__(self, text, color=NetSecColors.PRIMARY_BLUE, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setupStyle()
        self.setupAnimation()
    
    def setupStyle(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: "SF Pro Text", "Inter", "Segoe UI", sans-serif;
            }}
            QPushButton:hover {{
                background-color: {self.base_color};
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                background-color: {self.base_color};
                opacity: 0.6;
            }}
        """)
    
    def setupAnimation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        
    def adjustColor(self, color, factor):
        """Simple color adjustment"""
        return color

class StatusIndicator(QWidget):
    """Animated status indicator with pulse effect"""
    
    def __init__(self, status="online", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)
        
        # Pulse animation
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update)
        self.pulse_timer.start(1000)
        self.pulse_phase = 0
        
    def setStatus(self, status):
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color based on status
        colors = {
            "online": NetSecColors.SUCCESS_GREEN,
            "warning": NetSecColors.WARNING_ORANGE,
            "offline": NetSecColors.DANGER_RED,
            "attack": NetSecColors.DANGER_RED
        }
        
        color = QColor(colors.get(self.status, NetSecColors.TEXT_SECONDARY))
        
        # Pulse effect for attack status
        if self.status == "attack":
            self.pulse_phase += 0.1
            alpha = int(255 * (0.7 + 0.3 * math.sin(self.pulse_phase)))
            color.setAlpha(alpha)
        
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 12, 12)

class NetworkTopologyWidget(QWidget):
    """Enhanced network topology visualization with animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.nodes = self.generateNetworkNodes()
        self.connections = self.generateConnections()
        self.attack_path = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.updateAnimations)
        self.animation_timer.start(50)  # 20 FPS
        self.animation_phase = 0
        
    def generateNetworkNodes(self):
        """Generate AS network nodes with realistic positioning"""
        nodes = {
            "AS100": {"pos": (150, 300), "status": "online", "routes": 6, "type": "tier1"},
            "AS200": {"pos": (400, 300), "status": "online", "routes": 8, "type": "tier1"},
            "AS300": {"pos": (650, 300), "status": "online", "routes": 6, "type": "tier1"},
            "AS400": {"pos": (400, 150), "status": "online", "routes": 4, "type": "tier2"},
            "AS500": {"pos": (400, 450), "status": "online", "routes": 4, "type": "tier2"},
        }
        return nodes
    
    def generateConnections(self):
        """Generate BGP connections between AS nodes"""
        return [
            ("AS100", "AS200"),
            ("AS200", "AS300"),
            ("AS200", "AS400"),
            ("AS200", "AS500"),
            ("AS100", "AS400"),
            ("AS300", "AS500")
        ]
    
    def simulateAttack(self, attack_type="prefix_hijack"):
        """Simulate network attack with visual effects"""
        if attack_type == "prefix_hijack":
            self.nodes["AS100"]["status"] = "attack"
            self.nodes["AS400"]["status"] = "attack" 
            self.attack_path = [("AS100", "AS400"), ("AS400", "AS200")]
        
        self.update()
    
    def clearAttacks(self):
        """Clear all attacks and restore normal state"""
        for node in self.nodes.values():
            node["status"] = "online"
        self.attack_path = []
        self.update()
    
    def updateAnimations(self):
        """Update animation states"""
        self.animation_phase += 0.1
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor(NetSecColors.PANEL_BG))
        
        # Draw connections first
        self.drawConnections(painter)
        
        # Draw nodes on top
        self.drawNodes(painter)
        
        # Draw attack detection banner if needed
        if any(node["status"] == "attack" for node in self.nodes.values()):
            self.drawAttackBanner(painter)
    
    def drawConnections(self, painter):
        """Draw BGP connections between nodes"""
        pen = QPen(QColor(NetSecColors.BORDER_LIGHT), 3)
        painter.setPen(pen)
        
        for connection in self.connections:
            node1, node2 = connection
            pos1 = self.nodes[node1]["pos"]
            pos2 = self.nodes[node2]["pos"]
            
            # Highlight attack paths
            if connection in self.attack_path or (node2, node1) in self.attack_path:
                pen.setColor(QColor(NetSecColors.DANGER_RED))
                pen.setWidth(5)
                # Animated dashed line for attack
                pen.setStyle(Qt.PenStyle.DashLine)
                pen.setDashOffset(int(self.animation_phase * 10) % 20)
            else:
                pen.setColor(QColor(NetSecColors.SUCCESS_GREEN))
                pen.setWidth(3)
                pen.setStyle(Qt.PenStyle.SolidLine)
            
            painter.setPen(pen)
            painter.drawLine(pos1[0], pos1[1], pos2[0], pos2[1])
    
    def drawNodes(self, painter):
        """Draw AS nodes with status indicators"""
        for node_id, node_data in self.nodes.items():
            x, y = node_data["pos"]
            status = node_data["status"]
            
            # Node background circle
            if status == "attack":
                # Pulsing red for attacks
                alpha = int(255 * (0.7 + 0.3 * math.sin(self.animation_phase)))
                color = QColor(NetSecColors.DANGER_RED)
                color.setAlpha(alpha)
            else:
                color = QColor(NetSecColors.SUCCESS_GREEN)
            
            # Draw node circle with shadow effect
            shadow_offset = 2
            painter.setBrush(QBrush(QColor(0, 0, 0, 30)))  # Shadow
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x - 18 + shadow_offset, y - 18 + shadow_offset, 36, 36)
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(NetSecColors.TEXT_PRIMARY), 2))
            painter.drawEllipse(x - 18, y - 18, 36, 36)
            
            # Node label
            painter.setPen(QPen(QColor(NetSecColors.TEXT_PRIMARY)))
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            
            # Center text in node
            text_rect = QRect(x - 30, y - 8, 60, 16)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, node_id)
            
            # Routes info below node
            painter.setFont(QFont("Arial", 10))
            painter.setPen(QPen(QColor(NetSecColors.TEXT_SECONDARY)))
            info_text = f"BGP: {node_data['routes']}\nRoutes: {node_data['routes']}"
            info_rect = QRect(x - 40, y + 25, 80, 30)
            painter.drawText(info_rect, Qt.AlignmentFlag.AlignCenter, info_text)
    
    def drawAttackBanner(self, painter):
        """Draw attack detection banner"""
        banner_rect = QRect(10, 10, self.width() - 20, 40)
        
        # Animated background
        alpha = int(255 * (0.8 + 0.2 * math.sin(self.animation_phase * 2)))
        bg_color = QColor(NetSecColors.DANGER_RED)
        bg_color.setAlpha(alpha)
        
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(banner_rect, 8, 8)
        
        # Warning text
        painter.setPen(QPen(QColor("white")))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(banner_rect, Qt.AlignmentFlag.AlignCenter, "⚠️ ATTACK DETECTED!")

class ModernPanel(QFrame):
    """Modern panel with shadow and rounded corners"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setupStyle()
        self.setupLayout(title)
    
    def setupStyle(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {NetSecColors.PANEL_BG};
                border: 1px solid {NetSecColors.BORDER_LIGHT};
                border-radius: 12px;
                margin: 8px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def setupLayout(self, title):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {NetSecColors.TEXT_PRIMARY};
                    font-size: 18px;
                    font-weight: 600;
                    font-family: "Arial", sans-serif;
                    margin-bottom: 8px;
                }}
            """)
            layout.addWidget(title_label)
        
        self.setLayout(layout)

class NetSecSimDashboard(QMainWindow):
    """Main dashboard application"""
    
    def __init__(self):
        super().__init__()
        self.container_states = {
            "AS100": "online", "AS200": "online", "AS300": "online", 
            "AS400": "online", "AS500": "online"
        }
        self.setupUI()
        self.setupTimers()

    def setupUI(self):
        self.setWindowTitle("NetSecSim Professional Dashboard v2.0")
        self.setGeometry(100, 100, 1400, 900)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icons/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"[WARNING] Icon not found: {icon_path}") 

        # Modern window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {NetSecColors.BACKGROUND};
                font-family: "Arial", sans-serif;
            }}
        """)
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Left panel (controls)
        left_panel = self.createLeftPanel()
        left_panel.setFixedWidth(300)
        
        # Right panel (topology)
        right_panel = self.createRightPanel()
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)  # Stretch factor
        
        central_widget.setLayout(main_layout)
        
        # Status bar with modern styling
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {NetSecColors.PANEL_BG};
                border-top: 1px solid {NetSecColors.BORDER_LIGHT};
                color: {NetSecColors.TEXT_SECONDARY};
                font-size: 12px;
            }}
        """)
        self.updateStatusBar()
    
    def createLeftPanel(self):
        """Create the left control panel"""
        panel = ModernPanel()
        layout = panel.layout()
        
        # Container Status Section
        status_section = QWidget()
        status_layout = QVBoxLayout()
        
        # Section title
        title = QLabel("🛢️ Container Status")
        title.setStyleSheet(f"""
            QLabel {{
                color: {NetSecColors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 12px;
            }}
        """)
        status_layout.addWidget(title)
        
        # Container status grid
        self.container_widgets = {}
        grid = QGridLayout()
        containers = ["AS100", "AS200", "AS300", "AS400", "AS500"]
        
        for i, container in enumerate(containers):
            row, col = divmod(i, 2)
            
            container_widget = QWidget()
            container_layout = QHBoxLayout()
            container_layout.setContentsMargins(12, 8, 12, 8)
            
            # Status indicator
            status_indicator = StatusIndicator("online")
            
            # Container label
            label = QLabel(container)
            label.setStyleSheet(f"color: {NetSecColors.TEXT_PRIMARY}; font-weight: 500;")
            
            # Status text
            status_text = QLabel("ONLINE")
            status_text.setStyleSheet(f"color: {NetSecColors.SUCCESS_GREEN}; font-size: 11px; font-weight: 600;")
            
            container_layout.addWidget(status_indicator)
            container_layout.addWidget(label)
            container_layout.addStretch()
            container_layout.addWidget(status_text)
            
            container_widget.setLayout(container_layout)
            container_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {NetSecColors.BACKGROUND};
                    border: 1px solid {NetSecColors.BORDER_LIGHT};
                    border-radius: 8px;
                    margin: 2px;
                }}
            """)
            
            self.container_widgets[container] = {
                'widget': container_widget,
                'indicator': status_indicator,
                'status_label': status_text
            }
            
            grid.addWidget(container_widget, row, col)
        
        status_layout.addLayout(grid)
        status_section.setLayout(status_layout)
        layout.addWidget(status_section)
        
        # Attack Simulation Section
        attack_section = QWidget()
        attack_layout = QVBoxLayout()
        
        attack_title = QLabel("⚔️ Attack Simulation")
        attack_title.setStyleSheet(f"""
            QLabel {{
                color: {NetSecColors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                margin: 16px 0 12px 0;
            }}
        """)
        attack_layout.addWidget(attack_title)
        
        # Attack buttons
        self.prefix_hijack_btn = ModernButton("🚀 Launch Prefix Hijack", NetSecColors.DANGER_RED)
        self.route_poisoning_btn = ModernButton("🎯 Launch Route Poisoning", NetSecColors.WARNING_ORANGE)
        self.cleanup_btn = ModernButton("🧹 Clean Up Attacks", NetSecColors.SUCCESS_GREEN)
        
        self.prefix_hijack_btn.clicked.connect(self.launchPrefixHijack)
        self.route_poisoning_btn.clicked.connect(self.launchRoutePoisoning)
        self.cleanup_btn.clicked.connect(self.cleanupAttacks)
        
        attack_layout.addWidget(self.prefix_hijack_btn)
        attack_layout.addWidget(self.route_poisoning_btn)
        attack_layout.addWidget(self.cleanup_btn)
        
        attack_section.setLayout(attack_layout)
        layout.addWidget(attack_section)
        
        # Attack Log Section
        log_section = QWidget()
        log_layout = QVBoxLayout()
        
        log_title = QLabel("📋 Attack Log")
        log_title.setStyleSheet(f"""
            QLabel {{
                color: {NetSecColors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: 600;
                margin: 16px 0 12px 0;
            }}
        """)
        log_layout.addWidget(log_title)
        
        self.attack_log = QTextEdit()
        self.attack_log.setMaximumHeight(200)
        self.attack_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {NetSecColors.TEXT_PRIMARY};
                color: {NetSecColors.SUCCESS_GREEN};
                border: 1px solid {NetSecColors.BORDER_LIGHT};
                border-radius: 8px;
                padding: 12px;
                font-family: "Consolas", "Monaco", monospace;
                font-size: 11px;
                line-height: 1.4;
            }}
        """)
        
        # Add initial log entries
        initial_logs = [
            "[12:34:56] ✓ Cleaning up attacks...",
            "[12:34:56] ✓ Cleanup complete",
            "[12:35:12] ⚠ Prefix hijack launched",
            "[12:35:13] ✓ Cleaning up attacks...",
            "[12:35:14] ✓ Cleanup complete"
        ]
        
        for log in initial_logs:
            self.attack_log.append(log)
        
        log_layout.addWidget(self.attack_log)
        log_section.setLayout(log_layout)
        layout.addWidget(log_section)
        
        layout.addStretch()  # Push everything to top
        
        return panel
    
    def createRightPanel(self):
        """Create the right topology panel"""
        panel = ModernPanel("🌐 NetSecSim Network Topology")
        layout = panel.layout()
        
        # Add topology widget
        self.topology_widget = NetworkTopologyWidget()
        layout.addWidget(self.topology_widget)
        
        return panel
    
    def setupTimers(self):
        """Setup update timers"""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.updateStatusBar)
        self.status_timer.start(1000)  # Update every second
    
    def updateStatusBar(self):
        """Update status bar with current stats"""
        containers_online = sum(1 for state in self.container_states.values() if state == "online")
        routes_total = 30  # Mock data
        attacks_detected = sum(1 for state in self.container_states.values() if state == "attack")
        
        current_time = datetime.now().strftime("%H:%M:%S")
        status_text = f"🛢️ Containers: {containers_online}/5 | 🛣️ Routes: {routes_total} | ⚠️ Attacks: {attacks_detected} | 🕒 {current_time}"
        
        self.statusBar().showMessage(status_text)
    
    def launchPrefixHijack(self):
        """Launch prefix hijack attack simulation"""
        self.logAction("⚠ Prefix hijack launched")
        
        # Update container states
        self.container_states["AS100"] = "attack"
        self.container_states["AS400"] = "attack"
        self.updateContainerDisplay()
        
        # Update topology
        self.topology_widget.simulateAttack("prefix_hijack")
        
        self.updateStatusBar()
    
    def launchRoutePoisoning(self):
        """Launch route poisoning attack simulation"""
        self.logAction("⚠ Route poisoning launched")
        
        # Update container states
        self.container_states["AS200"] = "attack"
        self.updateContainerDisplay()
        
        self.updateStatusBar()
    
    def cleanupAttacks(self):
        """Clean up all active attacks"""
        self.logAction("✓ Cleaning up attacks...")
        
        # Reset all container states
        for container in self.container_states:
            self.container_states[container] = "online"
        
        self.updateContainerDisplay()
        self.topology_widget.clearAttacks()
        
        self.logAction("✓ Cleanup complete")
        self.updateStatusBar()
    
    def updateContainerDisplay(self):
        """Update container status indicators"""
        for container, state in self.container_states.items():
            if container in self.container_widgets:
                widgets = self.container_widgets[container]
                widgets['indicator'].setStatus(state)
                
                if state == "attack":
                    widgets['status_label'].setText("ATTACK")
                    widgets['status_label'].setStyleSheet(f"color: {NetSecColors.DANGER_RED}; font-size: 11px; font-weight: 600;")
                else:
                    widgets['status_label'].setText("ONLINE")
                    widgets['status_label'].setStyleSheet(f"color: {NetSecColors.SUCCESS_GREEN}; font-size: 11px; font-weight: 600;")
    
    def logAction(self, message):
        """Add message to attack log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.attack_log.append(log_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.attack_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("NetSecSim Dashboard")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("NetSecSim")
    
    # Create and show dashboard
    dashboard = NetSecSimDashboard()
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
