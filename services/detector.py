from config import Config
import google.generativeai as genai

genai.configure(api_key=Config.GEMINI_API_KEY)

class DecisionDetector:
    def __init__(self):
        self.keywords = Config.DECISION_KEYWORDS
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def detect(self, message: str) -> tuple[bool, float, str]:
        """
        Returns: (is_decision, confidence, suggested_title)
        """
        try:
            # Quick keyword check first
            message_lower = message.lower()
            keyword_match = any(kw in message_lower for kw in self.keywords)
            
            if not keyword_match:
                return False, 0.0, ""
            
            # Use Gemini to extract decision details
            prompt = """
            Analyze this message and determine if it's a team decision.
            
            Message: "{message}"
            
            If it's a decision, respond in this JSON format:
            {{
                "is_decision": true,
                "confidence": 0.85,
                "title": "Brief decision title (max 10 words)"
            }}
            
            If it's NOT a decision, respond:
            {{
                "is_decision": false,
                "confidence": 0.0,
                "title": ""
            }}
            """.format(message=message)
            
            response = self.model.generate_content(prompt)
            
            if not response or not hasattr(response, 'text') or not response.text:
                print("ERROR: Empty or invalid response from Gemini API")
                return False, 0.0, ""
            
            # Parse JSON from response (handle markdown code blocks)
            import json
            import re
            
            response_text = response.text.strip()
            
            # Handle case where response might be None or empty
            if not response_text:
                return False, 0.0, ""
                
            try:
                # Remove markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
                
                result = json.loads(json_str)
                
                return (
                    bool(result.get('is_decision', False)),
                    float(result.get('confidence', 0.0)),
                    str(result.get('title', ''))[:100]  # Limit title length
                )
            except (json.JSONDecodeError, AttributeError) as e:
                print(f"ERROR parsing Gemini response: {e}")
                print(f"Raw response: {response_text}")
                return False, 0.0, ""
                
        except Exception as e:
            print(f"ERROR in detect method: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, 0.0, ""
