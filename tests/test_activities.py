"""
Tests for FastAPI activity endpoints.
"""
import pytest


def test_get_activities(client):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Basketball Team" in data
    assert "Tennis Club" in data
    assert len(data) == 9


def test_get_activities_structure(client):
    """Test that activities have the correct structure."""
    response = client.get("/activities")
    data = response.json()
    
    activity = data["Basketball Team"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Basketball Team/signup?email=newstudent@mergington.edu",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_already_registered(client):
    """Test signup fails if student is already registered."""
    response = client.post(
        "/activities/Basketball Team/signup?email=alex@mergington.edu",
        json={}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test signup fails for nonexistent activity."""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu",
        json={}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_updates_participants_list(client):
    """Test that signup actually adds participant to the list."""
    # Verify initial state
    response = client.get("/activities")
    initial_count = len(response.json()["Basketball Team"]["participants"])
    
    # Sign up
    client.post(
        "/activities/Basketball Team/signup?email=newstudent@mergington.edu",
        json={}
    )
    
    # Verify participant was added
    response = client.get("/activities")
    new_count = len(response.json()["Basketball Team"]["participants"])
    assert new_count == initial_count + 1
    assert "newstudent@mergington.edu" in response.json()["Basketball Team"]["participants"]


def test_unregister_success(client):
    """Test successful unregistration from an activity."""
    response = client.post(
        "/activities/Basketball Team/unregister?email=alex@mergington.edu",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert "alex@mergington.edu" in data["message"]


def test_unregister_not_registered(client):
    """Test unregister fails if student is not registered."""
    response = client.post(
        "/activities/Basketball Team/unregister?email=notregistered@mergington.edu",
        json={}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client):
    """Test unregister fails for nonexistent activity."""
    response = client.post(
        "/activities/Nonexistent Club/unregister?email=test@mergington.edu",
        json={}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes participant from the list."""
    # Verify initial state
    response = client.get("/activities")
    initial_count = len(response.json()["Drama Club"]["participants"])
    assert "lucas@mergington.edu" in response.json()["Drama Club"]["participants"]
    
    # Unregister
    client.post(
        "/activities/Drama Club/unregister?email=lucas@mergington.edu",
        json={}
    )
    
    # Verify participant was removed
    response = client.get("/activities")
    new_count = len(response.json()["Drama Club"]["participants"])
    assert new_count == initial_count - 1
    assert "lucas@mergington.edu" not in response.json()["Drama Club"]["participants"]


def test_signup_then_unregister(client):
    """Test signup followed by unregister."""
    email = "teststudent@mergington.edu"
    activity = "Basketball Team"
    
    # Sign up
    response = client.post(
        f"/activities/{activity}/signup?email={email}",
        json={}
    )
    assert response.status_code == 200
    
    # Verify signup
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    response = client.post(
        f"/activities/{activity}/unregister?email={email}",
        json={}
    )
    assert response.status_code == 200
    
    # Verify unregister
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]
