"""Subject-related utility functions."""

from .config import SUBJECT_ALIASES


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

