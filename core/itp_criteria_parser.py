"""
ITP Criteria Parser & Numerical Entity Extraction Engine.
Extracts structured physical limits, temperatures, pressures, and tolerances
from multi-language (TR / EN) acceptance criteria text strings and compares them
against standard/calculated pipe engineering targets.
"""

import re
from typing import Dict, Optional, Any

_TR_ASCII_TABLE = str.maketrans("çğöşü", "cgosu")
_CHEM_SEP = r'(?:[\s:=≤<%]{1,8}(?:max\.?|azami|en\s{1,3}çok)[\s:=≤<%]{0,8}|[\s:=≤<%]{1,8})'


def norm_tr(text: str, ascii_fold: bool = False) -> str:
    s = (text or "").replace("İ", "i").replace("I", "i").replace("ı", "i").lower().replace("i\u0307", "i")
    return s.translate(_TR_ASCII_TABLE) if ascii_fold else s


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

        m_c = re.search(r'(?:(?<![a-z0-9])c(?![a-z0-9])|carbon|karbon)' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_c:
            res["C_max"] = float("0." + m_c.group(1))
        else:
            m_c2 = re.search(r'0\.(\d+)\s{0,4}%?[\s:=]{0,6}(?:max\.?|azami)[^\w]{0,5}(?:c|carbon|karbon)\b', t)
            if m_c2:
                res["C_max"] = float("0." + m_c2.group(1))

        m_p = re.search(r'(?:(?<![a-z0-9])p(?![a-z0-9])|phosphorus|fosfor)' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_p:
            res["P_max"] = float("0." + m_p.group(1))

        m_s = re.search(r'(?:(?<![a-z0-9])s(?![a-z0-9])|sulfur|sulphur|kükürt|kukurt)' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_s:
            res["S_max"] = float("0." + m_s.group(1))

        m_pcm = re.search(r'(?:(?<![a-z0-9])ce[\s_-]{0,3}\(?pcm\)?|(?<![a-z0-9])pcm(?![a-z0-9]))' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_pcm:
            res["CE_Pcm_max"] = float("0." + m_pcm.group(1))

        m_ce = re.search(r'(?<![a-z0-9])(?:ceq|cev|ce(?:[\s_-]{0,3}\(?iiw\)?|(?![\s_-]{0,3}\(?pcm\b)(?![a-z0-9])))' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_ce:
            res["CE_IIW_max"] = float("0." + m_ce.group(1))

        m_n = re.search(r'(?:(?<![a-z0-9])n(?![a-z0-9])|nitrogen|azot)' + _CHEM_SEP + r'0\.(\d+)', t)
        if m_n:
            res["N_max"] = float("0." + m_n.group(1))

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

        for m_yield in re.finditer(
            r'(?:rt\s{0,2}0?\.?5|rp\s{0,2}0?\.?2|akma(?:\s{1,3}(?:muk\.?|dayanımı|dayanimi))?|yield(?:\s{1,3}strength)?|smys|ys)[\s:=≥≤><]{1,6}(?:min\.?[\s:=≥≤><]{0,4})?(\d+(?:\.\d+)?)(?:\s{0,3}[-–/]\s{0,3}(\d+(?:\.\d+)?))?',
            t,
        ):
            v_y = float(m_yield.group(1))
            if v_y >= 100.0:
                res["yield_min"] = v_y
                if m_yield.group(2):
                    v_y2 = float(m_yield.group(2))
                    if v_y2 >= 100.0:
                        res["yield_max"] = v_y2
                break

        for m_tens in re.finditer(
            r'(?:(?<![a-z0-9/])rm(?![a-z0-9])|(?<![a-z0-9])uts(?![a-z0-9])|çekme(?:\s{1,3}(?:muk\.?|dayanımı|dayanimi))?|cekme|tensile(?:\s{1,3}strength)?)[\s:=≥≤><]{1,6}(?:min\.?[\s:=≥≤><]{0,4})?(\d+(?:\.\d+)?)(?:\s{0,3}[-–/]\s{0,3}(\d+(?:\.\d+)?))?',
            t,
        ):
            v_t = float(m_tens.group(1))
            if v_t >= 100.0:
                res["tensile_min"] = v_t
                if m_tens.group(2):
                    v_t2 = float(m_tens.group(2))
                    if v_t2 >= 100.0:
                        res["tensile_max"] = v_t2
                break

        m_ratio = re.search(
            r'(?:rt\s{0,2}0?\.?5\s{0,2}/\s{0,2}rm|rp\s{0,2}0?\.?2\s{0,2}/\s{0,2}rm|rt\s{0,2}/\s{0,2}rm|(?<![a-z0-9])y\s{0,2}/\s{0,2}t(?![a-z0-9])|(?<![a-z0-9])yt(?![a-z0-9])|oran[ıi]?|ratio)\s{0,4}(?:max\.?|azami)?[\s:=≤<>≥]{0,6}(0?\.\d+)',
            t,
        )
        if m_ratio:
            res["ratio_max"] = float(m_ratio.group(1))

        m_elo = re.search(
            r'(?:(?<![a-z0-9])(?:a50|a2in|af)(?![a-z0-9])|kopma\s{1,3}uzamas[ıi]|uzamas[ıi]|uzama|elongation)(?:\s{0,3}\(%\))?(?:\s{1,3}(?:min\.?|asgari|en\s{1,3}az))?[\s:=≥≤><%]{0,8}(\d+(?:\.\d+)?)',
            t,
        )
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

        m_temp = re.search(r'(?<![\d.])([+-]?\d+)\s{0,3}(?:°\s{0,2}c|deg\.?\s{0,2}c)|(?<![a-z0-9.])([+-]\d+)\s{0,2}c\b|(?<![\d.])(0)\s{1,2}c\b', t)
        if m_temp:
            temp_token = m_temp.group(1) or m_temp.group(2) or m_temp.group(3)
            if temp_token is not None:
                res["temp_c"] = float(temp_token)

        m_avg_exp = re.search(
            r'(?:ort(?:alama)?|avg|average)(?:\s{1,3}min\.?)?[\s:=≥>]{0,6}(\d+(?:\.\d+)?)(?:\s{0,3}[-–/]\s{0,3}(\d+(?:\.\d+)?))?\s{0,3}(?:j|joule)?',
            t,
        )
        if m_avg_exp:
            v1 = float(m_avg_exp.group(1))
            v2 = float(m_avg_exp.group(2)) if m_avg_exp.group(2) else None
            if v2:
                res["energy_avg_j"] = max(v1, v2)
                res["energy_min_j"] = min(v1, v2)
            else:
                res["energy_avg_j"] = v1
        else:
            m_avg = re.search(r'(?:min\.?[\s:=≥>]{0,4})?(\d+(?:\.\d+)?)(?:\s{0,3}[-–/]\s{0,3}(\d+(?:\.\d+)?))?\s{0,3}(?:j|joule)\b', t)
            if m_avg:
                v1 = float(m_avg.group(1))
                v2 = float(m_avg.group(2)) if m_avg.group(2) else None
                if v2 is not None:
                    res["energy_avg_j"] = max(v1, v2)
                    res["energy_min_j"] = min(v1, v2)
                else:
                    res["energy_avg_j"] = v1

        m_ind = re.search(
            r'(?:tekil|single|ind(?:ividual)?)(?:\s{1,3}min\.?)?[\s:=≥>]{0,6}(\d+(?:\.\d+)?)\s{0,3}(?:j|joule)?',
            t,
        )
        if m_ind:
            res["energy_min_j"] = float(m_ind.group(1))

        # Shear area percentage: 'min %85 shear', '%85 shear', 'liflilik >= %85', 'ortalama sünek kırılma min %70'
        m_shear = re.search(
            r'(?:(?:shear|liflilik|düşen|ductile|sünek|sunek|kırılma|kirilma)[^\d%]{0,15}[\s:=≥≤><%]{0,6}(\d+(?:\.\d+)?)|%?\s{0,3}(\d+(?:\.\d+)?)\s{0,3}%?\s{1,3}(?:shear|liflilik|ductile|sünek|sunek|kırılma|kirilma))',
            t,
        )
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

        m_bar = re.search(r'(\d+(?:\.\d+)?)\s{0,3}bar\b', t)
        if m_bar:
            res["pressure_bar"] = float(m_bar.group(1))
        else:
            m_mpa = re.search(r'(\d+(?:\.\d+)?)\s{0,3}mpa\b', t)
            if m_mpa:
                res["pressure_bar"] = float(m_mpa.group(1)) * 10.0
            else:
                m_psi = re.search(r'(\d+(?:\.\d+)?)\s{0,3}psi\b', t)
                if m_psi:
                    res["pressure_bar"] = round(float(m_psi.group(1)) * 0.0689476, 1)

        m_time = re.search(r'(?<![\d.])(\d+(?:\.\d+)?)\s{0,4}(?:s\b|sn\b|sec\b|second|saniye)', t)
        if m_time:
            res["holding_time_sec"] = float(m_time.group(1))

        m_smys = re.search(r'(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)\s{0,3}smys', t)
        if m_smys:
            res["smys_percent"] = float(m_smys.group(1) or m_smys.group(2))

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
            "holiday_kv_per_mm": None,
            "peel_n_mm": None,
            "impact_j_mm": None,
            "roughness_rz_min_um": None,
            "roughness_rz_max_um": None
        }

        m_fbe_um = re.search(r'(?:fbe|epoksi|epoxy|astar)[^\d]{0,20}(\d+(?:\.\d+)?)\s{0,3}(?:µm|um|mikron|micron)', t)
        if m_fbe_um:
            res["fbe_um"] = float(m_fbe_um.group(1))
        else:
            m_fbe_mm = re.search(r'(?:fbe|epoksi|epoxy|astar)[^\d]{0,20}(\d+(?:\.\d+)?)\s{0,3}mm\b(?!\s*/)', t)
            if m_fbe_mm and float(m_fbe_mm.group(1)) < 1.0:
                res["fbe_um"] = float(m_fbe_mm.group(1)) * 1000.0

        m_exp_pe = re.search(
            r'(?:toplam(?:\s{1,3}(?:kalınlık|kalinlik|pe|3lpe|hdpe|kaplama))?|total(?:\s{1,3}(?:thickness|pe|3lpe|hdpe|coating))?|pe(?:\s{1,3}(?:kaplama|kalınlık|kalinlik|thickness))?|3lpe|hdpe|polietilen|polyethylene)[^\d/]{0,25}(\d+(?:\.\d+)?)\s{0,3}mm\b(?!\s*/)',
            t,
        )
        if m_exp_pe and 0.5 <= float(m_exp_pe.group(1)) < 20.0:
            val_thk = float(m_exp_pe.group(1))
            res["thickness_mm"] = val_thk
            res["total_pe_mm"] = val_thk
        else:
            layer_kws = ("fbe", "epoksi", "epoxy", "astar", "yapıştırıcı", "yapistirici", "adhesive", "copolymer", "kopolimer")
            total_kws = ("toplam", "total", "3lpe", "hdpe", "polietilen", "polyethylene")
            mm_candidates = []
            for m_cand in re.finditer(r'(?<![/\d.])(\d+(?:\.\d+)?)\s{0,3}mm\b(?!\s*/)', t):
                val_cand = float(m_cand.group(1))
                if not (0.5 <= val_cand < 20.0):
                    continue
                prefix = t[max(0, m_cand.start() - 25):m_cand.start()]
                last_layer = max((prefix.rfind(k) for k in layer_kws), default=-1)
                last_total = max((prefix.rfind(k) for k in total_kws), default=-1)
                if last_layer > last_total:
                    continue
                mm_candidates.append(val_cand)
            if mm_candidates:
                val_thk = max(mm_candidates)
                res["thickness_mm"] = val_thk
                res["total_pe_mm"] = val_thk
            else:
                um_candidates = [
                    float(m_u.group(1)) / 1000.0
                    for m_u in re.finditer(r'(\d{4,5})\s{0,3}(?:µm|um|mikron|micron)', t)
                    if 1000.0 <= float(m_u.group(1)) < 20000.0
                ]
                if um_candidates:
                    val_thk = max(um_candidates)
                    res["thickness_mm"] = val_thk
                    res["total_pe_mm"] = val_thk

        m_kv_mm = re.search(r'(\d+(?:\.\d+)?)\s{0,3}kv\s{0,2}/\s{0,2}mm\b', t)
        if m_kv_mm:
            res["holiday_kv_per_mm"] = float(m_kv_mm.group(1))

        m_kv = re.search(r'(\d+(?:\.\d+)?)\s{0,3}kv\b(?!\s*/\s*mm)', t)
        if m_kv:
            res["holiday_kv"] = float(m_kv.group(1))
        else:
            m_v = re.search(r'(\d{4,5})\s{0,3}v(?:olt)?\b(?!\s*/\s*mm)', t)
            if m_v:
                res["holiday_kv"] = float(m_v.group(1)) / 1000.0

        m_peel_cm = re.search(r'(\d+(?:\.\d+)?)\s{0,3}n\s{0,1}/\s{0,1}cm\b', t)
        if m_peel_cm:
            res["peel_n_mm"] = float(m_peel_cm.group(1)) / 10.0
        else:
            m_peel_mm = re.search(r'(\d+(?:\.\d+)?)\s{0,3}n\s{0,1}/\s{0,1}mm\b', t)
            if m_peel_mm:
                res["peel_n_mm"] = float(m_peel_mm.group(1))

        m_imp = re.search(r'(\d+(?:\.\d+)?)\s{0,3}j\s{0,1}/\s{0,1}mm\b', t)
        if m_imp:
            res["impact_j_mm"] = float(m_imp.group(1))

        m_rz = re.search(r'rz[\s:=]{0,4}(\d+)(?:\s{0,3}[-–/]\s{0,3}(\d+))?', t)
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

        m_pm = re.search(r'(?:±|\+\s{0,3}[-/]{1,2})\s{0,4}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_pm:
            val_pm = float(m_pm.group(1))
            res["plus_tol_mm"] = val_pm
            res["minus_tol_mm"] = val_pm
            res["plus_mm"] = val_pm
            res["minus_mm"] = val_pm
        else:
            t_no_ranges = re.sub(r'(?<![+-±\d.])\d+(?:\.\d+)?\s{0,4}[-–]\s{0,4}\d+(?:\.\d+)?(?:\s{0,3}mm\b)?', ' ', t)
            m_asym1 = re.search(r'[-–]\s{0,3}(\d+(?:\.\d+)?)\s{0,3}(?:mm\b)?\s{0,3}[/,;]\s{0,3}\+\s{0,3}(\d+(?:\.\d+)?)\s{0,3}mm\b', t_no_ranges)
            m_asym2 = re.search(r'\+\s{0,3}(\d+(?:\.\d+)?)\s{0,3}(?:mm\b)?\s{0,3}[/,;]\s{0,3}[-–]\s{0,3}(\d+(?:\.\d+)?)\s{0,3}mm\b', t_no_ranges)
            if m_asym1:
                v_min = float(m_asym1.group(1))
                v_pls = float(m_asym1.group(2))
                res["minus_mm"] = v_min
                res["minus_tol_mm"] = v_min
                res["plus_mm"] = v_pls
                res["plus_tol_mm"] = v_pls
            elif m_asym2:
                v_pls = float(m_asym2.group(1))
                v_min = float(m_asym2.group(2))
                res["plus_mm"] = v_pls
                res["plus_tol_mm"] = v_pls
                res["minus_mm"] = v_min
                res["minus_tol_mm"] = v_min
            else:
                m_plus = re.search(r'(?<![-/])\+\s{0,3}(\d+(?:\.\d+)?)\s{0,3}mm\b', t_no_ranges)
                if m_plus:
                    v_p = float(m_plus.group(1))
                    res["plus_mm"] = v_p
                    res["plus_tol_mm"] = v_p
                m_minus = re.search(r'(?<![+/])[-–]\s{0,3}(\d+(?:\.\d+)?)\s{0,3}mm\b', t_no_ranges)
                if m_minus:
                    v_m = float(m_minus.group(1))
                    res["minus_mm"] = v_m
                    res["minus_tol_mm"] = v_m

        t_no_pct_ranges = re.sub(r'(?<![+-±\d.])\d+(?:\.\d+)?\s{0,4}[-–]\s{0,4}\d+(?:\.\d+)?\s{0,3}%', ' ', t)
        m_pct_plus = re.search(r'\+\s{0,3}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t_no_pct_ranges)
        if m_pct_plus:
            res["plus_pct"] = float(m_pct_plus.group(1) or m_pct_plus.group(2))

        m_pct_min = re.search(r'[-–]\s{0,3}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t_no_pct_ranges)
        if m_pct_min:
            res["minus_pct"] = float(m_pct_min.group(1) or m_pct_min.group(2))

        m_min_lim = re.search(r'(?:min\.?|asgari|en\s{1,3}az|≥)[\s:=]{0,4}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_min_lim:
            res["min_limit_mm"] = float(m_min_lim.group(1))

        m_max = re.search(r'(?:max\.?|azami|en\s{1,3}çok|≤)[\s:=]{0,4}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_max:
            val_m = float(m_max.group(1))
            res["max_val_mm"] = val_m
            res["max_limit_mm"] = val_m

        m_ang = re.search(r'(\d+)\s{0,3}(?:°|deg\b|derece)', t)
        if m_ang:
            res["angle_deg"] = float(m_ang.group(1))

        m_rf = re.search(r'(?:kök|root)(?:\s{1,3}(?:yüzeyi|yuzeyi|yüzü|yuzu|face))?[\s:=]{0,6}(\d+(?:\.\d+)?)', t)
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

        m_mand = re.search(r'mandrel[^\d]{0,12}(?:ag\b)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_mand:
            res["mandrel_dia_mm"] = float(m_mand.group(1))

        m_jaw = re.search(r'(?:çene|cene|jaw)[^\d]{0,12}(?:bg\b)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_jaw:
            res["jaw_opening_mm"] = float(m_jaw.group(1))

        m_crack = re.search(r'(?:çatlak|catlak|kusur|defect|crack|açılma|acilma)[^\d]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_crack:
            res["max_crack_mm"] = float(m_crack.group(1))
        else:
            m_crack2 = re.search(r'(?:<=|≤|<|max\.?|azami)\s{0,4}(\d+(?:\.\d+)?)\s{0,3}mm\b[^\d]{0,15}(?:çatlak|catlak|kusur|defect|crack)', t)
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

        m_rep = re.search(r'(?:tek\s{1,3}tamir|tekil\s{1,3}tamir|single\s{1,3}repair|tamir\s{1,3}boyu|length\s{1,3}of\s{1,3}repair)[^\d]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_rep:
            res["max_single_repair_length_mm"] = float(m_rep.group(1))
        else:
            m_rep2 = re.search(r'(?:<=|≤|<|max\.?|azami)\s{0,4}(\d+(?:\.\d+)?)\s{0,3}mm\b[^\d]{0,15}(?:tek\s{1,3}tamir|single\s{1,3}repair)', t)
            if m_rep2:
                res["max_single_repair_length_mm"] = float(m_rep2.group(1))

        m_end = re.search(r'(?:uçta|ucta|uçtan|uctan|from\s{1,3}ends?|pipe\s{1,3}ends?)[^\d]{0,15}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_end:
            res["end_restriction_distance_mm"] = float(m_end.group(1))
        else:
            m_end2 = re.search(r'(\d+(?:\.\d+)?)\s{0,3}mm\b[^\d]{0,15}(?:uç|uc|end)', t)
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

        m_end = re.search(r'(?:uç\s{1,3}ovalite|ovalite\s{1,3}uç|uc\s{1,3}ovalite|ovalite\s{1,3}uc|end\s{1,3}ovality|ovality\s{1,3}ends?|out-of-roundness\s{1,3}ends?)[^\d]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_end:
            res["ovality_end_max_mm"] = float(m_end.group(1))
            res["ovality_max_mm"] = float(m_end.group(1))

        m_body = re.search(r'(?:gövde\s{1,3}ovalite|govde\s{1,3}ovalite|body\s{1,3}ovality|ovality\s{1,3}body|out-of-roundness\s{1,3}body)[^\d]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
        if m_body:
            res["ovality_body_max_mm"] = float(m_body.group(1))
            if res["ovality_max_mm"] is None:
                res["ovality_max_mm"] = float(m_body.group(1))

        if res["ovality_max_mm"] is None:
            m_gen = re.search(r'(?:ovality|ovalite|roundness|yuvarlaklık|yuvarlaklik|dairesellik)[^\d]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(\d+(?:\.\d+)?)\s{0,3}mm\b', t)
            if m_gen:
                res["ovality_max_mm"] = float(m_gen.group(1))

        m_pct = re.search(r'(?:ovality|ovalite|roundness)[^\d%]{0,15}(?:<=|≤|<|max\.?|azami)?[\s:=]{0,6}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t)
        if m_pct:
            res["ovality_pct"] = float(m_pct.group(1) or m_pct.group(2))

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

        m_w = re.search(r'(?:teorik|nominal|(?<![a-z0-9])w\b|birim\s{1,3}ağırlık|weight)?[^\d]{0,10}(\d+(?:\.\d+)?)\s{0,3}kg/m\b', t)
        if m_w:
            res["nominal_kg_m"] = float(m_w.group(1))

        m_pm = re.search(r'(?:±|\+\s{0,3}[-/]{1,2})\s{0,3}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t)
        if m_pm:
            v_pm = float(m_pm.group(1) or m_pm.group(2))
            res["minus_pct"] = v_pm
            res["plus_pct"] = v_pm
        else:
            t_no_pct_ranges = re.sub(r'(?<![+-±\d.])\d+(?:\.\d+)?\s{0,4}[-–]\s{0,4}\d+(?:\.\d+)?\s{0,3}%', ' ', t)
            m_min = re.search(r'[-–]\s{0,3}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t_no_pct_ranges)
            if m_min:
                res["minus_pct"] = float(m_min.group(1) or m_min.group(2))

            m_pls = re.search(r'\+\s{0,3}(?:%\s{0,2}(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s{0,2}%)', t_no_pct_ranges)
            if m_pls:
                res["plus_pct"] = float(m_pls.group(1) or m_pls.group(2))

        return res
