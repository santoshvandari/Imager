@echo off
REM Imager Executable Build Script for Windows
REM This script builds a standalone .exe file for the Imager application

echo =========================================
echo    Imager Executable Builder - Windows
echo =========================================
echo.

REM Step 1: Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

REM Step 2: Create virtual environment
if not exist "venv_build" (
    echo [2/6] Creating virtual environment...
    python -m venv venv_build
    echo Virtual environment created
) else (
    echo [2/6] Virtual environment already exists
    echo Using existing virtual environment
)
echo.

REM Step 3: Activate virtual environment and install dependencies
echo [3/6] Installing dependencies...
call venv_build\Scripts\activate.bat

python -m pip install --quiet --upgrade pip
pip install --quiet -r ..\requirements.txt
pip install --quiet -r requirements_build.txt

echo All dependencies installed
echo.

REM Step 4: Clean previous builds
echo [4/6] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec.bak" del /q *.spec.bak
echo Cleanup complete
echo.

REM Step 5: Build the executable
echo [5/6] Building executable with PyInstaller...
echo This may take a few minutes...
pyinstaller --clean imager.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
echo Build successful!
echo.

REM Step 6: Create distribution package
echo [6/6] Creating distribution package...

REM Create distribution folder
set DIST_FOLDER=Imager_Portable
if exist "%DIST_FOLDER%" rmdir /s /q "%DIST_FOLDER%"
mkdir "%DIST_FOLDER%"

REM Copy executable
copy dist\Imager.exe "%DIST_FOLDER%\" >nul

REM Create README for end users
(
echo ========================================
echo    Imager - Portable GUI Version
echo ========================================
echo.
echo QUICK START:
echo ------------
echo 1. Double-click Imager.exe
echo 2. Enter your search terms ^(comma-separated^)
echo 3. Set number of images to download
echo 4. Specify save folder ^(default: downloaded_images^)
echo 5. Click "Start Scraping"
echo.
echo That's it! No configuration files needed!
echo.
echo REQUIREMENTS:
echo -------------
echo - Google Chrome browser must be installed
echo - Internet connection
echo.
echo FEATURES:
echo ---------
echo - Easy-to-use graphical interface
echo - Real-time activity log
echo - Progress indicator
echo - No setup or configuration files needed
echo - Automatic Chrome driver management
echo.
echo USAGE TIPS:
echo -----------
echo - Search Terms: Use comma to separate multiple terms
echo   Example: "cyberpunk city, nature landscape, sunset beach"
echo.
echo - Number of Images: Choose between 1-100 images per term
echo.
echo - Save Folder: Images will be saved in separate folders
echo   for each search term inside your specified folder
echo.
echo - Activity Log: Watch real-time progress and any issues
echo.
echo TROUBLESHOOTING:
echo ----------------
echo - If Chrome doesn't open: Make sure Google Chrome is installed
echo - If downloads fail: Check your internet connection
echo - For errors: Check the activity log in the application
echo.
echo For more help, visit:
echo https://github.com/santoshvandari/Imager
) > "%DIST_FOLDER%\README.txt"

REM Create batch file for easier running
(
echo @echo off
echo start Imager.exe
) > "%DIST_FOLDER%\run_imager.bat"

echo Distribution package created
echo.

REM Summary
echo =========================================
echo    BUILD COMPLETE!
echo =========================================
echo.
echo Your GUI executable is ready in: .\%DIST_FOLDER%\
echo.
echo What's included:
echo   - Imager.exe - GUI executable with:
echo     * Input fields for all settings
echo     * Real-time activity log
echo     * No .env or config files needed!
echo     * User-friendly interface
echo.
echo Next steps:
echo 1. Copy the entire '%DIST_FOLDER%' folder to share
echo 2. Recipients just double-click Imager.exe and use it!
echo 3. All settings are entered via the GUI
echo.
echo =========================================
echo.

call venv_build\Scripts\deactivate.bat

pause
