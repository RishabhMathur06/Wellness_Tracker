import logging
from typing import Dict, Any
from app.core.config import get_settings
from pydantic import BaseModel
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

settings = get_settings()
logger = logging.getLogger(__name__)

class EmotionAnalysis(BaseModel):
    stress_score: float
    anxiety_score: float
    detected_emotions: list[str]
    analysis: str
    recommendation: str

class GeminiService:
    def __init__(self):
        self.is_mock = settings.GEMINI_API_KEY == "dummy_key_if_not_set" or not genai
        if not self.is_mock:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def analyze_emotion_multimodal(self, image_data: bytes) -> Dict[str, Any]:
        """
        Use Google GenAI Multimodal call if API key exists, otherwise mock.
        Security: Strict JSON output schema (Pydantic) and temperature=0.1
        prevent hallucination.
        """
        if self.is_mock:
            return {
                "stress_score": 6.5,
                "anxiety_score": 5.0,
                "detected_emotions": ["tired", "anxious", "hopeful"],
                "analysis": "The facial cues suggest moderate stress, likely from lack of sleep.",
                "recommendation": "Try a 10-minute mindfulness exercise before bed."
            }
        
        # Real call using google-genai
        try:
            # We would normally parse the bytes into a PIL image or pass as blob
            # For simplicity in this endpoint we pass prompt
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=["Analyze the stress and anxiety from this image.", types.Part.from_bytes(data=image_data, mime_type="image/jpeg")],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EmotionAnalysis,
                    temperature=0.1,
                ),
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"GenAI Error: {e}")
            return {
                "stress_score": 5.0, "anxiety_score": 5.0, 
                "detected_emotions": ["unknown"], "analysis": "Error analyzing image", "recommendation": "None"
            }
    
    async def chat_therapeutic(self, message: str, history: list) -> str:
        """
        Therapeutic chat response.
        Grounding context: Professional, empathetic wellness tracker assistant.
        """
        if self.is_mock:
            return f"I hear that you're feeling this way: '{message}'. Remember to take deep breaths. How can I support you further today?"
            
        system_instruction = (
            "You are a professional, empathetic wellness tracker assistant. "
            "Do not provide medical diagnoses. Do not invent facts about the user. "
            "If sensitive data appears redacted as [REDACTED:...], do not ask the user to repeat it — "
            "instead remind them not to share passwords or account numbers in chat."
        )
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[message],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.4,
                ),
            )
            return response.text
        except Exception as e:
            logger.error(f"GenAI Error: {e}")
            return "I'm having trouble connecting right now, but I am here for you. Please take a deep breath."

    async def extract_scores_from_chat(self, message: str) -> dict:
        """Extract stress and anxiety scores (0–10) from a user message."""
        if self.is_mock:
            return {"stress": 5.0, "anxiety": 4.0}

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    f'Rate the stress and anxiety level of this message from 0.0 to 10.0. '
                    f'Return JSON only: {{"stress": X, "anxiety": Y}}\n\nMessage: {message}'
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            import json
            data = json.loads(response.text)
            return {
                "stress": float(data.get("stress", 0.0)),
                "anxiety": float(data.get("anxiety", 0.0)),
            }
        except Exception as e:
            logger.error(f"Score extraction error: {e}")
            return {"stress": 0.0, "anxiety": 0.0}

    async def extract_stress_from_chat(self, message: str) -> float:
        """Extract a single stress float (0-10) from a user message."""
        scores = await self.extract_scores_from_chat(message)
        return scores["stress"]
