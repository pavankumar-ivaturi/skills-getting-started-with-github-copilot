"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Basketball": {
            "description": "Competitive basketball team and practice sessions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and play friendly matches",
            "schedule": "Saturdays, 9:00 AM - 11:00 AM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Stage performances and theatrical productions",
            "schedule": "Tuesdays and Thursdays, 4:45 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["maya@mergington.edu", "tyler@mergington.edu"]
        },
        "Visual Arts": {
            "description": "Painting, drawing, and sculpture classes",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Basketball" in data
        assert "Tennis Club" in data
    
    def test_get_activities_contains_correct_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball"]
        
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)
    
    def test_get_activities_initial_participants(self, client, reset_activities):
        """Test that activities have correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" in data["Basketball"]["participants"]
        assert "lucas@mergington.edu" in data["Tennis Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newtudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newtudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds participant to the list"""
        client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_already_registered_student(self, client, reset_activities):
        """Test that signup fails if student is already registered"""
        response = client.post(
            "/activities/Basketball/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails for nonexistent activity"""
        response = client.post(
            "/activities/Underwater%20Basket%20Weaving/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test that multiple students can sign up for the same activity"""
        client.post("/activities/Basketball/signup?email=student1@mergington.edu")
        client.post("/activities/Basketball/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "student1@mergington.edu" in data["Basketball"]["participants"]
        assert "student2@mergington.edu" in data["Basketball"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant from list"""
        client.delete(
            "/activities/Basketball/unregister?email=alex@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test that unregister fails if student is not registered"""
        response = client.delete(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_from_activity_with_multiple_participants(self, client, reset_activities):
        """Test unregistering one participant doesn't affect others"""
        # Debate Team has multiple participants
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Debate Team"]["participants"])
        
        client.delete(
            "/activities/Debate%20Team/unregister?email=sarah@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Debate Team"]["participants"]) == initial_count - 1
        assert "sarah@mergington.edu" not in data["Debate Team"]["participants"]
        assert "james@mergington.edu" in data["Debate Team"]["participants"]


class TestSignupAndUnregisterWorkflow:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test complete workflow of signing up then unregistering"""
        # Sign up
        client.post("/activities/Tennis%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        assert "newstudent@mergington.edu" in response.json()["Tennis Club"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Tennis%20Club/unregister?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        assert "newstudent@mergington.edu" not in response.json()["Tennis Club"]["participants"]
    
    def test_signup_multiple_then_unregister_one(self, client, reset_activities):
        """Test signing up multiple then unregistering one"""
        # Sign up multiple students
        client.post("/activities/Chess%20Club/signup?email=student1@mergington.edu")
        client.post("/activities/Chess%20Club/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister one
        client.delete(
            "/activities/Chess%20Club/unregister?email=student1@mergington.edu"
        )
        
        response = client.get("/activities")
        final_count = len(response.json()["Chess Club"]["participants"])
        assert final_count == initial_count - 1
        assert "student1@mergington.edu" not in response.json()["Chess Club"]["participants"]
        assert "student2@mergington.edu" in response.json()["Chess Club"]["participants"]
