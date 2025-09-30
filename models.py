"""
Modelos de dados do sistema NUVE.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class PatientIdentifier:
    patient_id: str
    document_hash: str
    filename: str
    extracted_ids: Dict[str, str] = field(default_factory=dict)
    rghc: Optional[str] = None
    codigo_paciente: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[str] = None
    nome_paciente: Optional[str] = None

@dataclass
class PageInfo:
    page_number: int
    page_text: str
    page_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentMetadata:
    document_date: Optional[str] = None
    document_type: str = "OUTROS"
    creation_date: Optional[str] = None
    author: Optional[str] = None
    service: Optional[str] = None

@dataclass
class TextContent:
    text: str
    page_count: int
    extraction_method: str
    quality_level: str
    char_count: int
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    pages_info: List[PageInfo] = field(default_factory=list)
    document_metadata: DocumentMetadata = field(default_factory=DocumentMetadata)

@dataclass
class ViolenceDetection:
    term: str
    category: str
    base_weight: float
    adjusted_weight: float
    context_phrase: str
    position_start: int
    position_end: int
    confidence_score: float = 1.0
    intensity_multiplier: float = 1.0
    found_date: Optional[str] = None
    full_sentence: str = ""
    page_number: int = 0
    document_date: Optional[str] = None

@dataclass
class ViolencePatterns:
    chronic_violence: bool = False
    escalation_pattern: bool = False
    weapons_involved: bool = False
    children_present: bool = False
    pregnancy_violence: bool = False
    sexual_violence: bool = False
    death_threats: bool = False
    multiple_injuries: bool = False
    psychological_control: bool = False
    economic_abuse: bool = False
    pattern_severity_score: float = 0.0

@dataclass
class AnalysisResult:
    patient_id: PatientIdentifier
    text_content: TextContent
    total_score: float
    base_score: float
    contextual_bonus: float
    severity_level: str
    detections: List[ViolenceDetection]
    violence_patterns: ViolencePatterns
    category_scores: Dict[str, float]
    category_counts: Dict[str, int]
    context_phrases: List[str]
    processing_time_ms: int
    status: str
    error_message: Optional[str] = None