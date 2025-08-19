@echo off
setlocal EnableDelayedExpansion

:: ==== [1] Prüfung: Ist LM Studio installiert? ====
if not exist "C:\Program Files\LM Studio\LM Studio.exe" (
  echo [Fehler] LM Studio wurde nicht gefunden. Bitte installieren Sie es unter:
  echo "C:\Program Files\LM Studio\"
  pause
  exit /b
)

:: ==== [2] GPU-Erkennung: RTX und Tesla ====
set RTX_GPU=0
set TESLA_GPU=0
set CUDA_VISIBLE_DEVICES=

for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Where-Object {$_.Name -like '*NVIDIA*'} | ForEach-Object { $_.Name }"`) do (
  echo [GPU erkannt] %%i
  echo %%i | findstr /i "RTX" >nul && set RTX_GPU=1
  echo %%i | findstr /i "Tesla" >nul && set TESLA_GPU=1
)

if %RTX_GPU%==1 (
  echo [Info] NVIDIA RTX erkannt.
  set CUDA_VISIBLE_DEVICES=0
)

if %TESLA_GPU%==1 (
  echo [Info] NVIDIA Tesla erkannt.
  if not defined CUDA_VISIBLE_DEVICES (
    set CUDA_VISIBLE_DEVICES=0
  ) else (
    set CUDA_VISIBLE_DEVICES=!CUDA_VISIBLE_DEVICES!,1
  )
)

:: ==== [3] CPU-Kerne ====
set CPU_CORES=%NUMBER_OF_PROCESSORS%
echo [Info] CPU-Kerne: %CPU_CORES%

:: ==== [4] RAM ermitteln (in MB) ====
for /f %%i in ('powershell -NoProfile -Command "(Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize / 1024"') do set RAM_MB=%%i

:: ==== [5] VRAM ermitteln (in MB, alle GPUs summiert) ====
for /f %%i in ('powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Where-Object {$_.AdapterRAM -gt 0} | Measure-Object -Property AdapterRAM -Sum | ForEach-Object { [math]::Round($_.Sum / 1MB) }"') do set VRAM_MB=%%i

:: ==== [6] Gesamtspeicher berechnen ====
set /a TOTAL_MEMORY_MB=%RAM_MB% + %VRAM_MB%
set /a TOTAL_MEMORY_GB=%TOTAL_MEMORY_MB% / 1024

echo [Info] RAM:  %RAM_MB% MB
echo [Info] VRAM: %VRAM_MB% MB
echo [Info] Gesamt verfügbarer Speicher: %TOTAL_MEMORY_MB% MB (%TOTAL_MEMORY_GB% GB)

:: ==== [7] LM Studio starten ====
echo.
echo [Starte LM Studio...]
"C:\Program Files\LM Studio\LM Studio.exe" ^
  --cuda-device %CUDA_VISIBLE_DEVICES% ^
  --cpu-cores %CPU_CORES% ^
  --memory-limit %TOTAL_MEMORY_MB%

:: ==== [8] Tesla-Tool starten (wenn Tesla erkannt) ====
if %TESLA_GPU%==1 (
  if exist "C:\Program Files\Tesla-Tool\tesla-tool.exe" (
    echo.
    echo [Starte Tesla-Tool...]
    "C:\Program Files\Tesla-Tool\tesla-tool.exe"
  ) else (
    echo [Hinweis] Tesla-Tool nicht gefunden unter:
    echo "C:\Program Files\Tesla-Tool\tesla-tool.exe"
  )
)

:: ==== [9] Ende ====
echo.
echo [Fertig] Vorgang abgeschlossen.
pause
endlocal
