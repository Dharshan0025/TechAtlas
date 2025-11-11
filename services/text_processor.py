"""
Text Processor Service
Processes and analyzes text content
"""

import re
from collections import Counter
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Processes and analyzes text content
    """
    
    # Common stop words to filter
    STOP_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
        'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
        'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did',
        'having', 'may', 'should', 'could', 'would', 'might', 'must', 'shall', 'can'
    }
    
    def __init__(self):
        """Initialize the Text Processor"""
        logger.info("TextProcessor initialized successfully")
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_keywords(self, text: str, top_n: int = 10, min_length: int = 4) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            min_length: Minimum keyword length
        
        Returns:
            List of keywords
        """
        try:
            # Clean text
            cleaned = self.clean_text(text)
            
            # Split into words
            words = cleaned.split()
            
            # Filter stop words and short words
            keywords = [
                word for word in words
                if word not in self.STOP_WORDS and len(word) >= min_length
            ]
            
            # Count frequencies
            word_freq = Counter(keywords)
            
            # Return top N
            return [word for word, count in word_freq.most_common(top_n)]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities (people, tools, dates) from text
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of entity types and values
        """
        try:
            entities = {
                'people': [],
                'tools': [],
                'dates': []
            }
            
            # Extract email addresses (people)
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            entities['people'] = list(set(emails))
            
            # Extract common tools/technologies (simple pattern matching)
            tool_patterns = [
                r'\b(postgresql|postgres|mysql|mongodb|redis|docker|kubernetes|aws|azure|gcp)\b',
                r'\b(python|java|javascript|typescript|react|angular|vue|node\.?js)\b',
                r'\b(git|github|gitlab|jenkins|circleci|travis)\b'
            ]
            
            for pattern in tool_patterns:
                matches = re.findall(pattern, text.lower())
                entities['tools'].extend(matches)
            
            entities['tools'] = list(set(entities['tools']))
            
            # Extract dates (YYYY-MM-DD format)
            dates = re.findall(r'\b\d{4}-\d{2}-\d{2}\b', text)
            entities['dates'] = list(set(dates))
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {'people': [], 'tools': [], 'dates': []}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Simple sentiment analysis
        
        Args:
            text: Input text
        
        Returns:
            Sentiment analysis results
        """
        try:
            # Simple keyword-based sentiment
            positive_words = {
                'good', 'great', 'excellent', 'better', 'best', 'improve', 'benefit',
                'advantage', 'success', 'effective', 'efficient', 'optimal', 'positive'
            }
            
            negative_words = {
                'bad', 'poor', 'worse', 'worst', 'problem', 'issue', 'risk', 'concern',
                'difficult', 'challenge', 'negative', 'fail', 'error', 'bug'
            }
            
            neutral_words = {
                'consider', 'evaluate', 'review', 'analyze', 'discuss', 'decide'
            }
            
            # Clean and tokenize
            cleaned = self.clean_text(text)
            words = set(cleaned.split())
            
            # Count sentiment words
            positive_count = len(words & positive_words)
            negative_count = len(words & negative_words)
            neutral_count = len(words & neutral_words)
            
            # Determine overall sentiment
            if positive_count > negative_count:
                sentiment = 'positive'
                score = min(1.0, positive_count / max(1, len(words)) * 10)
            elif negative_count > positive_count:
                sentiment = 'negative'
                score = -min(1.0, negative_count / max(1, len(words)) * 10)
            else:
                sentiment = 'neutral'
                score = 0.0
            
            return {
                'sentiment': sentiment,
                'score': round(score, 2),
                'positive_words': positive_count,
                'negative_words': negative_count,
                'neutral_words': neutral_count
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {'sentiment': 'neutral', 'score': 0.0}
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Simple text summarization
        
        Args:
            text: Input text
            max_sentences: Maximum sentences in summary
        
        Returns:
            Summarized text
        """
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= max_sentences:
                return text
            
            # Simple scoring: prefer longer sentences with keywords
            scored_sentences = []
            for sentence in sentences:
                score = len(sentence.split())  # Length score
                keywords = self.extract_keywords(sentence, top_n=5)
                score += len(keywords) * 2  # Keyword bonus
                
                scored_sentences.append((sentence, score))
            
            # Sort by score and take top N
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            top_sentences = [s[0] for s in scored_sentences[:max_sentences]]
            
            # Maintain original order
            summary_sentences = []
            for sentence in sentences:
                if sentence in top_sentences:
                    summary_sentences.append(sentence)
                if len(summary_sentences) >= max_sentences:
                    break
            
            return '. '.join(summary_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return text[:200] + '...' if len(text) > 200 else text
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection
        
        Args:
            text: Input text
        
        Returns:
            Detected language code
        """
        # Very simple detection based on common words
        # In production, use a proper library like langdetect
        
        english_words = {'the', 'is', 'and', 'to', 'of', 'a', 'in', 'that'}
        
        words = set(self.clean_text(text).split())
        english_count = len(words & english_words)
        
        if english_count > 0:
            return 'en'
        else:
            return 'unknown'
    
    def detect_duplicates(self, text1: str, text2: str, threshold: float = 0.8) -> bool:
        """
        Detect if two texts are duplicates
        
        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold (0-1)
        
        Returns:
            True if texts are duplicates
        """
        try:
            # Clean texts
            clean1 = set(self.clean_text(text1).split())
            clean2 = set(self.clean_text(text2).split())
            
            if not clean1 or not clean2:
                return False
            
            # Calculate Jaccard similarity
            intersection = len(clean1 & clean2)
            union = len(clean1 | clean2)
            
            similarity = intersection / union if union > 0 else 0
            
            return similarity >= threshold
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            return False
    
    def extract_action_items(self, text: str) -> List[str]:
        """
        Extract action items from text
        
        Args:
            text: Input text
        
        Returns:
            List of action items
        """
        try:
            action_patterns = [
                r'(?:need to|should|must|will|going to)\s+([^.!?]+)',
                r'(?:action item|todo|task):\s*([^.!?]+)',
                r'(?:please|kindly)\s+([^.!?]+)'
            ]
            
            action_items = []
            
            for pattern in action_patterns:
                matches = re.findall(pattern, text.lower())
                action_items.extend(matches)
            
            # Clean and deduplicate
            action_items = [item.strip() for item in action_items if item.strip()]
            action_items = list(set(action_items))
            
            return action_items[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Action item extraction failed: {str(e)}")
            return []
