import logging
import os
import sys
from pathlib import Path


LOG_HANDLERS = [logging.StreamHandler(sys.stdout)]
LOG_FORMAT = "[%(name)s][%(levelname)s] %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, handlers=LOG_HANDLERS)



