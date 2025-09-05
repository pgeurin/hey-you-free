#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calendar data loading infrastructure
Handles file I/O operations
"""
import json
from pathlib import Path
from typing import List, Dict, Any


def load_calendar_data(filename: str) -> List[Dict[str, Any]]:
    """Load calendar data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)


def save_prompt_to_file(prompt: str, filename: str) -> None:
    """Save prompt to file"""
    with open(filename, 'w') as f:
        f.write(prompt)


def save_suggestions_to_file(suggestions: Dict[str, Any], filename: str) -> None:
    """Save meeting suggestions to JSON file"""
    with open(filename, 'w') as f:
        json.dump(suggestions, f, indent=2)


def file_exists(filename: str) -> bool:
    """Check if file exists"""
    return Path(filename).exists()
