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
