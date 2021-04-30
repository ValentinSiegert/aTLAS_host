from pathlib import Path
from os.path import dirname, abspath

# path variables
PROJECT_PATH = Path(abspath(dirname(__name__)))
LOG_PATH = PROJECT_PATH / 'log'
