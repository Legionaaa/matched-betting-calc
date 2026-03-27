@echo off
setlocal

set "PY_CMD="

where py.exe >nul 2>nul
if not errorlevel 1 set "PY_CMD=py"

if not defined PY_CMD (
    where py >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py"
)

if not defined PY_CMD (
    where python.exe >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python.exe"
)

if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    if exist "%LocalAppData%\Microsoft\WindowsApps\python.exe" (
        set "PY_CMD=%LocalAppData%\Microsoft\WindowsApps\python.exe"
    )
)

if not defined PY_CMD (
    if exist "%LocalAppData%\Microsoft\WindowsApps\python3.exe" (
        set "PY_CMD=%LocalAppData%\Microsoft\WindowsApps\python3.exe"
    )
)

if not defined PY_CMD (
    echo Python was not found on PATH.
    echo Install Python for Windows from https://www.python.org/downloads/windows/
    echo During install, enable "Add python.exe to PATH".
    exit /b 1
)

"%PY_CMD%" -m pip install --upgrade -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

"%PY_CMD%" scripts\create_logo_icon.py
if errorlevel 1 exit /b 1

"%PY_CMD%" scripts\package_windows.py
if errorlevel 1 exit /b 1

echo.
if exist dist\latest_build.txt (
    echo Built:
    type dist\latest_build.txt
) else (
    echo Build completed.
)
