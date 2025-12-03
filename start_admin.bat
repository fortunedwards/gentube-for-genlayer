@echo off
echo Starting GenTube Admin Dashboard...
cd admin_dashboard
pip install -r requirements.txt
python run.py
pause