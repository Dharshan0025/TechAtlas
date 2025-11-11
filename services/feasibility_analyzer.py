"""
Feasibility Analyzer Service
Performs AI-powered feasibility analysis on decisions
"""

import google.generativeai as genai
from config import Config
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class FeasibilityAnalyzer:
    """
    Analyzes decisions for feasibility, risks, and alternatives
    """
    
    def __init__(self):
        """Initialize the Feasibility Analyzer with Gemini AI"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            logger.info("FeasibilityAnalyzer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FeasibilityAnalyzer: {str(e)}")
            raise
    
    def analyze(self, title: str, rationale: str, context: str = "") -> Dict[str, Any]:
        """
        Perform comprehensive feasibility analysis
        
        Args:
            title: Decision title
            rationale: Decision rationale/reasoning
            context: Additional context (optional)
        
        Returns:
            Dictionary with analysis results
        """
        try:
            logger.info(f"Analyzing feasibility for: {title}")
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(title, rationale, context)
            
            # Get AI analysis
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Parse the response
            analysis = self._parse_analysis(analysis_text)
            
            # Calculate feasibility score
            feasibility_score = self._calculate_feasibility_score(analysis)
            
            # Determine risk level
            risk_level = self._determine_risk_level(feasibility_score, analysis)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(feasibility_score, risk_level)
            
            result = {
                "strengths": analysis.get("strengths", []),
                "risks": analysis.get("risks", []),
                "alternatives": analysis.get("alternatives", []),
                "past_decisions": [],  # TODO: Query vector store
                "recommendation": recommendation,
                "feasibility_score": feasibility_score,
                "risk_level": risk_level,
                "confidence": 0.85
            }
            
            logger.info(f"Analysis complete. Feasibility score: {feasibility_score}")
            return result
            
        except Exception as e:
            logger.error(f"Feasibility analysis failed: {str(e)}", exc_info=True)
            # Return fallback analysis
            return self._get_fallback_analysis()
    
    def _build_analysis_prompt(self, title: str, rationale: str, context: str) -> str:
        """Build the analysis prompt for Gemini"""
        prompt = f"""Analyze the following technical decision for feasibility:

**Decision Title**: {title}

**Rationale**: {rationale}

**Additional Context**: {context if context else "None provided"}

Please provide a comprehensive analysis in the following format:

**STRENGTHS** (List 3-5 key benefits and advantages):
- [Strength 1]
- [Strength 2]
...

**RISKS** (List 3-5 potential problems and challenges):
- [Risk 1]
- [Risk 2]
...

**ALTERNATIVES** (Suggest 2-3 alternative approaches):
1. **[Alternative Name]**
   - Pros: [Benefits]
   - Cons: [Drawbacks]

**BEST PRACTICES** (Industry standards and recommendations):
- [Practice 1]
- [Practice 2]

**OVERALL ASSESSMENT**:
[Brief summary and recommendation]

Be specific, technical, and actionable in your analysis."""
        
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the AI-generated analysis text"""
        try:
            analysis = {
                "strengths": [],
                "risks": [],
                "alternatives": [],
                "best_practices": [],
                "assessment": ""
            }
            
            # Simple parsing (can be improved with more sophisticated NLP)
            lines = analysis_text.split('\n')
            current_section = None
            current_alternative = None
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Detect sections
                if 'STRENGTHS' in line.upper():
                    current_section = 'strengths'
                    continue
                elif 'RISKS' in line.upper():
                    current_section = 'risks'
                    continue
                elif 'ALTERNATIVES' in line.upper():
                    current_section = 'alternatives'
                    continue
                elif 'BEST PRACTICES' in line.upper():
                    current_section = 'best_practices'
                    continue
                elif 'OVERALL ASSESSMENT' in line.upper():
                    current_section = 'assessment'
                    continue
                
                # Parse content based on section
                if current_section == 'strengths' and line.startswith('-'):
                    analysis['strengths'].append(line[1:].strip())
                elif current_section == 'risks' and line.startswith('-'):
                    analysis['risks'].append(line[1:].strip())
                elif current_section == 'alternatives':
                    if line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                        if current_alternative:
                            analysis['alternatives'].append(current_alternative)
                        current_alternative = {"option": line[2:].strip(), "pros": "", "cons": ""}
                    elif current_alternative and 'Pros:' in line:
                        current_alternative['pros'] = line.split('Pros:')[1].strip()
                    elif current_alternative and 'Cons:' in line:
                        current_alternative['cons'] = line.split('Cons:')[1].strip()
                elif current_section == 'best_practices' and line.startswith('-'):
                    analysis['best_practices'].append(line[1:].strip())
                elif current_section == 'assessment':
                    analysis['assessment'] += line + " "
            
            # Add last alternative if exists
            if current_alternative:
                analysis['alternatives'].append(current_alternative)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to parse analysis: {str(e)}")
            return {
                "strengths": ["Analysis parsing failed"],
                "risks": ["Unable to parse AI response"],
                "alternatives": [],
                "best_practices": [],
                "assessment": "Analysis incomplete"
            }
    
    def _calculate_feasibility_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate feasibility score (0-100)
        Based on strengths vs risks ratio
        """
        try:
            strengths_count = len(analysis.get("strengths", []))
            risks_count = len(analysis.get("risks", []))
            alternatives_count = len(analysis.get("alternatives", []))
            
            # Base score
            base_score = 50.0
            
            # Adjust for strengths (up to +30)
            strength_bonus = min(strengths_count * 6, 30)
            
            # Adjust for risks (up to -30)
            risk_penalty = min(risks_count * 5, 30)
            
            # Bonus for having alternatives (+10)
            alternative_bonus = 10 if alternatives_count > 0 else 0
            
            # Calculate final score
            score = base_score + strength_bonus - risk_penalty + alternative_bonus
            
            # Clamp to 0-100
            score = max(0, min(100, score))
            
            return round(score, 1)
            
        except Exception as e:
            logger.error(f"Failed to calculate feasibility score: {str(e)}")
            return 50.0
    
    def _determine_risk_level(self, feasibility_score: float, analysis: Dict[str, Any]) -> str:
        """Determine risk level based on score and analysis"""
        risks_count = len(analysis.get("risks", []))
        
        if feasibility_score >= 75 and risks_count <= 2:
            return "Low"
        elif feasibility_score >= 50 and risks_count <= 4:
            return "Medium"
        else:
            return "High"
    
    def _generate_recommendation(self, feasibility_score: float, risk_level: str) -> str:
        """Generate actionable recommendation"""
        if feasibility_score >= 75:
            return "Proceed with implementation. The decision appears well-founded with clear benefits."
        elif feasibility_score >= 60:
            return "Proceed with caution. Consider addressing identified risks before full implementation."
        elif feasibility_score >= 40:
            return "Reconsider approach. Significant risks identified. Explore alternatives or mitigation strategies."
        else:
            return "High risk decision. Strongly recommend exploring alternative approaches or gathering more information."
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Return fallback analysis when AI fails"""
        return {
            "strengths": [
                "Decision has been documented",
                "Team is aware of the change"
            ],
            "risks": [
                "Analysis service temporarily unavailable",
                "Manual review recommended"
            ],
            "alternatives": [],
            "past_decisions": [],
            "recommendation": "Unable to complete automated analysis. Please conduct manual review.",
            "feasibility_score": 50.0,
            "risk_level": "Medium",
            "confidence": 0.3
        }
    
    def analyze_with_history(self, title: str, rationale: str, context: str, 
                            past_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze with context from similar past decisions
        
        Args:
            title: Decision title
            rationale: Decision rationale
            context: Additional context
            past_decisions: List of similar past decisions
        
        Returns:
            Enhanced analysis with historical context
        """
        # Get base analysis
        analysis = self.analyze(title, rationale, context)
        
        # Add past decisions context
        if past_decisions:
            analysis["past_decisions"] = [
                {
                    "title": d.get("title", ""),
                    "outcome": d.get("status", "Unknown"),
                    "similarity": d.get("similarity_score", 0.0)
                }
                for d in past_decisions[:3]  # Top 3 similar decisions
            ]
            
            # Adjust score based on past outcomes
            successful_past = sum(1 for d in past_decisions if d.get("status") == "Completed")
            if successful_past > 0:
                analysis["feasibility_score"] = min(100, analysis["feasibility_score"] + 5)
        
        return analysis
