# Python Setup & Compatibility Guide

This project works with multiple Python installations and automatically detects which one is available.

## Supported Python Commands

The exporter works with any of these installed:
- `python3` (Linux, macOS, Windows)
- `python` (Windows, or system alias)
- `py` (Windows Python Launcher)

## Running Tools

### Option 1: Using `python` (Recommended)
```bash
python tools/exporter.py --interactive
```

### Option 2: Using `python3`
```bash
python3 tools/exporter.py --interactive
```

### Option 3: Direct execution (Linux/macOS)
```bash
./tools/exporter.py --interactive
```

### Option 4: Using Python detector script
```bash
# First, check which Python is available
python tools/python_detect.py

# Then use the detected version automatically
python tools/exporter.py --interactive
```

## Checking Your Python Installation

```bash
# Check if python is available
python --version

# Check if python3 is available
python3 --version

# Check system PATH for Python
which python        # Linux/macOS
where python        # Windows (PowerShell)
```

## Windows Users

If `python` doesn't work, try:
```cmd
# Using python3
python3 tools/exporter.py --interactive

# OR using py launcher (Windows)
py -3 tools/exporter.py --interactive

# OR using full path
C:\Python39\python.exe tools\exporter.py --interactive
```

## Linux/macOS Users

```bash
# Most common
python3 tools/exporter.py --interactive

# Or if python is aliased to python3
python tools/exporter.py --interactive
```

## Troubleshooting

### "Command not found: python"
Install Python 3: https://www.python.org/downloads/

### "Command not found: python3"
Try: `python --version` or check if it's installed in a non-standard location.

### Want to use a specific Python version?
```bash
# Use explicit path
/usr/bin/python3 tools/exporter.py --interactive

# OR on Windows
C:\Python39\python.exe tools\exporter.py --interactive
```

## Virtual Environment (Optional)

If using a virtual environment:
```bash
# Create venv
python -m venv venv

# Activate venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Run exporter
python tools/exporter.py --interactive
```

## How Auto-Detection Works

The tools use `sys.executable` at runtime, which means:
1. They use the exact Python executable that's running them
2. No hardcoded `python3` or `python` in subprocess calls
3. Works consistently across Windows, Linux, macOS

**Result:** Whatever Python you use to invoke the tool is what gets used for all subprocesses.

## All Tools Support This

- `exporter.py` ✅
- `interactive_exporter.py` ✅  
- `update_checker.py` ✅
- `context_builder.py` ✅
- All other tools ✅
