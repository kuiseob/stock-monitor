#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows EXE Builder - Enhanced Version
Converts Streamlit app to Windows EXE using PyInstaller with full support

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
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

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
    print_header("Stock Monitor - Windows EXE Build (Enhanced)")

    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # 1. Check required tools
    print("[1/7] Checking requirements...")
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        print(f"[ERROR] Python 3.9+ required (current: {python_version.major}.{python_version.minor})")
        return False
    print(f"OK Python {python_version.major}.{python_version.minor}")

    # 2. Check PyInstaller
    print("\n[2/7] Checking PyInstaller...")
    result = subprocess.run("pip show pyinstaller", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("[INFO] Installing PyInstaller...")
        if not run_command("pip install -q pyinstaller", "PyInstaller installation"):
            return False
    print("OK PyInstaller ready")

    # 3. Install dependencies
    print("\n[3/7] Installing dependencies...")
    if not run_command("pip install -q -r requirements.txt", "Dependency installation"):
        return False
    print("OK Dependencies installed")

    # 4. Clean build directory
    print("\n[4/7] Cleaning build directory...")
    for dir_name in ["build", "dist", "StockMonitor.spec"]:
        if os.path.exists(dir_name):
            if os.path.isdir(dir_name):
                shutil.rmtree(dir_name)
            else:
                os.remove(dir_name)
            print(f"OK Removed {dir_name}")

    # 5. Build EXE with enhanced settings
    print("\n[5/7] Building Windows EXE (Enhanced)...")
    print("(This may take 2-5 minutes)\n")

    # Enhanced PyInstaller command with better Streamlit support
    pyinstaller_cmd = (
        "pyinstaller "
        "--name=StockMonitor "
        "--onedir "
        "--windowed "
        "--distpath=dist "
        "--workpath=build "
        "--specpath=. "
        "--add-data=\"streamlit:streamlit\" "
        "--add-data=\"config:config\" "
        "--add-data=\"src:src\" "
        "--add-data=\".env.example:.\" "
        "--collect-all=streamlit "
        "--collect-all=altair "
        "--collect-all=pandas "
        "--collect-all=plotly "
        "--collect-all=numpy "
        "--collect-all=pydantic "
        "--hidden-import=streamlit "
        "--hidden-import=streamlit.elements "
        "--hidden-import=streamlit.proto "
        "--hidden-import=pandas "
        "--hidden-import=plotly "
        "--hidden-import=numpy "
        "--hidden-import=websocket "
        "--hidden-import=altair "
        "--hidden-import=pydantic "
        "streamlit/app.py"
    )

    if not run_command(pyinstaller_cmd, "EXE creation"):
        print("\n[WARNING] EXE creation failed")
        return False

    # 6. Verify build
    print("\n[6/7] Verifying build...")
    exe_path = project_root / "dist" / "StockMonitor" / "StockMonitor.exe"
    if not exe_path.exists():
        # Try alternative path
        exe_path = project_root / "dist" / "StockMonitor.exe"

    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024*1024)
        print(f"OK EXE created: {exe_path}")
        print(f"  Size: {file_size:.1f} MB")
    else:
        print("[ERROR] EXE file not found")
        return False

    # 7. Final setup
    print("\n[7/7] Final setup...")

    # Copy .env.example to dist folder
    env_example = project_root / ".env.example"
    if env_example.exists():
        if exe_path.parent.exists():
            dist_env = exe_path.parent / ".env.example"
        else:
            dist_env = project_root / "dist" / ".env.example"
        shutil.copy(env_example, dist_env)
        print(f"OK Copied .env.example to dist folder")

    print("\n[SUCCESS] Windows EXE build completed!")
    print_header("Next steps")
    print("1. Run: dist/StockMonitor/StockMonitor.exe")
    print("2. Or copy entire dist/StockMonitor/ folder to another PC")
    print("\nNote:")
    print("- No Python required on target PC")
    print("- Edit .env file to add API keys")
    print("- First run may take a moment (Streamlit startup)")

    return True

if __name__ == "__main__":
    print_header("Stock Monitor Windows EXE Builder (Enhanced)")
    success = main()

    if not success:
        print("\n" + "="*60)
        print("  Build failed")
        print("="*60)
        print("\n[Solutions]")
        print("1. Check Python is in PATH")
        print("2. Run as administrator")
        print("3. Check disk space (need ~500MB)")
        print("4. Run: pip install -q pyinstaller")
        sys.exit(1)

    sys.exit(0)
