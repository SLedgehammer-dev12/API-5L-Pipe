"""
Unlimited-OCR Document Parsing & ITP Ingestion Engine.

Designed for Baidu's Unlimited-OCR (R-SWA Long-Horizon Parsing) model.
Processes both digital (searchable) and scanned PDFs in a single forward pipeline,
extracting structured Inspection & Test Plan (ITP) tables containing:
    - Test Name (Muayene / Test Adı)
    - Test Frequency (Test / Numune Alma Frekansı)
    - Sampling Location (Numune Yeri & Yönü)
    - Specimen Type / Dimensions (Numune Tipi / Boyutu)
    - Test Standard (Test Standardı / Metodu)
    - Acceptance Criteria (Kabul Kriteri / Limit Değerler)
    - Clause Reference (Şartname Maddesi)
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class UnlimitedOCREngine:
    """
    Core document reading engine powered by Unlimited-OCR architecture.
    Handles digital/scanned PDFs and converts them into structured ITP JSON.
    """

    SYSTEM_PROMPT = (
        "Sen uzman bir Boru Kalite Güvence ve Muayene Denetçisisin (API 5L / BOTAŞ ITP Specialist). "
        "Aşağıdaki ITP (Inspection & Test Plan) dokümanındaki tüm testleri, numune frekanslarını ve "
        "kabul kriterlerini eksiksiz oku ve aşağıdaki JSON şemasına dönüştür:\n"
        "[\n"
        "  {\n"
        "    \"test_name\": \"Test veya Muayene Adı\",\n"
        "    \"test_frequency\": \"Test / Numune Alma Sıklığı\",\n"
        "    \"sampling_location\": \"Numune Yeri / Yönü\",\n"
        "    \"specimen_type\": \"Numune Tipi / Boyutu\",\n"
        "    \"test_standard\": \"Uygulanan Standart (ISO / ASTM / API)\",\n"
        "    \"acceptance_criteria\": \"Kabul Kriteri / Limit Değerler\",\n"
        "    \"clause_reference\": \"Şartname Maddesi\"\n"
        "  }\n"
        "]"
    )

    @classmethod
    def parse_pdf_or_image(
        cls,
        file_bytes: bytes,
        filename: str = "itp_document.pdf",
        api_endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses a PDF or image file into structured ITP records.
        Uses native PyMuPDF find_tables() table extraction, Unlimited-OCR worker/API if configured,
        or semantic pattern parsing with strict column isolation.
        """
        import os
        filename_lower = filename.lower()
        extracted_text = ""
        tables_found: List[Dict[str, Any]] = []
        is_fallback = False
        warning_msg = None

        # Resolve API endpoint from parameter or environment variable
        endpoint = api_endpoint or os.getenv("UNLIMITED_OCR_API_URL")

        # 1. Attempt PDF Native Table Extraction or Direct Image OCR
        if filename_lower.endswith(".pdf"):
            extracted_text, raw_tables = cls._extract_pdf_layers(file_bytes)
            if raw_tables:
                tables_found.extend(raw_tables)
        elif any(filename_lower.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
            try:
                import io
                from PIL import Image
                import pytesseract
                img = Image.open(io.BytesIO(file_bytes))
                extracted_text = pytesseract.image_to_string(img, lang="tur+eng")
            except Exception as e_img:
                logger.debug(f"Direct image OCR failed: {e_img}")

        # 2. If Unlimited-OCR remote/local worker endpoint is provided, query it
        if endpoint and not tables_found:
            try:
                ocr_res = cls._call_unlimited_ocr_api(file_bytes, filename, endpoint)
                if ocr_res and "items" in ocr_res and ocr_res["items"]:
                    return ocr_res
            except Exception as e:
                logger.warning(f"Unlimited-OCR API call failed, falling back to embedded parser: {e}")

        # 3. Structure extracted text into standardized ITP rows if native tables were not detected
        if not tables_found and extracted_text.strip():
            tables_found = cls._parse_text_into_itp_rows(extracted_text)

        # 4. If nothing could be extracted from a blank/scanned image file, provide reference fallback with explicit warning
        if not tables_found:
            is_fallback = True
            warning_msg = "⚠️ DİKKAT: Yüklenen PDF taranmış/vektörsüz görsel formatında olduğu için doğrudan dijital tablo çıkarılamadı. Sistem referans ITP şablonunu görüntülemektedir."
            tables_found = cls._heuristic_extract_fallback(extracted_text or filename)

        # 5. Automatically detect Project, Standard, Scope and Pipe Geometry Metadata
        detected_metadata = cls.detect_itp_metadata(extracted_text, tables_found, filename)

        return {
            "status": "warning" if is_fallback else "success",
            "is_fallback": is_fallback,
            "warning_message": warning_msg,
            "filename": filename,
            "engine": "Unlimited-OCR Table & Multi-Column Parser (PyMuPDF 1.23+)",
            "total_items_found": len(tables_found),
            "raw_text_snippet": extracted_text[:500] if extracted_text else "",
            "items": tables_found,
            "detected_metadata": detected_metadata
        }

    @classmethod
    def _extract_pdf_layers(cls, file_bytes: bytes) -> tuple[str, List[Dict[str, Any]]]:
        """
        Extracts structured tables and text layers from digital PDF using PyMuPDF (fitz) find_tables().
        Ensures strict column isolation without interleaving lines from adjacent columns.
        """
        text_content = ""
        extracted_rows: List[Dict[str, Any]] = []
        table_state: Optional[Dict[str, Any]] = None

        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text_content += (page.get_text() or "") + "\n"

                # Native PyMuPDF table detection (available in PyMuPDF 1.23.0+)
                try:
                    tabs = page.find_tables()
                    if tabs and tabs.tables:
                        for tab in tabs.tables:
                            raw_df = tab.extract()
                            if raw_df and len(raw_df) >= 1:
                                parsed, table_state = cls._parse_table_matrix_into_itp(raw_df, table_state)
                                for item in parsed:
                                    if not any(it.get("test_name") == item["test_name"] for it in extracted_rows):
                                        extracted_rows.append(item)
                except Exception as e_tab:
                    logger.debug(f"fitz find_tables error on page: {e_tab}")

            # If digital text extraction returned no text (scanned image PDF), attempt OCR on rasterized pages
            if not text_content.strip() and not extracted_rows:
                try:
                    import pytesseract
                    from PIL import Image
                    import io
                    for page in doc:
                        pix = page.get_pixmap(dpi=200)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_txt = pytesseract.image_to_string(img, lang="tur+eng")
                        if ocr_txt:
                            text_content += ocr_txt + "\n"
                except Exception as e_tess:
                    logger.debug(f"Local pytesseract fallback unavailable: {e_tess}")

        except Exception as e_fitz:
            try:
                import io
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text_content += (page.extract_text() or "") + "\n"
            except Exception as e_pypdf:
                logger.debug(f"PDF text extraction exception: {e_fitz} / {e_pypdf}")

        return text_content, extracted_rows

    @classmethod
    def _parse_table_matrix_into_itp(
        cls,
        table_data: List[List[Optional[str]]],
        last_state: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Dynamically analyzes multi-column table headers (e.g. Borusan / Tosçelik / BOTAŞ formats)
        and extracts structured ITP rows with column isolation, parent cell forward-fill,
        and cross-page multi-table continuation.
        """
        if not table_data or len(table_data) < 1:
            return [], last_state

        raw_joined_header = " ".join(str(c or "") for c in table_data[0]).lower()
        # Skip document title blocks and signature/abbreviation footers
        if any(k in raw_joined_header for k in ("kısaltmalar", "hazırlayan", "onaylayan", "temsilcisi", "sayfa no", "revizyon no", "sipariş bilgileri")):
            return [], last_state

        # 1. Scan first 5 rows for header definition
        header_row = []
        header_row_idx = -1
        idx_activity = -1
        idx_feature = -1
        idx_freq = -1
        idx_loc = -1
        idx_std = -1
        idx_crit = -1
        idx_clause = -1
        idx_mfg = -1
        idx_tpi = -1
        idx_client = -1

        for r_i, r in enumerate(table_data[:5]):
            cand_row = [str(c or "").lower().strip() for c in r]
            if not cand_row or not any(cand_row):
                continue
            # If the first cell is a pure numeric row index (e.g. '1.0', '6.0', '12'), it is a data row, not a header!
            if re.match(r'^\d+(?:\.\d+)*$', cand_row[0].strip()):
                continue

            cand_act = -1
            cand_feat = -1
            cand_freq = -1
            cand_loc = -1
            cand_std = -1
            cand_crit = -1
            cand_clause = -1
            cand_mfg = -1
            cand_tpi = -1
            cand_client = -1

            for col_i, col_text in enumerate(cand_row):
                # Independent Column Identification (No elif masking)
                if cand_feat == -1 and any(k in col_text for k in ("ürün özelli", "özellik", "gereksinim", "parametre", "test adı", "muayene türü", "özelliği", "kontrolü", "muayene / test", "test parametre")):
                    cand_feat = col_i
                if cand_act == -1 and any(k in col_text for k in ("faaliyet", "aktivite", "activity", "proses", "tanım", "aşama", "proses aşaması", "operasyon")):
                    cand_act = col_i
                elif cand_act == -1 and any(k in col_text for k in ("test", "inspection", "muayene", "deney", "item", "scope")) and cand_feat != col_i:
                    cand_act = col_i
                
                if cand_freq == -1 and any(k in col_text for k in ("freq", "extent", "frekans", "sıklık", "adet", "rate", "aralık", "frequency", "sıklığı", "numune alma", "numune boyutu")):
                    cand_freq = col_i
                if cand_loc == -1 and any(k in col_text for k in ("location", "specimen", "yer", "numune", "yön", "örnek", "position", "gerçekleştiren", "sorumlu")):
                    cand_loc = col_i
                if cand_std == -1 and any(k in col_text for k in ("kontrol eden", "kontrol doküman", "standard", "method", "metot", "prosedür", "code", "standart", "doküman", "dokümanı", "şartname", "şartnamesi", "spec")):
                    cand_std = col_i
                if cand_crit == -1 and "şartname" not in col_text and any(k in col_text for k in ("kabul", "kriter", "acceptance", "criteria", "limit", "tolerans", "requirement", "kabul şartı", "onay kriteri")):
                    cand_crit = col_i
                if cand_clause == -1 and any(k in col_text for k in ("clause", "madde", "ref", "section", "referans")):
                    cand_clause = col_i

                # Witness / Hold Point Columns (C / H / W / I / R)
                if cand_mfg == -1 and any(k in col_text for k in ("imalatçı", "üretici", "mfg", "manufacturer", "borusan", "tosçelik", "toscelik", "erciyas", "yapımcı")):
                    cand_mfg = col_i
                if cand_tpi == -1 and any(k in col_text for k in ("tpi", "gözetim", "3rd party", "üçüncü taraf", "denetim kurumu", "mümessil", "tüv", "lloyd", "sgs", "bv")):
                    cand_tpi = col_i
                if cand_client == -1 and any(k in col_text for k in ("müşteri", "botaş", "botas", "işveren", "client", "idare", "owner", "alıcı")):
                    cand_client = col_i

            matched = sum(1 for idx in (cand_act, cand_feat, cand_freq, cand_std, cand_crit, cand_clause) if idx != -1)
            if matched >= 1 and (cand_act != -1 or cand_feat != -1 or (cand_std != -1 and cand_crit != -1)):
                header_row = cand_row
                header_row_idx = r_i
                idx_activity, idx_feature, idx_freq, idx_loc, idx_std, idx_crit, idx_clause = (
                    cand_act, cand_feat, cand_freq, cand_loc, cand_std, cand_crit, cand_clause
                )
                idx_mfg, idx_tpi, idx_client = cand_mfg, cand_tpi, cand_client
                break

        start_row = 1
        confidence_level = "HIGH"
        if header_row_idx != -1:
            if idx_feature == -1 and idx_activity != -1 and len(header_row) > 3:
                idx_feature = 2 if idx_activity != 2 else (3 if len(header_row) > 3 else 1)

            current_state = {
                "indices": (idx_activity, idx_feature, idx_freq, idx_loc, idx_std, idx_crit, idx_clause, idx_mfg, idx_tpi, idx_client),
                "num_cols": len(header_row),
                "last_parent_activity": last_state.get("last_parent_activity", "") if last_state else ""
            }
            start_row = header_row_idx + 1
        elif last_state and (abs(len(table_data[0]) - last_state["num_cols"]) <= 4 or len(table_data[0]) >= 6):
            # Continuation table on next page without repeated header
            current_state = last_state
            confidence_level = "MEDIUM"
            idx_activity, idx_feature, idx_freq, idx_loc, idx_std, idx_crit, idx_clause, idx_mfg, idx_tpi, idx_client = current_state["indices"]
            ncols = len(table_data[0])
            idx_activity = min(idx_activity, ncols - 1) if idx_activity >= 0 else 1
            idx_feature = min(idx_feature, ncols - 1) if idx_feature >= 0 else 2
            idx_freq = min(idx_freq, ncols - 1) if idx_freq >= 0 else -1
            idx_loc = min(idx_loc, ncols - 1) if idx_loc >= 0 else -1
            idx_std = min(idx_std, ncols - 1) if idx_std >= 0 else -1
            idx_crit = min(idx_crit, ncols - 1) if idx_crit >= 0 else -1
            idx_clause = min(idx_clause, ncols - 1) if idx_clause >= 0 else -1
            idx_mfg = min(idx_mfg, ncols - 1) if idx_mfg >= 0 else -1
            idx_tpi = min(idx_tpi, ncols - 1) if idx_tpi >= 0 else -1
            idx_client = min(idx_client, ncols - 1) if idx_client >= 0 else -1
            start_row = 0
        else:
            return [], last_state

        items: List[Dict[str, Any]] = []
        last_parent_activity = current_state.get("last_parent_activity", "")

        # 2. Extract Data Rows
        for r_idx in range(start_row, len(table_data)):
            row = table_data[r_idx]
            if not row or not any(row):
                continue

            activity_val = str(row[idx_activity] or "").strip() if 0 <= idx_activity < len(row) else ""
            feature_val = str(row[idx_feature] or "").strip() if 0 <= idx_feature < len(row) else ""

            if activity_val and len(activity_val) > 2 and activity_val.lower() not in ("no", "item", "test", "faaliyet", "aktivite"):
                last_parent_activity = activity_val
            else:
                activity_val = last_parent_activity

            # Choose the most specific and descriptive test name
            test_name = ""
            if feature_val and len(feature_val) > 2 and feature_val.lower() not in ("no", "item", "test", "faaliyet"):
                act_clean = activity_val.strip().lower()
                feat_clean = feature_val.strip().lower()
                if act_clean and act_clean != feat_clean and feat_clean not in act_clean and not any(k in act_clean for k in ("ölçüsel", "laboratuvar", "muayene ve test", "doğrulama", "genel", "kaplama öncesi", "üretim")):
                    test_name = f"{activity_val} - {feature_val}"
                else:
                    test_name = feature_val
            elif activity_val and len(activity_val) > 2:
                test_name = activity_val

            # Filter out non-test metadata lines (e.g. document code, dates, revision numbers)
            if not test_name or len(test_name) < 2 or test_name.lower() in ("no", "item", "test", "faaliyet", "aktivite", "tarih", "imza", "isim", "isim :"):
                continue
            if re.match(r"^[\d\s,.\-/%]+$", test_name):
                continue
            if any(k in test_name.lower() for k in ("tos-itp", "gbb-itp", "rev.", "sayfa no", "müşteri", "sipariş no")):
                continue

            freq = str(row[idx_freq] or "").strip() if 0 <= idx_freq < len(row) else ""
            loc = str(row[idx_loc] or "").strip() if 0 <= idx_loc < len(row) else "Boru gövdesi / kaynak dikişi / kaplama"
            std = str(row[idx_std] or "").strip() if 0 <= idx_std < len(row) else "API Spec 5L / BOTAŞ / DIN 30670"
            crit = str(row[idx_crit] or "").strip() if 0 <= idx_crit < len(row) else ""
            clause = str(row[idx_clause] or "").strip() if 0 <= idx_clause < len(row) else "API 5L / BOTAŞ 5120 / 5410 R1"

            # Extract Witness / Hold Points (C, H, W, I, R)
            mfg_val = str(row[idx_mfg] or "").strip().upper() if 0 <= idx_mfg < len(row) else "C"
            tpi_val = str(row[idx_tpi] or "").strip().upper() if 0 <= idx_tpi < len(row) else "W"
            client_val = str(row[idx_client] or "").strip().upper() if 0 <= idx_client < len(row) else "W"

            if not freq:
                freq = cls._extract_frequency_from_text(f"{test_name} {crit}") or "Test ünitesi (lot) başına 1 set"
            if not crit:
                crit = cls._extract_criteria_from_text(f"{test_name} {freq}") or "API 5L / BOTAŞ şartname limitlerine uygun"

            items.append({
                "test_name": test_name.replace("\n", " ").strip(),
                "test_frequency": freq.replace("\n", " ").strip(),
                "sampling_location": loc.replace("\n", " ").strip(),
                "specimen_type": "Standart numune",
                "test_standard": std.replace("\n", " ").strip(),
                "acceptance_criteria": crit.replace("\n", " ").strip(),
                "clause_reference": clause.replace("\n", " ").strip(),
                "inspection_points": {
                    "mfg": mfg_val,
                    "tpi": tpi_val,
                    "client": client_val
                },
                "reading_confidence": confidence_level,
                "raw_text": " | ".join(str(c or "").replace("\n", " ").strip() for c in row)
            })

        current_state["last_parent_activity"] = last_parent_activity
        return items, current_state

    @classmethod
    def _parse_text_into_itp_rows(cls, text: str) -> List[Dict[str, Any]]:
        """Parses document text into structured ITP item dicts using semantic pattern matching."""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        items: List[Dict[str, Any]] = []
        
        # Fine-grained test category patterns (tolerant of Turkish and ASCII encoding variations)
        test_patterns = [
            (r"(ladle\s*heat|ıs[ıiI]\s*analiz|d[öo]k[üu]m\s*analiz|heat\s*analysis)", "Isı Analizi (Heat Analysis)"),
            (r"(product\s*analysis|[üu]r[üu]n\s*analiz|check\s*analysis|product\s*chemical)", "Ürün Analizi (Product Analysis)"),
            (r"(body\s*tensile|g[öo]vde\s*[çc]ekme|transverse\s*tensile|pipe\s*body\s*tensile)", "Gövde Çekme Testi (Body Tensile)"),
            (r"(weld\s*tensile|kaynak\s*[çc]ekme|weld\s*seam\s*tensile)", "Kaynak Çekme Testi (Weld Tensile)"),
            (r"(cvn\s*body|g[öo]vde\s*[çc]entik|g[öo]vde\s*darbe|body\s*impact|charpy.*body)", "Gövde Çentik Darbe Testi (CVN Body Impact)"),
            (r"(cvn\s*weld|kaynak\s*darbe|itab\s*darbe|weld\s*impact|charpy.*weld|weld.*haz)", "Kaynak & ITAB Çentik Darbe (CVN Weld & HAZ)"),
            (r"(dwtt|drop\s*weight|y[ıiI]rt[ıiI]lma\s*testi|d[üu][şs]en\s*a[ğgI]r[ıiI]k)", "DWTT (Düşen Ağırlık Yırtılma Testi)"),
            (r"(k[ıiI]lavuzlu\s*b[üu]kme|guided[- ]*bend|k[öo]k\s*b[üu]kme|kapak\s*b[üu]kme|root\s*bend|face\s*bend|bend\s*test)", "Kılavuzlu Bükme Testi (Guided-Bend)"),
            (r"(d[üu]zle[şs]tir|flattening|yass[ıiI]lt|ezme)", "Düzleştirme Testi (Flattening)"),
            (r"(metalograf|martenzit|mikro\s*yap[ıiI]|tavlama|normalizasyon)", "Metalografik İnceleme & Mikro Yapı"),
            (r"([çc]apak|flash\s*trim|oyuk\s*derinlik)", "İç ve Dış Çapak Alma & Geometri"),
            (r"(sertlik|hardness|hv10|hrc|hbw)", "Sertlik Testi (Hardness Testing)"),
            (r"(art[ıiI]k\s*stres|residual\s*stress|halka\s*kesme|stres\s*kontrol|ring\s*test)", "Artık Stres Testi (Residual Stress)"),
            (r"(hidrostatik|hydrostatic|water\s*test|bas[ıiI]n[çc]\s*deney|hydro\s*test|mill\s*hydro)", "Fabrika Hidrostatik Basınç Testi"),
            (r"((?:weld|kaynak).*(?:ut|rt|ndt|ultrasonic|radiographic)|(?:ut|rt|ndt|ultrasonic|radiographic).*(?:weld|kaynak))", "Kaynak Dikişi %100 NDT (UT / RT)"),
            (r"(body\s*laminar|g[öo]vde.*(?:laminas|laminar)|sac\s*laminas|plaka\s*laminas)", "Boru Gövdesi UT Laminasyon"),
            (r"(pipe\s*ends.*(?:ut|ndt|laminar)|u[çc].*(?:laminas|ndt|ut)|ends\s*ut)", "Boru Uçları Laminasyon NDT (UT)"),
            (r"(kaynak\s*a[ğgI]z.*(?:mt|manyetik)|manyetik\s*par[çc]ac[ıiI]k|magnetic\s*particle|mpi|bevel.*mt)", "Kaynak Ağzı ve Tamir Yüzeyi MT"),
            (r"(kumlama|y[üu]zey\s*haz[ıiI]rl[ıiI]|sa\s*2\.5|profil.*p[üu]r[üu]zl[üu]|rz|toz\s*testi|tuz\s*testi)", "Yüzey Hazırlığı ve Kumlama"),
            (r"((?:3lpe|3l\s*hdpe|fbe|kaplama).*(?:kal[ıiI]nl[ıiI]k|thickness)|(?:kal[ıiI]nl[ıiI]k|thickness).*(?:kaplama|3lpe|fbe))", "3LPE / HDPE Kaplama Kalınlığı"),
            (r"(holiday|elektrik.*porozite|k[ıiI]v[ıiI]lc[ıiI]m|25\s*kv|25000\s*volt)", "Elektrik Porozite (Holiday) Testi"),
            (r"(soyulma|yap[ıiI][şs]ma|peel|adhesion|150\s*n/cm)", "Soyulma Mukavemeti / Yapışma Testi"),
            (r"(kaplama.*darbe|darbe\s*diren[çc]|impact\s*resist|5\s*j/mm)", "Kaplama Darbe Direnci Testi"),
            (r"(delici\s*u[çc]|indentation|batma\s*diren[çc])", "Delici Uca Batma Direnci (Indentation)"),
            (r"(katodik\s*soyulma|cd\s*test|cathodic\s*disbond)", "Katodik Soyulma Testi (CD Test)"),
            (r"(cutback|cut[- ]*back|kaplamas[ıiI]z\s*b[öo]lge|boru\s*ucu\s*geri\s*kesme)", "Kaplamasız Bölge (Cutback) Hazırlığı"),
            (r"(kaplama.*tamir|heatshrink|yama\s*malzeme|tamir\s*metod)", "Kaplama Kusur Tamir Kuralları"),
            (r"(tamir|repair|re-repair|[öo]n\s*[ıiI]s[ıiI]tma|preheat)", "Kaynak ve Gövde Tamir Kuralları"),
            (r"(radyal\s*ka[çc][ıiI]kl[ıiI]k|radial\s*offset|basamaklanma)", "Sac Kenarları Radyal Kaçıklık"),
            (r"(tepele[şs]me|peaking)", "Boru Ucu Tepeleşme"),
            (r"(kaynak\s*y[üu]ksek|reinforcement|kaynak\s*diki[şs]\s*y[üu]ksek)", "Kaynak Dikiş Yüksekliği"),
            (r"((?:u[çc]|pipe\s*ends).*(?:[çc]evre|circumference)|(?:[çc]evre|circumference).*(?:u[çc]|ends))", "Boru Ucu Çevre Toleransı"),
            (r"((?:g[öo]vde|body).*(?:[çc]evre|circumference)|(?:[çc]evre|circumference).*(?:g[öo]vde|body))", "Boru Gövdesi Çevre Toleransı"),
            (r"((?:u[çc]|pipe\s*ends).*(?:ovallik|ovality|roundness)|(?:ovallik|ovality|roundness).*(?:u[çc]|ends))", "Ovalite - Boru Ucu"),
            (r"((?:g[öo]vde|body).*(?:ovallik|ovality|roundness)|(?:ovallik|ovality|roundness).*(?:g[öo]vde|body))", "Ovalite - Boru Gövdesi"),
            (r"((?:u[çc]|pipe\s*ends).*(?:d[ıiI][şs]\s*[çc]ap|diameter)|(?:d[ıiI][şs]\s*[çc]ap|diameter).*(?:u[çc]|ends))", "Boru Ucu Dış Çap Toleransı"),
            (r"((?:g[öo]vde|body).*(?:d[ıiI][şs]\s*[çc]ap|diameter)|(?:d[ıiI][şs]\s*[çc]ap|diameter).*(?:g[öo]vde|body))", "Boru Gövdesi Dış Çap Toleransı"),
            (r"(out[- ]*of[- ]*roundness|ovallik|d[ıiI][şs]\s*[çc]ap|diameter|dia\s*tolerans)", "Dış Çap ve Ovallik Kontrolü"),
            (r"(wall\s*thickness|et\s*kal|cidar\s*kal|thickness\s*verification)", "Et Kalınlığı Ölçümü ve Toleransı"),
            (r"(a[ğgI]r[ıiI]k|weight|kg/m|kantar|tart[ıiI]m|mass)", "Boru Birim Ağırlığı ve Toleransı"),
            (r"(straightness|do[ğgI]rusall[ıiI]k)", "Boru Toplam Doğrusallığı"),
            (r"(bevel|kaynak\s*a[ğgI]z|a[ğgI]z\s*a[çc][ıiI]s[ıiI]|k[öo]k\s*y[üu]zey)", "Alın Kaynak Ağzı Açısı ve Kök Yüzeyi"),
            (r"(diklik|squareness)", "Boru Ucu Diklikten Sapma"),
            (r"(g[öo]rsel|visual|y[üu]zey|surface)", "Görsel Yüzey Muayenesi"),
            (r"(manyetizma|magnetism|gauss)", "Kalıntı Manyetizma Ölçümü"),
            (r"(markalama|stenciling|[şs]ablonlama|en\s*10204|mtc|sertifika|certificate)", "Proje Markalaması ve Kalite Sertifikası"),
            (r"(tahribats[ıiI]z|ndt|ut|ultrasonic|radiographic|rt)", "Tahribatsız Muayene (NDT)"),
            (r"([çc]ekme|tensile|yield\s*strength)", "Çekme Testi (Tensile Test)"),
            (r"(darbe|[çc]entik|charpy|cvn|impact)", "Çentik Darbe Testi (CVN Impact)"),
        ]

        # Scan text lines
        for i, line in enumerate(lines):
            for pat, name in test_patterns:
                if re.search(pat, line, re.IGNORECASE):
                    neighbor_text = " ".join(lines[max(0, i - 1):min(len(lines), i + 4)])
                    freq = cls._extract_frequency_from_text(neighbor_text)
                    crit = cls._extract_criteria_from_text(neighbor_text)
                    
                    if not any(it["test_name"] == name for it in items):
                        items.append({
                            "test_name": name,
                            "test_frequency": freq or "Test ünitesi (lot) başına 1 set",
                            "sampling_location": "Boru gövdesi / kaynak dikişi",
                            "specimen_type": "Standart numune",
                            "test_standard": "API Spec 5L 47. Baskı",
                            "acceptance_criteria": crit or "API 5L / BOTAŞ şartname limitlerine uygun",
                            "clause_reference": "API 5L / İmalatçı ITP",
                            "inspection_points": {
                                "mfg": "C",
                                "tpi": "W",
                                "client": "W"
                            },
                            "reading_confidence": "LOW",
                            "raw_text": line
                        })
                    break

        return items

    @classmethod
    def _extract_frequency_from_text(cls, text: str) -> Optional[str]:
        """Finds sampling frequency expressions in text in English and Turkish."""
        freq_matches = [
            r"(her\s*boru(?:\s*\(?%100\)?)?|100%\s*(?:tüm\s*borular|all\s*pipes|full\s*length)?|each\s*pipe(?:\s*\(?100%\)?)?|all\s*pipes)",
            r"(\d+\s*boruda\s*1|1\s*per\s*\d+\s*pipes|100\s*boruda\s*1)",
            r"(her\s*d[öo]k[üu]m(?:de)?|d[öo]k[üu]m\s*ba[şs][ıiI]na|heat\s*ba[şs][ıiI]na|per\s*heat|every\s*heat|once\s*per\s*heat|one\s*analysis\s*per\s*heat|two\s*analyses\s*per\s*heat|ısı\s*başına\s*\d+)",
            r"(once\s*per\s*test\s*unit|lot\s*başına|test\s*ünitesi\s*başına|per\s*test\s*unit|per\s*lot|lot\s*ba[şs][ıiI]na|test\s*[üu]nitesi\s*ba[şs][ıiI]na)",
            r"(1\s*set\s*\(\d+\s*numune\)|1\s*set\s*\(\d+\s*specimens?\)|1\s*root\s*\+\s*1\s*face|1\s*kök\s*\+\s*1\s*kapak)",
            r"(vardiyada?\s*\d*\s*saatte\s*bir|her\s*\d+\s*saatte|per\s*shift|once\s*per\s*\d+\s*hours|at\s*least\s*once\s*per\s*\d+\s*hours|en\s*az\s*[ıiİi]ki\s*defa)",
            r"(rulo\s*başı\s*ve\s*sonu|crop\s*ends)",
        ]
        for fm in freq_matches:
            m = re.search(fm, text, re.IGNORECASE)
            if m:
                return m.group(0).strip()
        return None

    @classmethod
    def _extract_criteria_from_text(cls, text: str) -> Optional[str]:
        """Extracts numerical limits or criteria statements from text."""
        crit_matches = [
            r"(min\s*(?:avg|individual|ort\.?|tek\.?)?\s*\d+\.?\d*\s*(?:j(?:oules?)?|mpa|bar|sn|saniye|sec|seconds?|hv\d*|hrc))",
            r"(max\s*\d+\.?\d*\s*(?:%|mm|mpa|mt|gauss))",
            r"(rt0\.5\s*[≥>=]\s*\d+)",
            r"(rm\s*[≥>=:]\s*\d+(?:\s*-\s*\d+)?\s*mpa)",
            r"(af\s*[≥>=]\s*\d+\.?\d*%)",
            r"(y/t\s*[≤<=]\s*\d+\.?\d*)",
            r"(c\s*[≤<=]\s*0\.\d+)",
            r"(p\s*[≤<=]\s*0\.\d+)",
            r"(s\s*[≤<=]\s*0\.\d+)",
            r"(tolerance:\s*[-+]\d+\.?\d*%\s*/\s*[-+]\d+\.?\d*%)",
            r"(\d+\.?\d*\s*-\s*\d+\.?\d*\s*mpa)",
        ]
        found = []
        for cm in crit_matches:
            m = re.findall(cm, text, re.IGNORECASE)
            if m:
                found.extend(m)
        return ", ".join(found) if found else None

    @classmethod
    def _call_unlimited_ocr_api(cls, file_bytes: bytes, filename: str, endpoint: str) -> Dict[str, Any]:
        """Sends document to Unlimited-OCR inference microservice."""
        import urllib.request
        import urllib.error
        
        req = urllib.request.Request(
            endpoint,
            data=file_bytes,
            headers={
                "Content-Type": "application/pdf" if filename.endswith(".pdf") else "image/png",
                "X-Filename": filename
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data

    @classmethod
    def _heuristic_extract_fallback(cls, context: str) -> List[Dict[str, Any]]:
        """Provides realistic default ITP template rows for demonstration and baseline comparison."""
        return [
            {
                "test_name": "Isı Analizi (Heat Analysis)",
                "test_frequency": "Isı (Döküm) başına 1 analiz",
                "sampling_location": "Döküm potası",
                "specimen_type": "Spektrometre numunesi",
                "test_standard": "ASTM A751 / ISO 14284",
                "acceptance_criteria": "C ≤ 0.16%, P ≤ 0.020%, S ≤ 0.010%, CE_IIW ≤ 0.43",
                "clause_reference": "API 5L Madde 9.2",
            },
            {
                "test_name": "Ürün Analizi (Product Analysis)",
                "test_frequency": "Isı başına 2 analiz (farklı borulardan)",
                "sampling_location": "Boru ucu talaşı",
                "specimen_type": "Talaş / spektrometre",
                "test_standard": "ASTM A751",
                "acceptance_criteria": "C ≤ 0.16%, P ≤ 0.020%, S ≤ 0.010%, CE_IIW ≤ 0.43",
                "clause_reference": "API 5L Madde 9.2 & Tablo 5",
            },
            {
                "test_name": "Gövde Çekme Testi (Body Tensile)",
                "test_frequency": "Test ünitesi (lot) başına 1 set",
                "sampling_location": "Gövde enine",
                "specimen_type": "Şerit 38.1 mm x tam cidar",
                "test_standard": "ISO 6892-1 / ASTM A370",
                "acceptance_criteria": "Rt0.5 ≥ 450 MPa, Rm: 535-760 MPa, Af ≥ 19.5%, Y/T ≤ 0.93",
                "clause_reference": "API 5L Madde 9.3 & Tablo 7",
            },
            {
                "test_name": "Kaynak Çekme Testi (Weld Tensile)",
                "test_frequency": "Test ünitesi (lot) başına 1 set",
                "sampling_location": "Kaynak dikişi enine",
                "specimen_type": "Tam cidar şerit",
                "test_standard": "ISO 6892-1 / ASTM A370",
                "acceptance_criteria": "Rm ≥ 535 MPa (Ana metal dayanımını karşılamalıdır)",
                "clause_reference": "API 5L Madde 9.3.2",
            },
            {
                "test_name": "Gövde Çentik Darbe Testi (CVN Body Impact)",
                "test_frequency": "Test ünitesi başına 1 set (3 numune)",
                "sampling_location": "Gövde enine (0 °C)",
                "specimen_type": "10x10x55 mm Charpy V-Notch",
                "test_standard": "ISO 148-1 / ASTM A370",
                "acceptance_criteria": "Min Ort. 41 J, Min Tek 31 J (0 °C)",
                "clause_reference": "API 5L Madde 9.8 & Tablo 8",
            },
            {
                "test_name": "Kaynak & ITAB Çentik Darbe (CVN Weld & HAZ)",
                "test_frequency": "Test ünitesi başına 1 set kaynak + 1 set ITAB (3+3 numune)",
                "sampling_location": "Kaynak merkez hattı & ITAB",
                "specimen_type": "10x10x55 mm Charpy V-Notch",
                "test_standard": "ISO 148-1 / ASTM A370",
                "acceptance_criteria": "Min Ort. 27 J, Min Tek 20 J (0 °C)",
                "clause_reference": "API 5L Madde 9.8.3",
            },
            {
                "test_name": "DWTT (Düşen Ağırlık Yırtılma Testi)",
                "test_frequency": "Isı / test ünitesi başına 1 test (2 numune)",
                "sampling_location": "Gövde enine",
                "specimen_type": "Tam cidar press-notch",
                "test_standard": "API RP 5L3 / ASTM E436",
                "acceptance_criteria": "Ortalama sünek kırılma alanı ≥ %85 (0 °C)",
                "clause_reference": "API 5L Madde 9.9",
            },
            {
                "test_name": "Kılavuzlu Bükme Testi (Guided-Bend)",
                "test_frequency": "Test ünitesi (lot) başına 1 set (1 kök + 1 kapak)",
                "sampling_location": "Kaynak dikişi enine",
                "specimen_type": "Tam cidar şerit",
                "test_standard": "ISO 5173 / ASTM A370",
                "acceptance_criteria": "Kaynak veya ITAB'da > 3.2 mm çatlak/kusur oluşmayacak",
                "clause_reference": "API 5L Madde 9.7",
            },
            {
                "test_name": "Fabrika Hidrostatik Basınç Testi",
                "test_frequency": "Her boru (%100 tüm borular)",
                "sampling_location": "Boru tam boyu",
                "specimen_type": "Boru kendisi",
                "test_standard": "API 5L Madde 10.2.6",
                "acceptance_criteria": "Min 109.8 bar, Min Tutma Süresi: 10 saniye, Kaçak/Sızıntı yok",
                "clause_reference": "API 5L Madde 9.4 & 10.2.6",
            },
            {
                "test_name": "Kaynak Dikişi %100 NDT (UT / RT)",
                "test_frequency": "Her boru tam boy kaynak dikişi (%100)",
                "sampling_location": "Helisel / boyuna kaynak dikişi",
                "specimen_type": "Boru dikişi",
                "test_standard": "API 5L Ek E / ISO 10893-11",
                "acceptance_criteria": "Kabul edilemez çatlak, füzyon noksanlığı ve gözenek yok",
                "clause_reference": "API 5L Madde 9.13 & Ek E",
            },
            {
                "test_name": "Boru Uçları Laminasyon NDT (UT)",
                "test_frequency": "Her boru (%100) uç kısımları (min 100 mm çevre)",
                "sampling_location": "Boru uçları (100 mm band)",
                "specimen_type": "Boru ucu",
                "test_standard": "API 5L Ek E.8 / ISO 10893-8",
                "acceptance_criteria": "> 6.0 mm veya > 100 mm² laminasyon hatası bulunmayacaktır",
                "clause_reference": "API 5L Ek E.8",
            },
            {
                "test_name": "Dış Çap, Ovallik ve Et Kalınlığı",
                "test_frequency": "Her boru (%100)",
                "sampling_location": "Gövde ve boru uçları",
                "specimen_type": "Ölçüm aletleri / Ultrasonik",
                "test_standard": "API 5L Madde 10.2.8",
                "acceptance_criteria": "Çap: ±0.5% (Max ±4.0 mm), Ovallik ≤ 15.0 mm, Et Kalınlığı: -%8.0 / +%15.0",
                "clause_reference": "API 5L Tablo 10 & 11",
            },
            {
                "test_name": "Görsel Yüzey Muayenesi",
                "test_frequency": "Her boru (%100 iç ve dış yüzey)",
                "sampling_location": "Tüm yüzeyler",
                "specimen_type": "Görsel / lamba muayenesi",
                "test_standard": "API 5L Madde 10.2.7",
                "acceptance_criteria": "Çatlak, katmer, kabuk, > %12.5t çizik ve kusur yok",
                "clause_reference": "API 5L Madde 9.10.1",
            },
            {
                "test_name": "Kalıntı Manyetizma Ölçümü",
                "test_frequency": "Vardiyada 4 saatte bir ve sevkiyat öncesi her boru",
                "sampling_location": "Boru uçları",
                "specimen_type": "Manyetometre (Gaussmetre)",
                "test_standard": "API 5L Madde 10.2.10",
                "acceptance_criteria": "Ortalama ≤ 3.0 mT (30 Gauss), münferit ≤ 3.5 mT (35 Gauss)",
                "clause_reference": "API 5L Madde 9.14",
            },
        ]

    @classmethod
    def detect_itp_metadata(
        cls,
        extracted_text: str,
        items: List[Dict[str, Any]],
        filename: str = ""
    ) -> Dict[str, Any]:
        """
        Automatically detects pipe manufacturing & coating standards, scope discipline,
        geometry, grade, and project metadata from extracted text and structured ITP items.
        """
        text_lower = (extracted_text or "").replace("I", "ı").replace("İ", "i").lower()
        fn_lower = (filename or "").replace("I", "ı").replace("İ", "i").lower()
        items_text = " ".join([f"{it.get('test_name', '')} {it.get('acceptance_criteria', '')}" for it in items]).replace("I", "ı").replace("İ", "i").lower()
        combined_text = f"{text_lower} {fn_lower} {items_text}"

        # 1. Standard Detection
        has_botas = any(k in combined_text for k in ("botaş", "botas", "5120", "5410", "5140", "4-ngtl-0-gn-p-002"))
        has_api5l = any(k in combined_text for k in ("api 5l", "api spec 5l", "46th", "47th"))
        has_din30670 = "din 30670" in combined_text
        has_iso21809 = any(k in combined_text for k in ("iso 21809", "en 21809", "21809"))

        std_type = "BOTAŞ" if has_botas else ("API" if has_api5l else "API")
        std_label = "BOTAŞ (5120 R7 + 5410 R1)" if has_botas else ("API Spec 5L (47th / 46th Edition)" if has_api5l else "API Spec 5L")

        # 2. Scope / Discipline Detection
        coating_kw = ("kaplama", "kumlama", "holiday", "peel", "soyulma", "darbe", "indentation", "katodik", "cutback", "cut back", "fbe", "3lpe", "hdpe", "boyasız", "yama")
        bare_kw = ("çekme", "akma", "tensile", "yield", "cvn", "çentik", "dwtt", "flattening", "yassıltma", "ezme", "hidrostatik", "hydrostatic", "laminasyon", "çapak", "normalizasyon")

        coating_hits = sum(1 for k in coating_kw if k in combined_text)
        bare_hits = sum(1 for k in bare_kw if k in combined_text)

        # Check filename or title cues
        if any(k in fn_lower or k in text_lower[:500] for k in ("combined", "bütünsel", "tam kapsam", "full combined", "imalat ve kaplama")):
            scope_mode = "COMBINED"
            scope_label = "Bütünsel (İmalat + 3LPE Dış Kaplama)"
        elif any(k in fn_lower or k in text_lower[:500] for k in ("hdpe kaplama", "dış kaplama", "coating only", "sadece kaplama", "din 30670", "tos-itp-şrk-002")):
            scope_mode = "COATING_ONLY"
            scope_label = "Sadece 3LPE Dış Kaplama (DIN 30670 / BOTAŞ 5410 R1)"
        elif any(k in fn_lower or k in text_lower[:500] for k in ("siyah boru", "çıplak boru", "bare pipe", "tos-itp-şrk-001", "bare_pipe")):
            scope_mode = "BARE_PIPE_ONLY"
            scope_label = "Sadece Çıplak Boru İmalatı (API 5L / BOTAŞ 5120 R7)"
        elif coating_hits >= 4 and bare_hits >= 4:
            scope_mode = "COMBINED"
            scope_label = "Bütünsel (İmalat + 3LPE Dış Kaplama)"
        elif coating_hits >= 4 and bare_hits < 4:
            scope_mode = "COATING_ONLY"
            scope_label = "Sadece 3LPE Dış Kaplama (DIN 30670 / BOTAŞ 5410 R1)"
        elif bare_hits >= 4 and coating_hits < 4:
            scope_mode = "BARE_PIPE_ONLY"
            scope_label = "Sadece Çıplak Boru İmalatı (API 5L / BOTAŞ 5120 R7)"
        else:
            scope_mode = "COMBINED"
            scope_label = "Bütünsel Kalite Planı"

        # 3. Grade Detection
        grade = "X65"
        grades = [
            ("X80", "X80"), ("X70", "X70"), ("X65", "X65"), ("X60", "X60"),
            ("X56", "X56"), ("X52", "X52"), ("X46", "X46"), ("X42", "X42"),
            ("GRADE B", "Grade B"), ("GR.B", "Grade B"), ("GRB", "Grade B"), ("L485", "X70"),
            ("L450", "X65"), ("L415", "X60"), ("L360", "X52"), ("L290", "X42"), ("L245", "Grade B")
        ]
        for code, clean_name in grades:
            if re.search(r"\b" + code.lower() + r"\b", text_lower) or re.search(r"\b" + code.lower() + r"m\b", text_lower):
                grade = clean_name
                break

        # 4. Process Detection
        process = "SAWH"
        if any(k in combined_text for k in ("erw", "hfw", "yüksek frekans", "high frequency")):
            process = "ERW"
        elif any(k in combined_text for k in ("lsaw", "sawl", "boyuna tozaltı", "longitudinal")):
            process = "LSAW"
        elif any(k in combined_text for k in ("sawh", "hsaw", "spiral", "helical")):
            process = "SAWH"
        elif any(k in combined_text for k in ("smls", "dikişsiz", "seamless")):
            process = "SMLS"

        # 5. PSL Level
        if "psl1" in combined_text or "psl 1" in combined_text or "psl-1" in combined_text:
            psl = "PSL1"
        elif "psl2" in combined_text or "psl 2" in combined_text or "psl-2" in combined_text or has_botas:
            psl = "PSL2"
        else:
            psl = "PSL2"

        # 6. Diameter & Wall Thickness
        d_mm = 1219.0
        d_inch = '48"'
        t_mm = 14.30

        known_diameters = [
            (1219.0, '48"', [r"\b1219(?:[.,]0)?\b", r"\b48\s*(?:\"|inç|inch)\b"]),
            (1016.0, '40"', [r"\b1016(?:[.,]0)?\b", r"\b40\s*(?:\"|inç|inch)\b"]),
            (914.4, '36"', [r"\b914[.,]4\b", r"\b36\s*(?:\"|inç|inch)\b"]),
            (762.0, '30"', [r"\b762(?:[.,]0)?\b", r"\b30\s*(?:\"|inç|inch)\b"]),
            (610.0, '24"', [r"\b610(?:[.,]0)?\b", r"\b24\s*(?:\"|inç|inch)\b"]),
            (508.0, '20"', [r"\b508(?:[.,]0)?\b", r"\b20\s*(?:\"|inç|inch)\b"]),
            (406.4, '16"', [r"\b406[.,]4\b", r"\b16\s*(?:\"|inç|inch)\b"]),
            (323.9, '12"', [r"\b323[.,]9\b", r"\b12\s*(?:\"|inç|inch)\b"]),
            (273.0, '10"', [r"\b273(?:[.,]0)?\b", r"\b10\s*(?:\"|inç|inch)\b"]),
            (219.1, '8"', [r"\b219[.,]1\b", r"\b8\s*(?:\"|inç|inch)\b"]),
            (168.3, '6"', [r"\b168[.,]3\b", r"\b6\s*(?:\"|inç|inch)\b"]),
            (114.3, '4"', [r"\b114[.,]3\b", r"\b4\s*(?:\"|inç|inch)\b"])
        ]

        for mm_val, in_val, patterns in known_diameters:
            if any(re.search(p, text_lower) for p in patterns):
                d_mm = mm_val
                d_inch = in_val
                break

        # Check scope table row matches e.g. "1 219,1 6,40 PSL 2 X42M" - collect ALL variants
        scope_rows = re.findall(r"(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+([a-zA-Z0-9\-]+)", text_lower)
        scope_variants: List[Dict[str, Any]] = []
        if scope_rows:
            for _, d_raw, t_raw, _ in scope_rows:
                try:
                    d_parsed = float(d_raw.replace(",", "."))
                    t_parsed = float(t_raw.replace(",", "."))
                    if 50.0 <= d_parsed <= 3000.0 and 2.0 <= t_parsed <= 60.0:
                        # Deduplicate
                        if not any(abs(v["diameter_mm"] - d_parsed) < 0.5 and abs(v["wall_thickness_mm"] - t_parsed) < 0.1 for v in scope_variants):
                            scope_variants.append({"diameter_mm": d_parsed, "wall_thickness_mm": t_parsed})
                except Exception:
                    continue
            if scope_variants:
                d_mm = scope_variants[0]["diameter_mm"]
                t_mm = scope_variants[0]["wall_thickness_mm"]
        if not scope_variants:
            known_wts = [25.4, 22.2, 19.1, 17.5, 15.9, 14.3, 12.7, 11.1, 9.5, 8.2, 7.9, 7.1, 6.4, 5.6, 4.8]
            for w in known_wts:
                w_str = str(w).replace(".", "[.,]")
                if re.search(r"(?:et kalınlığı|kalınlık|wt|t)[\s:=]*" + w_str, text_lower) or re.search(r"\b" + w_str + r"\s*mm\b", text_lower):
                    t_mm = w
                    break

        customer = "BOTAŞ" if has_botas else "Genel Müşteri"
        proj_m = re.search(r"proje(?: ismi)?\s*[:\n]\s*([^\n\r]+)", text_lower)
        project_name = proj_m.group(1).strip() if proj_m else ("BOTAŞ Doğal Gaz Boru Hattı Projesi" if has_botas else "Çelik Boru İmalat & Test Projesi")

        confidence = 80
        if has_botas or has_api5l:
            confidence += 10
        if d_mm and t_mm:
            confidence += 10

        # Build inch string for scope variants
        def _to_inch_str(mm_val: float) -> str:
            for mm_c, in_c, _ in known_diameters:
                if abs(mm_c - mm_val) < 0.5:
                    return in_c
            return f'{mm_val:.1f} mm'
        
        # scope_variants already built, ensure inch string present
        for v in scope_variants if 'scope_variants' in locals() else []:
            v["diameter_inch"] = _to_inch_str(v["diameter_mm"])
            v["material_grade"] = grade
            v["manufacturing_process"] = process
            v["psl_level"] = psl
            v["standard_type"] = std_type

        return {
            "customer": customer,
            "project_name": project_name.title(),
            "detected_standard": std_type,
            "detected_standard_label": std_label,
            "detected_scope_mode": scope_mode,
            "detected_scope_label": scope_label,
            "detected_process": process,
            "detected_grade": grade,
            "detected_psl": psl,
            "detected_diameter_mm": d_mm,
            "detected_diameter_inch": d_inch,
            "detected_wall_thickness_mm": t_mm,
            "scope_variants": scope_variants if 'scope_variants' in locals() else [],
            "spec_references": {
                "botas_pipe_5120": has_botas,
                "botas_coating_5410": has_botas or has_din30670,
                "botas_transport_5140": "5140" in combined_text,
                "api_5l": has_api5l,
                "din_30670": has_din30670,
                "iso_21809": has_iso21809
            },
            "confidence_score": min(confidence, 100)
        }
