from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)
    assert data[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_a_new_participant():
    # Arrange
    activity = "Programming Class"
    email = "newstudent@example.com"
    url = f"/activities/{quote(activity)}/signup?email={email}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]


def test_signup_duplicate_participant_returns_error():
    # Arrange
    activity = "Gym Class"
    email = "repeatstudent@example.com"
    signup_url = f"/activities/{quote(activity)}/signup?email={email}"

    # Act
    first_response = client.post(signup_url)
    second_response = client.post(signup_url)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    # Arrange
    activity = "Debate Team"
    email = "removetest@example.com"
    signup_url = f"/activities/{quote(activity)}/signup?email={email}"
    remove_url = f"/activities/{quote(activity)}/remove?email={email}"

    client.post(signup_url)

    # Act
    response = client.delete(remove_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in activities[activity]["participants"]
