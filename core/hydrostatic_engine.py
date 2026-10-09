"""
API 5L PSL2 & BOTAŞ Mill Hydrostatic Pressure Test Engine.
Implements API 5L Clause 10.2.6 & Equation 6 (P = 2·S·t / D),
BOTAŞ Specification Clause 8.4 (%100 SMYS test pressure, min 20 sec holding time),
pipe internal water volume, water tonnage, elastic volumetric expansion (dV/dP),
water compressibility, and hydrostatic test pressure-time cycle modeling.
"""

import math
from typing import Dict, Any, Optional

# Constants
STEEL_E_MPA = 206000.0          # Young's modulus of carbon steel (MPa)
STEEL_POISSON = 0.30            # Poisson's ratio
WATER_BULK_MODULUS_MPA = 2200.0 # Bulk modulus of ambient test water (MPa)
WATER_DENSITY_KG_M3 = 1000.0    # Density of fresh test water (kg/m^3)


def compute_hydrostatic_calc(
    d_mm: float,
    t_mm: float,
    smys_mpa: float = 450.0,
    pipe_length_m: float = 12.0,
    is_botas: bool = True,
    press_cap_bar: float = 250.0,
) -> Dict[str, Any]:
    """
    Computes hydrostatic test pressures, hoop stresses, test water volume,
    fill tonnage, pressure-induced elastic expansion, and holding time specifications.
    """
    d = float(d_mm)
    t = float(t_mm if t_mm is not None else 0.0)
    smys = float(smys_mpa if smys_mpa and smys_mpa > 0 else 450.0)
    l_pipe = float(pipe_length_m if pipe_length_m and pipe_length_m > 0 else 12.0)
    cap_bar = float(press_cap_bar if press_cap_bar and press_cap_bar > 0 else 250.0)

    din_mm = max(0.0, d - 2.0 * t)
    din_m = din_mm / 1000.0
    d_m = d / 1000.0
    t_m = t / 1000.0

    # 1. API 5L Equation 6 Hydrostatic Test Pressure (P = 2 * S * t / D)
    # S = Fiber stress:
    #   - BOTAŞ: 100% of SMYS
    #   - API 5L PSL2 Standard: 95% of SMYS (Table 26)
    #   - API 5L PSL1: 75% of SMYS
    # P (MPa) = (2 * S_mpa * t_mm) / d_mm
    # P (bar) = P_mpa * 10.0
    s_botas_mpa = smys * 1.00
    s_api_95_mpa = smys * 0.95
    s_api_90_mpa = smys * 0.90

    p_botas_bar_theo = ((2.0 * s_botas_mpa * t) / d * 10.0) if d > 0 else 0.0
    p_api_95_bar_theo = ((2.0 * s_api_95_mpa * t) / d * 10.0) if d > 0 else 0.0
    p_api_90_bar_theo = ((2.0 * s_api_90_mpa * t) / d * 10.0) if d > 0 else 0.0

    # Governing target pressure based on selected specification
    governing_spec = "BOTAŞ Madde 8.4 (%100 SMYS)" if is_botas else "API 5L PSL2 (%95 SMYS)"
    target_p_bar_theo = p_botas_bar_theo if is_botas else p_api_95_bar_theo

    # Hydro test bench capacity clamp
    p_clamped = min(target_p_bar_theo, cap_bar)
    bench_limited = p_clamped < target_p_bar_theo

    # Minimum acceptable test pressure (gauge lower tolerance)
    # BOTAŞ allows +0 / -2.0 bar gauge tolerance
    min_acceptable_p_bar = max(0.0, p_clamped - 2.0)

    # Actual hoop stress under clamped test pressure
    # sigma_h = (P_bar * d_mm) / (20.0 * t_mm)  (in MPa)
    sigma_hoop_mpa = ((p_clamped / 10.0) * d / (2.0 * t)) if t > 0 else 0.0
    hoop_stress_ratio_pct = (sigma_hoop_mpa / smys * 100.0) if smys > 0 else 0.0

    # 2. Water Filling Volume and Tonnage
    # Internal volume: V0 = pi/4 * Din^2 * L
    area_in_m2 = (math.pi / 4.0) * (din_m ** 2)
    vol_water_m3 = area_in_m2 * l_pipe
    vol_water_liters = vol_water_m3 * 1000.0
    water_mass_kg = vol_water_m3 * WATER_DENSITY_KG_M3
    water_mass_tons = water_mass_kg / 1000.0

    # Theoretical empty pipe weight (API 5L formula: (D - t) * t * 0.0246615 * L)
    pipe_dry_mass_kg = ((d - t) * t * 0.0246615 * l_pipe) if d > t else 0.0
    pipe_dry_mass_tons = pipe_dry_mass_kg / 1000.0
    pipe_flooded_mass_tons = pipe_dry_mass_tons + water_mass_tons

    # 3. Elastic Volumetric Expansion & Additional Pressurization Water (dV/dP)
    # Radial elastic strain under test pressure:
    # eps_h = (sigma_h - nu * sigma_z) / E = [ (P*D)/(2t) * (1 - nu/2) ] / E
    # Volumetric pipe strain: dV_pipe / V0 = 2 * eps_h = [ (P*D)/(t*E) * (1 - nu/2) ]
    # Water compressibility strain: dV_water / V0 = P / K_water
    # P in MPa: P_mpa = p_clamped / 10.0
    p_mpa = p_clamped / 10.0
    vol_strain_pipe = ((p_mpa * d) / (t * STEEL_E_MPA) * (1.0 - STEEL_POISSON / 2.0)) if t > 0 else 0.0
    vol_strain_water = (p_mpa / WATER_BULK_MODULUS_MPA)
    total_vol_strain = vol_strain_pipe + vol_strain_water

    delta_vol_liters = vol_water_liters * total_vol_strain
    delta_vol_pct = total_vol_strain * 100.0

    # Circumferential expansion under test pressure:
    # delta_circ_mm = pi * D * eps_h
    delta_circ_mm = math.pi * d * (vol_strain_pipe / 2.0)

    # 4. Holding Time & Inspection Cycle
    # API 5L 10.2.6.2: >= 10 sec for welded pipe D > 457 mm (or 5 sec for small)
    # BOTAŞ 8.4: >= 20 sec mandatory with continuous chart recording
    holding_time_sec = 20 if is_botas else (10 if d > 457.0 else 5)
    fill_time_sec = max(10, int(round(vol_water_liters / 150.0)))   # approx. 150 L/s fill pump
    pressurize_time_sec = max(6, int(round(p_clamped / 18.0)))       # approx. 18 bar/s intensifier
    depressurize_time_sec = 6
    total_cycle_sec = fill_time_sec + pressurize_time_sec + holding_time_sec + depressurize_time_sec

    # Verdict & Safety Notes
    safe_test = not bench_limited and hoop_stress_ratio_pct >= (98.0 if is_botas else 93.0)
    if safe_test:
        test_status = "PASS"
        test_note = (
            f"UYGUN (PASS): Test basıncı {p_clamped:.1f} bar, SMYS'in %{hoop_stress_ratio_pct:.1f}'ine "
            f"ulaşarak boru gövdesini tam akma sınırında başarıyla test eder. Tutma süresi {holding_time_sec} sn."
        )
    elif bench_limited:
        test_status = "BENCH_LIMITED"
        test_note = (
            f"UYARI (PRES SINIRI): Teorik test basıncı {target_p_bar_theo:.1f} bar iken, "
            f"pres kafası mekanik kapasitesi ({cap_bar:.0f} bar) nedeniyle basınç sınırlandırılmıştır (SMYS %{hoop_stress_ratio_pct:.1f})."
        )
    else:
        test_status = "PASS"
        test_note = f"UYGUN (PASS): Test basıncı {p_clamped:.1f} bar (SMYS %{hoop_stress_ratio_pct:.1f})."

    return {
        "d_mm": round(d, 2),
        "t_mm": round(t, 2),
        "d_in_mm": round(din_mm, 2),
        "pipe_length_m": round(l_pipe, 2),
        "smys_mpa": round(smys, 1),
        "is_botas": is_botas,
        "governing_spec": governing_spec,
        # Test Pressures
        "p_botas_100_smys_bar": round(p_botas_bar_theo, 1),
        "p_api_95_smys_bar": round(p_api_95_bar_theo, 1),
        "p_api_90_smys_bar": round(p_api_90_bar_theo, 1),
        "target_test_pressure_bar": round(p_clamped, 1),
        "min_acceptable_pressure_bar": round(min_acceptable_p_bar, 1),
        "press_bench_capacity_bar": round(cap_bar, 1),
        "bench_limited": bench_limited,
        # Stresses
        "sigma_hoop_mpa": round(sigma_hoop_mpa, 1),
        "hoop_stress_ratio_percent": round(hoop_stress_ratio_pct, 1),
        # Water & Weights
        "water_volume_m3": round(vol_water_m3, 3),
        "water_volume_liters": round(vol_water_liters, 1),
        "water_mass_tons": round(water_mass_tons, 3),
        "pipe_dry_mass_tons": round(pipe_dry_mass_tons, 3),
        "pipe_flooded_mass_tons": round(pipe_flooded_mass_tons, 3),
        # Elastic & Volumetric Expansion
        "additional_water_liters": round(delta_vol_liters, 2),
        "volumetric_expansion_percent": round(delta_vol_pct, 3),
        "circumferential_expansion_mm": round(delta_circ_mm, 2),
        # Timing Cycle
        "holding_time_sec": holding_time_sec,
        "fill_time_sec": fill_time_sec,
        "pressurize_time_sec": pressurize_time_sec,
        "total_test_cycle_sec": total_cycle_sec,
        # Verdict
        "test_status": test_status,
        "test_note": test_note,
        "formula": "P = 2·S·t / D,  S_botas = 1.00·SMYS,  S_api = 0.95·SMYS,  V_su = π/4·Din²·L",
    }
