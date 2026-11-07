"""The SBTET importer must be additive, source-labelled, and repeatable."""
import json
import shutil
import sqlite3

from database.import_sbtet_directory import import_directory


def test_import_is_idempotent_and_preserves_existing_data(tmp_path):
    source_db = "database/college_darpan.db"
    test_db = tmp_path / "college_darpan_test.db"
    shutil.copy2(source_db, test_db)
    connection = sqlite3.connect(test_db)
    before_count = connection.execute("SELECT COUNT(*) FROM colleges").fetchone()[0]
    before_names = connection.execute("SELECT id, name FROM colleges ORDER BY id").fetchall()
    existing_codes = {
        row[0] for row in connection.execute("SELECT college_code FROM colleges").fetchall()
    }
    connection.close()

    with open("database/sbtet_polytechnics_2026.json", encoding="utf-8") as data_file:
        expected_entries = json.load(data_file)
    expected_new = sum(f"SBTET-{item['code']}" not in existing_codes for item in expected_entries)
    first = import_directory(str(test_db))
    second = import_directory(str(test_db))

    connection = sqlite3.connect(test_db)
    after_count = connection.execute("SELECT COUNT(*) FROM colleges").fetchone()[0]
    after_names = connection.execute(
        "SELECT id, name FROM colleges WHERE id <= ? ORDER BY id", (before_count,)
    ).fetchall()
    listed = connection.execute(
        """SELECT COUNT(*) FROM colleges
           WHERE college_code LIKE 'SBTET-%' AND source_name IS NOT NULL
             AND source_academic_year = '2026-27' AND source_url IS NOT NULL
             AND verification_status = 'Verified'"""
    ).fetchone()[0]
    added_metrics = connection.execute(
        """SELECT COUNT(*) FROM college_metrics m
           JOIN colleges c ON c.id = m.college_id
           WHERE c.college_code LIKE 'SBTET-%'"""
    ).fetchone()[0]
    connection.close()

    assert before_names == after_names
    assert after_count == before_count + expected_new
    assert first["inserted"] == expected_new
    assert second["inserted"] == 0
    assert listed == len(expected_entries)
    assert added_metrics == 0
