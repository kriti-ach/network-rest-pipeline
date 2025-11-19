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
    if not analysis.files:
        return False

    # Get file names (case-insensitive comparison)
    analysis_files_lower = {f.name.lower() for f in analysis.files}
    for pattern in PHYSIO_FILE_PATTERNS:
        if pattern.lower() in analysis_files_lower:
            return True
    return False

