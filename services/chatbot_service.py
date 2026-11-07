"""
Conversational Chatbot Service: Darpan AI Assistant.
Provides intelligent, database-backed guidance across:
- Polytechnic / Diploma (TS POLYCET)
- B.Tech / Engineering (TS EAPCET, TS ECET)
- Pharmacy (B.Pharm, Pharm.D, D.Pharm)
Without requiring external paid APIs.
"""

import re
from database.db import query_db

SOURCE_URL = "https://sbtet.telangana.gov.in/downloads/Circular/LPCET%202026%20Booklet.pdf"

COLLEGE_ALIAS_MAP = {
    # Engineering
    "ou": "OUCE",
    "osmania": "OUCE",
    "uceou": "OUCE",
    "ouce": "OUCE",
    "jntu": "JNTUH",
    "jntuh": "JNTUH",
    "kukatpally": "JNTUH",
    "cbit": "CBIT",
    "chaitanya bharathi": "CBIT",
    "vasavi": "VCE",
    "vce": "VCE",
    "vnr": "VNRV",
    "vnrvjiet": "VNRV",
    "vignana jyothi": "VNRV",
    "griet": "GRIET",
    "gokaraju": "GRIET",
    "cvr": "CVRH",
    "cvrh": "CVRH",
    "mrec": "MREC",
    "malla reddy": "MREC",
    "gcet": "GCET",
    "geethanjali": "GCET",
    "iare": "IARE",
    "aeronautical": "IARE",
    "anurag": "ANUR",
    "anurag university": "ANUR",
    "mgit": "MGIT",
    "mahatma gandhi": "MGIT",
    "bvrit": "BVRW",
    "bvrith": "BVRW",
    "vardhaman": "VMEG",
    "vmeg": "VMEG",
    "kits": "KITSW",
    "kitsw": "KITSW",
    "kakatiya institute": "KITSW",
    # Polytechnic
    "masab tank": "GPTM",
    "gpt masab tank": "GPTM",
    "gptm": "GPTM",
    "ramanthapur": "JNGP",
    "jngp": "JNGP",
    "jn govt polytechnic": "JNGP",
    "secunderabad polytechnic": "GPW",
    "women polytechnic": "GPW",
    "gpw": "GPW",
    "warangal polytechnic": "GPTW",
    "gptw": "GPTW",
    "nizamabad polytechnic": "GPTN",
    "gptn": "GPTN",
    "quli qutub": "QQGPT",
    "qqgpt": "QQGPT",
    "nalgonda polytechnic": "GPTLG",
    "tkr polytechnic": "TKRP",
    "tkrp": "TKRP",
    # Pharmacy
    "ucps": "UCPS",
    "kakatiya pharmacy": "UCPS",
    "pulla reddy": "GPRCP",
    "gprcp": "GPRCP",
    "g pulla reddy": "GPRCP",
    "sultan ul uloom": "SUCP",
    "sucp": "SUCP",
    "shadan": "SHDN",
    "shadan pharmacy": "SHDN",
    "st peters": "SPIPS",
    "spips": "SPIPS",
    "anurag pharmacy": "ANRP",
    "anrp": "ANRP"
}

def extract_colleges(text):
    """Finds referenced colleges in the user's question."""
    found = []
    text_lower = text.lower()
    for alias, code in COLLEGE_ALIAS_MAP.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text_lower):
            if code not in found:
                found.append(code)
    return found

def extract_branch_and_category(text):
    """Detects target discipline and education category."""
    text_upper = text.upper()
    
    # Category checks
    if any(k in text_upper for k in ["PHARMACY", "B.PHARM", "B PHARM", "PHARM.D", "PHARM D", "D.PHARM", "D PHARM", "MEDICINE"]):
        if "PHARM.D" in text_upper or "PHARM D" in text_upper:
            return "PHD", "Doctor of Pharmacy (Pharm.D)", "pharmacy"
        if "D.PHARM" in text_upper or "D PHARM" in text_upper:
            return "DPH", "Diploma in Pharmacy (D.Pharm)", "pharmacy"
        return "BPH", "Bachelor of Pharmacy (B.Pharm)", "pharmacy"

    if any(k in text_upper for k in ["POLYCET", "POLYTECHNIC", "DIPLOMA"]):
        if "COMPUTER" in text_upper or "CME" in text_upper:
            return "CME", "Computer Engineering (Diploma)", "polytechnic"
        if "PACKAGING" in text_upper or "PKG" in text_upper:
            return "PKG", "Packaging Technology (Diploma)", "polytechnic"
        return "CME", "Polytechnic / Diploma Programmes", "polytechnic"

    # Engineering Branches
    if "AIML" in text_upper or "AI & ML" in text_upper or "MACHINE LEARNING" in text_upper:
        return "AIML", "Artificial Intelligence & Machine Learning", "engineering"
    if "DATA SCIENCE" in text_upper or "CSD" in text_upper or "AIDS" in text_upper:
        return "CSD", "Data Science / AI & Data Science", "engineering"
    if "CSE" in text_upper or "COMPUTER SCIENCE" in text_upper:
        return "CSE", "Computer Science and Engineering", "engineering"
    if "INF" in text_upper or "INFORMATION TECH" in text_upper or " IT " in f" {text_upper} ":
        return "INF", "Information Technology", "engineering"
    if "ECE" in text_upper or "ELECTRONICS" in text_upper:
        return "ECE", "Electronics & Communication Engineering", "engineering"
    if "AERONAUTICAL" in text_upper or "AERO" in text_upper:
        return "AERO", "Aeronautical Engineering", "engineering"
    if "MECH" in text_upper or "MECHANICAL" in text_upper:
        return "MECH", "Mechanical Engineering", "engineering"
    if "CIVIL" in text_upper:
        return "CIVIL", "Civil Engineering", "engineering"
        
    return None, None, None

def extract_budget(text):
    """Parses numeric budget figures (e.g. 50000, 1 lakh, 1.2L)."""
    text_lower = text.lower()
    lakh_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)\b", text_lower)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)
        
    k_match = re.search(r"(\d+)\s*k\b", text_lower)
    if k_match:
        return int(k_match.group(1)) * 1000

    num_match = re.search(r"\b(\d{4,6})\b", text_lower)
    if num_match:
        return int(num_match.group(1))

    return None

def process_chat_message(user_message, session_context=None):
    """
    Main dialogue manager for Darpan AI Assistant.
    Analyzes intent across Polytechnic, Engineering, and Pharmacy.
    """
    if not user_message or not user_message.strip():
        return {
            "response": "Hello! I am **Darpan AI Assistant**, your transparent guidance counselor for Telangana education across **Polytechnic / Diploma, B.Tech / Engineering, and Pharmacy**. How can I help you today?",
            "suggested_actions": ["Government polytechnics offering Computer Engineering", "Which colleges offer AIML in Hyderabad?", "Top Pharmacy colleges in Telangana", "Compare OUCE and CBIT"],
            "matched_colleges": [],
            "source": "College Darpan Multi-Category Counselor"
        }

    msg = user_message.strip()
    msg_lower = msg.lower()
    
    colleges_found = extract_colleges(msg)
    branch_code, branch_name, category = extract_branch_and_category(msg)
    budget = extract_budget(msg)

    # 1. Comparison Intent
    if ("compare" in msg_lower or "vs" in msg_lower or "versus" in msg_lower or "difference between" in msg_lower) and len(colleges_found) >= 2:
        return handle_comparison(colleges_found)

    # Exam comparisons must win over the individual exam keyword branches.
    if any(k in msg_lower for k in ["difference between ecet", "ecet and eapcet", "polycet vs", "explain exams"]):
        return handle_entrance_exams_explanation()

    # 2. Pharmacy Specific Queries
    if "pharmacy" in msg_lower or "b.pharm" in msg_lower or "pharm.d" in msg_lower or "d.pharm" in msg_lower or category == "pharmacy":
        return handle_pharmacy_guidance(msg_lower, branch_code)

    # 3. Polytechnic / POLYCET Specific Queries
    if "polytechnic" in msg_lower or "polycet" in msg_lower or "diploma" in msg_lower or category == "polytechnic":
        return handle_polytechnic_guidance(msg_lower, branch_code)

    # 5. TS ECET Lateral Entry inquiries
    if "ecet" in msg_lower or "lateral entry" in msg_lower:
        return handle_ecet_guidance(branch_code, msg_lower)

    # 6. Verification status / Data transparency inquiries
    if any(k in msg_lower for k in ["unverified", "verification", "fake", "authentic", "accurate", "source", "verify"]):
        return handle_verification_inquiry()

    # 7. Factors to consider when choosing a college
    if any(k in msg_lower for k in ["factor", "how to choose", "consider", "decide", "criteria"]):
        return handle_decision_factors()

    # 8. Budget / Affordability inquiries
    if budget or any(k in msg_lower for k in ["budget", "afford", "cheap", "low fee", "fees", "tuition"]):
        return handle_budget_query(budget, msg_lower)

    # 9. Single College Specific inquiry
    if len(colleges_found) == 1:
        return handle_single_college(colleges_found[0])

    # 10. Branch specific queries
    if branch_code:
        return handle_branch_query(branch_code, branch_name, category, msg_lower)

    # 11. Placements inquiry
    if any(k in msg_lower for k in ["placement", "highest package", "average package", "recruiters", "salary", "jobs"]):
        return handle_placements_query()

    # 12. Greetings & General Help
    if any(k in msg_lower for k in ["hi", "hello", "hey", "help", "who are you", "start"]):
        return {
            "response": (
                "Hello! I am **Darpan AI Assistant**, designed to bring transparency to educational admissions across Telangana.\n\n"
                "I support all three major education pathways:\n"
                "• **Polytechnic / Diploma:** Find SBTET-listed institutions and browse source-backed programme details.\n"
                "• **B.Tech / Engineering:** TS EAPCET first-year and TS ECET lateral-entry cutoffs, branches (AIML, CSE, IT, ECE).\n"
                "• **Pharmacy:** B.Pharm, Pharm.D (6-year doctoral), D.Pharm, hospital affiliations, PCI approvals.\n\n"
                "What would you like to explore?"
            ),
            "suggested_actions": [
                "Government polytechnics offering Computer Engineering",
                "Which colleges offer AIML in Hyderabad?",
                "Colleges offering Pharm.D in Telangana",
                "Compare OUCE and CBIT"
            ],
            "matched_colleges": [],
            "source": "College Darpan Assistant"
        }

    # Fallback with graceful guided assistance
    return handle_general_search(msg)

def handle_comparison(college_codes):
    """Compares 2 or 3 colleges side-by-side using real database metrics."""
    codes = college_codes[:3]
    placeholders = ",".join(["?"] * len(codes))
    
    rows = query_db(f"""
        SELECT c.*, m.annual_tuition_fee, m.placement_percentage, m.average_package, 
               m.highest_package, m.top_recruiters, m.faculty_information,
               m.source_url AS metrics_source_url,
               m.verification_status AS metrics_verification_status,
               m.academic_year AS metrics_year
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE c.college_code IN ({placeholders})
    """, codes)

    if len(rows) < 2:
        return {
            "response": "I couldn't locate enough data for both institutions to perform a direct comparison. Please check the institution codes or use our dedicated **Compare Colleges** tool.",
            "suggested_actions": ["Open Compare Colleges Page", "Show all colleges"],
            "matched_colleges": [],
            "source": "College Darpan Database"
        }

    c1, c2 = rows[0], rows[1]
    
    metrics1_verified = c1.get("metrics_verification_status") == "Verified" and c1.get("metrics_source_url") and c1.get("metrics_year")
    metrics2_verified = c2.get("metrics_verification_status") == "Verified" and c2.get("metrics_source_url") and c2.get("metrics_year")
    fee_diff = "A source-backed annual fee comparison is unavailable for these records."
    if c1.get("annual_tuition_fee") and c2.get("annual_tuition_fee") and metrics1_verified and metrics2_verified:
        f1, f2 = c1["annual_tuition_fee"], c2["annual_tuition_fee"]
        if f1 < f2:
            fee_diff = f"**{c1['name']}** has a lower published annual tuition fee (₹{int(f1):,} vs ₹{int(f2):,})."
        elif f2 < f1:
            fee_diff = f"**{c2['name']}** has a lower published tuition fee (₹{int(f2):,} vs ₹{int(f1):,})."
        else:
            fee_diff = f"Both have identical published tuition fees of ₹{int(f1):,} / year."
    fee1 = f"₹{int(c1['annual_tuition_fee']):,}" if c1.get("annual_tuition_fee") and metrics1_verified else "Not verified"
    fee2 = f"₹{int(c2['annual_tuition_fee']):,}" if c2.get("annual_tuition_fee") and metrics2_verified else "Not verified"
    placement1 = f"{c1['placement_percentage']}%" if c1.get("placement_percentage") is not None and metrics1_verified else "Not verified"
    placement2 = f"{c2['placement_percentage']}%" if c2.get("placement_percentage") is not None and metrics2_verified else "Not verified"
    package1 = f"{c1['average_package']} LPA" if c1.get("average_package") and metrics1_verified else "Not verified"
    package2 = f"{c2['average_package']} LPA" if c2.get("average_package") and metrics2_verified else "Not verified"
    hostel1 = "Listed" if c1.get("hostel_available") == 1 else "Not listed"
    hostel2 = "Listed" if c2.get("hostel_available") == 1 else "Not listed"
    approval1 = c1.get("approval_body") or "Not listed"
    approval2 = c2.get("approval_body") or "Not listed"

    response_text = f"""### Side-by-Side Comparison: {c1['college_code']} vs {c2['college_code']}

| Feature | **{c1['college_code']}** ({c1['name'].split(',')[0]}) | **{c2['college_code']}** ({c2['name'].split(',')[0]}) |
| :--- | :--- | :--- |
| **Category** | {c1['primary_category'].capitalize()} | {c2['primary_category'].capitalize()} |
| **Management** | {c1['management_type']} ({c1['institution_type']}) | {c2['management_type']} ({c2['institution_type']}) |
| **District** | {c1['district']} | {c2['district']} |
| **Annual Tuition** | {fee1} | {fee2} |
| **Placement Rate** | {placement1} | {placement2} |
| **Avg Package** | {package1} | {package2} |
| **Hostel** | {hostel1} | {hostel2} |
| **Approval** | {approval1} | {approval2} |

**Trade-off Summary:**
{fee_diff}

> [!NOTE]
> Confirm fees, concessions, and other charges in the current official notice before making a decision.
"""
    return {
        "response": response_text,
        "suggested_actions": ["Compare in full matrix", "Check admission cutoffs", "Ask another question"],
        "matched_colleges": rows,
        "source": "College Darpan Verified Metrics"
    }

def handle_polytechnic_guidance(msg_lower, branch_code):
    """Provides specific guidance for Polytechnic / Diploma students in Telangana."""
    colleges = query_db("""
        SELECT c.id, c.name, c.college_code, c.district, c.institution_type, c.management_type
        FROM colleges c
        WHERE c.primary_category = 'polytechnic'
          AND c.source_name IS NOT NULL AND c.source_academic_year = '2026-27'
        ORDER BY c.name ASC
        LIMIT 6
    """)

    if branch_code:
        return handle_branch_query(branch_code, branch_code, "polytechnic", msg_lower)
    names = "\n".join(
        f"• **{college['name']}** — {college['district']} ({college['college_code']})"
        for college in colleges
    ) or "No polytechnic institutions are currently listed."
    response = (
        "### Telangana Polytechnic Directory\n\n"
        "These institution names are drawn from the local directory. The current SBTET "
        "2026–27 list is linked below. Fees, branch availability, and cutoffs are shown "
        "only when the database contains a source-backed record; missing figures are not estimated.\n\n"
        f"{names}\n\n"
        f"[Open the SBTET 2026–27 polytechnic booklet]({SOURCE_URL})"
    )
    return {
        "response": response,
        "suggested_actions": ["Show Government Polytechnics", "POLYCET Cutoffs for Computer Engineering", "Compare GPT Masab Tank and Ramanthapur"],
        "matched_colleges": colleges,
        "source": SOURCE_URL
    }

def handle_pharmacy_guidance(msg_lower, branch_code):
    """Provides specific guidance for Pharmacy programmes (B.Pharm, Pharm.D, D.Pharm)."""
    colleges = query_db("""
        SELECT c.id, c.name, c.college_code, c.district, c.institution_type, c.management_type
        FROM colleges c
        WHERE c.primary_category = 'pharmacy'
        ORDER BY c.name ASC
        LIMIT 5
    """)

    names = "\n".join(
        f"• **{college['name']}** — {college['district']} ({college['college_code']})"
        for college in colleges
    ) or "No pharmacy institutions are currently listed."
    response = (
        "### Pharmacy directory\n\n"
        "These names come from the local College Darpan records. This update did not "
        "recheck programme approvals, hospital training, fees, or placements. Confirm "
        "those details with PCI and the current TGEAPCET counselling information.\n\n"
        f"{names}"
    )
    return {
        "response": response,
        "suggested_actions": ["Colleges offering Pharm.D", "B.Pharmacy tuition fees", "Compare Kakatiya Pharmacy and Pulla Reddy"],
        "matched_colleges": colleges,
        "source": "Pharmacy Council of India (PCI) & TGCHE Official Notifications"
    }

def handle_entrance_exams_explanation():
    """Explains differences between TS POLYCET, TS EAPCET, and TS ECET."""
    response = """### Entrance Examinations in Telangana Explained

| Examination | Conducting Body | Target Audience | Destination Programme |
| :--- | :--- | :--- | :--- |
| **TS POLYCET** | SBTET Telangana | **10th Class (SSC)** passouts | **3-Year Diploma in Engineering** & D.Pharm in Polytechnic colleges |
| **TS EAPCET** | JNTUH on behalf of TGCHE | **10+2 / Intermediate (MPC & BiPC)** | **1st Year B.Tech, B.Pharmacy, & Pharm.D** (4 & 6 years) |
| **TS ECET** | Osmania Univ on behalf of TGCHE | **Diploma Holders** | **Lateral Entry directly into 2nd Year B.Tech** (3 years) |
| **GPAT / TS PGECET**| JNTUH / NTA | **B.Pharm / B.Tech graduates** | **M.Pharm & M.Tech** postgraduate degrees |

**Key Advice:**
- Diploma students save one academic year through TS ECET by skipping the 1st year B.Tech curriculum.
- For Pharmacy, Intermediate BiPC students have dedicated reservation quotas in TS EAPCET.
"""
    return {
        "response": response,
        "suggested_actions": ["POLYCET Diploma guidance", "EAPCET B.Tech options", "Pharmacy admission rules"],
        "matched_colleges": [],
        "source": "Telangana State Council of Higher Education (TGCHE)"
    }

def handle_ecet_guidance(branch_code, msg):
    """Provides specific guidance for ECET lateral entry diploma students."""
    colleges = query_db("""
        SELECT DISTINCT c.id, c.name, c.college_code, c.district, c.institution_type,
               b.branch_name, ac.category, ac.admission_year, ac.source_url, ac.cutoff_rank
        FROM colleges c
        JOIN admission_cutoffs ac ON c.id = ac.college_id
        JOIN branches b ON b.id = ac.branch_id
        WHERE ac.exam_name = 'TS ECET' AND ac.category = 'OC_BOYS'
          AND ac.verification_status = 'Verified' AND ac.source_url IS NOT NULL
        ORDER BY ac.cutoff_rank ASC
        LIMIT 6
    """)

    response = (
        "### TS ECET Lateral Entry\n\n"
        "Historical cutoff ranks depend on branch, category, gender, and counselling round. "
        "The records below are from the local database; use them only when the source and year are shown. "
        "I do not estimate current admission chances.\n\n"
    )
    response += "\n".join(
        f"• **{row['name']}**, {row['branch_name']}, {row['category']}: historical rank {row['cutoff_rank']} ({row['admission_year']}); [source]({row['source_url']})"
        for row in colleges if row.get("source_url")
    ) or "No source-linked TS ECET cutoff entries are available in the database."
    return {
        "response": response,
        "suggested_actions": ["Run AI Recommendation with my ECET rank", "Compare OUCE and CBIT", "How are cutoffs determined?"],
        "matched_colleges": colleges,
        "source": "TS ECET Convener Counselling Records & TGCHE"
    }

def handle_decision_factors():
    """Educational advice on what factors to prioritize."""
    response = """### Key Factors When Choosing an Institution in Telangana

1. Confirm the institution's current approval and affiliation from the relevant regulator or university.
2. Compare total costs using current official fee notices; do not assume transport or other charges are included.
3. Compare placement disclosures only when the academic year, denominator, and source are available.
4. Check programme names, approved intake, admission route, and current counselling notices before applying.
"""
    return {
        "response": response,
        "suggested_actions": ["Start AI Recommendation", "Colleges under ₹1.0 Lakh", "Show Data Verification Standards"],
        "matched_colleges": [],
        "source": "Academic & Admissions Guidance Best Practices"
    }

def handle_verification_inquiry():
    """Explains which fields are verified and which still need review."""
    counts = query_db("""
        SELECT verification_status, COUNT(*) AS count FROM colleges
        GROUP BY verification_status ORDER BY verification_status
    """)
    counts_text = "\n".join(f"• {row['verification_status']}: {row['count']} institution records" for row in counts)
    response = (
        "### Source and verification notes\n\n"
        "A verified badge on a new directory entry confirms its name is present in the "
        "linked official list for the displayed academic year. It does not verify fees, "
        "branches, hostel, cutoffs, or placements. Those need their own source and year.\n\n"
        "Existing imported records retain their previous status and should be checked "
        "against current primary sources before using them for decisions. Missing values "
        "are shown as unavailable rather than estimated.\n\n"
        f"Current institution status counts:\n{counts_text}\n\n"
        f"[SBTET 2026–27 directory source]({SOURCE_URL})"
    )
    return {
        "response": response,
        "suggested_actions": ["Explore All Colleges", "Open College Profile", "How does recommendation scoring work?"],
        "matched_colleges": [],
        "source": "College Darpan Transparency Engine"
    }

def handle_branch_query(branch_code, branch_name, category, msg_lower):
    """Retrieves colleges offering the specified engineering, diploma, or pharmacy course."""
    districts = query_db(
        "SELECT DISTINCT district FROM colleges WHERE district IS NOT NULL "
        "ORDER BY LENGTH(district) DESC"
    )
    district = next(
        (row["district"] for row in districts if row["district"].strip().lower() in msg_lower),
        None,
    )
    sql = """
        SELECT DISTINCT c.id, c.name, c.college_code, c.district, c.institution_type, c.primary_category
        FROM colleges c
        JOIN branches b ON c.id = b.college_id
        WHERE (b.branch_code = ? OR b.branch_name LIKE ? OR b.course_name LIKE ?)
          AND b.verification_status = 'Verified' AND b.source LIKE 'http%'
    """
    params = [branch_code, f"%{branch_name}%", f"%{branch_name}%"]

    if category:
        sql += " AND c.primary_category = ?"
        params.append(category)
    if district:
        sql += " AND lower(c.district) = lower(?)"
        params.append(district)

    sql += " ORDER BY c.name ASC LIMIT 6"

    colleges = query_db(sql, params)

    if not colleges:
        legacy_sql = """
            SELECT DISTINCT c.id, c.name, c.college_code, c.district,
                            b.academic_year, b.source
            FROM colleges c
            JOIN branches b ON c.id = b.college_id
            WHERE (b.branch_code = ? OR b.branch_name LIKE ? OR b.course_name LIKE ?)
        """
        legacy_params = [branch_code, f"%{branch_name}%", f"%{branch_name}%"]
        if category:
            legacy_sql += " AND c.primary_category = ?"
            legacy_params.append(category)
        if district:
            legacy_sql += " AND lower(c.district) = lower(?)"
            legacy_params.append(district)
        legacy_sql += " ORDER BY c.name ASC LIMIT 6"
        legacy_rows = query_db(legacy_sql, legacy_params)
        if legacy_rows:
            response = (
                f"The local directory has older records matching **{branch_name}** ({branch_code}), "
                "but those programme rows do not include a direct source URL. Treat them as "
                "historical leads, not confirmation of a current offering:\n\n"
            )
            response += "\n".join(
                f"• **{row['name']}** ({row['college_code']}) — {row['district']}; year: {row.get('academic_year') or 'not recorded'}; needs current verification"
                for row in legacy_rows
            )
            return {
                "response": response,
                "suggested_actions": ["Open the college directory", "Check current official counselling list", "Ask about source verification"],
                "matched_colleges": legacy_rows,
                "source": "College Darpan legacy programme rows"
            }
        return {
            "response": f"I couldn't find a source-linked current listing for '{branch_name}'. Please check the current official counselling list or search the directory.",
            "suggested_actions": ["Show all engineering branches", "Reset filters"],
            "matched_colleges": [],
            "source": "College Darpan Database"
        }

    response = f"### Institutions Offering {branch_name} ({branch_code})\n\n"
    response += f"Found **{len(colleges)} directory records** matching this programme:\n\n"
    for col in colleges:
        response += f"• **{col['name']}** ({col['college_code']}) — *{col['district']}*\n"

    return {
        "response": response,
        "suggested_actions": [f"Compare top {branch_code} colleges", "Start AI Recommendation", "Check Cutoffs"],
        "matched_colleges": colleges,
        "source": "College Darpan Database"
    }

def handle_budget_query(budget, msg_lower):
    """Filters colleges within budget across categories."""
    if budget is None:
        return {
            "response": "Tell me your maximum annual tuition budget (for example, “under ₹80,000”). I will only include fee rows marked verified with a source link.",
            "suggested_actions": ["Show source-linked fees", "Browse colleges", "How is data verified?"],
            "matched_colleges": [],
            "source": "College Darpan database"
        }
    target_budget = budget

    colleges = query_db("""
        SELECT c.id, c.name, c.college_code, c.district, c.institution_type, c.primary_category,
               m.annual_tuition_fee, m.placement_percentage, m.average_package,
               m.academic_year, m.source_url, m.verification_status AS metric_status
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE m.annual_tuition_fee IS NOT NULL AND m.annual_tuition_fee <= ?
          AND m.verification_status = 'Verified' AND m.source_url IS NOT NULL
          AND m.academic_year IS NOT NULL
        ORDER BY m.annual_tuition_fee ASC
        LIMIT 6
    """, [target_budget])

    response = f"### Institutions with a recorded annual tuition fee at or below ₹{target_budget:,}\n\n"
    response += "Only database fee rows marked verified and carrying a source URL are included. Values may be from the academic year shown; check the source for current applicability.\n\n"

    for col in colleges:
        fee = int(col['annual_tuition_fee'])
        cat_badge = col['primary_category'].capitalize()
        response += f"• **{col['name']}** ({col['college_code']}) — **₹{fee:,} / year** [{cat_badge}] ({col['district']}); year: {col.get('academic_year') or 'not recorded'}; [source]({col['source_url']})\n"
    if not colleges:
        response += "No fee record meeting those source and verification requirements was found."

    return {
        "response": response,
        "suggested_actions": ["Colleges with high placements", "Explain Telangana fee reimbursement", "Open recommendation form"],
        "matched_colleges": colleges,
        "source": "TAFRC & SBTET Official Orders"
    }

def handle_single_college(college_code):
    """Details about a single college."""
    col = query_db("""
        SELECT c.*, m.annual_tuition_fee, m.other_fees, m.placement_percentage,
               m.average_package, m.highest_package, m.top_recruiters,
               m.faculty_information, m.infrastructure_information,
               m.source_url AS metrics_source_url,
               m.verification_status AS metrics_verification_status,
               m.academic_year AS metrics_year
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE c.college_code = ?
    """, [college_code], one=True)

    if not col:
        return {
            "response": f"I couldn't find records for institution code **{college_code}**. Please check the directory.",
            "suggested_actions": ["Browse College Directory", "Search colleges"],
            "matched_colleges": [],
            "source": "College Darpan Database"
        }

    branches = query_db("SELECT branch_name, branch_code, degree_level FROM branches WHERE college_id = ?", [col["id"]])
    branch_list = ", ".join([f"{b['branch_code']} ({b['degree_level']})" for b in branches])

    metrics_verified = col.get("metrics_verification_status") == "Verified" and col.get("metrics_source_url") and col.get("metrics_year")
    fee_str = f"₹{int(col['annual_tuition_fee']):,} / year" if col.get("annual_tuition_fee") and metrics_verified else "Not verified"
    pct_str = f"{col['placement_percentage']}%" if col.get("placement_percentage") is not None and metrics_verified else "Not verified"
    avg_str = f"{col['average_package']} LPA" if col.get("average_package") and metrics_verified else "Not verified"
    hostel_str = "Listed" if col.get("hostel_available") == 1 else "Not listed"

    response = f"""### {col['name']} ({col['college_code']})

**Category:** {col['primary_category'].capitalize()} | **Management:** {col['management_type']}  
**Location:** {col['address']}  
**Hostel:** {hostel_str} | **Approval:** {col.get('approval_body') or 'Not listed'}

**Key Numbers:**
• **Annual Tuition Fee:** {fee_str}
• **Placement Rate:** {pct_str} | **Average Package:** {avg_str}
• **Top Recruiters:** {col.get('top_recruiters') if metrics_verified and col.get('top_recruiters') else 'Not verified'}

**Programmes Offered:** {branch_list}

**Infrastructure & Campus:**
{col.get('infrastructure_information') or col.get('description') or 'Not in the database'}
"""
    return {
        "response": response,
        "suggested_actions": [f"View full profile for {col['college_code']}", f"Compare {col['college_code']} with others", "Check cutoff ranks"],
        "matched_colleges": [col],
        "source": col.get("metrics_source_url") if metrics_verified else (col.get("source_url") or "College Darpan local database")
    }

def handle_placements_query():
    """Lists only placement records carrying a source and a verified status."""
    colleges = query_db("""
        SELECT c.id, c.name, c.college_code, c.district, c.institution_type, c.primary_category,
               m.annual_tuition_fee, m.placement_percentage, m.average_package, m.highest_package,
               m.academic_year, m.source_url
        FROM colleges c
        JOIN college_metrics m ON c.id = m.college_id
        WHERE m.placement_percentage IS NOT NULL
          AND m.verification_status = 'Verified' AND m.source_url IS NOT NULL
          AND m.academic_year IS NOT NULL
        ORDER BY m.average_package DESC, m.placement_percentage DESC
        LIMIT 5
    """)

    response = "### Placement records with source links\n\n"
    response += "Only rows marked verified and carrying a source URL are included. Check the year and original disclosure; placement figures are not directly comparable across institutions.\n\n"
    for col in colleges:
        cat = col['primary_category'].capitalize()
        response += f"• **{col['name']}** ({col['college_code']}) [{cat}]: {col.get('placement_percentage') if col.get('placement_percentage') is not None else 'not recorded'}% reported; average package: {col.get('average_package') or 'not recorded'} LPA; year: {col.get('academic_year') or 'not recorded'}; [source]({col['source_url']})\n"
    if not colleges:
        response += "No placement record met both the verification and source URL checks."

    return {
        "response": response,
        "suggested_actions": ["Compare top colleges", "Check fees for these colleges", "Start recommendation"],
        "matched_colleges": colleges,
        "source": "College Darpan database placement records"
    }

def handle_general_search(query_text):
    """Fallback handler searching database for any mentions."""
    colleges = query_db("""
        SELECT c.id, c.name, c.college_code, c.district, c.institution_type, c.primary_category,
               m.annual_tuition_fee, m.placement_percentage, m.average_package
        FROM colleges c
        LEFT JOIN college_metrics m ON c.id = m.college_id
        WHERE c.name LIKE ? OR c.description LIKE ? OR c.district LIKE ?
        LIMIT 4
    """, [f"%{query_text}%", f"%{query_text}%", f"%{query_text}%"])

    if colleges:
        response = f"I found **{len(colleges)} institutions** related to your query '{query_text}':\n\n"
        for col in colleges:
            cat = col['primary_category'].capitalize()
            response += f"• **{col['name']}** ({col['college_code']}) in {col['district']} [{cat}]\n"
        response += "\nWould you like more details on any of these or a side-by-side comparison?"
    else:
        response = (
            f"I searched our Telangana database for *'{query_text}'*, but could not find a direct match. "
            "You can ask about:\n"
            "• **Polytechnic:** *'Government polytechnics offering Computer Engineering'*\n"
            "• **Engineering:** *'Which colleges offer AIML in Hyderabad?'*\n"
            "• **Pharmacy:** *'Colleges offering Pharm.D or B.Pharmacy'*\n"
            "• **Comparisons:** *'Compare OUCE and CBIT'* or *'Compare GPT Masab Tank and Ramanthapur'*."
        )

    return {
        "response": response,
        "suggested_actions": ["Polytechnic Colleges", "Engineering Colleges", "Pharmacy Colleges", "Compare OUCE and CBIT"],
        "matched_colleges": colleges,
        "source": "College Darpan Rule-Based Assistant"
    }
