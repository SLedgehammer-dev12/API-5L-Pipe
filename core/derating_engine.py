"""
Pipe Wall Thickness Underflow (Minus Tolerance), Barlow Design Pressure Derating,
and Hydrostatic Hoop Stress Verification Engine.

Conforms to:
- API Spec 5L (46th & 47th Editions) Clause 9.11.2 (Tolerances for wall thickness), Table 11
- API Spec 5L Clause 9.4 & 10.2.6 (Hydrostatic test pressure & hoop stress limit <= 90-95% SMYS)
- ASME B31.8 (Gas Transmission and Distribution Piping Systems) Section 841.1 (Steel Pipe Design)
- BOTAŞ Petroleum Pipeline Corporation Specification Clauses 3.3.7, 5.5, 8.1.2.4
"""

import math
from typing import Any, Dict, List, Optional


class DeratingEngine:
    @staticmethod
    def get_wall_thickness_tolerances(
        diameter_mm: float,
        wall_thickness_mm: float,
        manufacturing_process: str = "SAWH",
        is_botas: bool = True
    ) -> Dict[str, float]:
        """
        Determines the positive and negative wall thickness tolerances (% and mm)
        per API Spec 5L Table 11 and BOTAŞ Specification.
        """
        D = float(max(21.3, diameter_mm))
        t = float(max(1.5, wall_thickness_mm))
        proc = str(manufacturing_process or "SAWH").upper().strip()
        is_smls = "SMLS" in proc or "SEAMLESS" in proc

        if is_smls:
            # Seamless Pipe (API 5L Table 11)
            if t < 4.0:
                tol_pos_pct = 15.0
                tol_neg_pct = -12.5
            elif t < 10.0:
                tol_pos_pct = 15.0
                tol_neg_pct = -12.5
            elif t < 25.0:
                tol_pos_pct = 12.5
                tol_neg_pct = -12.5
            else:
                tol_pos_pct = 10.0
                tol_neg_pct = -10.0
        else:
            # Welded Pipe (SAWH, SAWL, HFW/ERW, COW)
            if is_botas:
                # BOTAŞ Clause 8.1.2.4 tightened tolerance for gas line pipe
                if t >= 15.0:
                    tol_pos_pct = 10.0
                    tol_neg_pct = -8.0
                else:
                    tol_pos_pct = 10.0
                    tol_neg_pct = -10.0
            else:
                # API 5L Table 11 standard
                if t <= 5.0:
                    tol_pos_pct = 10.0
                    tol_neg_pct = -10.0
                elif t < 15.0:
                    tol_pos_pct = 10.0
                    tol_neg_pct = -10.0
                else:
                    tol_pos_pct = 10.0
                    tol_neg_pct = -8.0

        tol_pos_mm = round((tol_pos_pct / 100.0) * t, 3)
        tol_neg_mm = round((tol_neg_pct / 100.0) * t, 3)
        t_min = round(t + tol_neg_mm, 3)  # tol_neg_mm is negative
        t_max = round(t + tol_pos_mm, 3)

        return {
            "tol_pos_pct": tol_pos_pct,
            "tol_neg_pct": tol_neg_pct,
            "tol_pos_mm": tol_pos_mm,
            "tol_neg_mm": tol_neg_mm,
            "t_min_allowed_mm": t_min,
            "t_max_allowed_mm": t_max,
        }

    @staticmethod
    def calculate_derating(
        diameter_mm: float,
        wall_thickness_mm: float,
        material_grade: str = "X65",
        manufacturing_process: str = "SAWH",
        standard_code: str = "BOTAŞ",
        design_factor_f: float = 0.72,
        corrosion_allowance_mm: float = 0.0,
        smys_mpa: Optional[float] = None,
        design_pressure_bar: Optional[float] = None,
        hydro_test_pressure_bar: Optional[float] = None,
        pipe_length_m: float = 12.0,
        actual_measured_thickness_mm: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates wall thickness underflow limits, Barlow internal pressure capacity loss,
        hydrostatic hoop stress jump at minimum allowable thickness, linear mass variance,
        and assesses safety margin compliance.
        """
        D = float(max(21.3, diameter_mm))
        t = float(max(1.5, wall_thickness_mm))
        grade = str(material_grade or "X65").upper().strip()
        proc = str(manufacturing_process or "SAWH").upper().strip()
        std = str(standard_code or "BOTAŞ").upper().strip()
        is_botas = "BOTAŞ" in std or "BOTAS" in std
        F = float(max(0.3, min(0.8, design_factor_f)))
        CA = float(max(0.0, corrosion_allowance_mm))
        L = float(max(1.0, pipe_length_m))

        # Default SMYS from grade if not supplied
        if smys_mpa is None or smys_mpa <= 0:
            from core.database import get_smys_info
            g_info = get_smys_info(grade)
            S = float(g_info.get("yield_min_mpa", 450.0))
        else:
            S = float(smys_mpa)

        # Tolerances
        tols = DeratingEngine.get_wall_thickness_tolerances(D, t, proc, is_botas)
        t_min = tols["t_min_allowed_mm"]
        t_max = tols["t_max_allowed_mm"]
        tol_neg_pct = tols["tol_neg_pct"]
        tol_pos_pct = tols["tol_pos_pct"]

        # ---------------------------------------------------------------------
        # 1. Barlow Design Pressure (ASME B31.8 / API 5L)
        # P = (2 * S * t / D) * F * E * T (bar = MPa * 10)
        # E = 1.0 (DSAW/SAWH/SAWL/ERW/SMLS), T = 1.0 (<= 121 °C)
        # ---------------------------------------------------------------------
        # Nominal design pressure (without CA derating and with CA)
        p_des_nom_no_ca_bar = round(((2.0 * S * t) / D) * F * 10.0, 2)
        t_eff_nom = max(0.5, t - CA)
        p_des_nom_bar = round(((2.0 * S * t_eff_nom) / D) * F * 10.0, 2)

        # Derated design pressure based on minimum allowable wall thickness (t_min)
        t_eff_min = max(0.5, t_min - CA)
        p_des_min_bar = round(((2.0 * S * t_eff_min) / D) * F * 10.0, 2)

        # Pressure Capacity Loss (Derating)
        delta_p_des_bar = round(p_des_nom_bar - p_des_min_bar, 2)
        derating_loss_pct = round((delta_p_des_bar / p_des_nom_bar) * 100.0, 2) if p_des_nom_bar > 0 else 0.0

        # If user supplied a specific operating/design pressure, check hoop stresses
        op_press_bar = float(design_pressure_bar) if design_pressure_bar and design_pressure_bar > 0 else p_des_nom_bar

        # Operating Hoop Stresses (sigma_h = P * D / (2 * t))
        sigma_op_nom_mpa = round((op_press_bar / 10.0) * D / (2.0 * t), 2)
        sigma_op_min_mpa = round((op_press_bar / 10.0) * D / (2.0 * t_min), 2)
        hoop_util_nom_pct = round((sigma_op_nom_mpa / S) * 100.0, 2)
        hoop_util_min_pct = round((sigma_op_min_mpa / S) * 100.0, 2)

        # ---------------------------------------------------------------------
        # 2. Hydrostatic Factory Mill Test Hoop Stress (API 5L Clause 10.2.6.7)
        # Standard: 90% SMYS for API 5L, 95% SMYS for BOTAŞ high pressure
        # ---------------------------------------------------------------------
        if hydro_test_pressure_bar is None or hydro_test_pressure_bar <= 0:
            hydro_stress_factor = 0.95 if is_botas else 0.90
            p_hydro_nom_bar = round(((2.0 * S * t) / D) * hydro_stress_factor * 10.0, 2)
        else:
            p_hydro_nom_bar = float(hydro_test_pressure_bar)

        # Hoop stress at nominal vs t_min during hydrotest
        sigma_hydro_nom_mpa = round((p_hydro_nom_bar / 10.0) * D / (2.0 * t), 2)
        sigma_hydro_min_mpa = round((p_hydro_nom_bar / 10.0) * D / (2.0 * t_min), 2)
        hydro_smys_nom_pct = round((sigma_hydro_nom_mpa / S) * 100.0, 2)
        hydro_smys_min_pct = round((sigma_hydro_min_mpa / S) * 100.0, 2)
        hydro_stress_jump_pct = round(hydro_smys_min_pct - hydro_smys_nom_pct, 2)

        # Hydrotest limit: API 5L 10.2.6.7 max 95% (standard) or 100% (alternative)
        hydro_max_allowed_smys_pct = 95.0 if is_botas else 90.0
        is_hydro_stress_critical = hydro_smys_min_pct > 100.0

        # ---------------------------------------------------------------------
        # 3. Steel Mass & Weight Variance (kg/m and total pipe kg)
        # Formula: w = 0.0246615 * (D - t) * t (API 5L 9.11.3)
        # ---------------------------------------------------------------------
        w_factor = 0.0246615
        mass_nom_kg_m = round(w_factor * (D - t) * t, 2)
        mass_min_kg_m = round(w_factor * (D - t_min) * t_min, 2)
        mass_max_kg_m = round(w_factor * (D - t_max) * t_max, 2)

        mass_nom_pipe_kg = round(mass_nom_kg_m * L, 1)
        mass_min_pipe_kg = round(mass_min_kg_m * L, 1)
        mass_max_pipe_kg = round(mass_max_kg_m * L, 1)

        mass_loss_per_pipe_kg = round(mass_nom_pipe_kg - mass_min_pipe_kg, 1)
        mass_variance_pct = round(((mass_min_kg_m - mass_nom_kg_m) / mass_nom_kg_m) * 100.0, 2)

        # ---------------------------------------------------------------------
        # 4. Actual Measurement Evaluation (if provided)
        # ---------------------------------------------------------------------
        t_act = actual_measured_thickness_mm
        checks: List[Dict[str, Any]] = []
        is_compliant = True

        # Check 1: Thickness within tolerance band [t_min, t_max]
        c1_stat = "NOT_EVALUATED"
        if t_act is not None:
            if t_min <= t_act <= t_max:
                c1_stat = "PASS"
            else:
                c1_stat = "FAIL"
                is_compliant = False

        checks.append({
            "parameter": "Et Kalınlığı Tolerans Aralığı (Wall Thickness Band)",
            "nominal": t,
            "min_allowed": t_min,
            "max_allowed": t_max,
            "actual": t_act,
            "unit": "mm",
            "status": c1_stat,
            "criteria": f"{t_min:.2f} mm — {t_max:.2f} mm (%{tol_neg_pct:+.1f} / %{tol_pos_pct:+.1f})",
            "clause": "API 5L Tablo 11 & BOTAŞ 8.1.2.4",
        })

        # Check 2: Hydrotest Hoop Stress Jump (Advisory / Engineering Warning for Mill Test)
        c2_stat = "PASS" if not is_hydro_stress_critical else "WARNING"

        checks.append({
            "parameter": "Alt Sınırda Hidrostatik Gerilme (Hydro Stress at t_min)",
            "nominal": hydro_smys_nom_pct,
            "min_allowed": 0.0,
            "max_allowed": 100.0,
            "actual": hydro_smys_min_pct,
            "unit": "% SMYS",
            "status": c2_stat,
            "criteria": f"≤ %100.0 SMYS (Nominalde: %{hydro_smys_nom_pct:.1f} SMYS)",
            "clause": "API 5L Madde 10.2.6.7 & BOTAŞ 3.3.7",
        })

        # Check 3: Design Pressure Derating Loss
        # Warning if derating capacity loss exceeds 10%
        c3_stat = "PASS" if derating_loss_pct <= 12.0 else "WARNING"
        checks.append({
            "parameter": "Tasarım Basıncı Kapasite İndirgemesi (Derating Loss)",
            "nominal": p_des_nom_bar,
            "min_allowed": p_des_min_bar,
            "max_allowed": p_des_nom_bar,
            "actual": p_des_min_bar,
            "unit": "bar",
            "status": c3_stat,
            "criteria": f"İndirgenmiş: {p_des_min_bar:.1f} bar (Kayıp: -{delta_p_des_bar:.1f} bar / -%{derating_loss_pct:.1f})",
            "clause": "ASME B31.8 Madde 841.1 & API 5L 9.4",
        })

        if t_act is None:
            verdict = "NOMINAL (DENETİME HAZIR)"
            verdict_class = "text-indigo-600 bg-indigo-50"
        elif is_compliant:
            verdict = "UYGUN (KABUL / PASS)"
            verdict_class = "text-emerald-700 bg-emerald-50"
        else:
            verdict = "RED (UYGUNSUZ / REJECT)"
            verdict_class = "text-red-700 bg-red-50"

        methodology_note = (
            f"Tolerans ve İndirgeme Değerlendirmesi (API 5L Tablo 11 & ASME B31.8):\n"
            f"1. Eksi Tolerans Alt Sınırı: Nominal et kalınlığı {t:.2f} mm olan boruda %{tol_neg_pct:.1f} eksi tolerans "
            f"ile minimum cidar t_min = {t_min:.2f} mm olarak gerçekleşebilir.\n"
            f"2. Tasarım Basıncı İndirgemesi: Borunun alt toleransta üretilmesi durumunda güvenli tasarım basıncı "
            f"{p_des_nom_bar:.1f} bar'dan {p_des_min_bar:.1f} bar'a geriler (-{delta_p_des_bar:.1f} bar / -%{derating_loss_pct:.1f}).\n"
            f"3. Hidrostatik Gerilme Sıçraması: Fabrika hidrostatik test basıncında ({p_hydro_nom_bar:.1f} bar) çeper gerilmesi "
            f"%{hydro_smys_nom_pct:.1f} SMYS'den %{hydro_smys_min_pct:.1f} SMYS'ye yükselir (+%{hydro_stress_jump_pct:.1f} artış)."
        )

        return {
            "diameter_mm": D,
            "wall_thickness_mm": t,
            "material_grade": grade,
            "manufacturing_process": proc,
            "standard_code": std,
            "is_botas": is_botas,
            "smys_mpa": S,
            "design_factor_f": F,
            "corrosion_allowance_mm": CA,
            "pipe_length_m": L,
            # Tolerances
            "tol_pos_pct": tol_pos_pct,
            "tol_neg_pct": tol_neg_pct,
            "tol_pos_mm": tols["tol_pos_mm"],
            "tol_neg_mm": tols["tol_neg_mm"],
            "t_min_allowed_mm": t_min,
            "t_max_allowed_mm": t_max,
            # Barlow Design Pressures
            "p_des_nom_no_ca_bar": p_des_nom_no_ca_bar,
            "p_des_nom_bar": p_des_nom_bar,
            "p_des_min_bar": p_des_min_bar,
            "delta_p_des_bar": delta_p_des_bar,
            "derating_loss_pct": derating_loss_pct,
            # Operating Stresses
            "operating_pressure_bar": op_press_bar,
            "sigma_op_nom_mpa": sigma_op_nom_mpa,
            "sigma_op_min_mpa": sigma_op_min_mpa,
            "hoop_util_nom_pct": hoop_util_nom_pct,
            "hoop_util_min_pct": hoop_util_min_pct,
            # Hydrostatic Stresses
            "hydro_test_pressure_bar": p_hydro_nom_bar,
            "sigma_hydro_nom_mpa": sigma_hydro_nom_mpa,
            "sigma_hydro_min_mpa": sigma_hydro_min_mpa,
            "hydro_smys_nom_pct": hydro_smys_nom_pct,
            "hydro_smys_min_pct": hydro_smys_min_pct,
            "hydro_stress_jump_pct": hydro_stress_jump_pct,
            "is_hydro_stress_critical": is_hydro_stress_critical,
            # Mass & Weight
            "mass_nom_kg_m": mass_nom_kg_m,
            "mass_min_kg_m": mass_min_kg_m,
            "mass_max_kg_m": mass_max_kg_m,
            "mass_nom_pipe_kg": mass_nom_pipe_kg,
            "mass_min_pipe_kg": mass_min_pipe_kg,
            "mass_max_pipe_kg": mass_max_pipe_kg,
            "mass_loss_per_pipe_kg": mass_loss_per_pipe_kg,
            "mass_variance_pct": mass_variance_pct,
            # Actual & Verification
            "actual_measured_thickness_mm": t_act,
            "checks": checks,
            "verdict": verdict,
            "verdict_class": verdict_class,
            "is_compliant": is_compliant,
            "methodology_note": methodology_note,
        }
