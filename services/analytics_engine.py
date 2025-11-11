"""
Analytics Engine Service
Provides analytics and insights on decisions
"""

from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Analyzes decision data for trends, patterns, and insights
    """
    
    def __init__(self):
        """Initialize the Analytics Engine"""
        self.db = firestore.client()
        logger.info("AnalyticsEngine initialized successfully")
    
    def get_decision_count(self, filters: Dict[str, Any] = None) -> int:
        """Get total count of decisions with optional filters"""
        try:
            query = self.db.collection('decisions')
            
            if filters:
                if 'status' in filters:
                    query = query.where('status', '==', filters['status'])
                if 'owner' in filters:
                    query = query.where('owner', '==', filters['owner'])
                if 'channel_id' in filters:
                    query = query.where('channel_id', '==', filters['channel_id'])
            
            return len(list(query.stream()))
            
        except Exception as e:
            logger.error(f"Failed to get decision count: {str(e)}")
            return 0
    
    def get_trend_analysis(self, period: str = 'month', limit: int = 12) -> List[Dict[str, Any]]:
        """
        Analyze decision trends over time
        
        Args:
            period: 'day', 'week', 'month', or 'year'
            limit: Number of periods to analyze
        
        Returns:
            List of trend data points
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            # Group by time period
            trends = defaultdict(lambda: {'count': 0, 'completed': 0, 'open': 0})
            
            for doc in decisions:
                data = doc.to_dict()
                created_at = data.get('created_at', '')
                
                if not created_at:
                    continue
                
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    
                    if period == 'day':
                        key = dt.strftime('%Y-%m-%d')
                    elif period == 'week':
                        key = dt.strftime('%Y-W%U')
                    elif period == 'month':
                        key = dt.strftime('%Y-%m')
                    else:  # year
                        key = dt.strftime('%Y')
                    
                    trends[key]['count'] += 1
                    
                    status = data.get('status', '')
                    if status == 'Completed':
                        trends[key]['completed'] += 1
                    elif status == 'Open':
                        trends[key]['open'] += 1
                        
                except Exception:
                    continue
            
            # Convert to sorted list
            trend_list = [
                {
                    'period': period_key,
                    'total_decisions': data['count'],
                    'completed': data['completed'],
                    'open': data['open'],
                    'completion_rate': round((data['completed'] / data['count'] * 100) if data['count'] > 0 else 0, 1)
                }
                for period_key, data in sorted(trends.items())
            ]
            
            return trend_list[-limit:]  # Return last N periods
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return []
    
    def get_topic_frequency(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Analyze most frequent topics/keywords in decisions
        
        Args:
            top_n: Number of top topics to return
        
        Returns:
            List of topics with frequency counts
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            # Extract keywords from titles
            word_freq = defaultdict(int)
            
            for doc in decisions:
                data = doc.to_dict()
                title = data.get('title', '').lower()
                rationale = data.get('rationale', '').lower()
                
                # Simple word extraction (can be improved with NLP)
                words = title.split() + rationale.split()
                
                for word in words:
                    # Filter short words and common words
                    if len(word) > 4 and word not in ['about', 'using', 'should', 'would', 'could']:
                        word_freq[word] += 1
            
            # Sort and format
            topics = [
                {
                    'topic': word,
                    'frequency': count,
                    'percentage': round((count / len(decisions) * 100) if decisions else 0, 1)
                }
                for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
            ]
            
            return topics
            
        except Exception as e:
            logger.error(f"Topic frequency analysis failed: {str(e)}")
            return []
    
    def get_owner_contribution_metrics(self) -> List[Dict[str, Any]]:
        """
        Calculate contribution metrics per owner
        
        Returns:
            List of owner metrics
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            owner_stats = defaultdict(lambda: {
                'total': 0,
                'completed': 0,
                'open': 0,
                'in_progress': 0,
                'high_risk': 0
            })
            
            for doc in decisions:
                data = doc.to_dict()
                owner = data.get('owner', 'Unknown')
                status = data.get('status', 'Open')
                risk_score = data.get('risk_score', 0)
                
                owner_stats[owner]['total'] += 1
                
                if status == 'Completed':
                    owner_stats[owner]['completed'] += 1
                elif status == 'Open':
                    owner_stats[owner]['open'] += 1
                elif status == 'In Progress':
                    owner_stats[owner]['in_progress'] += 1
                
                if risk_score >= 7:
                    owner_stats[owner]['high_risk'] += 1
            
            # Format results
            metrics = [
                {
                    'owner': owner,
                    'total_decisions': stats['total'],
                    'completed': stats['completed'],
                    'open': stats['open'],
                    'in_progress': stats['in_progress'],
                    'high_risk_count': stats['high_risk'],
                    'completion_rate': round((stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
                }
                for owner, stats in owner_stats.items()
            ]
            
            # Sort by total decisions
            metrics.sort(key=lambda x: x['total_decisions'], reverse=True)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Owner contribution metrics failed: {str(e)}")
            return []
    
    def get_channel_activity(self) -> List[Dict[str, Any]]:
        """
        Track activity per channel
        
        Returns:
            List of channel activity metrics
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            channel_stats = defaultdict(lambda: {
                'count': 0,
                'active_owners': set(),
                'avg_risk': []
            })
            
            for doc in decisions:
                data = doc.to_dict()
                channel = data.get('channel_id', 'Unknown')
                owner = data.get('owner', '')
                risk_score = data.get('risk_score', 0)
                
                channel_stats[channel]['count'] += 1
                channel_stats[channel]['active_owners'].add(owner)
                channel_stats[channel]['avg_risk'].append(risk_score)
            
            # Format results
            activity = [
                {
                    'channel_id': channel,
                    'decision_count': stats['count'],
                    'active_contributors': len(stats['active_owners']),
                    'avg_risk_score': round(sum(stats['avg_risk']) / len(stats['avg_risk']), 1) if stats['avg_risk'] else 0
                }
                for channel, stats in channel_stats.items()
            ]
            
            # Sort by decision count
            activity.sort(key=lambda x: x['decision_count'], reverse=True)
            
            return activity
            
        except Exception as e:
            logger.error(f"Channel activity analysis failed: {str(e)}")
            return []
    
    def calculate_completion_rate(self, filters: Dict[str, Any] = None) -> float:
        """
        Calculate overall completion rate
        
        Args:
            filters: Optional filters (owner, channel, date_range)
        
        Returns:
            Completion rate as percentage
        """
        try:
            query = self.db.collection('decisions')
            
            if filters:
                if 'owner' in filters:
                    query = query.where('owner', '==', filters['owner'])
                if 'channel_id' in filters:
                    query = query.where('channel_id', '==', filters['channel_id'])
            
            decisions = list(query.stream())
            
            if not decisions:
                return 0.0
            
            completed = sum(1 for doc in decisions if doc.to_dict().get('status') == 'Completed')
            
            return round((completed / len(decisions) * 100), 1)
            
        except Exception as e:
            logger.error(f"Completion rate calculation failed: {str(e)}")
            return 0.0
    
    def calculate_avg_time_to_resolution(self) -> Dict[str, Any]:
        """
        Calculate average time from decision creation to completion
        
        Returns:
            Dictionary with timing metrics
        """
        try:
            completed_decisions = self.db.collection('decisions').where('status', '==', 'Completed').stream()
            
            resolution_times = []
            
            for doc in completed_decisions:
                data = doc.to_dict()
                created_at = data.get('created_at', '')
                status_updated_at = data.get('status_updated_at', '')
                
                if created_at and status_updated_at:
                    try:
                        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        completed = datetime.fromisoformat(status_updated_at.replace('Z', '+00:00'))
                        
                        days = (completed - created).days
                        resolution_times.append(days)
                    except:
                        continue
            
            if not resolution_times:
                return {
                    'avg_days': 0,
                    'median_days': 0,
                    'min_days': 0,
                    'max_days': 0,
                    'sample_size': 0
                }
            
            resolution_times.sort()
            
            return {
                'avg_days': round(sum(resolution_times) / len(resolution_times), 1),
                'median_days': resolution_times[len(resolution_times) // 2],
                'min_days': min(resolution_times),
                'max_days': max(resolution_times),
                'sample_size': len(resolution_times)
            }
            
        except Exception as e:
            logger.error(f"Time to resolution calculation failed: {str(e)}")
            return {'avg_days': 0, 'median_days': 0, 'min_days': 0, 'max_days': 0, 'sample_size': 0}
    
    def get_decision_velocity(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate decision velocity (decisions per time period)
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Velocity metrics
        """
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            all_decisions = list(self.db.collection('decisions').stream())
            recent_decisions = [
                doc for doc in all_decisions
                if doc.to_dict().get('created_at', '') >= cutoff_date
            ]
            
            velocity = {
                'period_days': days,
                'total_decisions': len(recent_decisions),
                'decisions_per_day': round(len(recent_decisions) / days, 2),
                'decisions_per_week': round(len(recent_decisions) / (days / 7), 1),
                'trend': 'stable'  # TODO: Compare with previous period
            }
            
            return velocity
            
        except Exception as e:
            logger.error(f"Velocity calculation failed: {str(e)}")
            return {'period_days': days, 'total_decisions': 0, 'decisions_per_day': 0, 'decisions_per_week': 0}
    
    def get_comprehensive_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get all dashboard statistics in one call
        
        Returns:
            Comprehensive dashboard data
        """
        try:
            return {
                'overview': {
                    'total_decisions': self.get_decision_count(),
                    'open_decisions': self.get_decision_count({'status': 'Open'}),
                    'completed_decisions': self.get_decision_count({'status': 'Completed'}),
                    'completion_rate': self.calculate_completion_rate()
                },
                'trends': self.get_trend_analysis(period='month', limit=6),
                'top_topics': self.get_topic_frequency(top_n=10),
                'top_contributors': self.get_owner_contribution_metrics()[:10],
                'channel_activity': self.get_channel_activity()[:10],
                'velocity': self.get_decision_velocity(days=30),
                'resolution_time': self.calculate_avg_time_to_resolution()
            }
            
        except Exception as e:
            logger.error(f"Failed to get comprehensive stats: {str(e)}")
            return {}
