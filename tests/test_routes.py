"""
Automated integration tests for College Darpan web routes and REST API endpoints.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"College Darpan" in response.data
    assert b"Find the Right College for Your Future" in response.data

def test_colleges_directory(client):
    response = client.get("/colleges")
    assert response.status_code == 200
    assert b"Explore Telangana Colleges" in response.data
    assert b"OUCE" in response.data or b"CBIT" in response.data

def test_college_detail_page(client):
    response = client.get("/colleges/1")
    assert response.status_code == 200
    assert b"Institution Overview" in response.data

def test_college_detail_404_redirect(client):
    response = client.get("/colleges/99999", follow_redirects=True)
    assert response.status_code == 200
    assert b"The requested college was not found" in response.data

def test_recommendations_get_and_post(client):
    # GET form
    res_get = client.get("/recommendations")
    assert res_get.status_code == 200
    assert b"AI College Recommendation Engine" in res_get.data

    # POST calculation
    res_post = client.post("/recommendations", data={
        "exam": "TS ECET",
        "rank": "150",
        "category": "OC_BOYS",
        "branch": "AIML",
        "district": "Hyderabad",
        "max_budget": "140000",
        "institution_type": "Any",
        "w_branch": "3",
        "w_fee": "2.5",
        "w_placements": "2",
        "w_location": "1",
        "w_infra": "1.5"
    })
    assert res_post.status_code == 200
    assert b"Ranked Recommendations for You" in res_post.data

def test_compare_page(client):
    response = client.get("/compare?ids=1,3", follow_redirects=True)
    assert response.status_code == 200
    assert b"Compare Colleges" in response.data

def test_compare_session_flow_and_four_college_limit(client):
    available = client.get("/api/colleges").get_json()["colleges"]
    selected = available[:5]
    ids = [college["id"] for college in selected]

    assert client.get("/api/compare").get_json()["selected_ids"] == []
    first = client.post("/api/compare", json={"action": "add", "id": ids[0]}).get_json()
    assert first["count"] == 1
    one_selected = client.get("/compare")
    assert b"Add one more college to compare" in one_selected.data
    assert b">1</span>" in one_selected.data
    directory = client.get("/colleges").get_data(as_text=True)
    assert "CompareManager.add(" in directory
    assert ">1</span>" in directory

    second = client.post("/api/compare", json={"action": "add", "id": ids[1]}).get_json()
    assert second["selected_ids"] == ids[:2]
    comparison = client.get("/compare").get_data(as_text=True)
    assert ">2</span>" in comparison
    table = comparison.split("<table", 1)[1].split("</table>", 1)[0]
    assert all(college["name"] in table for college in selected[:2])

    removed = client.post("/api/compare", json={"action": "remove", "id": ids[0]}).get_json()
    assert removed["selected_ids"] == [ids[1]]
    refreshed = client.get("/compare").get_data(as_text=True)
    assert client.get("/api/compare").get_json()["selected_ids"] == [ids[1]]
    assert "Add one more college to compare" in refreshed
    assert ">1</span>" in refreshed

    for college_id in ids[2:5]:
        result = client.post("/api/compare", json={"action": "add", "id": college_id})
        assert result.status_code == 200
    full_selection = client.get("/api/compare").get_json()
    assert full_selection["selected_ids"] == ids[1:5]
    assert full_selection["count"] == 4
    assert len({college["id"] for college in full_selection["colleges"]}) == 4
    assert client.post("/api/compare", json={"action": "add", "id": ids[0]}).status_code == 400

    duplicate = client.post("/api/compare", json={"action": "add", "id": ids[1]}).get_json()
    assert duplicate["already_selected"] is True
    assert duplicate["count"] == 4

    client.post("/api/compare", json={"action": "clear"})
    empty = client.get("/api/compare").get_json()
    assert empty["selected_ids"] == []
    assert empty["colleges"] == []
    assert b"No Colleges in Comparison Tray" in client.get("/compare").data
    assert b"compare-count-badge" in client.get("/compare").data

def test_compare_rejects_invalid_college_ids(client):
    malformed = client.post("/api/compare", json={"action": "add", "id": "abc"})
    assert malformed.status_code == 400
    missing = client.post("/api/compare", json={"action": "add", "id": 99999999})
    assert missing.status_code == 404
    malformed_json = client.post("/api/compare", data="{", content_type="application/json")
    assert malformed_json.status_code == 400
    invalid_query = client.get("/compare?ids=99999999", follow_redirects=True)
    assert b"No Colleges in Comparison Tray" in invalid_query.data
    assert client.get("/api/compare").get_json()["selected_ids"] == []

def test_chatbot_page(client):
    response = client.get("/chatbot")
    assert response.status_code == 200
    assert b"Darpan AI Assistant" in response.data

def test_admission_guide_page(client):
    response = client.get("/admission-guide")
    assert response.status_code == 200
    assert b"TS ECET" in response.data

def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About College Darpan" in response.data

def test_api_colleges_endpoint(client):
    response = client.get("/api/colleges")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["count"] > 0

def test_api_chat_endpoint(client):
    response = client.post("/api/chat", json={"message": "Which colleges offer AIML in Hyderabad?"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "AIML" in json_data["message"]
    assert json_data["matched_colleges"]
    assert all(college["district"].lower() == "hyderabad" for college in json_data["matched_colleges"])

def test_api_recommend_endpoint(client):
    response = client.post("/api/recommend", json={
        "exam": "TS ECET",
        "rank": 250,
        "branch": "CSE",
        "district": "Hyderabad",
        "max_budget": 120000
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]["results"]) > 0

@pytest.mark.parametrize("payload", [
    {"rank": "not-a-rank"},
    {"rank": 0},
    {"rank": 200001},
    {"max_budget": -1},
    {"max_budget": "NaN"},
    {"weights": {"branch": 5.5}},
])
def test_api_recommend_rejects_invalid_preferences(client, payload):
    response = client.post("/api/recommend", json=payload)
    assert response.status_code == 400
    assert response.get_json()["success"] is False

def test_recommendation_form_reports_invalid_inputs(client):
    response = client.post("/recommendations", data={"rank": "-2", "w_branch": "6"})
    assert response.status_code == 200
    assert b"Rank must be a whole number" in response.data
    assert b"Ranked Recommendations for You" not in response.data

def test_api_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
