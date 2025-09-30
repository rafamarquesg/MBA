"""
Léxico hierárquico para detecção de violência (base pública).
"""

VIOLENCE_LEXICON = {
    "medical_formal": {
        "weight": 2.8,
        "terms": [
            "trauma contundente", "TCE", "hematoma", "fratura", "equimose"
            # ... adicione todos os termos conforme sua base
        ]
    },
    "legal_police": {
        "weight": 2.5,
        "terms": [
            "agressão física", "lesão corporal", "vias de fato"
            # ... adicione todos os termos conforme sua base
        ]
    }
    # ... outras categorias
}

def get_lexicon():
    """Retorna o léxico completo"""
    return VIOLENCE_LEXICON

def get_category_weights():
    """Retorna os pesos por categoria"""
    return {cat: info["weight"] for cat, info in VIOLENCE_LEXICON.items()}