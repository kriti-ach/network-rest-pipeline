"""Subject-related utility functions."""

from pathlib import Path

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


def load_subjects_from_file(file_path: str) -> set[str]:
    """Load subject IDs from a text file.

    Args:
        file_path: Path to the file containing subject IDs (one per line).

    Returns:
        set[str]: Set of subject IDs from the file.
    """
    subjects = set()
    path = Path(file_path)
    if path.exists():
        with path.open() as f:
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
    # Return intersection - subjects in both files
    return validation_subs & discovery_subs
