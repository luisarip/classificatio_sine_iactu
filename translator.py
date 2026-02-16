from deep_translator import GoogleTranslator
import time

def translate_latin_to_english(sentences, delay=0.5):
    """
    Translates a list of Latin sentences to English.
    """
    translator = GoogleTranslator(source='la', target='en')
    translated = []

    for i, sent in enumerate(sentences):
        try:
            translation = translator.translate(sent)
            translated.append(translation)
            print(f"Progress: {i+1}/{len(sentences)} sentences translated.")
            time.sleep(delay)
        except Exception as e:
            print(f"Error at index {i}: {e}")
            translated.append(sent) # Fallback to original
            
    return translated