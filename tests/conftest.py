import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def original_activities():
    """Store the original activities state"""
    return deepcopy(activities)


@pytest.fixture
def client(original_activities):
    """Provide a TestClient with reset activities for each test"""
    # Reset activities to original state before each test
    activities.clear()
    activities.update(deepcopy(original_activities))
    
    return TestClient(app)
