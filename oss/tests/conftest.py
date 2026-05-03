"""Pytest configuration and shared fixtures"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    store_dir = Path(temp_dir) / "store"
    store_dir.mkdir()

    (store_dir / "NebulaShell").mkdir()
    (store_dir / "@{Falck}").mkdir()

    yield str(store_dir)

    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config(temp_data_dir, temp_store_dir):
    from oss.config.config import _global_config
    original_config = _global_config
    _global_config = None

    yield

    _global_config = original_config
