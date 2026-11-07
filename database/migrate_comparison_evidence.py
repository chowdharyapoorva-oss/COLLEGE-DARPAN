"""Create field-level evidence storage and migrate the sourced comparison facts."""
import json
import sqlite3
from pathlib import Path

from config import Config


def migrate(database_path=None):
    database_path = database_path or Config.DATABASE_PATH
    root = Path(__file__).resolve().parent
    evidence = json.loads((root / "comparison_evidence.json").read_text(encoding="utf-8"))
    conn = sqlite3.connect(database_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript((root / "migrations" / "001_comparison_evidence.sql").read_text(encoding="utf-8"))
        moved = 0
        for code, fields in evidence.items():
            row = conn.execute("SELECT id FROM colleges WHERE college_code = ?", (code,)).fetchone()
            if not row:
                continue
            for name, item in fields.items():
                value = str(item["value"])
                if item.get("unit"):
                    value += f" {item['unit']}"
                cur = conn.execute(
                    """INSERT OR IGNORE INTO college_attribute_evidence
                       (college_id, field_name, value, source_title, source_url,
                        academic_year, status, scope)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (row[0], name, value, item["source_name"], item["source_url"],
                     item.get("academic_year"), item["status"], item["scope"]),
                )
                moved += cur.rowcount
        conn.commit()
        return moved
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print({"evidence_rows_inserted": migrate()})
