"""Keep route tests away from the developer's working database."""

import os
import shutil
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DATABASE = PROJECT_ROOT / "database" / "college_darpan.db"
TEST_DATABASE_DIR = Path(tempfile.mkdtemp(prefix="college-darpan-tests-"))
TEST_DATABASE = TEST_DATABASE_DIR / "college_darpan.db"

if SOURCE_DATABASE.exists():
    shutil.copy2(SOURCE_DATABASE, TEST_DATABASE)

os.environ["COLLEGE_DARPAN_DATABASE_PATH"] = str(TEST_DATABASE)
