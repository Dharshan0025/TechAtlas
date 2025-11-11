"""
Data Exporter Service
Exports data in various formats
"""

from firebase_admin import firestore
import csv
import json
from io import StringIO, BytesIO
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """
    Exports data in various formats (CSV, JSON, etc.)
    """
    
    def __init__(self):
        """Initialize the Data Exporter"""
        self.db = firestore.client()
        logger.info("DataExporter initialized successfully")
    
    def export_decisions_csv(self, filters: Dict[str, Any] = None) -> str:
        """
        Export decisions to CSV format
        
        Args:
            filters: Optional filters (status, owner, channel_id)
        
        Returns:
            CSV string
        """
        try:
            # Get decisions
            decisions = self._get_decisions(filters)
            
            if not decisions:
                return ""
            
            # Create CSV
            output = StringIO()
            
            # Define fields
            fieldnames = [
                'decision_id', 'title', 'owner', 'status', 'created_at',
                'due_date', 'risk_score', 'risk_level', 'channel_id',
                'participants_count', 'rationale'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            # Write rows
            for decision in decisions:
                row = {
                    'decision_id': decision.get('decision_id', ''),
                    'title': decision.get('title', ''),
                    'owner': decision.get('owner', ''),
                    'status': decision.get('status', ''),
                    'created_at': decision.get('created_at', ''),
                    'due_date': decision.get('due_date', ''),
                    'risk_score': decision.get('risk_score', 0),
                    'risk_level': decision.get('risk_level', ''),
                    'channel_id': decision.get('channel_id', ''),
                    'participants_count': len(decision.get('participants', [])),
                    'rationale': decision.get('rationale', '')[:200]  # Truncate for CSV
                }
                writer.writerow(row)
            
            csv_data = output.getvalue()
            logger.info(f"Exported {len(decisions)} decisions to CSV")
            
            return csv_data
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            return ""
    
    def export_decisions_json(self, filters: Dict[str, Any] = None, pretty: bool = True) -> str:
        """
        Export decisions to JSON format
        
        Args:
            filters: Optional filters
            pretty: Pretty print JSON
        
        Returns:
            JSON string
        """
        try:
            # Get decisions
            decisions = self._get_decisions(filters)
            
            # Convert to JSON
            json_data = json.dumps(
                decisions,
                indent=2 if pretty else None,
                ensure_ascii=False
            )
            
            logger.info(f"Exported {len(decisions)} decisions to JSON")
            
            return json_data
            
        except Exception as e:
            logger.error(f"JSON export failed: {str(e)}")
            return "[]"
    
    def export_analytics_report(self, format: str = 'json') -> str:
        """
        Export analytics report
        
        Args:
            format: Export format ('json' or 'csv')
        
        Returns:
            Formatted report
        """
        try:
            from services.analytics_engine import AnalyticsEngine
            
            analytics = AnalyticsEngine()
            report_data = analytics.get_comprehensive_dashboard_stats()
            
            if format == 'csv':
                # Convert to CSV (simplified)
                output = StringIO()
                writer = csv.writer(output)
                
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Decisions', report_data.get('overview', {}).get('total_decisions', 0)])
                writer.writerow(['Open Decisions', report_data.get('overview', {}).get('open_decisions', 0)])
                writer.writerow(['Completion Rate', report_data.get('overview', {}).get('completion_rate', 0)])
                
                return output.getvalue()
            else:
                return json.dumps(report_data, indent=2)
                
        except Exception as e:
            logger.error(f"Analytics export failed: {str(e)}")
            return ""
    
    def export_user_report(self, user_email: str, format: str = 'json') -> str:
        """
        Export user activity report
        
        Args:
            user_email: User's email
            format: Export format
        
        Returns:
            Formatted report
        """
        try:
            # Get user's decisions
            decisions = self._get_decisions({'owner': user_email})
            
            # Get participation
            all_decisions = self._get_decisions()
            participated = [
                d for d in all_decisions
                if user_email in d.get('participants', []) and d.get('owner') != user_email
            ]
            
            report = {
                'user': user_email,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'decisions_owned': len(decisions),
                    'decisions_participated': len(participated),
                    'total_contributions': len(decisions) + len(participated)
                },
                'owned_decisions': decisions,
                'participated_decisions': participated
            }
            
            if format == 'json':
                return json.dumps(report, indent=2)
            else:
                # CSV format
                output = StringIO()
                writer = csv.writer(output)
                
                writer.writerow(['User Report', user_email])
                writer.writerow(['Generated', report['generated_at']])
                writer.writerow([])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Decisions Owned', report['summary']['decisions_owned']])
                writer.writerow(['Decisions Participated', report['summary']['decisions_participated']])
                
                return output.getvalue()
                
        except Exception as e:
            logger.error(f"User report export failed: {str(e)}")
            return ""
    
    def create_backup(self) -> Dict[str, Any]:
        """
        Create full database backup
        
        Returns:
            Backup data dictionary
        """
        try:
            backup = {
                'created_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0',
                'data': {
                    'decisions': self._get_decisions(),
                    # Add other collections as needed
                }
            }
            
            logger.info("Database backup created")
            return backup
            
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}")
            return {}
    
    def restore_from_backup(self, backup_data: Dict[str, Any]) -> bool:
        """
        Restore from backup
        
        Args:
            backup_data: Backup data dictionary
        
        Returns:
            True if successful
        """
        try:
            decisions = backup_data.get('data', {}).get('decisions', [])
            
            # Restore decisions
            for decision in decisions:
                decision_id = decision.get('decision_id')
                if decision_id:
                    self.db.collection('decisions').document(decision_id).set(decision)
            
            logger.info(f"Restored {len(decisions)} decisions from backup")
            return True
            
        except Exception as e:
            logger.error(f"Backup restore failed: {str(e)}")
            return False
    
    def _get_decisions(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get decisions with optional filters
        
        Args:
            filters: Filter criteria
        
        Returns:
            List of decisions
        """
        try:
            query = self.db.collection('decisions')
            
            # Apply filters
            if filters:
                if 'status' in filters:
                    query = query.where('status', '==', filters['status'])
                if 'owner' in filters:
                    query = query.where('owner', '==', filters['owner'])
                if 'channel_id' in filters:
                    query = query.where('channel_id', '==', filters['channel_id'])
            
            # Execute query
            decisions = []
            for doc in query.stream():
                decision_data = doc.to_dict()
                decision_data['id'] = doc.id
                decisions.append(decision_data)
            
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to get decisions: {str(e)}")
            return []
    
    def export_with_filters(self, export_config: Dict[str, Any]) -> str:
        """
        Export with comprehensive configuration
        
        Args:
            export_config: Export configuration
                - format: 'csv' or 'json'
                - filters: Filter criteria
                - fields: Fields to include
                - sort_by: Sort field
        
        Returns:
            Exported data
        """
        try:
            format_type = export_config.get('format', 'json')
            filters = export_config.get('filters', {})
            
            if format_type == 'csv':
                return self.export_decisions_csv(filters)
            else:
                return self.export_decisions_json(filters)
                
        except Exception as e:
            logger.error(f"Export with filters failed: {str(e)}")
            return ""
