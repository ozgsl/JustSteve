@echo off
echo Gerekli kutuphaneler kontrol ediliyor...
.\venv\Scripts\python.exe -m pip install pygame-ce
.\venv\Scripts\python.exe main.py
pause
