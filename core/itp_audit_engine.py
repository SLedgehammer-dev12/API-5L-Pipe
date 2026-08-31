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

    # Keyword mappings to match uploaded row names to standard test keys
    TEST_MATCHER_KEYWORDS = {
        "chemical_heat": ["ısı analizi", "döküm analizi", "heat analysis", "ladle analysis", "cast analysis", "ladle heat", "isi analizi"],
        "chemical_product": ["ürün analizi", "product analysis", "check analysis", "product chemical", "urun analizi"],
        "tensile_body": ["gövde çekme", "pipe body tensile", "body tensile", "çekme testi", "tensile test", "transverse tensile", "govde cekme"],
        "tensile_weld": ["kaynak çekme", "weld tensile", "weld seam tensile", "kaynak dikişi çekme", "all weld tensile", "kaynak cekme"],
        "cvn_body": ["gövde çentik", "gövde darbe", "cvn body", "charpy body", "body impact", "çentik darbe", "charpy v-notch", "govde centik"],
        "cvn_weld_haz": ["kaynak darbe", "itab darbe", "haz impact", "weld impact", "cvn weld", "charpy weld", "weld & haz", "weld and haz", "kaynak & itab"],
        "dwtt": ["dwtt", "drop weight", "yırtılma testi", "düşen ağırlık", "yirtilma testi", "dusen agirlik"],
        "guided_bend": ["kılavuzlu bükme", "guided bend", "guided-bend", "kök bükme", "kapak bükme", "root bend", "face bend", "bend test", "kilavuzlu bukme", "mandrel"],
        "flattening": ["düzleştirme", "flattening", "yassıltma", "duzlestirme"],
        "hardness": ["sertlik", "hardness", "hv10", "hrc", "hbw"],
        "residual_stress": ["artık stres", "residual stress", "halka kesme", "stres kontrolü", "ring test", "çevresel gerilme", "artik stres"],
        "hydrostatic": ["hidrostatik", "hydrostatic", "su basınç", "basınç testi", "hydro test", "mill hydro", "basinc testi"],
        "ndt_weld_seam": ["kaynak dikişi ndt", "kaynak ndt", "weld seam ndt", "weld ut", "weld rt", "radyografi", "ultrasonik kaynak", "ultrasonic weld", "weld inspection", "radiographic weld", "kaynak dikişi %100 ndt", "kaynak dikisi ndt"],
        "ndt_pipe_body_lamination": ["gövde laminasyon", "gövdesi laminasyon", "body lamination", "gövde ut", "gövdesi ut", "sac laminasyon", "plaka laminasyon", "body laminar", "gövde laminas", "boru gövdesi ut laminasyon", "govde laminasyon"],
        "ndt_pipe_ends": ["boru uçları ndt", "uç laminasyon", "pipe ends ndt", "laminar testing", "end ut", "ends ut", "boru uçları laminasyon", "uçları laminasyon", "uç laminar", "pipe ends laminar", "boru uclari laminasyon", "uclari laminasyon"],
        "ndt_smls_body": ["dikişsiz gövde ndt", "smls body ndt", "flux leakage", "gövde ut", "seamless body", "dikissiz govde"],
        "ndt_bevel_mt": ["kaynak ağzı mt", "tamir mt", "manyetik parçacık", "magnetic particle", "mpi", "bevel mt", "kaynak agzi mt", "manyetik muayene"],
        "weld_repair_rules": ["tamir kuralları", "tamir kaynağı", "onarım", "weld repair", "repair procedure", "tamir şartları", "kaynak tamiri", "repair conditions", "tamir kurallari", "tamir sarti"],
        "weld_geometry_offset_height": ["kaynak geometrisi", "kaynak yüksekliği", "radyal kaçıklık", "radial offset", "weld height", "reinforcement", "tepeleşme", "peaking", "misalignment", "kaynak dikiş yüksekliği", "kaynak yuksekligi", "radyal kaciklik"],
        "dimensional_diameter_ovality": ["dış çap", "ovallik", "çap toleransı", "diameter", "out of roundness", "ovality", "out-of-roundness", "dış çap ve ovallik", "dis cap", "dis cap ve ovallik"],
        "dimensional_wall_thickness": ["et kalınlığı", "wall thickness", "cidar kalınlığı", "thickness verification", "et kalınlığı ölçümü", "et kalinligi", "et kal"],
        "dimensional_weight": ["birim ağırlık", "boru ağırlığı", "weight per meter", "mass", "tartım", "kantar", "ağırlık toleransı", "pipe weight", "birim agirlik", "boru agirligi"],
        "dimensional_length_straightness_bevel": ["doğrusallık", "boy", "alın kaynak ağzı", "straightness", "length", "bevel", "ağız açısı", "doğrusallık, boy", "dogrusallik", "kaynak agzi"],
        "visual_surface": ["görsel muayene", "yüzey muayenesi", "visual inspection", "surface inspection", "gözle muayene", "görsel yüzey", "gorsel", "yuzey muayenesi"],
        "residual_magnetism": ["kalıntı manyetizma", "manyetizma", "residual magnetism", "gaussmetre", "gauss", "kalinti manyetizma"],
        "quality_marking_surface_prep": ["proje markalaması", "markalama", "stenciling", "şablonlama", "yüzey hazırlığı", "surface prep", "sa 2.5", "en 10204", "mtc", "kalite sertifikası", "3.1 sertifika", "3.2 sertifika", "marking", "sablonlama"],
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

                # Contextual & Specificity Reinforcement
                if test_key == "ndt_pipe_ends" and any(k in full_up_text for k in ("uç", "uclari", "ends", "pipe end")):
                    score += 45
                elif test_key == "ndt_pipe_body_lamination" and any(k in full_up_text for k in ("40%", "gövde laminas", "sac laminas", "12094", "body lamin")):
                    score += 45
                elif test_key == "ndt_weld_seam" and any(k in full_up_text for k in ("dikiş", "seam", "10893-11", "10893-6", "aut", "kaynak dikiş")):
                    score += 50
                elif test_key == "ndt_smls_body" and is_smls and any(k in full_up_text for k in ("dikişsiz", "smls", "10893-10", "flux")):
                    score += 60
                elif test_key == "weld_repair_rules" and any(k in full_up_text for k in ("tamir", "repair", "re-repair", "ön ısıtma", "preheat")):
                    score += 50
                elif test_key == "dimensional_weight" and any(k in full_up_text for k in ("ağırlık", "weight", "kg/m", "kantar", "mass", "tartım")):
                    score += 50
                elif test_key == "guided_bend" and any(k in full_up_text for k in ("mandrel", "bükme", "bend", "çene", "5173")):
                    score += 50
                elif test_key == "weld_geometry_offset_height" and any(k in full_up_text for k in ("yükseklik", "kaçıklık", "offset", "peaking", "tepeleşme", "misalignment")):
                    score += 50
                elif test_key == "quality_marking_surface_prep" and any(k in full_up_text for k in ("markalama", "sa 2.5", "stenciling", "şablon", "3.1", "3.2", "mtc")):
                    score += 50
                elif test_key == "residual_stress" and any(k in full_up_text for k in ("artık stres", "residual stress", "halka kesme", "ring test")):
                    score += 55

                # Anti-affinity penalties
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
                # Missing from uploaded ITP
                if master_item["is_mandatory"]:
                    row_eval = {
                        "test_key": test_key,
                        "category": master_item["category"],
                        "test_name": master_item["test_name"],
                        "calculated_target": master_item.get("calculated_target_str", "—"),
                        "ndt_method_standard": master_item.get("ndt_method_standard", "—"),
                        "ndt_acceptance_level": master_item.get("ndt_acceptance_level", "—"),
                        "uploaded_frequency": "— (ITP'de Bulunamadı / Eksik)",
                        "standard_frequency": master_item["standard_frequency"],
                        "uploaded_criteria": "—",
                        "standard_criteria": master_item["standard_acceptance_criteria"],
                        "status": "NON_COMPLIANT",
                        "issue_type": "MISSING_MANDATORY_TEST",
                        "audit_remarks": f"🔴 ZORUNLU TEST EKSİK: {master_item['clause_ref']} uyarınca zorunlu olan bu test imalatçı ITP'sinde bulunmamaktadır!",
                        "clause_ref": master_item["clause_ref"],
                        "table_ref": master_item["table_ref"]
                    }
                    audit_rows.append(row_eval)
                    findings.append({
                        "test_name": master_item["test_name"],
                        "severity": "CRITICAL",
                        "issue_type": "MISSING_MANDATORY_TEST",
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
                        "table_ref": master_item["table_ref"]
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
                    "table_ref": "—"
                })

        # Calculate Statistics & Weighted Compliance Score (A5 Solution)
        total_rows = len(audit_rows)
        non_compliant_count = sum(1 for r in audit_rows if r["status"] == "NON_COMPLIANT")
        more_stringent_count = sum(1 for r in audit_rows if r["status"] == "MORE_STRINGENT")
        compliant_count = sum(1 for r in audit_rows if r["status"] == "COMPLIANT")

        if total_rows > 0:
            if non_compliant_count > 0:
                compliance_score = max(0.0, round(((compliant_count + (0.5 * more_stringent_count) - (1.5 * non_compliant_count)) / total_rows) * 100.0, 1))
                overall_verdict = "REJECTED"
            elif more_stringent_count > 0:
                compliance_score = round(((compliant_count + more_stringent_count) / total_rows * 100.0), 1)
                overall_verdict = "APPROVED_WITH_COMMENTS"
            else:
                compliance_score = 100.0
                overall_verdict = "APPROVED"
        else:
            compliance_score = 100.0
            overall_verdict = "APPROVED"

        return {
            "pipe_summary": {
                "diameter_mm": pipe_config.get("diameter_mm", 1219.0),
                "diameter_inch": pipe_config.get("diameter_inch", '48"'),
                "wall_thickness_mm": pipe_config.get("wall_thickness_mm", 14.30),
                "material_grade": pipe_config.get("material_grade", "X65"),
                "manufacturing_process": pipe_config.get("manufacturing_process", "SAWH"),
                "psl_level": pipe_config.get("psl_level", "PSL2"),
                "standard_edition": "API Spec 5L 47th Edition / BOTAŞ Şartnamesi"
            },
            "kpi": {
                "total_tests_audited": total_rows,
                "compliant_count": compliant_count,
                "more_stringent_count": more_stringent_count,
                "non_compliant_count": non_compliant_count,
                "compliance_score_percent": compliance_score,
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

        up_freq_lower = up_freq.lower()
        up_crit_lower = up_crit.lower()
        up_std_lower = up_std.lower()
        full_up_text = f"{up_crit_lower} {up_std_lower}"

        # --- 1. Comprehensive Canonical Frequency Evaluation (R4 Solution) ---
        canon_freq = FrequencyNormalizer.normalize(up_freq)

        if test_key in ("hydrostatic", "ndt_weld_seam", "visual_surface", "dimensional_wall_thickness",
                        "dimensional_length_straightness_bevel", "ndt_pipe_ends", "ndt_bevel_mt",
                        "quality_marking_surface_prep", "dimensional_diameter_ovality", "dimensional_weight"):
            if canon_freq in (FrequencyCanonical.INADEQUATE_SAMPLING, FrequencyCanonical.PER_TEST_UNIT, FrequencyCanonical.PERIODIC_SHIFT):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append(f"🔴 FREKANS YETERSİZ: Standart gereği bu test İSTİSNASIZ HER BORUDA (%100) yapılmalıdır; '{up_freq}' kabul edilemez.")
        elif test_key == "chemical_product":
            if not is_botas and ("1 analiz" in up_freq_lower or "1 adet" in up_freq_lower or "1 per" in up_freq_lower):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: Ürün analizi ısı başına en az 2 adet (ayrı borulardan) yapılmalıdır (API 5L 9.2).")
        elif test_key == "chemical_heat":
            if canon_freq == FrequencyCanonical.INADEQUATE_SAMPLING or any(k in up_freq_lower for k in ("1 per 5", "1 per 10", "1/5", "1/10")):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: Döküm analizi istisnasız her dökümde (per heat) yapılmalıdır!")
        elif test_key == "residual_stress":
            if is_botas and canon_freq != FrequencyCanonical.PER_HEAT and any(k in up_freq_lower for k in ("lot", "örneklem", "sample", "test ünitesi")):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: BOTAŞ Şartnamesi Madde 3.3.9 uyarınca artık stres testi HER DÖKÜMDE (HEAT) zorunludur.")

        # --- 2. Comprehensive Criteria & Numeric Evaluations ---

        # 2a. CVN Body Impact
        if test_key == "cvn_body":
            j_matches = re.findall(r"(\d+)\s*(?:j|joule)", up_crit_lower)
            req_avg = float(calc_targets.get("avg_j", 60.0 if is_botas else 41.0))
            if j_matches:
                val = float(j_matches[0])
                if val < req_avg:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DARBE ENERJİSİ (GÖVDE): Asgari ortalama darbe enerjisi {req_avg:.0f} J olmalıdır; ITP'de {val:.0f} J yazılmıştır!")
                elif val > req_avg + 5.0:
                    status = "MORE_STRINGENT"
                    issue_type = "MORE_STRINGENT"
                    remarks.append(f"🟡 DAHA SIKI DARBE ENERJİSİ: İmalatçı {val:.0f} J taahhüt etmiştir (Hesaplanan: {req_avg:.0f} J).")
            if is_botas and "0 °c" in full_up_text and "-20" not in full_up_text:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 HATALI TEST SICAKLIĞI: BOTAŞ Madde 3.3.5 uyarınca gövde darbe deneyi -20 °C'de yapılmalıdır; ITP'de 0 °C belirtilmiştir!")

        # 2b. CVN Weld & HAZ Impact
        elif test_key == "cvn_weld_haz":
            j_matches = re.findall(r"(\d+)\s*(?:j|joule)", up_crit_lower)
            req_avg = float(calc_targets.get("avg_j", 45.0 if is_botas else 27.0))
            if j_matches:
                val = float(j_matches[0])
                if val < req_avg:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DARBE ENERJİSİ (KAYNAK/ITAB): Asgari ortalama {req_avg:.0f} J olmalıdır; ITP'de {val:.0f} J yazılmıştır!")
            if is_botas and "0 °c" in full_up_text and "-20" not in full_up_text:
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 HATALI TEST SICAKLIĞI: BOTAŞ Madde 3.3.5 uyarınca Kaynak & ITAB darbe deneyi -20 °C'de yapılmalıdır!")

        # 2c. DWTT (Drop Weight Tear Test)
        elif test_key == "dwtt":
            shear_matches = re.findall(r"(?:%\s*(\d+)|\b(\d+)\s*%)", up_crit_lower)
            vals = [int(m[0] or m[1]) for m in shear_matches if (m[0] or m[1])]
            if vals:
                val_shear = vals[0]
                if val_shear < 85:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DWTT SÜNEK KIRILMA: Ortalama sünek kırılma alanı min %85 olmalıdır; ITP'de %{val_shear} yazılmıştır!")
            if is_botas and any(k in up_crit_lower for k in ("< 60", "<%60", "tekil < 60")):
                pass  # Compliant individual rule
            elif is_botas and any(k in up_crit_lower for k in ("50%", "tekil 50", "40%")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 DWTT MÜNFERİT LİMİTİ: BOTAŞ Madde 3.3.6 uyarınca hiçbir tekil numune <%60 olamaz!")

        # 2d. Tensile Body & Weld
        elif test_key == "tensile_body":
            # Yield Rt0.5
            rt_matches = re.findall(r"rt0?\.?5?\s*[≥>=:]*\s*(\d+(?:\.\d+)?)", up_crit_lower)
            req_rt = float(calc_targets.get("yield_min_mpa", 450.0))
            if rt_matches:
                val_rt = float(rt_matches[0])
                if val_rt < req_rt - 0.5:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 DÜŞÜK AKMA MUKAVEMETİ: Asgari Rt0.5={req_rt:.1f} MPa olmalıdır; ITP'de {val_rt:.1f} MPa belirtilmiş!")

            # Elongation Af
            af_matches = re.findall(r"(?:af|uzama|elongation)\s*[≥>=:]*\s*%?\s*(\d+(?:\.\d+)?)%?", up_crit_lower)
            req_af = float(calc_targets.get("elongation_min_pct", 19.5))
            if af_matches:
                val_af = float(af_matches[0])
                if val_af < (req_af - 0.2):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ KOPMA UZAMASI: Boru et kalınlığına göre asgari uzama %{req_af:.1f} iken ITP'de %{val_af:.1f} belirtilmiş!")

            # Y/T Ratio
            yt_matches = re.findall(r"y\s*/\s*t\s*[≤<=:]*\s*0\.(\d+)", up_crit_lower)
            req_yt = float(calc_targets.get("yt_ratio_max", 0.90 if is_botas else 0.93))
            if yt_matches:
                val_yt = float("0." + yt_matches[0])
                if val_yt > (req_yt + 0.005):
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK Y/T ORANI: Azami Y/T={req_yt:.2f} olmalıdır; ITP'de {val_yt:.2f} yazılmıştır!")

        elif test_key == "tensile_weld":
            rm_matches = re.findall(r"rm\s*[≥>=:]*\s*(\d+(?:\.\d+)?)", up_crit_lower)
            req_rm = float(calc_targets.get("tensile_min_mpa", 535.0))
            if rm_matches:
                val_rm = float(rm_matches[0])
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

        # 2f. Hydrostatic Pressure & Holding Time (A4 Solution)
        elif test_key == "hydrostatic":
            time_matches = re.findall(r"(\d+)\s*(?:sn|saniye|sec|second)", up_crit_lower)
            req_time = int(calc_targets.get("min_holding_time_sec", 20 if is_botas else (10 if (is_welded and d_mm > 457.0) else 5)))
            req_nom_p = float(calc_targets.get("nominal_pressure_bar", 100.0))
            req_min_p = float(calc_targets.get("min_pressure_bar", req_nom_p - 2.0 if is_botas else req_nom_p * 0.90))

            if time_matches:
                val_time = int(time_matches[0])
                if val_time < req_time:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ TEST SÜRESİ: Hidrostatik tutma süresi EN AZ {req_time} SANİYE olmalıdır; ITP'de {val_time} sn yazılmıştır!")

            bar_matches = re.findall(r"(?:basınç|pressure|p|test|min|smys)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:bar)", up_crit_lower)
            if bar_matches:
                val_p = float(bar_matches[-1])  # Take the target pressure value
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
            if any(k in full_up_text for k in ("u3", "u4", "n10", "class a")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 YETERSİZ NDT KABUL SEVİYESİ: Kaynak dikişi AUT için ISO 10893-11 Seviye U2 ve RT için ISO 10893-6 Sınıf B zorunludur!")

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

        # 2n. Weld Geometry & Peaking
        elif test_key == "weld_geometry_offset_height":
            if is_botas and any(k in up_crit_lower for k in ("3.5 mm", "3.0 mm", "4.0 mm")):
                status = "NON_COMPLIANT"
                issue_type = "CRITERIA_VIOLATION"
                remarks.append("🔴 KAYNAK YÜKSEKLİK LİMİTİ: BOTAŞ Çizelge 4 uyarınca iç/dış kaynak dikiş yüksekliği azami 2.625 mm olabilir!")

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
            "table_ref": master["table_ref"]
        }

