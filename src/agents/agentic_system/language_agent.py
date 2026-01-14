"""
Language Agent
==============

Handles translation and language-specific content generation.
Supports English, Urdu, and Roman Urdu.
"""

from typing import Dict, Any, Optional


class LanguageAgent:
    """Manages multilingual content delivery."""

    def __init__(self):
        self.supported_languages = ["en", "ur", "ur_roman"]
        
        self.translations = {
            "hello": {"en": "Hello", "ur": "السلام علیکم", "ur_roman": "Assalamu Alaikum"},
            "what": {"en": "What", "ur": "کیا", "ur_roman": "Kya"},
            "how": {"en": "How", "ur": "کیسے", "ur_roman": "Kaise"},
            "why": {"en": "Why", "ur": "کیوں", "ur_roman": "Kyun"},
            "when": {"en": "When", "ur": "کب", "ur_roman": "Kab"},
            "where": {"en": "Where", "ur": "کہاں", "ur_roman": "Kahan"},
            "question": {"en": "Question", "ur": "سوال", "ur_roman": "Sawal"},
            "answer": {"en": "Answer", "ur": "جواب", "ur_roman": "Jawab"},
            "correct": {"en": "Correct", "ur": "صحیح", "ur_roman": "Sahih"},
            "wrong": {"en": "Wrong", "ur": "غلط", "ur_roman": "Ghalat"},
            "excellent": {"en": "Excellent", "ur": "بہترین", "ur_roman": "Behtareen"},
            "good_try": {"en": "Good try", "ur": "اچھی کوشش", "ur_roman": "Achi Koshish"},
            "try_again": {"en": "Try again", "ur": "دوبارہ کوشش کریں", "ur_roman": "Dobara Koshish Karen"},
            "solution": {"en": "Solution", "ur": "حل", "ur_roman": "Hal"},
            "step": {"en": "Step", "ur": "قدم", "ur_roman": "Qadam"},
        }

    def translate_content(
        self,
        content: str,
        targetLanguage: str,
        context: Dict[str, Any] = None,
    ) -> str:
        """Translate content to target language."""
        if targetLanguage == "en":
            return content
        
        # Simple word-by-word translation for demonstration
        translated = content
        
        for english, translations in self.translations.items():
            if english in content.lower():
                if targetLanguage in translations:
                    translated = translated.replace(
                        english,
                        translations[targetLanguage],
                        1
                    )
        
        return translated

    def format_for_language(
        self,
        content: Dict[str, Any],
        language: str,
    ) -> Dict[str, Any]:
        """Format content for specific language."""
        if language == "ur":
            # Urdu: right-to-left
            return {
                **content,
                "direction": "rtl",
                "font": "urdu",
                "encoding": "utf-8",
            }
        elif language == "ur_roman":
            # Roman Urdu: left-to-right
            return {
                **content,
                "direction": "ltr",
                "font": "roman",
                "encoding": "utf-8",
            }
        else:
            # English
            return {
                **content,
                "direction": "ltr",
                "font": "english",
                "encoding": "utf-8",
            }

    def generate_multilingual_response(
        self,
        enContent: str,
        language: str,
    ) -> Dict[str, Any]:
        """Generate response in student's language."""
        if language not in self.supported_languages:
            language = "en"
        
        # Translate to target language
        translated = self.translate_content(enContent, language)
        
        # Format appropriately
        formatted = self.format_for_language(
            {"content": translated},
            language,
        )
        
        return {
            "language": language,
            "originalLanguage": "en",
            **formatted,
        }

    def detect_language_preference(
        self,
        userInput: str,
    ) -> str:
        """Detect user's language preference from input."""
        # Urdu script detection
        urdu_chars = "آ ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن ں و ہ ء ی ے"
        if any(char in userInput for char in urdu_chars):
            return "ur"
        
        # Roman Urdu detection
        roman_urdu_patterns = [
            "kya", "hai", "acha", "bilkul", "theek", "phir", 
            "seekh", "soch", "likh", "sunn", "pooch"
        ]
        if any(pattern in userInput.lower() for pattern in roman_urdu_patterns):
            return "ur_roman"
        
        return "en"

    def adapt_vocabulary(
        self,
        content: str,
        difficulty: str,
        language: str,
    ) -> str:
        """Adapt vocabulary level for difficulty."""
        if difficulty == "beginner":
            # Use simpler words
            vocabulary_map = {
                "calculate": "find",
                "determine": "figure out",
                "demonstrate": "show",
                "analyze": "look at",
            }
        elif difficulty == "advanced":
            # Use technical terms
            vocabulary_map = {
                "find": "calculate",
                "figure out": "determine",
                "show": "demonstrate",
                "look at": "analyze",
            }
        else:
            vocabulary_map = {}
        
        adapted = content
        for simple, technical in vocabulary_map.items():
            adapted = adapted.replace(simple, technical, 1)
        
        return adapted

    def get_cultural_context(self, language: str) -> Dict[str, Any]:
        """Get cultural context for language."""
        contexts = {
            "en": {
                "culturalReferences": "Western context",
                "examples": "Western scenarios",
                "timeFormat": "12-hour",
                "dateFormat": "MM/DD/YYYY",
            },
            "ur": {
                "culturalReferences": "Pakistani/Islamic context",
                "examples": "Pakistani scenarios",
                "timeFormat": "12-hour",
                "dateFormat": "DD/MM/YYYY",
            },
            "ur_roman": {
                "culturalReferences": "Pakistani context (Roman script)",
                "examples": "Pakistani scenarios",
                "timeFormat": "12-hour",
                "dateFormat": "DD/MM/YYYY",
            },
        }
        
        return contexts.get(language, contexts["en"])

    def generate_culturally_relevant_example(
        self,
        topic: str,
        language: str,
    ) -> str:
        """Generate culturally relevant example for topic."""
        examples = {
            "en": {
                "algebra": "If John has 5 apples...",
                "geometry": "A rectangular field...",
            },
            "ur": {
                "algebra": "اگر علی کے پاس 5 سیب ہیں...",
                "geometry": "ایک مربع باغ...",
            },
            "ur_roman": {
                "algebra": "Agar Ali ke paas 5 seb hain...",
                "geometry": "Ek murabba baagh...",
            },
        }
        
        lang_examples = examples.get(language, examples["en"])
        return lang_examples.get(topic, f"Example for {topic}")
