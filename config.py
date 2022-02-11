from pathlib import Path
from os.path import dirname, abspath

# path variables
PROJECT_PATH = Path(abspath(dirname(__name__)))
LOG_PATH = PROJECT_PATH / 'log'

# buffer size for TCP connections
BUFFER_SIZE = 2048

# aTLAS Version for check at supervisor <-> director connection
ATLAS_VERSION = "v 0.0.1"

TIME_MEASURE = False