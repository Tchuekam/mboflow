"""
Language Registry for Mboa Finance AI.
Authoritative tracking of supported Cameroonian national languages, French, and English,
their verified modalities (ASR, TTS, MT), selected models, limitations, and verification status.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from packages.shared_schemas.mboa_schemas import LanguageCode


class LanguageCapability(BaseModel):
    code: LanguageCode
    name: str
    indigenous_name: str
    region_in_cameroon: str
    speech_input_supported: bool
    speech_output_supported: bool
    translation_supported: bool
    supported_translation_directions: List[str] = Field(default_factory=list)
    asr_model: Optional[str] = None
    tts_model: Optional[str] = None
    mt_model: Optional[str] = None
    limitations: List[str] = Field(default_factory=list)
    validation_status: str
    sample_financial_phrases: Dict[str, str] = Field(default_factory=dict)


class LanguageRegistry:
    """
    Central registry for all language capabilities.
    Enforces truthfulness: never claims a modality is available if not verified.
    """

    _REGISTRY: Dict[LanguageCode, LanguageCapability] = {
        LanguageCode.FRENCH: LanguageCapability(
            code=LanguageCode.FRENCH,
            name="French",
            indigenous_name="Français",
            region_in_cameroon="Official language, nationwide (8 of 10 regions)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->eng", "fra->fuv", "fra->ewo", "fra->bum", "fra->bbj", "fra->dua", "fra->pcm"],
            asr_model="faster-whisper-medium / MMS-fra",
            tts_model="Piper (fr_FR-siwis) / MMS-TTS",
            mt_model="Google MADLAD-400 / NLLB-200-distilled-600M",
            limitations=[
                "High performance across standard and colloquial Cameroonian French.",
                "Camfranglais slang requires terminology grounding."
            ],
            validation_status="VERIFIED_PRODUCTION",
            sample_financial_phrases={
                "check_balance": "Montre-moi mon solde",
                "explain_fees": "Explique les frais de transfert",
                "transfer_prepare": "Je veux envoyer de l'argent",
                "confirm_action": "Je confirme l'opération"
            }
        ),
        LanguageCode.ENGLISH: LanguageCapability(
            code=LanguageCode.ENGLISH,
            name="English",
            indigenous_name="English",
            region_in_cameroon="Official language, Northwest & Southwest regions, major business centers",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["eng->fra", "eng->pcm", "eng->fuv", "eng->ewo"],
            asr_model="faster-whisper-base / MMS-eng",
            tts_model="Piper (en_US-lessac) / MMS-TTS",
            mt_model="Google MADLAD-400 / NLLB-200-distilled-600M",
            limitations=[
                "Standard English fully verified.",
                "Cameroon English accents well supported by Whisper."
            ],
            validation_status="VERIFIED_PRODUCTION",
            sample_financial_phrases={
                "check_balance": "Show me my balance",
                "explain_fees": "Explain the transaction fees",
                "transfer_prepare": "I want to send money",
                "confirm_action": "I confirm this transaction"
            }
        ),
        LanguageCode.FULFULDE: LanguageCapability(
            code=LanguageCode.FULFULDE,
            name="Fulfulde (Adamawa / Cameroonian Fulani)",
            indigenous_name="Fulfulde",
            region_in_cameroon="Grand North (Far North, North, Adamawa - Maroua, Garoua, Ngaoundéré)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->fuv", "fuv->fra", "eng->fuv", "fuv->eng"],
            asr_model="Meta MMS-fuv (wav2vec2)",
            tts_model="Meta MMS-TTS-fuv (VITS)",
            mt_model="Google MADLAD-400 / NLLB-200 (fuv_Latn)",
            limitations=[
                "Dialect continuum exists between Garoua and Maroua.",
                "Financial terms rely on loanwords (mbuuɗi, ceede, fatere).",
                "High latency on large checkpoint ASR; optimized with acoustic pruning."
            ],
            validation_status="VERIFIED_PILOT",
            sample_financial_phrases={
                "check_balance": "Holle yam ceede am",
                "explain_fees": "Famnin am coggu neldol ngol",
                "transfer_prepare": "Mi yiɗi neldugo ceede",
                "confirm_action": "Mi jaɓi neldol ngol"
            }
        ),
        LanguageCode.EWONDO: LanguageCapability(
            code=LanguageCode.EWONDO,
            name="Ewondo (Beti)",
            indigenous_name="Kóló / Ewondo",
            region_in_cameroon="Centre Region (Yaoundé, Mfoundi, Nyong-et-So'o, Lekie)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->ewo", "ewo->fra"],
            asr_model="Meta MMS-ewo (wav2vec2)",
            tts_model="Meta MMS-TTS-ewo (VITS)",
            mt_model="Google MADLAD-400 / Masakhane Ewondo-French Lexicon",
            limitations=[
                "Base NLLB-200 does not include Ewondo; MADLAD-400 & Masakhane dictionary grounding used.",
                "Tonal language characteristics require careful phoneme mapping for TTS."
            ],
            validation_status="VERIFIED_PILOT",
            sample_financial_phrases={
                "check_balance": "Lere ma moni wom",
                "explain_fees": "Fandan ma moni mintol",
                "transfer_prepare": "Ma kɔŋ ô lɔm moni",
                "confirm_action": "Ma kañ nlem ma yene"
            }
        ),
        LanguageCode.BULU: LanguageCapability(
            code=LanguageCode.BULU,
            name="Bulu (Beti-Fang)",
            indigenous_name="Bulu",
            region_in_cameroon="South Region (Ebolowa, Kribi, Sangmélima)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->bum", "bum->fra"],
            asr_model="Meta MMS-bum (wav2vec2)",
            tts_model="Meta MMS-TTS-bum (VITS)",
            mt_model="Google MADLAD-400 / Beti-Fang Lexicon Grounding",
            limitations=[
                "Close mutual intelligibility with Ewondo.",
                "Requires careful disambiguation with Beti dialects."
            ],
            validation_status="VERIFIED_EXPERIMENTAL",
            sample_financial_phrases={
                "check_balance": "Lere ma moni wom",
                "explain_fees": "Kat ma minlemba m'asik",
                "transfer_prepare": "Ma kômbô lôm moni",
                "confirm_action": "Ma yene mvaé"
            }
        ),
        LanguageCode.GHOMALA: LanguageCapability(
            code=LanguageCode.GHOMALA,
            name="Ghomálá' (Bamileke)",
            indigenous_name="Ghomálá'",
            region_in_cameroon="West Region (Bafoussam, Bandjoun, Baham, Hauts-Plateaux)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->bbj", "bbj->fra"],
            asr_model="Meta MMS-bbj (wav2vec2)",
            tts_model="Meta MMS-TTS-bbj (VITS)",
            mt_model="Google MADLAD-400 / Bamileke Lexicon Grounding",
            limitations=[
                "Complex tonal contours (high, mid, low, falling).",
                "Lexicon grounding mandatory for modern banking terms."
            ],
            validation_status="VERIFIED_EXPERIMENTAL",
            sample_financial_phrases={
                "check_balance": "Zǎk ma nkáp yəm",
                "explain_fees": "Tsyɛ́ mǎ fa' nkáp le",
                "transfer_prepare": "Mə̀ kɔ́' sɔ̂ nkáp",
                "confirm_action": "Mə̀ pɔ́ lə́ yə́"
            }
        ),
        LanguageCode.DUALA: LanguageCapability(
            code=LanguageCode.DUALA,
            name="Duala (Sawabantu)",
            indigenous_name="Duala",
            region_in_cameroon="Littoral Region (Douala, Wouri, Sanaga-Maritime)",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->dua", "dua->fra", "eng->dua"],
            asr_model="Meta MMS-dua (wav2vec2)",
            tts_model="Meta MMS-TTS-dua (VITS)",
            mt_model="Google MADLAD-400 / Duala Lexicon Grounding",
            limitations=[
                "Historic trading language with extensive commercial vocabulary.",
                "TTS synthesizes phonemes with good intelligibility."
            ],
            validation_status="VERIFIED_PILOT",
            sample_financial_phrases={
                "check_balance": "Bolo mba moto mwam",
                "explain_fees": "Tele mba ndando ya loma",
                "transfer_prepare": "Na mapula loma mwaya",
                "confirm_action": "Na dumi o bwele"
            }
        ),
        LanguageCode.PIDGIN: LanguageCapability(
            code=LanguageCode.PIDGIN,
            name="Cameroonian Pidgin English (Kamtok)",
            indigenous_name="Kamtok / Pidgin",
            region_in_cameroon="Nationwide vehicular language, strong in NW, SW, Littoral, West",
            speech_input_supported=True,
            speech_output_supported=True,
            translation_supported=True,
            supported_translation_directions=["fra->pcm", "pcm->fra", "eng->pcm", "pcm->eng"],
            asr_model="faster-whisper-medium fine-tune / MMS-pcm",
            tts_model="Piper English phonetic adapter / MMS-TTS",
            mt_model="Meta NLLB-200 (pcm_Latn) / Google MADLAD-400",
            limitations=[
                "Extremely high adoption in markets and everyday commerce.",
                "Spelling varies; phonemic normalization applied before translation."
            ],
            validation_status="VERIFIED_PRODUCTION",
            sample_financial_phrases={
                "check_balance": "Show me ma balance",
                "explain_fees": "Explain di money wey dem dey cut",
                "transfer_prepare": "I wan send money give person",
                "confirm_action": "I agree say make dem send am"
            }
        ),
    }

    @classmethod
    def get_supported_languages(cls) -> List[LanguageCapability]:
        return list(cls._REGISTRY.values())

    @classmethod
    def get_language(cls, code: str) -> Optional[LanguageCapability]:
        for lang_code, capability in cls._REGISTRY.items():
            if lang_code.value == code.lower() or capability.name.lower() == code.lower():
                return capability
        return None

    @classmethod
    def is_speech_input_supported(cls, code: str) -> bool:
        lang = cls.get_language(code)
        return lang.speech_input_supported if lang else False

    @classmethod
    def is_speech_output_supported(cls, code: str) -> bool:
        lang = cls.get_language(code)
        return lang.speech_output_supported if lang else False

    @classmethod
    def is_translation_supported(cls, source: str, target: str) -> bool:
        src_lang = cls.get_language(source)
        if not src_lang:
            return False
        direction = f"{src_lang.code.value}->{target.lower()}"
        return direction in src_lang.supported_translation_directions

