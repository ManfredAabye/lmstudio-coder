@echo off
chcp 65001 >nul
title KI-Code-Updater
color 0A

:: Python-Check
python --version >nul 2>&1
if errorlevel 1 (
    echo Fehler: Python nicht gefunden.
    echo Bitte installieren Sie Python von https://www.python.org/downloads/
    pause
    exit /b
)

:: Abhängigkeitscheck mit sauberer Ausgabe
echo Überprüfe Python-Abhängigkeiten...
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installiere requests...
    pip install --user requests
) else (
    echo Alle Abhängigkeiten bereits installiert.
)

:: Hauptprogramm starten
echo Starte KI-Code-Updater...
python main.py
pause
