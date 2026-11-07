"""
Database initialization script for College Darpan.
Run this script to set up SQLite tables and load the verified dataset.
"""

import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config
from database.db import execute_script
from database.seed_data import seed_database

def initialize_database():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    print(f"[Init DB] Initializing database at: {Config.DATABASE_PATH}")
    
    # 1. Execute Schema
    execute_script(schema_path)
    print("[Init DB] Schema tables created successfully.")
    
    # 2. Seed Data
    seed_database()
    print("[Init DB] Database ready for College Darpan.")

if __name__ == "__main__":
    initialize_database()
