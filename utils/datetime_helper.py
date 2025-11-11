"""
DateTime Helper Utility
Provides date and time manipulation functions
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DateTimeHelper:
    """
    Helper class for date and time operations
    """
    
    @staticmethod
    def get_current_utc() -> datetime:
        """Get current UTC datetime"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def get_current_iso() -> str:
        """Get current datetime in ISO format"""
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def parse_iso_date(date_str: str) -> Optional[datetime]:
        """
        Parse ISO format date string
        
        Args:
            date_str: ISO format date string
        
        Returns:
            datetime object or None if invalid
        """
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Failed to parse date: {date_str}, error: {str(e)}")
            return None
    
    @staticmethod
    def format_date(dt: datetime, format_str: str = '%Y-%m-%d') -> str:
        """
        Format datetime object
        
        Args:
            dt: datetime object
            format_str: Format string
        
        Returns:
            Formatted date string
        """
        try:
            return dt.strftime(format_str)
        except Exception as e:
            logger.error(f"Failed to format date: {str(e)}")
            return ""
    
    @staticmethod
    def calculate_days_until(target_date: str) -> int:
        """
        Calculate days until target date
        
        Args:
            target_date: Target date in YYYY-MM-DD format
        
        Returns:
            Number of days (negative if past)
        """
        try:
            target = datetime.strptime(target_date, '%Y-%m-%d')
            target = target.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            
            delta = target - now
            return delta.days
        except Exception as e:
            logger.error(f"Failed to calculate days until: {str(e)}")
            return 0
    
    @staticmethod
    def calculate_age_days(created_at: str) -> int:
        """
        Calculate age in days from creation date
        
        Args:
            created_at: Creation date in ISO format
        
        Returns:
            Age in days
        """
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            delta = now - created
            return delta.days
        except Exception as e:
            logger.error(f"Failed to calculate age: {str(e)}")
            return 0
    
    @staticmethod
    def get_relative_time_string(dt: datetime) -> str:
        """
        Get relative time string (e.g., "3 days ago", "in 2 weeks")
        
        Args:
            dt: datetime object
        
        Returns:
            Relative time string
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Ensure dt is timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            delta = now - dt
            
            # Future dates
            if delta.total_seconds() < 0:
                delta = -delta
                
                if delta.days > 365:
                    years = delta.days // 365
                    return f"in {years} year{'s' if years > 1 else ''}"
                elif delta.days > 30:
                    months = delta.days // 30
                    return f"in {months} month{'s' if months > 1 else ''}"
                elif delta.days > 0:
                    return f"in {delta.days} day{'s' if delta.days > 1 else ''}"
                elif delta.seconds > 3600:
                    hours = delta.seconds // 3600
                    return f"in {hours} hour{'s' if hours > 1 else ''}"
                else:
                    minutes = delta.seconds // 60
                    return f"in {minutes} minute{'s' if minutes > 1 else ''}"
            
            # Past dates
            if delta.days > 365:
                years = delta.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
            elif delta.days > 30:
                months = delta.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            elif delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds > 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "just now"
                
        except Exception as e:
            logger.error(f"Failed to get relative time: {str(e)}")
            return "unknown"
    
    @staticmethod
    def add_business_days(start_date: datetime, days: int) -> datetime:
        """
        Add business days (excluding weekends)
        
        Args:
            start_date: Starting date
            days: Number of business days to add
        
        Returns:
            Resulting datetime
        """
        try:
            current = start_date
            days_added = 0
            
            while days_added < days:
                current += timedelta(days=1)
                # Skip weekends (Saturday=5, Sunday=6)
                if current.weekday() < 5:
                    days_added += 1
            
            return current
        except Exception as e:
            logger.error(f"Failed to add business days: {str(e)}")
            return start_date
    
    @staticmethod
    def is_overdue(due_date: str) -> bool:
        """
        Check if a date is overdue
        
        Args:
            due_date: Due date in YYYY-MM-DD format
        
        Returns:
            True if overdue
        """
        try:
            due = datetime.strptime(due_date, '%Y-%m-%d')
            due = due.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            
            return now > due
        except Exception as e:
            logger.error(f"Failed to check overdue: {str(e)}")
            return False
    
    @staticmethod
    def get_date_range(period: str) -> tuple:
        """
        Get date range for a period
        
        Args:
            period: 'today', 'week', 'month', 'year'
        
        Returns:
            Tuple of (start_date, end_date) in ISO format
        """
        try:
            now = datetime.now(timezone.utc)
            
            if period == 'today':
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = now
            elif period == 'week':
                start = now - timedelta(days=7)
                end = now
            elif period == 'month':
                start = now - timedelta(days=30)
                end = now
            elif period == 'year':
                start = now - timedelta(days=365)
                end = now
            else:
                start = now - timedelta(days=30)
                end = now
            
            return (start.isoformat(), end.isoformat())
            
        except Exception as e:
            logger.error(f"Failed to get date range: {str(e)}")
            return ("", "")
    
    @staticmethod
    def get_week_number(dt: datetime) -> int:
        """Get ISO week number"""
        return dt.isocalendar()[1]
    
    @staticmethod
    def get_month_name(dt: datetime) -> str:
        """Get month name"""
        return dt.strftime('%B')
    
    @staticmethod
    def get_quarter(dt: datetime) -> int:
        """Get quarter (1-4)"""
        return (dt.month - 1) // 3 + 1
