"""Safely add SBTET's 2026-27 polytechnic directory to an existing database.

This importer only adds missing institutions and two source metadata columns.
It never resets tables, edits existing records, or inserts fees/cutoffs/placements.
It is idempotent and can be run with: python -m database.import_sbtet_directory
"""
import json
import os
import sqlite3

from config import Config

SOURCE_URL = "https://sbtet.telangana.gov.in/downloads/Circular/LPCET%202026%20Booklet.pdf"
SOURCE_NAME = "SBTET Telangana LPCET 2026-27 Booklet"
ACADEMIC_YEAR = "2026-27"


def import_directory(database_path=None):
    database_path = database_path or Config.DATABASE_PATH
    entries_path = os.path.join(os.path.dirname(__file__), "sbtet_polytechnics_2026.json")
    with open(entries_path, encoding="utf-8") as source_file:
        entries = json.load(source_file)

    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(colleges)")}
        if not existing_columns:
            raise RuntimeError("The colleges table is missing; initialize the app database first.")
        if "source_name" not in existing_columns:
            connection.execute("ALTER TABLE colleges ADD COLUMN source_name TEXT")
        if "source_academic_year" not in existing_columns:
            connection.execute("ALTER TABLE colleges ADD COLUMN source_academic_year TEXT")

        inserted = 0
        for item in entries:
            college_code = f"SBTET-{item['code']}"
            found = connection.execute(
                "SELECT 1 FROM colleges WHERE college_code = ?", (college_code,)
            ).fetchone()
            if found:
                continue
            connection.execute(
                """INSERT INTO colleges
                   (name, college_code, district, city, address, primary_category,
                    institution_type, management_type, approval_body, hostel_available,
                    transport_available, verification_status, source_url, last_checked_date,
                    source_name, source_academic_year)
                   VALUES (?, ?, ?, ?, ?, 'polytechnic', 'Government Polytechnic',
                           'Government', 'SBTET', NULL, NULL, 'Verified', ?,
                           date('now'), ?, ?)""",
                (item["name"], college_code, item["district"], item["city"], item["address"],
                 SOURCE_URL, SOURCE_NAME, ACADEMIC_YEAR),
            )
            inserted += 1
        connection.commit()
        return {"listed": len(entries), "inserted": inserted, "academic_year": ACADEMIC_YEAR}
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    print(import_directory())
