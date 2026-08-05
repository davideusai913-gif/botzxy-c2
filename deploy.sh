#!/bin/bash
# BotZXY - Deployment Script

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║              BotZXY - Deployment Script                  ║"
echo "║              Command & Control System v2.0               ║"
echo "║                                                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[-] Python3 not found. Install it first."
    exit 1
fi

# Create virtual environment
echo "[+] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate# Install dependencies
echo "[+] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "[+] Creating directories..."
mkdir -p database
mkdir -p logs
mkdir -p static/css
mkdir -p static/js
mkdir -p payloads
mkdir -p utils
mkdir -p templates

# Initialize database
echo "[+] Initializing database..."
python3 -c "from app import init_db; init_db()"

# Create admin user
echo "[+] Creating admin user..."
python3 -c "from app import setup_admin_user; setup_admin_user()"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║              ✅ BotZXY Deployment Complete                ║"
echo "║                                                          ║"
echo "║  Run:        python app.py                               ║"
echo "║  Or:         gunicorn -k eventlet app:app               ║"
echo "║                                                          ║"
echo "║  Dashboard:  http://localhost:5000                      ║"
echo "║  Login:      admin / BotZXY2026!                        ║"
echo "║                                                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"