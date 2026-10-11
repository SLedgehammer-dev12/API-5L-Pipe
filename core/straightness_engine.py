"""
Pipe Straightness, Full-Length Sweep / Camber, and End Straightness (Deviation)
Calculation & Verification Engine.

Conforms to:
- API Spec 5L (46th & 47th Editions) Clause 9.11.3 (Tolerances for straightness), Table 12
- API Spec 5L Clause 10.2.8.3 (Inspection of straightness)
- BOTAŞ Petroleum Pipeline Corporation Specification Clauses 5.5 & 8.1.2.4
"""

import math
from typing import Any, Dict, List, Optional


class StraightnessEngine:
    @staticmethod
    def calculate_straightness(
        diameter_mm: float,
        wall_thickness_mm: float,
        pipe_length_m: float = 12.0,
        standard_code: str = "BOTAŞ",
        material_grade: str = "X65",
        manufacturing_process: str = "SAWH",
        total_straightness_actual_mm: Optional[float] = None,
        end_straightness_left_actual_mm: Optional[float] = None,
        end_straightness_right_actual_mm: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculates maximum allowable full-length straightness deviation (sweep/camber)
        and pipe end chord deviation (within 1.0 m) per API 5L Clause 9.11.3 and BOTAŞ 8.1.2.4.
        Verifies actual measurements and produces station profiles for 2D/3D visualization and QA/QC reporting.
        """
        try:
            D = float(diameter_mm)
            t = float(wall_thickness_mm)
            L = float(pipe_length_m)
        except (TypeError, ValueError):
            raise ValueError("Straightness inputs D, t and L must be numeric.")
        if not D > 0.0:
            raise ValueError("diameter_mm must be > 0.")
        if not t > 0.0:
            raise ValueError("wall_thickness_mm must be > 0.")
        if not L > 0.0:
            raise ValueError("pipe_length_m must be > 0.")
        L_mm = L * 1000.0
        grade = str(material_grade or "X65").upper().strip()
        proc = str(manufacturing_process or "SAWH").upper().strip()
        std = str(standard_code or "BOTAŞ").upper().strip()
        is_botas = "BOTAŞ" in std or "BOTAS" in std

        # ---------------------------------------------------------------------
        # 1. Full-Length Total Straightness Deviation (API 5L 9.11.3.1 & BOTAŞ 5.5)
        # ---------------------------------------------------------------------
        # API 5L Clause 9.11.3.1: Total deviation <= 0.2 % of pipe length (0.002 * L)
        # BOTAŞ 5120 R7 Clause 5.5: Tightened limit <= 0.1 % of pipe length (0.0010 * L)
        if is_botas:
            total_ratio = 0.0010  # 0.10%
            total_ratio_pct = 0.10
            total_std_ref = "BOTAŞ 5.5 / 8.1.2.4 (≤ %0,10 × L)"
        else:
            total_ratio = 0.0020  # 0.20%
            total_ratio_pct = 0.20
            total_std_ref = "API Spec 5L 9.11.3.1 / Tablo 12 (≤ %0,20 × L)"

        total_straightness_max_limit_mm = round(total_ratio * L_mm, 2)

        # ---------------------------------------------------------------------
        # 2. Pipe End Straightness Deviation within 1.0 m (API 5L 9.11.3.2 & BOTAŞ 8.1.2.4)
        # ---------------------------------------------------------------------
        # API 5L Clause 9.11.3.2: Max deviation at each end for 1.0 m (3.0 ft) <= 4.0 mm
        # BOTAŞ Clause 8.1.2.4: Max deviation at each end for 1.0 m <= 3.0 mm
        end_chord_length_m = 1.00
        end_chord_length_mm = 1000.0

        if is_botas:
            end_straightness_max_limit_mm = 3.00
            end_std_ref = "BOTAŞ 8.1.2.4 (1,0 m uç mesafesinde ≤ 3,00 mm)"
        else:
            end_straightness_max_limit_mm = 4.00
            end_std_ref = "API Spec 5L 9.11.3.2 (1,0 m uç mesafesinde ≤ 4,00 mm)"

        # ---------------------------------------------------------------------
        # 3. Measurement Stations & Simulated Coordinate Profiles (0 to L)
        # ---------------------------------------------------------------------
        # 7 canonical QA/QC inspection stations along pipe axis
        stations: List[Dict[str, Any]] = [
            {"station": "Boru Sol Uç (Bevel A)", "x_m": 0.0, "location_type": "end_a"},
            {"station": "Sol Uç Mastar Sınırı (1.0 m Chord)", "x_m": 1.0, "location_type": "chord_a"},
            {"station": "Çeyrek Boy (L / 4)", "x_m": round(L * 0.25, 2), "location_type": "quarter"},
            {"station": "Boru Orta Noktası (L / 2 - Tepe Sehim)", "x_m": round(L * 0.50, 2), "location_type": "midspan"},
            {"station": "Üç Çeyrek Boy (3L / 4)", "x_m": round(L * 0.75, 2), "location_type": "three_quarter"},
            {"station": "Sağ Uç Mastar Sınırı (L - 1.0 m Chord)", "x_m": round(L - 1.0, 2), "location_type": "chord_b"},
            {"station": "Boru Sağ Uç (Bevel B)", "x_m": round(L, 2), "location_type": "end_b"},
        ]

        # Use actual total deflection if supplied, otherwise nominal demo (e.g. 40% of max allowed)
        demo_act_f = float(total_straightness_actual_mm) if total_straightness_actual_mm is not None else round(total_straightness_max_limit_mm * 0.42, 2)

        for st in stations:
            x = st["x_m"]
            # Parabolic envelope: y(x) = 4 * f * (x/L) * (1 - x/L)
            parabolic_factor = 4.0 * (x / L) * (1.0 - (x / L))
            st["allowed_envelope_mm"] = round(total_straightness_max_limit_mm * parabolic_factor, 2)
            st["simulated_deviation_mm"] = round(demo_act_f * parabolic_factor, 2)

        # ---------------------------------------------------------------------
        # 4. QA/QC Evaluation & Verification Checks
        # ---------------------------------------------------------------------
        checks: List[Dict[str, Any]] = []
        is_compliant = True

        # Check 1: Total Straightness (Tam Boy Düzlük / Sweep)
        c1_stat = "NOT_EVALUATED"
        if total_straightness_actual_mm is not None:
            if total_straightness_actual_mm <= total_straightness_max_limit_mm:
                c1_stat = "PASS"
            else:
                c1_stat = "FAIL"
                is_compliant = False

        checks.append({
            "parameter": "Tam Boy Düzlük Sapması (Total Sweep / Camber)",
            "nominal": 0.0,
            "max_allowed": total_straightness_max_limit_mm,
            "actual": total_straightness_actual_mm,
            "unit": "mm",
            "status": c1_stat,
            "criteria": f"≤ {total_straightness_max_limit_mm:.2f} mm (%{total_ratio_pct:.2f} × L)",
            "clause": total_std_ref,
        })

        # Check 2: Left End Straightness (Sol Uç 1.0 m Mastar Sapması)
        c2_stat = "NOT_EVALUATED"
        if end_straightness_left_actual_mm is not None:
            if end_straightness_left_actual_mm <= end_straightness_max_limit_mm:
                c2_stat = "PASS"
            else:
                c2_stat = "FAIL"
                is_compliant = False

        checks.append({
            "parameter": "Sol Uç Düzlük Sapması (Left End Chord ≤ 1.0 m)",
            "nominal": 0.0,
            "max_allowed": end_straightness_max_limit_mm,
            "actual": end_straightness_left_actual_mm,
            "unit": "mm",
            "status": c2_stat,
            "criteria": f"≤ {end_straightness_max_limit_mm:.2f} mm",
            "clause": end_std_ref,
        })

        # Check 3: Right End Straightness (Sağ Uç 1.0 m Mastar Sapması)
        c3_stat = "NOT_EVALUATED"
        if end_straightness_right_actual_mm is not None:
            if end_straightness_right_actual_mm <= end_straightness_max_limit_mm:
                c3_stat = "PASS"
            else:
                c3_stat = "FAIL"
                is_compliant = False

        checks.append({
            "parameter": "Sağ Uç Düzlük Sapması (Right End Chord ≤ 1.0 m)",
            "nominal": 0.0,
            "max_allowed": end_straightness_max_limit_mm,
            "actual": end_straightness_right_actual_mm,
            "unit": "mm",
            "status": c3_stat,
            "criteria": f"≤ {end_straightness_max_limit_mm:.2f} mm",
            "clause": end_std_ref,
        })

        # Determine overall verdict
        has_actuals = any(x is not None for x in [
            total_straightness_actual_mm,
            end_straightness_left_actual_mm,
            end_straightness_right_actual_mm
        ])

        if not has_actuals:
            verdict = "NOMINAL (DENETİME HAZIR)"
            verdict_class = "text-indigo-600 bg-indigo-50"
        elif is_compliant:
            verdict = "UYGUN (KABUL / PASS)"
            verdict_class = "text-emerald-700 bg-emerald-50"
        else:
            verdict = "RED (UYGUNSUZ / REJECT)"
            verdict_class = "text-red-700 bg-red-50"

        # Methodology description
        methodology_note = (
            f"Ölçüm Yöntemi (API 5L 10.2.8.3 & BOTAŞ 8.1.2.4):\n"
            f"1. Tam Boy Düzlük: Boru eksenine paralel gerdirilen çelik piyano teli (taut wire) veya lazer kolimatör ışını "
            f"ile boru gövdesi arasındaki maksimum aralık (sehim) ölçülür. L={L:.1f} m için üst sınır: {total_straightness_max_limit_mm:.2f} mm.\n"
            f"2. Uç Düzlüğü: Her iki boru ucunda (Bevel A ve Bevel B) 1,0 m boyundaki hassas çelik mastar (straight edge) "
            f"boru yüzeyine teğet oturtularak fener mastarı / sentil ile maksimum boşluk kontrol edilir. Üst sınır: {end_straightness_max_limit_limit_mm if 'end_straightness_max_limit_limit_mm' in locals() else end_straightness_max_limit_mm:.2f} mm."
        )

        return {
            "diameter_mm": D,
            "wall_thickness_mm": t,
            "material_grade": grade,
            "manufacturing_process": proc,
            "standard_code": std,
            "pipe_length_m": L,
            "pipe_length_mm": L_mm,
            "is_botas": is_botas,
            # Straightness limit metrics
            "total_straightness_ratio_pct": total_ratio_pct,
            "total_straightness_max_limit_mm": total_straightness_max_limit_mm,
            "total_straightness_clause": total_std_ref,
            "end_chord_length_m": end_chord_length_m,
            "end_straightness_max_limit_mm": end_straightness_max_limit_mm,
            "end_straightness_clause": end_std_ref,
            # Actual values
            "total_straightness_actual_mm": total_straightness_actual_mm,
            "end_straightness_left_actual_mm": end_straightness_left_actual_mm,
            "end_straightness_right_actual_mm": end_straightness_right_actual_mm,
            # Inspection stations & profiles
            "stations": stations,
            "methodology_note": methodology_note,
            "checks": checks,
            "verdict": verdict,
            "verdict_class": verdict_class,
            "is_compliant": is_compliant,
        }
