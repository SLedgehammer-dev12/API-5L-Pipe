"""
Inspection & Test Plan (ITP) Automated Comparison & Audit Engine.

Audits uploaded/parsed manufacturer ITP documents against API 5L 47th Edition
(Tables 17, 18, 19, 20) and BOTAŞ specifications.

Detects:
    - Inadequate testing/sampling frequencies (🔴 Non-compliant)
    - Insufficient mechanical/chemical acceptance limits (🔴 Non-compliant)
    - Shorter hydrostatic holding times / low pressures (🔴 Non-compliant)
    - Missing mandatory standard tests (🔴 Critical Missing Test)
    - Tighter/superior quality commitments (🟡 More Stringent / Acceptable)
    - Conforming items (🟢 Compliant)
"""

import re
from typing import Any, Dict, List
from core.test_plan import get_comprehensive_itp_specification
from core.itp_criteria_parser import ITPCriteriaParser


class FrequencyCanonical:
    EVERY_PIPE_100 = "EVERY_PIPE_100"
    PER_HEAT = "PER_HEAT"
    PER_TEST_UNIT = "PER_TEST_UNIT"
    PER_COIL_ENDS = "PER_COIL_ENDS"
    PERIODIC_SHIFT = "PERIODIC_SHIFT"
    INADEQUATE_SAMPLING = "INADEQUATE_SAMPLING"
    UNKNOWN = "UNKNOWN"


class FrequencyNormalizer:
    """Normalizes raw unstructured frequency text into a canonical engineering classification."""

    @staticmethod
    def normalize(freq_text: str) -> str:
        t = (freq_text or "").lower().strip()
        if not t or t == "—":
            return FrequencyCanonical.UNKNOWN
        
        # Sparse sampling detection (e.g. 1/200 boru, 1 per 100, 50 boruda 1, 1/10)
        m_sparse = re.search(r'(?:1\s*/\s*(\d+)|1\s+per\s+(\d+)|(\d+)\s*boruda\s*1)', t)
        if m_sparse:
            denom = int(m_sparse.group(1) or m_sparse.group(2) or m_sparse.group(3))
            if denom >= 5:
                return FrequencyCanonical.INADEQUATE_SAMPLING

        if any(k in t for k in ("1 per 5", "1 per 10", "1/5", "1/10", "spot", "örneklem", "5%", "10%", "10 boruda 1", "5 boruda 1", "20 boruda 1", "sample 1 per shift")):
            return FrequencyCanonical.INADEQUATE_SAMPLING
        if any(k in t for k in ("her boru", "%100", "100%", "each pipe", "all pipes", "tüm borular", "istisnasız", "every pipe", "her kaynaklı boru")):
            return FrequencyCanonical.EVERY_PIPE_100
        if any(k in t for k in ("her döküm", "döküm başına", "dokum", "heat", "ısı başına", "isi basina", "pota", "per heat", "her dökümde")):
            return FrequencyCanonical.PER_HEAT
        if any(k in t for k in ("rulo", "bobin", "crop end", "coil")):
            return FrequencyCanonical.PER_COIL_ENDS
        if any(k in t for k in ("vardiya", "shift")):
            return FrequencyCanonical.PERIODIC_SHIFT
        if any(k in t for k in ("test ünitesi", "test unitesi", "lot", "unit", "ebat bazında")):
            return FrequencyCanonical.PER_TEST_UNIT
        return FrequencyCanonical.UNKNOWN


class ITPAuditEngine:
    """
    Automated ITP Audit and Discrepancy Evaluation Engine.
    Dynamically compares uploaded ITPs against API 5L 47th Ed. / BOTAŞ master requirements
    and 40+ computed pipe column parameters.
    """

    # Comprehensive bilingual (TR & EN) keyword mappings to match uploaded ITP test names to standard test keys
    TEST_MATCHER_KEYWORDS = {
        "chemical_heat": [
            "ısı analizi", "isi analizi", "döküm analizi", "dokum analizi", "pota analizi", "kimyasal bileşim",
            "kimyasal analiz", "spektrometre", "ladle chemical", "heat analysis", "ladle analysis", "cast analysis",
            "ladle heat", "chemical composition", "heat chemistry", "melt analysis", "ladle sample", "karbon eşdeğeri",
            "carbon equivalent", "ceiiw", "cepcm", "kimyasal bileşim kontrolü", "heat chemical analysis"
        ],
        "chemical_product": [
            "ürün analizi", "urun analizi", "ürün kimyasal", "product analysis", "check analysis", "product chemical",
            "product chemistry", "pipe chemistry", "body chemical analysis", "ürün kontrol analizi", "mamul analizi",
            "cross-product chemical", "pipe product analysis"
        ],
        "tensile_body": [
            "gövde çekme", "govde cekme", "pipe body tensile", "body tensile", "çekme testi", "cekme testi",
            "tensile test", "transverse tensile", "longitudinal tensile", "enine çekme", "boyuna çekme", "akma dayanımı",
            "akma mukavemeti", "yield strength", "proof stress", "rt0.5", "rp0.2", "uts", "ultimate tensile",
            "kopma uzaması", "elongation", "çekme deneyi", "strap specimen", "round bar tensile", "çekme - boru gövdesi",
            "tensile test on pipe body", "body mechanical tensile", "çekme dayanımı", "yield to tensile ratio"
        ],
        "tensile_weld": [
            "kaynak çekme", "kaynak cekme", "weld tensile", "weld seam tensile", "kaynak dikişi çekme", "all weld tensile",
            "transverse weld tensile", "cross weld tensile", "kaynak dikiş çekme", "kaynak metali çekme",
            "reduced section tensile", "kaynak çekme testi", "tensile test on weld seam"
        ],
        "cvn_body": [
            "gövde çentik", "gövde darbe", "govde centik", "govde darbe", "cvn body", "charpy body", "body impact",
            "çentik darbe", "charpy v-notch", "charpy impact", "absorbed energy", "darbe tokluğu", "yutulan enerji",
            "gövde tokluk", "transverse charpy", "body cvn", "impact test body", "çentik darbe - boru gövdesi",
            "çentik darbe testi (gövde)", "charpy v-notch on pipe body", "cvn impact test @ -20"
        ],
        "cvn_weld_haz": [
            "kaynak darbe", "itab darbe", "haz impact", "weld impact", "cvn weld", "charpy weld", "weld & haz",
            "weld and haz", "kaynak & itab", "kaynak ve itab", "fusion line impact", "erime hattı darbe", "weld metal cvn",
            "fl+2mm", "fl+5mm", "kaynak çentik darbe", "çentik darbe - kaynak ve itab", "çentik darbe testi (kaynak/haz)",
            "charpy v-notch on weld & haz", "heat affected zone impact", "weld center impact"
        ],
        "dwtt": [
            "dwtt", "drop weight", "yırtılma testi", "yirtilma testi", "düşen ağırlık", "dusen agirlik",
            "drop-weight tear test", "shear area", "liflilik oranı", "kırılma yüzeyi görünümü", "dwtt deneyi",
            "düşen ağırlık darbe", "drop weight tear testing", "fracture appearance transit"
        ],
        "guided_bend": [
            "kılavuzlu bükme", "kilavuzlu bukme", "guided bend", "guided-bend", "kök bükme", "kapak bükme", "yan bükme",
            "root bend", "face bend", "side bend", "transverse bend", "bend test", "mandrel", "bükme deneyi",
            "kılavuzlu bükme testi", "transverse guided bend test"
        ],
        "flattening": [
            "düzleştirme", "duzlestirme", "flattening", "yassıltma", "flattening test", "ring flattening", "ezme testi",
            "halka yassıltma", "yassıltma deneyi", "crush test", "hfw flattening"
        ],
        "hardness": [
            "sertlik", "hardness", "hv10", "hrc", "hbw", "vickers", "vickers hardness", "rockwell", "brinell",
            "sertlik taraması", "sertlik dağılımı", "traverse hardness", "weld hardness", "haz hardness",
            "kaynak sertlik", "sertlik testi", "vickers hardness test hv10", "microhardness survey"
        ],
        "residual_stress": [
            "artık stres", "artik stres", "artık gerilme", "residual stress", "halka kesme", "stres kontrolü",
            "ring test", "çevresel gerilme", "ring slit test", "halka kesme deneyi", "kalıntı gerilme",
            "residual stress measurement", "ring expansion test"
        ],
        "hydrostatic": [
            "hidrostatik", "hydrostatic", "su basınç", "su basinc", "basınç testi", "basinc testi", "hydro test",
            "mill hydro", "hydrostatic test", "sızdırmazlık", "leak tightness", "su basıncı",
            "fabrika hidrostatik basınç testi", "hydrostatic pressure test", "full body hydro test"
        ],
        "ndt_weld_seam": [
            "kaynak dikişi ndt", "kaynak ndt", "weld seam ndt", "weld ut", "weld rt", "radyografi", "ultrasonik kaynak",
            "ultrasonic weld", "weld inspection", "radiographic weld", "kaynak dikişi %100 ndt", "kaynak dikisi ndt",
            "paut", "phased array", "x-ray weld", "seam ut", "automated ultrasonic", "dikiş tahribatsız muayene",
            "full length seam ut", "weld radiographic inspection", "digital rt on weld"
        ],
        "ndt_pipe_body_lamination": [
            "gövde laminasyon", "gövdesi laminasyon", "body lamination", "gövde ut", "gövdesi ut", "sac laminasyon",
            "plaka laminasyon", "body laminar", "gövde laminas", "boru gövdesi ut laminasyon", "govde laminasyon",
            "full body ut", "mid-wall lamination", "gövde laminasyon kontrolü", "ultrasonic body lamination",
            "plate ultrasonic testing", "strip body ut"
        ],
        "ndt_pipe_ends": [
            "boru uçları ndt", "uç laminasyon", "pipe ends ndt", "laminar testing", "end ut", "ends ut",
            "boru uçları laminasyon", "uçları laminasyon", "uç laminar", "pipe ends laminar", "boru uclari laminasyon",
            "uclari laminasyon", "end zone ut", "pipe end scanning", "boru ucu laminasyon", "ultrasonic testing of pipe ends",
            "end face lamination inspection"
        ],
        "ndt_smls_body": [
            "dikişsiz gövde ndt", "smls body ndt", "flux leakage", "gövde ut", "seamless body", "dikissiz govde",
            "mfl", "magnetic flux leakage", "eddy current smls", "full length seamless body inspection"
        ],
        "ndt_bevel_mt": [
            "kaynak ağzı mt", "tamir mt", "manyetik parçacık", "magnetic particle", "mpi", "bevel mt",
            "kaynak agzi mt", "manyetik muayene", "tamir yüzeyi mt", "alın kaynak ağzı mt", "mt inspection",
            "magnetic particle inspection of bevel", "bevel end mpi"
        ],
        "weld_repair_rules": [
            "tamir kuralları", "tamir kaynağı", "onarım", "weld repair", "repair procedure", "tamir şartları",
            "kaynak tamiri", "repair conditions", "tamir kurallari", "tamir sarti", "repair limit",
            "tamir kaynağı kuralları", "procedure for weld repair", "repair cavity rules"
        ],
        "weld_geometry_offset_height": [
            "kaynak geometrisi", "kaynak dikiş yüksekliği", "kaynak yüksekliği", "weld height", "reinforcement",
            "weld reinforcement", "kaynak yuksekligi", "weld crown", "weld cap", "iç paso yüksekliği",
            "dış paso yüksekliği", "height of weld seam", "weld bead geometry", "reinforcement height"
        ],
        "weld_radial_offset": [
            "radyal kaçıklık", "radial offset", "basamaklanma", "sac kenarları kaçıklık", "offset of plate edges",
            "kenar kaçıklığı", "radyal kaciklik", "misalignment", "high-low", "sac basamaklanması",
            "radial offset of strip edges", "edge offset"
        ],
        "dimensional_peaking_offset": [
            "tepeleşme", "tepelesme", "peaking", "weld peaking", "çıkıntı", "boru ucu tepeleşme", "end peaking",
            "body peaking", "kaynak tepeleşmesi", "peaking at seam", "weld seam peaking"
        ],
        "dimensional_diameter_ends": [
            "boru ucu dış çap", "boru ucu çap", "uç çapı", "uç dış çap", "diameter ends", "pipe ends diameter",
            "dış çap - boru ucu", "cap toleransi - boru ucu", "dis cap boru ucu", "boru ucu çap toleransı",
            "boru ucu dış çap toleransı", "end od", "outside diameter ends", "diameter at ends",
            "pipe end diameter tolerance", "calliper end diameter"
        ],
        "dimensional_diameter_body": [
            "boru gövdesi dış çap", "gövde çapı", "gövde dış çap", "body diameter", "pipe body diameter",
            "dış çap - boru gövdesi", "cap toleransi - boru govdesi", "dis cap boru govdesi",
            "boru gövdesi çap toleransı", "gövde çap toleransı", "body od", "outside diameter body",
            "diameter along body", "pi tape body diameter", "body diameter tolerance"
        ],
        "dimensional_circumference_ends": [
            "boru ucu çevre", "çevre toleransı - boru ucu", "uç çevre", "circumference ends", "pipe ends circumference",
            "uc cevre", "boru ucu çevre toleransı", "boru çevre toleransı - boru ucu", "pi tape ends", "pi-mezura uç",
            "circumference at pipe ends"
        ],
        "dimensional_circumference_body": [
            "boru gövdesi çevre", "çevre toleransı - gövde", "çevre toleransı - boru gövdesi", "gövde çevre",
            "circumference body", "pipe body circumference", "govde cevre", "boru gövdesi çevre toleransı",
            "boru çevre toleransı - gövde", "pi tape body", "circumference along body"
        ],
        "dimensional_ovality_ends": [
            "boru ucu ovalite", "ovalite - boru ucu", "uç ovalite", "dairesellikten sapma - boru ucu",
            "yuvarlaklıktan sapma - boru ucu", "ovality ends", "ovality end", "pipe ends ovality",
            "out of roundness ends", "uc ovalite", "ovalite - uc", "ovalite ucu", "boru ucu ovalitesi",
            "boru ucu ovalite toleransı", "ovalite / yuvarlaklıktan sapma - boru ucu", "out-of-roundness ends",
            "end ovality", "out of roundness at pipe ends"
        ],
        "dimensional_ovality_body": [
            "boru gövdesi ovalite", "gövde ovalite", "ovalite - boru gövdesi", "ovalite - gövde",
            "dairesellikten sapma - gövde", "yuvarlaklıktan sapma - boru gövdesi", "ovality body",
            "pipe body ovality", "out of roundness body", "govde ovalite", "gövde ovalitesi",
            "boru gövdesi ovalite toleransı", "ovalite / yuvarlaklıktan sapma - boru gövdesi",
            "out-of-roundness body", "body ovality", "out of roundness along body"
        ],
        "dimensional_wall_thickness": [
            "et kalınlığı", "wall thickness", "cidar kalınlığı", "thickness verification",
            "et kalınlığı ölçümü", "et kalinligi", "et kal", "wt tolerance", "minimum wall thickness",
            "ultrasonic thickness", "et kalınlığı toleransı", "wall thickness tolerance", "nominal thickness check"
        ],
        "dimensional_weight": [
            "birim ağırlık", "boru ağırlığı", "weight per meter", "mass", "tartım", "kantar",
            "ağırlık toleransı", "pipe weight", "birim agirlik", "boru agirligi", "mass per unit length",
            "weighing of pipe", "pipe mass tolerance", "scale weighting"
        ],
        "dimensional_straightness": [
            "doğrusallık", "dogrusallik", "straightness", "doğrusallıktan sapma", "boru doğrusallığı",
            "straightness deviation", "toplam doğrusallık", "full length straightness", "end straightness",
            "düzlemsellik", "straightness verification", "string line measurement"
        ],
        "dimensional_bevel_ends": [
            "alın kaynak ağzı", "kaynak ağzı", "kaynak agzi", "bevel", "bevel angle", "ağız açısı",
            "kök yüzeyi", "root face", "kaynak ağzı geometrisi", "alın kaynak ağzı açısı", "end bevel",
            "weld preparation", "pah açısı", "bevel angle and root face", "pipe end preparation"
        ],
        "dimensional_squareness_ends": [
            "diklik", "diklikten sapma", "squareness", "pipe end squareness", "uç diklik", "boru ucu diklik",
            "end squareness", "out-of-squareness", "gönye kaçıklığı", "squareness of pipe ends"
        ],
        "erw_metallographic_seam": [
            "metalografik", "metalografi", "martenzit", "mikro yapı", "tavlama", "normalizasyon sıcaklığı",
            "kaynak tavlama", "metallographic", "microstructure", "tavlama sıcaklığı", "seam heat treatment",
            "seam normalization", "hfw seam metallography", "mikro yapı incelemesi", "metallographic examination of seam"
        ],
        "erw_flash_trim_weld": [
            "çapak", "iç ve dış çapak", "çapak alma", "kaynak çapağı", "flash trim", "oyuk derinliği",
            "iç çapak", "dış çapak", "flash removal", "capak alma", "iç çapak alma", "dış çapak alma",
            "weld flash removal", "internal flash trim", "external flash trim", "height of remaining flash"
        ],
        "coating_surface_prep_blasting": [
            "kumlama", "yüzey hazırlığı", "yüzey temizliği", "surface preparation", "blasting", "sa 2.5",
            "yüzey profili", "rz", "toz testi", "tuz testi", "çiğ noktası", "kumlama öncesi", "kumlama sonrası",
            "boru yüzeyi kumlama", "boru yüzey kalitesi", "grit blasting", "shot blasting", "anchor profile",
            "surface cleanliness", "blast cleaning to sa 2.5", "surface profile rz"
        ],
        "coating_thickness_3lpe": [
            "kaplama kalınlığı", "3lpe kalınlık", "hdpe kalınlık", "fbe kalınlığı", "yapıştırıcı kalınlığı",
            "pe kaplama", "coating thickness", "3lpe", "3l hdpe", "3000 mikron", "3 mm", "fbe kaplama",
            "yapışkan tabaka", "3lpe – muayene", "kaplama kalınlık", "total coating thickness",
            "polyethylene thickness", "toplam kaplama kalınlığı", "3-layer pe coating thickness"
        ],
        "coating_holiday_test": [
            "holiday", "elektrik testi", "porozite", "holiday dedektör", "kıvılcım", "25 kv", "25000 volt",
            "spark test", "pinhole", "elektrik (holiday) testi", "porozite kontrolü", "holiday detection",
            "high voltage spark test", "spark testing", "delik kontrolü", "holiday detector testing"
        ],
        "coating_peel_adhesion": [
            "soyulma", "yapışma", "peel adhesion", "peel strength", "150 n/cm", "18 n/mm", "soyulma testi",
            "pe kaplama testleri", "soyulma mukavemeti", "yapışma testi", "adhesion test", "peel resistance",
            "yapışma dayanımı", "peel strength test at 23°c", "coating peel adhesion"
        ],
        "coating_impact_resistance": [
            "darbe direnci", "kaplama darbe", "impact resistance", "5 j/mm", "darbe testi kaplama",
            "darbe testi", "falling weight impact", "drop weight coating impact", "darbe dayanımı",
            "impact strength of coating"
        ],
        "coating_indentation": [
            "delici uca direnç", "indentation", "batma direnci", "penetrasyon", "delici uç", "indentation test",
            "delici uca direnç testi", "batma", "penetration resistance", "delici uç batma", "indentation resistance test"
        ],
        "coating_cathodic_disbondment": [
            "katodik", "cd test", "cathodic disbondment", "katodik test", "cd testi", "katodik soyulma testi",
            "disbondment", "katodik soyulma", "28 days cd", "cathodic delamination", "cathodic disbondment 28 days"
        ],
        "coating_cutback_bevel": [
            "cutback", "cut-back", "kaplamasız bölge", "boru ucu geri kesme", "pah açısı kaplama", "pe açısı",
            "cutback mesafesi", "koruyucu tapa", "vernik", "kaplamasız bölge (cut back) hazırlığı",
            "boru ucu koruma", "cutback length", "chamfer angle", "end cutback", "cutback preparation"
        ],
        "coating_repair_rules": [
            "kaplama tamiri", "kaplama kusur tamiri", "kusur tamir", "tamir metodu", "heatshrink",
            "yama malzemesi", "kaplama onarım", "coating repair", "pe tamiri", "tamir metodu ve kontrolü",
            "tamir", "repair of coating", "melt stick repair", "patch repair", "coating defect repair"
        ],
        "personnel_qualification_ndt": [
            "personel yetkinliği", "ndt personeli", "seviye 3", "level 3", "level 2", "en iso 9712",
            "en iso 11484", "personel kalifikasyon", "ndt operatörleri", "ndt personnel qualification",
            "operator certification", "asnt level ii", "iso 9712 level 2"
        ],
        "visual_surface": [
            "görsel muayene", "yüzey muayenesi", "visual inspection", "surface inspection", "gözle muayene",
            "görsel yüzey", "gorsel", "yuzey muayenesi", "görsel kontrol", "visual examination",
            "surface imperfections", "gözle kontrol", "pipe visual inspection"
        ],
        "residual_magnetism": [
            "kalıntı manyetizma", "manyetizma", "residual magnetism", "gaussmetre", "gauss", "kalinti manyetizma",
            "kalıcı manyetiklik", "remanent magnetism", "magnetic field strength", "gauss level", "hall effect measurement"
        ],
        "quality_marking_surface_prep": [
            "proje markalaması", "markalama", "stenciling", "şablonlama", "yüzey hazırlığı", "surface prep",
            "en 10204", "mtc", "kalite sertifikası", "3.1 sertifika", "3.2 sertifika", "marking",
            "sablonlama", "sertifikalandırma", "pipe marking", "die stamping", "inspection certificate 3.1"
        ],
    }

    @classmethod
    def audit_itp(
        cls,
        uploaded_items: List[Dict[str, Any]],
        pipe_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audits a list of uploaded ITP items against official API 5L 47th Ed. / BOTAŞ master requirements
        and exact calculated pipe parameters using Maximum-Weight Bipartite Assignment.
        """
        master_spec = get_comprehensive_itp_specification(pipe_config)
        audit_rows: List[Dict[str, Any]] = []
        findings: List[Dict[str, Any]] = []

        process = str(pipe_config.get("manufacturing_process") or "SAWH").upper()
        is_smls = any(k in process for k in ("SMLS", "SEAMLESS", "DIKISSIZ"))

        # --- 1. Compute Scored Bipartite Match Matrix (A2 Solution) ---
        candidates = []
        for m_idx, master_item in enumerate(master_spec):
            test_key = master_item["test_key"]
            keywords = cls.TEST_MATCHER_KEYWORDS.get(test_key, [])

            for u_idx, up_item in enumerate(uploaded_items):
                up_name = str(up_item.get("test_name") or "").lower()
                up_crit = str(up_item.get("acceptance_criteria") or "").lower()
                up_std = str(up_item.get("test_standard") or "").lower()
                full_up_text = f"{up_name} {up_crit} {up_std}"

                score = 0
                for kw in keywords:
                    if kw in up_name:
                        score = max(score, 60 + len(kw) * 3)
                    elif kw in full_up_text:
                        score = max(score, 30 + len(kw) * 2)

                # Contextual & Specificity Reinforcement (Bilingual TR & EN)
                if test_key == "tensile_body" and any(k in full_up_text for k in ("gövde", "govde", "body", "pipe body", "transverse", "longitudinal", "base metal")):
                    score += 40
                elif test_key == "tensile_weld" and any(k in full_up_text for k in ("kaynak", "weld", "seam", "dikiş", "cross weld")):
                    score += 45
                elif test_key == "cvn_body" and any(k in full_up_text for k in ("gövde", "govde", "body", "pipe body", "base metal", "charpy body")):
                    score += 40
                elif test_key == "cvn_weld_haz" and any(k in full_up_text for k in ("kaynak", "weld", "itab", "haz", "fusion line", "fl+2", "fl+5")):
                    score += 45
                elif test_key == "dwtt" and any(k in full_up_text for k in ("dwtt", "drop weight", "shear", "liflilik", "tear test")):
                    score += 55
                elif test_key == "dimensional_diameter_ends" and any(k in full_up_text for k in ("uç", "uclari", "ends", "pipe end", "both ends", "pipe ends")):
                    score += 60
                elif test_key == "dimensional_diameter_body" and any(k in full_up_text for k in ("gövde", "govde", "body", "pipe body")):
                    score += 60
                elif test_key == "dimensional_ovality_ends" and any(k in full_up_text for k in ("uç", "uclari", "ends", "pipe end", "both ends", "pipe ends")):
                    score += 60
                elif test_key == "dimensional_ovality_body" and any(k in full_up_text for k in ("gövde", "govde", "body", "pipe body")):
                    score += 60
                elif test_key == "ndt_pipe_ends" and any(k in full_up_text for k in ("uç", "uclari", "ends", "pipe end", "end zone", "end face")):
                    score += 45
                elif test_key == "ndt_pipe_body_lamination" and any(k in full_up_text for k in ("40%", "gövde laminas", "sac laminas", "12094", "body lamin", "plate lamination", "full body ut")):
                    score += 45
                elif test_key == "ndt_weld_seam" and any(k in full_up_text for k in ("dikiş", "seam", "10893-11", "10893-6", "aut", "kaynak dikiş", "weld ut", "weld rt", "paut")):
                    score += 50
                elif test_key == "ndt_smls_body" and is_smls and any(k in full_up_text for k in ("dikişsiz", "smls", "10893-10", "flux", "seamless")):
                    score += 60
                elif test_key == "ndt_bevel_mt" and any(k in full_up_text for k in ("kaynak ağzı mt", "bevel mt", "bevel mpi", "magnetic particle", "mpi")):
                    score += 50
                elif test_key == "weld_repair_rules" and any(k in full_up_text for k in ("tamir", "repair", "re-repair", "ön ısıtma", "preheat", "repair procedure")):
                    score += 50
                elif test_key == "dimensional_weight" and any(k in full_up_text for k in ("ağırlık", "weight", "kg/m", "kantar", "mass", "tartım", "weighing")):
                    score += 50
                elif test_key == "guided_bend" and any(k in full_up_text for k in ("mandrel", "bükme", "bend", "çene", "5173", "guided-bend", "root bend", "face bend")):
                    score += 50
                elif test_key == "flattening" and any(k in full_up_text for k in ("flattening", "yassıltma", "düzleştirme", "crush", "ring flattening")):
                    score += 50
                elif test_key == "hardness" and any(k in full_up_text for k in ("hardness", "sertlik", "hv10", "hrc", "vickers", "microhardness")):
                    score += 50
                elif test_key == "hydrostatic" and any(k in full_up_text for k in ("hydrostatic", "hydro", "hidrostatik", "bar", "psi", "smys", "holding time")):
                    score += 50
                elif test_key == "weld_geometry_offset_height" and any(k in full_up_text for k in ("yükseklik", "kaçıklık", "offset", "peaking", "tepeleşme", "misalignment", "weld crown", "weld height")):
                    score += 50
                elif test_key == "quality_marking_surface_prep" and any(k in full_up_text for k in ("markalama", "sa 2.5", "stenciling", "şablon", "3.1", "3.2", "mtc", "marking", "die stamp")):
                    score += 50
                elif test_key == "residual_stress" and any(k in full_up_text for k in ("artık stres", "residual stress", "halka kesme", "ring test", "slit ring")):
                    score += 55
                elif test_key == "coating_holiday_test" and any(k in full_up_text for k in ("holiday", "porozite", "25 kv", "gerilim", "spark", "high voltage", "pinhole")):
                    score += 55
                elif test_key == "coating_thickness_3lpe" and any(k in full_up_text for k in ("3lpe", "hdpe", "fbe", "kaplama kalın", "yapıştırıcı", "coating thickness", "polyethylene")):
                    score += 55
                elif test_key == "coating_peel_adhesion" and any(k in full_up_text for k in ("soyulma", "yapışma", "peel", "adhesion", "n/cm", "n/mm", "peel strength")):
                    score += 55
                elif test_key == "coating_cathodic_disbondment" and any(k in full_up_text for k in ("katodik", "cd test", "disbond", "cathodic", "28 days")):
                    score += 55
                elif test_key == "coating_indentation" and any(k in full_up_text for k in ("indentation", "delici", "batma", "penetration")):
                    score += 55
                elif test_key == "coating_surface_prep_blasting" and any(k in full_up_text for k in ("kumlama", "blasting", "sa 2.5", "yüzey hazırl", "grit blast", "anchor profile", "rz")):
                    score += 55
                elif test_key == "coating_cutback_bevel" and any(k in full_up_text for k in ("cutback", "cut-back", "chamfer", "kaplamasız", "vernik", "protective cap")):
                    score += 55
                elif test_key == "coating_repair_rules" and any(k in full_up_text for k in ("coating repair", "melt stick", "heatshrink", "kaplama tamir", "patch repair")):
                    score += 55
                elif test_key == "erw_flash_trim_weld" and any(k in full_up_text for k in ("çapak", "flash", "trim", "oyuk", "flash removal")):
                    score += 55
                elif test_key == "erw_metallographic_seam" and any(k in full_up_text for k in ("metalograf", "martenzit", "tavlama", "metallographic", "microstructure", "normalization")):
                    score += 55

                # Disambiguation and Anti-affinity penalties
                if test_key in ("tensile_body", "tensile_weld") and any(k in up_name for k in ("charpy", "cvn", "darbe", "çentik", "impact", "joule", "v-notch", "dwtt")):
                    score = 0
                elif test_key in ("cvn_body", "cvn_weld_haz", "dwtt") and any(k in up_name for k in ("tensile", "çekme", "cekme", "akma", "yield", "kopma uzama")) and not any(k in up_name for k in ("charpy", "cvn", "darbe", "çentik", "impact", "dwtt")):
                    score = 0
                elif test_key in ("dimensional_diameter_ends", "dimensional_diameter_body") and any(k in up_name for k in ("ovality", "ovalite", "roundness", "yuvarlaklık", "dairesellik")):
                    score = 0
                elif test_key in ("dimensional_ovality_ends", "dimensional_ovality_body") and any(k in up_name for k in ("outside diameter", "dış çap", "dis cap", "diameter tolerance")) and not any(k in up_name for k in ("ovality", "ovalite", "roundness", "yuvarlaklık", "dairesellik")):
                    score = 0

                if not is_smls and test_key == "ndt_smls_body":
                    score = 0
                if is_smls and "weld" in test_key and test_key not in ("ndt_pipe_ends", "visual_surface"):
                    score = 0

                if score >= 30:
                    candidates.append((score, m_idx, u_idx))

        # Maximum Weight Greedy Bipartite Assignment
        candidates.sort(key=lambda x: x[0], reverse=True)
        matched_master = set()
        matched_uploaded = set()
        master_to_uploaded: Dict[int, int] = {}

        for score, m_idx, u_idx in candidates:
            if m_idx not in matched_master and u_idx not in matched_uploaded:
                matched_master.add(m_idx)
                matched_uploaded.add(u_idx)
                master_to_uploaded[m_idx] = u_idx

        # --- 2. Evaluate Assigned Master Items ---
        for m_idx, master_item in enumerate(master_spec):
            test_key = master_item["test_key"]

            if m_idx in master_to_uploaded:
                u_idx = master_to_uploaded[m_idx]
                matched_uploaded_item = uploaded_items[u_idx]
                row_eval = cls._evaluate_matched_row(master_item, matched_uploaded_item, pipe_config)
                audit_rows.append(row_eval)
                if row_eval["status"] != "COMPLIANT":
                    findings.append({
                        "test_name": master_item["test_name"],
                        "severity": "CRITICAL" if row_eval["status"] == "NON_COMPLIANT" else "INFO",
                        "issue_type": row_eval["issue_type"],
                        "message": row_eval["audit_remarks"],
                        "clause_ref": master_item["clause_ref"],
                        "table_ref": master_item["table_ref"]
                    })
            else:
                # Missing or Not Detected from uploaded ITP
                is_scanned_or_sparse = len(uploaded_items) < 15
                issue_code = "MISSING_MANDATORY_TEST"
                remark_text = (
                    f"🔴 ZORUNLU TEST EKSİK VEYA DOKÜMANDA ALGILANAMADI: {master_item['clause_ref']} kapsamındaki bu test imalatçı ITP'sinde yer almamakta veya otomatik tespit edilememiştir; lütfen manuel doğrulayınız."
                    if is_scanned_or_sparse else
                    f"🔴 ZORUNLU TEST EKSİK: {master_item['clause_ref']} uyarınca zorunlu olan bu test imalatçı ITP'sinde bulunmamaktadır!"
                )

                if master_item["is_mandatory"]:
                    row_eval = {
                        "test_key": test_key,
                        "category": master_item["category"],
                        "test_name": master_item["test_name"],
                        "calculated_target": master_item.get("calculated_target_str", "—"),
                        "ndt_method_standard": master_item.get("ndt_method_standard", "—"),
                        "ndt_acceptance_level": master_item.get("ndt_acceptance_level", "—"),
                        "uploaded_frequency": "— (Dokümanda Tespit Edilemedi)" if is_scanned_or_sparse else "— (ITP'de Bulunamadı / Eksik)",
                        "standard_frequency": master_item["standard_frequency"],
                        "uploaded_criteria": "—",
                        "standard_criteria": master_item["standard_acceptance_criteria"],
                        "status": "NON_COMPLIANT",
                        "issue_type": issue_code,
                        "audit_remarks": remark_text,
                        "clause_ref": master_item["clause_ref"],
                        "table_ref": master_item["table_ref"],
                        "is_coating": master_item.get("is_coating", False),
                        "reading_confidence": "NOT_DETECTED",
                        "inspection_points": {"mfg": "—", "tpi": "—", "client": "—"}
                    }
                    audit_rows.append(row_eval)
                    findings.append({
                        "test_name": master_item["test_name"],
                        "severity": "WARNING" if is_scanned_or_sparse else "CRITICAL",
                        "issue_type": issue_code,
                        "message": row_eval["audit_remarks"],
                        "clause_ref": master_item["clause_ref"],
                        "table_ref": master_item["table_ref"]
                    })
                else:
                    audit_rows.append({
                        "test_key": test_key,
                        "category": master_item["category"],
                        "test_name": master_item["test_name"],
                        "calculated_target": master_item.get("calculated_target_str", "—"),
                        "ndt_method_standard": master_item.get("ndt_method_standard", "—"),
                        "ndt_acceptance_level": master_item.get("ndt_acceptance_level", "—"),
                        "uploaded_frequency": "— (İsteğe Bağlı)",
                        "standard_frequency": master_item["standard_frequency"],
                        "uploaded_criteria": "—",
                        "standard_criteria": master_item["standard_acceptance_criteria"],
                        "status": "COMPLIANT",
                        "issue_type": "OPTIONAL_NOT_SPECIFIED",
                        "audit_remarks": "🟢 İsteğe bağlı standart maddesi; ITP'de yer almaması uygundur.",
                        "clause_ref": master_item["clause_ref"],
                        "table_ref": master_item["table_ref"],
                        "is_coating": master_item.get("is_coating", False),
                        "reading_confidence": "NOT_DETECTED",
                        "inspection_points": {"mfg": "—", "tpi": "—", "client": "—"}
                    })

        # Process any extra unmapped items in uploaded ITP
        for u_idx, up_item in enumerate(uploaded_items):
            if u_idx not in matched_uploaded:
                audit_rows.append({
                    "test_key": f"custom_{u_idx}",
                    "category": "Ek / Özel Muayene",
                    "test_name": up_item.get("test_name", "Özel Muayene"),
                    "calculated_target": "İmalatçı & Müşteri Anlaşmasına Bağlı",
                    "ndt_method_standard": up_item.get("test_standard", "Özel Test Metodu"),
                    "ndt_acceptance_level": up_item.get("acceptance_criteria", "Özel Kabul Kriteri"),
                    "uploaded_frequency": up_item.get("test_frequency", "—"),
                    "standard_frequency": "Standart Dışı / İmalatçı Özel Testi",
                    "uploaded_criteria": up_item.get("acceptance_criteria", "—"),
                    "standard_criteria": "İmalatçı & Müşteri Anlaşmasına Bağlı",
                    "status": "MORE_STRINGENT",
                    "issue_type": "ADDITIONAL_TEST",
                    "audit_remarks": "🟡 Standart haricinde ek kalite kontrol testi taahhüt edilmiştir.",
                    "clause_ref": "Ek Müşteri Şartı",
                    "table_ref": "—",
                    "is_coating": "kaplama" in str(up_item.get("test_name", "")).lower() or "coating" in str(up_item.get("test_name", "")).lower(),
                    "reading_confidence": up_item.get("reading_confidence", "HIGH"),
                    "inspection_points": up_item.get("inspection_points", {"mfg": "C", "tpi": "W", "client": "W"})
                })

        # Calculate Statistics & Hybrid Dual Compliance Score (Bare Pipe vs Coating)
        bare_rows = [r for r in audit_rows if not r.get("is_coating", False)]
        coat_rows = [r for r in audit_rows if r.get("is_coating", False)]

        # Bare pipe score
        bare_total = len(bare_rows)
        bare_more_str = sum(1 for r in bare_rows if r["status"] == "MORE_STRINGENT")
        bare_comp = sum(1 for r in bare_rows if r["status"] == "COMPLIANT")
        bare_score = max(0.0, round(((bare_comp + bare_more_str) / bare_total) * 100.0, 1)) if bare_total > 0 else None

        # Coating score
        coat_total = len(coat_rows)
        coat_more_str = sum(1 for r in coat_rows if r["status"] == "MORE_STRINGENT")
        coat_comp = sum(1 for r in coat_rows if r["status"] == "COMPLIANT")
        coat_score = max(0.0, round(((coat_comp + coat_more_str) / coat_total) * 100.0, 1)) if coat_total > 0 else None

        total_rows = len(audit_rows)
        non_compliant_count = sum(1 for r in audit_rows if r["status"] == "NON_COMPLIANT")
        more_stringent_count = sum(1 for r in audit_rows if r["status"] == "MORE_STRINGENT")
        compliant_count = sum(1 for r in audit_rows if r["status"] == "COMPLIANT")

        if bare_score is not None and coat_score is not None:
            compliance_score = round((0.70 * bare_score) + (0.30 * coat_score), 1)
        elif bare_score is not None:
            compliance_score = bare_score
        elif coat_score is not None:
            compliance_score = coat_score
        else:
            compliance_score = 100.0

        if non_compliant_count > 0:
            overall_verdict = "REJECTED"
        elif more_stringent_count > 0:
            overall_verdict = "APPROVED_WITH_COMMENTS"
        else:
            overall_verdict = "APPROVED"

        std_ed = "API Spec 5L 46. Baskı" if "46" in str(pipe_config.get("standard_edition", "")).lower() else "API Spec 5L 47. Baskı"
        if "BOTAŞ" in str(pipe_config.get("standard_type", "")).upper():
            std_ed += " & BOTAŞ 5120 R7 / 5410 R1"

        return {
            "pipe_summary": {
                "diameter_mm": pipe_config.get("diameter_mm", 1219.0),
                "diameter_inch": pipe_config.get("diameter_inch", '48"'),
                "wall_thickness_mm": pipe_config.get("wall_thickness_mm", 14.30),
                "material_grade": pipe_config.get("material_grade", "X65"),
                "manufacturing_process": pipe_config.get("manufacturing_process", "SAWH"),
                "psl_level": pipe_config.get("psl_level", "PSL2"),
                "standard_edition": std_ed
            },
            "kpi": {
                "total_tests_audited": total_rows,
                "compliant_count": compliant_count,
                "more_stringent_count": more_stringent_count,
                "non_compliant_count": non_compliant_count,
                "compliance_score_percent": compliance_score,
                "bare_pipe_score_percent": bare_score,
                "coating_score_percent": coat_score,
                "overall_verdict": overall_verdict
            },
            "findings_count": len(findings),
            "findings": findings,
            "audit_rows": audit_rows
        }

    @classmethod
    def _evaluate_matched_row(
        cls,
        master: Dict[str, Any],
        uploaded: Dict[str, Any],
        pipe_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates a single matched ITP test row against dynamic calculations, NDT standards,
        and full dimensional/chemical/mechanical rules (A3 & A4 Solution).
        """
        test_key = master["test_key"]
        up_name = str(uploaded.get("test_name") or "").strip()
        up_freq = str(uploaded.get("test_frequency") or "").strip()
        up_crit = str(uploaded.get("acceptance_criteria") or "").strip()
        up_std = str(uploaded.get("test_standard") or "").strip()
        std_freq = master["standard_frequency"]
        std_crit = master["standard_acceptance_criteria"]
        calc_targets = master.get("calculated_targets", {})

        status = "COMPLIANT"
        issue_type = "CONFORMING"
        remarks: List[str] = []

        d_mm = float(pipe_config.get("diameter_mm") or 1219.0)
        t_mm = float(pipe_config.get("wall_thickness_mm") or 14.30)
        process = str(pipe_config.get("manufacturing_process") or "SAWH").upper()
        is_welded = any(k in process for k in ("SAW", "ERW", "HFW", "LSAW", "COW"))
        std_type = str(pipe_config.get("standard_type") or pipe_config.get("standard_code") or "").upper()
        is_botas = "BOTAŞ" in std_type or "BOTAS" in std_type

        up_name_lower = up_name.lower()
        up_freq_lower = up_freq.lower()
        up_crit_lower = up_crit.lower()
        up_std_lower = up_std.lower()
        full_up_text = f"{up_name_lower} {up_crit_lower} {up_std_lower}"

        # --- 1. Comprehensive Canonical Frequency Evaluation (R4 Solution) ---
        canon_freq = FrequencyNormalizer.normalize(up_freq)

        if canon_freq == FrequencyCanonical.INADEQUATE_SAMPLING:
            status = "NON_COMPLIANT"
            issue_type = "INADEQUATE_SAMPLING_FREQUENCY"
            remarks.append(f"🔴 NUMUNE FREKANSI YETERSİZ (SEYREK FREKANS): API 5L / BOTAŞ şartnamesi uyarınca test ünitesi veya döküm frekansı aşılmıştır; '{up_freq}' kabul edilemez.")
        elif test_key in ("hydrostatic", "ndt_weld_seam", "visual_surface", "dimensional_wall_thickness",
                        "dimensional_diameter_ends", "dimensional_diameter_body",
                        "dimensional_circumference_ends", "dimensional_circumference_body",
                        "dimensional_ovality_ends", "dimensional_ovality_body",
                        "dimensional_straightness", "dimensional_bevel_ends",
                        "dimensional_squareness_ends", "dimensional_peaking_offset",
                        "weld_radial_offset", "weld_geometry_offset_height",
                        "coating_holiday_test", "coating_thickness_3lpe",
                        "coating_surface_prep_blasting", "coating_cutback_bevel",
                        "erw_flash_trim_weld",
                        "dimensional_length_straightness_bevel", "ndt_pipe_ends", "ndt_bevel_mt",
                        "quality_marking_surface_prep", "dimensional_diameter_ovality", "dimensional_weight"):
            if canon_freq in (FrequencyCanonical.PER_TEST_UNIT, FrequencyCanonical.PERIODIC_SHIFT):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append(f"🔴 FREKANS YETERSİZ: Standart gereği bu test İSTİSNASIZ HER BORUDA (%100) yapılmalıdır; '{up_freq}' kabul edilemez.")
        elif test_key == "chemical_product":
            if not is_botas and ("1 analiz" in up_freq_lower or "1 adet" in up_freq_lower or "1 per" in up_freq_lower):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: Ürün analizi ısı başına en az 2 adet (ayrı borulardan) yapılmalıdır (API 5L 9.2).")
        elif test_key == "chemical_heat":
            if any(k in up_freq_lower for k in ("1 per 5", "1 per 10", "1/5", "1/10")):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: Döküm analizi istisnasız her dökümde (per heat) yapılmalıdır!")
        elif test_key == "residual_stress":
            if is_botas and canon_freq != FrequencyCanonical.PER_HEAT and any(k in up_freq_lower for k in ("lot", "örneklem", "sample", "test ünitesi")):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: BOTAŞ Şartnamesi Madde 3.3.9 uyarınca artık stres testi HER DÖKÜMDE (HEAT) zorunludur.")

        # --- 2. Comprehensive Criteria & Numeric Evaluations ---

        # --- 2. Comprehensive Criteria & Numeric Evaluations (via ITPCriteriaParser) ---

        # 2a. CVN Body Impact
        if test_key == "cvn_body":
            parsed_cvn = ITPCriteriaParser.parse_cvn_criteria(f"{up_crit_lower} {up_name.lower()}")
            req_avg = float(calc_targets.get("avg_j", 48.0 if (is_botas and "X52" in str(pipe_config.get("material_grade", ""))) else (60.0 if is_botas else 41.0)))
            if parsed_cvn["energy_avg_j"] is not None:
                val = parsed_cvn["energy_avg_j"]
                if val < req_avg:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DARBE ENERJİSİ (GÖVDE): Asgari ortalama darbe enerjisi {req_avg:.0f} J olmalıdır; ITP'de {val:.0f} J yazılmıştır!")
                elif val > req_avg + 5.0:
                    status = "MORE_STRINGENT"
                    issue_type = "MORE_STRINGENT"
                    remarks.append(f"🟡 DAHA SIKI DARBE ENERJİSİ: İmalatçı {val:.0f} J taahhüt etmiştir (Hesaplanan: {req_avg:.0f} J).")
            if is_botas and (("0 °c" in full_up_text or "0°c" in full_up_text) and "-20" not in full_up_text):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 HATALI TEST SICAKLIĞI: BOTAŞ Madde 3.3.5 uyarınca gövde darbe deneyi -20 °C'de yapılmalıdır; ITP'de 0 °C belirtilmiştir!")

        # 2b. CVN Weld & HAZ Impact
        elif test_key == "cvn_weld_haz":
            parsed_cvn = ITPCriteriaParser.parse_cvn_criteria(f"{up_crit_lower} {up_name.lower()}")
            req_avg = float(calc_targets.get("avg_j", 36.0 if (is_botas and "X52" in str(pipe_config.get("material_grade", ""))) else (45.0 if is_botas else 27.0)))
            if parsed_cvn["energy_avg_j"] is not None:
                val = parsed_cvn["energy_avg_j"]
                if val < req_avg:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DARBE ENERJİSİ (KAYNAK/ITAB): Asgari ortalama {req_avg:.0f} J olmalıdır; ITP'de {val:.0f} J yazılmıştır!")
            if is_botas and (("0 °c" in full_up_text or "0°c" in full_up_text) and "-20" not in full_up_text):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 HATALI TEST SICAKLIĞI: BOTAŞ Madde 3.3.5 uyarınca Kaynak & ITAB darbe deneyi -20 °C'de yapılmalıdır!")

        # 2c. DWTT (Drop Weight Tear Test)
        elif test_key == "dwtt":
            parsed_cvn = ITPCriteriaParser.parse_cvn_criteria(f"{up_crit_lower} {up_name.lower()}")
            if parsed_cvn["shear_area_percent"] is not None:
                val_shear = parsed_cvn["shear_area_percent"]
                if val_shear < 85:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DWTT SÜNEK KIRILMA: Ortalama sünek kırılma alanı min %85 olmalıdır; ITP'de %{val_shear:.0f} yazılmıştır!")
            if is_botas and any(k in up_crit_lower for k in ("< 60", "<%60", "tekil < 60")):
                pass  # Compliant individual rule
            elif is_botas and any(k in up_crit_lower for k in ("50%", "tekil 50", "40%")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 DWTT MÜNFERİT LİMİTİ: BOTAŞ Madde 3.3.6 uyarınca hiçbir tekil numune <%60 olamaz!")

        # 2d. Tensile Body & Weld
        elif test_key == "tensile_body":
            parsed_tensile = ITPCriteriaParser.parse_tensile_criteria(f"{up_crit_lower} {up_name.lower()}")
            # Yield Rt0.5
            req_rt = float(calc_targets.get("yield_min_mpa", 450.0))
            if parsed_tensile["yield_min"] is not None:
                val_rt = parsed_tensile["yield_min"]
                if val_rt < req_rt - 0.5:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 DÜŞÜK AKMA MUKAVEMETİ: Asgari Rt0.5={req_rt:.1f} MPa olmalıdır; ITP'de {val_rt:.1f} MPa belirtilmiş!")

            # Elongation Af
            req_af = float(calc_targets.get("elongation_min_pct", 19.5))
            if parsed_tensile["elongation_min"] is not None:
                val_af = parsed_tensile["elongation_min"]
                if val_af < (req_af - 0.2):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ KOPMA UZAMASI: Boru et kalınlığına göre asgari uzama %{req_af:.1f} iken ITP'de %{val_af:.1f} belirtilmiş!")

            # Y/T Ratio
            req_yt = float(calc_targets.get("yt_ratio_max", 0.90 if is_botas else 0.93))
            if parsed_tensile["ratio_max"] is not None:
                val_yt = parsed_tensile["ratio_max"]
                if val_yt > (req_yt + 0.005):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK Y/T ORANI: Azami Y/T={req_yt:.2f} olmalıdır; ITP'de {val_yt:.2f} yazılmıştır!")

        elif test_key == "tensile_weld":
            parsed_tensile = ITPCriteriaParser.parse_tensile_criteria(f"{up_crit_lower} {up_name.lower()}")
            req_rm = float(calc_targets.get("tensile_min_mpa", 535.0))
            if parsed_tensile["tensile_min"] is not None:
                val_rm = parsed_tensile["tensile_min"]
                if val_rm < req_rm - 0.5:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ KAYNAK ÇEKME MUKAVEMETİ: Asgari Rm={req_rm:.1f} MPa olmalıdır; ITP'de {val_rm:.1f} MPa belirtilmiş!")

        # 2e. Chemical Composition (C, P, S, N, CE)
        elif test_key in ("chemical_heat", "chemical_product"):
            c_matches = re.findall(r"c\s*[≤<=:]*\s*0\.(\d+)", up_crit_lower)
            max_c = float(calc_targets.get("C_max", 0.12 if is_botas else 0.16))
            if c_matches:
                val_c = float("0." + c_matches[0])
                if val_c > (max_c + 0.005):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK KARBON LİMİTİ: C max %{max_c:.2f} olmalıdır; ITP'de %{val_c:.2f} yazılmıştır!")

            p_matches = re.findall(r"p\s*[≤<=:]*\s*0\.0(\d+)", up_crit_lower)
            max_p = float(calc_targets.get("P_max", 0.025 if is_botas else 0.020))
            if p_matches:
                val_p = float("0.0" + p_matches[0])
                if val_p > (max_p + 0.0001):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK FOSFOR LİMİTİ: P max %{max_p:.3f} olmalıdır; ITP'de %{val_p:.3f} yazılmıştır!")

            s_matches = re.findall(r"s\s*[≤<=:]*\s*0\.0(\d+)", up_crit_lower)
            max_s = float(calc_targets.get("S_max", 0.010))
            if s_matches:
                val_s = float("0.0" + s_matches[0])
                if val_s > (max_s + 0.0001):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK KÜKÜRT LİMİTİ: S max %{max_s:.3f} olmalıdır; ITP'de %{val_s:.3f} yazılmıştır!")

        # 2f. Hydrostatic Pressure & Holding Time (via ITPCriteriaParser)
        elif test_key == "hydrostatic":
            parsed_hydro = ITPCriteriaParser.parse_hydrostatic_criteria(f"{up_crit_lower} {up_name.lower()}")
            req_time = int(calc_targets.get("min_holding_time_sec", 20 if is_botas else (10 if (is_welded and d_mm > 457.0) else 5)))
            req_nom_p = float(calc_targets.get("nominal_pressure_bar", 100.0))
            req_min_p = float(calc_targets.get("min_pressure_bar", req_nom_p - 2.0 if is_botas else req_nom_p * 0.90))

            if parsed_hydro["holding_time_sec"] is not None:
                val_time = int(parsed_hydro["holding_time_sec"])
                if val_time < req_time:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ TEST SÜRESİ: Hidrostatik tutma süresi EN AZ {req_time} SANİYE olmalıdır; ITP'de {val_time} sn yazılmıştır!")

            if parsed_hydro["pressure_bar"] is not None:
                val_p = parsed_hydro["pressure_bar"]
                if val_p < req_min_p:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 DÜŞÜK HİDROSTATİK BASINÇ: Boru için hesaplanan fabrika test basıncı {req_nom_p:.1f} bar (Kabul: min {req_min_p:.1f} bar) iken ITP'de {val_p:.1f} bar taahhüt edilmiş!")

        # 2g. Guided Bend Mandrel & Jaw
        elif test_key == "guided_bend":
            crack_matches = re.findall(r"(\d+(?:\.\d+)?)\s*mm", up_crit_lower)
            if crack_matches:
                val_crack = float(crack_matches[0])
                if val_crack > 3.2:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 BÜKME KUSUR LİMİTİ AŞILDI: Maksimum çatlak boyutu 3.2 mm olmalıdır; ITP'de {val_crack:.1f} mm belirtilmiş!")

        # 2h. Residual Stress Ring Test (BOTAŞ)
        elif test_key == "residual_stress":
            s_matches = re.findall(r"(?:artık|stres|stress|s)\s*[≤<=:]*\s*(\d+(?:\.\d+)?)\s*mpa", up_crit_lower)
            max_s = float(calc_targets.get("max_stress_mpa", 45.0))
            if s_matches:
                val_s = float(s_matches[0])
                if val_s > (max_s + 0.5):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 ARTIK GERİLME LİMİTİ AŞILDI: Azami artık gerilme {max_s:.1f} MPa (0.10 x SMYS) olmalıdır; ITP'de {val_s:.1f} MPa belirtilmiş!")

        # 2i. Hardness
        elif test_key == "hardness":
            hv_matches = re.findall(r"(\d+)\s*(?:hv|hv10)", up_crit_lower)
            max_hv = float(calc_targets.get("max_hv10", 300.0))
            if hv_matches:
                val_hv = float(hv_matches[0])
                if val_hv > (max_hv + 1.0):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK SERTLİK LİMİTİ: Azami sertlik {max_hv:.0f} HV10 olmalıdır; ITP'de {val_hv:.0f} HV10 yazılmıştır!")

        # 2j. NDT Weld Seam
        elif test_key == "ndt_weld_seam":
            if re.search(r'\b(?:u1|u1h|u3|u4|n10)\b', full_up_text) or any(k in full_up_text for k in ("seviye u1", "level u1", "u1h", "class a")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YETERSİZ NDT KABUL SEVİYESİ: Kaynak dikişi AUT için ISO 10893-11 Seviye U2 ve RT için ISO 10893-6 Sınıf B zorunludur (U1 / U1H kabul edilemez)!")

        # 2k. NDT Body Lamination (BOTAŞ %40 scan)
        elif test_key == "ndt_pipe_body_lamination":
            scan_matches = re.findall(r"(?:%\s*(\d+)|\b(\d+)\s*%)", full_up_text)
            scan_vals = [int(m[0] or m[1]) for m in scan_matches if (m[0] or m[1])]
            if is_botas and scan_vals and any(v < 40 for v in scan_vals):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YETERSİZ GÖVDE TARAMA ORANI: BOTAŞ Madde 8.8.4.4.1 uyarınca gövde yüzeyinin EN AZ %40'ı ultrasonik taranmalıdır!")
            elif is_botas and "spot" in full_up_text:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YETERSİZ GÖVDE TARAMA ORANI: BOTAŞ Madde 8.8.4.4.1 uyarınca gövde yüzeyinin EN AZ %40'ı ultrasonik taranmalıdır!")

        # 2l. Weld Repair Rules
        elif test_key == "weld_repair_rules":
            if any(k in full_up_text for k in ("gövde tamiri serbest", "body repair permitted", "ana metal kaynak")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 GÖVDE TAMİRİ YASAKTIR: API 5L Madde C.1 ve BOTAŞ uyarınca boru ana metaline kaynakla tamir kesinlikle yasaktır!")
            if any(k in full_up_text for k in ("200 mm tamir", "250 mm tamir", "300 mm tamir")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 TAMİR BOY LİMİTİ AŞILDI: Tek bir kaynak tamirinin boyu en fazla 150 mm olabilir!")
            if t_mm > 10.0 and any(k in full_up_text for k in ("ön ısıtmasız", "no preheat")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 ÖN ISITMA ZORUNLU: t={t_mm:.1f} mm > 10.0 mm borularda tamir öncesi en az 100 °C ön ısıtma şarttır!")

        # 2m. Dimensional Unit Weight
        elif test_key == "dimensional_weight":
            if any(k in up_crit_lower for k in ("-%5", "-5%", "+%15", "+15%")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 AĞIRLIK TOLERANSI AŞILDI: API 5L Madde 9.11.2 uyarınca münferit boru ağırlık toleransı -%3.5 / +%10.0'dur!")

        # 2n. Weld Geometry (Weld Height, Radial Offset, Peaking)
        elif test_key == "weld_geometry_offset_height":
            if is_botas and any(k in up_crit_lower for k in ("3.5 mm", "3.0 mm", "4.0 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KAYNAK YÜKSEKLİK LİMİTİ: BOTAŞ Çizelge 4 uyarınca iç/dış kaynak dikiş yüksekliği azami 2.625 mm olabilir!")

        elif test_key == "weld_radial_offset":
            req_rad = float(calc_targets.get("max_radial_offset_mm", 1.5))
            if any(k in up_crit_lower for k in ("> 2.0", ">2.0", "3.0 mm", "2.5 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 RADYAL KAÇIKLIK LİMİTİ AŞILDI: Azami radyal basamaklanma {req_rad:.2f} mm olabilir!")

        elif test_key == "dimensional_peaking_offset":
            req_peak = float(calc_targets.get("max_peaking_mm", 1.5 if is_botas else 3.2))
            if is_botas and any(k in up_crit_lower for k in ("3.0 mm", "3.2 mm", "2.5 mm", "2.0 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 TEPELEŞME (PEAKING) LİMİTİ AŞILDI: BOTAŞ Çizelge 4 uyarınca boru ucu tepeleşmesi azami {req_peak:.2f} mm olabilir!")

        # 2o. Diameter (Ends & Body)
        elif test_key == "dimensional_diameter_ends":
            req_d_min = float(calc_targets.get("d_end_min_mm", d_mm - 1.6))
            req_d_max = float(calc_targets.get("d_end_max_mm", d_mm + 1.6))
            if any(k in up_crit_lower for k in ("±3.2", "± 3.2", "±4.0", "± 4.0", "±5.0")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 BORU UCU ÇAP TOLERANSI AŞILDI: Boru ucu çap toleransı {req_d_min:.1f} - {req_d_max:.1f} mm aralığında olmalıdır!")

        elif test_key == "dimensional_diameter_body":
            req_d_min = float(calc_targets.get("d_body_min_mm", d_mm - 4.0))
            req_d_max = float(calc_targets.get("d_body_max_mm", d_mm + 4.0))
            if any(k in up_crit_lower for k in ("±8.0", "± 8.0", "±10.0", "± 10.0")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 GÖVDE ÇAP TOLERANSI AŞILDI: Boru gövdesi çap toleransı {req_d_min:.1f} - {req_d_max:.1f} mm aralığında olmalıdır!")

        # 2p. Circumference (Ends & Body)
        elif test_key in ("dimensional_circumference_ends", "dimensional_circumference_body"):
            if any(k in up_crit_lower for k in ("±25 mm", "±30 mm", "± 25", "± 30")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 ÇEVRE TOLERANSI AŞILDI: Pi-mezura çevre ölçüm toleransı aşılmıştır!")

        # 2q. Ovality (Ends & Body)
        elif test_key == "dimensional_ovality_ends":
            req_ov = float(calc_targets.get("ovality_end_max_mm", 3.05 if is_botas else 6.10))
            ov_matches = re.findall(r"(\d+(?:\.\d+)?)\s*mm", up_crit_lower)
            if ov_matches:
                val_ov = float(ov_matches[0])
                if val_ov > (req_ov + 0.05):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 BORU UCU OVALİTE LİMİTİ AŞILDI: BOTAŞ Şartnamesi Madde 5.1 uyarınca uç ovalitesi azami {req_ov:.2f} mm olmalıdır; ITP'de {val_ov:.2f} mm belirtilmiş!")
            elif is_botas and any(k in up_crit_lower for k in ("10 mm", "12 mm", "15 mm", "8 mm", "15")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 BORU UCU OVALİTE LİMİTİ AŞILDI: BOTAŞ Şartnamesi Madde 5.1 uyarınca uç ovalitesi azami {req_ov:.2f} mm olmalıdır!")

        elif test_key == "dimensional_ovality_body":
            req_ov = float(calc_targets.get("ovality_body_max_mm", 6.10 if is_botas else 18.30))
            ov_matches = re.findall(r"(\d+(?:\.\d+)?)\s*mm", up_crit_lower)
            if ov_matches:
                val_ov = float(ov_matches[0])
                if val_ov > (req_ov + 0.05):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 GÖVDE OVALİTE LİMİTİ AŞILDI: BOTAŞ Şartnamesi Madde 5.1 uyarınca gövde ovalitesi azami {req_ov:.2f} mm olmalıdır; ITP'de {val_ov:.2f} mm belirtilmiş!")
            elif is_botas and any(k in up_crit_lower for k in ("15 mm", "18 mm", "20 mm", "25")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 GÖVDE OVALİTE LİMİTİ AŞILDI: BOTAŞ Şartnamesi Madde 5.1 uyarınca gövde ovalitesi azami {req_ov:.2f} mm olmalıdır!")

        # 2r. Wall Thickness
        elif test_key == "dimensional_wall_thickness":
            req_min_t = float(calc_targets.get("min_mm", t_mm * 0.90))
            if any(k in up_crit_lower for k in ("-%15", "-15%", "-%20", "-20%")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 ET KALINLIĞI NEGATİF TOLERANSI AŞILDI: Asgari et kalınlığı {req_min_t:.2f} mm olmalıdır!")

        # 2s. Straightness
        elif test_key == "dimensional_straightness":
            if any(k in up_crit_lower for k in ("0.4% l", "0.5% l", "%0.4", "%0.5", "0.4%", "0.5%")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 DOĞRUSALLIK SAPMASI AŞILDI: Toplam boy doğrusallıktan sapma azami %0.20L (BOTAŞ: %0.10L) olmalıdır!")

        # 2t. Bevel & Root Face
        elif test_key == "dimensional_bevel_ends":
            if any(k in up_crit_lower for k in ("45°", "45 deg", "50°", "50 deg", "20°")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KAYNAK AĞZI AÇISI HATALI: Standart alın kaynak ağzı açısı 30° (+5°/-0°) (veya 35°) olmalıdır!")

        # 2u. Squareness
        elif test_key in ("dimensional_squareness_ends", "dimensional_squareness"):
            if any(k in up_crit_lower for k in ("> 3.0 mm", ">3.0", "4.0 mm", "5.0 mm", "2.5 mm", "3.0 mm", "3.5 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 DİKLİKTEN SAPMA LİMİTİ AŞILDI: API 5L Çizelge 11 uyarınca boru ucu diklikten sapma azami 1.6 mm olmalıdır!")

        # 2v. Wall Thickness
        elif test_key == "dimensional_wall_thickness":
            parsed_dim = ITPCriteriaParser.parse_dimensional_criteria(up_crit_lower)
            if parsed_dim.get("minus_pct") is not None:
                minus_p = parsed_dim["minus_pct"]
                allowed_minus = 10.0 if not is_botas else 8.0
                if minus_p > allowed_minus:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 ET KALINLIĞI EKSİ TOLERANSI AŞILDI: İzin verilen azami eksi tolerans -%{allowed_minus:.1f}'dir; ITP'de -%{minus_p:.1f} yazılmıştır!")
            elif any(k in up_crit_lower for k in ("-12.5%", "-15%", "-%12.5", "-%15")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 ET KALINLIĞI EKSİ TOLERANSI AŞILDI: API 5L Çizelge 11 / BOTAŞ uyarınca eksi tolerans aşılmıştır!")

        # 2w. Dimensional Diameter (Body & Ends)
        elif test_key in ("dimensional_diameter_ends", "dimensional_diameter_body"):
            req_d_min = float(calc_targets.get("d_end_min_mm" if "ends" in test_key else "d_body_min_mm", d_mm - 3.2))
            req_d_max = float(calc_targets.get("d_end_max_mm" if "ends" in test_key else "d_body_max_mm", d_mm + 3.2))
            parsed_dim = ITPCriteriaParser.parse_dimensional_criteria(up_crit_lower)
            
            if parsed_dim.get("plus_mm") is not None and parsed_dim.get("plus_mm") > (abs(req_d_max - d_mm) + 1.0):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 DIŞ ÇAP ARTI TOLERANSI AŞILDI: İzin verilen azami artı tolerans +{abs(req_d_max-d_mm):.2f} mm'dir!")
            elif parsed_dim.get("minus_mm") is not None and parsed_dim.get("minus_mm") > (abs(d_mm - req_d_min) + 1.0):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 DIŞ ÇAP EKSİ TOLERANSI AŞILDI: İzin verilen azami eksi tolerans -{abs(d_mm-req_d_min):.2f} mm'dir!")

        # 2x. Ovality (Out of Roundness)
        elif test_key in ("dimensional_ovality_ends", "dimensional_ovality_body"):
            req_ov = float(calc_targets.get("ovality_end_max_mm" if "ends" in test_key else "ovality_body_max_mm", 4.0))
            parsed_dim = ITPCriteriaParser.parse_dimensional_criteria(up_crit_lower)
            if parsed_dim.get("max_limit_mm") is not None and parsed_dim["max_limit_mm"] > (req_ov + 0.5):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append(f"🔴 OVALİTE LİMİTİ AŞILDI: Azami izin verilen dairesellikten sapma {req_ov:.2f} mm'dir; ITP'de {parsed_dim['max_limit_mm']:.2f} mm belirtilmiştir!")

        # 2y. Residual Magnetism
        elif test_key == "residual_magnetism":
            if re.search(r'(?<![\d.])\b(?:50|40)\s*gauss\b|(?<![\d.])\b5(?:\.0)?\s*mt\b', up_crit_lower):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 MANYETİZMA LİMİTİ AŞILDI: BOTAŞ Madde 8.1.1 ve API 5L 9.14 uyarınca artık manyetizma ortalama max 3.0 mT (30 Gauss), tekil max 3.5 mT (35 Gauss) olmalıdır!")

        # 2z. Surface Quality
        elif test_key == "surface_visual_quality":
            if any(k in up_crit_lower for k in ("sınıf a", "class a")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YÜZEY KALİTE SINIFI YETERSİZ: BOTAŞ Madde 8.2 uyarınca EN 10163-2 Sınıf B Alt Sınıf 3 yüzey kalitesi şarttır!")

        # 2aa. Stenciling / Marking
        elif test_key == "pipe_marking_stenciling":
            if not any(k in full_up_text for k in ("api", "botaş", "botas", "en 10204", "3.1", "3.2", "barkod", "şablon", "markalama")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 EKSİK PROJE MARKALAMASI: Boru üzerinde API 5L Monogramı, BOTAŞ Proje Kodu, Isı/Boru No ve EN 10204 3.1/3.2 sertifikası yer almalıdır!")

        # 2ab. Personnel Qualification
        elif test_key == "personnel_qualification_ndt":
            if any(k in full_up_text for k in ("sertifikasız", "level 1 süpervizör", "asnt level 1")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 NDT PERSONEL YETKİNLİK HATASI: NDT Süpervizörü EN ISO 9712 Level 3, operatörler ise Level 2 sertifikalı olmalıdır!")

        # 2ac. Laboratory Qualification
        elif test_key == "laboratory_qualification":
            if any(k in full_up_text for k in ("akreditesiz", "türkak yok", "no accreditation")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 LABORATUVAR AKREDİTASYONU EKSİK: İmalatçı test laboratuvarı ISO/IEC 17025 (TÜRKAK / ILAC) akreditasyonuna sahip olmalıdır!")

        # 2ad. 3LPE Coating Thickness
        elif test_key == "coating_thickness_3lpe":
            parsed_c = ITPCriteriaParser.parse_coating_criteria(f"{up_crit_lower} {up_name.lower()}")
            if (parsed_c["total_pe_mm"] is not None and parsed_c["total_pe_mm"] < 2.85) or "< 2.5" in up_crit_lower:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 3LPE KAPLAMA KALINLIĞI YETERSİZ: BOTAŞ 5410 R1 ve DIN 30670 Yükseltilmiş Tip (v) uyarınca toplam PE kalınlığı en az 3.0 mm (3000 µm) olmalıdır!")
            if parsed_c["fbe_um"] is not None and parsed_c["fbe_um"] < 100:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 FBE ASTAR KALINLIĞI YETERSİZ: FBE epoksi astar kalınlığı en az 120 µm olmalıdır!")

        # 2ae. Coating Impact Resistance
        elif test_key == "coating_impact_resistance":
            parsed_c = ITPCriteriaParser.parse_coating_criteria(f"{up_crit_lower} {up_name.lower()}")
            if (parsed_c["impact_j_mm"] is not None and parsed_c["impact_j_mm"] < 4.8) or "< 5" in up_crit_lower:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KAPLAMA DARBE DİRENCİ YETERSİZ: BOTAŞ 5410 R1 uyarınca darbe enerjisi en az 5.0 J/mm (veya 7.0 J/mm) olmalıdır!")

        # 2af. Coating Holiday Test
        elif test_key == "coating_holiday_test":
            parsed_c = ITPCriteriaParser.parse_coating_criteria(f"{up_crit_lower} {up_name.lower()}")
            if (parsed_c["holiday_kv"] is not None and parsed_c["holiday_kv"] < 24.0) or re.search(r'(?<![\d.])\b(?:15|10|5)\s*kv\b', up_crit_lower):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 HOLIDAY TEST GERİLİMİ HATALI: BOTAŞ 5410 R1 uyarınca test gerilimi 25.000 Volt (25 kV) olmalı ve kesinlikle kıvılcım/delik oluşmamalıdır!")

        # 2ag. Coating Peel Adhesion
        elif test_key == "coating_peel_adhesion":
            parsed_c = ITPCriteriaParser.parse_coating_criteria(f"{up_crit_lower} {up_name.lower()}")
            if (parsed_c["peel_n_mm"] is not None and parsed_c["peel_n_mm"] < 14.5) or "< 100" in up_crit_lower:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 SOYULMA MUKAVEMETİ YETERSİZ: BOTAŞ 5410 R1 uyarınca 23 °C'de yapışma direnci en az 150 N/cm (veya 15 N/mm) olmalıdır!")

        # 2ah. Coating Cathodic Disbondment (CD)
        elif test_key == "coating_cathodic_disbondment":
            if re.search(r"(?:>|\b)(?:1[0-9]|2[0-9])\s*mm", up_crit_lower) or any(k in up_crit_lower for k in ("> 10 mm", "> 12 mm", "> 15 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KATODİK SOYULMA LİMİTİ AŞILDI: ISO 21809-1 ve BOTAŞ uyarınca 28 gün (20 °C) / 24 saat (65 °C) katodik soyulma yarıçapı azami 7.0 mm olabilir!")

        # 2ai. Coating Surface Preparation & Blasting
        elif test_key == "coating_surface_prep_blasting":
            if any(k in up_crit_lower for k in ("sa 2\b", "sa 1\b", "sa 2.0", "> 25 mg/m2", "> 30 mg/m2", "> 120 µm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KUMLAMA YÜZEY TEMİZLİĞİ YETERSİZ: Temizlik min Sa 2½, pürüzlülük Rz 60-100 µm ve tuz miktarı max 20 mg/m² (2 µg/cm²) olmalıdır!")

        # 2aj. Coating Indentation
        elif test_key == "coating_indentation":
            if re.search(r"(?:>|\b)(?:0\.[4-9]|1\.[0-9])\s*mm", up_crit_lower) or any(k in up_crit_lower for k in ("> 0.4 mm", "> 0.5 mm", "0.5 mm", "0.6 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 DELİCİ UÇ BATMA LİMİTİ AŞILDI: 23 °C'de batma derinliği max 0.20 mm, 50 °C'de max 0.30 mm olmalıdır!")

        # 2ak. Flattening Test
        elif test_key == "flattening":
            if any(k in up_crit_lower for k in ("laminasyon serbest", "çatlak serbest", "crack permitted")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YASSILTMA KUSURU: API 5L Madde 9.10.2 uyarınca dikiş açılması veya gövde çatlağı kesinlikle yasaktır!")

        # 2al. ERW Flash Trim & Groove
        elif test_key == "erw_flash_trim_weld":
            if any(k in up_crit_lower for k in ("> 1.5 mm", "> 1.2 mm", "1.5 mm", "2.0 mm", "> 0.1 mm", "> 0.5 mm", "0.5 mm", "0.6 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 ERW ÇAPAK LİMİTİ AŞILDI: API 5L Madde 9.13.2 uyarınca iç çapak yüksekliği max 1.1 mm ve oyuk derinliği max 0.04 mm olmalıdır!")

        # 2am. ERW Metallography
        elif test_key == "erw_metallographic_seam":
            if any(k in up_crit_lower for k in ("martenzit serbest", "martensite permitted")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 MARTENZİT YASAKTIR: ERW kaynak dikişinde martenzit yapısı kesinlikle yasaktır, tam normalizasyon tavlaması zorunludur!")

        # Final remarks formatting
        if not remarks:
            if is_botas:
                remarks_text = "🟢 BOTAŞ Çelik Boru Şartnamesi (4-NGTL-0-GN-P-002-5120 R7) ve hesaplanan boru parametrelerine tam uyumludur."
            else:
                remarks_text = "🟢 API Spec 5L 47. Baskı ve hesaplanan boru parametrelerine tam uyumludur."
        else:
            remarks_text = " ".join(remarks)

        return {
            "test_key": test_key,
            "category": master["category"],
            "test_name": master["test_name"],
            "calculated_target": master.get("calculated_target_str", "—"),
            "ndt_method_standard": master.get("ndt_method_standard", "—"),
            "ndt_acceptance_level": master.get("ndt_acceptance_level", "—"),
            "uploaded_frequency": up_freq or "—",
            "standard_frequency": std_freq,
            "uploaded_criteria": up_crit or "—",
            "standard_criteria": std_crit,
            "status": status,
            "issue_type": issue_type,
            "audit_remarks": remarks_text,
            "clause_ref": master["clause_ref"],
            "table_ref": master["table_ref"],
            "is_coating": master.get("is_coating", False),
            "reading_confidence": uploaded.get("reading_confidence", "HIGH"),
            "inspection_points": uploaded.get("inspection_points", {"mfg": "C", "tpi": "W", "client": "W"})
        }
