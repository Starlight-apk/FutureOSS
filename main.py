#!/usr/bin/env python3
import sys
from pathlib import Path

workspace_dir = Path(__file__).parent.resolve()
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

from oss.cli import main

if __name__ == "__main__":
    main()
