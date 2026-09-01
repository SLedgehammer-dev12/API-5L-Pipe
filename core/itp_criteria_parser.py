"""
ITP Criteria Parser & Numerical Entity Extraction Engine.
Extracts structured physical limits, temperatures, pressures, and tolerances
from multi-language (TR / EN) acceptance criteria text strings and compares them
against standard/calculated pipe engineering targets.
"""

import re
from typing import Dict, Optional


class ITPCriteriaParser:
    """
    Rule-based numeric entity extraction for ITP criteria.
    Parses complex criteria strings with units (MPa, J, bar, %, mm, kV, N/mm, °C).
    """

    @classmethod
    def parse_tensile_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts yield strength (Rt0.5/Rp0.2), tensile strength (Rm/UTS),
        yield ratio (Rt/Rm), and elongation (A%).
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "yield_min": None,
            "yield_max": None,
            "tensile_min": None,
            "tensile_max": None,
            "ratio_max": None,
            "elongation_min": None
        }

        # Yield strength (Rt0.5, Rp0.2, akma, yield, SMYS)
        # e.g., 'Rt0.5: 450 - 570 MPa' or 'Rt0.5 >= 450' or 'akma: 450-570'
        m_yield = re.search(r'(?:rt0?\.?5?|rp0?\.?2?|akma|yield|smys|ys)[\s:=≥≤><]*(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?', t)
        if m_yield:
            res["yield_min"] = float(m_yield.group(1))
            if m_yield.group(2):
                res["yield_max"] = float(m_yield.group(2))

        # Tensile strength (Rm, UTS, çekme, tensile)
        # e.g., 'Rm: 535 - 760 MPa' or 'Rm >= 535'
        m_tens = re.search(r'(?:rm|uts|çekme|cekme|tensile)[\s:=≥≤><]*(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?', t)
        if m_tens:
            res["tensile_min"] = float(m_tens.group(1))
            if m_tens.group(2):
                res["tensile_max"] = float(m_tens.group(2))

        # Yield-to-tensile ratio (Rt/Rm, ratio, oran)
        m_ratio = re.search(r'(?:rt/rm|yt|y/t|oran|ratio)\s*(?:<=|>=|:=|[=:≤<>])\s*(0?\.\d+)', t)
        if m_ratio:
            res["ratio_max"] = float(m_ratio.group(1))

        # Elongation (A, A50, Af, uzama, elongation, kopma uzaması)
        m_elo = re.search(r'(?:a50|a2in|af|uzama|elongation|kopma)[\s:=≥≤><%]*(\d+(?:\.\d+)?)', t)
        if m_elo:
            res["elongation_min"] = float(m_elo.group(1))

        return res

    @classmethod
    def parse_cvn_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts Charpy V-Notch impact parameters:
        test temperature (°C), average energy (J), single/minimum energy (J), shear area (%).
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "temp_c": None,
            "energy_avg_j": None,
            "energy_min_j": None,
            "shear_area_percent": None
        }

        # Temperature: '-20°C', '-20 c', '0°C', '+20°C', 'at -20 deg c'
        m_temp = re.search(r'([+-]?\d+)\s*(?:°\s*c|deg\s*c|c)', t)
        if m_temp:
            res["temp_c"] = float(m_temp.group(1))

        # 1. Explicit average energy: 'ortalama 48 J', 'min ortalama 48 J', 'ort 48 J', 'avg 48 J'
        m_avg_exp = re.search(r'(?:ort(?:alama)?|avg|average)\s*(?:min)?\s*[:=≥>]?\s*(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?\s*(?:j|joule)?', t)
        if m_avg_exp:
            v1 = float(m_avg_exp.group(1))
            v2 = float(m_avg_exp.group(2)) if m_avg_exp.group(2) else None
            if v2:
                res["energy_avg_j"] = max(v1, v2)
                res["energy_min_j"] = min(v1, v2)
            else:
                res["energy_avg_j"] = v1
        else:
            # Fallback average energy: '40/30 J', 'min 40 J'
            m_avg = re.search(r'(?:min)?\s*(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?\s*(?:j|joule)', t)
            if m_avg:
                v1 = float(m_avg.group(1))
                v2 = float(m_avg.group(2)) if m_avg.group(2) else None
                if v2:
                    res["energy_avg_j"] = max(v1, v2)
                    res["energy_min_j"] = min(v1, v2)
                else:
                    res["energy_avg_j"] = v1

        # Explicit single minimum: 'tekil min 30 J', 'single min 30 J', 'ind 30 J'
        m_ind = re.search(r'(?:tekil|single|ind(?:ividual)?)\s*(?:min)?\s*[:=≥>]?\s*(\d+(?:\.\d+)?)\s*(?:j|joule)?', t)
        if m_ind:
            res["energy_min_j"] = float(m_ind.group(1))

        # Shear area percentage: 'min %85 shear', '%85 shear', 'liflilik >= %85', 'ortalama sünek kırılma min %70'
        m_shear = re.search(r'(?:(?:shear|liflilik|düşen|ductile|sünek|sunek|kırılma|kirilma)[^\d%]{0,15}[\s:=≥≤><%]*(\d+(?:\.\d+)?)|%?\s*(\d+(?:\.\d+)?)\s*%?\s*(?:shear|liflilik|ductile|sünek|sunek|kırılma|kirilma))', t)
        if m_shear:
            res["shear_area_percent"] = float(m_shear.group(1) or m_shear.group(2))

        return res

    @classmethod
    def parse_hydrostatic_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts hydrostatic test pressure (bar/psi/MPa), holding time (seconds), and % SMYS.
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "pressure_bar": None,
            "holding_time_sec": None,
            "smys_percent": None
        }

        # Pressure in bar, psi or MPa
        m_bar = re.search(r'(\d+(?:\.\d+)?)\s*bar\b', t)
        if m_bar:
            res["pressure_bar"] = float(m_bar.group(1))
        else:
            m_mpa = re.search(r'(\d+(?:\.\d+)?)\s*mpa\b', t)
            if m_mpa:
                res["pressure_bar"] = float(m_mpa.group(1)) * 10.0
            else:
                m_psi = re.search(r'(\d+(?:\.\d+)?)\s*psi\b', t)
                if m_psi:
                    res["pressure_bar"] = round(float(m_psi.group(1)) * 0.0689476, 1)

        # Holding duration in seconds: '10 s', '10 sn', '10 saniye', '5 sec', '10 seconds'
        m_time = re.search(r'(\d+)\s*(?:s\b|sn\b|sec\b|second|saniye)', t)
        if m_time:
            res["holding_time_sec"] = float(m_time.group(1))

        # % SMYS: '%95 SMYS', '95% SMYS', '%100 SMYS'
        m_smys = re.search(r'%?\s*(\d+(?:\.\d+)?)\s*%?\s*smys', t)
        if m_smys:
            res["smys_percent"] = float(m_smys.group(1))

        return res

    @classmethod
    def parse_coating_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts 3LPE coating parameters:
        thickness (mm/µm), holiday voltage (kV), peel strength (N/mm or N/cm),
        impact resistance (J/mm), blasting cleanliness (Sa 2.5), roughness Rz (µm).
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "thickness_mm": None,
            "total_pe_mm": None,
            "fbe_um": None,
            "holiday_kv": None,
            "peel_n_mm": None,
            "impact_j_mm": None,
            "roughness_rz_min_um": None,
            "roughness_rz_max_um": None
        }

        # Coating Thickness: 'min 3.0 mm', 'min 3000 µm', '2.7 mm'
        m_thk_mm = re.search(r'(?:min|azami)?\s*(\d+(?:\.\d+)?)\s*mm\b', t)
        if m_thk_mm and float(m_thk_mm.group(1)) < 20.0:
            val_thk = float(m_thk_mm.group(1))
            res["thickness_mm"] = val_thk
            res["total_pe_mm"] = val_thk
        else:
            m_thk_um = re.search(r'(\d{3,5})\s*(?:µm|um|mikron|micron)', t)
            if m_thk_um:
                val_thk = float(m_thk_um.group(1)) / 1000.0
                res["thickness_mm"] = val_thk
                res["total_pe_mm"] = val_thk

        # FBE thickness: 'fbe 120 µm', 'epoksi 100 um'
        m_fbe = re.search(r'(?:fbe|epoksi|epoxy|astar)\s*[:=≥≥]*\s*(\d+(?:\.\d+)?)\s*(?:µm|um)', t)
        if m_fbe:
            res["fbe_um"] = float(m_fbe.group(1))

        # Holiday voltage: '25 kV', '25000 V', '25kv'
        m_kv = re.search(r'(\d+(?:\.\d+)?)\s*kv\b', t)
        if m_kv:
            res["holiday_kv"] = float(m_kv.group(1))
        else:
            m_v = re.search(r'(\d{4,5})\s*v(?:olt)?\b', t)
            if m_v:
                res["holiday_kv"] = float(m_v.group(1)) / 1000.0

        # Peel adhesion: '150 N/cm' -> 15.0 N/mm, '15 N/mm', '18 N/mm'
        m_peel_cm = re.search(r'(\d+(?:\.\d+)?)\s*n/cm\b', t)
        if m_peel_cm:
            res["peel_n_mm"] = float(m_peel_cm.group(1)) / 10.0
        else:
            m_peel_mm = re.search(r'(\d+(?:\.\d+)?)\s*n/mm\b', t)
            if m_peel_mm:
                res["peel_n_mm"] = float(m_peel_mm.group(1))

        # Impact resistance: '5 J/mm', '5.0 j/mm'
        m_imp = re.search(r'(\d+(?:\.\d+)?)\s*j/mm\b', t)
        if m_imp:
            res["impact_j_mm"] = float(m_imp.group(1))

        # Roughness Rz: 'Rz 60-100 µm'
        m_rz = re.search(r'rz\s*(\d+)\s*(?:[-–/]\s*(\d+))?', t)
        if m_rz:
            res["roughness_rz_min_um"] = float(m_rz.group(1))
            if m_rz.group(2):
                res["roughness_rz_max_um"] = float(m_rz.group(2))

        return res

    @classmethod
    def parse_dimensional_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts dimensional limits: tolerance (± mm or %), max value (mm),
        angle (degrees °), root face (mm).
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "plus_tol_mm": None,
            "minus_tol_mm": None,
            "plus_mm": None,
            "minus_mm": None,
            "plus_pct": None,
            "minus_pct": None,
            "max_val_mm": None,
            "max_limit_mm": None,
            "min_limit_mm": None,
            "angle_deg": None,
            "root_face_mm": None
        }

        # ± X.X mm
        m_pm = re.search(r'[±\+\-]\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_pm:
            val_pm = float(m_pm.group(1))
            res["plus_tol_mm"] = val_pm
            res["minus_tol_mm"] = val_pm
            res["plus_mm"] = val_pm
            res["minus_mm"] = val_pm

        # +X.X / -Y.Y mm
        m_plus = re.search(r'\+\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_plus:
            res["plus_mm"] = float(m_plus.group(1))
            res["plus_tol_mm"] = float(m_plus.group(1))
        m_minus = re.search(r'-\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_minus:
            res["minus_mm"] = float(m_minus.group(1))
            res["minus_tol_mm"] = float(m_minus.group(1))

        # Minus percentage (e.g. -%12.5, -12.5%, -8%)
        m_pct_min = re.search(r'[-–]\s*[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
        if m_pct_min:
            res["minus_pct"] = float(m_pct_min.group(1))
        m_pct_min2 = re.search(r'[-–]\s*%\s*(\d+(?:\.\d+)?)', t)
        if m_pct_min2:
            res["minus_pct"] = float(m_pct_min2.group(1))

        # Max / Azami X.X mm
        m_max = re.search(r'(?:max|azami|en çok|≤)\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_max:
            val_m = float(m_max.group(1))
            res["max_val_mm"] = val_m
            res["max_limit_mm"] = val_m

        # Angle: '30°', '30 deg', '35°'
        m_ang = re.search(r'(\d+)\s*(?:°|deg|derece)', t)
        if m_ang:
            res["angle_deg"] = float(m_ang.group(1))

        # Root face: 'kök yüzü 1.6 mm', 'root face 1.6'
        m_rf = re.search(r'(?:kök|root)\s*(?:yüzü|face)?\s*[:=]?\s*(\d+(?:\.\d+)?)', t)
        if m_rf:
            res["root_face_mm"] = float(m_rf.group(1))

        return res
