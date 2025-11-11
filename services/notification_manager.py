"""
Notification Manager Service
Handles notifications and reminders
"""

from datetime import datetime, timezone
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages notifications and reminders
    """
    
    def __init__(self):
        """Initialize the Notification Manager"""
        self.notification_templates = self._load_templates()
        logger.info("NotificationManager initialized successfully")
    
    def _load_templates(self) -> Dict[str, str]:
        """Load notification templates"""
        return {
            'due_soon': """
Decision Due Soon: {title}

Hello {owner},

Your decision "{title}" is due on {due_date} ({days_remaining} days remaining).

Status: {status}
Thread: {thread_link}

Please take action if needed.

Best regards,
TechAtlas Team
            """.strip(),
            
            'overdue': """
Decision Overdue: {title}

Hello {owner},

Your decision "{title}" was due on {due_date} and is now {days_overdue} days overdue.

Status: {status}
Thread: {thread_link}

Please update the status or extend the deadline.

Best regards,
TechAtlas Team
            """.strip(),
            
            'high_risk': """
High Risk Decision Alert: {title}

Hello {owner},

Your decision "{title}" has been flagged as high risk.

Risk Score: {risk_score}/10
Risk Factors:
{risk_factors}

Please review and take appropriate action.

Best regards,
TechAtlas Team
            """.strip(),
            
            'assignment': """
New Decision Assigned: {title}

Hello {owner},

You have been assigned as the owner of a new decision:

Title: {title}
Due Date: {due_date}
Thread: {thread_link}

Please review and take action.

Best regards,
TechAtlas Team
            """.strip()
        }
    
    def send_due_date_reminder(self, decision_data: Dict[str, Any], recipient: str) -> Dict[str, Any]:
        """
        Send due date reminder
        
        Args:
            decision_data: Decision dictionary
            recipient: Recipient email
        
        Returns:
            Notification result
        """
        try:
            from utils.datetime_helper import DateTimeHelper
            
            days_remaining = DateTimeHelper.calculate_days_until(decision_data.get('due_date', ''))
            
            message = self.notification_templates['due_soon'].format(
                title=decision_data.get('title', ''),
                owner=decision_data.get('owner', ''),
                due_date=decision_data.get('due_date', ''),
                days_remaining=days_remaining,
                status=decision_data.get('status', ''),
                thread_link=decision_data.get('thread_link', '')
            )
            
            # TODO: Implement actual email/notification sending
            logger.info(f"Due date reminder sent to {recipient} for decision: {decision_data.get('title')}")
            
            return {
                'success': True,
                'recipient': recipient,
                'type': 'due_soon',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send due date reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_overdue_alert(self, decision_data: Dict[str, Any], recipient: str) -> Dict[str, Any]:
        """Send overdue decision alert"""
        try:
            from utils.datetime_helper import DateTimeHelper
            
            days_overdue = abs(DateTimeHelper.calculate_days_until(decision_data.get('due_date', '')))
            
            message = self.notification_templates['overdue'].format(
                title=decision_data.get('title', ''),
                owner=decision_data.get('owner', ''),
                due_date=decision_data.get('due_date', ''),
                days_overdue=days_overdue,
                status=decision_data.get('status', ''),
                thread_link=decision_data.get('thread_link', '')
            )
            
            logger.info(f"Overdue alert sent to {recipient}")
            
            return {
                'success': True,
                'recipient': recipient,
                'type': 'overdue',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send overdue alert: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_high_risk_notification(self, decision_data: Dict[str, Any], recipient: str) -> Dict[str, Any]:
        """Send high risk decision notification"""
        try:
            risk_factors = decision_data.get('risk_factors', [])
            risk_factors_text = '\n'.join([f"- {factor}" for factor in risk_factors])
            
            message = self.notification_templates['high_risk'].format(
                title=decision_data.get('title', ''),
                owner=decision_data.get('owner', ''),
                risk_score=decision_data.get('risk_score', 0),
                risk_factors=risk_factors_text or '- No specific factors identified'
            )
            
            logger.info(f"High risk notification sent to {recipient}")
            
            return {
                'success': True,
                'recipient': recipient,
                'type': 'high_risk',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send high risk notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_assignment_notification(self, decision_data: Dict[str, Any], recipient: str) -> Dict[str, Any]:
        """Send decision assignment notification"""
        try:
            message = self.notification_templates['assignment'].format(
                title=decision_data.get('title', ''),
                owner=decision_data.get('owner', ''),
                due_date=decision_data.get('due_date', ''),
                thread_link=decision_data.get('thread_link', '')
            )
            
            logger.info(f"Assignment notification sent to {recipient}")
            
            return {
                'success': True,
                'recipient': recipient,
                'type': 'assignment',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send assignment notification: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def batch_send_reminders(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send reminders for multiple decisions
        
        Args:
            decisions: List of decision dictionaries
        
        Returns:
            Batch send results
        """
        results = {
            'total': len(decisions),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for decision in decisions:
            owner = decision.get('owner', '')
            result = self.send_due_date_reminder(decision, owner)
            
            if result.get('success'):
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append(result)
        
        return results
    
    def get_notification_preferences(self, user_email: str) -> Dict[str, Any]:
        """
        Get user notification preferences
        
        Args:
            user_email: User's email
        
        Returns:
            Notification preferences
        """
        # TODO: Implement actual preference storage
        return {
            'email_notifications': True,
            'due_date_reminders': True,
            'high_risk_alerts': True,
            'daily_digest': False,
            'reminder_days_before': 7
        }
    
    def update_notification_preferences(self, user_email: str, preferences: Dict[str, Any]) -> bool:
        """Update user notification preferences"""
        # TODO: Implement actual preference storage
        logger.info(f"Updated notification preferences for {user_email}")
        return True
