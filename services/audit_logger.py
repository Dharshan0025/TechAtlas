"""
Audit Logger Service
Tracks and logs all system actions for compliance
"""

from firebase_admin import firestore
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs all system actions for audit trail
    """
    
    def __init__(self):
        """Initialize the Audit Logger"""
        self.db = firestore.client()
        logger.info("AuditLogger initialized successfully")
    
    def log_action(self, action: str, user: str, resource_type: str, 
                   resource_id: str, details: Dict[str, Any] = None) -> bool:
        """
        Log an action to the audit trail
        
        Args:
            action: Action performed (create, update, delete, view, etc.)
            user: User who performed the action
            resource_type: Type of resource (decision, user, etc.)
            resource_id: ID of the resource
            details: Additional details
        
        Returns:
            True if logged successfully
        """
        try:
            audit_entry = {
                'action': action,
                'user': user,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'details': details or {},
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'ip_address': None,  # TODO: Capture from request
                'user_agent': None   # TODO: Capture from request
            }
            
            # Store in Firestore
            self.db.collection('audit_logs').add(audit_entry)
            
            logger.debug(f"Audit log: {action} on {resource_type}:{resource_id} by {user}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
            return False
    
    def log_decision_created(self, decision_id: str, user: str, decision_data: Dict[str, Any]) -> bool:
        """Log decision creation"""
        return self.log_action(
            action='create',
            user=user,
            resource_type='decision',
            resource_id=decision_id,
            details={
                'title': decision_data.get('title', ''),
                'owner': decision_data.get('owner', '')
            }
        )
    
    def log_decision_updated(self, decision_id: str, user: str, changes: Dict[str, Any]) -> bool:
        """Log decision update"""
        return self.log_action(
            action='update',
            user=user,
            resource_type='decision',
            resource_id=decision_id,
            details={'changes': changes}
        )
    
    def log_decision_deleted(self, decision_id: str, user: str) -> bool:
        """Log decision deletion"""
        return self.log_action(
            action='delete',
            user=user,
            resource_type='decision',
            resource_id=decision_id
        )
    
    def log_decision_viewed(self, decision_id: str, user: str) -> bool:
        """Log decision view"""
        return self.log_action(
            action='view',
            user=user,
            resource_type='decision',
            resource_id=decision_id
        )
    
    def log_search(self, user: str, query: str, results_count: int) -> bool:
        """Log search query"""
        return self.log_action(
            action='search',
            user=user,
            resource_type='system',
            resource_id='search',
            details={
                'query': query,
                'results_count': results_count
            }
        )
    
    def log_export(self, user: str, export_type: str, record_count: int) -> bool:
        """Log data export"""
        return self.log_action(
            action='export',
            user=user,
            resource_type='system',
            resource_id='export',
            details={
                'export_type': export_type,
                'record_count': record_count
            }
        )
    
    def log_login(self, user: str, success: bool) -> bool:
        """Log login attempt"""
        return self.log_action(
            action='login' if success else 'login_failed',
            user=user,
            resource_type='auth',
            resource_id='login',
            details={'success': success}
        )
    
    def get_audit_logs(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with filters
        
        Args:
            filters: Filter criteria (user, action, resource_type, date_range)
            limit: Maximum number of logs to return
        
        Returns:
            List of audit log entries
        """
        try:
            query = self.db.collection('audit_logs')
            
            # Apply filters
            if filters:
                if 'user' in filters:
                    query = query.where('user', '==', filters['user'])
                if 'action' in filters:
                    query = query.where('action', '==', filters['action'])
                if 'resource_type' in filters:
                    query = query.where('resource_type', '==', filters['resource_type'])
            
            # Order by timestamp descending
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            # Execute query
            logs = []
            for doc in query.stream():
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {str(e)}")
            return []
    
    def get_user_activity(self, user: str, days: int = 30) -> Dict[str, Any]:
        """
        Get user activity summary
        
        Args:
            user: User email
            days: Number of days to analyze
        
        Returns:
            User activity summary
        """
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            logs = self.get_audit_logs(filters={'user': user}, limit=1000)
            
            # Filter by date
            recent_logs = [
                log for log in logs
                if log.get('timestamp', '') >= cutoff_date
            ]
            
            # Analyze activity
            action_counts = {}
            for log in recent_logs:
                action = log.get('action', 'unknown')
                action_counts[action] = action_counts.get(action, 0) + 1
            
            return {
                'user': user,
                'period_days': days,
                'total_actions': len(recent_logs),
                'action_breakdown': action_counts,
                'most_common_action': max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None,
                'last_activity': recent_logs[0].get('timestamp') if recent_logs else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user activity: {str(e)}")
            return {}
    
    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate compliance report for a date range
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
        
        Returns:
            Compliance report
        """
        try:
            logs = self.get_audit_logs(limit=10000)
            
            # Filter by date range
            filtered_logs = [
                log for log in logs
                if start_date <= log.get('timestamp', '') <= end_date
            ]
            
            # Analyze
            total_actions = len(filtered_logs)
            unique_users = len(set(log.get('user') for log in filtered_logs))
            
            action_summary = {}
            for log in filtered_logs:
                action = log.get('action', 'unknown')
                action_summary[action] = action_summary.get(action, 0) + 1
            
            return {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'summary': {
                    'total_actions': total_actions,
                    'unique_users': unique_users,
                    'actions_per_day': round(total_actions / max(1, (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days), 2)
                },
                'action_breakdown': action_summary,
                'top_users': self._get_top_users_from_logs(filtered_logs, top_n=10)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {str(e)}")
            return {}
    
    def _get_top_users_from_logs(self, logs: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top users by activity from logs"""
        user_counts = {}
        for log in logs:
            user = log.get('user', 'unknown')
            user_counts[user] = user_counts.get(user, 0) + 1
        
        top_users = [
            {'user': user, 'action_count': count}
            for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        ]
        
        return top_users
    
    def cleanup_old_logs(self, days_to_keep: int = 365) -> int:
        """
        Clean up old audit logs
        
        Args:
            days_to_keep: Number of days to retain
        
        Returns:
            Number of logs deleted
        """
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).isoformat()
            
            # Query old logs
            old_logs = self.db.collection('audit_logs').where('timestamp', '<', cutoff_date).stream()
            
            deleted_count = 0
            for doc in old_logs:
                doc.reference.delete()
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old audit logs")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {str(e)}")
            return 0
