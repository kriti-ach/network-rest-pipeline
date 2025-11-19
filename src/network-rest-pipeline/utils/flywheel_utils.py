"""Flywheel-related utility functions."""

import os

import flywheel
from flywheel import ApiException

from config import PHYSIO_FILE_PATTERNS

def find_physio_files(analysis: flywheel.Analysis) -> bool:
    """Check if analysis contains any physio files.

    Args:
        analysis: Flywheel Analysis object to check.

    Returns:
        bool: True if analysis contains any physio files, False otherwise.
    """
    # Try different ways to access files
    files = None
    
    # Method 1: Direct access
    if hasattr(analysis, 'files') and analysis.files:
        files = analysis.files
    # Method 2: Check if files is callable
    elif hasattr(analysis, 'files') and callable(analysis.files):
        try:
            files = analysis.files()
        except (TypeError, AttributeError):
            pass
    # Method 3: Check outputs
    elif hasattr(analysis, 'outputs') and analysis.outputs:
        files = analysis.outputs
    
    if not files:
        return False

    # Get file names (case-insensitive comparison)
    # Handle both list and iterable
    if isinstance(files, list):
        file_list = files
    else:
        try:
            file_list = list(files)
        except (TypeError, AttributeError):
            return False
    
    analysis_files_lower = set()
    for f in file_list:
        # Handle different file object types
        if hasattr(f, 'name'):
            analysis_files_lower.add(f.name.lower())
        elif isinstance(f, str):
            analysis_files_lower.add(f.lower())
        elif isinstance(f, dict) and 'name' in f:
            analysis_files_lower.add(f['name'].lower())
    
    # Debug: print found files for first few analyses
    if len(analysis_files_lower) > 0:
        # Only print first time to avoid spam
        if not hasattr(find_physio_files, '_debug_printed'):
            print(f'    Debug: Found {len(analysis_files_lower)} files in analysis')
            print(f'    Debug: File names: {sorted(analysis_files_lower)[:10]}')  # First 10
            find_physio_files._debug_printed = True
    
    for pattern in PHYSIO_FILE_PATTERNS:
        if pattern.lower() in analysis_files_lower:
            return True
    return False

