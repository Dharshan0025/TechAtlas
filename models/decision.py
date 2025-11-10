from datetime import datetime
from typing import List, Optional

class Decision:
    def __init__(
        self,
        title: str,
        owner: str,
        rationale: str,
        due_date: str,
        thread_link: str,
        participants: List[str],
        channel_id: str,
        decision_id: Optional[str] = None
    ):
        self.decision_id = decision_id or f"dec_{int(datetime.now().timestamp() * 1000)}"
        self.title = title
        self.owner = owner
        self.rationale = rationale
        self.due_date = due_date
        self.thread_link = thread_link
        self.participants = participants
        self.channel_id = channel_id
        self.created_at = datetime.now().isoformat()
        self.status = "Open"
        self.risk_score = self._calculate_risk_score()
    
    def _calculate_risk_score(self) -> int:
        """Simple risk scoring: single owner = high risk"""
        if len(self.participants) <= 1:
            return 8  # High risk
        elif len(self.participants) == 2:
            return 5  # Medium risk
        else:
            return 2  # Low risk
    
    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "owner": self.owner,
            "rationale": self.rationale,
            "due_date": self.due_date,
            "thread_link": self.thread_link,
            "participants": self.participants,
            "channel_id": self.channel_id,
            "created_at": self.created_at,
            "status": self.status,
            "risk_score": self.risk_score
        }
    
    def get_embedding_text(self) -> str:
        """Text to vectorize"""
        return f"{self.title}. {self.rationale}. Owner: {self.owner}"
