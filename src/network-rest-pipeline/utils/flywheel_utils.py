"""Flywheel-related utility functions."""

import os

import flywheel
from flywheel import ApiException

from config import PHYSIO_FILE_PATTERNS

def find_physio_files(analysis):
    """
    Checks if an analysis object contains physio-related CSV files in its outputs.

    Args:
        analysis (flywheel.Analysis): The full analysis object to inspect.

    Returns:
        bool: True if physio CSV files are found, False otherwise.
    """
    # Ensure the analysis object is valid and has an 'outputs' attribute
    if not analysis or not hasattr(analysis, 'outputs'):
        return False

    # Iterate through the OUTPUT files of the analysis
    for output_file in analysis.outputs:
        # Check if the file is a CSV and looks like a physio file
        if output_file.name.endswith('.csv'):
            # You can make this check more specific if needed
            if 'PPG_' in output_file.name or 'RESP_' in output_file.name:
                return True  # Found one, no need to look further
    
    return False # Did not find any physio files in the outputs

