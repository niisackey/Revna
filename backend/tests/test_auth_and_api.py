#!/usr/bin/env python3
"""
Test suite for Leave Request Application Authentication
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main_with_auth import app
from database import get_db, User, LeaveRequest
from auth import get_password_hash, verify_password, create_access_token

client = TestClient(app)

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) == True
        assert verify_password("wrongpassword", hashed) == False
    
    def test_token_creation(self):
        """Test JWT token creation"""
        user_data = {"sub": "test@example.com", "role": "Employee"}
        token = create_access_token(data=user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_register_endpoint(self):
        """Test user registration"""
        user_data = {
            "email": "newuser@test.com",
            "password": "password123",
            "employee_id": "TEST001",
            "full_name": "Test User",
            "department": "IT",
            "role": "Employee"
        }
        
        response = client.post("/register", json=user_data)
        assert response.status_code in [200, 400]  # 400 if user already exists
    
    def test_login_endpoint(self):
        """Test user login"""
        # First register a user
        user_data = {
            "email": "logintest@test.com",
            "password": "password123",
            "employee_id": "LOGIN001",
            "full_name": "Login Test User",
            "department": "IT",
            "role": "Employee"
        }
        client.post("/register", json=user_data)
        
        # Then try to login
        login_data = {
            "email": "logintest@test.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 401

class TestLeaveRequests:
    """Test leave request functionality"""
    
    def get_auth_headers(self):
        """Helper method to get authentication headers"""
        # Register and login a test user
        user_data = {
            "email": "leavetester@test.com",
            "password": "password123",
            "employee_id": "LEAVE001",
            "full_name": "Leave Tester",
            "department": "IT",
            "role": "Employee"
        }
        client.post("/register", json=user_data)
        
        login_data = {
            "email": "leavetester@test.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_leave_request(self):
        """Test creating a leave request"""
        headers = self.get_auth_headers()
        
        leave_data = {
            "start_date": "2025-09-01",
            "end_date": "2025-09-05",
            "leave_type": "Annual",
            "reason": "Vacation"
        }
        
        response = client.post("/leave-requests", json=leave_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["leave_type"] == "Annual"
    
    def test_get_leave_requests(self):
        """Test getting leave requests"""
        headers = self.get_auth_headers()
        
        response = client.get("/leave-requests", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        leave_data = {
            "start_date": "2025-09-01",
            "end_date": "2025-09-05",
            "leave_type": "Annual",
            "reason": "Vacation"
        }
        
        response = client.post("/leave-requests", json=leave_data)
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
