"""
API 5L PSL2 & BOTAŞ Pipe QA/QC & Factory Acceptance Test (FAT) Calculation Engine.
Calculates all dimensional, mechanical, chemical, destructive/non-destructive tests,
safety factors and attaches engineering remarks / standard references for every parameter.
"""

import math
from typing import Any, Dict, Optional

from core.database import (
    compute_api5l_tolerances,
    default_design_pressure_for_factor,
    get_api5l_yt_ratio,
    get_chemical_rules,
    get_cvn,
    get_cvn_specimen_size,
    get_pipe_size_by_inch,
    get_pipe_size_by_mm,
    get_smys_info,
    parse_design_factor,
)
from core.edition_notes import build_edition_notes

# Table 21 (47th Ed.): (D_max_mm, t_min for 12.7 mm round bar, t_min for 8.9 mm round bar).
# A round bar is used for transverse tensile tests of welded pipe; Axc = 130 mm² (12.7/8.9 mm bar)
# or 65 mm² (6.4 mm bar).
_TABLE21_ROUNDBAR = [
    (219.1, None, 28.1), (273.1, 36.1, 25.5), (323.9, 33.5, 23.9), (355.6, 32.3, 23.2),
    (406.4, 30.9, 22.2), (457.0, 29.7, 21.5), (508.0, 28.8, 21.0), (559.0, 28.1, 20.5),
    (610.0, 27.5, 20.1), (660.0, 27.0, 19.8), (711.0, 26.5, 19.5), (762.0, 26.2, 19.3),
    (813.0, 25.8, 19.1), (864.0, 25.5, 18.9), (914.0, 25.3, 18.7), (965.0, 25.1, 18.6),
    (1016.0, 24.9, 18.5), (1067.0, 24.7, 18.3), (1118.0, 24.5, 18.2), (1168.0, 24.4, 18.1),
    (1219.0, 24.2, 18.1), (1321.0, 24.0, 17.9), (1422.0, 23.8, 17.8), (1524.0, 23.6, 17.6),
    (1626.0, 23.4, 17.5), (1727.0, 23.3, 17.4), (1829.0, 23.1, 17.4), (1930.0, 23.0, 17.3),
    (float("inf"), 22.9, 17.2),
]


def _round_bar_axc(d_mm: float, t_mm: float) -> float:
    """Axc (mm²) for transverse round-bar tensile test pieces (Table 21)."""
    d, t = float(d_mm), float(t_mm)
    t12 = t89 = None
    for d_max, a, b in _TABLE21_ROUNDBAR:
        if d <= d_max:
            t12, t89 = a, b
            break
    if t12 is not None and t >= t12:
        return 130.0
    if t89 is not None and t >= t89:
        return 130.0
    return 65.0


def _elongation_axc(d_mm: float, t_mm: float, manufacturing_process: str) -> float:
    """Applicable tensile test piece cross-sectional area (Axc, mm²) for the elongation formula."""
    d, t = float(d_mm), float(t_mm)
    proc = (manufacturing_process or "").upper()
    is_smls = "SMLS" in proc or "SEAMLESS" in proc or "DIKISSIZ" in proc
    if is_smls:
        area = math.pi * t * (d - t)
        return min(485.0, round(area, -1))
    if d >= 219.1:
        return _round_bar_axc(d, t)
    area = 38.1 * t
    return min(485.0, round(area, -1))

# Standard references and engineering explanations for every matrix row.
# Built per pipe via build_standard_explanations() so the text always matches
# the selected evaluation standard (BOTAŞ vs API 5L) and PSL level.
def build_standard_explanations(is_botas: bool = False, is_psl1: bool = False) -> dict:
    """Returns the {key: {tr, en}} explanation map for the given standard selection."""
    if is_psl1:
        grade_text = {
            'tr': 'API 5L PSL1 / ISO 3183 Çelik Kalitesi',
            'en': 'API 5L PSL1 / ISO 3183 Steel Grade'
        }
        chemical_text = {
            'tr': 'API 5L Çizelge 4 (PSL1 Kimyasal Bileşim Limitleri)',
            'en': 'API 5L Table 4 (PSL1 Chemical Composition Limits)'
        }
        yt_ratio_text = {
            'tr': 'API 5L PSL1 borularda Y/T oranı limiti yoktur',
            'en': 'No Y/T ratio limit for API 5L PSL1 pipe'
        }
        hardness_text = {
            'tr': 'API 5L Madde 9.10.6 (PSL1: Yalnız 50 mm üzeri sert nokta kontrolü; 35 HRC / 345 HV10 / 327 HBW üzeri defekttir)',
            'en': 'API 5L Cl. 9.10.6 (PSL1: hard-spot testing only for spots > 50 mm; above 35 HRC / 345 HV10 / 327 HBW is a defect)'
        }
        dwtt_text = {
            'tr': 'API 5L PSL1 borularda DWTT zorunlu değildir (Çizelge 19)',
            'en': 'DWTT not mandatory for API 5L PSL1 pipe (Table 19)'
        }
        cvn_text = {
            'tr': 'API 5L PSL1 borularda Çentik Darbe (CVN) zorunlu değildir (Çizelge 17)',
            'en': 'Charpy V-Notch Impact (CVN) not mandatory for API 5L PSL1 pipe (Table 17)'
        }
    else:
        if is_botas:
            grade_text = {
                'tr': 'BOTAŞ Şartnamesi / API 5L PSL2 Çelik Mukavemet Sınıfı',
                'en': 'BOTAŞ Spec / API 5L PSL2 Steel Strength Grade'
            }
            chemical_text = {
                'tr': 'BOTAŞ Şartnamesi Tablo 1 (Kimyasal Bileşim Limitleri)',
                'en': 'BOTAŞ Spec Table 1 (Chemical Composition Limits)'
            }
            yt_ratio_text = {
                'tr': 'BOTAŞ Şartnamesi (Y/T oranı: X65 ve üzeri ≤ 0.90 soğuk genişletilmemiş / ≤ 0.93 genişletilmiş)',
                'en': 'BOTAŞ Spec (Y/T ratio: X65 and above ≤ 0.90 unexpanded / ≤ 0.93 cold-expanded)'
            }
            hardness_text = {
                'tr': 'BOTAŞ Şartnamesi Madde 3.3.7 (Maksimum 300 HV10; aşılırsa dökümdeki boruların %100\'ü test edilir)',
                'en': 'BOTAŞ Spec Cl. 3.3.7 (Maximum 300 HV10; if exceeded, 100% of the heat is tested)'
            }
            dwtt_text = {
                'tr': 'BOTAŞ Şartnamesi Madde 3.3.6 (D ≥ 508 mm\'de 0 °C\'de zorunlu; ortalama ≥ %85, tekil ≥ %60)',
                'en': 'BOTAŞ Spec Cl. 3.3.6 (mandatory at 0 °C for D ≥ 508 mm; average ≥ 85%, single ≥ 60%)'
            }
            cvn_text = {
                'tr': 'BOTAŞ Tablo 3 (Gövde ve Kaynak Çentik Darbe Tokluğu - CVN -20°C)',
                'en': 'BOTAŞ Table 3 (Body & Weld Charpy V-Notch Toughness - CVN -20°C)'
            }
        else:
            grade_text = {
                'tr': 'API 5L PSL2 / ISO 3183 Çelik Mukavemet Sınıfı',
                'en': 'API 5L PSL2 / ISO 3183 Steel Strength Grade'
            }
            chemical_text = {
                'tr': 'API 5L Çizelge 5 (PSL2 Kimyasal Bileşim Ürün Analizi Limitleri)',
                'en': 'API 5L Table 5 (PSL2 Chemical Composition Product Analysis Limits)'
            }
            yt_ratio_text = {
                'tr': 'API 5L Çizelge 7 (Maksimum Akma/Çekme Oranı Sınırı)',
                'en': 'API 5L Table 7 (Maximum Yield-to-Tensile Ratio Limit)'
            }
            hardness_text = {
                'tr': 'API 5L Madde 10.2.4.8 (Maksimum Sertlik Sınırı: 300 HV10 / 250 HV)',
                'en': 'API 5L Cl. 10.2.4.8 (Maximum Hardness Limit: 300 HV10 / 250 HV)'
            }
            dwtt_text = {
                'tr': 'API 5L Madde 9.9 & Çizelge 20 (D ≥ 508 mm kaynaklı hat borusunda zorunlu; ortalama ≥ %85, tekil ≥ %60)',
                'en': 'API 5L Cl. 9.9 & Table 20 (mandatory for welded line pipe D ≥ 508 mm; average ≥ 85%, single ≥ 60%)'
            }
            cvn_text = {
                'tr': 'API 5L Çizelge 8 (Gövde ve Kaynak Çentik Darbe Tokluğu - CVN 0°C)',
                'en': 'API 5L Table 8 (Body & Weld Charpy V-Notch Toughness - CVN 0°C)'
            }
    if is_botas:
        wall_thickness_tol_text = {
            'tr': 'BOTAŞ Şartnamesi (İmalat Et Kalınlığı Sabit Düşümleri: t<8.71 → -0.04 / t<12.71 → -0.10 / diğer → -0.15 mm)',
            'en': 'BOTAŞ Spec (Manufacturing Wall Thickness Fixed Deductions: t<8.71 → -0.04 / t<12.71 → -0.10 / else → -0.15 mm)'
        }
        residual_stress_text = {
            'tr': 'BOTAŞ Şartnamesi Madde 3.3.9: Delta = 12.566*Dₘ²*Yield*0.1 / (E*t), Dₘ = D-t (Artık Gerilme Halka Açılması)',
            'en': 'BOTAŞ Spec Cl. 3.3.9: Delta = 12.566*Dm²*Yield*0.1 / (E*t), Dm = D-t (Residual Stress Ring Test)'
        }
        peaking_text = {
            'tr': 'BOTAŞ Şartnamesi & API 5L Madde 9.10.5.1 (Boru Ucu Tepeleşme Azami Geometrik Sapma: 3.2 mm)',
            'en': 'BOTAŞ Spec & API 5L Cl. 9.10.5.1 (Pipe End Peaking Max Geometric Deviation: 3.2 mm)'
        }
        diameter_tol_text = {
            'tr': 'BOTAŞ Şartnamesi Çizelge 4 (Boru Ucu ve Gövde Dış Çap Toleransları - sabit limitler)',
            'en': 'BOTAŞ Spec Table 4 (Pipe End & Body Diameter Tolerances - fixed limits)'
        }
        circumference_tol_text = {
            'tr': 'BOTAŞ Şartnamesi Çizelge 4 (Çap Toleransı x Pi / Çevre Ölçüm Bandı)',
            'en': 'BOTAŞ Spec Table 4 (Diameter Tolerance x Pi / Circumferential Tape)'
        }
        ovality_text = {
            'tr': 'BOTAŞ Şartnamesi Çizelge 4 (Boru Ucu ve Gövde Ovalite Sabit Sınırları; büyük çaplarda anlaşmaya bağlı)',
            'en': 'BOTAŞ Spec Table 4 (Pipe End & Body Out-of-Roundness Fixed Limits; by agreement for large diameters)'
        }
        radial_offset_text = {
            'tr': 'BOTAŞ Şartnamesi (API 5L Çizelge 14/Ek E değerlerinin 0.75 katsayılı hali: t<15 → 1.125 / t<25 → 0.075*t / t≥25 → 1.875 mm)',
            'en': 'BOTAŞ Spec (0.75 factor on API 5L Table 14/Annex E: t<15 → 1.125 / t<25 → 0.075*t / t≥25 → 1.875 mm)'
        }
        weld_height_text = {
            'tr': 'BOTAŞ Şartnamesi (İç/Dış Kaynak Takviyesi 0.75 katsayılı: iç 2.625 mm; dış 3.375 mm (t>13) / 2.625 mm)',
            'en': 'BOTAŞ Spec (I/O weld reinforcement with 0.75 factor: inside 2.625 mm; outside 3.375 mm (t>13) / 2.625 mm)'
        }
        misalignment_text = {
            'tr': 'BOTAŞ Şartnamesi (Kaynak Hiza Kaçıklığı 0.75 katsayılı: t>20 → 3.0 / t≤20 → 2.25 mm)',
            'en': 'BOTAŞ Spec (Weld misalignment with 0.75 factor: t>20 → 3.0 / t≤20 → 2.25 mm)'
        }
        hydro_text = {
            'tr': 'ASME B31.8 & BOTAŞ Madde 8.4 (Barlow: P = 2*S*t / D; min test basıncı = P_max - 2.0 Bar, SMYS %100)',
            'en': 'ASME B31.8 & BOTAŞ Cl. 8.4 (Barlow: P = 2*S*t / D; min test pressure = P_max - 2.0 bar, 100% SMYS)'
        }
        api_std_test_text = {
            'tr': 'API 5L Madde 9.3.1 / Çizelge 26 (karşılaştırma amaçlı; BOTAŞ\'ta alt sınır P_max - 2.0 Bar)',
            'en': 'API 5L Cl. 9.3.1 / Table 26 (for reference; BOTAŞ minimum is P_max - 2.0 bar)'
        }
        smys_text = {
            'tr': 'BOTAŞ Şartnamesi Tablo 2 / API 5L Çizelge 7 (Belirtilmiş Minimum Akma Mukavemeti - SMYS)',
            'en': 'BOTAŞ Spec Table 2 / API 5L Table 7 (Specified Minimum Yield Strength - SMYS)'
        }
        yield_tensile_text = {
            'tr': 'BOTAŞ Şartnamesi Tablo 2 (Akma ve Çekme Dayanım Aralıkları)',
            'en': 'BOTAŞ Spec Table 2 (Yield & Tensile Strength Ranges)'
        }
        weld_repair_text = {
            'tr': 'BOTAŞ Şartnamesi Madde 9.1 & Ek C (Tek Tamir Max 150 mm; uçta 300 mm yasak; >X52 & t>10mm 100°C ön ısıtma)',
            'en': 'BOTAŞ Spec Cl. 9.1 & Annex C (single repair max 150 mm; 300 mm end ban; 100°C preheat for >X52 & t>10mm)'
        }
        mandrel_jaw_text = {
            'tr': 'BOTAŞ Şartnamesi / API 5L Madde 9.10.2 (Kılavuzlu Bükme Mandrel Çapı ve Çene Açıklığı)',
            'en': 'BOTAŞ Spec / API 5L Cl. 9.10.2 (Guided-Bend Mandrel Diameter & Jaw Opening)'
        }
        squareness_text = {
            'tr': 'BOTAŞ Şartnamesi Çizelge 4 (Boru Ucu Diklikten Sapma: Max 1.6 mm)',
            'en': 'BOTAŞ Spec Table 4 (Pipe End Out-of-Squareness: Max 1.6 mm)'
        }
        design_factor_text = {
            'tr': 'BOTAŞ Şartnamesi (Tasarım Faktörü F: 0.72 Hat / 0.60 Hat / 0.50 Hat-İstasyon)',
            'en': 'BOTAŞ Spec (Design Factor F: 0.72 Line / 0.60 Line / 0.50 Line-Station)'
        }
        wall_thickness_text = {
            'tr': 'BOTAŞ Standart Et Kalınlığı Matrisi (Şartname çizelgesi)',
            'en': 'BOTAŞ Standard Thickness Matrix (Spec table)'
        }
    else:
        wall_thickness_tol_text = {
            'tr': 'API 5L Çizelge 11 (İmalat Et Kalınlığı Toleransı: SMLS ve kaynaklı proses kırılımlı)',
            'en': 'API 5L Table 11 (Manufacturing Wall Thickness Tolerances: SMLS vs welded process bands)'
        }
        residual_stress_text = {
            'tr': 'API 5L şartnamesinde halka-açılma artık stres testi yoktur; bu satır yalnız BOTAŞ boruları içindir',
            'en': 'No ring-opening residual stress test in API 5L; this row applies to BOTAŞ pipe only'
        }
        peaking_text = {
            'tr': 'API 5L Madde 9.11.3.4 & 9.10.5.1 (Tepeleşme ölçümü 0.25D/200 mm şablon; azami geometrik sapma 3.2 mm)',
            'en': 'API 5L Cl. 9.11.3.4 & 9.10.5.1 (peaking measured with 0.25D/200 mm template; max geometric deviation 3.2 mm)'
        }
        diameter_tol_text = {
            'tr': 'API 5L Çizelge 10 (Boru Ucu ve Gövde Dış Çap Toleransları - D\'ye ve SMLS/kaynaklı prosesine bağlı)',
            'en': 'API 5L Table 10 (Pipe End & Body Diameter Tolerances - depend on D and SMLS/welded process)'
        }
        circumference_tol_text = {
            'tr': 'API 5L Çizelge 10 (Çap Toleransı x Pi / Çevre Ölçüm Bandı)',
            'en': 'API 5L Table 10 (Diameter Tolerance x Pi / Circumferential Tape)'
        }
        ovality_text = {
            'tr': 'API 5L Madde 9.11.3.3 / Çizelge 10 (Ovalite: D≤610 → uç %1.5D / gövde %2.0D; D>610 → uç 0.010D / gövde 0.015D; D/t>75 anlaşmaya bağlı)',
            'en': 'API 5L Cl. 9.11.3.3 / Table 10 (Out-of-roundness: D≤610 → end 1.5%D / body 2.0%D; D>610 → end 0.010D / body 0.015D; D/t>75 by agreement)'
        }
        radial_offset_text = {
            'tr': 'API 5L Çizelge 14 & Ek E (Radyal Kaçıklık: t<15 → 1.5 / t<25 → 0.1*t / t≥25 → 2.5 mm)',
            'en': 'API 5L Table 14 & Annex E (Radial Offset: t<15 → 1.5 / t<25 → 0.1*t / t≥25 → 2.5 mm)'
        }
        weld_height_text = {
            'tr': 'API 5L Çizelge 16 & Madde 9.13.3 (İç Kaynak Takviyesi 3.5 mm; dış 4.5 mm (t>13) / 3.5 mm)',
            'en': 'API 5L Table 16 & Cl. 9.13.3 (Inside weld reinforcement 3.5 mm; outside 4.5 mm (t>13) / 3.5 mm)'
        }
        misalignment_text = {
            'tr': 'API 5L Ek E & Madde 9.13.3 (Kaynak Hiza Kaçıklığı: t>20 → 4.0 / t≤20 → 3.0 mm)',
            'en': 'API 5L Annex E & Cl. 9.13.3 (Weld Misalignment: t>20 → 4.0 / t≤20 → 3.0 mm)'
        }
        hydro_text = {
            'tr': 'ASME B31.8 & API 5L Madde 9.3 (Barlow: P = 2*S*t / D)',
            'en': 'ASME B31.8 & API 5L Cl. 9.3 (Barlow: P = 2*S*t / D)'
        }
        api_std_test_text = {
            'tr': 'API 5L Madde 9.3.1 / Çizelge 26 (Standart Fabrika Hidrostatik Deney Basıncı Katsayıları)',
            'en': 'API 5L Cl. 9.3.1 / Table 26 (Standard Mill Hydrostatic Test Pressure Factors)'
        }
        smys_text = {
            'tr': 'API 5L Çizelge 7 (Belirtilmiş Minimum Akma Mukavemeti - SMYS)',
            'en': 'API 5L Table 7 (Specified Minimum Yield Strength - SMYS)'
        }
        yield_tensile_text = {
            'tr': 'API 5L Çizelge 7 (Mekanik Çekme ve Akma Dayanım Aralıkları)',
            'en': 'API 5L Table 7 (Mechanical Tensile & Yield Strength Limits)'
        }
        weld_repair_text = {
            'tr': 'API 5L Ek C (Tek Tamir Kaynağı Max 150 mm ve >X52 & t>10mm için 100°C Ön Isıtma)',
            'en': 'API 5L Annex C (Single Repair Weld Max 150 mm & 100°C Preheat for >X52 & t>10mm)'
        }
        mandrel_jaw_text = {
            'tr': 'API 5L Madde 9.10.2 (Kılavuzlu Bükme Mandrel Çapı ve Çene Açıklığı)',
            'en': 'API 5L Cl. 9.10.2 (Guided-Bend Mandrel Diameter & Jaw Opening)'
        }
        squareness_text = {
            'tr': 'API 5L Madde 9.11.3.5 (Boru Ucu Diklikten Sapma Toleransı: Max 1.6 mm)',
            'en': 'API 5L Cl. 9.11.3.5 (Pipe End Out-of-Squareness Tolerance: Max 1.6 mm)'
        }
        design_factor_text = {
            'tr': 'ASME B31.8 Çizelge 841.1.6-1 (Tasarım Faktörü F)',
            'en': 'ASME B31.8 Table 841.1.6-1 (Design Factor F)'
        }
        wall_thickness_text = {
            'tr': 'ASME B31.8 Madde 841.1.1 & Kullanıcı Seçimi (Et Kalınlığı)',
            'en': 'ASME B31.8 Cl. 841.1.1 & User Selection (Wall Thickness)'
        }
    return {
    'diameter': {
        'tr': 'API 5L Madde 9.11.3 / BOTAŞ Çizelge 4 (Boru Anma Çapı ve Dış Çap OD)',
        'en': 'API 5L Cl. 9.11.3 / BOTAŞ Table 4 (Nominal Pipe Size & Outside Diameter OD)'
    },
    'design_factor': design_factor_text,
    'wall_thickness': wall_thickness_text,
    'process': {
        'tr': 'API 5L Madde 6.1 (SAWH: Helisel Tozaltı, ERW: Yüksek Frekans Direnç, SMLS: Dikişsiz)',
        'en': 'API 5L Cl. 6.1 (SAWH: Spiral Submerged Arc, ERW: Electric Resistance, SMLS: Seamless)'
    },
    'grade': grade_text,
    'smys': smys_text,
    'chemical': chemical_text,
    'wall_thickness_tol': wall_thickness_tol_text,
    'yield_tensile': yield_tensile_text,
    'hydro_test': hydro_text,
    'api_std_test': api_std_test_text,
    'diameter_tol': diameter_tol_text,
    'circumference_tol': circumference_tol_text,
    'ovality': ovality_text,
    'elongation': {
        'tr': 'API 5L Madde 9.3.2 Formülü: e = 1940 * A^0.2 / U^0.9 (Minimum Uzama %)',
        'en': 'API 5L Cl. 9.3.2 Formula: e = 1940 * A^0.2 / U^0.9 (Min. Elongation %)'
    },
    'radial_offset': radial_offset_text,
    'weld_height': weld_height_text,
    'misalignment': misalignment_text,
    'cvn': cvn_text,
    'yt_ratio': yt_ratio_text,
    'residual_stress': residual_stress_text,
    'dwtt': dwtt_text,
    'hardness': hardness_text,
    'mandrel_jaw': mandrel_jaw_text,
    'flattening': {
        'tr': 'API 5L Madde 9.10.1 (ERW Borularda Düzleştirme/Yassıltma Testi Kriterleri)',
        'en': 'API 5L Cl. 9.10.1 (Flattening Test Criteria for ERW Line Pipe)'
    },
    'peaking': peaking_text,
    'squareness': squareness_text,
    'weld_repair': weld_repair_text,
    'weight': {
        'tr': 'API 5L Madde 9.11.2 (W = 0.02466 * t * (D - t) kg/m; Min -%3.5, Max +%10)',
        'en': 'API 5L Cl. 9.11.2 (W = 0.02466 * t * (D - t) kg/m; Min -3.5%, Max +10%)'
    },
    'fracture_control': {
        'tr': 'ASME B31.8 Madde 841.1.2 & API 5L Annex G (D > 14" ve Gerilme > %40 SMYS için Kırılma Kontrolü)',
        'en': 'ASME B31.8 Cl. 841.1.2 & API 5L Annex G (Fracture Control for D > 14" & Stress > 40% SMYS)'
    },
    'thick_wall_alt': {
        'tr': 'ASME B31.8 Madde 841.1.1 (D/t < 30 Kalın Etli Boru Alternatif Basınç Tasarım Formülü)',
        'en': 'ASME B31.8 Cl. 841.1.1 (D/t < 30 Thick Wall Pipe Alternative Design Pressure Formula)'
    }
    }


# Legacy alias: default (API 5L PSL2) explanation map for backward compatibility.
STANDARD_EXPLANATIONS = build_standard_explanations()

class PipeQAQCEngine:
    @staticmethod
    def calculate_pipe_qc(
        diameter_inch: str,
        diameter_mm: Optional[float] = None,
        wall_thickness_mm: Optional[float] = None,
        design_factor_str: str = "0.72 (Hat)",
        material_grade: Optional[str] = None,
        manufacturing_process: str = "SAWH",
        standard_type: str = "BOTAŞ",
        design_pressure_bar: Optional[float] = None,
        psl_level: str = "PSL2",
        delivery_condition: str = "M"
    ) -> Dict[str, Any]:
        """
        Executes complete QA/QC inspection and design calculation for a single pipe configuration.
        Dynamically applies BOTAŞ specification tables or API 5L PSL1/PSL2 rules (47th Ed.).
        """
        # 1. Resolve Nominal Diameter (NPS) and Actual Outside Diameter (OD mm)
        pipe_size = get_pipe_size_by_inch(diameter_inch)
        if pipe_size:
            d_mm = float(pipe_size['mm'])
            d_inch = diameter_inch if (diameter_inch and str(diameter_inch).strip()) else pipe_size['inch']
        elif diameter_mm:
            pipe_size = get_pipe_size_by_mm(diameter_mm)
            d_mm = float(diameter_mm)
            d_inch = diameter_inch if (diameter_inch and str(diameter_inch).strip()) else (pipe_size['inch'] if pipe_size else f"{round(d_mm / 25.4, 1)}\"")
        else:
            d_inch = "48\""
            d_mm = 1219.0
            pipe_size = get_pipe_size_by_inch(d_inch)

        # 2. BOTAŞ vs API 5L Logic for Default Material and Wall Thickness
        std_upper = standard_type.upper().strip()
        is_botas_mode = ("BOTAŞ" in std_upper or "BOTAS" in std_upper)
        is_api_mode = "API" in std_upper
        is_psl1 = psl_level and "PSL1" in str(psl_level).upper()
        delivery = (delivery_condition or "M").upper()

        # Map design factor (tolerates comma/dot decimal separators and Turkish labels)
        factor_key, f_factor = parse_design_factor(design_factor_str)

        # Determine Material Grade
        if is_botas_mode and (not material_grade or material_grade.strip() == ""):
            # Pick from BOTAŞ standard table
            grade_clean = pipe_size['default_material'] if pipe_size else "X65"
        elif material_grade:
            grade_clean = material_grade.upper().strip()
        else:
            grade_clean = pipe_size['default_material'] if (pipe_size and is_botas_mode) else "X65"

        # Determine Wall Thickness (t)
        t = wall_thickness_mm
        if (t is None or t <= 0) and is_botas_mode and pipe_size:
            botas_thk_val = pipe_size['botas_thk'].get(factor_key, 0.0)
            if botas_thk_val > 0:
                t = botas_thk_val
            else:
                # Fallback to standard station thickness if hat is None for small diameters
                t = pipe_size['botas_thk'].get('0.50_ist1', 14.30)

        if t is None or t <= 0:
            t = 14.30

        # Check BOTAŞ compliance of selected thickness
        botas_req_thk = pipe_size['botas_thk'].get(factor_key, 0.0) if pipe_size else 0.0
        botas_thickness_status = "UYGUN"
        if is_botas_mode and botas_req_thk > 0:
            if t < (botas_req_thk - 0.01):
                botas_thickness_status = f"BOTAŞ Şartından Düşük (Gereken: {botas_req_thk} mm)"

        # Delivery-condition / process validation (API 5L Table 3)
        validation_warning = ""
        if is_api_mode and not is_psl1 and delivery == "M" and "SMLS" in (manufacturing_process or "").upper():
            validation_warning = "M teslim koşulu yalnız kaynaklı boruya aittir (Tablo 3); SMLS geçerli değildir."

        # 3. Material & SMYS Properties
        smys_info = get_smys_info(grade_clean, psl_level)
        smys_psi = smys_info['smys_psi']
        yield_min_mpa = smys_info['yield_min_mpa']
        yield_max_psi = smys_info['yield_max_psi']
        yield_max_mpa = smys_info['yield_max_mpa']
        tensile_min_psi = smys_info['tensile_min_psi']
        tensile_min_mpa = smys_info['tensile_min_mpa']
        tensile_max_psi = smys_info['tensile_max_psi']
        tensile_max_mpa = smys_info['tensile_max_mpa']
        # Y/T ratio: API PSL2 -> Table 7 (47th Ed.); BOTAŞ / PSL1 -> table values (0 = no limit)
        if is_api_mode and not is_psl1:
            yt_max = get_api5l_yt_ratio(grade_clean, delivery)
        else:
            yt_max = smys_info['yield_tensile_max']
        cvn_info = get_cvn(grade_clean, standard_type, psl_level, d_mm, manufacturing_process)
        cvn_mat = cvn_info['material_j']
        cvn_weld = cvn_info['weld_j']
        cvn_required = cvn_info['required']
        strain_val = smys_info['strain_value']

        # 4. Chemical Composition Rules
        chem_rules = get_chemical_rules(
            grade_clean, standard_type, psl_level, delivery, manufacturing_process, t
        )
        chem_as_agreed = bool(chem_rules.get("as_agreed", False))

        # 5. Wall Thickness Tolerances
        proc_upper = manufacturing_process.upper()

        # Negative tolerance differs by standard:
        #   BOTAŞ  -> fixed small deductions (Excel 'Boru Seçim-Kontrol Aracı')
        #   API 5L -> Table 11 (process-specific)
        if is_botas_mode:
            if t < 8.71:
                t_min = round(t - 0.04, 2)
            elif t < 12.71:
                t_min = round(t - 0.10, 2)
            else:
                t_min = round(t - 0.15, 2)
        elif "SMLS" in proc_upper:
            # API 5L Table 11 — SMLS: -0.5 / -0.125t / -3.0 (or -0.1t)
            if t <= 4.0:
                t_min = round(t - 0.5, 2)
            elif t < 25.0:
                t_min = round(t - 0.125 * t, 2)
            else:
                t_min = round(t - max(3.0, 0.1 * t), 2)
        else:
            # API 5L Table 11 — welded: -0.5 / -0.1t / -1.5
            if t <= 5.0:
                t_min = round(t - 0.5, 2)
            elif t < 15.0:
                t_min = round(t - 0.10 * t, 2)
            else:
                t_min = round(t - 1.5, 2)

        # Positive tolerance (same for BOTAŞ and API 5L)
        if "SMLS" in proc_upper:
            if t <= 4.0:
                t_max = round(t + 0.6, 2)
            elif t < 25.0:
                t_max = round(t * 1.15, 2)
            else:
                # Table 11: +3.7 or +0.1t, whichever is the greater
                t_max = round(t + max(3.7, 0.1 * t), 2)
        else:
            if t <= 5.0:
                t_max = round(t + 0.5, 2)
            elif t < 15.0:
                t_max = round(t * 1.10, 2)
            else:
                t_max = round(t + 1.5, 2)

        # 6. Hydrostatic Test Pressures (Barlow Formula)
        p_hydro_max = (2.0 * smys_psi * t) / (d_mm * 14.5037738)

        # API 5L Standard Test Pressure Factors (Table 26 / 10.2.6.4)
        # 47th Ed. Table 26: A/B -> 60 % any D; X42+ -> 60 % (D<=141.3), 75 % (<=219.1),
        # 85 % (<508), 90 % (>=508). Standard test pressure need not exceed 20.5 MPa
        # (17.0/19.0 MPa for A/B), see footnotes a)/b).
        if grade_clean in ("GRADE A", "GRADE B"):
            api_std_factor = 0.60
            cap_mpa = 17.0 if d_mm <= 88.9 else 19.0
        elif d_mm <= 141.3:
            api_std_factor = 0.60
            cap_mpa = 20.5
        elif d_mm < 219.2:
            api_std_factor = 0.75
            cap_mpa = 20.5
        elif d_mm < 508.0:
            api_std_factor = 0.85
            cap_mpa = 20.5
        else:
            api_std_factor = 0.90
            cap_mpa = 20.5

        api_std_test_press = min(p_hydro_max * api_std_factor, cap_mpa * 10.0)

        # Minimum required test pressure:
        #   BOTAŞ -> P_max - 2.0 bar (Excel 'Boru Seçim-Kontrol Aracı')
        #   API   -> the standard test pressure (10.2.6.4 / Table 26)
        if is_botas_mode:
            p_hydro_min = p_hydro_max - 2.0 if p_hydro_max > 0 else 0.0
        else:
            p_hydro_min = api_std_test_press

        # 7. Diameter & Circumference Tolerances (mm)
        api_tol = None
        if not is_botas_mode:
            api_tol = compute_api5l_tolerances(d_mm, t, manufacturing_process)

        if is_botas_mode and pipe_size and 'diameter_tol_botas' in pipe_size:
            d_end_max = pipe_size['diameter_tol_botas']['end_max']
            d_end_min = pipe_size['diameter_tol_botas']['end_min']
            d_body_max = pipe_size['diameter_tol_botas']['body_max']
            d_body_min = pipe_size['diameter_tol_botas']['body_min']
        elif not is_botas_mode and api_tol:
            d_end_max = api_tol['end_max']
            d_end_min = api_tol['end_min']
            d_body_max = api_tol['body_max']
            d_body_min = api_tol['body_min']
        else:
            d_end_max = d_mm + 1.6
            d_end_min = d_mm - 1.6
            d_body_max = d_mm + 4.0
            d_body_min = d_mm - 4.0

        circ_end_max = round(d_end_max * math.pi, 2) if isinstance(d_end_max, (int, float)) else d_end_max
        circ_end_min = round(d_end_min * math.pi, 2) if isinstance(d_end_min, (int, float)) else d_end_min
        circ_body_max = round(d_body_max * math.pi, 2) if isinstance(d_body_max, (int, float)) else d_body_max
        circ_body_min = round(d_body_min * math.pi, 2) if isinstance(d_body_min, (int, float)) else d_body_min

        if not is_botas_mode and api_tol:
            ovality_end = api_tol['ovality_end']
            ovality_body = api_tol['ovality_body']
        else:
            ovality_end = pipe_size['ovality']['end'] if pipe_size else "Anlaşmaya bağlıdır."
            ovality_body = pipe_size['ovality']['body'] if pipe_size else "18.3"

        # 8. Minimum Elongation (% e)
        # API 5L: e = 1940 * Axc^0.2 / U^0.9  (Table 7 footnote f)
        a_cross = _elongation_axc(d_mm, t, manufacturing_process)
        u_val = tensile_min_mpa if tensile_min_mpa > 0 else 535.0
        elongation_mat = 1940.0 * (math.pow(a_cross, 0.2)) / (math.pow(u_val, 0.9))
        elongation_weld = 10.0

        # Elongation for both specimen types when both are permitted (10.2.3.2.3):
        # welded pipe D >= 219.1 mm -> strip (Axc = 38.1 x t) or round bar (Table 21).
        _proc_u = (manufacturing_process or "").upper()
        _is_smls_here = "SMLS" in _proc_u or "SEAMLESS" in _proc_u or "DIKISSIZ" in _proc_u
        _tensile_dual = (not _is_smls_here) and d_mm >= 219.1
        if _is_smls_here:
            _strip_axc = min(485.0, round(math.pi * t * (d_mm - t), -1))  # full-section
        else:
            _strip_axc = min(485.0, round(38.1 * t, -1))                  # strip
        _round_axc = _round_bar_axc(d_mm, t)

        def _af(axc_val):
            return 1940.0 * (math.pow(axc_val, 0.2)) / (math.pow(u_val, 0.9))

        elongation_strip_pct = _af(_strip_axc)
        elongation_round_pct = _af(_round_axc)

        # CVN specimen size (API 5L Table 22) based on diameter AND wall thickness
        if not cvn_required:
            notch_specimen_size = "PSL1'de zorunlu değil"
        else:
            notch_specimen_size = get_cvn_specimen_size(d_mm, t)['label']

        # 9. Radial Offset, Weld Height, Misalignment
        # BOTAŞ applies a 0.75 reduction factor; API 5L uses the Table 14/16/9.13.3 base values.
        weld_k = 0.75 if is_botas_mode else 1.0
        if "SAWH" in proc_upper or "SAWL" in proc_upper:
            if t < 15.01:
                radial_offset = 1.5 * weld_k
            elif t < 25.01:
                radial_offset = 0.1 * weld_k * t
            else:
                radial_offset = 2.5 * weld_k

            weld_h_inside = 3.5 * weld_k
            weld_h_outside = 4.5 * weld_k if t > 13.0 else 3.5 * weld_k
            misalignment = 4.0 * weld_k if t > 20.0 else 3.0 * weld_k
            # Pipe end peaking: measured per 10.2.8.4 (template 0.25D or 200 mm);
            # acceptance per 9.10.5.1 (geometric deviation <= 3.2 mm).
            weld_peaking = 3.2
            weld_repair_single = min(d_mm * 0.2, 150.0)
        else:
            radial_offset = "Değer Yok"
            weld_h_inside = "Değer Yok"
            weld_h_outside = "Değer Yok"
            misalignment = "DEĞER YOK"
            weld_peaking = "Bu Ölçü Yok"
            weld_repair_single = "Değer Yok"

        pipe_end_squareness = 1.6

        # 10. Residual Stress Test Max (mm) (BOTAŞ Cl. 3.3.9 / Cl. 4.2)
        # Formula: S = (E * t * C) / (12.566 * D_mean^2) <= 0.10 * SMYS
        # where D_mean = D_outer - t (ring mean diameter), C = ring opening gap (delta)
        # Solving for max gap C_max: C_max = 12.566 * D_mean^2 * 0.10 * SMYS / (E * t)
        if "SAWH" in proc_upper:
            stress_coeff = yield_min_mpa if yield_min_mpa > 0 else 450.0
            d_mean = d_mm - t  # Ring mean diameter (D_outer - wall_thickness)
            residual_stress_max = (12.566 * math.pow(d_mean, 2) * stress_coeff * 0.1) / (200000.0 * t)
        else:
            residual_stress_max = "TEST YOK"

        # 11. DWTT (Drop Weight Tear Test - API 5L 9.9 / Table 20): welded pipe only, D >= 508 mm.
        is_welded = not ("SMLS" in proc_upper or "SEAMLESS" in proc_upper)
        if is_psl1:
            dwtt = "TEST YOK (PSL1)"  # PSL 1 has no DWT requirement (Table 19)
        else:
            dwtt = "Var" if (is_welded and d_mm >= 508.0) else "TEST YOK"

        # 12. Hardness & Bending (Mandrel & Jaw Opening)
        if is_psl1:
            # PSL 1: hardness is limited to hard-spot testing (Table 17 item 17 / 9.10.6).
            hardness_test = "Sadece sert nokta testi (9.10.6)"
        else:
            hardness_test = "300 HV"
        if "SAWH" in proc_upper and strain_val > 0:
            denom = ((strain_val * d_mm / t) - (2.0 * strain_val) - 1.0)
            if denom > 0:
                mandrel_dia = (1.15 * (d_mm - 2.0 * t) / denom) - t
            else:
                mandrel_dia = 200.0
            jaw_opening = mandrel_dia + 3.2 + (2.0 * t)
        else:
            mandrel_dia = "TEST YOK"
            jaw_opening = "TEST YOK"

        # 13. Flattening Test (ERW Pipes)
        if "ERW" in proc_upper or "HFW" in proc_upper:
            weld_open_h = d_mm * 0.66 if (smys_psi > 56600 and t > 12.69) else d_mm * 0.50
            mat_crack_h = d_mm * 0.33 if (d_mm / t > 10.0) else "Soruştur"
            # 47th Ed. 9.6 a)3): no lack of fusion / incomplete fusion in the weld / laminations
            lamination = ("Düzleştirme testinde karşı duvarlar değene kadar kaynakta füzyon eksikliği, "
                          "eksik nüfuziyet veya laminasyon bulunmayacaktır")
        else:
            weld_open_h = "TEST YOK"
            mat_crack_h = "TEST YOK"
            lamination = "TEST YOK"

        # 14. Weld Repair Preheat
        if smys_psi > 52000 and t > 10.0:
            repair_preheat = "100 C Ön Isıtma"
        else:
            repair_preheat = "Ön Isıtma Yok"

        # 15. Pipe Weights (kg/m) — API 5L 9.11.2: W = 0.0246615 * t * (D - t)
        weight_nom = t * 0.0246615 * (d_mm - t)
        weight_min = weight_nom * 0.965
        weight_max = weight_nom * 1.10

        # 16. Operating Pressure / SMYS & Fracture Control
        if design_pressure_bar and design_pressure_bar > 0:
            p_oper = float(design_pressure_bar)
        else:
            p_oper = default_design_pressure_for_factor(f_factor)

        oper_press_ratio = (p_oper / p_hydro_max) if p_hydro_max > 0 else 0.0

        # ASME B31.8 841.1.2 Fracture Control & Arrest (OD > 14" / 355.6 mm)
        d_inch_num = round(d_mm / 25.4, 2)
        if d_inch_num > 14.0:
            if oper_press_ratio > 0.40:
                fracture_control = "Brittle Fracture Control, API 5L Annex G ye Bakınız"
            else:
                fracture_control = "API 5L Annex G işlemine gerek yok"
        else:
            if oper_press_ratio > 0.80:
                fracture_control = "Brittle Fracture Control, API 5L Annex G ye Bakınız"
            else:
                fracture_control = "API 5L Annex G işlemine gerek yok"

        # 17. D/t Ratio and Alternative Design Pressure
        d_over_t = d_mm / t
        if d_over_t < 30.0:
            design_formula_alt = "Alternatif Basınç Dizayn Hesabı Kullanılabilir"
            alt_design_press = (2.0 * smys_psi * t / ((d_mm - t) * 14.5037738)) * f_factor
        else:
            design_formula_alt = "Normal Basınç Dizayn Hesabı"
            alt_design_press = "Hesaplamaya Gerek Yok"

        return {
            'input_summary': {
                'diameter_inch': d_inch,
                'diameter_mm': round(d_mm, 2),
                'design_factor_str': design_factor_str,
                'design_factor_num': round(f_factor, 2),
                'wall_thickness_mm': round(t, 2),
                'manufacturing_process': manufacturing_process,
                'material_grade': grade_clean,
                'standard_type': standard_type,
                'psl_level': psl_level if is_api_mode else "BOTAŞ",
                'delivery_condition': delivery if is_api_mode and not is_psl1 else "—",
                'design_pressure_bar': round(p_oper, 2),
                'botas_thickness_status': botas_thickness_status,
                'validation_warning': validation_warning
            },
            'chemical_analysis': {
                'as_agreed': chem_as_agreed,
                'as_agreed_note': chem_rules.get('note', '') if chem_as_agreed else '',
                'C_max': chem_rules.get('C_max'),
                'Mn_max': chem_rules.get('Mn_max'),
                'P_min': chem_rules.get('P_min', 0.0),
                'P_max': chem_rules.get('P_max'),
                'S_max': chem_rules.get('S_max'),
                'Nb_min_max': (f"{chem_rules['Nb_min']:.3f}-{chem_rules['Nb_max']:.3f}"
                               if chem_rules.get('Nb_min', 0) > 0 and chem_rules.get('Nb_max')
                               else (f"{chem_rules['Nb_max']:.2f}" if chem_rules.get('Nb_max') is not None else None)),
                'Nb_label': "Min%-Max%" if chem_rules.get('Nb_min', 0) > 0 else "Max %",
                'V_max': chem_rules.get('V_max'),
                'Ti_max': chem_rules.get('Ti_max'),
                'nb_v_ti_combined_max': chem_rules.get('nb_v_ti_combined_max'),
                'N_max': chem_rules.get('N_max'),
                'CE_IIW_max': chem_rules.get('CE_IIW_max'),
                'CE_Pcm_max': chem_rules.get('CE_Pcm_max')
            },
            'wall_thickness_tolerance': {
                'nominal_mm': round(t, 2),
                'min_mm': round(t_min, 2),
                'max_mm': round(t_max, 2)
            },
            'mechanical_properties': {
                'smys_psi': round(smys_psi, 2),
                'yield_min_psi': round(smys_psi, 2),
                'yield_min_mpa': round(yield_min_mpa, 2),
                'yield_max_psi': round(yield_max_psi, 2),
                'yield_max_mpa': round(yield_max_mpa, 2),
                'tensile_min_psi': round(tensile_min_psi, 2),
                'tensile_min_mpa': round(tensile_min_mpa, 2),
                'tensile_max_psi': round(tensile_max_psi, 2),
                'tensile_max_mpa': round(tensile_max_mpa, 2),
                'yield_to_tensile_ratio_max': round(yt_max, 2)
            },
            'hydrostatic_test': {
                'hydro_test_max_bar': round(p_hydro_max, 2),
                'hydro_test_min_bar': round(p_hydro_min, 2),
                'api_5l_std_test_bar': round(api_std_test_press, 2),
                # API 5L 9.3.1.1: alternative test pressure is by agreement between
                # purchaser and manufacturer (not the thick-wall design pressure).
                'api_5l_alt_test_bar': "Anlaşmaya bağlıdır (API 5L 9.3.1.1)"
            },
            'dimensional_tolerances': {
                'diameter_end_max_mm': round(d_end_max, 2) if isinstance(d_end_max, (int, float)) else d_end_max,
                'diameter_end_min_mm': round(d_end_min, 2) if isinstance(d_end_min, (int, float)) else d_end_min,
                'diameter_body_max_mm': round(d_body_max, 2) if isinstance(d_body_max, (int, float)) else d_body_max,
                'diameter_body_min_mm': round(d_body_min, 2) if isinstance(d_body_min, (int, float)) else d_body_min,
                'circ_end_max_mm': round(circ_end_max, 2) if isinstance(circ_end_max, (int, float)) else circ_end_max,
                'circ_end_min_mm': round(circ_end_min, 2) if isinstance(circ_end_min, (int, float)) else circ_end_min,
                'circ_body_max_mm': round(circ_body_max, 2) if isinstance(circ_body_max, (int, float)) else circ_body_max,
                'circ_body_min_mm': round(circ_body_min, 2) if isinstance(circ_body_min, (int, float)) else circ_body_min,
                'ovality_end_mm': round(ovality_end, 2) if isinstance(ovality_end, (int, float)) else ovality_end,
                'ovality_body_mm': round(ovality_body, 2) if isinstance(ovality_body, (int, float)) else ovality_body,
                'pipe_end_peaking_max_mm': round(weld_peaking, 2) if isinstance(weld_peaking, (int, float)) else weld_peaking,
                'pipe_end_squareness_max_mm': round(pipe_end_squareness, 2) if isinstance(pipe_end_squareness, (int, float)) else pipe_end_squareness
            },
            'weld_and_geometry': {
                'radial_offset_max_mm': round(radial_offset, 2) if isinstance(radial_offset, (int, float)) else radial_offset,
                'weld_height_inside_mm': round(weld_h_inside, 2) if isinstance(weld_h_inside, (int, float)) else weld_h_inside,
                'weld_height_outside_mm': round(weld_h_outside, 2) if isinstance(weld_h_outside, (int, float)) else weld_h_outside,
                'misalignment_max_mm': round(misalignment, 2) if isinstance(misalignment, (int, float)) else misalignment,
                'weld_repair_length_max_mm': round(weld_repair_single, 2) if isinstance(weld_repair_single, (int, float)) else weld_repair_single,
                'weld_repair_preheat': repair_preheat
            },
            'toughness_and_tests': {
                'elongation_mat_min_percent': round(elongation_mat, 2),
                'elongation_strip_percent': round(elongation_strip_pct, 2),
                'elongation_round_percent': round(elongation_round_pct, 2),
                'tensile_dual_option': _tensile_dual,
                'elongation_weld_min_percent': round(elongation_weld, 2) if isinstance(elongation_weld, (int, float)) else elongation_weld,
                'notch_impact_mat_j': round(cvn_mat, 2) if (isinstance(cvn_mat, (int, float)) and cvn_required) else ("PSL1'de zorunlu değil" if not cvn_required else cvn_mat),
                'notch_impact_weld_j': round(cvn_weld, 2) if (isinstance(cvn_weld, (int, float)) and cvn_required) else ("PSL1'de zorunlu değil" if not cvn_required else cvn_weld),
                'cvn_required': cvn_required,
                'notch_specimen_size': notch_specimen_size,
                'residual_stress_max_mm': round(residual_stress_max, 2) if isinstance(residual_stress_max, (int, float)) else residual_stress_max,
                'dwtt_test': dwtt,
                'hardness_test_max': hardness_test,
                'mandrel_dia_max_mm': round(mandrel_dia, 2) if isinstance(mandrel_dia, (int, float)) else mandrel_dia,
                'jaw_opening_max_mm': round(jaw_opening, 2) if isinstance(jaw_opening, (int, float)) else jaw_opening
            },
            'flattening': {
                'weld_opening_height_mm': round(weld_open_h, 2) if isinstance(weld_open_h, (int, float)) else weld_open_h,
                'material_crack_height_mm': round(mat_crack_h, 2) if isinstance(mat_crack_h, (int, float)) else mat_crack_h,
                'lamination_rule': lamination
            },
            'weights_and_safety': {
                'weight_nominal_kg_m': round(weight_nom, 2),
                'weight_min_kg_m': round(weight_min, 2),
                'weight_max_kg_m': round(weight_max, 2),
                'operating_press_over_smys_percent': f"{round(oper_press_ratio * 100.0, 2)}%",
                'operating_press_over_smys_val': round(oper_press_ratio, 2),
                'fracture_control_asme_841_1_2': fracture_control,
                'd_over_t': round(d_over_t, 2),
                'design_formula_asme_841_1_1': design_formula_alt,
                'alternative_design_pressure_bar': round(alt_design_press, 2) if isinstance(alt_design_press, (int, float)) else alt_design_press
            },
            'explanations': build_standard_explanations(is_botas_mode, is_psl1),
            'edition_notes': build_edition_notes({
                'material_grade': material_grade,
                'diameter_mm': d_mm,
                'wall_thickness_mm': t,
                'psl_level': psl_level,
                'manufacturing_process': manufacturing_process,
                'delivery_condition': delivery_condition,
                'standard_type': standard_type
            })
        }
