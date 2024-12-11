import logging
import os
import sys
from pathlib import Path

LOG_HANDLERS = [logging.StreamHandler(sys.stdout)]
LOG_FORMAT = "[%(name)s][%(levelname)s] %(message)s"
LOG_LEVEL = logging.INFO

DIRNAME_AND_FILENAME_SEPARATOR = "_"

ROOT_DIR_PATH = Path(os.path.abspath(__file__)).parents[2]

PROJECT_SPECS_FILENAME = "project_specs.json"
PROJECT_ID_JSON_KEY = "project_id"
CONTEXT_FILENAME = "000_context.jsonld"
CONTEXT_JSON_KEY = "@context"
TERM_ID_JSON_KEY = 'id'
COMPOSITE_JSON_KEY = 'parts'
PATTERN_JSON_KEY = 'regex'
TERM_TYPE_JSON_KEY = 'type'
DRS_SPECS_JSON_KEY = 'drs_name'
SQLITE_FIRST_PK = 1

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=LOG_HANDLERS)

# TODO: file names should be rework.
SKIPPED_FILE_DIR_NAME_PREFIXES = ['_', '.', 'src']

# TODO: should be replaced by the type key in term json files.
DATA_DESCRIPTOR_JSON_KEY = "@base"

# TODO: this variable lists the data descriptors whose terms are references to terms from other data descriptors.
# This list will be removed when mechanism that automatically recognizes such data descriptors, will be implemented.
DATA_DESCRIPTORS_WHOSE_TERMS_ARE_REFERENCES_TO_OTHER_TERMS = ['organisation']
