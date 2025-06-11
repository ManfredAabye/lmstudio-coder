@echo off
title KI-Code-Updater - Installer
echo ================================================
echo     KI-Code-Updater - Abhaengigkeiten Setup
echo ================================================

REM Python-Installation prüfen
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Fehler: Python ist nicht installiert oder nicht im PATH.
    echo Bitte installiere Python 3.8 oder neuer.
    pause
    exit /b 1
)

REM Pakete installieren
echo Installiere benoetigte Python-Pakete ...
pip install --upgrade pip
pip install requests

REM Hinweis zu Tkinter (bereits in stdlib)
echo.
echo Hinweis: Tkinter ist normalerweise in Python enthalten.
echo Falls es fehlt, installiere das Paket "python3-tk" manuell.

echo.
echo Installation abgeschlossen.
pause
