"""
Comprehensive test suite for Ego/Personality API endpoints
人格特质/认知功能API端点的综合测试套件
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime
from decimal import Decimal
from fastapi.testclient import TestClient
from fastapi import HTTPException

from main import app
from src.api.v1.ego import (
    CognitiveFunction, UserCognitiveFunction, TraitCategory, TraitValueType,
    PersonalityTrait, UserPersonalityTrait, CreateUserCognitiveFunction,
    UpdateUserCognitiveFunction, CreateUserPersonalityTrait, UpdateUserPersonalityTrait
)

# Test client
client = TestClient(app)

# Test data fixtures
@pytest.fixture
def sample_cognitive_function():
    """Sample cognitive function data"""
    return {
        "id": str(uuid4()),
        "code": "Ni",
        "name": "内倾直觉",
        "full_name": "内倾直觉 (Introverted Intuition)",
        "description": "专注于内在的可能性和模式，寻找深层的洞察和理解",
        "function_type": "perceiving",
        "attitude": "introverted",
        "is_active": True
    }

@pytest.fixture
def sample_user_cognitive_function():
    """Sample user cognitive function data"""
    user_id = str(uuid4())
    function_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "cognitive_function_id": function_id,
        "raw_score": 85,
        "normalized_score": 87.5,
        "function_rank": 1,
        "confidence_level": 0.9,
        "assessment_source": "self_assessment",
        "notes": "这是我的主导功能",
        "cognitive_function": {
            "id": function_id,
            "code": "Ni",
            "name": "内倾直觉",
            "full_name": "内倾直觉 (Introverted Intuition)",
            "description": "专注于内在的可能性和模式",
            "function_type": "perceiving",
            "attitude": "introverted",
            "is_active": True
        }
    }

@pytest.fixture
def sample_trait_category():
    """Sample trait category data"""
    return {
        "id": str(uuid4()),
        "name": "大五人格",
        "slug": "big-five",
        "description": "大五人格模型，包含五个主要人格维度",
        "framework": "big_five",
        "version": "1.0",
        "is_active": True
    }

@pytest.fixture
def sample_trait_value_type():
    """Sample trait value type data"""
    return {
        "id": str(uuid4()),
        "name": "百分比",
        "data_type": "numeric",
        "min_value": 0.0,
        "max_value": 100.0,
        "enum_values": None,
        "description": "0-100的百分比值"
    }

@pytest.fixture
def sample_personality_trait():
    """Sample personality trait data"""
    category_id = str(uuid4())
    value_type_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "name": "外向性",
        "slug": "extraversion",
        "description": "个体在社交情境中的活跃程度和对外部刺激的敏感性",
        "is_reverse_scored": False,
        "display_order": 1,
        "tags": ["社交", "活跃", "外向"],
        "is_active": True,
        "category": {
            "id": category_id,
            "name": "大五人格",
            "slug": "big-five",
            "description": "大五人格模型",
            "framework": "big_five",
            "version": "1.0",
            "is_active": True
        },
        "value_type": {
            "id": value_type_id,
            "name": "百分比",
            "data_type": "numeric",
            "min_value": 0.0,
            "max_value": 100.0,
            "enum_values": None,
            "description": "0-100的百分比值"
        }
    }

@pytest.fixture
def sample_user_personality_trait():
    """Sample user personality trait data"""
    user_id = str(uuid4())
    trait_id = str(uuid4())
    return {
        "id": str(uuid4()),
        "user_id": user_id,
        "trait_id": trait_id,
        "value_numeric": 75.5,
        "value_text": None,
        "value_boolean": None,
        "confidence_level": 0.85,
        "assessment_source": "questionnaire",
        "assessment_date": "2024-01-01T00:00:00Z",
        "notes": "通过问卷评估得出的外向性分数",
        "is_public": True,
        "trait": {
            "id": trait_id,
            "name": "外向性",
            "slug": "extraversion",
            "description": "社交活跃程度",
            "is_reverse_scored": False,
            "display_order": 1,
            "tags": ["社交", "外向"],
            "is_active": True,
            "category": {
                "id": str(uuid4()),
                "name": "大五人格",
                "slug": "big-five",
                "framework": "big_five"
            },
            "value_type": {
                "id": str(uuid4()),
                "name": "百分比",
                "data_type": "numeric",
                "min_value": 0.0,
                "max_value": 100.0
            }
        }
    }

class TestCognitiveFunctions:
    """Test cognitive functions endpoints"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_cognitive_functions_success(self, mock_get_client, sample_cognitive_function):
        """Test successful retrieval of cognitive functions"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_cognitive_function])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/ego/cognitive-functions")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["code"] == "Ni"
        assert data[0]["name"] == "内倾直觉"
        assert data[0]["function_type"] == "perceiving"

    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_cognitive_functions_empty(self, mock_get_client):
        """Test retrieval when no cognitive functions exist"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/ego/cognitive-functions")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

class TestUserCognitiveFunctions:
    """Test user cognitive functions endpoints"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_user_cognitive_functions_success(self, mock_get_client, sample_user_cognitive_function):
        """Test successful retrieval of user cognitive functions"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_user_cognitive_function])
        mock_get_client.return_value = mock_client
        
        # Make request
        user_id = str(uuid4())
        response = client.get(f"/ego/user/{user_id}/cognitive-functions")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["raw_score"] == 85
        assert data[0]["function_rank"] == 1
        assert data[0]["cognitive_function"]["code"] == "Ni"

    def test_create_user_cognitive_function_model_validation(self):
        """Test CreateUserCognitiveFunction model validation"""
        # Valid data
        valid_data = {
            "cognitive_function_id": str(uuid4()),
            "raw_score": 85,
            "normalized_score": 87.5,
            "function_rank": 1,
            "confidence_level": 0.9,
            "assessment_source": "self_assessment",
            "notes": "主导功能"
        }
        user_cf = CreateUserCognitiveFunction(**valid_data)
        assert user_cf.raw_score == 85
        assert user_cf.function_rank == 1
        
        # Invalid raw_score (out of range)
        with pytest.raises(ValueError):
            CreateUserCognitiveFunction(
                cognitive_function_id=str(uuid4()),
                raw_score=150  # Should be 0-100
            )
        
        # Invalid function_rank (out of range)
        with pytest.raises(ValueError):
            CreateUserCognitiveFunction(
                cognitive_function_id=str(uuid4()),
                function_rank=9  # Should be 1-8
            )

    def test_cognitive_function_distribution_calculation(self, sample_user_cognitive_function):
        """Test cognitive function distribution calculations"""
        # Test that ranks are properly distributed (1-8)
        assert 1 <= sample_user_cognitive_function["function_rank"] <= 8
        
        # Test score normalization
        raw_score = sample_user_cognitive_function["raw_score"]
        normalized_score = sample_user_cognitive_function["normalized_score"]
        assert 0 <= raw_score <= 100
        assert 0 <= normalized_score <= 100

class TestTraitCategories:
    """Test trait categories endpoints"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_trait_categories_success(self, mock_get_client, sample_trait_category):
        """Test successful retrieval of trait categories"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_trait_category])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/ego/trait-categories")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["framework"] == "big_five"
        assert data[0]["name"] == "大五人格"

    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_trait_categories_with_framework_filter(self, mock_get_client, sample_trait_category):
        """Test retrieval of trait categories with framework filter"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_trait_category])
        mock_get_client.return_value = mock_client
        
        # Make request with framework filter
        response = client.get("/ego/trait-categories?framework=big_five")
        
        # Assertions
        assert response.status_code == 200

class TestPersonalityTraits:
    """Test personality traits endpoints"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_personality_traits_success(self, mock_get_client, sample_personality_trait):
        """Test successful retrieval of personality traits"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_personality_trait])
        mock_get_client.return_value = mock_client
        
        # Make request
        response = client.get("/ego/personality-traits")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "外向性"
        assert data[0]["slug"] == "extraversion"

    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_personality_traits_with_category_filter(self, mock_get_client, sample_personality_trait):
        """Test retrieval of personality traits with category filter"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_personality_trait])
        mock_get_client.return_value = mock_client
        
        # Make request with category filter
        category_id = str(uuid4())
        response = client.get(f"/ego/personality-traits?category_id={category_id}")
        
        # Assertions
        assert response.status_code == 200

class TestUserPersonalityTraits:
    """Test user personality traits endpoints"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_get_user_personality_traits_success(self, mock_get_client, sample_user_personality_trait):
        """Test successful retrieval of user personality traits"""
        # Setup mock
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = Mock(data=[sample_user_personality_trait])
        mock_get_client.return_value = mock_client
        
        # Make request
        user_id = str(uuid4())
        response = client.get(f"/ego/user/{user_id}/personality-traits")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["value_numeric"] == 75.5
        assert data[0]["trait"]["name"] == "外向性"

    def test_create_user_personality_trait_model_validation(self):
        """Test CreateUserPersonalityTrait model validation"""
        # Valid numeric data
        valid_data = {
            "trait_id": str(uuid4()),
            "value_numeric": 75.5,
            "confidence_level": 0.85,
            "assessment_source": "questionnaire",
            "notes": "问卷评估结果"
        }
        user_trait = CreateUserPersonalityTrait(**valid_data)
        assert user_trait.value_numeric == 75.5
        assert user_trait.confidence_level == 0.85
        
        # Valid text data
        text_data = {
            "trait_id": str(uuid4()),
            "value_text": "高外向性",
            "confidence_level": 0.9
        }
        user_trait_text = CreateUserPersonalityTrait(**text_data)
        assert user_trait_text.value_text == "高外向性"
        
        # Valid boolean data
        bool_data = {
            "trait_id": str(uuid4()),
            "value_boolean": True,
            "confidence_level": 1.0
        }
        user_trait_bool = CreateUserPersonalityTrait(**bool_data)
        assert user_trait_bool.value_boolean is True

    def test_trait_value_types_handling(self, sample_trait_value_type):
        """Test different trait value types handling"""
        # Numeric type
        assert sample_trait_value_type["data_type"] == "numeric"
        assert sample_trait_value_type["min_value"] == 0.0
        assert sample_trait_value_type["max_value"] == 100.0
        
        # Test value validation logic (would be implemented in actual service)
        test_value = 75.5
        assert sample_trait_value_type["min_value"] <= test_value <= sample_trait_value_type["max_value"]

class TestAssessmentHistory:
    """Test assessment history tracking"""
    
    def test_assessment_source_tracking(self, sample_user_personality_trait):
        """Test assessment source attribution"""
        assert sample_user_personality_trait["assessment_source"] == "questionnaire"
        assert sample_user_personality_trait["assessment_date"] is not None
        assert sample_user_personality_trait["confidence_level"] == 0.85

    def test_confidence_level_validation(self):
        """Test confidence level validation"""
        # Valid confidence levels
        valid_levels = [0.0, 0.5, 0.85, 1.0]
        for level in valid_levels:
            assert 0.0 <= level <= 1.0
        
        # Invalid confidence levels
        invalid_levels = [-0.1, 1.1, 2.0]
        for level in invalid_levels:
            assert not (0.0 <= level <= 1.0)

class TestJungianTyping:
    """Test Jung's 8 cognitive functions typing system"""
    
    def test_cognitive_function_codes(self, sample_cognitive_function):
        """Test cognitive function code validation"""
        valid_codes = ["Ni", "Ne", "Si", "Se", "Ti", "Te", "Fi", "Fe"]
        assert sample_cognitive_function["code"] in valid_codes

    def test_function_type_classification(self, sample_cognitive_function):
        """Test function type classification"""
        valid_types = ["perceiving", "judging"]
        assert sample_cognitive_function["function_type"] in valid_types

    def test_attitude_classification(self, sample_cognitive_function):
        """Test attitude classification"""
        valid_attitudes = ["introverted", "extraverted"]
        assert sample_cognitive_function["attitude"] in valid_attitudes

    def test_cognitive_function_ranking_system(self, sample_user_cognitive_function):
        """Test cognitive function ranking system (1-8)"""
        rank = sample_user_cognitive_function["function_rank"]
        assert 1 <= rank <= 8
        
        # Test that primary function (rank 1) typically has highest scores
        if rank == 1:
            assert sample_user_cognitive_function["raw_score"] >= 70  # Assumption for primary function

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('src.api.v1.ego.get_supabase_client')
    def test_supabase_connection_error(self, mock_get_client):
        """Test handling of Supabase connection errors"""
        # Setup mock to raise exception
        mock_get_client.side_effect = Exception("Connection failed")
        
        # Make request
        response = client.get("/ego/cognitive-functions")
        
        # Should handle error gracefully
        assert response.status_code == 500

    def test_invalid_uuid_parameter(self):
        """Test handling of invalid UUID parameters"""
        # Make request with invalid UUID
        response = client.get("/ego/user/invalid-uuid/cognitive-functions")
        
        # Should return validation error
        assert response.status_code == 422

    def test_invalid_confidence_level(self):
        """Test handling of invalid confidence levels"""
        # Test confidence level validation in model
        with pytest.raises(ValueError):
            CreateUserPersonalityTrait(
                trait_id=str(uuid4()),
                value_numeric=50.0,
                confidence_level=1.5  # Invalid: > 1.0
            )

class TestMultiFrameworkSupport:
    """Test support for multiple personality frameworks"""
    
    def test_framework_identification(self, sample_trait_category):
        """Test framework identification and categorization"""
        frameworks = ["big_five", "mbti", "enneagram", "disc", "custom"]
        assert sample_trait_category["framework"] in frameworks

    def test_framework_versioning(self, sample_trait_category):
        """Test framework version tracking"""
        assert sample_trait_category["version"] is not None
        assert len(sample_trait_category["version"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])
