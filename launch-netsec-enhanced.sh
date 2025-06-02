#!/bin/bash
# NetSecSim Enhanced Dashboard Launcher

echo "🚀 Starting NetSecSim Enhanced Dashboard..."
echo "=========================================="

cd ~/NetSecSim
source venv/bin/activate

echo "✅ Environment activated"
echo "🎮 Launching professional dashboard..."

python3 dashboard/netsec_dashboard_enhanced.py
