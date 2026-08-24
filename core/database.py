"""
Database containing standards for API 5L PSL2, BOTAŞ Specifications, ASME B31.8 & ASME B36.10.
Generated automatically from verified Excel data source with accurate column mappings.
"""

# API 5L PSL2 Steel Grades SMYS & Mechanical Properties
API_5L_SMYS_TABLE = {
    "GRADE A": {
        "grade": "GRADE A",
        "iso_grade": "L210",
        "smys_psi": 30500.0,
        "yield_tensile_max": 0.9,
        "cvn_material_j": 0.0,
        "cvn_weld_j": 0.0,
        "yield_min_mpa": 210.0,
        "yield_max_psi": 0.0,
        "yield_max_mpa": 0.0,
        "tensile_min_psi": 0.0,
        "tensile_min_mpa": 0.0,
        "tensile_max_psi": 0.0,
        "tensile_max_mpa": 0.0,
        "strain_value": 0.1
    },
    "GRADE B": {
        "grade": "GRADE B",
        "iso_grade": "L245",
        "smys_psi": 35500.0,
        "yield_tensile_max": 0.8,
        "cvn_material_j": 27.0,
        "cvn_weld_j": 27.0,
        "yield_min_mpa": 245.0,
        "yield_max_psi": 65300.0,
        "yield_max_mpa": 450.0,
        "tensile_min_psi": 60200.0,
        "tensile_min_mpa": 415.0,
        "tensile_max_psi": 95000.0,
        "tensile_max_mpa": 655.0,
        "strain_value": 0.1375
    },
    "X42": {
        "grade": "X42",
        "iso_grade": "L290",
        "smys_psi": 42100.0,
        "yield_tensile_max": 0.85,
        "cvn_material_j": 27.0,
        "cvn_weld_j": 27.0,
        "yield_min_mpa": 290.0,
        "yield_max_psi": 71800.0,
        "yield_max_mpa": 495.0,
        "tensile_min_psi": 60200.0,
        "tensile_min_mpa": 415.0,
        "tensile_max_psi": 95000.0,
        "tensile_max_mpa": 655.0,
        "strain_value": 0.1375
    },
    "X46": {
        "grade": "X46",
        "iso_grade": "L320",
        "smys_psi": 46400.0,
        "yield_tensile_max": 0.85,
        "cvn_material_j": 48.0,
        "cvn_weld_j": 36.0,
        "yield_min_mpa": 320.0,
        "yield_max_psi": 76100.0,
        "yield_max_mpa": 525.0,
        "tensile_min_psi": 63100.0,
        "tensile_min_mpa": 435.0,
        "tensile_max_psi": 95000.0,
        "tensile_max_mpa": 655.0,
        "strain_value": 0.1325
    },
    "X52": {
        "grade": "X52",
        "iso_grade": "L360",
        "smys_psi": 52200.0,
        "yield_tensile_max": 0.87,
        "cvn_material_j": 48.0,
        "cvn_weld_j": 36.0,
        "yield_min_mpa": 360.0,
        "yield_max_psi": 76900.0,
        "yield_max_mpa": 530.0,
        "tensile_min_psi": 66700.0,
        "tensile_min_mpa": 460.0,
        "tensile_max_psi": 110200.0,
        "tensile_max_mpa": 760.0,
        "strain_value": 0.125
    },
    "X56": {
        "grade": "X56",
        "iso_grade": "L390",
        "smys_psi": 56600.0,
        "yield_tensile_max": 0.87,
        "cvn_material_j": 48.0,
        "cvn_weld_j": 36.0,
        "yield_min_mpa": 390.0,
        "yield_max_psi": 79000.0,
        "yield_max_mpa": 545.0,
        "tensile_min_psi": 71100.0,
        "tensile_min_mpa": 490.0,
        "tensile_max_psi": 110200.0,
        "tensile_max_mpa": 760.0,
        "strain_value": 0.1175
    },
    "X60": {
        "grade": "X60",
        "iso_grade": "L415",
        "smys_psi": 60200.0,
        "yield_tensile_max": 0.9,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 415.0,
        "yield_max_psi": 81900.0,
        "yield_max_mpa": 565.0,
        "tensile_min_psi": 75400.0,
        "tensile_min_mpa": 520.0,
        "tensile_max_psi": 110200.0,
        "tensile_max_mpa": 760.0,
        "strain_value": 0.1125
    },
    "X65": {
        "grade": "X65",
        "iso_grade": "L450",
        "smys_psi": 65300.0,
        "yield_tensile_max": 0.9,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 450.0,
        "yield_max_psi": 87000.0,
        "yield_max_mpa": 600.0,
        "tensile_min_psi": 77600.0,
        "tensile_min_mpa": 535.0,
        "tensile_max_psi": 110200.0,
        "tensile_max_mpa": 760.0,
        "strain_value": 0.11
    },
    "X70": {
        "grade": "X70",
        "iso_grade": "L485",
        "smys_psi": 70300.0,
        "yield_tensile_max": 0.93,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 485.0,
        "yield_max_psi": 92100.0,
        "yield_max_mpa": 635.0,
        "tensile_min_psi": 82700.0,
        "tensile_min_mpa": 570.0,
        "tensile_max_psi": 110200.0,
        "tensile_max_mpa": 760.0,
        "strain_value": 0.1025
    },
    "X80": {
        "grade": "X80",
        "iso_grade": "L555",
        "smys_psi": 80500.0,
        "yield_tensile_max": 0.93,
        "cvn_material_j": 90.0,
        "cvn_weld_j": 68.0,
        "yield_min_mpa": 555.0,
        "yield_max_psi": 102300.0,
        "yield_max_mpa": 705.0,
        "tensile_min_psi": 90600.0,
        "tensile_min_mpa": 625.0,
        "tensile_max_psi": 119700.0,
        "tensile_max_mpa": 825.0,
        "strain_value": 0.095
    },
    "X90": {
        "grade": "X90",
        "iso_grade": "L625",
        "smys_psi": 90600.0,
        "yield_tensile_max": 0.95,
        "cvn_material_j": 0.0,
        "cvn_weld_j": 0.0,
        "yield_min_mpa": 625.0,
        "yield_max_psi": 112400.0,
        "yield_max_mpa": 775.0,
        "tensile_min_psi": 100800.0,
        "tensile_min_mpa": 695.0,
        "tensile_max_psi": 132700.0,
        "tensile_max_mpa": 915.0,
        "strain_value": 0.085
    },
    "X100": {
        "grade": "X100",
        "iso_grade": "L690",
        "smys_psi": 100100.0,
        "yield_tensile_max": 0.97,
        "cvn_material_j": 0.0,
        "cvn_weld_j": 0.0,
        "yield_min_mpa": 690.0,
        "yield_max_psi": 121800.0,
        "yield_max_mpa": 840.0,
        "tensile_min_psi": 110200.0,
        "tensile_min_mpa": 760.0,
        "tensile_max_psi": 143600.0,
        "tensile_max_mpa": 990.0,
        "strain_value": 0.08
    },
    "X120": {
        "grade": "X120",
        "iso_grade": "L830",
        "smys_psi": 120400.0,
        "yield_tensile_max": 0.99,
        "cvn_material_j": 0.0,
        "cvn_weld_j": 0.0,
        "yield_min_mpa": 830.0,
        "yield_max_psi": 152300.0,
        "yield_max_mpa": 1050.0,
        "tensile_min_psi": 132700.0,
        "tensile_min_mpa": 915.0,
        "tensile_max_psi": 166100.0,
        "tensile_max_mpa": 1145.0,
        "strain_value": 0.0675
    },
    "SS 304 / 304L": {
        "grade": "SS 304 / 304L",
        "iso_grade": "TP304L",
        "smys_psi": 30000.0,
        "yield_tensile_max": 0.85,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 205.0,
        "yield_max_psi": 58000.0,
        "yield_max_mpa": 400.0,
        "tensile_min_psi": 70000.0,
        "tensile_min_mpa": 485.0,
        "tensile_max_psi": 95000.0,
        "tensile_max_mpa": 655.0,
        "allowable_stress_mpa": 115.0,
        "allowable_stress_psi": 16700.0,
        "strain_value": 0.35,
        "is_stainless": True
    },
    "SS 316 / 316L": {
        "grade": "SS 316 / 316L",
        "iso_grade": "TP316L",
        "smys_psi": 30000.0,
        "yield_tensile_max": 0.85,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 205.0,
        "yield_max_psi": 58000.0,
        "yield_max_mpa": 400.0,
        "tensile_min_psi": 70000.0,
        "tensile_min_mpa": 485.0,
        "tensile_max_psi": 95000.0,
        "tensile_max_mpa": 655.0,
        "allowable_stress_mpa": 115.0,
        "allowable_stress_psi": 16700.0,
        "strain_value": 0.35,
        "is_stainless": True
    },
    "SS 321": {
        "grade": "SS 321",
        "iso_grade": "TP321",
        "smys_psi": 30000.0,
        "yield_tensile_max": 0.85,
        "cvn_material_j": 60.0,
        "cvn_weld_j": 45.0,
        "yield_min_mpa": 205.0,
        "yield_max_psi": 58000.0,
        "yield_max_mpa": 400.0,
        "tensile_min_psi": 75000.0,
        "tensile_min_mpa": 515.0,
        "tensile_max_psi": 100000.0,
        "tensile_max_mpa": 690.0,
        "allowable_stress_mpa": 115.0,
        "allowable_stress_psi": 16700.0,
        "strain_value": 0.35,
        "is_stainless": True
    },
    "Duplex 2205": {
        "grade": "Duplex 2205",
        "iso_grade": "UNS S32205",
        "smys_psi": 65300.0,
        "yield_tensile_max": 0.88,
        "cvn_material_j": 80.0,
        "cvn_weld_j": 60.0,
        "yield_min_mpa": 450.0,
        "yield_max_psi": 95000.0,
        "yield_max_mpa": 655.0,
        "tensile_min_psi": 95000.0,
        "tensile_min_mpa": 655.0,
        "tensile_max_psi": 130000.0,
        "tensile_max_mpa": 900.0,
        "allowable_stress_mpa": 175.0,
        "allowable_stress_psi": 25400.0,
        "strain_value": 0.25,
        "is_stainless": True
    },
    "Super Duplex 2507": {
        "grade": "Super Duplex 2507",
        "iso_grade": "UNS S32750",
        "smys_psi": 80000.0,
        "yield_tensile_max": 0.90,
        "cvn_material_j": 80.0,
        "cvn_weld_j": 60.0,
        "yield_min_mpa": 550.0,
        "yield_max_psi": 110000.0,
        "yield_max_mpa": 760.0,
        "tensile_min_psi": 110000.0,
        "tensile_min_mpa": 760.0,
        "tensile_max_psi": 145000.0,
        "tensile_max_mpa": 1000.0,
        "allowable_stress_mpa": 210.0,
        "allowable_stress_psi": 30500.0,
        "strain_value": 0.20,
        "is_stainless": True
    }
}

# Chemical Composition Limits (API 5L PSL2 & BOTAŞ & Stainless)
CHEMICAL_COMPOSITION_RULES = {
    'GRADE A': {'C_max': 0.22, 'Mn_max': 0.90, 'P_max': 0.025, 'S_max': 0.015, 'Nb_min': 0.0, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.012, 'CE_IIW_max': 0.42, 'CE_Pcm_max': 0.24},
    'GRADE B': {'C_max': 0.18, 'Mn_max': 1.20, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.0, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.42, 'CE_Pcm_max': 0.24},
    'X42':     {'C_max': 0.18, 'Mn_max': 1.30, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.0, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.42, 'CE_Pcm_max': 0.24},
    'X46':     {'C_max': 0.18, 'Mn_max': 1.30, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.0, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.42, 'CE_Pcm_max': 0.24},
    'X52':     {'C_max': 0.18, 'Mn_max': 1.40, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.0, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X56':     {'C_max': 0.18, 'Mn_max': 1.40, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.015, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X60':     {'C_max': 0.12, 'Mn_max': 1.60, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.015, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X65':     {'C_max': 0.12, 'Mn_max': 1.60, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.015, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X70':     {'C_max': 0.12, 'Mn_max': 1.70, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.015, 'Nb_max': 0.05, 'V_max': 0.05, 'Ti_max': 0.04, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X80':     {'C_max': 0.12, 'Mn_max': 1.85, 'P_max': 0.025, 'S_max': 0.010, 'Nb_min': 0.015, 'Nb_max': 0.06, 'V_max': 0.06, 'Ti_max': 0.05, 'N_max': 0.009, 'CE_IIW_max': 0.43, 'CE_Pcm_max': 0.25},
    'X90':     {'C_max': 0.10, 'Mn_max': 1.90, 'P_max': 0.020, 'S_max': 0.008, 'Nb_min': 0.015, 'Nb_max': 0.06, 'V_max': 0.06, 'Ti_max': 0.05, 'N_max': 0.009, 'CE_IIW_max': 0.44, 'CE_Pcm_max': 0.25},
    'X100':    {'C_max': 0.10, 'Mn_max': 1.95, 'P_max': 0.020, 'S_max': 0.008, 'Nb_min': 0.015, 'Nb_max': 0.06, 'V_max': 0.06, 'Ti_max': 0.05, 'N_max': 0.009, 'CE_IIW_max': 0.44, 'CE_Pcm_max': 0.25},
    'X120':    {'C_max': 0.10, 'Mn_max': 2.00, 'P_max': 0.015, 'S_max': 0.006, 'Nb_min': 0.015, 'Nb_max': 0.06, 'V_max': 0.06, 'Ti_max': 0.05, 'N_max': 0.009, 'CE_IIW_max': 0.45, 'CE_Pcm_max': 0.26},
    'SS 304 / 304L': {'C_max': 0.030, 'Mn_max': 2.00, 'P_max': 0.045, 'S_max': 0.030, 'Nb_min': 0.0, 'Nb_max': 0.0, 'V_max': 0.0, 'Ti_max': 0.0, 'N_max': 0.10, 'CE_IIW_max': 0.0, 'CE_Pcm_max': 0.0},
    'SS 316 / 316L': {'C_max': 0.030, 'Mn_max': 2.00, 'P_max': 0.045, 'S_max': 0.030, 'Nb_min': 0.0, 'Nb_max': 0.0, 'V_max': 0.0, 'Ti_max': 0.0, 'N_max': 0.10, 'CE_IIW_max': 0.0, 'CE_Pcm_max': 0.0},
    'SS 321':        {'C_max': 0.080, 'Mn_max': 2.00, 'P_max': 0.045, 'S_max': 0.030, 'Nb_min': 0.0, 'Nb_max': 0.0, 'V_max': 0.0, 'Ti_max': 0.70, 'N_max': 0.10, 'CE_IIW_max': 0.0, 'CE_Pcm_max': 0.0},
    'Duplex 2205':   {'C_max': 0.030, 'Mn_max': 2.00, 'P_max': 0.030, 'S_max': 0.020, 'Nb_min': 0.0, 'Nb_max': 0.0, 'V_max': 0.0, 'Ti_max': 0.0, 'N_max': 0.20, 'CE_IIW_max': 0.0, 'CE_Pcm_max': 0.0},
    'Super Duplex 2507': {'C_max': 0.030, 'Mn_max': 1.20, 'P_max': 0.035, 'S_max': 0.020, 'Nb_min': 0.0, 'Nb_max': 0.0, 'V_max': 0.0, 'Ti_max': 0.0, 'N_max': 0.32, 'CE_IIW_max': 0.0, 'CE_Pcm_max': 0.0}
}

# API 5L 46th Ed. Table 8 (PSL2) minimum absorbed energy (J), full-size specimen, average of 3, 0 °C.
# DRAFT — values to be verified against the exact Table 8 of the 46th edition.
CVN_API5L = {
    "GRADE A": {"material_j": 27.0, "weld_j": 20.0},
    "GRADE B": {"material_j": 27.0, "weld_j": 20.0},
    "X42": {"material_j": 27.0, "weld_j": 20.0},
    "X46": {"material_j": 27.0, "weld_j": 20.0},
    "X52": {"material_j": 27.0, "weld_j": 20.0},
    "X56": {"material_j": 40.0, "weld_j": 27.0},
    "X60": {"material_j": 40.0, "weld_j": 27.0},
    "X65": {"material_j": 40.0, "weld_j": 27.0},
    "X70": {"material_j": 40.0, "weld_j": 27.0},
    "X80": {"material_j": 68.0, "weld_j": 54.0},
}

# Design factor canonical key -> numeric F value.
DESIGN_FACTOR_MAP = {
    "0.80_hat": 0.80,
    "0.72_hat": 0.72,
    "0.60_hat": 0.60,
    "0.50_hat": 0.50,
    "0.50_ist1": 0.50,
    "0.50_ist2": 0.50,
    "0.40_hat": 0.40,
}

# Standard Pipe Sizes, Wall Thicknesses & Tolerances (BOTAŞ & ASME B31.8)
PIPE_SIZES_TABLE = [
    {
        "inch": "½\"",
        "mm": 21.3,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 3.7,
            "0.50_ist2": 3.7
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 3.73,
            "0.50_ist2": 3.73
        },
        "diameter_tol_botas": {
            "end_max": 21.7,
            "end_min": 20.5,
            "body_max": 21.7,
            "body_min": 20.5
        },
        "diameter_tol_asme": {
            "end_max": 21.7,
            "end_min": 20.5,
            "body_max": 21.7,
            "body_min": 20.5
        },
        "ovality": {
            "end": "0.45",
            "body": "1.2"
        }
    },
    {
        "inch": "¾\"",
        "mm": 26.7,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 3.9,
            "0.50_ist2": 3.9
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 3.91,
            "0.50_ist2": 3.91
        },
        "diameter_tol_botas": {
            "end_max": 27.099999999999998,
            "end_min": 25.9,
            "body_max": 27.099999999999998,
            "body_min": 25.9
        },
        "diameter_tol_asme": {
            "end_max": 27.099999999999998,
            "end_min": 25.9,
            "body_max": 27.099999999999998,
            "body_min": 25.9
        },
        "ovality": {
            "end": "0.45",
            "body": "1.2"
        }
    },
    {
        "inch": "1\"",
        "mm": 33.4,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 4.6,
            "0.50_ist2": 4.6
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 4.55,
            "0.50_ist2": 4.55
        },
        "diameter_tol_botas": {
            "end_max": 33.8,
            "end_min": 32.6,
            "body_max": 33.8,
            "body_min": 32.6
        },
        "diameter_tol_asme": {
            "end_max": 33.8,
            "end_min": 32.6,
            "body_max": 33.8,
            "body_min": 32.6
        },
        "ovality": {
            "end": "0.45",
            "body": "1.2"
        }
    },
    {
        "inch": "1¼\"",
        "mm": 42.2,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 4.9,
            "0.50_ist2": 4.9
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 4.85,
            "0.50_ist2": 4.85
        },
        "diameter_tol_botas": {
            "end_max": 42.6,
            "end_min": 41.400000000000006,
            "body_max": 42.6,
            "body_min": 41.400000000000006
        },
        "diameter_tol_asme": {
            "end_max": 42.6,
            "end_min": 41.400000000000006,
            "body_max": 42.6,
            "body_min": 41.400000000000006
        },
        "ovality": {
            "end": "0.45",
            "body": "1.2"
        }
    },
    {
        "inch": "1½\"",
        "mm": 48.3,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.1,
            "0.50_ist2": 5.1
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.08,
            "0.50_ist2": 5.08
        },
        "diameter_tol_botas": {
            "end_max": 48.699999999999996,
            "end_min": 47.5,
            "body_max": 48.699999999999996,
            "body_min": 47.5
        },
        "diameter_tol_asme": {
            "end_max": 48.699999999999996,
            "end_min": 47.5,
            "body_max": 48.699999999999996,
            "body_min": 47.5
        },
        "ovality": {
            "end": "0.45",
            "body": "1.2"
        }
    },
    {
        "inch": "2\"",
        "mm": 60.3,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.5,
            "0.50_ist2": 5.5
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.54,
            "0.50_ist2": 5.54
        },
        "diameter_tol_botas": {
            "end_max": 61.9,
            "end_min": 59.9,
            "body_max": 60.752250000000004,
            "body_min": 59.84775
        },
        "diameter_tol_asme": {
            "end_max": 61.9,
            "end_min": 59.9,
            "body_max": 60.752250000000004,
            "body_min": 59.84775
        },
        "ovality": {
            "end": "0.45225",
            "body": "1.206"
        }
    },
    {
        "inch": "2½\"",
        "mm": 73.0,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.2,
            "0.50_ist2": 5.2
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.16,
            "0.50_ist2": 5.16
        },
        "diameter_tol_botas": {
            "end_max": 74.6,
            "end_min": 72.6,
            "body_max": 73.5475,
            "body_min": 72.4525
        },
        "diameter_tol_asme": {
            "end_max": 74.6,
            "end_min": 72.6,
            "body_max": 73.5475,
            "body_min": 72.4525
        },
        "ovality": {
            "end": "0.5475",
            "body": "1.46"
        }
    },
    {
        "inch": "3\"",
        "mm": 88.9,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.5,
            "0.50_ist2": 5.5
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 5.49,
            "0.50_ist2": 5.49
        },
        "diameter_tol_botas": {
            "end_max": 90.5,
            "end_min": 88.5,
            "body_max": 89.56675000000001,
            "body_min": 88.23325000000001
        },
        "diameter_tol_asme": {
            "end_max": 90.5,
            "end_min": 88.5,
            "body_max": 89.56675000000001,
            "body_min": 88.23325000000001
        },
        "ovality": {
            "end": "0.6667500000000001",
            "body": "1.7780000000000002"
        }
    },
    {
        "inch": "4\"",
        "mm": 114.3,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 6.0,
            "0.50_ist2": 6.0
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 6.02,
            "0.50_ist2": 6.02
        },
        "diameter_tol_botas": {
            "end_max": 115.89999999999999,
            "end_min": 113.89999999999999,
            "body_max": 115.15725,
            "body_min": 113.44275
        },
        "diameter_tol_asme": {
            "end_max": 115.89999999999999,
            "end_min": 113.89999999999999,
            "body_max": 115.15725,
            "body_min": 113.44275
        },
        "ovality": {
            "end": "0.85725",
            "body": "2.286"
        }
    },
    {
        "inch": "5\"",
        "mm": 141.3,
        "default_material": "GRADE B",
        "botas_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 6.6,
            "0.50_ist2": 7.1
        },
        "asme_thk": {
            "0.72_hat": 0.0,
            "0.60_hat": 0.0,
            "0.50_hat": 0.0,
            "0.50_ist1": 6.55,
            "0.50_ist2": 7.1
        },
        "diameter_tol_botas": {
            "end_max": 142.9,
            "end_min": 140.9,
            "body_max": 142.35975000000002,
            "body_min": 140.24025000000003
        },
        "diameter_tol_asme": {
            "end_max": 142.9,
            "end_min": 140.9,
            "body_max": 142.35975000000002,
            "body_min": 140.24025000000003
        },
        "ovality": {
            "end": "1.05975",
            "body": "2.826"
        }
    },
    {
        "inch": "6\"",
        "mm": 168.3,
        "default_material": "X42",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 5.2,
            "0.50_hat": 5.2,
            "0.50_ist1": 6.4,
            "0.50_ist2": 6.4
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 5.16,
            "0.50_hat": 5.16,
            "0.50_ist1": 6.35,
            "0.50_ist2": 6.35
        },
        "diameter_tol_botas": {
            "end_max": 169.14149999999998,
            "end_min": 167.45850000000002,
            "body_max": 169.56225000000003,
            "body_min": 167.03775000000002
        },
        "diameter_tol_asme": {
            "end_max": 169.14149999999998,
            "end_min": 167.45850000000002,
            "body_max": 169.56225000000003,
            "body_min": 167.03775000000002
        },
        "ovality": {
            "end": "1.26225",
            "body": "3.366"
        }
    },
    {
        "inch": "8\"",
        "mm": 219.1,
        "default_material": "X42",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 5.2,
            "0.50_hat": 6.4,
            "0.50_ist1": 7.9,
            "0.50_ist2": 7.9
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 5.16,
            "0.50_hat": 6.35,
            "0.50_ist1": 7.92,
            "0.50_ist2": 7.92
        },
        "diameter_tol_botas": {
            "end_max": 220.19549999999998,
            "end_min": 218.0045,
            "body_max": 220.74325000000002,
            "body_min": 217.45675
        },
        "diameter_tol_asme": {
            "end_max": 220.19549999999998,
            "end_min": 218.0045,
            "body_max": 220.74325000000002,
            "body_min": 217.45675
        },
        "ovality": {
            "end": "1.6432499999999999",
            "body": "4.382"
        }
    },
    {
        "inch": "10\"",
        "mm": 273.1,
        "default_material": "X46",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 5.6,
            "0.50_hat": 7.1,
            "0.50_ist1": 8.7,
            "0.50_ist2": 8.7
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 5.56,
            "0.50_hat": 7.09,
            "0.50_ist1": 8.74,
            "0.50_ist2": 8.74
        },
        "diameter_tol_botas": {
            "end_max": 274.4655,
            "end_min": 271.7345,
            "body_max": 275.14825,
            "body_min": 271.05175
        },
        "diameter_tol_asme": {
            "end_max": 274.4655,
            "end_min": 271.7345,
            "body_max": 275.14825,
            "body_min": 271.05175
        },
        "ovality": {
            "end": "2.04825",
            "body": "5.462000000000001"
        }
    },
    {
        "inch": "12\"",
        "mm": 323.9,
        "default_material": "X52",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 6.4,
            "0.50_hat": 7.1,
            "0.50_ist1": 8.4,
            "0.50_ist2": 9.5
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 6.35,
            "0.50_hat": 7.14,
            "0.50_ist1": 8.38,
            "0.50_ist2": 9.53
        },
        "diameter_tol_botas": {
            "end_max": 325.5,
            "end_min": 322.29999999999995,
            "body_max": 326.32925,
            "body_min": 321.47075
        },
        "diameter_tol_asme": {
            "end_max": 325.5,
            "end_min": 322.29999999999995,
            "body_max": 326.32925,
            "body_min": 321.47075
        },
        "ovality": {
            "end": "2.4292499999999997",
            "body": "6.478"
        }
    },
    {
        "inch": "14\"",
        "mm": 355.6,
        "default_material": "X52",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 6.4,
            "0.50_hat": 7.9,
            "0.50_ist1": 9.5,
            "0.50_ist2": 10.3
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 6.35,
            "0.50_hat": 7.92,
            "0.50_ist1": 9.53,
            "0.50_ist2": 10.31
        },
        "diameter_tol_botas": {
            "end_max": 357.20000000000005,
            "end_min": 354.0,
            "body_max": 358.26700000000005,
            "body_min": 352.93300000000005
        },
        "diameter_tol_asme": {
            "end_max": 357.20000000000005,
            "end_min": 354.0,
            "body_max": 358.26700000000005,
            "body_min": 352.93300000000005
        },
        "ovality": {
            "end": "2.6670000000000003",
            "body": "7.112000000000001"
        }
    },
    {
        "inch": "16\"",
        "mm": 406.4,
        "default_material": "X60",
        "botas_thk": {
            "0.72_hat": 5.2,
            "0.60_hat": 6.4,
            "0.50_hat": 7.9,
            "0.50_ist1": 9.5,
            "0.50_ist2": 10.3
        },
        "asme_thk": {
            "0.72_hat": 5.16,
            "0.60_hat": 6.35,
            "0.50_hat": 7.92,
            "0.50_ist1": 9.53,
            "0.50_ist2": 10.31
        },
        "diameter_tol_botas": {
            "end_max": 408.0,
            "end_min": 404.79999999999995,
            "body_max": 409.448,
            "body_min": 403.352
        },
        "diameter_tol_asme": {
            "end_max": 408.0,
            "end_min": 404.79999999999995,
            "body_max": 409.448,
            "body_min": 403.352
        },
        "ovality": {
            "end": "3.0479999999999996",
            "body": "8.128"
        }
    },
    {
        "inch": "18\"",
        "mm": 457.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 5.6,
            "0.60_hat": 6.4,
            "0.50_hat": 7.9,
            "0.50_ist1": 9.5,
            "0.50_ist2": 10.3
        },
        "asme_thk": {
            "0.72_hat": 5.56,
            "0.60_hat": 6.35,
            "0.50_hat": 7.92,
            "0.50_ist1": 9.53,
            "0.50_ist2": 10.31
        },
        "diameter_tol_botas": {
            "end_max": 458.6,
            "end_min": 455.4,
            "body_max": 460.2,
            "body_min": 453.57250000000005
        },
        "diameter_tol_asme": {
            "end_max": 458.6,
            "end_min": 455.4,
            "body_max": 460.2,
            "body_min": 453.57250000000005
        },
        "ovality": {
            "end": "3.4274999999999998",
            "body": "9.14"
        }
    },
    {
        "inch": "20\"",
        "mm": 508.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 6.4,
            "0.60_hat": 7.1,
            "0.50_hat": 8.7,
            "0.50_ist1": 10.3,
            "0.50_ist2": 11.1
        },
        "asme_thk": {
            "0.72_hat": 6.35,
            "0.60_hat": 7.14,
            "0.50_hat": 8.74,
            "0.50_ist1": 10.31,
            "0.50_ist2": 11.13
        },
        "diameter_tol_botas": {
            "end_max": 509.6,
            "end_min": 506.4,
            "body_max": 511.2,
            "body_min": 504.19
        },
        "diameter_tol_asme": {
            "end_max": 509.6,
            "end_min": 506.4,
            "body_max": 511.2,
            "body_min": 504.19
        },
        "ovality": {
            "end": "3.81",
            "body": "10.16"
        }
    },
    {
        "inch": "22\"",
        "mm": 559.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 7.1,
            "0.60_hat": 7.9,
            "0.50_hat": 9.5,
            "0.50_ist1": 11.1,
            "0.50_ist2": 11.9
        },
        "asme_thk": {
            "0.72_hat": 7.14,
            "0.60_hat": 7.92,
            "0.50_hat": 9.53,
            "0.50_ist1": 11.13,
            "0.50_ist2": 11.97
        },
        "diameter_tol_botas": {
            "end_max": 560.6,
            "end_min": 557.4,
            "body_max": 562.2,
            "body_min": 554.8075
        },
        "diameter_tol_asme": {
            "end_max": 560.6,
            "end_min": 557.4,
            "body_max": 562.2,
            "body_min": 554.8075
        },
        "ovality": {
            "end": "4.1925",
            "body": "11.18"
        }
    },
    {
        "inch": "24\"",
        "mm": 610.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 7.1,
            "0.60_hat": 8.7,
            "0.50_hat": 10.3,
            "0.50_ist1": 11.9,
            "0.50_ist2": 12.7
        },
        "asme_thk": {
            "0.72_hat": 7.14,
            "0.60_hat": 8.74,
            "0.50_hat": 10.31,
            "0.50_ist1": 11.97,
            "0.50_ist2": 12.7
        },
        "diameter_tol_botas": {
            "end_max": 611.6,
            "end_min": 608.4,
            "body_max": 613.2,
            "body_min": 605.4250000000001
        },
        "diameter_tol_asme": {
            "end_max": 611.6,
            "end_min": 608.4,
            "body_max": 613.2,
            "body_min": 605.4250000000001
        },
        "ovality": {
            "end": "4.575",
            "body": "12.200000000000001"
        }
    },
    {
        "inch": "30\"",
        "mm": 762.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 9.5,
            "0.60_hat": 11.1,
            "0.50_hat": 12.7,
            "0.50_ist1": 14.3,
            "0.50_ist2": 15.9
        },
        "asme_thk": {
            "0.72_hat": 9.53,
            "0.60_hat": 11.13,
            "0.50_hat": 12.7,
            "0.50_ist1": 14.27,
            "0.50_ist2": 15.88
        },
        "diameter_tol_botas": {
            "end_max": 763.6,
            "end_min": 760.4,
            "body_max": 765.81,
            "body_min": 758.1899999999999
        },
        "diameter_tol_asme": {
            "end_max": 763.6,
            "end_min": 760.4,
            "body_max": 765.81,
            "body_min": 758.1899999999999
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "32\"",
        "mm": 813.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 9.5,
            "0.60_hat": 11.9,
            "0.50_hat": 14.3,
            "0.50_ist1": 15.9,
            "0.50_ist2": 17.5
        },
        "asme_thk": {
            "0.72_hat": 9.53,
            "0.60_hat": 11.91,
            "0.50_hat": 14.27,
            "0.50_ist1": 15.88,
            "0.50_ist2": 17.48
        },
        "diameter_tol_botas": {
            "end_max": 814.6,
            "end_min": 811.4,
            "body_max": 817.0,
            "body_min": 809.0
        },
        "diameter_tol_asme": {
            "end_max": 814.6,
            "end_min": 811.4,
            "body_max": 817.0,
            "body_min": 809.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "34\"",
        "mm": 864.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 10.3,
            "0.60_hat": 12.7,
            "0.50_hat": 15.9,
            "0.50_ist1": 15.9,
            "0.50_ist2": 17.5
        },
        "asme_thk": {
            "0.72_hat": 10.31,
            "0.60_hat": 12.7,
            "0.50_hat": 15.88,
            "0.50_ist1": 15.88,
            "0.50_ist2": 17.48
        },
        "diameter_tol_botas": {
            "end_max": 865.6,
            "end_min": 862.4,
            "body_max": 868.0,
            "body_min": 860.0
        },
        "diameter_tol_asme": {
            "end_max": 865.6,
            "end_min": 862.4,
            "body_max": 868.0,
            "body_min": 860.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "36\"",
        "mm": 914.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 11.1,
            "0.60_hat": 12.7,
            "0.50_hat": 15.9,
            "0.50_ist1": 17.5,
            "0.50_ist2": 19.1
        },
        "asme_thk": {
            "0.72_hat": 11.13,
            "0.60_hat": 12.7,
            "0.50_hat": 15.88,
            "0.50_ist1": 17.48,
            "0.50_ist2": 19.05
        },
        "diameter_tol_botas": {
            "end_max": 915.6,
            "end_min": 912.4,
            "body_max": 918.0,
            "body_min": 910.0
        },
        "diameter_tol_asme": {
            "end_max": 915.6,
            "end_min": 912.4,
            "body_max": 918.0,
            "body_min": 910.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "38\"",
        "mm": 965.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 11.9,
            "0.60_hat": 14.3,
            "0.50_hat": 17.5,
            "0.50_ist1": 19.1,
            "0.50_ist2": 20.6
        },
        "asme_thk": {
            "0.72_hat": 11.91,
            "0.60_hat": 14.27,
            "0.50_hat": 17.48,
            "0.50_ist1": 19.05,
            "0.50_ist2": 20.62
        },
        "diameter_tol_botas": {
            "end_max": 966.6,
            "end_min": 963.4,
            "body_max": 969.0,
            "body_min": 961.0
        },
        "diameter_tol_asme": {
            "end_max": 966.6,
            "end_min": 963.4,
            "body_max": 969.0,
            "body_min": 961.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "40\"",
        "mm": 1016.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 11.9,
            "0.60_hat": 14.3,
            "0.50_hat": 17.5,
            "0.50_ist1": 19.1,
            "0.50_ist2": 20.6
        },
        "asme_thk": {
            "0.72_hat": 11.91,
            "0.60_hat": 14.27,
            "0.50_hat": 17.48,
            "0.50_ist1": 19.05,
            "0.50_ist2": 20.62
        },
        "diameter_tol_botas": {
            "end_max": 1017.6,
            "end_min": 1014.4,
            "body_max": 1020.0,
            "body_min": 1012.0
        },
        "diameter_tol_asme": {
            "end_max": 1017.6,
            "end_min": 1014.4,
            "body_max": 1020.0,
            "body_min": 1012.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "42\"",
        "mm": 1067.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 12.7,
            "0.60_hat": 15.9,
            "0.50_hat": 19.1,
            "0.50_ist1": 20.6,
            "0.50_ist2": 22.2
        },
        "asme_thk": {
            "0.72_hat": 12.7,
            "0.60_hat": 15.88,
            "0.50_hat": 19.05,
            "0.50_ist1": 20.62,
            "0.50_ist2": 22.23
        },
        "diameter_tol_botas": {
            "end_max": 1068.6,
            "end_min": 1065.4,
            "body_max": 1071.0,
            "body_min": 1063.0
        },
        "diameter_tol_asme": {
            "end_max": 1068.6,
            "end_min": 1065.4,
            "body_max": 1071.0,
            "body_min": 1063.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "44\"",
        "mm": 1118.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 14.3,
            "0.60_hat": 15.9,
            "0.50_hat": 19.1,
            "0.50_ist1": 20.6,
            "0.50_ist2": 22.2
        },
        "asme_thk": {
            "0.72_hat": 14.27,
            "0.60_hat": 15.88,
            "0.50_hat": 19.05,
            "0.50_ist1": 20.62,
            "0.50_ist2": 22.23
        },
        "diameter_tol_botas": {
            "end_max": 1119.6,
            "end_min": 1116.4,
            "body_max": 1122.0,
            "body_min": 1114.0
        },
        "diameter_tol_asme": {
            "end_max": 1119.6,
            "end_min": 1116.4,
            "body_max": 1122.0,
            "body_min": 1114.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "46\"",
        "mm": 1168.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 14.3,
            "0.60_hat": 17.5,
            "0.50_hat": 20.6,
            "0.50_ist1": 22.2,
            "0.50_ist2": 23.8
        },
        "asme_thk": {
            "0.72_hat": 14.27,
            "0.60_hat": 17.48,
            "0.50_hat": 20.62,
            "0.50_ist1": 22.23,
            "0.50_ist2": 23.83
        },
        "diameter_tol_botas": {
            "end_max": 1169.6,
            "end_min": 1166.4,
            "body_max": 1172.0,
            "body_min": 1164.0
        },
        "diameter_tol_asme": {
            "end_max": 1169.6,
            "end_min": 1166.4,
            "body_max": 1172.0,
            "body_min": 1164.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "48\"",
        "mm": 1219.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 14.3,
            "0.60_hat": 17.5,
            "0.50_hat": 20.6,
            "0.50_ist1": 22.2,
            "0.50_ist2": 23.8
        },
        "asme_thk": {
            "0.72_hat": 14.27,
            "0.60_hat": 17.48,
            "0.50_hat": 20.62,
            "0.50_ist1": 22.23,
            "0.50_ist2": 23.83
        },
        "diameter_tol_botas": {
            "end_max": 1220.6,
            "end_min": 1217.4,
            "body_max": 1223.0,
            "body_min": 1215.0
        },
        "diameter_tol_asme": {
            "end_max": 1220.6,
            "end_min": 1217.4,
            "body_max": 1223.0,
            "body_min": 1215.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "52\"",
        "mm": 1321.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 15.9,
            "0.60_hat": 19.1,
            "0.50_hat": 22.2,
            "0.50_ist1": 23.8,
            "0.50_ist2": 27.0
        },
        "asme_thk": {
            "0.72_hat": 15.88,
            "0.60_hat": 19.05,
            "0.50_hat": 22.23,
            "0.50_ist1": 23.83,
            "0.50_ist2": 26.97
        },
        "diameter_tol_botas": {
            "end_max": 1322.6,
            "end_min": 1319.4,
            "body_max": 1325.0,
            "body_min": 1317.0
        },
        "diameter_tol_asme": {
            "end_max": 1322.6,
            "end_min": 1319.4,
            "body_max": 1325.0,
            "body_min": 1317.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "56\"",
        "mm": 1422.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 17.5,
            "0.60_hat": 20.6,
            "0.50_hat": 23.8,
            "0.50_ist1": 25.4,
            "0.50_ist2": 28.6
        },
        "asme_thk": {
            "0.72_hat": 17.48,
            "0.60_hat": 20.62,
            "0.50_hat": 23.83,
            "0.50_ist1": 25.4,
            "0.50_ist2": 28.58
        },
        "diameter_tol_botas": {
            "end_max": 1423.6,
            "end_min": 1420.4,
            "body_max": 1426.0,
            "body_min": 1418.0
        },
        "diameter_tol_asme": {
            "end_max": 1423.6,
            "end_min": 1420.4,
            "body_max": 1426.0,
            "body_min": 1418.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    },
    {
        "inch": "60\"",
        "mm": 1524.0,
        "default_material": "X65",
        "botas_thk": {
            "0.72_hat": 19.1,
            "0.60_hat": 22.2,
            "0.50_hat": 25.4,
            "0.50_ist1": 27.0,
            "0.50_ist2": 30.2
        },
        "asme_thk": {
            "0.72_hat": 19.05,
            "0.60_hat": 22.23,
            "0.50_hat": 25.4,
            "0.50_ist1": 26.97,
            "0.50_ist2": 30.18
        },
        "diameter_tol_botas": {
            "end_max": 1525.6,
            "end_min": 1522.4,
            "body_max": 1528.0,
            "body_min": 1520.0
        },
        "diameter_tol_asme": {
            "end_max": 1525.6,
            "end_min": 1522.4,
            "body_max": 1528.0,
            "body_min": 1520.0
        },
        "ovality": {
            "end": "Anlaşmaya bağlıdır.",
            "body": "Anlaşmaya bağlıdır."
        }
    }
]

# ASME B36.10 Schedule Thicknesses Matrix
ASME_B36_10_TABLE = {
    "0.125": [
        1.24,
        1.45,
        1.73,
        2.41
    ],
    "0.25": [
        1.65,
        1.85,
        2.24,
        3.02
    ],
    "0.375": [
        1.65,
        1.85,
        2.31,
        3.2
    ],
    "0.5": [
        1.65,
        2.11,
        2.41,
        2.77,
        3.73,
        4.78,
        7.47
    ],
    "0.75": [
        1.65,
        2.11,
        2.41,
        2.87,
        3.91,
        5.56,
        7.82
    ],
    "1": [
        1.65,
        2.77,
        2.9,
        3.38,
        4.55,
        6.35,
        9.09
    ],
    "1.25": [
        1.65,
        2.77,
        2.97,
        3.56,
        4.85,
        6.35,
        9.7
    ],
    "1.5": [
        1.65,
        2.77,
        3.18,
        3.68,
        5.08,
        7.14,
        10.15
    ],
    "2": [
        1.65,
        2.11,
        2.77,
        3.18,
        3.91,
        4.37,
        4.78,
        5.54,
        6.35,
        7.14,
        8.74,
        11.07
    ],
    "2.5": [
        2.11,
        2.77,
        3.05,
        3.18,
        3.58,
        3.96,
        4.37,
        4.78,
        5.16,
        5.49,
        6.35,
        7.01,
        9.53,
        14.02
    ],
    "3": [
        2.11,
        2.77,
        3.05,
        3.18,
        3.58,
        3.96,
        4.37,
        4.78,
        5.49,
        6.35,
        7.14,
        7.62,
        11.13,
        15.24
    ],
    "3.5": [
        2.11,
        2.77,
        3.05,
        3.18,
        3.58,
        3.96,
        4.37,
        4.78,
        5.74,
        6.35,
        7.14,
        8.08
    ],
    "4": [
        1.13,
        2.11,
        2.77,
        3.05,
        3.18,
        3.58,
        3.96,
        4.37,
        4.78,
        5.16,
        5.56,
        6.02,
        6.35,
        7.14,
        7.92,
        8.56,
        13.49,
        17.12
    ],
    "5": [
        2.11,
        2.77,
        3.18,
        3.4,
        3.96,
        4.78,
        5.56,
        6.55,
        7.14,
        7.92,
        8.74,
        9.53,
        12.7,
        15.88,
        19.05
    ],
    "6": [
        2.11,
        2.77,
        3.18,
        3.4,
        3.58,
        3.96,
        4.37,
        4.78,
        5.16,
        5.56,
        6.35,
        7.11,
        7.92,
        8.74,
        9.53,
        10.97,
        12.7,
        14.27,
        15.88,
        18.26,
        19.05,
        21.95,
        22.23
    ],
    "8": [
        2.77,
        3.18,
        3.76,
        3.96,
        4.78,
        5.16,
        5.56,
        6.35,
        7.04,
        7.92,
        8.18,
        8.74,
        9.53,
        10.31,
        11.13,
        12.7,
        14.27,
        15.09,
        15.88,
        18.26,
        19.05,
        20.62,
        22.23,
        23.01,
        25.4
    ],
    "10": [
        3.4,
        3.96,
        4.19,
        4.78,
        5.16,
        5.56,
        6.35,
        7.09,
        7.8,
        8.74,
        9.27,
        11.13,
        12.7,
        14.27,
        15.09,
        15.88,
        18.26,
        20.62,
        21.44,
        22.23,
        23.83,
        25.4,
        28.58,
        31.75
    ],
    "12": [
        3.96,
        4.37,
        4.57,
        4.78,
        5.16,
        5.56,
        6.35,
        7.14,
        7.92,
        8.38,
        8.74,
        9.53,
        10.31,
        11.13,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        21.44,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        31.75,
        33.32
    ],
    "14": [
        3.96,
        4.78,
        5.16,
        5.33,
        5.56,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.09,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        27.79,
        28.58,
        31.75,
        35.71,
        50.8,
        53.98,
        55.88,
        63.5
    ],
    "16": [
        4.19,
        4.78,
        5.16,
        5.56,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        16.66,
        17.48,
        19.05,
        20.62,
        21.44,
        22.23,
        23.83,
        25.4,
        26.19,
        26.97,
        28.58,
        30.18,
        30.96,
        31.73,
        36.53,
        40.49
    ],
    "18": [
        4.19,
        4.78,
        5.56,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        29.36,
        30.18,
        31.75,
        34.93,
        39.67,
        45.24
    ],
    "20": [
        4.78,
        5.56,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.09,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.19,
        26.97,
        28.58,
        30.18,
        31.75,
        32.54,
        33.32,
        34.93,
        38.1,
        44.45,
        50.01
    ],
    "22": [
        4.78,
        5.56,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75,
        33.92,
        34.93,
        36.53,
        38.1,
        41.28,
        47.63,
        53.98
    ],
    "24": [
        5.54,
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        24.61,
        25.4,
        26.97,
        28.58,
        30.18,
        30.96,
        31.75,
        33.32,
        34.93,
        36.53,
        38.1,
        38.89,
        39.67,
        46.02,
        52.37,
        59.54
    ],
    "26": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4
    ],
    "28": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4
    ],
    "30": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "32": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "34": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "36": [
        6.35,
        7.14,
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "38": [
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "40": [
        7.92,
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "42": [
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "44": [
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "46": [
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "48": [
        8.74,
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "52": [
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "56": [
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "60": [
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "64": [
        9.53,
        10.31,
        11.13,
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "68": [
        11.91,
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "72": [
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "76": [
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ],
    "80": [
        12.7,
        14.27,
        15.88,
        17.48,
        19.05,
        20.62,
        22.23,
        23.83,
        25.4,
        26.97,
        28.58,
        30.18,
        31.75
    ]
}

# ASME B36.19M Stainless Steel Pipe Dimensions (Schedules 5S, 10S, 40S, 80S)
ASME_B36_19_TABLE = {
    "1/8": [1.24, 1.45, 1.73, 2.41],
    "1/4": [1.24, 1.65, 2.24, 3.02],
    "3/8": [1.24, 1.65, 2.31, 3.20],
    "1/2": [1.65, 2.11, 2.77, 3.73],
    "3/4": [1.65, 2.11, 2.87, 3.91],
    "1": [1.65, 2.77, 3.38, 4.55],
    "1 1/4": [1.65, 2.77, 3.56, 4.85],
    "1 1/2": [1.65, 2.77, 3.68, 5.08],
    "2": [1.65, 2.77, 3.91, 5.54],
    "2 1/2": [2.11, 3.05, 5.16, 7.01],
    "3": [2.11, 3.05, 5.49, 7.62],
    "3 1/2": [2.11, 3.05, 5.74, 8.08],
    "4": [2.11, 3.05, 6.02, 8.56],
    "5": [2.77, 3.40, 6.55, 9.53],
    "6": [2.77, 3.40, 7.11, 10.97],
    "8": [2.77, 3.76, 8.18, 12.70],
    "10": [3.40, 4.19, 9.27, 12.70],
    "12": [3.96, 4.57, 9.53, 12.70],
    "14": [3.96, 4.78, 9.53, 12.70],
    "16": [4.19, 4.78, 9.53, 12.70],
    "18": [4.19, 4.78, 9.53, 12.70],
    "20": [4.78, 5.54, 9.53, 12.70],
    "22": [4.78, 5.54, 9.53, 12.70],
    "24": [5.54, 6.35, 9.53, 12.70],
    "30": [6.35, 7.92, 9.53, 12.70],
    "36": [6.35, 7.92, 9.53, 12.70]
}

def is_stainless_grade(grade: str) -> bool:
    """Returns True if the material grade is stainless steel or duplex."""
    g = grade.upper().strip()
    return "SS" in g or "304" in g or "316" in g or "321" in g or "DUPLEX" in g

# Helper functions
def get_smys_info(grade: str):
    return API_5L_SMYS_TABLE.get(grade.upper().strip(), API_5L_SMYS_TABLE['X65'])

def get_chemical_rules(grade: str, standard_type: str = "BOTAŞ"):
    grade = grade.upper().strip()
    base = CHEMICAL_COMPOSITION_RULES.get(grade, CHEMICAL_COMPOSITION_RULES['X65'])
    if "API" in standard_type.upper():
        # API 5L PSL2 Table 5 (t <= 25 mm) — draft deltas vs BOTAŞ:
        #   S <= 0.015 (BOTAŞ is 0.010 for most grades), Nb reported as max-only.
        rules = dict(base)
        if grade not in ('GRADE A',):
            rules['S_max'] = 0.015
        rules['Nb_min'] = 0.0
        return rules
    return base

def get_cvn(grade: str, standard_type: str = "BOTAŞ"):
    """Returns {'material_j': .., 'weld_j': ..} CVN minimums for the given standard."""
    grade = grade.upper().strip()
    if "API" in standard_type.upper() and grade in CVN_API5L:
        return CVN_API5L[grade]
    info = API_5L_SMYS_TABLE.get(grade, API_5L_SMYS_TABLE['X65'])
    return {"material_j": info.get('cvn_material_j', 0.0), "weld_j": info.get('cvn_weld_j', 0.0)}

def normalize_design_factor(factor_str) -> str:
    """Normalize a design factor label (tolerates comma/dot decimal separators and Turkish words)."""
    if not factor_str:
        return "0.72_hat"
    s = str(factor_str).replace(",", ".").lower()
    # Turkish capital 'İ' lowercases to 'i\u0307' (i + combining dot above); strip the dot.
    s = s.replace("\u0307", "")
    has_ist = ("ist" in s) or ("istasyon" in s)
    has_ist2 = ("ist. 2" in s) or ("ist2" in s) or ("istasyon 2" in s)
    if "0.8" in s:
        return "0.80_hat"
    if "0.6" in s:
        return "0.60_hat"
    if "0.5" in s:
        if has_ist2:
            return "0.50_ist2"
        if has_ist:
            return "0.50_ist1"
        return "0.50_hat"
    if "0.4" in s:
        return "0.40_hat"
    return "0.72_hat"

def parse_design_factor(factor_str):
    """Returns (canonical_key, numeric_F) for a design factor string."""
    key = normalize_design_factor(factor_str)
    return key, DESIGN_FACTOR_MAP.get(key, 0.72)

def default_design_pressure_for_factor(f_factor: float) -> float:
    """Excel 'Design P F' mapping: 75 bar -> F=0.8, 82.5 -> F=0.72, 100 -> F=0.6/0.5/0.4."""
    if f_factor >= 0.80:
        return 75.0
    if f_factor >= 0.72:
        return 82.5
    return 100.0

FRACTIONS_NORMALIZATION = {
    "1/2": "½", "½": "½", "0.5": "½",
    "3/4": "¾", "¾": "¾", "0.75": "¾",
    "1 1/4": "1¼", "1-1/4": "1¼", "1 1/4\"": "1¼", "1¼": "1¼", "1.25": "1¼",
    "1 1/2": "1½", "1-1/2": "1½", "1 1/2\"": "1½", "1½": "1½", "1.5": "1½",
    "2 1/2": "2½", "2-1/2": "2½", "2 1/2\"": "2½", "2½": "2½", "2.5": "2½",
    "3 1/2": "3½", "3-1/2": "3½", "3 1/2\"": "3½", "3½": "3½", "3.5": "3½"
}

def normalize_inch_str(s: str) -> str:
    cleaned = str(s).replace('\\', '').replace('"', '').replace("'", '').strip()
    return FRACTIONS_NORMALIZATION.get(cleaned, cleaned)

def get_pipe_size_by_inch(inch: str):
    inch_norm = normalize_inch_str(inch)
    for p in PIPE_SIZES_TABLE:
        p_norm = normalize_inch_str(p['inch'])
        if p_norm == inch_norm or p['inch'] == inch:
            return p
    # Try numeric conversion
    try:
        inch_float = float(inch_norm)
        for p in PIPE_SIZES_TABLE:
            try:
                p_float = float(normalize_inch_str(p['inch']))
                if abs(p_float - inch_float) < 0.05:
                    return p
            except (ValueError, TypeError):
                pass
    except (ValueError, TypeError):
        pass
    return None

def get_pipe_size_by_mm(mm: float):
    best_match = None
    min_diff = 999999
    for p in PIPE_SIZES_TABLE:
        diff = abs(p['mm'] - mm)
        if diff < min_diff:
            min_diff = diff
            best_match = p
    return best_match

def get_botas_all_factors_for_diameter(diameter_inch: str):
    pipe_size = get_pipe_size_by_inch(diameter_inch)
    if not pipe_size:
        return []
    
    factors = [
        ('0,72 (Hat)', '0.72_hat'),
        ('0,6 (Hat)', '0.60_hat'),
        ('0,5 (Hat)', '0.50_hat'),
        ('0,5 (İst.)', '0.50_ist1'),
        ('0,5 (İst. 2)', '0.50_ist2'),
    ]
    
    d_mm = pipe_size['mm']
    if d_mm >= 406.4:
        default_proc = 'SAWH'
    elif d_mm >= 114.3:
        default_proc = 'ERW HFW'
    else:
        default_proc = 'SMLS'

    pipes = []
    seen_factors = set()
    for factor_label, factor_key in factors:
        thk = pipe_size['botas_thk'].get(factor_key, 0.0)
        if thk > 0:
            # Check if this exact thk and factor was already added
            if (factor_label, thk) not in seen_factors:
                seen_factors.add((factor_label, thk))
                pipes.append({
                    'id': f"pipe_botas_{len(pipes)+1}_{int(d_mm)}_{int(thk*100)}",
                    'diameter_inch': pipe_size['inch'],
                    'diameter_mm': pipe_size['mm'],
                    'design_factor_str': factor_label,
                    'wall_thickness_mm': thk,
                    'manufacturing_process': default_proc,
                    'material_grade': pipe_size['default_material'],
                    'standard_type': 'BOTAŞ',
                    'design_pressure_bar': 75.0
                })
    return pipes
