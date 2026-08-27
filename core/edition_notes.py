"""
Edition comparison notes (API 5L 46th vs 47th Edition).

For every parameter row the program displays, an optional note shows:
  - whether the value is identical in the 46th and 47th editions (or what changed),
  - the source table / clause,
  - and, where the program previously used an outdated (e.g. 45th-edition) value,
    the correct 46th/47th-edition value.

These notes are rendered as a per-row info icon only (they are NOT exported to
Excel/PDF reports).
"""

from typing import Any, Dict

EDITION_NOTES: Dict[str, Dict[str, Any]] = {
    "yt_ratio": {
        "title": "Akma/Çekme Oranı (Y/T) — Tablo 7",
        "source": "API 5L 47. baskı Tablo 7 / dipnot c",
        "edition_46": "≤X80 için 0.93 (yalnız D > 323.9 mm).",
        "edition_47": "≤X80 için 0.93 (yalnız D > 323.9 mm); X90: 0.95 (M)/0.97 (Q); X100: 0.97; X120: 0.99.",
        "changed_46_47": False,
        "program_note": ("Program daha önce 45. baskı kademe değerlerini kullanıyordu "
                         "(B=0.80, X42=0.85, X52=0.87, X65=0.90). 46. ve 47. baskıda "
                         "tüm ≤X80 kademeleri için 0.93'tür."),
    },
    "cvn_body": {
        "title": "CVN Gövde Enerjisi — Tablo 8",
        "source": "API 5L 47. baskı Tablo 8 (46. baskı ile aynı)",
        "edition_46": "Çapa ve kademeye bağlı: 27/40/54/68/81/95/108 J (D aralığına göre).",
        "edition_47": "46. baskı ile aynı (çapa ve kademeye bağlı).",
        "changed_46_47": False,
        "program_note": ("Program daha önce sabit kademe değerleri kullanıyordu "
                         "(örn. X80=68 J). 46. ve 47. baskıda değer D ve kademeye göre "
                         "değişir (örn. X80 ≤1219 mm için 40 J)."),
    },
    "cvn_weld": {
        "title": "CVN Kaynak/ITAB — Madde 9.8.3.1",
        "source": "API 5L 9.8.3.1 (47. baskı)",
        "edition_46": "D < 1422 mm ve ≤X80: 27 J; D ≥ 1422 mm: 40 J; >X80: 40 J (tüm kaynaklı tipler).",
        "edition_47": "HFW dışı D < 1422 mm ve ≤X80: 27 J; HFW dışı D ≥ 1422 mm: 40 J; "
                      "HFW dışı >X80: 40 J; HFW: 20 J (YENİ).",
        "changed_46_47": True,
        "program_note": None,
    },
    "hydro_factor": {
        "title": "Hidrostatik Test Standard Faktörü — Tablo 26",
        "source": "API 5L 10.2.6.4 / Tablo 26 (46. baskı ile aynı)",
        "edition_46": "A/B: 60 %; X42+: D≤141.3 → 60 %, ≤219.1 → 75 %, <508 → 85 %, ≥508 → 90 %.",
        "edition_47": "46. baskı ile aynı; standard test basıncı 20.5 MPa'yı aşmak zorunda değildir.",
        "changed_46_47": False,
        "program_note": ("Program daha önce D<219.2 mm için 0.75 kullanıyordu. Doğrusu D≤141.3 mm "
                         "için 0.60'tır (örn. 4\" X42)."),
    },
    "diameter_tol": {
        "title": "Çap Toleransı — Tablo 10",
        "source": "API 5L 47. baskı Tablo 10 (46. baskı ile aynı)",
        "edition_46": "Kaynaklı gövde: 168.3<D≤610 → ±0.0075D (max ±3.2); 610<D≤1422 → ±0.005D (max ±4.0).",
        "edition_47": "46. baskı ile aynı.",
        "changed_46_47": False,
        "program_note": ("Program daha önce ±3.2 tavanını uygulamıyor ve 610<D≤1422 aralığında "
                         "SMLS değeri olan ±0.01D'yi kullanıyordu."),
    },
    "smls_wall_tol": {
        "title": "SMLS Et Kalınlığı Toleransı — Tablo 11",
        "source": "API 5L 47. baskı Tablo 11 (46. baskı ile aynı)",
        "edition_46": "t ≥ 25.0 mm: +3.7 veya +0.1t (hangisi büyükse); -3.0 veya -0.1t (hangisi büyükse).",
        "edition_47": "46. baskı ile aynı.",
        "changed_46_47": False,
        "program_note": "Program daha önce t ≥ 25 mm için yalnız +3.7 kullanıyordu (t ≥ 37 mm'de yanlış).",
    },
    "elongation": {
        "title": "Minimum Uzama (Af) — Tablo 7 dipnot f / Tablo 21",
        "source": "API 5L 47. baskı Tablo 7 dipnot f (46. baskı ile aynı)",
        "edition_46": "Af = 1940·Axc^0.2 / U^0.9; Axc numuneye göre (yuvarlak çubuk 130/65 mm², şerit/tam kesit ≤485 mm²).",
        "edition_47": "46. baskı ile aynı.",
        "changed_46_47": False,
        "program_note": ("Program daha önce her zaman şerit numune alanı kullanıyordu. "
                         "Kaynaklı D≥219.1 mm borularda Tablo 21'e göre yuvarlak çubuk (Axc 130/65 mm²) geçerlidir."),
    },
    "strain_a": {
        "title": "Guided-bend Strain — Tablo 23",
        "source": "API 5L 47. baskı Tablo 23 (46. baskı ile aynı)",
        "edition_46": "Grade A (L210): 0.1650.",
        "edition_47": "46. baskı ile aynı (Grade A: 0.1650).",
        "changed_46_47": False,
        "program_note": "Program daha önce Grade A için 0.1 kullanıyordu.",
    },
    "flattening": {
        "title": "Düzleştirme Testi — Madde 9.6",
        "source": "API 5L 9.6 a) 3) (47. baskı)",
        "edition_46": "Karşı duvarlar değene kadar 'laminasyon veya yanık metal' bulunmayacaktır.",
        "edition_47": "Karşı duvarlar değene kadar 'kaynakta füzyon eksikliği, eksik nüfuziyet veya "
                      "laminasyon' bulunmayacaktır (ayrıca yeni NOT 4: API 5T1 tanımları).",
        "changed_46_47": True,
        "program_note": None,
    },
    "hydro_calibration": {
        "title": "Hidrostatik Basınç Ölçer Kalibrasyonu — 10.2.6.1",
        "source": "API 5L 10.2.6.1 (47. baskı)",
        "edition_46": "Dead-weight tester ile kullanımdan önce en fazla 4 ay içinde kalibrasyon.",
        "edition_47": "Mekanik (Bourdon/dial) max 6 ay; elektronik (transducer) max 12 ay; "
                      "aralık borcun son gününe kadar.",
        "changed_46_47": True,
        "program_note": None,
    },
    "chem_m_grade": {
        "title": "Kimyasal Bileşim (M kademeleri) — Tablo 5",
        "source": "API 5L 47. baskı Tablo 5 (Welded Pipe / M)",
        "edition_46": "X60M–X120M: Ti 'g' (açık değer yok).",
        "edition_47": "Ti 0.06 (g); yeni dipnot m: C+Nb ≤ 0.20; yeni dipnot n: Al_total ≤ 0.070, N ≤ 0.015.",
        "changed_46_47": True,
        "program_note": None,
    },
    "peaking": {
        "title": "Boru Ucu Peaking",
        "source": "API 5L 9.10.5.1 / 10.2.8.4",
        "edition_46": "Geometrik sapma ≤ 3.2 mm (9.10.5.1); ölçüm şablonla (0.25D veya 200 mm).",
        "edition_47": "46. baskı ile aynı; D×0.0015 formülü standardda yoktur.",
        "changed_46_47": False,
        "program_note": "Program daha önce D×0.0015 formülünü kullanıyordu; standard limiti 3.2 mm'dir.",
    },
    "dwtt": {
        "title": "DWTT — Madde 9.9 / Tablo 20",
        "source": "API 5L 9.9 / Tablo 20",
        "edition_46": "Kaynaklı boru D ≥ 508 mm için (SMLS'te yok).",
        "edition_47": "46. baskı ile aynı; PSL1'de DWTT zorunlu değildir.",
        "changed_46_47": False,
        "program_note": "Program daha önce SMLS dahil tüm D≥508 mm borularda 'Var' gösteriyordu.",
    },
}


def build_edition_notes(pipe_result: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the subset of edition notes relevant for the given pipe result."""
    keys = {
        "yt_ratio", "cvn_body", "cvn_weld", "hydro_factor", "diameter_tol",
        "smls_wall_tol", "elongation", "strain_a", "flattening",
        "hydro_calibration", "chem_m_grade", "peaking", "dwtt",
    }
    notes: Dict[str, Any] = {}
    for k in keys:
        n = EDITION_NOTES.get(k)
        if n:
            notes[k] = {
                "title": n["title"],
                "source": n["source"],
                "edition_46": n["edition_46"],
                "edition_47": n["edition_47"],
                "changed_46_47": n["changed_46_47"],
                "program_note": n.get("program_note"),
            }
    return notes