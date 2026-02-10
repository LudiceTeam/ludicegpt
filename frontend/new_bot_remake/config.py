import sys
import os
from pathlib import Path



PROJECT_ROOT = Path(__file__).parent.parent.parent


if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
print(f"Project root added to path: {PROJECT_ROOT}") 