#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-load .env file for Cursor
This script automatically loads environment variables from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def auto_load_env():
    """Automatically load .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
        return True
    else:
        print(f"⚠️  No .env file found at {env_file.absolute()}")
        return False

if __name__ == "__main__":
    auto_load_env()
