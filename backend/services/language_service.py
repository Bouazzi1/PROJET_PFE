from lingua import Language, LanguageDetectorBuilder


class LanguageService:
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_languages(
            Language.FRENCH, Language.ARABIC, Language.ENGLISH
        ).build()

    def detect(self, text: str) -> str:
        lang = self.detector.detect_language_of(text)
        if lang == Language.ARABIC:
            return "ar"
        # Default to French for both French and English
        return "fr"


language_service = LanguageService()
