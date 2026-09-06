"""
Feature Flags Configuration for API 5L Pipe QA/QC Suite.
Controls experimental and breaking features with safe defaults.
"""
import os
from typing import Dict, Any


def _get_bool(env_var: str, default: bool) -> bool:
    """Environment variable'dan boolean okur."""
    val = os.getenv(env_var, "").lower()
    if val in ("1", "true", "yes", "on", "enabled"):
        return True
    if val in ("0", "false", "no", "off", "disabled"):
        return False
    return default


class FeatureFlags:
    """
    Feature flags for experimental and breaking changes.
    All flags default to False for backward compatibility.
    Can be overridden via environment variables.
    """
    
    # Faz 1: Çekirdek Motor Düzeltmeleri
    ENABLE_COMPOSITE_MATCHING = _get_bool("ENABLE_COMPOSITE_MATCHING", False)
    """1-N ve N-1 eşleme (Composite Test Unbundling)"""
    
    ENABLE_CONTEXT_PARSER = _get_bool("ENABLE_CONTEXT_PARSER", False)
    """Context-aware criteria parser (mandrel vs crack ayırımı)"""
    
    # Faz 2: Doküman Türü ve Süreç İzolasyonu
    ENABLE_GATEKEEPER = _get_bool("ENABLE_GATEKEEPER", False)
    """Document type classification (ITP/Spec/Schedule)"""
    
    ENABLE_GATEKEEPER_INTERACTIVE = _get_bool("ENABLE_GATEKEEPER_INTERACTIVE", False)
    """Kullanıcı onayı bekle (True) vs sadece uyarı ver (False)"""
    
    ENABLE_DYNAMIC_MASTER = _get_bool("ENABLE_DYNAMIC_MASTER", False)
    """Süreç/PSL/Kapsam-a göre dinamik master spec"""
    
    # Faz 3: Meta Veri ve Frekans
    ENABLE_STRICT_FREQUENCY = _get_bool("ENABLE_STRICT_FREQUENCY", False)
    """NOT_SPECIFIED frekans modu (varsayılan frekans tuzağı kaldırılır)"""
    
    # Faz 4: Gelişmiş Özellikler
    ENABLE_TABLE_STITCHING = _get_bool("ENABLE_TABLE_STITCHING", False)
    """Multi-page table stitching"""
    
    ENABLE_COATING_ISOLATION = _get_bool("ENABLE_COATING_ISOLATION", False)
    """Tam kaplama/imalat izolasyonu"""
    
    # Geliştirici/Debug
    DEBUG_MODE = _get_bool("DEBUG_MODE", False)
    """Debug logging ve detaylı hata mesajları"""
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Tüm flag'lerin durumunu döndürür."""
        return {
            "ENABLE_COMPOSITE_MATCHING": cls.ENABLE_COMPOSITE_MATCHING,
            "ENABLE_CONTEXT_PARSER": cls.ENABLE_CONTEXT_PARSER,
            "ENABLE_GATEKEEPER": cls.ENABLE_GATEKEEPER,
            "ENABLE_GATEKEEPER_INTERACTIVE": cls.ENABLE_GATEKEEPER_INTERACTIVE,
            "ENABLE_DYNAMIC_MASTER": cls.ENABLE_DYNAMIC_MASTER,
            "ENABLE_STRICT_FREQUENCY": cls.ENABLE_STRICT_FREQUENCY,
            "ENABLE_TABLE_STITCHING": cls.ENABLE_TABLE_STITCHING,
            "ENABLE_COATING_ISOLATION": cls.ENABLE_COATING_ISOLATION,
            "DEBUG_MODE": cls.DEBUG_MODE,
        }
    
    @classmethod
    def is_any_enabled(cls) -> bool:
        """Herhangi bir deneysel özellik aktif mi?"""
        return any([
            cls.ENABLE_COMPOSITE_MATCHING,
            cls.ENABLE_CONTEXT_PARSER,
            cls.ENABLE_GATEKEEPER,
            cls.ENABLE_DYNAMIC_MASTER,
            cls.ENABLE_STRICT_FREQUENCY,
            cls.ENABLE_TABLE_STITCHING,
            cls.ENABLE_COATING_ISOLATION,
        ])
