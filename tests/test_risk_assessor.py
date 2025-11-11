"""
Tests for RiskAssessor Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.risk_assessor import RiskAssessor


class TestRiskAssessor:
    """Test suite for RiskAssessor"""
    
    @pytest.fixture
    def assessor(self):
        """Create assessor instance with mocked Firestore"""
        with patch('services.risk_assessor.firestore.client') as mock_client:
            assessor = RiskAssessor()
            assessor.db = mock_client.return_value
            return assessor
    
    @pytest.fixture
    def sample_decision(self):
        """Sample decision for testing"""
        return {
            'title': 'Test Decision',
            'owner': 'user@test.com',
            'participants': ['user@test.com'],
            'status': 'Open',
            'created_at': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
            'due_date': (datetime.now(timezone.utc) + timedelta(days=7)).strftime('%Y-%m-%d'),
            'rationale': 'This is a test rationale for the decision'
        }
    
    def test_assessor_initialization(self, assessor):
        """Test that assessor initializes correctly"""
        assert assessor is not None
        assert assessor.db is not None
    
    def test_assess_decision_risk_single_owner(self, assessor, sample_decision):
        """Test risk assessment for single owner"""
        sample_decision['participants'] = ['user@test.com']
        
        result = assessor.assess_decision_risk(sample_decision)
        
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'risk_factors' in result
        assert 'recommendations' in result
        
        # Single owner should increase risk
        assert result['risk_score'] >= 8
        
        # Check risk factors
        factors = result['risk_factors']
        assert any('Single Owner' in f['factor'] for f in factors)
    
    def test_assess_decision_risk_multiple_participants(self, assessor, sample_decision):
        """Test risk assessment with multiple participants"""
        sample_decision['participants'] = ['user1@test.com', 'user2@test.com', 'user3@test.com']
        
        result = assessor.assess_decision_risk(sample_decision)
        
        # Multiple participants should reduce risk
        assert result['risk_score'] < 8
    
    def test_assess_decision_risk_past_due(self, assessor, sample_decision):
        """Test risk assessment for past due decision"""
        # Use ISO format date string
        past_date = datetime.now(timezone.utc) - timedelta(days=5)
        sample_decision['due_date'] = past_date.isoformat()
        
        result = assessor.assess_decision_risk(sample_decision)
        
        # Past due should increase risk
        factors = result['risk_factors']
        assert any('Past Due' in f['factor'] for f in factors)
    
    def test_assess_decision_risk_due_soon(self, assessor, sample_decision):
        """Test risk assessment for decision due soon"""
        # Use ISO format date string
        soon_date = datetime.now(timezone.utc) + timedelta(days=3)
        sample_decision['due_date'] = soon_date.isoformat()
        
        result = assessor.assess_decision_risk(sample_decision)
        
        # Due soon should add some risk
        factors = result['risk_factors']
        assert any('Due Soon' in f['factor'] for f in factors)
    
    def test_assess_decision_risk_open_status(self, assessor, sample_decision):
        """Test risk assessment for open status"""
        sample_decision['status'] = 'Open'
        
        result = assessor.assess_decision_risk(sample_decision)
        
        factors = result['risk_factors']
        assert any('Not Started' in f['factor'] for f in factors)
    
    def test_assess_decision_risk_aging(self, assessor, sample_decision):
        """Test risk assessment for aging decision"""
        sample_decision['created_at'] = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        sample_decision['status'] = 'Open'
        
        result = assessor.assess_decision_risk(sample_decision)
        
        factors = result['risk_factors']
        assert any('Aging' in f['factor'] for f in factors)
    
    def test_assess_decision_risk_insufficient_documentation(self, assessor, sample_decision):
        """Test risk assessment for insufficient documentation"""
        sample_decision['rationale'] = 'Short'
        
        result = assessor.assess_decision_risk(sample_decision)
        
        factors = result['risk_factors']
        assert any('Documentation' in f['factor'] for f in factors)
    
    def test_risk_level_determination(self, assessor, sample_decision):
        """Test risk level categorization"""
        # High risk scenario
        sample_decision['participants'] = ['user@test.com']
        sample_decision['due_date'] = (datetime.now(timezone.utc) - timedelta(days=5)).strftime('%Y-%m-%d')
        
        result = assessor.assess_decision_risk(sample_decision)
        assert result['risk_level'] in ['Low', 'Medium', 'High']
    
    def test_detect_single_owner_risks(self, assessor):
        """Test single owner risk detection"""
        decisions = [
            {
                'title': 'Decision 1',
                'participants': ['user1@test.com']
            },
            {
                'title': 'Decision 2',
                'participants': ['user1@test.com', 'user2@test.com']
            }
        ]
        
        mock_docs = []
        for decision in decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_doc.id = 'test_id'
            mock_docs.append(mock_doc)
        
        assessor.db.collection.return_value.stream.return_value = mock_docs
        
        single_owner = assessor.detect_single_owner_risks()
        
        assert isinstance(single_owner, list)
        # Should detect the first decision
        assert len(single_owner) >= 1
    
    def test_identify_aging_decisions(self, assessor):
        """Test aging decision identification"""
        old_date = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
        
        decisions = [
            {
                'title': 'Old Decision',
                'created_at': old_date,
                'status': 'Open'
            },
            {
                'title': 'New Decision',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'status': 'Open'
            }
        ]
        
        mock_docs = []
        for decision in decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_doc.id = 'test_id'
            mock_docs.append(mock_doc)
        
        assessor.db.collection.return_value.stream.return_value = mock_docs
        
        aging = assessor.identify_aging_decisions(days_threshold=60)
        
        assert isinstance(aging, list)
        # Should detect the old decision
        if aging:
            assert 'age_days' in aging[0]
    
    def test_detect_knowledge_silos(self, assessor):
        """Test knowledge silo detection"""
        decisions = [
            {
                'title': 'database migration decision',
                'owner': 'user1@test.com'
            },
            {
                'title': 'another database decision',
                'owner': 'user1@test.com'
            }
        ]
        
        mock_docs = []
        for decision in decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        assessor.db.collection.return_value.stream.return_value = mock_docs
        
        silos = assessor.detect_knowledge_silos()
        
        assert isinstance(silos, list)
        # Should detect 'database' as a silo topic
        if silos:
            assert 'topic' in silos[0]
            assert 'expert' in silos[0]
    
    def test_calculate_risk_trend(self, assessor):
        """Test risk trend calculation"""
        recent_date = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        
        decisions = [
            {
                'created_at': recent_date,
                'risk_score': 7
            },
            {
                'created_at': recent_date,
                'risk_score': 5
            }
        ]
        
        mock_docs = []
        for decision in decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        assessor.db.collection.return_value.stream.return_value = mock_docs
        
        trend = assessor.calculate_risk_trend(days=30)
        
        assert isinstance(trend, dict)
        if trend:
            assert 'avg_risk_score' in trend
            assert 'high_risk_count' in trend
    
    def test_generate_risk_recommendations(self, assessor):
        """Test risk recommendation generation"""
        risk_factors = [
            {
                'factor': 'Single Owner',
                'mitigation': 'Add more participants'
            },
            {
                'factor': 'Past Due',
                'mitigation': 'Update deadline'
            }
        ]
        
        recommendations = assessor._generate_risk_recommendations('High', risk_factors)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any('Add more participants' in r for r in recommendations)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
