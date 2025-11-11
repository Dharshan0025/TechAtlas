"""
Input Validation Service
Validates and sanitizes all input data
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates and sanitizes user input
    """
    
    # Validation patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    URL_PATTERN = re.compile(r'^https?://[^\s]+$')
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    def __init__(self):
        """Initialize the Input Validator"""
        logger.info("InputValidator initialized successfully")
    
    def validate_decision_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate decision creation/update input
        
        Args:
            data: Decision data dictionary
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate title
        if 'title' in data:
            title_valid, title_errors = self.validate_title(data['title'])
            if not title_valid:
                errors.extend(title_errors)
        
        # Validate owner
        if 'owner' in data:
            owner_valid, owner_errors = self.validate_email(data['owner'], 'owner')
            if not owner_valid:
                errors.extend(owner_errors)
        
        # Validate rationale
        if 'rationale' in data:
            rationale_valid, rationale_errors = self.validate_rationale(data['rationale'])
            if not rationale_valid:
                errors.extend(rationale_errors)
        
        # Validate due_date
        if 'due_date' in data:
            date_valid, date_errors = self.validate_date(data['due_date'])
            if not date_valid:
                errors.extend(date_errors)
        
        # Validate thread_link
        if 'thread_link' in data:
            url_valid, url_errors = self.validate_url(data['thread_link'], 'thread_link')
            if not url_valid:
                errors.extend(url_errors)
        
        # Validate participants
        if 'participants' in data:
            participants_valid, participants_errors = self.validate_participants(data['participants'])
            if not participants_valid:
                errors.extend(participants_errors)
        
        # Validate channel_id
        if 'channel_id' in data:
            channel_valid, channel_errors = self.validate_channel_id(data['channel_id'])
            if not channel_valid:
                errors.extend(channel_errors)
        
        return (len(errors) == 0, errors)
    
    def validate_title(self, title: str) -> Tuple[bool, List[str]]:
        """Validate decision title"""
        errors = []
        
        if not title or not title.strip():
            errors.append("Title cannot be empty")
        elif len(title) < 5:
            errors.append("Title must be at least 5 characters long")
        elif len(title) > 500:
            errors.append("Title must be less than 500 characters")
        
        return (len(errors) == 0, errors)
    
    def validate_rationale(self, rationale: str) -> Tuple[bool, List[str]]:
        """Validate decision rationale"""
        errors = []
        
        if not rationale or not rationale.strip():
            errors.append("Rationale cannot be empty")
        elif len(rationale) < 10:
            errors.append("Rationale must be at least 10 characters long")
        elif len(rationale) > 5000:
            errors.append("Rationale must be less than 5000 characters")
        
        return (len(errors) == 0, errors)
    
    def validate_email(self, email: str, field_name: str = 'email') -> Tuple[bool, List[str]]:
        """Validate email address"""
        errors = []
        
        if not email or not email.strip():
            errors.append(f"{field_name} cannot be empty")
        elif not self.EMAIL_PATTERN.match(email):
            errors.append(f"{field_name} must be a valid email address")
        
        return (len(errors) == 0, errors)
    
    def validate_url(self, url: str, field_name: str = 'url') -> Tuple[bool, List[str]]:
        """Validate URL"""
        errors = []
        
        if not url or not url.strip():
            errors.append(f"{field_name} cannot be empty")
        elif not self.URL_PATTERN.match(url):
            errors.append(f"{field_name} must be a valid URL (http:// or https://)")
        
        return (len(errors) == 0, errors)
    
    def validate_date(self, date_str: str) -> Tuple[bool, List[str]]:
        """Validate date in YYYY-MM-DD format"""
        errors = []
        
        if not date_str or not date_str.strip():
            errors.append("Date cannot be empty")
        elif not self.DATE_PATTERN.match(date_str):
            errors.append("Date must be in YYYY-MM-DD format")
        else:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date value")
        
        return (len(errors) == 0, errors)
    
    def validate_participants(self, participants: List[str]) -> Tuple[bool, List[str]]:
        """Validate participants list"""
        errors = []
        
        if not isinstance(participants, list):
            errors.append("Participants must be a list")
            return (False, errors)
        
        if len(participants) > 50:
            errors.append("Maximum 50 participants allowed")
        
        for i, participant in enumerate(participants):
            email_valid, email_errors = self.validate_email(participant, f'participant[{i}]')
            if not email_valid:
                errors.extend(email_errors)
        
        return (len(errors) == 0, errors)
    
    def validate_channel_id(self, channel_id: str) -> Tuple[bool, List[str]]:
        """Validate channel ID"""
        errors = []
        
        if not channel_id or not channel_id.strip():
            errors.append("Channel ID cannot be empty")
        elif len(channel_id) > 100:
            errors.append("Channel ID must be less than 100 characters")
        
        return (len(errors) == 0, errors)
    
    def validate_status(self, status: str) -> Tuple[bool, List[str]]:
        """Validate decision status"""
        errors = []
        
        valid_statuses = ['Open', 'In Progress', 'Completed', 'Archived']
        
        if status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return (len(errors) == 0, errors)
    
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text input to prevent injection attacks
        
        Args:
            text: Input text
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = text.strip()
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags (optional - depends on requirements)
        # sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        return sanitized
    
    def validate_query_params(self, params: Dict[str, Any], allowed_params: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate query parameters
        
        Args:
            params: Query parameters dictionary
            allowed_params: List of allowed parameter names
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        for param in params.keys():
            if param not in allowed_params:
                errors.append(f"Unknown parameter: {param}")
        
        return (len(errors) == 0, errors)
    
    def validate_pagination(self, limit: int, offset: int) -> Tuple[bool, List[str]]:
        """Validate pagination parameters"""
        errors = []
        
        if limit < 1:
            errors.append("Limit must be at least 1")
        elif limit > 1000:
            errors.append("Limit cannot exceed 1000")
        
        if offset < 0:
            errors.append("Offset cannot be negative")
        
        return (len(errors) == 0, errors)
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that required fields are present and non-empty
        
        Args:
            data: Data dictionary
            required_fields: List of required field names
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                errors.append(f"Field cannot be empty: {field}")
        
        return (len(errors) == 0, errors)
    
    def validate_field_types(self, data: Dict[str, Any], type_spec: Dict[str, type]) -> Tuple[bool, List[str]]:
        """
        Validate field types
        
        Args:
            data: Data dictionary
            type_spec: Dictionary mapping field names to expected types
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        for field, expected_type in type_spec.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
        
        return (len(errors) == 0, errors)
    
    def validate_and_sanitize(self, data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Comprehensive validation and sanitization
        
        Args:
            data: Input data
            validation_rules: Validation rules dictionary
        
        Returns:
            Tuple of (is_valid, sanitized_data, error_messages)
        """
        errors = []
        sanitized_data = {}
        
        for field, value in data.items():
            # Sanitize string fields
            if isinstance(value, str):
                sanitized_data[field] = self.sanitize_text(value)
            else:
                sanitized_data[field] = value
        
        # Apply validation rules
        if 'required' in validation_rules:
            valid, req_errors = self.validate_required_fields(sanitized_data, validation_rules['required'])
            if not valid:
                errors.extend(req_errors)
        
        if 'types' in validation_rules:
            valid, type_errors = self.validate_field_types(sanitized_data, validation_rules['types'])
            if not valid:
                errors.extend(type_errors)
        
        return (len(errors) == 0, sanitized_data, errors)
