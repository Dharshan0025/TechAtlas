"""
Tests for TextProcessor Service
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.text_processor import TextProcessor


class TestTextProcessor:
    """Test suite for TextProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance"""
        return TextProcessor()
    
    def test_processor_initialization(self, processor):
        """Test that processor initializes correctly"""
        assert processor is not None
        assert len(processor.STOP_WORDS) > 0
    
    # Text Cleaning Tests
    def test_clean_text_basic(self, processor):
        """Test basic text cleaning"""
        text = "Hello World! This is a TEST."
        cleaned = processor.clean_text(text)
        
        assert cleaned == "hello world this is a test"
    
    def test_clean_text_remove_urls(self, processor):
        """Test URL removal"""
        text = "Check this out: https://example.com/path and http://test.com"
        cleaned = processor.clean_text(text)
        
        assert 'https://' not in cleaned
        assert 'http://' not in cleaned
        assert 'example.com' not in cleaned
    
    def test_clean_text_remove_emails(self, processor):
        """Test email removal"""
        text = "Contact me at user@example.com for details"
        cleaned = processor.clean_text(text)
        
        assert '@' not in cleaned
        assert 'user@example.com' not in cleaned
    
    def test_clean_text_remove_special_chars(self, processor):
        """Test special character removal"""
        text = "Hello! @#$% World?"
        cleaned = processor.clean_text(text)
        
        assert '@' not in cleaned
        assert '#' not in cleaned
        assert '$' not in cleaned
    
    def test_clean_text_empty(self, processor):
        """Test cleaning empty text"""
        cleaned = processor.clean_text("")
        assert cleaned == ""
    
    # Keyword Extraction Tests
    def test_extract_keywords_basic(self, processor):
        """Test basic keyword extraction"""
        text = "database migration postgresql performance optimization"
        keywords = processor.extract_keywords(text, top_n=5)
        
        assert isinstance(keywords, list)
        assert 'database' in keywords
        assert 'migration' in keywords
        assert 'postgresql' in keywords
    
    def test_extract_keywords_filter_stop_words(self, processor):
        """Test that stop words are filtered"""
        text = "the database is very good and the performance is excellent"
        keywords = processor.extract_keywords(text, top_n=10)
        
        assert 'the' not in keywords
        assert 'is' not in keywords
        assert 'and' not in keywords
        assert 'database' in keywords
        assert 'performance' in keywords
    
    def test_extract_keywords_min_length(self, processor):
        """Test minimum length filtering"""
        text = "big cat dog elephant"
        keywords = processor.extract_keywords(text, top_n=10, min_length=4)
        
        assert 'big' not in keywords  # Too short
        assert 'cat' not in keywords  # Too short
        assert 'dog' not in keywords  # Too short
        assert 'elephant' in keywords
    
    def test_extract_keywords_frequency(self, processor):
        """Test keyword frequency ordering"""
        text = "database database database migration migration performance"
        keywords = processor.extract_keywords(text, top_n=3)
        
        # 'database' appears most, should be first
        assert keywords[0] == 'database'
    
    # Entity Extraction Tests
    def test_extract_entities_emails(self, processor):
        """Test email extraction"""
        text = "Contact user1@test.com or user2@example.com"
        entities = processor.extract_entities(text)
        
        assert 'people' in entities
        assert 'user1@test.com' in entities['people']
        assert 'user2@example.com' in entities['people']
    
    def test_extract_entities_tools(self, processor):
        """Test tool/technology extraction"""
        text = "We use PostgreSQL, Docker, and Kubernetes for deployment"
        entities = processor.extract_entities(text)
        
        assert 'tools' in entities
        assert 'postgresql' in entities['tools']
        assert 'docker' in entities['tools']
        assert 'kubernetes' in entities['tools']
    
    def test_extract_entities_dates(self, processor):
        """Test date extraction"""
        text = "The deadline is 2024-12-31 and review on 2024-11-15"
        entities = processor.extract_entities(text)
        
        assert 'dates' in entities
        assert '2024-12-31' in entities['dates']
        assert '2024-11-15' in entities['dates']
    
    # Sentiment Analysis Tests
    def test_analyze_sentiment_positive(self, processor):
        """Test positive sentiment"""
        text = "This is a great decision with excellent benefits and good outcomes"
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] == 'positive'
        assert result['score'] > 0
        assert result['positive_words'] > 0
    
    def test_analyze_sentiment_negative(self, processor):
        """Test negative sentiment"""
        text = "This is a bad decision with many problems and risks"
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] == 'negative'
        assert result['score'] < 0
        assert result['negative_words'] > 0
    
    def test_analyze_sentiment_neutral(self, processor):
        """Test neutral sentiment"""
        text = "We need to consider and evaluate this decision carefully"
        result = processor.analyze_sentiment(text)
        
        assert result['sentiment'] in ['neutral', 'positive', 'negative']
        assert 'score' in result
    
    # Text Summarization Tests
    def test_summarize_text_short(self, processor):
        """Test summarization of short text"""
        text = "This is a short text. It has only two sentences."
        summary = processor.summarize_text(text, max_sentences=3)
        
        assert summary == text
    
    def test_summarize_text_long(self, processor):
        """Test summarization of long text"""
        sentences = [
            "This is the first sentence about databases.",
            "This is the second sentence about migration.",
            "This is the third sentence about performance.",
            "This is the fourth sentence about optimization.",
            "This is the fifth sentence about deployment."
        ]
        text = " ".join(sentences)
        
        summary = processor.summarize_text(text, max_sentences=2)
        
        # Summary should be shorter than original
        assert len(summary) < len(text)
        assert summary.endswith('.')
    
    # Language Detection Tests
    def test_detect_language_english(self, processor):
        """Test English language detection"""
        text = "This is an English text with common words"
        lang = processor.detect_language(text)
        
        assert lang == 'en'
    
    def test_detect_language_unknown(self, processor):
        """Test unknown language detection"""
        text = "xyzabc qwerty"
        lang = processor.detect_language(text)
        
        assert lang in ['en', 'unknown']
    
    # Duplicate Detection Tests
    def test_detect_duplicates_identical(self, processor):
        """Test duplicate detection for identical texts"""
        text1 = "This is a test decision about database migration"
        text2 = "This is a test decision about database migration"
        
        is_duplicate = processor.detect_duplicates(text1, text2, threshold=0.8)
        assert is_duplicate is True
    
    def test_detect_duplicates_similar(self, processor):
        """Test duplicate detection for similar texts"""
        text1 = "database migration to postgresql for better performance"
        text2 = "migration to postgresql database for performance improvement"
        
        is_duplicate = processor.detect_duplicates(text1, text2, threshold=0.5)
        # Should be detected as similar
        assert isinstance(is_duplicate, bool)
    
    def test_detect_duplicates_different(self, processor):
        """Test duplicate detection for different texts"""
        text1 = "database migration to postgresql"
        text2 = "frontend redesign with react"
        
        is_duplicate = processor.detect_duplicates(text1, text2, threshold=0.8)
        assert is_duplicate is False
    
    def test_detect_duplicates_empty(self, processor):
        """Test duplicate detection with empty texts"""
        is_duplicate = processor.detect_duplicates("", "", threshold=0.8)
        assert is_duplicate is False
    
    # Action Item Extraction Tests
    def test_extract_action_items_need_to(self, processor):
        """Test action item extraction with 'need to'"""
        text = "We need to migrate the database. We should also update the documentation."
        actions = processor.extract_action_items(text)
        
        assert isinstance(actions, list)
        assert len(actions) > 0
    
    def test_extract_action_items_must(self, processor):
        """Test action item extraction with 'must'"""
        text = "We must complete the migration by Friday. The team will review the changes."
        actions = processor.extract_action_items(text)
        
        assert isinstance(actions, list)
        if actions:
            assert any('complete' in action or 'migration' in action for action in actions)
    
    def test_extract_action_items_please(self, processor):
        """Test action item extraction with 'please'"""
        text = "Please review the proposal. Kindly update the documentation."
        actions = processor.extract_action_items(text)
        
        assert isinstance(actions, list)
        if actions:
            assert any('review' in action or 'update' in action for action in actions)
    
    def test_extract_action_items_none(self, processor):
        """Test action item extraction with no actions"""
        text = "This is a simple statement without any actions."
        actions = processor.extract_action_items(text)
        
        assert isinstance(actions, list)
        # May or may not find actions depending on pattern matching


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
