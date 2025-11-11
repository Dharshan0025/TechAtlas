"""
Tests for InputValidator Service
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.input_validator import InputValidator


class TestInputValidator:
    """Test suite for InputValidator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return InputValidator()
    
    def test_validator_initialization(self, validator):
        """Test that validator initializes correctly"""
        assert validator is not None
    
    # Email Validation Tests
    def test_validate_email_valid(self, validator):
        """Test valid email validation"""
        is_valid, errors = validator.validate_email('user@example.com')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_email_invalid(self, validator):
        """Test invalid email validation"""
        is_valid, errors = validator.validate_email('invalid-email')
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_email_empty(self, validator):
        """Test empty email validation"""
        is_valid, errors = validator.validate_email('')
        assert is_valid is False
        assert len(errors) > 0
    
    # Title Validation Tests
    def test_validate_title_valid(self, validator):
        """Test valid title validation"""
        is_valid, errors = validator.validate_title('Valid Decision Title')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_title_too_short(self, validator):
        """Test title too short"""
        is_valid, errors = validator.validate_title('Hi')
        assert is_valid is False
        assert any('at least 5 characters' in e for e in errors)
    
    def test_validate_title_too_long(self, validator):
        """Test title too long"""
        long_title = 'A' * 501
        is_valid, errors = validator.validate_title(long_title)
        assert is_valid is False
        assert any('less than 500' in e for e in errors)
    
    def test_validate_title_empty(self, validator):
        """Test empty title"""
        is_valid, errors = validator.validate_title('')
        assert is_valid is False
        assert any('cannot be empty' in e for e in errors)
    
    # Rationale Validation Tests
    def test_validate_rationale_valid(self, validator):
        """Test valid rationale validation"""
        is_valid, errors = validator.validate_rationale('This is a valid rationale for the decision')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_rationale_too_short(self, validator):
        """Test rationale too short"""
        is_valid, errors = validator.validate_rationale('Short')
        assert is_valid is False
        assert any('at least 10 characters' in e for e in errors)
    
    def test_validate_rationale_too_long(self, validator):
        """Test rationale too long"""
        long_rationale = 'A' * 5001
        is_valid, errors = validator.validate_rationale(long_rationale)
        assert is_valid is False
        assert any('less than 5000' in e for e in errors)
    
    # URL Validation Tests
    def test_validate_url_valid_http(self, validator):
        """Test valid HTTP URL"""
        is_valid, errors = validator.validate_url('http://example.com')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_url_valid_https(self, validator):
        """Test valid HTTPS URL"""
        is_valid, errors = validator.validate_url('https://example.com/path')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_url_invalid(self, validator):
        """Test invalid URL"""
        is_valid, errors = validator.validate_url('not-a-url')
        assert is_valid is False
        assert len(errors) > 0
    
    # Date Validation Tests
    def test_validate_date_valid(self, validator):
        """Test valid date"""
        is_valid, errors = validator.validate_date('2024-12-31')
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_date_invalid_format(self, validator):
        """Test invalid date format"""
        is_valid, errors = validator.validate_date('31-12-2024')
        assert is_valid is False
        assert any('YYYY-MM-DD' in e for e in errors)
    
    def test_validate_date_invalid_value(self, validator):
        """Test invalid date value"""
        is_valid, errors = validator.validate_date('2024-13-45')
        assert is_valid is False
        assert any('Invalid date' in e for e in errors)
    
    # Participants Validation Tests
    def test_validate_participants_valid(self, validator):
        """Test valid participants list"""
        participants = ['user1@test.com', 'user2@test.com']
        is_valid, errors = validator.validate_participants(participants)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_participants_invalid_email(self, validator):
        """Test participants with invalid email"""
        participants = ['user1@test.com', 'invalid-email']
        is_valid, errors = validator.validate_participants(participants)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_participants_too_many(self, validator):
        """Test too many participants"""
        participants = [f'user{i}@test.com' for i in range(51)]
        is_valid, errors = validator.validate_participants(participants)
        assert is_valid is False
        assert any('Maximum 50' in e for e in errors)
    
    def test_validate_participants_not_list(self, validator):
        """Test participants not a list"""
        is_valid, errors = validator.validate_participants('not-a-list')
        assert is_valid is False
        assert any('must be a list' in e for e in errors)
    
    # Status Validation Tests
    def test_validate_status_valid(self, validator):
        """Test valid status"""
        for status in ['Open', 'In Progress', 'Completed', 'Archived']:
            is_valid, errors = validator.validate_status(status)
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_status_invalid(self, validator):
        """Test invalid status"""
        is_valid, errors = validator.validate_status('Invalid Status')
        assert is_valid is False
        assert len(errors) > 0
    
    # Decision Input Validation Tests
    def test_validate_decision_input_valid(self, validator):
        """Test valid decision input"""
        data = {
            'title': 'Valid Decision Title',
            'owner': 'user@test.com',
            'rationale': 'This is a valid rationale for the decision',
            'due_date': '2024-12-31',
            'thread_link': 'https://example.com/thread',
            'participants': ['user1@test.com', 'user2@test.com'],
            'channel_id': 'tech-team'
        }
        
        is_valid, errors = validator.validate_decision_input(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_decision_input_missing_fields(self, validator):
        """Test decision input with invalid fields"""
        data = {
            'title': 'Hi',  # Too short
            'owner': 'invalid-email',
            'rationale': 'Short',  # Too short
        }
        
        is_valid, errors = validator.validate_decision_input(data)
        assert is_valid is False
        assert len(errors) > 0
    
    # Text Sanitization Tests
    def test_sanitize_text_basic(self, validator):
        """Test basic text sanitization"""
        text = '  Hello World  '
        sanitized = validator.sanitize_text(text)
        assert sanitized == 'Hello World'
    
    def test_sanitize_text_script_removal(self, validator):
        """Test script tag removal"""
        text = 'Hello <script>alert("xss")</script> World'
        sanitized = validator.sanitize_text(text)
        assert '<script>' not in sanitized
        assert 'alert' not in sanitized
    
    def test_sanitize_text_empty(self, validator):
        """Test sanitizing empty text"""
        sanitized = validator.sanitize_text('')
        assert sanitized == ''
    
    def test_sanitize_text_none(self, validator):
        """Test sanitizing None"""
        sanitized = validator.sanitize_text(None)
        assert sanitized == ''
    
    # Query Parameters Validation Tests
    def test_validate_query_params_valid(self, validator):
        """Test valid query parameters"""
        params = {'limit': 10, 'offset': 0}
        allowed = ['limit', 'offset', 'sort_by']
        
        is_valid, errors = validator.validate_query_params(params, allowed)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_query_params_unknown(self, validator):
        """Test unknown query parameters"""
        params = {'limit': 10, 'unknown_param': 'value'}
        allowed = ['limit', 'offset']
        
        is_valid, errors = validator.validate_query_params(params, allowed)
        assert is_valid is False
        assert any('Unknown parameter' in e for e in errors)
    
    # Pagination Validation Tests
    def test_validate_pagination_valid(self, validator):
        """Test valid pagination"""
        is_valid, errors = validator.validate_pagination(50, 0)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_pagination_invalid_limit(self, validator):
        """Test invalid limit"""
        is_valid, errors = validator.validate_pagination(0, 0)
        assert is_valid is False
        assert any('at least 1' in e for e in errors)
        
        is_valid, errors = validator.validate_pagination(1001, 0)
        assert is_valid is False
        assert any('cannot exceed 1000' in e for e in errors)
    
    def test_validate_pagination_invalid_offset(self, validator):
        """Test invalid offset"""
        is_valid, errors = validator.validate_pagination(10, -1)
        assert is_valid is False
        assert any('cannot be negative' in e for e in errors)
    
    # Required Fields Validation Tests
    def test_validate_required_fields_present(self, validator):
        """Test all required fields present"""
        data = {'title': 'Test', 'owner': 'user@test.com'}
        required = ['title', 'owner']
        
        is_valid, errors = validator.validate_required_fields(data, required)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_required_fields_missing(self, validator):
        """Test missing required fields"""
        data = {'title': 'Test'}
        required = ['title', 'owner']
        
        is_valid, errors = validator.validate_required_fields(data, required)
        assert is_valid is False
        assert any('owner' in e for e in errors)
    
    def test_validate_required_fields_empty(self, validator):
        """Test empty required fields"""
        data = {'title': '', 'owner': 'user@test.com'}
        required = ['title', 'owner']
        
        is_valid, errors = validator.validate_required_fields(data, required)
        assert is_valid is False
        assert any('title' in e for e in errors)
    
    # Field Types Validation Tests
    def test_validate_field_types_correct(self, validator):
        """Test correct field types"""
        data = {'title': 'Test', 'count': 5}
        types = {'title': str, 'count': int}
        
        is_valid, errors = validator.validate_field_types(data, types)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_field_types_incorrect(self, validator):
        """Test incorrect field types"""
        data = {'title': 'Test', 'count': 'not-a-number'}
        types = {'title': str, 'count': int}
        
        is_valid, errors = validator.validate_field_types(data, types)
        assert is_valid is False
        assert any('count' in e for e in errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
