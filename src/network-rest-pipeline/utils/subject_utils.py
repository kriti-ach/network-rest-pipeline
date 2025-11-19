"""Subject-related utility functions."""

import os

from config import DISCOVERY_SUBS_FILE, SUBJECT_ALIASES, VALIDATION_SUBS_FILE


def normalize_subject_id(subject_id: str) -> str:
    """Normalize subject ID using aliases.

    Maps subject IDs according to SUBJECT_ALIASES configuration.
    For example, 's29-2' will be mapped to 's29'.

    Args:
        subject_id: Original subject ID string.

    Returns:
        str: Normalized subject ID (mapped if alias exists, otherwise original).
    """
    return SUBJECT_ALIASES.get(subject_id, subject_id)


def load_subjects_from_file(filepath: str) -> set[str]:
    """Read subject IDs from file.

    Args:
        filepath: Path to the file containing subject IDs.

    Returns:
        set[str]: Set of subject IDs.
    """
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return set()
    subjects = set()
    with open(filepath, 'r') as f:
        for line in f:
            subject_id = line.strip()
            if subject_id:  # Skip empty lines
                subjects.add(subject_id)
    return subjects


def get_valid_subjects() -> set[str]:
    """Get subjects that are in both validation and discovery files.

    Returns:
        set[str]: Set of subject IDs that appear in both files.
    """
    validation_subs = load_subjects_from_file(VALIDATION_SUBS_FILE)
    discovery_subs = load_subjects_from_file(DISCOVERY_SUBS_FILE)
    
    print(f"Loaded {len(validation_subs)} subjects from validation file")
    print(f"Loaded {len(discovery_subs)} subjects from discovery file")
    
    # Return intersection - subjects in both files
    valid_subs = validation_subs & discovery_subs
    print(f"Found {len(valid_subs)} subjects in both files")
    
    return valid_subs
