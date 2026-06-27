#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows EXE Builder
Converts Streamlit app to Windows EXE using PyInstaller

Usage:
    python build_windows_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print header"""
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def run_command(cmd, description=""):
    """Execute command"""
    if description:
        print(f"[INFO] {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print_header("Stock Monitor - Windows EXE Build")

    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # 1. Check required tools
    print("[1/6] Checking requirements...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        print(f"[ERROR] Python 3.9+ required (current: {python_version.major}.{python_version.minor})")
        return False

    print(f"OK Python {python_version.major}.{python_version.minor}")

    # 2. Check PyInstaller
    print("\n[2/6] Checking PyInstaller...")
    result = subprocess.run("pip show pyinstaller", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("[INFO] Installing PyInstaller...")
        if not run_command("pip install -q pyinstaller", "PyInstaller installation"):
            return False
    print("OK PyInstaller ready")

    # 3. Install dependencies
    print("\n[3/6] Installing dependencies...")
    if not run_command("pip install -q -r requirements.txt", "Dependency installation"):
        return False
    print("OK Dependencies installed")

    # 4. Clean build directory
    print("\n[4/6] Cleaning build directory...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"OK Removed {dir_name}/")

    # 5. Build EXE
    print("\n[5/6] Building Windows EXE...")
    print("(This may take 1-3 minutes)\n")

    # PyInstaller command
    pyinstaller_cmd = (
        "pyinstaller "
        "--name=StockMonitor "
        "--onefile "
        "--windowed "
        "--add-data=\"streamlit:streamlit\" "
        "--add-data=\"config:config\" "
        "--add-data=\".env.example:.\" "
        "--hidden-import=streamlit "
        "--hidden-import=streamlit.elements "
        "--hidden-import=streamlit.elements.utils "
        "--hidden-import=pandas "
        "--hidden-import=plotly "
        "--hidden-import=numpy "
        "--hidden-import=websocket "
        "--hidden-import=websocket._core "
        "--hidden-import=websocket._socket "
        "--collect-submodules=streamlit "
        "streamlit/app.py"
    )

    if not run_command(pyinstaller_cmd, "EXE creation"):
        print("\n[WARNING] Could not create EXE with PyInstaller")
        print("Use run.bat instead")
        return False

    # 6. Final cleanup
    print("\n[6/6] Finalizing...")

    # Check executable
    exe_path = project_root / "dist" / "StockMonitor.exe"
    if exe_path.exists():
        print(f"OK EXE created: {exe_path}")
        print(f"  Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")

        print("\n[SUCCESS] Windows EXE build completed!")
        print_header("Next steps")
        print("1. Run dist/StockMonitor.exe")
        print("2. Or copy dist/ folder to another PC")
        print("\nNote:")
        print("- No Python required on target PC")
        print("- First run takes 1-2 minutes (loading)")
        print("- Edit .env file to add API keys")

        return True
    else:
        print("[ERROR] EXE creation failed")
        return False

if __name__ == "__main__":
    print_header("Stock Monitor Windows EXE Builder")
    success = main()

    if not success:
        print("\n" + "="*50)
        print("  Build failed")
        print("="*50)
        print("\n[Solutions]")
        print("1. Check Python is in PATH")
        print("2. Run as administrator")
        print("3. Or use run.bat instead")
        sys.exit(1)

    sys.exit(0)
