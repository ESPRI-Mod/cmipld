import sys
import logging

LOG_HANDLERS = [logging.StreamHandler(sys.stdout)]
LOG_FORMAT = '[%(name)s][%(levelname)s] %(message)s'
LOG_LEVEL = logging.DEBUG

DIRNAME_AND_FILENAME_SEPARATOR = "_"

SQLITE_URL_PREFIX = 'sqlite://'
PROJECT_SQLITE_FILENAME = "projects.sqlite"
UNIVERS_SQLITE_FILENAME = "univers.sqlite"
PROJECT_SQLITE_URL = f'{SQLITE_URL_PREFIX}/{PROJECT_SQLITE_FILENAME}'
UNIVERS_SQLITE_URL = f'{SQLITE_URL_PREFIX}/{UNIVERS_SQLITE_FILENAME}'

PROJECT_SPECS_FILENAME = 'project_specs.json'
PROJECT_ID_JSON_KEY = 'project_id'
CONTEXT_FILENAME = '000_context.jsonld'
CONTEXT_JSON_KEY = '@context'
DATA_DESCRIPTOR_JSON_KEY = '@id'

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=LOG_HANDLERS)