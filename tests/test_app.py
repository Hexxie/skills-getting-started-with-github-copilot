"""
Test suite for the Mergington High School Activities API

Uses the Arrange-Act-Assert (AAA) pattern for clear test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Fresh activities state
        Act: Call GET /activities
        Assert: Response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_returns_activity_details(self, client):
        """
        Arrange: Fresh activities state
        Act: Call GET /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_populated_participants(self, client):
        """
        Arrange: Fresh activities state (some activities have pre-populated participants)
        Act: Call GET /activities
        Assert: Some activities have non-empty participants lists
        """
        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        has_participants = any(
            len(activity["participants"]) > 0
            for activity in activities.values()
        )
        assert has_participants, "At least one activity should have participants"


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Fresh state
        Act: Call GET /
        Assert: Response is a redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [307, 308]
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """
        Arrange: Clean state, select Chess Club activity
        Act: POST signup with new email
        Assert: Response is 200 OK, email is added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert new_email in result["message"]

        # Verify participant was added by fetching activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Arrange: Email already signed up for Chess Club
        Act: POST same signup again
        Assert: Response is 400 Bad Request with appropriate error message
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Clean state
        Act: POST signup for non-existent activity
        Assert: Response is 404 Not Found
        """
        # Arrange
        fake_activity = "Fake Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_successful_unregister(self, client):
        """
        Arrange: Email is already signed up for Chess Club
        Act: DELETE unregister request
        Assert: Response is 200 OK, email is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Verify participant is there before unregister
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Clean state
        Act: DELETE unregister for non-existent activity
        Assert: Response is 404 Not Found
        """
        # Arrange
        fake_activity = "Fake Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister?email={email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_not_signed_up_returns_400(self, client):
        """
        Arrange: Clean state, email is NOT signed up for Chess Club
        Act: DELETE unregister for email not in participants
        Assert: Response is 400 Bad Request
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}",
            follow_redirects=False
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"].lower()
