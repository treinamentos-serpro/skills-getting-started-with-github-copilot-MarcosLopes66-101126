import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(app_module.activities))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Basketball Team"

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    assert activities
    assert {
        "description",
        "schedule",
        "max_participants",
        "participants",
    } <= activities[expected_activity].keys()
    assert isinstance(activities[expected_activity]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    email = "student@example.edu"

    # Act
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )
    participants = client.get("/activities").json()["Basketball Team"]["participants"]

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Basketball Team"
    }
    assert email in participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.edu"

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "student@example.edu"
    endpoint = "/activities/Basketball Team/signup"
    signup_response = client.post(endpoint, params={"email": email})

    # Act
    duplicate_response = client.post(endpoint, params={"email": email})
    participants = client.get("/activities").json()["Basketball Team"]["participants"]

    # Assert
    assert signup_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"
    assert participants.count(email) == 1


def test_signup_requires_email(client):
    # Arrange
    endpoint = "/activities/Basketball Team/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_delete_signup_removes_participant(client):
    # Arrange
    email = "student@example.edu"
    signup_response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )
    participants = client.get("/activities").json()["Basketball Team"]["participants"]

    # Assert
    assert signup_response.status_code == 200
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Basketball Team"}
    assert email not in participants


def test_delete_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_signup_rejects_unregistered_participant(client):
    # Arrange
    email = "student@example.edu"

    # Act
    response = client.delete(
        "/activities/Basketball Team/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_delete_signup_requires_email(client):
    # Arrange
    endpoint = "/activities/Basketball Team/signup"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 422