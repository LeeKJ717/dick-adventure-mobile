@echo off
chcp 65001 >nul 2>&1
echo ======================================== DEQJAM Build ========================================
echo.

echo [1/4] Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and add it to your system PATH.
    pause
    exit /b 1
)

echo.
echo [2/4] Installing required packages...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip!
    pause
    exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install required packages!
    echo Please check requirements.txt and your internet connection.
    pause
    exit /b 1
)

echo.
echo [3/4] Cleaning old build directory...
echo Please close DEQJAM.exe if it is running...
timeout /t 2 /nobreak >nul
if exist build\exe.win-amd64-3.12 (
    echo Attempting to remove old build directory...
    rmdir /s /q build\exe.win-amd64-3.12 2>nul
    if exist build\exe.win-amd64-3.12 (
        echo Warning: Could not remove build\exe.win-amd64-3.12 directory.
        echo Please manually delete it or close any running instances.
        echo Trying to continue anyway...
    ) else (
        echo Old build directory removed.
    )
)

echo.
echo [4/5] Building executable...
echo This may take a few minutes...
python setup_cxfreeze.py build
if errorlevel 1 (
    echo.
    echo ======================================== Build Failed! ========================================
    echo An error occurred during the build process.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo - Make sure cx_Freeze is installed: pip install cx_Freeze
    echo - Make sure all dependencies are installed: pip install -r requirements.txt
    echo - Check that main.py exists and is valid
    pause
    exit /b 1
)

echo.
echo [5/5] Verifying build output...
if exist "build\exe.win-amd64-3.12\DEQJAM.exe" (
    echo.
    echo ======================================== Build Complete! ========================================
    echo Executable location: build\exe.win-amd64-3.12\DEQJAM.exe
    echo.
    echo You can now run the game by executing DEQJAM.exe
) else (
    echo.
    echo ======================================== Build Warning! ========================================
    echo Build completed but executable not found at expected location.
    echo Please check the build directory for output files.
    dir /b build
)

echo.
pause
