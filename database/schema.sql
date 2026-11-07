-- College Darpan Database Schema
-- Focus: Multi-Category Education Discovery (Polytechnic/Diploma, B.Tech/Engineering, Pharmacy) in Telangana

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS admission_cutoffs;
DROP TABLE IF EXISTS college_metrics;
DROP TABLE IF EXISTS branches;
DROP TABLE IF EXISTS shortlists;
DROP TABLE IF EXISTS chat_sessions;
DROP TABLE IF EXISTS colleges;

-- 1. Colleges / Institutions Table
CREATE TABLE colleges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    college_code TEXT UNIQUE NOT NULL,
    district TEXT NOT NULL,
    city TEXT,
    address TEXT NOT NULL,
    primary_category TEXT NOT NULL DEFAULT 'engineering', -- 'polytechnic', 'engineering', 'pharmacy', 'multi'
    institution_type TEXT NOT NULL, -- 'Government Polytechnic', 'University College', 'Private Autonomous', 'Affiliated Private', 'State Private University'
    management_type TEXT NOT NULL DEFAULT 'Private', -- 'Government', 'University', 'Private Aided', 'Private Unaided'
    official_website TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    description TEXT,
    est_year INTEGER,
    campus_area_acres REAL,
    naac_grade TEXT,
    nirf_band TEXT,
    approval_body TEXT DEFAULT 'AICTE', -- 'AICTE', 'PCI', 'SBTET', 'UGC', 'AICTE & PCI'
    hostel_available INTEGER DEFAULT 0, -- 1 for yes, 0 for no
    transport_available INTEGER DEFAULT 1,
    verification_status TEXT NOT NULL DEFAULT 'Needs Verification', -- 'Verified', 'Partially Verified', 'Needs Verification', 'Information Unavailable'
    source_url TEXT,
    source_name TEXT,
    source_academic_year TEXT,
    last_checked_date TEXT DEFAULT '2024-09-01'
);

-- 2. Programmes / Branches Table (Backward compatible with branches)
CREATE TABLE branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    category TEXT NOT NULL DEFAULT 'engineering', -- 'polytechnic', 'engineering', 'pharmacy'
    degree_level TEXT NOT NULL DEFAULT 'B.Tech', -- 'Diploma', 'B.Tech', 'D.Pharm', 'B.Pharm', 'Pharm.D', 'M.Pharm', 'M.Tech'
    course_name TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    branch_code TEXT NOT NULL,
    duration_years INTEGER DEFAULT 4,
    seats_intake INTEGER,
    program_status TEXT DEFAULT 'Active', -- 'Active', 'Approved by AICTE', 'Approved by PCI', 'SBTET Recognized'
    admission_route TEXT, -- 'TS POLYCET', 'TS EAPCET', 'TS ECET', 'GPAT / TS PGECET'
    eligibility_criteria TEXT,
    approval_info TEXT,
    source TEXT,
    academic_year TEXT DEFAULT '2024-25',
    verification_status TEXT DEFAULT 'Verified',
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

-- 3. College Metrics Table
CREATE TABLE college_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    academic_year TEXT NOT NULL,
    annual_tuition_fee REAL, -- In INR
    other_fees REAL,
    govt_concession_fee REAL, -- subsidized fee under TS ePASS
    placement_percentage REAL, -- percentage 0-100
    average_package REAL, -- in Lakhs per Annum (LPA)
    highest_package REAL, -- in LPA
    median_package REAL, -- in LPA
    eligible_students_count INTEGER,
    placed_students_count INTEGER,
    top_recruiters TEXT,
    faculty_information TEXT,
    infrastructure_information TEXT,
    laboratories_information TEXT,
    hostel_information TEXT,
    internship_support TEXT,
    source_url TEXT,
    last_updated TEXT,
    verification_status TEXT NOT NULL DEFAULT 'Needs Verification',
    notes TEXT,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

-- 4. Admission Cutoffs Table
CREATE TABLE admission_cutoffs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    exam_name TEXT NOT NULL, -- 'TS POLYCET', 'TS ECET', 'TS EAPCET', 'GPAT'
    admission_year TEXT NOT NULL, -- '2023', '2024'
    admission_pathway TEXT NOT NULL, -- 'Diploma First Year', 'Lateral Entry (2nd Year)', 'First Year Entry', 'Doctoral Professional'
    category TEXT NOT NULL, -- 'OC_BOYS', 'OC_GIRLS', 'BC_A', 'BC_B', 'BC_D', 'SC', 'ST', 'EWS'
    cutoff_rank INTEGER NOT NULL,
    source_url TEXT,
    verification_status TEXT NOT NULL DEFAULT 'Verified',
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE
);

-- 5. Chat Sessions Table (Minimal, local, privacy-friendly)
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_identifier TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Temporary Shortlist Table (For student dashboard/shortlisting)
CREATE TABLE shortlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    college_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE
);

-- Indexes for fast searching and filtering
CREATE INDEX idx_colleges_category ON colleges(primary_category);
CREATE INDEX idx_colleges_district ON colleges(district);
CREATE INDEX idx_colleges_type ON colleges(institution_type);
CREATE INDEX idx_colleges_mgmt ON colleges(management_type);
CREATE INDEX idx_branches_college ON branches(college_id);
CREATE INDEX idx_branches_cat ON branches(category);
CREATE INDEX idx_branches_code ON branches(branch_code);
CREATE INDEX idx_metrics_college ON college_metrics(college_id);
CREATE INDEX idx_cutoffs_lookup ON admission_cutoffs(college_id, branch_id, exam_name, category);
