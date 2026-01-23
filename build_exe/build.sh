#!/bin/bash

# Imager Executable Build Script
# This script builds a standalone .exe file for the Imager application

set -e  # Exit on error

echo "========================================="
echo "   Imager Executable Builder"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo -e "${BLUE}[1/6]${NC} Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if (( $(echo "$python_version < 3.10" | bc -l) )); then
    echo -e "${RED}Error: Python 3.10+ is required. You have Python $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"
echo ""

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d "venv_build" ]; then
    echo -e "${BLUE}[2/6]${NC} Creating virtual environment..."
    python3 -m venv venv_build
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${BLUE}[2/6]${NC} Virtual environment already exists"
    echo -e "${GREEN}✓ Using existing virtual environment${NC}"
fi
echo ""

# Step 3: Activate virtual environment and install dependencies
echo -e "${BLUE}[3/6]${NC} Installing dependencies..."
source venv_build/bin/activate

# Install main dependencies
pip install -q --upgrade pip
pip install -q -r ../requirements.txt
pip install -q -r requirements_build.txt

echo -e "${GREEN}✓ All dependencies installed${NC}"
echo ""

# Step 4: Clean previous builds
echo -e "${BLUE}[4/6]${NC} Cleaning previous builds..."
rm -rf dist build *.spec.bak
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Step 5: Build the executable
echo -e "${BLUE}[5/6]${NC} Building executable with PyInstaller..."
echo "This may take a few minutes..."
pyinstaller --clean imager.spec

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful!${NC}"
else
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
echo ""

# Step 6: Create distribution package
echo -e "${BLUE}[6/6]${NC} Creating distribution package..."

# Create distribution folder
DIST_FOLDER="Imager_Portable"
rm -rf "$DIST_FOLDER"
mkdir -p "$DIST_FOLDER"

# Copy executable
cp dist/Imager "$DIST_FOLDER/"

# Create README for end users
cat > "$DIST_FOLDER/README.txt" << 'EOF'
========================================
   Imager - Portable GUI Version
========================================

QUICK START:
------------
1. Double-click the Imager executable
2. Enter your search terms (comma-separated)
3. Set number of images to download
4. Specify save folder (default: downloaded_images)
5. Click "Start Scraping"

That's it! No configuration files needed!

REQUIREMENTS:
-------------
- Google Chrome browser must be installed
- Internet connection

FEATURES:
---------
- Easy-to-use graphical interface
- Real-time activity log
- Progress indicator
- No setup or configuration files needed
- Automatic Chrome driver management

USAGE TIPS:
-----------
- Search Terms: Use comma to separate multiple terms
  Example: "cyberpunk city, nature landscape, sunset beach"
  
- Number of Images: Choose between 1-100 images per term

- Save Folder: Images will be saved in separate folders
  for each search term inside your specified folder

- Activity Log: Watch real-time progress and any issues

TROUBLESHOOTING:
----------------
- If Chrome doesn't open: Make sure Google Chrome is installed
- If downloads fail: Check your internet connection
- For errors: Check the activity log in the application

For more help, visit:
https://github.com/santoshvandari/Imager
EOF

# Create a simple batch file for Windows users
cat > "$DIST_FOLDER/run_imager.bat" << 'EOF'
@echo off
start Imager.exe
EOF

echo -e "${GREEN}✓ Distribution package created${NC}"
echo ""

# Summary
echo "========================================="
echo -e "${GREEN}   BUILD COMPLETE!${NC}"
echo "========================================="
echo ""
echo "Your GUI executable is ready in: ./$DIST_FOLDER/"
echo ""
echo "What's included:"
echo "  ✓ Imager - GUI executable with:"
echo "    - Input fields for all settings"
echo "    - Real-time activity log"
echo "    - No .env or config files needed!"
echo "    - User-friendly interface"
echo ""
echo "Next steps:"
echo "1. Copy the entire '$DIST_FOLDER' folder to share"
echo "2. Recipients just double-click Imager and use it!"
echo "3. All settings are entered via the GUI"
echo ""
echo "========================================="

deactivate
