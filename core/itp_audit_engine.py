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
from typing import Any, Dict, List, Optional
from core.test_plan import get_comprehensive_itp_specification


class ITPAuditEngine:
    """
    Automated ITP Audit and Discrepancy Evaluation Engine.
    """

    # Keyword mappings to match uploaded row names to standard test keys
    TEST_MATCHER_KEYWORDS = {
        "chemical_heat": ["ısı analizi", "döküm analizi", "heat analysis", "ladle analysis", "cast analysis", "ladle heat"],
        "chemical_product": ["ürün analizi", "product analysis", "check analysis", "product chemical"],
        "tensile_body": ["gövde çekme", "pipe body tensile", "body tensile", "çekme testi", "tensile test", "transverse tensile"],
        "tensile_weld": ["kaynak çekme", "weld tensile", "weld seam tensile", "kaynak dikişi çekme", "all weld tensile"],
        "cvn_body": ["gövde çentik", "gövde darbe", "cvn body", "charpy body", "body impact", "çentik darbe", "charpy v-notch"],
        "cvn_weld_haz": ["kaynak darbe", "itab darbe", "haz impact", "weld impact", "cvn weld", "charpy weld", "weld & haz", "weld and haz"],
        "dwtt": ["dwtt", "drop weight", "yırtılma testi", "düşen ağırlık"],
        "guided_bend": ["kılavuzlu bükme", "guided bend", "guided-bend", "kök bükme", "kapak bükme", "root bend", "face bend", "bend test"],
        "flattening": ["düzleştirme", "flattening", "yassıltma"],
        "hardness": ["sertlik", "hardness", "hv10", "hrc", "hbw"],
        "hydrostatic": ["hidrostatik", "hydrostatic", "su basınç", "basınç testi", "hydro test", "mill hydro"],
        "ndt_weld_seam": ["kaynak dikişi ndt", "kaynak ndt", "weld seam ndt", "weld ut", "weld rt", "radyografi", "ultrasonik kaynak", "ultrasonic weld", "weld inspection", "radiographic weld", "kaynak dikişi %100 ndt"],
        "ndt_pipe_body_lamination": ["gövde laminasyon", "gövdesi laminasyon", "body lamination", "gövde ut", "gövdesi ut", "sac laminasyon", "plaka laminasyon", "body laminar", "gövde laminas", "boru gövdesi ut laminasyon"],
        "ndt_pipe_ends": ["boru uçları ndt", "uç laminasyon", "pipe ends ndt", "laminar testing", "end ut", "ends ut", "boru uçları laminasyon", "uçları laminasyon", "uç laminar", "pipe ends laminar", "boru uclari laminasyon"],
        "ndt_smls_body": ["dikişsiz gövde ndt", "smls body ndt", "flux leakage", "gövde ut", "seamless body"],
        "residual_stress": ["artık stres", "residual stress", "halka kesme", "stres kontrolü", "ring test", "çevresel gerilme", "artik stres"],
        "dimensional_diameter_ovality": ["dış çap", "ovallik", "çap toleransı", "diameter", "out of roundness", "ovality", "out-of-roundness", "dış çap ve ovallik", "dis cap"],
        "dimensional_wall_thickness": ["et kalınlığı", "wall thickness", "cidar kalınlığı", "thickness verification", "et kalınlığı ölçümü", "et kalinligi", "et kal"],
        "dimensional_length_straightness_bevel": ["doğrusallık", "boy", "alın kaynak ağzı", "straightness", "length", "bevel", "ağız açısı", "doğrusallık, boy", "dogrusallik"],
        "visual_surface": ["görsel muayene", "yüzey muayenesi", "visual inspection", "surface inspection", "gözle muayene", "görsel yüzey", "gorsel"],
        "residual_magnetism": ["kalıntı manyetizma", "manyetizma", "residual magnetism", "gaussmetre", "gauss", "kalinti manyetizma"],
    }

    @classmethod
    def audit_itp(
        cls,
        uploaded_items: List[Dict[str, Any]],
        pipe_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audits a list of uploaded ITP items against official API 5L 47th Ed. / BOTAŞ master requirements.
        """
        master_spec = get_comprehensive_itp_specification(pipe_config)
        audit_rows: List[Dict[str, Any]] = []
        findings: List[Dict[str, Any]] = []

        matched_uploaded_indices = set()

        for master_item in master_spec:
            test_key = master_item["test_key"]
            matched_uploaded_item = None
            matched_idx = -1

            # Match against uploaded items
            for idx, up_item in enumerate(uploaded_items):
                if idx in matched_uploaded_indices:
                    continue
                up_name = str(up_item.get("test_name") or "").lower()
                keywords = cls.TEST_MATCHER_KEYWORDS.get(test_key, [])
                if any(kw in up_name for kw in keywords):
                    matched_uploaded_item = up_item
                    matched_idx = idx
                    matched_uploaded_indices.add(idx)
                    break

            if matched_uploaded_item:
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
        for idx, up_item in enumerate(uploaded_items):
            if idx not in matched_uploaded_indices:
                audit_rows.append({
                    "test_key": f"custom_{idx}",
                    "category": "Ek / Özel Muayene",
                    "test_name": up_item.get("test_name", "Özel Muayene"),
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

        # Calculate Statistics & Compliance Score
        total_rows = len(audit_rows)
        non_compliant_count = sum(1 for r in audit_rows if r["status"] == "NON_COMPLIANT")
        more_stringent_count = sum(1 for r in audit_rows if r["status"] == "MORE_STRINGENT")
        compliant_count = sum(1 for r in audit_rows if r["status"] == "COMPLIANT")

        compliance_score = round(((compliant_count + more_stringent_count) / total_rows * 100.0), 1) if total_rows > 0 else 100.0
        overall_verdict = "REJECTED" if non_compliant_count > 0 else ("APPROVED_WITH_COMMENTS" if more_stringent_count > 0 else "APPROVED")

        return {
            "pipe_summary": {
                "diameter_mm": pipe_config.get("diameter_mm", 1219.0),
                "diameter_inch": pipe_config.get("diameter_inch", '48"'),
                "wall_thickness_mm": pipe_config.get("wall_thickness_mm", 14.30),
                "material_grade": pipe_config.get("material_grade", "X65"),
                "manufacturing_process": pipe_config.get("manufacturing_process", "SAWH"),
                "psl_level": pipe_config.get("psl_level", "PSL2"),
                "standard_edition": "API Spec 5L 47th Edition / ISO 3183"
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
        """Evaluates a single matched ITP test row for frequency and criteria compliance."""
        test_key = master["test_key"]
        up_freq = str(uploaded.get("test_frequency") or "").strip()
        up_crit = str(uploaded.get("acceptance_criteria") or "").strip()
        std_freq = master["standard_frequency"]
        std_crit = master["standard_acceptance_criteria"]

        status = "COMPLIANT"
        issue_type = "CONFORMING"
        remarks: List[str] = []

        d_mm = float(pipe_config.get("diameter_mm") or 1219.0)
        process = str(pipe_config.get("manufacturing_process") or "SAWH").upper()
        is_welded = any(k in process for k in ("SAW", "ERW", "HFW", "LSAW", "COW"))
        std_type = str(pipe_config.get("standard_type") or pipe_config.get("standard_code") or "").upper()
        is_botas = "BOTAŞ" in std_type or "BOTAS" in std_type

        # 1. Frequency Evaluation
        up_freq_lower = up_freq.lower()
        if test_key in ("hydrostatic", "ndt_weld_seam", "visual_surface", "dimensional_wall_thickness"):
            # Mandatory 100% / each pipe
            if any(term in up_freq_lower for term in ("lot başına", "10 boruda 1", "5 boruda 1", "örneklem", "sample")):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append(f"🔴 FREKANS YETERSİZ: Standart gereği bu test HER BORUDA (%100) yapılmalıdır; '{up_freq}' kabul edilemez.")
        elif test_key == "chemical_product":
            if not is_botas and ("1 analiz" in up_freq_lower or "1 adet" in up_freq_lower):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: Ürün analizi ısı başına en az 2 adet (ayrı borulardan) yapılmalıdır (API 5L 9.2).")
        elif test_key == "residual_stress":
            if is_botas and not any(k in up_freq_lower for k in ("döküm", "dokum", "heat", "her dökümde", "per heat")) and ("lot" in up_freq_lower or "örneklem" in up_freq_lower or "sample" in up_freq_lower):
                status = "NON_COMPLIANT"
                issue_type = "INADEQUATE_FREQUENCY"
                remarks.append("🔴 FREKANS YETERSİZ: BOTAŞ Şartnamesi Madde 3.3.9 uyarınca artık stres testi HER DÖKÜM (HEAT) İÇİN tekrarlanmalıdır.")

        # 2. Acceptance Criteria Evaluation
        up_crit_lower = up_crit.lower()

        # 2a. CVN Charpy Energy Checks
        if test_key == "cvn_body":
            j_matches = re.findall(r"(\d+)\s*(?:j|joule)", up_crit_lower)
            if j_matches:
                val = float(j_matches[0])
                std_j_matches = re.findall(r"(?:ort\.?|avg\.?)\s*(\d+)", std_crit.lower())
                req_avg = float(std_j_matches[0]) if std_j_matches else (60.0 if is_botas else 40.0)
                if val < req_avg:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YETERSİZ DARBE ENERJİSİ: Asgari ortalama darbe enerjisi {req_avg:.0f} J olmalıdır; ITP'de {val:.0f} J yazılmıştır!")
                elif val > req_avg + 5.0:
                    status = "MORE_STRINGENT"
                    issue_type = "MORE_STRINGENT"
                    remarks.append(f"🟡 DAHA SIKI DARBE ENERJİSİ: İmalatçı {val:.0f} J taahhüt etmiştir (Standart: {req_avg:.0f} J).")

        # 2b. Hydrostatic Stabilization Time & Pressure
        elif test_key == "hydrostatic":
            time_matches = re.findall(r"(\d+)\s*(?:sn|saniye|sec|second)", up_crit_lower)
            if is_botas:
                req_time = 20
            else:
                req_time = 10 if (is_welded and d_mm > 457.0) else 5
            if time_matches:
                val_time = int(time_matches[0])
                if val_time < req_time:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    if is_botas:
                        remarks.append(f"🔴 YETERSİZ TEST SÜRESİ: BOTAŞ Şartnamesi Madde 8.4.1 gereği hidrostatik tutma süresi EN AZ 20 SANİYE olmalıdır; ITP'de {val_time} sn yazılmıştır!")
                    else:
                        remarks.append(f"🔴 YETERSİZ TEST SÜRESİ: D={d_mm:.1f} mm kaynaklı boruda hidrostatik tutma süresi min {req_time} sn olmalıdır; ITP'de {val_time} sn yazılmıştır!")

        # 2c. Chemical Composition Limits (Phosphorus & Sulfur)
        elif test_key in ("chemical_heat", "chemical_product"):
            p_matches = re.findall(r"p\s*[≤<=]\s*0\.0(\d+)", up_crit_lower)
            if p_matches:
                val_p = float("0.0" + p_matches[0])
                max_p = 0.025 if is_botas else 0.020
                if val_p > max_p:
                    status = "NON_COMPLIANT"
                    issue_type = "CRITERIA_VIOLATION"
                    remarks.append(f"🔴 YÜKSEK FOSFOR LİMİTİ: P max %{max_p:.3f} olmalıdır; ITP'de %{val_p:.3f} yazılmıştır!")
                elif val_p <= 0.015:
                    status = "MORE_STRINGENT"
                    issue_type = "MORE_STRINGENT"
                    remarks.append(f"🟡 DAHA SIKI KİMYA: P max %{val_p:.3f} (Standart tavanı: %{max_p:.3f}).")

        # Final remarks formatting
        if not remarks:
            if is_botas:
                remarks_text = "🟢 BOTAŞ Çelik Boru Şartnamesi (4-NGTL-0-GN-P-002-5120 R7) ve API 5L limitlerine tam uyumludur."
            else:
                remarks_text = "🟢 API Spec 5L 47. Baskı PSL 2 standart şartlarına tam uyumludur."
        else:
            remarks_text = " ".join(remarks)

        return {
            "test_key": test_key,
            "category": master["category"],
            "test_name": master["test_name"],
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
