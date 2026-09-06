"""
ITP Criteria Parser & Numerical Entity Extraction Engine.
Extracts structured physical limits, temperatures, pressures, and tolerances
from multi-language (TR / EN) acceptance criteria text strings and compares them
against standard/calculated pipe engineering targets.
"""

import re
from typing import Dict, Optional, Any


class ITPCriteriaParser:
    """
    Rule-based numeric entity extraction for ITP criteria.
    Parses complex criteria strings with units (MPa, J, bar, %, mm, kV, N/mm, °C).
    """

    @classmethod
    def parse_chemical_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts chemical analysis maximum limits:
        C (%), P (%), S (%), CE_IIW, CE_Pcm, N (%).
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "C_max": None,
            "P_max": None,
            "S_max": None,
            "CE_IIW_max": None,
            "CE_Pcm_max": None,
            "N_max": None
        }

        # Carbon C max
        m_c = re.search(r'(?:(?<![a-z0-9])c|carbon|karbon)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.(\d+)', t)
        if m_c:
            res["C_max"] = float("0." + m_c.group(1))
        else:
            m_c2 = re.search(r'0\.(\d+)\s*(?:%|\b)[\s:=]*(?:max|azami)[^\w]*(?:c|carbon|karbon)', t)
            if m_c2:
                res["C_max"] = float("0." + m_c2.group(1))

        # Phosphorus P max
        m_p = re.search(r'(?:(?<![a-z0-9])p|phosphorus|fosfor)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.0(\d+)', t)
        if m_p:
            res["P_max"] = float("0.0" + m_p.group(1))

        # Sulfur S max
        m_s = re.search(r'(?:(?<![a-z0-9])s|sulfur|sulphur|kükürt|kukurt)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.0(\d+)', t)
        if m_s:
            res["S_max"] = float("0.0" + m_s.group(1))

        # CE_Pcm max
        m_pcm = re.search(r'(?:ce[_\s-]*pcm|pcm)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.(\d+)', t)
        if m_pcm:
            res["CE_Pcm_max"] = float("0." + m_pcm.group(1))

        # CE_IIW max
        m_ce = re.search(r'(?:ce[_\s-]*(?:\([a-z0-9]+\)|[a-z0-9]+)?|ce)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.(\d+)', t)
        if m_ce:
            v_ce = float("0." + m_ce.group(1))
            if res["CE_Pcm_max"] != v_ce:
                res["CE_IIW_max"] = v_ce

        # Nitrogen N max
        m_n = re.search(r'(?:(?<![a-z0-9])n|nitrogen|azot)[\s:=≤<=]*(?:max\.?|azami|en\s*çok)?[\s:=≤<=]*0\.0(\d+)', t)
        if m_n:
            res["N_max"] = float("0.0" + m_n.group(1))

        return res

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
        m_yield = re.search(r'(?:rt\s*0?\.?5|rp\s*0?\.?2|akma\s*(?:muk\.?|dayanımı)?|yield\s*(?:strength)?|smys|ys)[\s:=≥≤><]+(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?', t)
        if m_yield:
            v_y = float(m_yield.group(1))
            if v_y >= 100.0:
                res["yield_min"] = v_y
                if m_yield.group(2):
                    v_y2 = float(m_yield.group(2))
                    if v_y2 >= 100.0:
                        res["yield_max"] = v_y2

        # Tensile strength (Rm, UTS, çekme, tensile)
        # e.g., 'Rm: 535 - 760 MPa' or 'Rm >= 535'
        m_tens = re.search(r'(?:rm|uts|çekme\s*(?:muk\.?|dayanımı)?|cekme|tensile\s*(?:strength)?)[\s:=≥≤><]+(\d+(?:\.\d+)?)\s*(?:[-–/]\s*(\d+(?:\.\d+)?))?', t)
        if m_tens:
            v_t = float(m_tens.group(1))
            if v_t >= 100.0:
                res["tensile_min"] = v_t
                if m_tens.group(2):
                    v_t2 = float(m_tens.group(2))
                    if v_t2 >= 100.0:
                        res["tensile_max"] = v_t2

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

        # 1. Plus-Minus: '± 1.6 mm', '+/- 1.6 mm', '+- 1.6 mm'
        m_pm = re.search(r'(?:±|\+\s*[\-/]+\s*)\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_pm:
            val_pm = float(m_pm.group(1))
            res["plus_tol_mm"] = val_pm
            res["minus_tol_mm"] = val_pm
            res["plus_mm"] = val_pm
            res["minus_mm"] = val_pm
        else:
            # Standalone +X.X mm
            m_plus = re.search(r'(?<![-/])\+\s*(\d+(?:\.\d+)?)\s*mm', t)
            if m_plus:
                res["plus_mm"] = float(m_plus.group(1))
                res["plus_tol_mm"] = float(m_plus.group(1))
            # Standalone -X.X mm
            m_minus = re.search(r'(?<![+/])[-–]\s*(\d+(?:\.\d+)?)\s*mm', t)
            if m_minus:
                res["minus_mm"] = float(m_minus.group(1))
                res["minus_tol_mm"] = float(m_minus.group(1))

        # Plus percentage (e.g. +%15, +15%, + 10 %)
        m_pct_plus = re.search(r'\+\s*[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
        if m_pct_plus:
            res["plus_pct"] = float(m_pct_plus.group(1))
        else:
            m_pct_plus2 = re.search(r'\+\s*%\s*(\d+(?:\.\d+)?)', t)
            if m_pct_plus2:
                res["plus_pct"] = float(m_pct_plus2.group(1))

        # Minus percentage (e.g. -%12.5, -12.5%, -8%)
        m_pct_min = re.search(r'[-–]\s*[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
        if m_pct_min:
            res["minus_pct"] = float(m_pct_min.group(1))
        else:
            m_pct_min2 = re.search(r'[-–]\s*%\s*(\d+(?:\.\d+)?)', t)
            if m_pct_min2:
                res["minus_pct"] = float(m_pct_min2.group(1))

        # Min / Asgari X.X mm
        m_min_lim = re.search(r'(?:min|asgari|en az|≥)\s*(\d+(?:\.\d+)?)\s*mm', t)
        if m_min_lim:
            res["min_limit_mm"] = float(m_min_lim.group(1))

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

    @classmethod
    def parse_bend_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts guided bend parameters without confusing mandrel diameter with crack defect limits.
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "mandrel_dia_mm": None,
            "jaw_opening_mm": None,
            "max_crack_mm": None
        }

        # Mandrel diameter Ag
        m_mand = re.search(r'mandrel[^\d]{0,12}(?:ag\b)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_mand:
            res["mandrel_dia_mm"] = float(m_mand.group(1))

        # Jaw opening Bg
        m_jaw = re.search(r'(?:çene|cene|jaw)[^\d]{0,12}(?:bg\b)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_jaw:
            res["jaw_opening_mm"] = float(m_jaw.group(1))

        # Defect / crack length limit specifically tied to crack keywords
        m_crack = re.search(r'(?:çatlak|catlak|kusur|defect|crack|açılma|acilma)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_crack:
            res["max_crack_mm"] = float(m_crack.group(1))
        else:
            m_crack2 = re.search(r'(?:<=|≤|<|max|azami)\s*(\d+(?:\.\d+)?)\s*mm[^\d]{0,15}(?:çatlak|catlak|kusur|defect|crack)', t)
            if m_crack2:
                res["max_crack_mm"] = float(m_crack2.group(1))

        return res

    @classmethod
    def parse_weld_repair_criteria(cls, text: str) -> Dict[str, Any]:
        """
        Extracts weld repair limits, distinguishing single repair length from pipe end distance restrictions.
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Any] = {
            "body_repair_allowed": None,
            "re_repair_allowed": None,
            "max_single_repair_length_mm": None,
            "end_restriction_distance_mm": None
        }

        if any(k in t for k in ("gövdeye kaynak yasak", "govdeye kaynak yasak", "gövde tamiri yasak", "no body repair", "body repair prohibited")):
            res["body_repair_allowed"] = False
        elif any(k in t for k in ("gövde tamiri serbest", "govde tamiri serbest", "gövdeye kaynak yapılabilir")):
            res["body_repair_allowed"] = True

        if any(k in t for k in ("re-repair yasak", "tekrar tamir yasak", "ikinci tamir yasak", "no re-repair", "re-welding prohibited")):
            res["re_repair_allowed"] = False
        elif any(k in t for k in ("re-repair serbest", "tekrar tamir serbest")):
            res["re_repair_allowed"] = True

        # Single repair length (e.g. 'Tek tamir <= 150 mm', 'max 150 mm')
        m_rep = re.search(r'(?:tek\s*tamir|tekil\s*tamir|single\s*repair|tamir\s*boyu|length\s*of\s*repair)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_rep:
            res["max_single_repair_length_mm"] = float(m_rep.group(1))
        else:
            m_rep2 = re.search(r'(?:<=|≤|<|max|azami)\s*(\d+(?:\.\d+)?)\s*mm[^\d]{0,15}(?:tek\s*tamir|single\s*repair)', t)
            if m_rep2:
                res["max_single_repair_length_mm"] = float(m_rep2.group(1))

        # End restriction distance (e.g. 'uçta 300 mm tamir yasağı', '300 mm from ends')
        m_end = re.search(r'(?:uçta|ucta|uçtan|uctan|from\s*ends?|pipe\s*ends?)[^\d]{0,15}(\d+(?:\.\d+)?)\s*mm', t)
        if m_end:
            res["end_restriction_distance_mm"] = float(m_end.group(1))
        else:
            m_end2 = re.search(r'(\d+(?:\.\d+)?)\s*mm[^\d]{0,15}(?:uç|uc|end)', t)
            if m_end2:
                res["end_restriction_distance_mm"] = float(m_end2.group(1))

        return res

    @classmethod
    def parse_ovality_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts ovality limits specifically tied to ovality / out-of-roundness keywords,
        without being misled by nominal pipe diameter ranges.
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "ovality_end_max_mm": None,
            "ovality_body_max_mm": None,
            "ovality_max_mm": None,
            "ovality_pct": None
        }

        # End ovality
        m_end = re.search(r'(?:uç\s*ovalite|ovalite\s*uç|uc\s*ovalite|ovalite\s*uc|end\s*ovality|ovality\s*ends?|out-of-roundness\s*ends?)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_end:
            res["ovality_end_max_mm"] = float(m_end.group(1))
            res["ovality_max_mm"] = float(m_end.group(1))

        # Body ovality
        m_body = re.search(r'(?:gövde\s*ovalite|govde\s*ovalite|body\s*ovality|ovality\s*body|out-of-roundness\s*body)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
        if m_body:
            res["ovality_body_max_mm"] = float(m_body.group(1))
            if res["ovality_max_mm"] is None:
                res["ovality_max_mm"] = float(m_body.group(1))

        # General ovality if neither end nor body specifically isolated
        if res["ovality_max_mm"] is None:
            m_gen = re.search(r'(?:ovality|ovalite|roundness|yuvarlaklık|yuvarlaklik|dairesellik)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*mm', t)
            if m_gen:
                res["ovality_max_mm"] = float(m_gen.group(1))

        # Ovality percentage (e.g. '%0.5 D', '0.5%')
        m_pct = re.search(r'(?:ovality|ovalite|roundness)[^\d]{0,15}(?:<=|≤|<|max|azami)?[\s:=]*(\d+(?:\.\d+)?)\s*%', t)
        if m_pct:
            res["ovality_pct"] = float(m_pct.group(1))

        return res

    @classmethod
    def parse_weight_criteria(cls, text: str) -> Dict[str, Optional[float]]:
        """
        Extracts pipe unit weight (kg/m) and weight tolerances (-% / +%).
        API 5L 9.11.2 specifies -3.5% / +10.0% for individual pipes.
        """
        t = (text or "").lower().replace(",", ".")
        res: Dict[str, Optional[float]] = {
            "nominal_kg_m": None,
            "minus_pct": None,
            "plus_pct": None
        }

        # Nominal / theoretical weight: e.g. '424.8 kg/m', 'W = 425 kg/m'
        m_w = re.search(r'(?:teorik|nominal|w\b|birim\s*ağırlık|weight)?[^\d]{0,10}(\d+(?:\.\d+)?)\s*kg/m', t)
        if m_w:
            res["nominal_kg_m"] = float(m_w.group(1))

        # Plus/minus percentage: e.g. '± %5', '±5%', '+/- 5%'
        m_pm = re.search(r'(?:±|\+\s*[\-/]+\s*)[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
        if m_pm:
            res["minus_pct"] = float(m_pm.group(1))
            res["plus_pct"] = float(m_pm.group(1))
        else:
            # Minus pct: e.g. '-3.5%', '-%3.5', '- 3.5 %'
            m_min = re.search(r'[-–]\s*[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
            if m_min:
                res["minus_pct"] = float(m_min.group(1))
            else:
                m_min2 = re.search(r'[-–]\s*%\s*(\d+(?:\.\d+)?)', t)
                if m_min2:
                    res["minus_pct"] = float(m_min2.group(1))

            # Plus pct: e.g. '+10%', '+%10', '+ 10 %'
            m_pls = re.search(r'\+\s*[%]?\s*(\d+(?:\.\d+)?)\s*%', t)
            if m_pls:
                res["plus_pct"] = float(m_pls.group(1))
            else:
                m_pls2 = re.search(r'\+\s*%\s*(\d+(?:\.\d+)?)', t)
                if m_pls2:
                    res["plus_pct"] = float(m_pls2.group(1))

        return res
