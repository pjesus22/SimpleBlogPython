import re
import unicodedata


def normalize_text(text):
    text = text.lower()
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'
    )
    text = re.sub(r'[^\w\s]', ' ', text)
    text = f' {text.strip()} '
    return text
