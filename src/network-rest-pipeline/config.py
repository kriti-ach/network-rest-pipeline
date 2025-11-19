"""Configuration for Flywheel project and subject mappings."""

# Flywheel project name
FLYWHEEL_PROJECT = 'r01network'
OUTPUT_DIR = '/oak/stanford/groups/russpold/data/network_grant/rest_pipeline_outputs/'

# Special subject mappings (e.g., s29-2 should be counted as s29)
SUBJECT_ALIASES = {
    's29-2': 's29',
    's19-2': 's19',
    's43-2': 's43',
}

# Physio file patterns to look for in Analyses tab
PHYSIO_FILE_PATTERNS = [
    'PPG_FItData.csv',
    'PPG_FItTrig.csv',
    'RESP_FItData.csv',
    'RESP_FItTrig.csv',
]

