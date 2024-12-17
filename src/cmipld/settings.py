import logging
import os
import sys
from pathlib import Path


LOG_HANDLERS = [logging.StreamHandler(sys.stdout)]
LOG_FORMAT = "[%(name)s][%(levelname)s] %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=LOG_HANDLERS)


DIRNAME_AND_FILENAME_SEPARATOR = "_"

PROJECT_SPECS_FILENAME = "project_specs.json"
PROJECT_ID_JSON_KEY = "project_id"
CONTEXT_FILENAME = "000_context.jsonld"
CONTEXT_JSON_KEY = "@context"
TERM_ID_JSON_KEY = 'id'
COMPOSITE_PARTS_JSON_KEY = 'parts'
COMPOSITE_SEPARATOR_JSON_KEY = 'separator'
PATTERN_JSON_KEY = 'regex'
TERM_TYPE_JSON_KEY = 'type'
DRS_SPECS_JSON_KEY = 'drs_name'
SQLITE_FIRST_PK = 1
DATA_DESCRIPTOR_JSON_KEY = "@base"

