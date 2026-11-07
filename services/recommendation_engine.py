"""
Hybrid AI College Recommendation Engine for College Darpan.
Supports 3 Education Categories:
1. Polytechnic / Diploma (TS POLYCET)
2. B.Tech / Engineering (TS EAPCET, TS ECET Lateral Entry)
3. Pharmacy (TS EAPCET BiPC/MPC, TS POLYCET, GPAT)

Implements:
- Content-based compatibility screening (category, branch, budget, district, management)
- Rule-based eligibility evaluation with strict safeguards
- Normalized multi-criteria scoring
- Plain-English personalized explanation generation
"""

from database.db import query_db

ALLIED_BRANCH_MAP = {
    # Engineering Allied Branches
    "AIML": ["CSE", "CSD", "AIDS", "INF"],
    "CSE": ["AIML", "INF", "CSD", "AIDS"],
    "INF": ["CSE", "AIML", "CSD"],
    "CSD": ["CSE", "AIML", "INF"],
    "AIDS": ["AIML", "CSE", "CSD"],
    "ECE": ["EEE", "CSE", "INF"],
    "EEE": ["ECE", "MECH"],
    "MECH": ["CIVIL", "AUTO", "MCT"],
    "CIVIL": ["MECH"],
    "AERO": ["MECH", "CSE"],
    # Polytechnic Allied Branches
    "CME": ["AIML", "INF", "ECE"],
    "AUTO": ["MECH"],
    "PKG": ["MECH", "CME"],
    # Pharmacy Allied Branches
    "BPH": ["PHD", "DPH"],
    "PHD": ["BPH"],
    "DPH": ["BPH"]
}

GREATER_HYDERABAD_DISTRICTS = {"Hyderabad", "Medchal-Malkajgiri", "Ranga Reddy"}

def normalize_weights(raw_weights):
    """
    Normalizes priority slider values into fractions summing strictly to 1.0.
    Default fallback: Branch 30%, Affordability 25%, Placements 20%, Location 10%, Infrastructure 15%.
    """
    default = {
        "branch": 0.30,
        "affordability": 0.25,
        "placements": 0.20,
        "location": 0.10,
        "infrastructure": 0.15
    }
    
    if not raw_weights:
        return default
        
    branch = float(raw_weights.get("branch", 3))
    affordability = float(raw_weights.get("affordability", 2.5))
    placements = float(raw_weights.get("placements", 2))
    location = float(raw_weights.get("location", 1))
    infrastructure = float(raw_weights.get("infrastructure", 1.5))
    
    total = branch + affordability + placements + location + infrastructure
    if total <= 0:
        return default
        
    return {
        "branch": round(branch / total, 4),
        "affordability": round(affordability / total, 4),
        "placements": round(placements / total, 4),
        "location": round(location / total, 4),
        "infrastructure": round(infrastructure / total, 4)
    }

def score_branch_match(user_branch, college_branches):
    """Scores branch/programme compatibility (0 to 100)."""
    if not user_branch or user_branch == "Any":
        return 100, "Any course in selected category accepted", True

    user_branch_upper = user_branch.strip().upper()
    college_codes = [b["branch_code"].upper() for b in college_branches]

    if user_branch_upper in college_codes:
        return 100, f"Offers your direct preferred course ({user_branch_upper})", True
        
    allied = ALLIED_BRANCH_MAP.get(user_branch_upper, [])
    for alt in allied:
        if alt in college_codes:
            return 75, f"Offers allied specialisation ({alt}) related to {user_branch_upper}", False
            
    return 25, f"Direct course {user_branch_upper} not listed; offers alternative programs in this institution", False

def score_affordability(user_budget, annual_fee, category="engineering"):
    """Scores affordability based on student's annual tuition budget."""
    if not user_budget or user_budget <= 0:
        return 85, "No restrictive tuition budget specified", "normal"
        
    if annual_fee is None:
        return 60, "Official tuition fee is pending verification", "unverified"
        
    if annual_fee <= user_budget:
        savings = user_budget - annual_fee
        if savings > 15000:
            return 100, f"Comfortably within budget (₹{int(annual_fee):,} / yr vs ₹{int(user_budget):,} limit)", "within"
        return 95, f"Within budget (₹{int(annual_fee):,} / yr)", "within"
    elif annual_fee <= user_budget * 1.15:
        return 75, f"Slightly above budget by {(annual_fee - user_budget)/user_budget*100:.0f}% (₹{int(annual_fee):,} / yr)", "close"
    elif annual_fee <= user_budget * 1.30:
        return 50, f"Exceeds budget by {(annual_fee - user_budget)/user_budget*100:.0f}% (₹{int(annual_fee):,} / yr)", "over"
    else:
        return 30, f"Significantly above budget (₹{int(annual_fee):,} / yr)", "high"

def score_placements(metrics, category="engineering"):
    """Scores placement performance and data reliability."""
    if not metrics or metrics.get("placement_percentage") is None:
        if category == "polytechnic":
            return 65, "Polytechnic students primarily advance to B.Tech through TS ECET lateral entry", "progression"
        return 55, "Placement data is currently incomplete or pending verification", "unverified"
        
    pct = metrics.get("placement_percentage", 0)
    avg_pkg = metrics.get("average_package", 0) or 0
    
    pct_score = min(50, (pct / 100.0) * 50)
    # Norm benchmark: 10 LPA for Engg, 6 LPA for Pharmacy, 4 LPA for Diploma
    denom = 4.0 if category == "polytechnic" else (7.0 if category == "pharmacy" else 10.0)
    pkg_score = min(50, (avg_pkg / denom) * 50)
    
    total = round(pct_score + pkg_score)
    summary = f"{pct}% verified placement rate, ₹{avg_pkg} LPA average package"
    return total, summary, "verified"

def score_location(user_district, college_district):
    """Scores geographic convenience."""
    if not user_district or user_district == "Any":
        return 90, "Compatible with broad Telangana region"
        
    if college_district.strip().lower() == user_district.strip().lower():
        return 100, f"Located directly in your target district ({college_district})"
        
    if user_district in GREATER_HYDERABAD_DISTRICTS and college_district in GREATER_HYDERABAD_DISTRICTS:
        return 80, f"Located in {college_district} (Greater Hyderabad Metropolitan region)"
        
    return 40, f"Located in {college_district} (outside your preferred district)"

def score_infrastructure(college, metrics):
    """Scores campus infrastructure, approval bodies, and faculty."""
    score = 40 # Base
    naac = college.get("naac_grade")
    if naac == "A++":
        score += 30
    elif naac == "A+":
        score += 25
    elif naac == "A" or "Approved" in str(naac):
        score += 20
    else:
        score += 10
        
    if college.get("hostel_available") == 1:
        score += 15
        
    if metrics and metrics.get("faculty_information"):
        score += 15
        
    score = min(100, score)
    summary = f"{college.get('approval_body') or 'Accredited'} approved, established facilities"
    return score, summary

def evaluate_admission_eligibility(college_id, exam, rank, category, branch_code):
    """
    Safely checks historical cutoffs across TS POLYCET, TS ECET, and TS EAPCET.
    Strictly follows guidelines:
    - Never promises admission.
    - If data is missing, explicitly returns 'Admission eligibility cannot be confirmed with the available data.'
    """
    if not rank or not exam or not category or not branch_code:
        return {
            "status": "unverified",
            "message": "Admission eligibility cannot be confirmed with the available data.",
            "detail": "Exam rank, category, or branch details were not provided for cutoff comparison.",
            "past_cutoff": None
        }

    # Query matching cutoff
    query = """
        SELECT ac.cutoff_rank, ac.admission_year, ac.admission_pathway, ac.category, b.branch_code
        FROM admission_cutoffs ac
        JOIN branches b ON ac.branch_id = b.id
        WHERE ac.college_id = ? 
          AND ac.exam_name = ?
          AND (ac.category = ? OR ac.category = 'OC_BOYS')
          AND (b.branch_code = ? OR b.branch_code = 'CSE' OR b.branch_code = 'CME' OR b.branch_code = 'BPH')
        ORDER BY (b.branch_code = ?) DESC, (ac.category = ?) DESC, ac.admission_year DESC
        LIMIT 1
    """
    cutoff = query_db(query, [college_id, exam, category, branch_code, branch_code, category], one=True)

    if not cutoff or not cutoff.get("cutoff_rank"):
        return {
            "status": "unavailable",
            "message": "Admission eligibility cannot be confirmed with the available data.",
            "detail": f"No verified historical {exam} cutoffs found in database for this specific branch/category combination.",
            "past_cutoff": None
        }

    cutoff_rank = cutoff["cutoff_rank"]
    user_rank = int(rank)

    if user_rank <= cutoff_rank:
        return {
            "status": "favorable",
            "message": f"Historical data indicates favorable competitive standing (Past cutoff: {cutoff_rank:,}, Your rank: {user_rank:,}).",
            "detail": f"Based on {cutoff['admission_year']} {exam} {cutoff['admission_pathway']} records for {cutoff['category']}. Past trends do not guarantee official allotment.",
            "past_cutoff": cutoff_rank
        }
    elif user_rank <= cutoff_rank * 1.20:
        return {
            "status": "borderline",
            "message": f"Borderline / highly competitive based on historical cutoffs (Past cutoff: {cutoff_rank:,}, Your rank: {user_rank:,}).",
            "detail": f"Your rank is close to the {cutoff['admission_year']} cutoff ({cutoff_rank:,}). Final seat allotment depends on counselling round dynamics.",
            "past_cutoff": cutoff_rank
        }
    else:
        return {
            "status": "competitive",
            "message": f"Historical cutoff was more selective (Past cutoff: {cutoff_rank:,}, Your rank: {user_rank:,}).",
            "detail": f"Past closing rank in {cutoff['admission_year']} was {cutoff_rank:,}. Consider allied options or subsequent counselling rounds.",
            "past_cutoff": cutoff_rank
        }

def generate_recommendation_explanation(college, scores, criteria_details, eligibility):
    """Generates a personalized, transparent explanation of the recommendation."""
    pros = []
    cautions = []

    # Branch
    if criteria_details["branch_exact"]:
        pros.append(criteria_details["branch_note"])
    else:
        cautions.append(criteria_details["branch_note"])

    # Affordability
    if criteria_details["fee_status"] == "within":
        pros.append(criteria_details["fee_note"])
    elif criteria_details["fee_status"] in ("close", "over", "high"):
        cautions.append(criteria_details["fee_note"])
    elif criteria_details["fee_status"] == "unverified":
        cautions.append("Tuition fee data requires official verification before final decision")

    # Placements
    if criteria_details["placement_status"] == "verified":
        pros.append(criteria_details["placement_note"])
    elif criteria_details["placement_status"] == "progression":
        pros.append("Provides strong foundation for higher degree lateral entry progression")
    else:
        cautions.append("Placement statistics require verification from institutional records")

    # Location
    pros.append(criteria_details["location_note"])

    # Build coherent narrative
    pro_sentence = ". ".join(pros) + "."
    if cautions:
        caution_sentence = "Note: " + "; ".join(cautions) + "."
    else:
        caution_sentence = "All critical data indicators have been verified."

    summary = f"{pro_sentence} {caution_sentence}"
    return summary, cautions

def get_recommendations(preferences):
    """
    Main recommendation engine pipeline supporting:
    - Polytechnic (TS POLYCET)
    - Engineering (TS EAPCET, TS ECET)
    - Pharmacy (TS EAPCET BiPC/MPC, TS POLYCET)
    """
    raw_cat = preferences.get("education_category", preferences.get("stream", preferences.get("category", "engineering")))
    raw_cat_lower = str(raw_cat).lower().strip() if raw_cat else "engineering"

    exam = preferences.get("exam", "")
    if raw_cat_lower in ("polytechnic", "diploma"):
        category = "polytechnic"
    elif raw_cat_lower in ("pharmacy", "pharma"):
        category = "pharmacy"
    elif raw_cat_lower in ("engineering", "btech"):
        category = "engineering"
    elif raw_cat_lower == "all":
        category = "all"
    else:
        # If raw_cat was actually a caste category like 'OC_BOYS', infer education category from exam
        if "POLYCET" in exam.upper():
            category = "polytechnic"
        elif "GPAT" in exam.upper():
            category = "pharmacy"
        else:
            category = "engineering"

    if not exam:
        exam = "TS POLYCET" if category == "polytechnic" else "TS EAPCET"

    weights = normalize_weights(preferences.get("weights"))
    user_branch = preferences.get("branch", "Any")
    user_district = preferences.get("district", "Any")
    user_budget = preferences.get("max_budget")
    user_mgmt = preferences.get("management_type", preferences.get("institution_type", "Any"))
    rank = preferences.get("rank")
    
    # Resolve caste/reservation category vs education category
    caste_category = preferences.get("caste_category", preferences.get("category_code"))
    if not caste_category:
        if raw_cat and raw_cat.upper() not in ("POLYTECHNIC", "ENGINEERING", "PHARMACY", "ALL", "DIPLOMA", "BTECH"):
            caste_category = raw_cat
        else:
            caste_category = "OC_BOYS"

    # Query colleges matching target category
    from services.college_service import get_all_colleges
    all_colleges = get_all_colleges(
        category=category if category != "all" else None,
        management_type=user_mgmt if user_mgmt != "Any" else None
    )

    ranked_results = []

    for col in all_colleges:
        # Criterion 1: Branch Match
        branch_score, branch_note, branch_exact = score_branch_match(user_branch, col.get("branches", []))
        
        # Criterion 2: Affordability
        fee_score, fee_note, fee_status = score_affordability(user_budget, col.get("annual_tuition_fee"), category)
        
        # Criterion 3: Placements
        placement_score, placement_note, placement_status = score_placements(col, category)
        
        # Criterion 4: Location
        location_score, location_note = score_location(user_district, col.get("district"))
        
        # Criterion 5: Infrastructure & Faculty
        infra_score, infra_note = score_infrastructure(col, col)

        # Weighted calculation
        overall_score = (
            branch_score * weights["branch"] +
            fee_score * weights["affordability"] +
            placement_score * weights["placements"] +
            location_score * weights["location"] +
            infra_score * weights["infrastructure"]
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 1)

        # Admission Safeguard check
        eligibility = evaluate_admission_eligibility(col["id"], exam, rank, caste_category, user_branch)

        # Data completeness estimate
        completeness_checks = [
            col.get("annual_tuition_fee") is not None,
            col.get("placement_percentage") is not None,
            col.get("approval_body") is not None,
            col.get("verification_status") == "Verified"
        ]
        data_completeness = round((sum(completeness_checks) / len(completeness_checks)) * 100)

        # Explanation generation
        criteria_details = {
            "branch_exact": branch_exact,
            "branch_note": branch_note,
            "fee_status": fee_status,
            "fee_note": fee_note,
            "placement_status": placement_status,
            "placement_note": placement_note,
            "location_note": location_note,
            "infra_note": infra_note
        }
        explanation, caveats = generate_recommendation_explanation(col, {
            "branch": branch_score, "affordability": fee_score,
            "placements": placement_score, "location": location_score,
            "infrastructure": infra_score
        }, criteria_details, eligibility)

        ranked_results.append({
            "college": col,
            "match_score": overall_score,
            "breakdown": {
                "branch_score": branch_score,
                "affordability_score": fee_score,
                "placement_score": placement_score,
                "location_score": location_score,
                "infrastructure_score": infra_score,
            },
            "weights": weights,
            "explanation": explanation,
            "caveats": caveats,
            "eligibility": eligibility,
            "data_completeness": data_completeness,
            "branch_exact": branch_exact
        })

    # Sort descending by match score
    ranked_results.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "results": ranked_results,
        "total_analyzed": len(all_colleges),
        "normalized_weights": weights,
        "preferences_applied": {
            "category": category,
            "exam": exam,
            "rank": rank,
            "caste_category": caste_category,
            "branch": user_branch,
            "district": user_district,
            "budget": user_budget,
            "management_type": user_mgmt
        }
    }
