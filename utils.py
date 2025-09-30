"""
Funções auxiliares do sistema NUVE.
"""

import hashlib

def hash_text(text: str) -> str:
    """Gera hash SHA256 para anonimização."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()