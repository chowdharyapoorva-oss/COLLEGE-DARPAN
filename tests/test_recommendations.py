"""
Automated unit tests for College Darpan Hybrid Recommendation Engine.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.recommendation_engine import (
    normalize_weights, score_branch_match, score_affordability, 
    score_placements, evaluate_admission_eligibility, get_recommendations
)

def test_normalize_weights_default():
    weights = normalize_weights(None)
    assert abs(sum(weights.values()) - 1.0) < 0.001
    assert "branch" in weights
    assert "affordability" in weights

def test_normalize_weights_custom():
    custom = {
        "branch": 5,
        "affordability": 5,
        "placements": 5,
        "location": 5,
        "infrastructure": 5
    }
    normalized = normalize_weights(custom)
    assert abs(sum(normalized.values()) - 1.0) < 0.001
    assert normalized["branch"] == 0.2

def test_score_branch_match():
    branches = [
        {"branch_code": "CSE", "branch_name": "Computer Science and Engineering"},
        {"branch_code": "AIML", "branch_name": "Artificial Intelligence & Machine Learning"}
    ]
    # Exact match
    score, note, exact = score_branch_match("AIML", branches)
    assert score == 100
    assert exact is True

    # Allied match (e.g. user wants CSD or INF, and college has CSE/AIML)
    score_allied, note_allied, exact_allied = score_branch_match("CSD", branches)
    assert score_allied >= 70
    assert exact_allied is False

    # Any branch
    score_any, note_any, _ = score_branch_match("Any", branches)
    assert score_any == 100

def test_score_affordability():
    # Within budget
    score_within, note_within, status = score_affordability(120000, 105000)
    assert score_within >= 95
    assert status == "within"

    # Slightly above budget (within 15%)
    score_close, _, status_close = score_affordability(100000, 110000)
    assert score_close == 75
    assert status_close == "close"

    # Missing fee handling (neutral, not negative)
    score_missing, _, status_missing = score_affordability(100000, None)
    assert score_missing == 60
    assert status_missing == "unverified"

def test_admission_eligibility_safeguard_missing():
    # If no rank or category provided
    result = evaluate_admission_eligibility(1, "TS ECET", None, None, "AIML")
    assert result["message"] == "Admission eligibility cannot be confirmed with the available data."

def test_full_recommendation_pipeline():
    prefs = {
        "exam": "TS ECET",
        "rank": 200,
        "category": "OC_BOYS",
        "branch": "AIML",
        "district": "Hyderabad",
        "max_budget": 140000,
        "institution_type": "Any",
        "weights": {"branch": 3, "affordability": 2.5, "placements": 2, "location": 1, "infrastructure": 1.5}
    }
    output = get_recommendations(prefs)
    assert "results" in output
    assert len(output["results"]) > 0
    top = output["results"][0]
    assert "match_score" in top
    assert 0 <= top["match_score"] <= 100
    assert "explanation" in top
    assert "eligibility" in top
