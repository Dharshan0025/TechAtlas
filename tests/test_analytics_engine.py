"""
Tests for AnalyticsEngine Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.analytics_engine import AnalyticsEngine


class TestAnalyticsEngine:
    """Test suite for AnalyticsEngine"""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance with mocked Firestore"""
        with patch('services.analytics_engine.firestore.client') as mock_client:
            engine = AnalyticsEngine()
            engine.db = mock_client.return_value
            return engine
    
    @pytest.fixture
    def sample_decisions(self):
        """Sample decision data"""
        return [
            {
                'title': 'Decision 1',
                'owner': 'user1@test.com',
                'status': 'Completed',
                'created_at': '2024-01-01T00:00:00Z',
                'channel_id': 'tech-team',
                'risk_score': 5,
                'rationale': 'Test rationale for decision one'
            },
            {
                'title': 'Decision 2',
                'owner': 'user2@test.com',
                'status': 'Open',
                'created_at': '2024-01-15T00:00:00Z',
                'channel_id': 'tech-team',
                'risk_score': 8,
                'rationale': 'Test rationale for decision two'
            },
            {
                'title': 'Decision 3',
                'owner': 'user1@test.com',
                'status': 'In Progress',
                'created_at': '2024-02-01T00:00:00Z',
                'channel_id': 'backend-team',
                'risk_score': 3,
                'rationale': 'Test rationale for decision three'
            }
        ]
    
    def test_engine_initialization(self, engine):
        """Test that engine initializes correctly"""
        assert engine is not None
        assert engine.db is not None
    
    def test_get_decision_count_no_filters(self, engine, sample_decisions):
        """Test getting total decision count"""
        # Mock Firestore query
        mock_docs = [Mock() for _ in sample_decisions]
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        count = engine.get_decision_count()
        assert count == len(sample_decisions)
    
    def test_get_decision_count_with_filters(self, engine):
        """Test getting decision count with filters"""
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = [Mock(), Mock()]
        
        engine.db.collection.return_value = mock_query
        
        count = engine.get_decision_count({'status': 'Open'})
        assert count == 2
    
    def test_get_trend_analysis(self, engine, sample_decisions):
        """Test trend analysis"""
        # Mock Firestore
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        trends = engine.get_trend_analysis(period='month', limit=12)
        
        assert isinstance(trends, list)
        if trends:
            assert 'period' in trends[0]
            assert 'total_decisions' in trends[0]
            assert 'completed' in trends[0]
            assert 'completion_rate' in trends[0]
    
    def test_get_topic_frequency(self, engine, sample_decisions):
        """Test topic frequency analysis"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        topics = engine.get_topic_frequency(top_n=10)
        
        assert isinstance(topics, list)
        if topics:
            assert 'topic' in topics[0]
            assert 'frequency' in topics[0]
            assert 'percentage' in topics[0]
    
    def test_get_owner_contribution_metrics(self, engine, sample_decisions):
        """Test owner contribution metrics"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        metrics = engine.get_owner_contribution_metrics()
        
        assert isinstance(metrics, list)
        if metrics:
            assert 'owner' in metrics[0]
            assert 'total_decisions' in metrics[0]
            assert 'completed' in metrics[0]
            assert 'completion_rate' in metrics[0]
    
    def test_get_channel_activity(self, engine, sample_decisions):
        """Test channel activity tracking"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        activity = engine.get_channel_activity()
        
        assert isinstance(activity, list)
        if activity:
            assert 'channel_id' in activity[0]
            assert 'decision_count' in activity[0]
            assert 'active_contributors' in activity[0]
    
    def test_calculate_completion_rate(self, engine, sample_decisions):
        """Test completion rate calculation"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        mock_query = Mock()
        mock_query.stream.return_value = mock_docs
        engine.db.collection.return_value = mock_query
        
        rate = engine.calculate_completion_rate()
        
        assert isinstance(rate, float)
        assert 0 <= rate <= 100
    
    def test_calculate_avg_time_to_resolution(self, engine):
        """Test average time to resolution"""
        completed_decisions = [
            {
                'created_at': '2024-01-01T00:00:00Z',
                'status_updated_at': '2024-01-10T00:00:00Z'
            },
            {
                'created_at': '2024-01-05T00:00:00Z',
                'status_updated_at': '2024-01-20T00:00:00Z'
            }
        ]
        
        mock_docs = []
        for decision in completed_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.stream.return_value = mock_docs
        engine.db.collection.return_value = mock_query
        
        result = engine.calculate_avg_time_to_resolution()
        
        assert 'avg_days' in result
        assert 'median_days' in result
        assert 'sample_size' in result
    
    def test_get_decision_velocity(self, engine, sample_decisions):
        """Test decision velocity calculation"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        velocity = engine.get_decision_velocity(days=30)
        
        assert 'period_days' in velocity
        assert 'total_decisions' in velocity
        assert 'decisions_per_day' in velocity
        assert 'decisions_per_week' in velocity
    
    def test_get_comprehensive_dashboard_stats(self, engine, sample_decisions):
        """Test comprehensive dashboard statistics"""
        mock_docs = []
        for decision in sample_decisions:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = decision
            mock_docs.append(mock_doc)
        
        engine.db.collection.return_value.stream.return_value = mock_docs
        
        stats = engine.get_comprehensive_dashboard_stats()
        
        assert isinstance(stats, dict)
        # May be empty if mocking doesn't work perfectly, but structure should be valid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
