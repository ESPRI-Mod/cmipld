import sys
import logging

LOG_HANDLERS = [logging.StreamHandler(sys.stdout)]
LOG_FORMAT = '[%(name)s][%(levelname)s] %(message)s'
LOG_LEVEL = logging.DEBUG

DIRNAME_AND_FILENAME_SEPARATOR = "_"

PROJECT_SPECS_FILENAME = 'project_specs.json'
PROJECT_ID_JSON_KEY = 'project_id'
CONTEXT_FILENAME = '000_context.jsonld'
CONTEXT_JSON_KEY = '@context'
DATA_DESCRIPTOR_JSON_KEY = '@id'

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=LOG_HANDLERS)