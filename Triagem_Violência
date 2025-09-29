# SISTEMA NUVE v2.1 - Análise de Violência em "nome da pasta" Médicos
# Código completo para execução no Google Colab

#  INSTALAÇÃO DE DEPENDÊNCIAS
print("📦 Instalando dependências necessárias...")

!pip install pdfplumber pdf2image pytesseract pandas gspread google-auth PyMuPDF openpyxl -q
!sudo apt update > /dev/null 2>&1
!sudo apt install tesseract-ocr libtesseract-dev poppler-utils -y > /dev/null 2>&1

print("✅ Dependências instaladas com sucesso!")

# MONTAGEM DO GOOGLE DRIVE 
print("\n📁 Montando Google Drive...")

from google.colab import drive
drive.mount('/content/drive')

print("✅ Google Drive montado com sucesso!")

# CONFIGURAÇÃO
FOLDER_PATH = '/content/drive/MyDrive/"nome da pasta"_Nuve'
RESULTS_PATH = '/content/results_nuve'

print(f"\n🎯 Pasta configurada: {FOLDER_PATH}")

# Verificação da pasta
import os
from pathlib import Path

if os.path.exists(FOLDER_PATH):
    pdf_files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith('.pdf')]
    print(f"✅ Pasta encontrada! {len(pdf_files)} PDFs detectados:")
    for i, pdf in enumerate(pdf_files[:5]):
        print(f"  {i+1}. {pdf}")
    if len(pdf_files) > 5:
        print(f"  ... e mais {len(pdf_files)-5} arquivos")
else:
    print(f"❌ ATENÇÃO: Pasta não encontrada!")
    print("Certifique-se de que a pasta '"nome da pasta"_Nuve' existe no seu Google Drive")

# IMPORTAÇÕES
print("\n🔧 Importando bibliotecas...")

import re
import json
import hashlib
import logging
import tempfile
import zipfile
import csv
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
from enum import Enum
import pytz
from pathlib import Path

# Imports para processamento de PDF
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

print("✅ Bibliotecas importadas com sucesso!")

# CONFIGURAÇÕES E ENUMS 

@dataclass
class ProcessingConfig:
    ocr_threshold: int = 100
    max_file_size_mb: int = 50
    context_window_chars: int = 150
    min_text_quality_chars: int = 30
    anonymize_identifiers: bool = True
    secure_temp_processing: bool = True
    log_sensitive_data: bool = False
    batch_size: int = 10
    enable_parallel_processing: bool = False
    cache_compiled_patterns: bool = True
    output_formats: List[str] = field(default_factory=lambda: ['csv', 'json'])
    include_context_phrases: bool = True
    max_phrases_per_document: int = 25
    enable_pattern_analysis: bool = True

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

# MODELOS DE DADOS

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
    document_type: DocumentType = DocumentType.OUTROS
    creation_date: Optional[str] = None
    author: Optional[str] = None
    service: Optional[str] = None

@dataclass
class TextContent:
    text: str
    page_count: int
    extraction_method: str
    quality_level: QualityLevel
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
    status: ProcessingStatus
    error_message: Optional[str] = None

# BASE LEXICAL EXPANDIDA

class ExpandedViolenceLexicon:
    """Base lexical expandida com 1500+ termos para detecção de violência médica"""

    def __init__(self):
        self.categories = self._load_expanded_violence_lexicon()
        self.compiled_patterns = {}
        self.negation_patterns = self._compile_negation_patterns()
        self.contextual_patterns = self._compile_contextual_patterns()
        self._compile_all_patterns()

    def _load_expanded_violence_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Carrega base lexical expandida com categorias especializadas"""
        return {
            "medical_formal": {
                "weight": 2.8,
                "terms": [
                    "trauma contundente", "trauma por força contusa", "lesão contundente",
                    "trauma cranioencefálico", "TCE", "traumatismo craniano", "trauma facial",
                    "trauma cervical", "trauma torácico", "trauma abdominal", "politraumatismo",
                    "hematoma subdural", "hematoma epidural", "hematoma intracraniano",
                    "hematoma retroauricular", "hematoma periorbitário", "hematoma occipital",
                    "equimose periorbital", "hematoma periorbital", "olho roxo", "olho negro",
                    "equimoses múltiplas", "equimoses em diferentes estágios", "equimoses bilaterais",
                    "laceração cutânea", "laceração facial", "laceração profunda",
                    "laceração do couro cabeludo", "laceração labial", "laceração genital",
                    "ferimento corto-contuso", "ferimento inciso", "ferimento perfurante",
                    "ferimento por arma de fogo", "ferimento por arma branca", "lesão por projétil",
                    "fratura de mandíbula", "fratura maxilar", "fratura facial", "fratura nasal",
                    "fratura de órbita", "fratura zigomática", "fratura do arco zigomático",
                    "fratura de costela", "fraturas múltiplas", "fratura espiral",
                    "queimadura intencional", "queimadura por cigarro", "queimadura circunscrita",
                    "queimadura por líquido quente", "queimadura por ferro", "queimadura em luva",
                    "escoriações múltiplas", "escoriações lineares", "escoriações ungueais",
                    "marcas de mordida humana", "marcas de dedos", "marcas de mão",
                    "marcas de corda", "marcas de estrangulamento", "marcas de amarração",
                    "petéquias no pescoço", "equimoses cervicais", "sulco de enforcamento",
                    "lesões de defesa", "ferimentos defensivos", "trauma não acidental",
                    "violência sexual", "estupro", "abuso sexual", "trauma genital",
                    "laceração vaginal", "laceração anal", "lesão himenal", "hematoma genital",
                    "negligência grave", "desnutrição proteico-calórica", "abandono de incapaz",
                    "desidratação severa", "má higiene corporal", "lesões por decúbito",
                    "transtorno de estresse pós-traumático", "TEPT", "depressão reativa",
                    "ansiedade pós-traumática", "dissociação", "flashbacks",
                    "ideação suicida", "tentativa de suicídio", "automutilação", "autoextermínio",
                    "comportamento autodestrutivo", "tentativa de autolesão",
                    "síndrome do bebê sacudido", "trauma craniano não acidental",
                    "hemorragia retiniana", "hematoma subdural em criança"
                ]
            },
            "legal_police": {
                "weight": 2.5,
                "terms": [
                    "agressão física", "agressão corporal", "violência física",
                    "lesão corporal", "lesão corporal leve", "lesão corporal grave",
                    "lesão corporal gravíssima", "vias de fato", "violência doméstica",
                    "ameaça", "ameaça de morte", "intimidação", "ameaça grave",
                    "ameaça com arma", "ameaça de espancamento", "intimidação psicológica",
                    "chantagem", "extorsão", "coação", "constrangimento ilegal",
                    "cárcere privado", "sequestro", "sequestro relâmpago",
                    "privação de liberdade", "confinamento forçado", "aprisionamento",
                    "estupro", "estupro de vulnerável", "atentado violento ao pudor",
                    "assédio sexual", "abuso sexual", "exploração sexual",
                    "violência sexual", "estupro conjugal", "sexo forçado",
                    "homicídio", "tentativa de homicídio", "feminicídio",
                    "tentativa de feminicídio", "latrocínio", "assassinato",
                    "arma branca", "arma de fogo", "objeto contundente",
                    "faca", "revólver", "pistola", "martelo",
                    "bastão", "cassetete", "pedra", "tijolo",
                    "espancamento", "surra", "paulada", "facada", "tiro",
                    "enforcamento", "estrangulamento", "sufocamento", "asfixia",
                    "boletim de ocorrência", "B.O.", "inquérito policial",
                    "termo circunstanciado", "flagrante delito", "prisão em flagrante",
                    "medida protetiva de urgência", "ordem de proteção",
                    "exame de corpo de delito", "laudo pericial", "perícia criminal"
                ]
            },
            "maria_penha_domestic": {
                "weight": 2.3,
                "terms": [
                    "violência doméstica", "violência intrafamiliar", "violência conjugal",
                    "violência de gênero", "violência contra mulher", "maus-tratos domésticos",
                    "violência no lar", "agressão doméstica", "abuso doméstico",
                    "feminicídio", "tentativa de feminicídio", "crime passional",
                    "ciclo da violência", "ciclo de abuso", "escalada da violência",
                    "violência repetitiva", "padrão de agressão", "histórico de violência",
                    "relacionamento abusivo", "namoro violento", "parceiro abusivo",
                    "companheiro violento", "marido agressor", "ex-parceiro violento",
                    "violência física doméstica", "violência psicológica", "violência moral",
                    "violência sexual conjugal", "violência patrimonial", "violência econômica",
                    "controle coercitivo", "dominação psicológica", "ciúmes patológicos",
                    "possessividade excessiva", "controle obsessivo", "comportamento controlador",
                    "isolamento social forçado", "proibição de trabalhar", "proibição de sair",
                    "proibição de estudar", "afastamento da família", "isolamento de amigos",
                    "monitoramento digital", "controle de celular", "cyberstalking",
                    "violência virtual", "stalking digital", "perseguição online",
                    "humilhação constante", "gaslighting", "chantagem emocional",
                    "manipulação psicológica", "terrorismo psicológico", "tortura psicológica",
                    "destruição de objetos pessoais", "controle financeiro absoluto",
                    "privação de recursos", "destruição de documentos", "delegacia da mulher",
                    "casa abrigo", "medidas protetivas", "centro de referência"
                ]
            },
            "healthcare_nursing": {
                "weight": 2.0,
                "terms": [
                    "paciente relata violência", "usuário informa agressão", "refere maus-tratos",
                    "história de violência", "episódios de violência", "relato de agressão",
                    "menciona espancamento", "conta sobre agressão", "narra violência",
                    "história pregressa de violência", "episódios anteriores de violência",
                    "antecedentes de maus-tratos", "histórico de agressões",
                    "violência recorrente", "agressões repetidas", "maus-tratos crônicos",
                    "sinais evidentes de violência", "indícios de maus-tratos",
                    "suspeita de violência doméstica", "lesões compatíveis com agressão",
                    "ferimentos sugestivos", "padrão de lesões", "lesões não acidentais",
                    "hematomas múltiplos", "equimoses generalizadas", "roxos pelo corpo",
                    "marcas visíveis", "ferimentos em cicatrização", "lesões recentes",
                    "queimaduras circunscritas", "marca de cigarro", "queimadura suspeita",
                    "escoriações lineares", "arranhões defensivos", "marcas de unhas",
                    "dinâmica familiar conturbada", "relacionamento conjugal conflituoso",
                    "ambiente familiar violento", "tensão familiar evidente",
                    "filhos presenciam violência", "crianças traumatizadas",
                    "menores expostos à violência", "impacto psicológico nas crianças",
                    "comportamento de submissão", "evita contato visual", "hipervigilância",
                    "medo excessivo", "ansiedade extrema", "comportamento evasivo",
                    "tremores generalizados", "sudorese profusa", "taquicardia",
                    "notificação compulsória", "ficha de notificação de violência",
                    "comunicação ao conselho tutelar", "relatório de suspeita"
                ]
            },
            "colloquial_popular": {
                "weight": 1.8,
                "terms": [
                    "surra", "porrada", "pancada", "sova", "cacetada", "paulada",
                    "bordoada", "tapão", "sopapo", "bicuda", "coice", "pescoção",
                    "soco", "murro", "tapa", "bofetada", "cascudo", "chute", "pontapé",
                    "joelhada", "cabeçada", "cotovelada", "pisão", "empurrão", "beliscão",
                    "bateu na mulher", "agrediu a esposa", "espancou a companheira",
                    "deu uma surra", "quebrou na porrada", "meteu a mão",
                    "me bateu", "apanhei dele", "levei surra", "me deu porrada",
                    "me agrediu", "me espancou", "bateu em mim", "me machucou",
                    "ameaçou me matar", "disse que me mata", "prometeu me acabar",
                    "falou que ia me quebrar", "ameaçou me dar uma surra",
                    "muito ciumento", "não deixa sair", "controla tudo", "mexe no celular",
                    "não deixa trabalhar", "vigia sempre", "segue para todo lado",
                    "me forçou", "me obrigou", "não aceitou não", "forçou a barra",
                    "briga de casal", "confusão em casa", "quebra-pau em casa",
                    "barraco em casa", "discussão feia", "briga violenta",
                    "bebe e fica violento", "viciado agressivo", "noiado violento",
                    "tacou objeto", "jogou coisa", "atirou na parede",
                    "ficou todo roxo", "marcou o rosto", "deixou marca"
                ]
            },
            "orthographic_variations": {
                "weight": 1.5,
                "terms": [
                    "agressão", "agreção", "agressao", "agresão", "agrediu", "agridiu",
                    "agredindo", "agridindo", "agressor", "agresor", "agressivo", "agresivo",
                    "violência", "violencia", "violensia", "violensa", "violento", "violênto",
                    "espancamento", "spancamento", "espancou", "espankou", "espancada",
                    "machucou", "machukou", "machucu", "machucado", "machucada",
                    "bateu", "batêu", "batu", "batendo", "bateno", "bater", "batê",
                    "ameaçou", "ameaçô", "ameaço", "ameaçando", "ameaçano", "ameaça", "ameasa",
                    "judiou", "judiô", "judiar", "judiá", "maltratou", "maltrató"
                ]
            },
            "psychological_abuse": {
                "weight": 1.9,
                "terms": [
                    "manipulação psicológica", "chantagem emocional", "gaslighting",
                    "lavagem cerebral", "distorção da realidade", "confusão mental induzida",
                    "humilhação constante", "desmoralização", "diminuição sistemática",
                    "isolamento social", "afastamento forçado", "separação de familiares",
                    "controle mental", "dominação psicológica", "subjugação emocional"
                ]
            },
            "child_specific": {
                "weight": 2.7,
                "terms": [
                    "maus-tratos infantis", "abuso infantil", "negligência infantil",
                    "violência contra criança", "agressão a menor", "maltrato infantil",
                    "síndrome do bebê sacudido", "trauma craniano não acidental em criança",
                    "lesões não acidentais em menor", "negligência de cuidados básicos",
                    "privação de alimentos", "falta de higiene", "abandono de incapaz"
                ]
            }
        }

    def _compile_negation_patterns(self) -> List[re.Pattern]:
        """Compila padrões de negação expandidos"""
        negation_terms = [
            "não", "nao", "jamais", "nunca", "nega", "negou", "descarta",
            "afasta", "exclui", "ausente", "sem", "inexistente", "improvável",
            "sem evidências", "sem indícios", "sem sinais", "descartado"
        ]

        patterns = []
        for term in negation_terms:
            pattern = re.compile(
                rf'\b{re.escape(term)}\b[\s\w]{{0,80}}\b(?:viol|agred|espanc|machuc|bat|surr|ameaç|mal.?trat)\w*',
                re.IGNORECASE
            )
            patterns.append(pattern)

        return patterns

    def _compile_contextual_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compila padrões contextuais expandidos"""
        return {
            "intensifying_contexts": [
                re.compile(r'\b(sempre|todo\s*dia|constantemente|frequentemente|diariamente|rotineiramente)\b.{0,50}\b(agred|bat|violent|maltrat)\w*', re.IGNORECASE),
                re.compile(r'\b(na\s*frente|presença|vista)\b.{0,30}\b(crianças?|filhos?|menores?)\b.{0,50}\b(agred|bat|violent)\w*', re.IGNORECASE),
                re.compile(r'\b(grávida|gestante|gestação)\b.{0,50}\b(agred|bat|chut|violent|espanc)\w*', re.IGNORECASE),
                re.compile(r'\b(com|usando|ameaçou\s*com|empunhando)\b.{0,30}\b(faca|revólver|pistola|arma|martelo)\b', re.IGNORECASE),
            ],
            "medical_severity": [
                re.compile(r'\b(fratura|sangramento|hemorragia|trauma)\b.{0,30}\b(agred|bat|violent)\w*', re.IGNORECASE),
                re.compile(r'\b(cirurgia|sutura|pontos)\b.{0,50}\b(agred|bat|violent)\w*', re.IGNORECASE),
            ]
        }

    def _compile_all_patterns(self):
        """Compila todos os padrões regex"""
        for category, data in self.categories.items():
            terms_escaped = [re.escape(term) for term in data['terms']]
            combined_pattern = '|'.join(terms_escaped)
            full_pattern = rf'(.{{0,150}})({combined_pattern})(.{{0,150}})'

            self.compiled_patterns[category] = {
                'pattern': re.compile(full_pattern, re.IGNORECASE | re.DOTALL),
                'weight': data['weight'],
                'terms_count': len(data['terms'])
            }

    def detect_negation_context(self, text: str, match_start: int, match_end: int) -> bool:
        """Detecta contexto de negação"""
        context_start = max(0, match_start - 150)
        before_context = text[context_start:match_end]

        for negation_pattern in self.negation_patterns:
            if negation_pattern.search(before_context):
                return True
        return False

    def analyze_contextual_intensity(self, text: str, detection: ViolenceDetection) -> float:
        """Analisa intensidade contextual expandida"""
        intensity_multiplier = 1.0

        start = max(0, detection.position_start - 200)
        end = min(len(text), detection.position_end + 200)
        context = text[start:end].lower()

        # Verificar contextos intensificadores
        for pattern in self.contextual_patterns['intensifying_contexts']:
            if pattern.search(context):
                intensity_multiplier += 0.5

        # Verificar severidade médica
        for pattern in self.contextual_patterns['medical_severity']:
            if pattern.search(context):
                intensity_multiplier += 0.7

        return max(0.1, min(5.0, intensity_multiplier))

    def detect_violence_patterns(self, text: str) -> ViolencePatterns:
        """Detecta padrões específicos de violência expandidos"""
        text_lower = text.lower()
        patterns = ViolencePatterns()

        # Violência crônica
        chronic_indicators = ['sempre', 'todo dia', 'constantemente', 'anos', 'rotina', 'frequentemente']
        if any(indicator in text_lower for indicator in chronic_indicators):
            patterns.chronic_violence = True
            patterns.pattern_severity_score += 1.2

        # Armas
        weapons = ['faca', 'revolver', 'pistola', 'arma', 'martelo']
        if any(weapon in text_lower for weapon in weapons):
            patterns.weapons_involved = True
            patterns.pattern_severity_score += 1.8

        # Crianças presentes
        children_contexts = ['na frente das crianças', 'criança viu', 'filho assistiu']
        if any(context in text_lower for context in children_contexts):
            patterns.children_present = True
            patterns.pattern_severity_score += 1.5

        # Violência na gravidez
        pregnancy_terms = ['grávida', 'gestante', 'chutou barriga']
        if any(term in text_lower for term in pregnancy_terms):
            patterns.pregnancy_violence = True
            patterns.pattern_severity_score += 2.2

        # Violência sexual
        sexual_terms = ['estupro', 'abuso sexual', 'forçou', 'obrigou']
        if any(term in text_lower for term in sexual_terms):
            patterns.sexual_violence = True
            patterns.pattern_severity_score += 2.5

        # Ameaças de morte
        death_threats = ['vou te matar', 'vai morrer', 'ameaçou de morte']
        if any(threat in text_lower for threat in death_threats):
            patterns.death_threats = True
            patterns.pattern_severity_score += 2.0

        return patterns

# EXTRATOR DE TEXTO

class EnhancedTextExtractor:
    """Extrator de texto incrementado com informações de página e metadados"""

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger("EnhancedTextExtractor")
        self.document_classifier = DocumentClassifier()
        self.metadata_extractor = DocumentMetadataExtractor()

    def extract_from_pdf(self, pdf_path: Path) -> TextContent:
        """Extrai texto com informações de página e metadados"""

        # Validar arquivo
        self._validate_input_file(pdf_path)

        # Tentar métodos em ordem de preferência
        extraction_methods = []

        if HAS_PDFPLUMBER:
            extraction_methods.append(("pdfplumber", self._extract_with_pdfplumber))
        if HAS_FITZ:
            extraction_methods.append(("fitz", self._extract_with_fitz))
        if HAS_OCR:
            extraction_methods.append(("ocr", self._extract_with_ocr))

        if not extraction_methods:
            raise Exception("Nenhuma biblioteca de PDF disponível")

        last_error = None

        for method_name, extract_method in extraction_methods:
            try:
                print(f"  Tentando {method_name}...")
                text, metadata, pages_info = extract_method(pdf_path)

                if self._is_sufficient_text(text):
                    quality = self._assess_text_quality(text)
                    print(f"  ✓ Sucesso com {method_name}")

                    # Extrair metadados do documento
                    doc_metadata = self.metadata_extractor.extract_metadata(text, pages_info)

                    return TextContent(
                        text=self._clean_text(text),
                        page_count=metadata.get('page_count', 0),
                        extraction_method=method_name,
                        quality_level=quality,
                        char_count=len(text),
                        word_count=len(text.split()),
                        metadata=metadata,
                        pages_info=pages_info,
                        document_metadata=doc_metadata
                    )
                else:
                    print(f"  ⚠ Texto insuficiente com {method_name}")
            except Exception as e:
                last_error = e
                print(f"  ✗ {method_name} falhou: {e}")
                continue

        raise Exception(f"Todos os métodos falharam para {pdf_path.name}. Último erro: {last_error}")

    def _validate_input_file(self, file_path: Path):
        """Valida arquivo de entrada"""
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise Exception(f"Arquivo muito grande: {file_size_mb:.2f}MB")

        if file_path.suffix.lower() != '.pdf':
            raise Exception(f"Tipo de arquivo não suportado: {file_path.suffix}")

    def _extract_with_pdfplumber(self, pdf_path: Path) -> Tuple[str, Dict, List[PageInfo]]:
        """Extração com pdfplumber - INCREMENTADA"""
        text = ""
        metadata = {"method": "pdfplumber", "pages_processed": []}
        pages_info = []

        with pdfplumber.open(pdf_path) as pdf:
            metadata['page_count'] = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 10:
                        text += f"\n--- PÁGINA {i+1} ---\n{page_text}\n"
                        metadata['pages_processed'].append(i+1)

                        # Criar informações da página
                        page_info = PageInfo(
                            page_number=i+1,
                            page_text=page_text,
                            page_metadata={
                                'width': page.width,
                                'height': page.height,
                                'rotation': getattr(page, 'rotation', 0)
                            }
                        )
                        pages_info.append(page_info)
                except Exception:
                    continue

        return text, metadata, pages_info

    def _extract_with_fitz(self, pdf_path: Path) -> Tuple[str, Dict, List[PageInfo]]:
        """Extração com PyMuPDF - INCREMENTADA"""
        text = ""
        metadata = {"method": "fitz", "pages_processed": []}
        pages_info = []

        doc = fitz.open(pdf_path)
        metadata['page_count'] = len(doc)

        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text and len(page_text.strip()) > 10:
                    text += f"\n--- PÁGINA {page_num+1} ---\n{page_text}\n"
                    metadata['pages_processed'].append(page_num+1)

                    # Criar informações da página
                    page_info = PageInfo(
                        page_number=page_num+1,
                        page_text=page_text,
                        page_metadata={
                            'rect': page.rect,
                            'rotation': page.rotation
                        }
                    )
                    pages_info.append(page_info)
            except Exception:
                continue

        doc.close()
        return text, metadata, pages_info

    def _extract_with_ocr(self, pdf_path: Path) -> Tuple[str, Dict, List[PageInfo]]:
        """Extração com OCR - INCREMENTADA"""
        text = ""
        metadata = {"method": "ocr", "pages_processed": []}
        pages_info = []

        try:
            pages = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=5)
            metadata['page_count'] = len(pages)

            for i, page_image in enumerate(pages):
                try:
                    page_text = pytesseract.image_to_string(page_image, lang='por')

                    if page_text and len(page_text.strip()) > 20:
                        text += f"\n--- PÁGINA {i+1} (OCR) ---\n{page_text}\n"
                        metadata['pages_processed'].append(i+1)

                        # Criar informações da página
                        page_info = PageInfo(
                            page_number=i+1,
                            page_text=page_text,
                            page_metadata={
                                'ocr_method': 'pytesseract',
                                'image_size': page_image.size
                            }
                        )
                        pages_info.append(page_info)
                except Exception:
                    continue
        except Exception as e:
            raise Exception(f"Erro OCR: {e}")

        return text, metadata, pages_info

    def _is_sufficient_text(self, text: str) -> bool:
        """Verifica se o texto é suficiente"""
        if not text:
            return False
       
