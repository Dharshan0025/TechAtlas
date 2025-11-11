"""
Tests for FeasibilityAnalyzer Service
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.feasibility_analyzer import FeasibilityAnalyzer


class TestFeasibilityAnalyzer:
    """Test suite for FeasibilityAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return FeasibilityAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.model is not None
    
    def test_analyze_basic_decision(self, analyzer):
        """Test basic feasibility analysis"""
        result = analyzer.analyze(
            title="Migrate to PostgreSQL",
            rationale="Need better join support and ACID compliance",
            context="Currently using MySQL"
        )
        
        # Check structure
        assert 'strengths' in result
        assert 'risks' in result
        assert 'alternatives' in result
        assert 'recommendation' in result
        assert 'feasibility_score' in result
        assert 'risk_level' in result
        assert 'confidence' in result
        
        # Check types
        assert isinstance(result['strengths'], list)
        assert isinstance(result['risks'], list)
        assert isinstance(result['alternatives'], list)
        assert isinstance(result['feasibility_score'], (int, float))
        assert isinstance(result['risk_level'], str)
        
        # Check score range
        assert 0 <= result['feasibility_score'] <= 100
        
        # Check risk level values
        assert result['risk_level'] in ['Low', 'Medium', 'High']
    
    def test_calculate_feasibility_score(self, analyzer):
        """Test feasibility score calculation"""
        # Test with many strengths, few risks
        analysis = {
            'strengths': ['benefit1', 'benefit2', 'benefit3', 'benefit4'],
            'risks': ['risk1'],
            'alternatives': [{'option': 'alt1'}]
        }
        score = analyzer._calculate_feasibility_score(analysis)
        assert score > 50  # Should be positive
        
        # Test with few strengths, many risks
        analysis = {
            'strengths': ['benefit1'],
            'risks': ['risk1', 'risk2', 'risk3', 'risk4'],
            'alternatives': []
        }
        score = analyzer._calculate_feasibility_score(analysis)
        assert score < 50  # Should be negative
    
    def test_determine_risk_level(self, analyzer):
        """Test risk level determination"""
        analysis = {'risks': ['risk1', 'risk2']}
        
        # High score, few risks = Low risk
        risk_level = analyzer._determine_risk_level(80, analysis)
        assert risk_level == 'Low'
        
        # Low score, many risks = High risk
        analysis['risks'] = ['r1', 'r2', 'r3', 'r4', 'r5']
        risk_level = analyzer._determine_risk_level(30, analysis)
        assert risk_level == 'High'
    
    def test_generate_recommendation(self, analyzer):
        """Test recommendation generation"""
        # High score
        rec = analyzer._generate_recommendation(80, 'Low')
        assert 'proceed' in rec.lower()
        
        # Medium score
        rec = analyzer._generate_recommendation(60, 'Medium')
        assert 'caution' in rec.lower()
        
        # Low score
        rec = analyzer._generate_recommendation(30, 'High')
        assert 'risk' in rec.lower() or 'reconsider' in rec.lower()
    
    def test_fallback_analysis(self, analyzer):
        """Test fallback analysis when AI fails"""
        fallback = analyzer._get_fallback_analysis()
        
        assert fallback['feasibility_score'] == 50.0
        assert fallback['risk_level'] == 'Medium'
        assert fallback['confidence'] == 0.3
        assert len(fallback['strengths']) > 0
        assert len(fallback['risks']) > 0
    
    def test_analyze_with_empty_context(self, analyzer):
        """Test analysis with empty context"""
        result = analyzer.analyze(
            title="Test Decision",
            rationale="Test rationale",
            context=""
        )
        
        assert result is not None
        assert 'feasibility_score' in result
    
    def test_analyze_with_history(self, analyzer):
        """Test analysis with past decisions"""
        past_decisions = [
            {
                'title': 'Similar Decision',
                'status': 'Completed',
                'similarity_score': 0.85
            }
        ]
        
        result = analyzer.analyze_with_history(
            title="New Decision",
            rationale="Test rationale",
            context="",
            past_decisions=past_decisions
        )
        
        assert result is not None
        assert 'past_decisions' in result
        assert len(result['past_decisions']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
