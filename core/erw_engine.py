"""
ERW / HFW (Electric Resistance Welded / High Frequency Induction Welded)
Pipe Manufacturing Geometry, Skelp Sizing, Flash Trimming, and Flattening Test Engine.

Conforms to:
- API Spec 5L (46th & 47th Editions) Clause 8.4, 9.11.3.2, 10.2.4.3, 10.2.5.3, Table 16
- BOTAŞ Petroleum Pipeline Corporation Specification Clauses 3.2.1, 3.3.3
"""

import math
from typing import Any, Dict, Optional


def get_erw_deformation_factor(material_grade: str) -> float:
    """
    Returns API Spec 5L Clause 10.2.4.3 flattening test deformation factor 'e'.

    API 5L Equation 10.2.4.3:
    - Grade A25: e = 0.09
    - Grade A:   e = 0.08
    - Grade B:   e = 0.08 (L245)
    - X42:       e = 0.08 (L290)
    - X46:       e = 0.07 (L320)
    - X52:       e = 0.07 (L360)
    - X56:       e = 0.06 (L390)
    - X60:       e = 0.06 (L415)
    - X65:       e = 0.06 (L450)
    - X70:       e = 0.05 (L485)
    - X80:       e = 0.04 (L555)
    """
    g = str(material_grade or "").upper().replace("GRADE", "").strip()
    if "80" in g:
        return 0.04
    if "70" in g:
        return 0.05
    if any(k in g for k in ("65", "60", "56")):
        return 0.06
    if any(k in g for k in ("52", "46")):
        return 0.07
    if any(k in g for k in ("42", "B", "245", "290")):
        return 0.08
    if "A25" in g:
        return 0.09
    return 0.07  # safe engineering default


class ErwEngine:
    @staticmethod
    def calculate_erw_geometry(
        diameter_mm: float,
        wall_thickness_mm: float,
        material_grade: str = "X52",
        psl_level: str = "PSL2",
        pipe_length_m: float = 12.0
    ) -> Dict[str, Any]:
        """
        Calculates ERW/HFW strip width, upset squeeze allowance, flash trimming limits,
        API 5L Clause 10.2.4.3 flattening test heights (H, 0.33D, 2t), and seam heat treatment.
        """
        D = float(max(21.3, diameter_mm))
        t = float(max(1.5, wall_thickness_mm))
        L = float(max(1.0, pipe_length_m))
        grade = str(material_grade or "X52").upper().strip()
        psl = str(psl_level or "PSL2").upper().strip()

        D_mid = max(1.0, D - t)
        C_mid = math.pi * D_mid  # theoretical formed neutral circumference

        # Squeeze allowance / upset metal (metal displaced during high-frequency forging):
        # Typically 1.25t to 1.50t for pipeline steels, nominal ~1.35t
        delta_upset = 1.35 * t

        # Skelp (coiled hot-rolled strip) ordered width
        W_skelp = C_mid + delta_upset

        # Gross slitting width (edge trimming margin: ~7.5 mm per edge)
        W_gross = W_skelp + 15.0

        # Weights
        # Pipe nominal mass per meter (API 5L Barlow mass: 0.02466 * t * (D - t))
        mass_pipe_kg_m = 0.02466 * t * (D - t)
        pipe_total_mass_kg = mass_pipe_kg_m * L

        # Skelp mass per meter (steel density 7850 kg/m^3)
        mass_skelp_kg_m = 7850.0 * 1e-6 * W_skelp * t
        upset_loss_kg_m = max(0.0, mass_skelp_kg_m - mass_pipe_kg_m)
        upset_loss_percent = (upset_loss_kg_m / mass_skelp_kg_m * 100.0) if mass_skelp_kg_m > 0 else 0.0

        # API 5L Clause 9.11.3.2 & Table 16: Flash Trimming Limits
        # Outside flash: Trimmed flush with pipe contour (max height <= 0.0 mm; underfill/groove <= 0.15 mm)
        flash_outside_max_mm = 0.00
        flash_outside_desc = "Boru dış yüzeyi ile hemzemin traşlanmalı (kalan yükseklik ≤ 0.00 mm, oyuk ≤ 0.15 mm)"

        # Inside flash (API 5L Table 16 / Clause 9.11.3.2):
        # Normal ERW: <= 0.38 mm (or agreement <= 0.50 mm)
        if t <= 7.5:
            flash_inside_max_mm = 0.38
        else:
            flash_inside_max_mm = 0.50
        flash_inside_desc = f"API 5L Tablo 16: İç çapak kesilmiş olmalı (Maksimum yükseklik ≤ {flash_inside_max_mm:.2f} mm)"

        # ---------------------------------------------------------------
        # API Spec 5L Clause 10.2.4.3 & BOTAŞ 3.3.3: Flattening Test (H)
        # ---------------------------------------------------------------
        e_factor = get_erw_deformation_factor(grade)

        # Equation 10.2.4.3: H = ((1 + e) * t) / (e + t / D)
        t_over_D = t / D
        H_weld_mm = ((1.0 + e_factor) * t) / (e_factor + t_over_D)

        # Stage 2: Ductility limit (H_duct = 0.33 * D)
        H_ductility_mm = 0.33 * D

        # Stage 3: Soundness / Full flattening (H_sound = 2 * t)
        H_soundness_mm = 2.0 * t

        # Minimum ring test specimen length per API 5L 10.2.4.3 (>= 50 mm, typically 60 mm)
        specimen_length_mm = 60.0

        # Seam Normalizing Heat Treatment (API 5L 10.2.5.3 & BOTAŞ 3.2.1)
        temp_normalizing_min = 720.0
        temp_normalizing_nominal = 920.0  # Above Ac3 for complete austenitization & fine grain
        seam_treatment_desc = (
            "API 5L 10.2.5.3 & BOTAŞ 3.2.1: PSL2 borularda kaynak dikişi on-line indüksiyon ile "
            "en az 720°C (nominal 900-950°C Ac3 üzeri) tam normalize edilmeli ve havada soğutulmalıdır."
        )

        return {
            "diameter_mm": round(D, 2),
            "wall_thickness_mm": round(t, 2),
            "material_grade": grade,
            "psl_level": psl,
            "pipe_length_m": round(L, 2),
            "mean_diameter_mm": round(D_mid, 2),
            "circumference_mid_mm": round(C_mid, 2),
            "upset_allowance_mm": round(delta_upset, 2),
            "skelp_width_net_mm": round(W_skelp, 2),
            "skelp_width_gross_mm": round(W_gross, 2),
            "pipe_mass_kg_m": round(mass_pipe_kg_m, 2),
            "pipe_total_mass_kg": round(pipe_total_mass_kg, 1),
            "skelp_mass_kg_m": round(mass_skelp_kg_m, 2),
            "upset_loss_kg_m": round(upset_loss_kg_m, 2),
            "upset_loss_percent": round(upset_loss_percent, 2),
            # Flash Trimming (API 5L Table 16)
            "flash_outside_max_mm": flash_outside_max_mm,
            "flash_outside_desc": flash_outside_desc,
            "flash_inside_max_mm": flash_inside_max_mm,
            "flash_inside_desc": flash_inside_desc,
            # Flattening Test (API 5L 10.2.4.3)
            "deformation_factor_e": e_factor,
            "flattening_h_mm": round(H_weld_mm, 2),
            "flattening_ductility_h_mm": round(H_ductility_mm, 2),
            "flattening_soundness_h_mm": round(H_soundness_mm, 2),
            "flattening_specimen_len_mm": specimen_length_mm,
            "stages": [
                {
                    "stage": 1,
                    "title": "Aşama 1: Kaynak Dikişi Açılması ve Çatlak Kontrolü",
                    "target_height_mm": round(H_weld_mm, 2),
                    "formula": "H = (1 + e)·t / (e + t/D)",
                    "seam_position": "Saat 9 veya Saat 3 (90° Maksimum Gerilme Konumu)",
                    "criterion": "Plakalar H mesafesine inene kadar kaynakta hiçbir çatlak veya açılma olmamalıdır."
                },
                {
                    "stage": 2,
                    "title": "Aşama 2: Boru Gövdesi Süneklik Sınırı Kontrolü",
                    "target_height_mm": round(H_ductility_mm, 2),
                    "formula": "H_duct = 0.33 · D",
                    "seam_position": "Saat 9 veya Saat 3 Konumu Korunur",
                    "criterion": "Plakalar 0.33D mesafesine inene kadar boru gövdesinde (saat 12 ve 6 noktalarında) çatlama olmamalıdır."
                },
                {
                    "stage": 3,
                    "title": "Aşama 3: Tam Ezilme ve Sac Yapı Kusurları (Katmer) Kontrolü",
                    "target_height_mm": round(H_soundness_mm, 2),
                    "formula": "H_sound = 2 · t",
                    "seam_position": "İç Cidarlar Birbirine Değene Kadar",
                    "criterion": "Plakalar 2t mesafesinde temas edene kadar gövdede katmer, laminasyon veya yanmış metal parçalanması olmamalıdır."
                }
            ],
            # Heat Treatment (API 5L 10.2.5.3)
            "normalizing_temp_min_c": temp_normalizing_min,
            "normalizing_temp_nominal_c": temp_normalizing_nominal,
            "seam_heat_treatment_rule": seam_treatment_desc
        }
