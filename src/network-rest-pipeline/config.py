"""Configuration for Flywheel project and subject mappings."""

import os

# Flywheel project name
FLYWHEEL_PROJECT = 'russpold/r01network'
BASE_PATH = "/home/groups/russpold/code/network_fmri"
VALIDATION_SUBS_FILE = os.path.join(BASE_PATH, "subs.txt")
DISCOVERY_SUBS_FILE = os.path.join(BASE_PATH, "discovery_subs.txt")
OUTPUT_DIR = '/oak/stanford/groups/russpold/data/network_grant/rest_pipeline_outputs'

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

