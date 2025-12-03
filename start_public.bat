@echo off
echo Starting GenTube Public Archive...
cd public_archive
python -m http.server 8000
pause