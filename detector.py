"""
Detector de violência em textos médicos usando léxico hierárquico.
"""

from .lexicon import get_lexicon

class ViolenceDetector:
    def __init__(self):
        self.lexicon = get_lexicon()
    
    def analyze(self, text):
        text_lower = text.lower()
        results = []
        for category, info in self.lexicon.items():
            for term in info["terms"]:
                if term.lower() in text_lower:
                    results.append({
                        "term": term,
                        "category": category,
                        "weight": info["weight"]
                    })
        return results