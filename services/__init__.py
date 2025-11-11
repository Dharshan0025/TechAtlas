"""
Services Package
Centralized service initialization and management
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Service instances (lazy initialization)
_detector = None
_feasibility_analyzer = None
_embedder = None
_rag_engine = None
_vector_store = None
_analytics_engine = None
_risk_assessor = None
_search_engine = None
_expertise_mapper = None
_input_validator = None
_text_processor = None
_notification_manager = None
_audit_logger = None
_data_exporter = None


def get_detector():
    """Get or create DecisionDetector instance"""
    global _detector
    if _detector is None:
        from services.detector import DecisionDetector
        _detector = DecisionDetector()
        logger.info("DecisionDetector initialized")
    return _detector


def get_feasibility_analyzer():
    """Get or create FeasibilityAnalyzer instance"""
    global _feasibility_analyzer
    if _feasibility_analyzer is None:
        from services.feasibility_analyzer import FeasibilityAnalyzer
        _feasibility_analyzer = FeasibilityAnalyzer()
        logger.info("FeasibilityAnalyzer initialized")
    return _feasibility_analyzer


def get_embedder():
    """Get or create GeminiEmbedder instance"""
    global _embedder
    if _embedder is None:
        from services.embedder import GeminiEmbedder
        _embedder = GeminiEmbedder()
        logger.info("GeminiEmbedder initialized")
    return _embedder


def get_rag_engine():
    """Get or create RAGEngine instance"""
    global _rag_engine
    if _rag_engine is None:
        from services.rag_engine import RAGEngine
        _rag_engine = RAGEngine()
        logger.info("RAGEngine initialized")
    return _rag_engine


def get_vector_store():
    """Get or create VectorStore instance"""
    global _vector_store
    if _vector_store is None:
        from services.vector_store import VectorStore
        _vector_store = VectorStore()
        logger.info("VectorStore initialized")
    return _vector_store


def get_analytics_engine():
    """Get or create AnalyticsEngine instance"""
    global _analytics_engine
    if _analytics_engine is None:
        from services.analytics_engine import AnalyticsEngine
        _analytics_engine = AnalyticsEngine()
        logger.info("AnalyticsEngine initialized")
    return _analytics_engine


def get_risk_assessor():
    """Get or create RiskAssessor instance"""
    global _risk_assessor
    if _risk_assessor is None:
        from services.risk_assessor import RiskAssessor
        _risk_assessor = RiskAssessor()
        logger.info("RiskAssessor initialized")
    return _risk_assessor


def get_search_engine():
    """Get or create SearchEngine instance"""
    global _search_engine
    if _search_engine is None:
        from services.search_engine import SearchEngine
        _search_engine = SearchEngine()
        logger.info("SearchEngine initialized")
    return _search_engine


def get_expertise_mapper():
    """Get or create ExpertiseMapper instance"""
    global _expertise_mapper
    if _expertise_mapper is None:
        from services.expertise_mapper import ExpertiseMapper
        _expertise_mapper = ExpertiseMapper()
        logger.info("ExpertiseMapper initialized")
    return _expertise_mapper


def get_input_validator():
    """Get or create InputValidator instance"""
    global _input_validator
    if _input_validator is None:
        from services.input_validator import InputValidator
        _input_validator = InputValidator()
        logger.info("InputValidator initialized")
    return _input_validator


def get_text_processor():
    """Get or create TextProcessor instance"""
    global _text_processor
    if _text_processor is None:
        from services.text_processor import TextProcessor
        _text_processor = TextProcessor()
        logger.info("TextProcessor initialized")
    return _text_processor


def get_notification_manager():
    """Get or create NotificationManager instance"""
    global _notification_manager
    if _notification_manager is None:
        from services.notification_manager import NotificationManager
        _notification_manager = NotificationManager()
        logger.info("NotificationManager initialized")
    return _notification_manager


def get_audit_logger():
    """Get or create AuditLogger instance"""
    global _audit_logger
    if _audit_logger is None:
        from services.audit_logger import AuditLogger
        _audit_logger = AuditLogger()
        logger.info("AuditLogger initialized")
    return _audit_logger


def get_data_exporter():
    """Get or create DataExporter instance"""
    global _data_exporter
    if _data_exporter is None:
        from services.data_exporter import DataExporter
        _data_exporter = DataExporter()
        logger.info("DataExporter initialized")
    return _data_exporter


# Export all getter functions
__all__ = [
    'get_detector',
    'get_feasibility_analyzer',
    'get_embedder',
    'get_rag_engine',
    'get_vector_store',
    'get_analytics_engine',
    'get_risk_assessor',
    'get_search_engine',
    'get_expertise_mapper',
    'get_input_validator',
    'get_text_processor',
    'get_notification_manager',
    'get_audit_logger',
    'get_data_exporter'
]
