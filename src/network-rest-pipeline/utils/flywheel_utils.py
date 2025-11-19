"""Flywheel-related utility functions."""

import os

import flywheel
from flywheel import ApiException

from .config import PHYSIO_FILE_PATTERNS


def get_flywheel_client() -> flywheel.Client:
    """Initialize and return Flywheel client.

    Returns:
        flywheel.Client: Initialized Flywheel client.

    Raises:
        ValueError: If FLYWHEEL_API_KEY environment variable is not set.
    """
    api_key = os.environ.get('FLYWHEEL_API_KEY')
    if not api_key:
        raise ValueError(
            'FLYWHEEL_API_KEY environment variable not set. '
            'Please set it before running this script.'
        )

    return flywheel.Client(api_key)


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

