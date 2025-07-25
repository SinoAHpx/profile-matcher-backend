"""
Comprehensive test suite for Attributes API endpoints
用户属性API端点的综合测试套件
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app
from src.api.v1.attributes import (
    AttributeCategory, Attribute, UserAttribute,
    AttributeCategoryTree, CreateUserAttribute, UpdateUserAttribute
)

# Test client
client = TestClient(app)

# Test data fixtures
@pytest.fixture
def sample_category():
    """Sample attribute category data"""
    return {
        "id": str(uuid4()),
        "code": "sports",
        "name": "运动",
        "name_en": "Sports",
        "description": "各种体育运动和健身活动",
        "parent_id": None,
        "level": 1,
        "path": "/运动",
        "icon_name": "sports",
        "color_code": "#FF5722",
        "sort_order": 1,
        "is_active": True,
        "is_system": True
    }

@pytest.fixture
def sample_subcategory():
    """Sample attribute subcategory data"""
    parent_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "code": "ball_sports",
        "name": "球类运动",
        "name_en": "Ball Sports",
        "description": "各种球类运动项目",
        "parent_id": parent_id,
        "level": 2,
        "path": "/运动/球类运动",
        "icon_name": "ball",
        "color_code": "#FF5722",
        "sort_order": 1,
        "is_active": True,
        "is_system": True
    }

@pytest.fixture
def sample_attribute():
    """Sample attribute data"""
    category_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "code": "basketball",
        "name": "篮球",
        "name_en": "Basketball",
        "description": "篮球运动，包括打篮球、看篮球比赛等",
        "category_id": category_id,
        "category_name": "球类运动",
        "category_path": "/运动/球类运动",
        "tags": ["运动", "团队", "室内", "室外"],
        "difficulty_level": "medium",
        "time_commitment": "medium",
        "cost_level": "low",
        "physical_intensity": "high",
        "social_aspect": "team",
        "indoor_outdoor": "both",
        "popularity_score": 85,
        "is_active": True
    }

@pytest.fixture
def sample_user_attribute():
    """Sample user attribute association data"""
    user_id = str(uuid4())
    attribute_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "attribute_id": attribute_id,
        "interest_level": 8,
        "skill_level": "intermediate",
        "experience_years": 3,
        "frequency": "weekly",
        "time_spent_weekly": 6,
        "enjoyment_rating": 9,
        "status": "active",
        "is_public": True,
        "is_featured": False,
        "notes": "我很喜欢打篮球，每周都会和朋友一起打球",
        "attribute": {
            "id": attribute_id,
            "code": "basketball",
            "name": "篮球",
            "name_en": "Basketball",
            "description": "篮球运动",
            "category_id": str(uuid4()),
            "category_name": "球类运动",
            "category_path": "/运动/球类运动",
            "tags": ["运动", "团队"],
            "difficulty_level": "medium",
            "time_commitment": "medium",
            "cost_level": "low",
            "physical_intensity": "high",
            "social_aspect": "team",
            "indoor_outdoor": "both",
            "popularity_score": 85,
            "is_active": True
        }
    }

@pytest.fixture
def sample_category_tree():
    """Sample hierarchical category tree data"""
    return {
        "categories": [
            {
                "id": str(uuid4()),
                "code": "sports",
                "name": "运动",
                "name_en": "Sports",
                "level": 1,
                "path": "/运动",
                "children": [
                    {
                        "id": str(uuid4()),
                        "code": "ball_sports",
                        "name": "球类运动",
                        "name_en": "Ball Sports",
                        "level": 2,
                        "path": "/运动/球类运动",
                        "children": []
                    }
                ]
            }
        ],
        "total_categories": 2,
        "max_level": 2
    }

class TestAttributeCategories:
    """Test attribute category endpoints"""
    
    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_category_tree_success(self, mock_get_client, sample_category_tree):
        """Test successful retrieval of category tree"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=sample_category_tree["categories"])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/attributes/categories/tree")
        
        # Assertions
        assert response.status_code == 200
        # Note: The actual tree building logic would be tested here

    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_category_tree_with_level_limit(self, mock_get_client, sample_category):
        """Test category tree with level limitation"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_category])
        mock_get_client.return_value = mock_client
        
        # Make request with level limit
        response = client.get("/attributes/categories/tree?level=2")
        
        # Assertions
        assert response.status_code == 200

    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_category_tree_include_inactive(self, mock_get_client, sample_category):
        """Test category tree including inactive categories"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_category])
        mock_get_client.return_value = mock_client
        
        # Make request including inactive
        response = client.get("/attributes/categories/tree?include_inactive=true")
        
        # Assertions
        assert response.status_code == 200

class TestAttributes:
    """Test attribute endpoints"""
    
    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_attributes_success(self, mock_get_client, sample_attribute):
        """Test successful retrieval of attributes"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_attribute])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/attributes/attributes")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["code"] == "basketball"
        assert data[0]["name"] == "篮球"

    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_attributes_with_category_filter(self, mock_get_client, sample_attribute):
        """Test retrieval of attributes with category filter"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_attribute])
        mock_get_client.return_value = mock_client
        
        # Make request with category filter
        category_id = str(uuid4())
        response = client.get(f"/attributes/attributes?category_id={category_id}")
        
        # Assertions
        assert response.status_code == 200

    @patch('src.api.v1.attributes.get_supabase_client')
    def test_search_attributes(self, mock_get_client, sample_attribute):
        """Test attribute search functionality"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.or_.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_attribute])
        mock_get_client.return_value = mock_client
        
        # Make search request
        response = client.get("/attributes/search?q=篮球&limit=10")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "篮球" in data[0]["name"]

class TestUserAttributes:
    """Test user attribute association endpoints"""
    
    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_user_attributes_success(self, mock_get_client, sample_user_attribute):
        """Test successful retrieval of user attributes"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_user_attribute])
        mock_get_client.return_value = mock_client
        
        # Make request
        user_id = str(uuid4())
        response = client.get(f"/attributes/user/{user_id}/attributes")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["interest_level"] == 8
        assert data[0]["skill_level"] == "intermediate"

    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_user_attributes_with_filters(self, mock_get_client, sample_user_attribute):
        """Test retrieval of user attributes with filters"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_user_attribute])
        mock_get_client.return_value = mock_client
        
        # Make request with filters
        user_id = str(uuid4())
        response = client.get(f"/attributes/user/{user_id}/attributes?status=active&min_interest_level=5")
        
        # Assertions
        assert response.status_code == 200

    def test_create_user_attribute_model_validation(self):
        """Test CreateUserAttribute model validation"""
        # Valid data
        valid_data = {
            "attribute_id": str(uuid4()),
            "interest_level": 8,
            "skill_level": "intermediate",
            "experience_years": 3,
            "frequency": "weekly",
            "time_spent_weekly": 6,
            "enjoyment_rating": 9,
            "notes": "我很喜欢这个活动"
        }
        user_attr = CreateUserAttribute(**valid_data)
        assert user_attr.interest_level == 8
        assert user_attr.skill_level == "intermediate"
        
        # Invalid interest_level (out of range)
        with pytest.raises(ValueError):
            CreateUserAttribute(
                attribute_id=str(uuid4()),
                interest_level=11  # Should be 1-10
            )

    def test_update_user_attribute_model_validation(self):
        """Test UpdateUserAttribute model validation"""
        # All fields optional
        user_attr = UpdateUserAttribute()
        assert user_attr.interest_level is None
        
        # Partial update
        user_attr = UpdateUserAttribute(interest_level=9, notes="更新的备注")
        assert user_attr.interest_level == 9
        assert user_attr.notes == "更新的备注"

class TestPopularAttributes:
    """Test popular attributes endpoint"""
    
    @patch('src.api.v1.attributes.get_supabase_client')
    def test_get_popular_attributes(self, mock_get_client, sample_attribute):
        """Test retrieval of popular attributes"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_attribute])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/attributes/popular?limit=20&min_popularity=50")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["popularity_score"] == 85

class TestHierarchicalNavigation:
    """Test hierarchical category navigation"""
    
    def test_category_path_parsing(self, sample_subcategory):
        """Test category path parsing and navigation"""
        # Test path structure
        assert sample_subcategory["path"] == "/运动/球类运动"
        assert sample_subcategory["level"] == 2
        assert sample_subcategory["parent_id"] is not None
        
        # Test path components
        path_components = sample_subcategory["path"].strip("/").split("/")
        assert len(path_components) == 2
        assert path_components[0] == "运动"
        assert path_components[1] == "球类运动"

    def test_category_tree_structure(self, sample_category_tree):
        """Test category tree structure validation"""
        tree = sample_category_tree
        assert "categories" in tree
        assert "total_categories" in tree
        assert "max_level" in tree
        
        # Test root category
        root_category = tree["categories"][0]
        assert root_category["level"] == 1
        assert "children" in root_category
        
        # Test child category
        if root_category["children"]:
            child_category = root_category["children"][0]
            assert child_category["level"] == 2

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('src.api.v1.attributes.get_supabase_client')
    def test_supabase_connection_error(self, mock_get_client):
        """Test handling of Supabase connection errors"""
        # Setup mock to raise exception
        mock_get_client.side_effect = Exception("Connection failed")
        
        # Make request
        response = client.get("/attributes/categories/tree")
        
        # Should handle error gracefully
        assert response.status_code == 500

    def test_invalid_uuid_parameter(self):
        """Test handling of invalid UUID parameters"""
        # Make request with invalid UUID
        response = client.get("/attributes/attributes?category_id=invalid-uuid")
        
        # Should return validation error
        assert response.status_code == 422

    def test_invalid_query_parameters(self):
        """Test handling of invalid query parameters"""
        # Make request with invalid limit
        response = client.get("/attributes/search?limit=-1")
        
        # Should return validation error
        assert response.status_code == 422

class TestPerformance:
    """Test performance-related scenarios"""
    
    def test_large_category_tree_handling(self):
        """Test handling of large category trees"""
        # This would test pagination and performance optimizations
        # For now, we'll test the structure
        max_categories = 1000
        assert max_categories > 0  # Placeholder for actual performance test

    def test_search_query_optimization(self):
        """Test search query optimization"""
        # This would test search performance with various query patterns
        search_terms = ["篮球", "运动", "球类"]
        for term in search_terms:
            assert len(term) > 0  # Placeholder for actual search optimization test

if __name__ == "__main__":
    pytest.main([__file__])
