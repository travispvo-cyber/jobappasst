#!/usr/bin/env python3
"""
Launch Dagster development server for Job Application Assistant

Usage:
    python scripts/run_dagster.py

This will start the Dagster UI at http://localhost:3000
"""

import subprocess
import sys
import os
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


def check_dagster_installed():
    """Check if Dagster is installed"""
    try:
        import dagster
        return True
    except ImportError:
        return False


def install_dagster():
    """Install Dagster and webserver"""
    print("Installing Dagster...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "dagster", "dagster-webserver"
    ])
    print("Dagster installed successfully!")


def run_dagster():
    """Run Dagster development server"""
    os.chdir(PROJECT_ROOT)

    print("\n" + "=" * 60)
    print("Starting Dagster Development Server")
    print("=" * 60)
    print(f"\nProject: {PROJECT_ROOT}")
    print("URL: http://localhost:3000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    subprocess.call([
        sys.executable, "-m", "dagster", "dev",
        "-m", "dagster_pipeline"
    ])


def main():
    if not check_dagster_installed():
        print("Dagster is not installed.")
        response = input("Would you like to install it? (y/n): ")
        if response.lower() == 'y':
            install_dagster()
        else:
            print("Dagster is required to run the pipeline.")
            sys.exit(1)

    run_dagster()


if __name__ == "__main__":
    main()
