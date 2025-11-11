"""
Expertise Mapper Service
Maps user expertise based on decision participation
"""

from firebase_admin import firestore
from collections import defaultdict
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ExpertiseMapper:
    """
    Tracks and maps user expertise across topics
    """
    
    def __init__(self):
        """Initialize the Expertise Mapper"""
        self.db = firestore.client()
        logger.info("ExpertiseMapper initialized successfully")
    
    def track_user_participation(self, user_email: str) -> Dict[str, Any]:
        """
        Track user's participation across decisions
        
        Args:
            user_email: User's email address
        
        Returns:
            User participation metrics
        """
        try:
            # Get decisions owned by user
            owned_decisions = list(
                self.db.collection('decisions')
                .where('owner', '==', user_email)
                .stream()
            )
            
            # Get decisions where user participated
            all_decisions = list(self.db.collection('decisions').stream())
            participated_decisions = [
                doc for doc in all_decisions
                if user_email in doc.to_dict().get('participants', [])
                and doc.to_dict().get('owner') != user_email
            ]
            
            # Extract topics
            topics = defaultdict(int)
            for doc in owned_decisions + participated_decisions:
                title = doc.to_dict().get('title', '').lower()
                words = title.split()
                for word in words:
                    if len(word) > 4:
                        topics[word] += 1
            
            # Calculate metrics
            total_contributions = len(owned_decisions) + len(participated_decisions)
            
            return {
                'user_email': user_email,
                'decisions_owned': len(owned_decisions),
                'decisions_participated': len(participated_decisions),
                'total_contributions': total_contributions,
                'top_topics': sorted(
                    [{'topic': topic, 'count': count} for topic, count in topics.items()],
                    key=lambda x: x['count'],
                    reverse=True
                )[:10],
                'expertise_score': self._calculate_expertise_score(
                    len(owned_decisions),
                    len(participated_decisions)
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to track participation for {user_email}: {str(e)}")
            return {}
    
    def score_topic_expertise(self, user_email: str, topic: str) -> float:
        """
        Score user's expertise on a specific topic
        
        Args:
            user_email: User's email
            topic: Topic to score
        
        Returns:
            Expertise score (0-100)
        """
        try:
            all_decisions = list(self.db.collection('decisions').stream())
            
            topic_decisions = []
            user_topic_decisions = []
            
            topic_lower = topic.lower()
            
            for doc in all_decisions:
                data = doc.to_dict()
                title = data.get('title', '').lower()
                rationale = data.get('rationale', '').lower()
                
                # Check if decision is about this topic
                if topic_lower in title or topic_lower in rationale:
                    topic_decisions.append(doc)
                    
                    # Check if user was involved
                    if (data.get('owner') == user_email or 
                        user_email in data.get('participants', [])):
                        user_topic_decisions.append(doc)
            
            if not topic_decisions:
                return 0.0
            
            # Calculate score based on involvement
            involvement_ratio = len(user_topic_decisions) / len(topic_decisions)
            
            # Bonus for ownership
            owned_count = sum(
                1 for doc in user_topic_decisions
                if doc.to_dict().get('owner') == user_email
            )
            
            base_score = involvement_ratio * 70
            ownership_bonus = (owned_count / len(user_topic_decisions) * 30) if user_topic_decisions else 0
            
            score = min(100, base_score + ownership_bonus)
            
            return round(score, 1)
            
        except Exception as e:
            logger.error(f"Failed to score expertise: {str(e)}")
            return 0.0
    
    def identify_experts_for_topic(self, topic: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Identify top experts for a specific topic
        
        Args:
            topic: Topic to find experts for
            top_n: Number of top experts to return
        
        Returns:
            List of experts with scores
        """
        try:
            all_decisions = list(self.db.collection('decisions').stream())
            
            # Track user involvement in topic
            user_involvement = defaultdict(lambda: {'owned': 0, 'participated': 0})
            
            topic_lower = topic.lower()
            
            for doc in all_decisions:
                data = doc.to_dict()
                title = data.get('title', '').lower()
                rationale = data.get('rationale', '').lower()
                
                if topic_lower in title or topic_lower in rationale:
                    owner = data.get('owner', '')
                    participants = data.get('participants', [])
                    
                    if owner:
                        user_involvement[owner]['owned'] += 1
                    
                    for participant in participants:
                        if participant != owner:
                            user_involvement[participant]['participated'] += 1
            
            # Calculate expertise scores
            experts = []
            for user, involvement in user_involvement.items():
                score = (involvement['owned'] * 10) + (involvement['participated'] * 5)
                experts.append({
                    'user_email': user,
                    'expertise_score': score,
                    'decisions_owned': involvement['owned'],
                    'decisions_participated': involvement['participated'],
                    'topic': topic
                })
            
            # Sort and return top N
            experts.sort(key=lambda x: x['expertise_score'], reverse=True)
            
            return experts[:top_n]
            
        except Exception as e:
            logger.error(f"Failed to identify experts: {str(e)}")
            return []
    
    def analyze_knowledge_distribution(self) -> Dict[str, Any]:
        """
        Analyze how knowledge is distributed across the organization
        
        Returns:
            Knowledge distribution metrics
        """
        try:
            all_decisions = list(self.db.collection('decisions').stream())
            
            # Track topics and their experts
            topic_experts = defaultdict(set)
            
            for doc in all_decisions:
                data = doc.to_dict()
                title = data.get('title', '').lower()
                owner = data.get('owner', '')
                participants = data.get('participants', [])
                
                # Extract topics
                words = title.split()
                for word in words:
                    if len(word) > 4:
                        topic_experts[word].add(owner)
                        for participant in participants:
                            topic_experts[word].add(participant)
            
            # Analyze distribution
            single_expert_topics = []
            well_distributed_topics = []
            
            for topic, experts in topic_experts.items():
                if len(experts) == 1:
                    single_expert_topics.append({
                        'topic': topic,
                        'expert': list(experts)[0],
                        'risk': 'High - Knowledge Silo'
                    })
                elif len(experts) >= 3:
                    well_distributed_topics.append({
                        'topic': topic,
                        'expert_count': len(experts),
                        'risk': 'Low - Well Distributed'
                    })
            
            return {
                'total_topics': len(topic_experts),
                'single_expert_topics': len(single_expert_topics),
                'well_distributed_topics': len(well_distributed_topics),
                'knowledge_silos': single_expert_topics[:10],
                'well_distributed': well_distributed_topics[:10],
                'distribution_health': 'Good' if len(single_expert_topics) < len(well_distributed_topics) else 'Needs Improvement'
            }
            
        except Exception as e:
            logger.error(f"Knowledge distribution analysis failed: {str(e)}")
            return {}
    
    def detect_expertise_gaps(self) -> List[Dict[str, Any]]:
        """
        Detect areas where expertise is lacking
        
        Returns:
            List of expertise gaps
        """
        try:
            distribution = self.analyze_knowledge_distribution()
            
            gaps = []
            
            # Single expert topics are gaps
            for silo in distribution.get('knowledge_silos', []):
                gaps.append({
                    'area': silo['topic'],
                    'current_experts': 1,
                    'recommended_experts': 3,
                    'severity': 'High',
                    'recommendation': f"Train additional team members on {silo['topic']}"
                })
            
            return gaps
            
        except Exception as e:
            logger.error(f"Expertise gap detection failed: {str(e)}")
            return []
    
    def recommend_decision_owner(self, decision_title: str, decision_rationale: str) -> List[Dict[str, Any]]:
        """
        Recommend potential owners for a decision based on expertise
        
        Args:
            decision_title: Decision title
            decision_rationale: Decision rationale
        
        Returns:
            List of recommended owners with scores
        """
        try:
            # Extract topics from decision
            text = (decision_title + " " + decision_rationale).lower()
            words = text.split()
            topics = [word for word in words if len(word) > 4]
            
            # Score users for each topic
            user_scores = defaultdict(float)
            
            for topic in topics[:5]:  # Top 5 topics
                experts = self.identify_experts_for_topic(topic, top_n=10)
                for expert in experts:
                    user_scores[expert['user_email']] += expert['expertise_score']
            
            # Format recommendations
            recommendations = [
                {
                    'user_email': user,
                    'match_score': round(score, 1),
                    'reason': 'Expertise in relevant topics'
                }
                for user, score in sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Owner recommendation failed: {str(e)}")
            return []
    
    def _calculate_expertise_score(self, owned: int, participated: int) -> float:
        """Calculate overall expertise score for a user"""
        # Ownership weighted more heavily
        score = (owned * 10) + (participated * 3)
        return min(100, score)
