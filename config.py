"""
Configurações e enums do sistema NUVE.
"""

from enum import Enum

class ProcessingStatus(Enum):
    SUCCESS = "sucesso"
    PDF_CORRUPTED = "pdf_corrompido"
    OCR_FAILED = "ocr_falhou"
    INSUFFICIENT_TEXT = "texto_insuficiente"
    PROCESSING_ERROR = "erro_processamento"
    SECURITY_ERROR = "erro_seguranca"

class QualityLevel(Enum):
    EXCELLENT = "excelente"
    GOOD = "boa"
    FAIR = "regular"
    POOR = "ruim"

class SeverityLevel(Enum):
    CRITICAL = "CRÍTICO"
    HIGH = "ALTO"
    MODERATE = "MODERADO"
    LOW = "BAIXO"
    MINIMAL = "MÍNIMO"
    NONE = "SEM INDICAÇÃO"

class DocumentType(Enum):
    EVOLUCAO_MEDICA = "Evolução Médica"
    ANOTACOES_ENFERMAGEM = "Anotações da Enfermagem"
    MULTIPROFISSIONAL = "Multiprofissional"
    OUTROS = "Outros"