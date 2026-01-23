# Building Imager GUI Executable

This folder contains everything needed to build a **standalone GUI executable** for the Imager application.

## ✨ What's New - GUI Version!

This version features a **graphical user interface** with:
- ✅ **Input fields** for search terms, number of images, and save folder
- ✅ **Real-time activity log** showing progress and status
- ✅ **No .env file needed** - all settings via the GUI
- ✅ **User-friendly** - just double-click and use!

## 📋 Prerequisites

- **Python 3.10+** installed on your system
- **Google Chrome** browser (required by Selenium)
- **Linux/macOS** for building (Windows users can use WSL)

## 🚀 Quick Build

### Linux/macOS:
```bash
cd /home/wabisabi/Desktop/Imager/build_exe
./build.sh
```

### Windows:
```cmd
cd build_exe
build.bat
```

The build takes **5-10 minutes** on first run (downloads dependencies).

## 📦 Distribution Package

After building, you'll get:

```
Imager_Portable/
├── Imager.exe       # The GUI executable
├── README.txt       # User instructions
└── run_imager.bat   # Optional Windows launcher
```

**Share the entire `Imager_Portable` folder** - it's completely standalone!

## 👥 For End Users (How to Use)

### Setup (One-time):
1. Extract/copy the `Imager_Portable` folder
2. Ensure **Google Chrome** is installed
3. Double-click **Imager.exe**

### Usage:
1. **Search Terms**: Enter comma-separated terms (e.g., "cyberpunk city, sunset beach")
2. **Images per Term**: Set how many images to download (1-100)
3. **Save Folder**: Specify where to save (default: downloaded_images)
4. **Click "Start Scraping"**: Watch the real-time log!

**No configuration files needed!** Everything is in the GUI.

## 🎨 GUI Features

### Input Fields:
- **Search Terms**: Comma-separated queries
- **Number of Images**: 1-100 per term
- **Save Folder**: Custom location for downloads

### Real-time Feedback:
- **Activity Log**: Color-coded messages (blue=info, green=success, red=error)
- **Progress Bar**: Visual indication of activity
- **Status Bar**: Current operation status

### Controls:
- **Start/Stop Button**: Begin scraping or cancel mid-process
- **Scrollable Log**: Full history of all operations

## 🔧 Technical Details

### Files Included:

**`main_gui.py`** - GUI application using tkinter
- Graphical interface with input validation
- Threading for non-blocking scraping
- Real-time log display
- No external config files needed

**`imager.spec`** - PyInstaller configuration
- Bundles all dependencies (Selenium, tkinter, etc.)
- Includes user_agent.json data file
- Creates single executable
- Console window disabled (GUI only)

**`build.sh` / `build.bat`** - Automated build scripts
- Creates virtual environment
- Installs dependencies
- Builds with PyInstaller
- Creates distribution package

**`requirements_build.txt`** - Build dependencies
- PyInstaller 6.11.1

## 🐛 Troubleshooting

### Build Issues:

**"Python not found"**
```bash
# Linux/Mac
which python3
# Install if needed: sudo apt install python3

# Windows
python --version
# Install from python.org
```

**"Build fails"**
```bash
# Clean and rebuild
rm -rf venv_build build dist Imager_Portable
./build.sh
```

### Runtime Issues:

**Executable crashes immediately**
- Run from terminal to see errors (helps debug)
- Check if Chrome is installed
- Ensure internet connection

**"Chrome driver not found"**
- Application auto-downloads Chrome driver
- Ensure internet connection is active
- Check firewall/antivirus settings

**GUI doesn't appear**
- On Linux, ensure display is available
- Check that no console window is blocking
- Try running from terminal to see messages

## 📊 Build Output Details

After successful build:

```
build_exe/
├── main_gui.py              # GUI source code
├── imager.spec              # PyInstaller config
├── build.sh / build.bat     # Build scripts
├── requirements_build.txt   # Dependencies
│
├── venv_build/             # Virtual environment (kept for faster rebuilds)
├── build/                  # Temporary PyInstaller files
├── dist/                   # Raw executable output
│   └── Imager              # Raw executable
│
└── Imager_Portable/        # ⭐ FINAL DISTRIBUTION ⭐
    ├── Imager.exe          # User-ready executable
    ├── README.txt          # User instructions
    └── run_imager.bat      # Windows helper
```

## 🎯 Sharing Your Executable

### Option 1: Zip and Upload
```bash
cd build_exe
zip -r Imager_Portable.zip Imager_Portable/
# Upload to Google Drive, Dropbox, etc.
```

### Option 2: GitHub Release
1. Create a new release on GitHub
2. Upload `Imager_Portable.zip` as an asset
3. Include installation instructions in release notes

### Option 3: Direct Share
Copy the `Imager_Portable` folder to:
- USB drive
- Network share
- Cloud storage

## ⚙️ Advanced Customization

### Add an Application Icon

1. Get a `.ico` file (256x256px recommended)
2. Place in `build_exe/` folder
3. Edit `imager.spec`:
   ```python
   icon='my_icon.ico',
   ```
4. Rebuild

### Change Window Size

Edit `main_gui.py`:
```python
self.root.geometry("800x700")  # Change from 700x600
```

### Modify Default Values

Edit `main_gui.py`:
```python
self.search_entry.insert(0, "your default search")
self.num_images_var = tk.StringVar(value="10")  # Change from 5
self.save_folder_var = tk.StringVar(value="my_images")
```

### Enable Debug Console (for testing)

Edit `imager.spec`:
```python
console=True,  # Change from False
```

This shows a console window with debug messages.

## 📏 Executable Size

**Expected size: 50-100 MB**

This is normal! The executable includes:
- Python interpreter
- Selenium + WebDriver
- Chrome driver manager
- Pillow (image processing)
- tkinter GUI library
- All other dependencies

To reduce size slightly, use UPX compression (already enabled).

## 🔄 Rebuild Process

### Quick Rebuild (after code changes):
```bash
cd build_exe
./build.sh
# Uses existing venv_build (faster: 2-5 min)
```

### Clean Rebuild (dependency changes):
```bash
cd build_exe
rm -rf venv_build build dist Imager_Portable
./build.sh
# Full rebuild (5-10 min)
```

## 🌐 Platform Notes

### Building for Different Platforms:

**Current platform creates executables for current OS only.**

- Build on **Linux** → Linux binary
- Build on **Windows** → Windows .exe
- Build on **macOS** → macOS app

To support multiple platforms, build on each separately.

### Linux Specific:
```bash
# Make executable
chmod +x Imager
./Imager
```

### Windows Specific:
- Just double-click `Imager.exe`
- Use `run_imager.bat` for quick launch
- May trigger antivirus (false positive - PyInstaller is safe)

### macOS Specific:
```bash
# If blocked by Gatekeeper
xattr -cr Imager_Portable/
# Then allow in System Preferences > Security
```

## ✅ Pre-Distribution Checklist

Before sharing your executable:

- [ ] Build completes without errors
- [ ] Test executable on clean system (no Python)
- [ ] Verify GUI opens and displays correctly
- [ ] Test with sample search terms
- [ ] Check images download successfully
- [ ] Review activity log for errors
- [ ] Test Start/Stop functionality
- [ ] Verify Chrome auto-downloads driver
- [ ] Include README.txt with instructions
- [ ] Test on target operating system

## 🆘 Getting Help

**Build problems?** Check error messages carefully:
- Missing Python? Install Python 3.10+
- Permission errors? Use `chmod +x` or run as admin
- Import errors? Clean build and try again

**Runtime problems?** Run from terminal to see logs:
```bash
cd Imager_Portable
./Imager  # See error messages
```

**Still stuck?** Create an issue:
https://github.com/santoshvandari/Imager/issues

Include:
- Your OS and version
- Python version (`python3 --version`)
- Error messages
- Build output

## 📝 License

This build configuration is part of the Imager project and follows the same MIT License.

---

**Ready to build?** Just run `./build.sh` and get your GUI executable in minutes! 🎉
