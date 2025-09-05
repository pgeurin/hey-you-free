#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for meeting scheduler
Delegates to CLI adapter following Clean Architecture
"""
from src.adapters.cli import main, generate_meeting_suggestions
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate_meeting_suggestions()
    else:
        main()