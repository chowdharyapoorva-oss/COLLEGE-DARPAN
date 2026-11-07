-- Additive field-level evidence store for comparison data.
-- Safe to apply repeatedly; existing institution and metric rows are untouched.
CREATE TABLE IF NOT EXISTS college_attribute_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    value TEXT NOT NULL,
    source_title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    academic_year TEXT,
    status TEXT NOT NULL CHECK (status IN ('Verified', 'Estimated', 'Historical')),
    scope TEXT NOT NULL,
    last_checked_date TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE,
    UNIQUE (college_id, field_name, source_url, academic_year)
);
CREATE INDEX IF NOT EXISTS idx_attribute_evidence_college
    ON college_attribute_evidence(college_id, field_name);
