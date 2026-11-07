"""
College Darpan — AI-Powered Education Discovery & Recommendation Platform
Flask Main Application Entry Point
Supports: Polytechnic / Diploma, B.Tech / Engineering, and Pharmacy in Telangana
"""

import os
import math
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from config import Config
from database.db import get_db_connection
from database.init_db import initialize_database
from database.import_sbtet_directory import import_directory as import_sbtet_directory
from services.college_service import (
    get_quick_statistics, get_districts, get_institution_types, 
    get_management_types, get_unique_branches, get_all_colleges, 
    get_college_by_id, compare_colleges
)
from services.recommendation_engine import get_recommendations
from services.chatbot_service import process_chat_message

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

def prepare_database():
    """Initialize/update the configured database when running the web app directly."""
    if not os.path.exists(Config.DATABASE_PATH):
        print("[Startup] Database not detected. Auto-initializing database...")
        initialize_database()

    # Idempotent, additive data update: preserves all existing records and metrics.
    import_sbtet_directory()

# Context processor for shared template variables
@app.context_processor
def inject_global_data():
    selected_ids = session.get("compare_ids", [])
    return {
        "platform_name": Config.PLATFORM_NAME,
        "tagline": Config.TAGLINE,
        "state": Config.STATE,
        "compare_count": len(selected_ids) if isinstance(selected_ids, list) else 0,
    }


def _parse_recommendation_preferences(data, from_form=False):
    """Validate recommendation inputs shared by the HTML form and JSON API."""
    valid_categories = {"OC_BOYS", "OC_GIRLS", "BC_A", "BC_B", "BC_C", "BC_D", "BC_E", "SC", "ST", "EWS"}
    raw_category = str(data.get("category") or "engineering").strip()
    legacy_caste_category = from_form and raw_category in valid_categories
    category = "engineering" if legacy_caste_category else raw_category.lower()
    if category not in {"engineering", "polytechnic", "pharmacy", "all"}:
        raise ValueError("Choose a supported education category.")

    default_exam = "TS POLYCET" if category == "polytechnic" else "TS EAPCET"
    exam = str(data.get("exam") or default_exam).strip()
    if exam not in {"TS POLYCET", "TS ECET", "TS EAPCET", "GPAT", "TS PGECET"}:
        raise ValueError("Choose a supported entrance examination.")

    rank_raw = data.get("rank")
    rank = None
    if rank_raw not in (None, ""):
        rank_text = str(rank_raw).strip()
        if not rank_text.isdecimal():
            raise ValueError("Rank must be a whole number from 1 to 200,000.")
        rank = int(rank_text)
        if not 1 <= rank <= 200000:
            raise ValueError("Rank must be between 1 and 200,000.")

    budget_raw = data.get("max_budget")
    budget = None
    if budget_raw not in (None, ""):
        if isinstance(budget_raw, bool):
            raise ValueError("Maximum budget must be a valid positive amount.")
        try:
            budget = float(budget_raw)
        except (TypeError, ValueError):
            raise ValueError("Maximum budget must be a valid positive amount.")
        if not math.isfinite(budget) or not 1 <= budget <= 10000000:
            raise ValueError("Maximum budget must be between ₹1 and ₹10,000,000.")

    caste_category = str(data.get("caste_category") or (raw_category if legacy_caste_category else "OC_BOYS")).strip()
    if caste_category not in valid_categories:
        raise ValueError("Choose a supported reservation category.")

    branch = str(data.get("branch") or "Any").strip()
    district = str(data.get("district") or "Any").strip()
    management_type = str(data.get("management_type") or data.get("institution_type") or "Any").strip()
    if not branch or len(branch) > 40 or not district or len(district) > 100 or len(management_type) > 80:
        raise ValueError("Branch, district, or institution preference is invalid.")

    raw_weights = data.get("weights", {})
    if raw_weights is None:
        raw_weights = {}
    if not isinstance(raw_weights, dict):
        raise ValueError("Weights must be an object of values from 1 to 5.")
    if from_form:
        raw_weights = {
            "branch": data.get("w_branch", 3),
            "affordability": data.get("w_fee", 2.5),
            "placements": data.get("w_placements", 2),
            "location": data.get("w_location", 1),
            "infrastructure": data.get("w_infra", 1.5),
        }
    weights = {}
    for name in ("branch", "affordability", "placements", "location", "infrastructure"):
        raw_value = raw_weights.get(name)
        if raw_value is None:
            continue
        if isinstance(raw_value, bool):
            raise ValueError("Each recommendation weight must be a number from 1 to 5.")
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            raise ValueError("Each recommendation weight must be a number from 1 to 5.")
        if not math.isfinite(value) or not 1 <= value <= 5:
            raise ValueError("Each recommendation weight must be from 1 to 5.")
        weights[name] = value

    return {
        "category": category,
        "exam": exam,
        "rank": rank,
        "caste_category": caste_category,
        "branch": branch,
        "district": district,
        "max_budget": budget,
        "management_type": management_type,
        "weights": weights,
    }


def _parse_college_id(value):
    if isinstance(value, bool):
        return None
    text = str(value).strip()
    if not text.isdecimal():
        return None
    college_id = int(text)
    return college_id if college_id > 0 else None


def _valid_compare_ids(values):
    """Keep only distinct, positive IDs backed by a current college record."""
    if not isinstance(values, list):
        return []
    result = []
    for value in values:
        college_id = _parse_college_id(value)
        if college_id and college_id not in result and get_college_by_id(college_id):
            result.append(college_id)
        if len(result) == 4:
            break
    return result


def _current_compare_ids():
    ids = session.get("compare_ids", [])
    if not isinstance(ids, list):
        session["compare_ids"] = []
        return []
    valid_ids = _valid_compare_ids(ids)
    if valid_ids != ids:
        session["compare_ids"] = valid_ids
    return valid_ids


def _compare_response():
    selected_ids = _current_compare_ids()
    colleges = compare_colleges(selected_ids)
    return {"success": True, "selected_ids": selected_ids, "count": len(selected_ids), "colleges": colleges}

# ----------------- WEB ROUTES ----------------- #

@app.route("/")
def index():
    """Home landing page with hero, education category selector, live statistics, and featured institutions."""
    stats = get_quick_statistics()
    featured_colleges = get_all_colleges(sort_by="placement_desc")[:6]
    districts = get_districts()
    branches = get_unique_branches()
    return render_template(
        "index.html",
        stats=stats,
        featured_colleges=featured_colleges,
        districts=districts,
        branches=branches
    )

@app.route("/colleges")
def colleges_directory():
    """Unified directory with category tabs, search, multi-criteria filtering, and sorting."""
    category = request.args.get("category", "All").strip()
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All")
    branch = request.args.get("branch", "All")
    institution_type = request.args.get("institution_type", "All")
    management_type = request.args.get("management_type", "All")
    max_fee = request.args.get("max_fee", "").strip()
    verified_only = request.args.get("verified_only") == "true"
    hostel_only = request.args.get("hostel_only") == "true"
    pathway = request.args.get("pathway", "All")
    sort_by = request.args.get("sort_by", "name_asc")

    colleges = get_all_colleges(
        category=category,
        search=search,
        district=district,
        branch=branch,
        institution_type=institution_type,
        management_type=management_type,
        max_fee=max_fee if max_fee else None,
        verified_placements_only=verified_only,
        hostel_only=hostel_only,
        pathway=pathway,
        sort_by=sort_by
    )

    stats = get_quick_statistics()
    districts = get_districts(category=category if category != "All" else None)
    branches = get_unique_branches(category=category if category != "All" else None)
    types = get_institution_types(category=category if category != "All" else None)
    mgmt_types = get_management_types()

    return render_template(
        "colleges.html",
        colleges=colleges,
        total_count=len(colleges),
        stats=stats,
        districts=districts,
        branches=branches,
        types=types,
        mgmt_types=mgmt_types,
        active_filters={
            "category": category,
            "search": search,
            "district": district,
            "branch": branch,
            "institution_type": institution_type,
            "management_type": management_type,
            "max_fee": max_fee,
            "verified_only": verified_only,
            "hostel_only": hostel_only,
            "pathway": pathway,
            "sort_by": sort_by
        }
    )

@app.route("/polytechnic")
def polytechnic_page():
    """Dedicated discovery experience for Polytechnic / Diploma colleges (TS POLYCET)."""
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All")
    branch = request.args.get("branch", "All")
    management_type = request.args.get("management_type", "All")
    max_fee = request.args.get("max_fee", "").strip()

    colleges = get_all_colleges(
        category="polytechnic",
        search=search,
        district=district,
        branch=branch,
        management_type=management_type,
        max_fee=max_fee if max_fee else None
    )

    districts = get_districts(category="polytechnic")
    branches = get_unique_branches(category="polytechnic")
    mgmt_types = ["Government", "Private Aided", "Private Unaided"]

    return render_template(
        "polytechnic.html",
        colleges=colleges,
        total_count=len(colleges),
        districts=districts,
        branches=branches,
        mgmt_types=mgmt_types,
        active_filters={
            "search": search,
            "district": district,
            "branch": branch,
            "management_type": management_type,
            "max_fee": max_fee
        }
    )

@app.route("/engineering")
def engineering_page():
    """Dedicated discovery experience for B.Tech / Engineering colleges (TS EAPCET / TS ECET)."""
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All")
    branch = request.args.get("branch", "All")
    management_type = request.args.get("management_type", "All")
    max_fee = request.args.get("max_fee", "").strip()

    colleges = get_all_colleges(
        category="engineering",
        search=search,
        district=district,
        branch=branch,
        management_type=management_type,
        max_fee=max_fee if max_fee else None
    )

    districts = get_districts(category="engineering")
    branches = get_unique_branches(category="engineering")
    mgmt_types = ["University", "Private Unaided"]

    return render_template(
        "engineering.html",
        colleges=colleges,
        total_count=len(colleges),
        districts=districts,
        branches=branches,
        mgmt_types=mgmt_types,
        active_filters={
            "search": search,
            "district": district,
            "branch": branch,
            "management_type": management_type,
            "max_fee": max_fee
        }
    )

@app.route("/pharmacy")
def pharmacy_page():
    """Dedicated discovery experience for Pharmacy institutions (B.Pharm, Pharm.D, D.Pharm)."""
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All")
    branch = request.args.get("branch", "All")
    management_type = request.args.get("management_type", "All")
    max_fee = request.args.get("max_fee", "").strip()

    colleges = get_all_colleges(
        category="pharmacy",
        search=search,
        district=district,
        branch=branch,
        management_type=management_type,
        max_fee=max_fee if max_fee else None
    )

    districts = get_districts(category="pharmacy")
    branches = get_unique_branches(category="pharmacy")
    mgmt_types = ["University", "Private Unaided"]

    return render_template(
        "pharmacy.html",
        colleges=colleges,
        total_count=len(colleges),
        districts=districts,
        branches=branches,
        mgmt_types=mgmt_types,
        active_filters={
            "search": search,
            "district": district,
            "branch": branch,
            "management_type": management_type,
            "max_fee": max_fee
        }
    )

@app.route("/colleges/<int:college_id>")
def college_detail(college_id):
    """Detailed college profile page with academics, fees, placements, faculty, and cutoffs."""
    college = get_college_by_id(college_id)
    if not college:
        flash("The requested college was not found.", "warning")
        return redirect(url_for("colleges_directory"))
        
    return render_template("college_detail.html", college=college)

@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    """AI College Recommendations page with category-aware step-by-step form and ranked results."""
    category = request.args.get("category", "engineering").lower()
    districts = get_districts()
    branches = get_unique_branches()
    types = get_institution_types()

    results_data = None
    if request.method == "POST":
        try:
            preferences = _parse_recommendation_preferences(request.form, from_form=True)
            category = preferences["category"]
            results_data = get_recommendations(preferences)
        except ValueError as error:
            flash(str(error), "warning")

    return render_template(
        "recommendations.html",
        districts=districts,
        branches=branches,
        types=types,
        category=category,
        results_data=results_data
    )

@app.route("/compare")
def compare_page():
    """Side-by-side comparison for up to four selected institutions."""
    colleges_list = get_all_colleges(sort_by="name_asc")

    # Import legacy/deep-link IDs into the session once, then use the session as
    # the single source of truth for subsequent navigation, removal, and refresh.
    if "ids" in request.args:
        query_ids = [_parse_college_id(value) for value in request.args.get("ids", "").split(",")]
        valid_ids = _valid_compare_ids([value for value in query_ids if value is not None])
        session["compare_ids"] = valid_ids
        return redirect(url_for("compare_page"))

    selected_ids = _current_compare_ids()
    compared_colleges = compare_colleges(selected_ids)

    return render_template(
        "compare.html",
        all_colleges=colleges_list,
        compared_colleges=compared_colleges,
        selected_ids=selected_ids
    )

@app.route("/chatbot")
def chatbot_page():
    """Dedicated full-screen conversational Darpan AI Assistant page."""
    return render_template("chatbot.html")

@app.route("/admission-guide")
def admission_guide():
    """Comprehensive admission information centre for POLYCET, EAPCET, ECET, and Pharmacy."""
    return render_template("admission_guide.html")

@app.route("/mtech-college-finder")
def mtech_college_finder():
    """Informational M.Tech guide with manually curated official external resources."""
    colleges = [
        {
            "name": "Indian Institute of Technology Hyderabad",
            "location": "Kandi, Sangareddy, Telangana",
            "description": "The institute publishes its M.Tech programmes, departments and admission routes on its official postgraduate page. Programme requirements vary by department and admission category.",
            "programmes": "Official M.Tech programme information available",
            "website": "https://www.iith.ac.in/academics/post-graduate/index.html",
        },
        {
            "name": "JNTUH University College of Engineering Hyderabad",
            "location": "Kukatpally, Hyderabad, Telangana",
            "description": "The college states that its regular two-year M.Tech admissions use GATE / Telangana PGECET counselling. Check the current notification for active specializations and eligibility.",
            "programmes": "Regular M.Tech admission information published",
            "website": "https://jntuhceh.ac.in/admissions",
        },
        {
            "name": "Jawaharlal Nehru Technological University Hyderabad",
            "location": "Kukatpally, Hyderabad, Telangana",
            "description": "JNTUH publishes postgraduate admission information, including M.Tech admission categories and current notices, through its university admissions pages.",
            "programmes": "M.Tech admission information published",
            "website": "https://jntuh.ac.in/admissions",
        },
        {
            "name": "University of Hyderabad",
            "location": "Gachibowli, Hyderabad, Telangana",
            "description": "The university publishes postgraduate admission notifications and programme-specific intake and entry routes. Review the current notification before applying.",
            "programmes": "Current M.Tech programme details in official notifications",
            "website": "https://acad.uohyd.ac.in/",
        },
    ]
    portals = [
        {"name": "GATE 2027", "description": "Current official examination information, eligibility, syllabus, notifications and application portal from IIT Madras, the organizing institute.", "url": "https://gate2027.iitm.ac.in/"},
        {"name": "Telangana PGECET admissions and counselling", "description": "TGCHE counselling portal for M.E./M.Tech./M.Arch admissions; check the current cycle and notices.", "url": "https://pgecetadm.tgche.ac.in/index_ME.html"},
        {"name": "Telangana Council of Higher Education", "description": "State higher education department and council information.", "url": "https://tgche.ac.in/"},
        {"name": "AICTE", "description": "Official technical education regulator information. Verify institution approval and programme details for the applicable academic year.", "url": "https://www.aicte-india.org/"},
        {"name": "JNTUH Directorate of Admissions", "description": "University postgraduate admission notices and application information.", "url": "https://doa.jntuh.ac.in/"},
        {"name": "IIT Hyderabad postgraduate admissions", "description": "Official postgraduate programme and admissions links.", "url": "https://www.iith.ac.in/academics/post-graduate/index.html"},
    ]
    return render_template("mtech_college_finder.html", colleges=colleges, portals=portals)

# Keep both endpoint spellings available for templates and older deep links.
# Both names render the same informational page and neither reads M.Tech data
# from the college database.
app.add_url_rule(
    "/mtech-college-finder",
    endpoint="mtech_colleges_finder",
    view_func=mtech_college_finder,
)

@app.route("/data-methodology")
def data_methodology():
    """Data Sources and Verification Methodology page."""
    stats = get_quick_statistics()
    return render_template("data_methodology.html", stats=stats)

@app.route("/about")
def about():
    """About College Darpan: story, vision, transparency methodology, tech stack."""
    stats = get_quick_statistics()
    return render_template("about.html", stats=stats)

# ----------------- REST JSON API ENDPOINTS ----------------- #

@app.route("/api/colleges", methods=["GET"])
def api_colleges():
    """Returns filtered JSON array of institutions."""
    category = request.args.get("category", "All").strip()
    search = request.args.get("search", "").strip()
    district = request.args.get("district", "All")
    branch = request.args.get("branch", "All")
    inst_type = request.args.get("institution_type", "All")
    mgmt_type = request.args.get("management_type", "All")
    max_fee = request.args.get("max_fee", "").strip()
    verified_only = request.args.get("verified_only") == "true"
    hostel_only = request.args.get("hostel_only") == "true"
    sort_by = request.args.get("sort_by", "name_asc")

    colleges = get_all_colleges(
        category=category,
        search=search,
        district=district,
        branch=branch,
        institution_type=inst_type,
        management_type=mgmt_type,
        max_fee=max_fee if max_fee else None,
        verified_placements_only=verified_only,
        hostel_only=hostel_only,
        sort_by=sort_by
    )
    return jsonify({"success": True, "count": len(colleges), "colleges": colleges})

@app.route("/api/colleges/<int:college_id>", methods=["GET"])
def api_college_detail(college_id):
    """Returns complete JSON object for a specific institution."""
    college = get_college_by_id(college_id)
    if not college:
        return jsonify({"success": False, "error": "Institution not found"}), 404
    return jsonify({"success": True, "college": college})

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """Endpoint to run hybrid recommendation algorithm via JSON."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Send recommendation preferences as a JSON object."}), 400
    try:
        preferences = _parse_recommendation_preferences(data)
        result = get_recommendations(preferences)
    except ValueError as error:
        return jsonify({"success": False, "error": str(error)}), 400
    return jsonify({"success": True, "data": result})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Conversational endpoint for Darpan AI Assistant."""
    data = request.get_json(force=True, silent=True) or {}
    raw_message = data.get("message", "")
    if not isinstance(raw_message, str):
        return jsonify({"success": False, "error": "Message must be text."}), 400
    message = raw_message.strip()
    if len(message) > 1000:
        return jsonify({"success": False, "error": "Keep messages under 1,000 characters."}), 400
    session_id = data.get("session_id", "default_guest")

    response_data = process_chat_message(message, session_context={"session_id": session_id})
    return jsonify({
        "success": True,
        "message": response_data["response"],
        "suggested_actions": response_data["suggested_actions"],
        "matched_colleges": response_data["matched_colleges"],
        "source": response_data["source"]
    })

@app.route("/api/compare", methods=["GET", "POST"])
def api_compare():
    """Read or update the session-backed comparison selection."""
    if request.method == "GET":
        return jsonify(_compare_response())

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Send a comparison action as a JSON object."}), 400

    action = data.get("action")
    # Keep compatibility with the original API body, while treating it as a
    # replacement of the same server-side selection.
    if action is None and "ids" in data:
        action = "set"
    current_ids = _current_compare_ids()

    already_selected = False
    if action == "add":
        college_id = _parse_college_id(data.get("id"))
        if college_id is None:
            return jsonify({"success": False, "error": "College ID must be a positive whole number."}), 400
        if not get_college_by_id(college_id):
            return jsonify({"success": False, "error": "College not found."}), 404
        if college_id not in current_ids:
            if len(current_ids) >= 4:
                return jsonify({"success": False, "error": "You can compare up to four colleges."}), 400
            current_ids.append(college_id)
            session["compare_ids"] = current_ids
        else:
            already_selected = True
    elif action == "remove":
        college_id = _parse_college_id(data.get("id"))
        if college_id is None:
            return jsonify({"success": False, "error": "College ID must be a positive whole number."}), 400
        session["compare_ids"] = [value for value in current_ids if value != college_id]
    elif action == "clear":
        session["compare_ids"] = []
    elif action == "set":
        ids = data.get("ids")
        if not isinstance(ids, list):
            return jsonify({"success": False, "error": "College IDs must be provided as a list."}), 400
        if len(ids) > 4:
            return jsonify({"success": False, "error": "You can compare up to four colleges."}), 400
        validated_ids = []
        for value in ids:
            college_id = _parse_college_id(value)
            if college_id is None:
                return jsonify({"success": False, "error": "Each college ID must be a positive whole number."}), 400
            if not get_college_by_id(college_id):
                return jsonify({"success": False, "error": f"College ID {college_id} was not found."}), 404
            if college_id not in validated_ids:
                validated_ids.append(college_id)
        session["compare_ids"] = validated_ids
    else:
        return jsonify({"success": False, "error": "Choose add, remove, clear, or set as the comparison action."}), 400

    response = _compare_response()
    response["already_selected"] = already_selected
    return jsonify(response)

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Returns live database statistics by category."""
    stats = get_quick_statistics()
    return jsonify({"success": True, "stats": stats})

@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "platform": Config.PLATFORM_NAME,
        "mode": "local_database_driven",
        "categories": ["polytechnic", "engineering", "pharmacy"],
        "state": Config.STATE
    })

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template("base.html", error_title="404 - Page Not Found", 
                           error_msg="The requested page does not exist on College Darpan."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", error_title="500 - Server Error", 
                           error_msg="An internal error occurred. Please try again or return home."), 500

if __name__ == "__main__":
    prepare_database()
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
