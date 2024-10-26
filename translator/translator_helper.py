
from googletrans import Translator

translator = Translator()


def translate_text(text: str, dest_language: str = 'en') -> str:
    """Translate text to the specified destination language."""
    try:
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")
