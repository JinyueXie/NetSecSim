#!/bin/bash
# NetSecSim Icon and Desktop Integration

cd ~/NetSecSim
mkdir -p assets/icons

# Create high-quality SVG icon
cat > assets/icons/netsec-icon.svg << 'ICON_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="64" cy="64" r="58" fill="url(#bgGrad)" stroke="#2c3e50" stroke-width="4"/>
  
  <!-- Network nodes -->
  <circle cx="35" cy="35" r="8" fill="#ecf0f1" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="64" cy="64" r="10" fill="#3498db" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="93" cy="35" r="8" fill="#27ae60" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="35" cy="93" r="8" fill="#f39c12" stroke="#2c3e50" stroke-width="2"/>
  <circle cx="93" cy="93" r="8" fill="#e74c3c" stroke="#2c3e50" stroke-width="2"/>
  
  <!-- Network connections -->
  <g stroke="#ecf0f1" stroke-width="3" opacity="0.8">
    <line x1="35" y1="35" x2="64" y2="64"/>
    <line x1="93" y1="35" x2="64" y2="64"/>
    <line x1="35" y1="93" x2="64" y2="64"/>
    <line x1="93" y1="93" x2="64" y2="64"/>
  </g>
  
  <!-- Title -->
  <text x="64" y="118" text-anchor="middle" fill="#2c3e50" font-size="12" font-weight="bold">NetSecSim</text>
</svg>
ICON_EOF

# Convert to PNG if possible
if command -v convert &> /dev/null; then
    convert assets/icons/netsec-icon.svg -resize 64x64 assets/icons/netsec.png
    echo "✅ Icon created successfully"
else
    cp assets/icons/netsec-icon.svg assets/icons/netsec.png
    echo "⚠️ Using SVG as PNG (install imagemagick for better results)"
fi

# Create enhanced launcher
cat > launch-netsec-v2.sh << 'LAUNCHER_EOF'
#!/bin/bash
# NetSecSim v2.0 Launcher

cd ~/NetSecSim

echo "🚀 NetSecSim Professional Dashboard v2.0"
echo "========================================"

# Create virtual environment if needed
if [[ ! -d "venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade PyQt6 PyQt6-Charts matplotlib networkx numpy

# Set Qt environment
export QT_QPA_PLATFORM=xcb
export QT_AUTO_SCREEN_SCALE_FACTOR=1

# Check containers
echo "🐳 Checking containers..."
if ! docker ps | grep -q "as[0-9]"; then
    echo "⚠️ No containers running. Dashboard will show offline status."
fi

# Launch enhanced dashboard
echo "🎮 Launching enhanced dashboard..."
python3 dashboard/netsec_dashboard_v2.py "$@"
LAUNCHER_EOF

chmod +x launch-netsec-v2.sh

# Create desktop entry
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/netsec-dashboard-v2.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=NetSecSim Dashboard v2.0
GenericName=Network Security Simulator
Comment=Professional BGP attack simulation and monitoring platform
Exec=/home/penny/NetSecSim/launch-netsec-v2.sh
Icon=/home/penny/NetSecSim/assets/icons/netsec.png
Terminal=false
Categories=Development;Network;Security;Education;
Keywords=network;security;bgp;simulation;monitoring;attack;
StartupNotify=true
DESKTOP_EOF

chmod +x ~/.local/share/applications/netsec-dashboard-v2.desktop

# Create desktop shortcut
if [[ -d "$HOME/Desktop" ]]; then
   cp ~/.local/share/applications/netsec-dashboard-v2.desktop "$HOME/Desktop/"
   chmod +x "$HOME/Desktop/netsec-dashboard-v2.desktop"
   echo "🖥️ Desktop shortcut created"
fi

# Create CLI wrapper
cat > netsec-gui-v2 << 'CLI_EOF'
#!/bin/bash
# NetSecSim v2.0 GUI Control

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "${1:-start}" in
   start)
       if pgrep -f "netsec_dashboard_v2" > /dev/null; then
           echo "✅ NetSecSim v2.0 is already running"
       else
           echo "🚀 Starting NetSecSim v2.0..."
           cd "$SCRIPT_DIR"
           nohup ./launch-netsec-v2.sh > /dev/null 2>&1 &
           sleep 2
           echo "✅ Dashboard started"
       fi
       ;;
   stop)
       echo "🛑 Stopping NetSecSim v2.0..."
       pkill -f "netsec_dashboard_v2"
       echo "✅ Dashboard stopped"
       ;;
   status)
       if pgrep -f "netsec_dashboard_v2" > /dev/null; then
           echo "✅ NetSecSim v2.0 is running"
       else
           echo "❌ NetSecSim v2.0 is not running"
       fi
       ;;
   *)
       echo "Usage: $0 {start|stop|status}"
       ;;
esac
CLI_EOF

chmod +x netsec-gui-v2

echo "✅ NetSecSim v2.0 Setup Complete!"
echo
echo "🎮 Launch Options:"
echo "   • Double-click desktop icon"
echo "   • Run: ./netsec-gui-v2 start"
echo "   • Run: ./launch-netsec-v2.sh"
echo
echo "🧪 Test: python3 dashboard/netsec_dashboard_v2.py"
