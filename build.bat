@echo off
echo ========================================
echo   Building LookAlive executable...
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Build the executable
pyinstaller --onefile --windowed --name LookAlive ^
    --add-data "core;core" ^
    --add-data "utils;utils" ^
    --hidden-import=pystray._win32 ^
    --hidden-import=PIL._tkinter_finder ^
    main.py

echo.
echo ========================================
echo   Build complete!
echo   Find LookAlive.exe in the 'dist' folder
echo ========================================
pause
