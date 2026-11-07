"""
College Service for College Darpan.
Provides multi-category data access, filtering, searching, metrics, and comparisons
across Polytechnic, B.Tech/Engineering, and Pharmacy institutions in Telangana.
"""

import json
from pathlib import Path

from database.db import query_db


def _get_comparison_evidence():
    """Load field-level comparison facts from SQLite, with JSON compatibility fallback."""
    try:
        rows = query_db("""SELECT c.college_code, e.field_name, e.value, e.source_title,
                                e.source_url, e.academic_year, e.status, e.scope
                         FROM college_attribute_evidence e
                         JOIN colleges c ON c.id = e.college_id
                         ORDER BY e.id""")
        if rows:
            evidence = {}
            for row in rows:
                evidence.setdefault(row["college_code"], {})[row["field_name"]] = {
                    "value": row["value"], "status": row["status"],
                    "academic_year": row["academic_year"], "source_name": row["source_title"],
                    "source_url": row["source_url"], "scope": row["scope"],
                }
            return evidence
    except Exception:
        # Older database copies may not have had the additive migration applied.
        pass
    source_path = Path(__file__).resolve().parent.parent / "database" / "comparison_evidence.json"
    try:
        with source_path.open(encoding="utf-8") as source_file:
            return json.load(source_file)
    except (OSError, json.JSONDecodeError):
        return {}

def get_quick_statistics():
    """Returns genuine counts directly from the database without fabricating numbers."""
    colleges_count = query_db("SELECT COUNT(*) as count FROM colleges", one=True)["count"]
    polytechnic_count = query_db("SELECT COUNT(*) as count FROM colleges WHERE primary_category = 'polytechnic'", one=True)["count"]
    engineering_count = query_db("SELECT COUNT(*) as count FROM colleges WHERE primary_category = 'engineering'", one=True)["count"]
    pharmacy_count = query_db("SELECT COUNT(*) as count FROM colleges WHERE primary_category = 'pharmacy'", one=True)["count"]
    
    branches_count = query_db("SELECT COUNT(DISTINCT branch_name) as count FROM branches", one=True)["count"]
    verified_placements = query_db(
        "SELECT COUNT(*) as count FROM college_metrics WHERE placement_percentage IS NOT NULL AND verification_status = 'Verified'",
        one=True
    )["count"]
    pathways_count = query_db("SELECT COUNT(DISTINCT admission_pathway) as count FROM admission_cutoffs", one=True)["count"]
    source_linked_count = query_db(
        "SELECT COUNT(*) as count FROM colleges WHERE source_name IS NOT NULL AND source_academic_year IS NOT NULL AND source_url IS NOT NULL",
        one=True
    )["count"]
    
    return {
        "colleges_count": colleges_count,
        "polytechnic_count": polytechnic_count,
        "engineering_count": engineering_count,
        "pharmacy_count": pharmacy_count,
        "branches_count": branches_count,
        "verified_placements": verified_placements,
        "admission_pathways": pathways_count,
        "source_linked_count": source_linked_count
    }

def get_districts(category=None):
    """Returns sorted unique districts present in the college database, optionally filtered by category."""
    if category and category != "All":
        rows = query_db("SELECT DISTINCT district FROM colleges WHERE primary_category = ? ORDER BY district ASC", [category])
    else:
        rows = query_db("SELECT DISTINCT district FROM colleges ORDER BY district ASC")
    return [r["district"] for r in rows]

def get_institution_types(category=None):
    """Returns sorted unique institution types."""
    if category and category != "All":
        rows = query_db("SELECT DISTINCT institution_type FROM colleges WHERE primary_category = ? ORDER BY institution_type ASC", [category])
    else:
        rows = query_db("SELECT DISTINCT institution_type FROM colleges ORDER BY institution_type ASC")
    return [r["institution_type"] for r in rows]

def get_management_types():
    """Returns sorted unique management types (Government, University, Private Unaided, etc.)."""
    rows = query_db("SELECT DISTINCT management_type FROM colleges ORDER BY management_type ASC")
    return [r["management_type"] for r in rows]

def get_unique_branches(category=None):
    """Returns distinct branch codes and names available across colleges."""
    if category and category != "All":
        rows = query_db(
            "SELECT DISTINCT branch_code, branch_name, category, degree_level FROM branches WHERE category = ? ORDER BY branch_name ASC",
            [category]
        )
    else:
        rows = query_db("SELECT DISTINCT branch_code, branch_name, category, degree_level FROM branches ORDER BY branch_name ASC")
    return rows

def get_all_colleges(search=None, district=None, branch=None, institution_type=None, 
                     category=None, management_type=None, max_fee=None, 
                     verified_placements_only=False, pathway=None, hostel_only=False, 
                     sort_by="name_asc"):
    """
    Search and filter colleges based on user selections across all 3 education categories.
    Supports safe parameterized SQL queries.
    """
    base_query = """
        SELECT 
            c.id, c.name, c.college_code, c.district, c.city, c.address, 
            c.primary_category, c.institution_type, c.management_type, 
            c.official_website, c.contact_email, c.contact_phone, c.description, 
            c.est_year, c.campus_area_acres, c.naac_grade, c.nirf_band,
            c.approval_body, c.hostel_available, c.transport_available,
            c.verification_status, c.source_url, c.last_checked_date,
            c.source_name, c.source_academic_year,
            m.annual_tuition_fee, m.other_fees, m.govt_concession_fee,
            m.placement_percentage, m.average_package, m.highest_package,
            m.median_package, m.top_recruiters,
            m.verification_status AS metrics_verification_status,
            m.academic_year AS metrics_academic_year, m.source_url AS metrics_source_url
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE 1=1
    """
    params = []

    # Category Filter (polytechnic, engineering, pharmacy)
    if category and category.strip() and category != "All":
        base_query += " AND c.primary_category = ?"
        params.append(category.strip().lower())

    # Management Type Filter (Government, University, Private Unaided)
    if management_type and management_type.strip() and management_type != "All":
        base_query += " AND c.management_type = ?"
        params.append(management_type.strip())

    # Search keyword
    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        base_query += """
            AND (
                c.name LIKE ? OR 
                c.college_code LIKE ? OR 
                c.district LIKE ? OR 
                c.city LIKE ? OR
                c.address LIKE ? OR
                EXISTS (
                    SELECT 1 FROM branches b 
                    WHERE b.college_id = c.id AND (b.branch_name LIKE ? OR b.branch_code LIKE ? OR b.course_name LIKE ?)
                )
            )
        """
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern])

    # District Filter
    if district and district.strip() and district != "All":
        base_query += " AND c.district = ?"
        params.append(district.strip())

    # Institution Type Filter
    if institution_type and institution_type.strip() and institution_type != "All":
        base_query += " AND c.institution_type = ?"
        params.append(institution_type.strip())

    # Branch / Programme Filter
    if branch and branch.strip() and branch != "All":
        base_query += """
            AND EXISTS (
                SELECT 1 FROM branches b 
                WHERE b.college_id = c.id AND (b.branch_code = ? OR b.branch_name LIKE ?)
            )
        """
        params.extend([branch.strip(), f"%{branch.strip()}%"])

    # Max Tuition Fee Filter
    if max_fee and str(max_fee).isdigit():
        base_query += " AND (m.annual_tuition_fee IS NOT NULL AND m.annual_tuition_fee <= ?)"
        params.append(float(max_fee))

    # Verified Placement Data Filter
    if verified_placements_only:
        base_query += """ AND (
            m.placement_percentage IS NOT NULL
            AND m.verification_status = 'Verified'
            AND m.source_url IS NOT NULL AND TRIM(m.source_url) != ''
            AND m.academic_year IS NOT NULL AND TRIM(m.academic_year) != ''
        )"""

    # Hostel Availability
    if hostel_only:
        base_query += " AND c.hostel_available = 1"

    # Admission Pathway Filter
    if pathway and pathway.strip() and pathway != "All":
        base_query += """
            AND EXISTS (
                SELECT 1 FROM admission_cutoffs ac 
                WHERE ac.college_id = c.id AND ac.admission_pathway LIKE ?
            )
        """
        params.append(f"%{pathway.strip()}%")

    # Sorting
    if sort_by == "name_desc":
        base_query += " ORDER BY c.name DESC"
    elif sort_by == "fee_asc":
        base_query += " ORDER BY m.annual_tuition_fee ASC NULLS LAST"
    elif sort_by == "fee_desc":
        base_query += " ORDER BY m.annual_tuition_fee DESC NULLS LAST"
    elif sort_by == "placement_desc":
        base_query += " ORDER BY m.placement_percentage DESC NULLS LAST"
    elif sort_by == "avg_pkg_desc":
        base_query += " ORDER BY m.average_package DESC NULLS LAST"
    elif sort_by == "est_year_asc":
        base_query += " ORDER BY c.est_year ASC NULLS LAST"
    else:  # default: name_asc
        base_query += " ORDER BY c.name ASC"

    colleges = query_db(base_query, params)

    # Attach branches summary to each college
    for col in colleges:
        branches = query_db(
            "SELECT branch_name, branch_code, category, degree_level, course_name, duration_years, seats_intake FROM branches WHERE college_id = ? ORDER BY branch_name ASC",
            [col["id"]]
        )
        col["branches"] = branches

    return colleges

def get_college_by_id(college_id):
    """Retrieves full college details including metrics, branches/programmes, and cutoffs."""
    college = query_db("""
        SELECT c.*, m.annual_tuition_fee, m.other_fees, m.govt_concession_fee,
               m.placement_percentage, m.average_package, m.highest_package, 
               m.median_package, m.eligible_students_count, m.placed_students_count,
               m.top_recruiters, m.faculty_information, m.infrastructure_information, 
               m.laboratories_information, m.hostel_information, m.internship_support,
               m.source_url as metrics_source_url, m.last_updated as metrics_last_updated,
               m.verification_status as metrics_verification_status, m.academic_year as metrics_year,
               m.notes as metrics_notes
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE c.id = ?
    """, [college_id], one=True)

    if not college:
        return None

    branches = query_db("""
        SELECT * FROM branches WHERE college_id = ? ORDER BY category ASC, branch_name ASC
    """, [college_id])

    cutoffs = query_db("""
        SELECT ac.*, b.branch_name, b.branch_code, b.course_name, b.category as branch_category
        FROM admission_cutoffs ac
        JOIN branches b ON ac.branch_id = b.id
        WHERE ac.college_id = ?
        ORDER BY ac.exam_name ASC, b.branch_name ASC, ac.cutoff_rank ASC
    """, [college_id])

    college["branches"] = branches
    college["cutoffs"] = cutoffs
    return college

def compare_colleges(college_ids):
    """Retrieves full comparative data for up to four selected colleges."""
    if not college_ids:
        return []
    
    colleges = []
    evidence_by_code = _get_comparison_evidence()
    for cid in college_ids[:4]:
        data = get_college_by_id(cid)
        if data:
            data["comparison_evidence"] = evidence_by_code.get(data["college_code"], {})
            colleges.append(data)
    return colleges
