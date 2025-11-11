"""
Risk Assessment Service
Identifies and assesses risks in decisions
"""

from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskAssessor:
    """
    Assesses risks in decisions and provides mitigation recommendations
    """
    
    def __init__(self):
        """Initialize the Risk Assessor"""
        self.db = firestore.client()
        logger.info("RiskAssessor initialized successfully")
    
    def assess_decision_risk(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive risk assessment for a single decision
        
        Args:
            decision_data: Decision dictionary
        
        Returns:
            Risk assessment results
        """
        try:
            risk_factors = []
            risk_score = 0
            
            # Factor 1: Ownership (single owner = higher risk)
            participants = decision_data.get('participants', [])
            if len(participants) <= 1:
                risk_score += 8
                risk_factors.append({
                    'factor': 'Single Owner',
                    'severity': 'High',
                    'description': 'Knowledge silo - only one person owns this decision',
                    'mitigation': 'Add more participants or document thoroughly'
                })
            elif len(participants) == 2:
                risk_score += 5
                risk_factors.append({
                    'factor': 'Limited Participants',
                    'severity': 'Medium',
                    'description': 'Limited knowledge distribution',
                    'mitigation': 'Consider involving more team members'
                })
            else:
                risk_score += 2
            
            # Factor 2: Due date proximity
            due_date = decision_data.get('due_date', '')
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    days_until = (due - now).days
                    
                    if days_until < 0:
                        risk_score += 3
                        risk_factors.append({
                            'factor': 'Past Due',
                            'severity': 'High',
                            'description': f'Decision is {abs(days_until)} days overdue',
                            'mitigation': 'Immediate action required or extend deadline'
                        })
                    elif days_until < 7:
                        risk_score += 2
                        risk_factors.append({
                            'factor': 'Due Soon',
                            'severity': 'Medium',
                            'description': f'Only {days_until} days remaining',
                            'mitigation': 'Prioritize completion'
                        })
                except:
                    pass
            
            # Factor 3: Status
            status = decision_data.get('status', 'Open')
            if status == 'Open':
                risk_score += 1
                risk_factors.append({
                    'factor': 'Not Started',
                    'severity': 'Low',
                    'description': 'Decision has not been acted upon',
                    'mitigation': 'Begin implementation or update status'
                })
            
            # Factor 4: Age of decision
            created_at = decision_data.get('created_at', '')
            if created_at:
                try:
                    created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.now(timezone.utc) - created).days
                    
                    if age_days > 90 and status != 'Completed':
                        risk_score += 2
                        risk_factors.append({
                            'factor': 'Aging Decision',
                            'severity': 'Medium',
                            'description': f'Decision is {age_days} days old without completion',
                            'mitigation': 'Review relevance and update or close'
                        })
                except:
                    pass
            
            # Factor 5: Lack of documentation
            rationale = decision_data.get('rationale', '')
            if len(rationale) < 50:
                risk_score += 1
                risk_factors.append({
                    'factor': 'Insufficient Documentation',
                    'severity': 'Low',
                    'description': 'Limited rationale provided',
                    'mitigation': 'Add detailed reasoning and context'
                })
            
            # Normalize score to 0-10
            risk_score = min(risk_score, 10)
            
            # Determine risk level
            if risk_score >= 7:
                risk_level = 'High'
            elif risk_score >= 4:
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'total_factors': len(risk_factors),
                'recommendations': self._generate_risk_recommendations(risk_level, risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {
                'risk_score': 5,
                'risk_level': 'Medium',
                'risk_factors': [],
                'total_factors': 0,
                'recommendations': []
            }
    
    def detect_single_owner_risks(self) -> List[Dict[str, Any]]:
        """
        Identify decisions with single owners (knowledge silos)
        
        Returns:
            List of high-risk single-owner decisions
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            single_owner_decisions = []
            
            for doc in decisions:
                data = doc.to_dict()
                participants = data.get('participants', [])
                
                if len(participants) <= 1:
                    data['id'] = doc.id
                    data['risk_reason'] = 'Single owner - knowledge silo'
                    single_owner_decisions.append(data)
            
            return single_owner_decisions
            
        except Exception as e:
            logger.error(f"Single owner detection failed: {str(e)}")
            return []
    
    def identify_aging_decisions(self, days_threshold: int = 60) -> List[Dict[str, Any]]:
        """
        Identify decisions that are aging without completion
        
        Args:
            days_threshold: Number of days to consider as "aging"
        
        Returns:
            List of aging decisions
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_threshold)).isoformat()
            
            aging_decisions = []
            
            for doc in decisions:
                data = doc.to_dict()
                created_at = data.get('created_at', '')
                status = data.get('status', '')
                
                if created_at < cutoff_date and status != 'Completed':
                    age_days = (datetime.now(timezone.utc) - 
                               datetime.fromisoformat(created_at.replace('Z', '+00:00'))).days
                    
                    data['id'] = doc.id
                    data['age_days'] = age_days
                    data['risk_reason'] = f'Aging decision ({age_days} days old)'
                    aging_decisions.append(data)
            
            # Sort by age
            aging_decisions.sort(key=lambda x: x['age_days'], reverse=True)
            
            return aging_decisions
            
        except Exception as e:
            logger.error(f"Aging decision detection failed: {str(e)}")
            return []
    
    def detect_knowledge_silos(self) -> List[Dict[str, Any]]:
        """
        Identify knowledge silos (topics with single experts)
        
        Returns:
            List of knowledge silo areas
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            # Map topics to owners
            topic_owners = {}
            
            for doc in decisions:
                data = doc.to_dict()
                title = data.get('title', '').lower()
                owner = data.get('owner', '')
                
                # Extract key words as topics
                words = title.split()
                for word in words:
                    if len(word) > 4:
                        if word not in topic_owners:
                            topic_owners[word] = set()
                        topic_owners[word].add(owner)
            
            # Identify single-owner topics
            silos = []
            for topic, owners in topic_owners.items():
                if len(owners) == 1:
                    silos.append({
                        'topic': topic,
                        'expert': list(owners)[0],
                        'risk_level': 'High',
                        'recommendation': f'Distribute knowledge about {topic} to more team members'
                    })
            
            return silos
            
        except Exception as e:
            logger.error(f"Knowledge silo detection failed: {str(e)}")
            return []
    
    def calculate_risk_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate risk trend over time
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Risk trend data
        """
        try:
            decisions = list(self.db.collection('decisions').stream())
            
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            recent_decisions = [
                doc for doc in decisions
                if doc.to_dict().get('created_at', '') >= cutoff_date
            ]
            
            if not recent_decisions:
                return {
                    'period_days': days,
                    'avg_risk_score': 0,
                    'high_risk_count': 0,
                    'trend': 'stable'
                }
            
            # Calculate average risk
            total_risk = sum(doc.to_dict().get('risk_score', 0) for doc in recent_decisions)
            avg_risk = total_risk / len(recent_decisions)
            
            # Count high risk
            high_risk_count = sum(
                1 for doc in recent_decisions
                if doc.to_dict().get('risk_score', 0) >= 7
            )
            
            return {
                'period_days': days,
                'total_decisions': len(recent_decisions),
                'avg_risk_score': round(avg_risk, 1),
                'high_risk_count': high_risk_count,
                'high_risk_percentage': round((high_risk_count / len(recent_decisions) * 100), 1),
                'trend': 'increasing' if avg_risk > 5 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Risk trend calculation failed: {str(e)}")
            return {}
    
    def _generate_risk_recommendations(self, risk_level: str, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable risk mitigation recommendations"""
        recommendations = []
        
        if risk_level == 'High':
            recommendations.append('Immediate attention required - address critical risk factors')
        
        for factor in risk_factors:
            if factor.get('mitigation'):
                recommendations.append(factor['mitigation'])
        
        # Add general recommendations
        if risk_level in ['High', 'Medium']:
            recommendations.append('Schedule review meeting with stakeholders')
            recommendations.append('Document decision rationale and alternatives')
        
        return recommendations
    
    def get_risk_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive risk dashboard data
        
        Returns:
            Risk dashboard metrics
        """
        try:
            return {
                'single_owner_risks': len(self.detect_single_owner_risks()),
                'aging_decisions': len(self.identify_aging_decisions(days_threshold=60)),
                'knowledge_silos': len(self.detect_knowledge_silos()),
                'risk_trend': self.calculate_risk_trend(days=30),
                'high_risk_decisions': self.db.collection('decisions').where('risk_score', '>=', 7).stream()
            }
            
        except Exception as e:
            logger.error(f"Failed to get risk dashboard: {str(e)}")
            return {}
