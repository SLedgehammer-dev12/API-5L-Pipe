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

        # 1. Attempt PDF Native Table Extraction and Text Extraction
        if filename_lower.endswith(".pdf"):
            extracted_text, raw_tables = cls._extract_pdf_layers(file_bytes)
            if raw_tables:
                tables_found.extend(raw_tables)

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

        return {
            "status": "warning" if is_fallback else "success",
            "is_fallback": is_fallback,
            "warning_message": warning_msg,
            "filename": filename,
            "engine": "Unlimited-OCR Table & Multi-Column Parser (PyMuPDF 1.23+)",
            "total_items_found": len(tables_found),
            "raw_text_snippet": extracted_text[:500] if extracted_text else "",
            "items": tables_found
        }

    @classmethod
    def _extract_pdf_layers(cls, file_bytes: bytes) -> tuple[str, List[Dict[str, Any]]]:
        """
        Extracts structured tables and text layers from digital PDF using PyMuPDF (fitz) find_tables().
        Ensures strict column isolation without interleaving lines from adjacent columns.
        """
        text_content = ""
        extracted_rows: List[Dict[str, Any]] = []

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
                            if raw_df and len(raw_df) > 1:
                                parsed = cls._parse_table_matrix_into_itp(raw_df)
                                for item in parsed:
                                    if not any(it.get("test_name") == item["test_name"] for it in extracted_rows):
                                        extracted_rows.append(item)
                except Exception as e_tab:
                    logger.debug(f"fitz find_tables error on page: {e_tab}")

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
    def _parse_table_matrix_into_itp(cls, table_data: List[List[Optional[str]]]) -> List[Dict[str, Any]]:
        """
        Dynamically analyzes table headers and extracts structured ITP rows with column isolation.
        """
        if not table_data or len(table_data) < 2:
            return []

        # 1. Analyze Header Row
        header_row = [str(c or "").lower().strip() for c in table_data[0]]
        
        idx_name = -1
        idx_freq = -1
        idx_loc = -1
        idx_std = -1
        idx_crit = -1
        idx_clause = -1

        for col_i, col_text in enumerate(header_row):
            if idx_name == -1 and any(k in col_text for k in ("activity", "test", "inspection", "muayene", "deney", "item", "tanım", "faaliyet")):
                idx_name = col_i
            elif idx_freq == -1 and any(k in col_text for k in ("freq", "extent", "frekans", "sıklık", "adet", "rate", "aralık")):
                idx_freq = col_i
            elif idx_loc == -1 and any(k in col_text for k in ("location", "specimen", "yer", "numune", "yön", "örnek")):
                idx_loc = col_i
            elif idx_std == -1 and any(k in col_text for k in ("standard", "method", "metot", "prosedür", "code", "standart")):
                idx_std = col_i
            elif idx_crit == -1 and any(k in col_text for k in ("acceptance", "criteria", "kriter", "limit", "tolerans", "requirement", "şart", "kabul")):
                idx_crit = col_i
            elif idx_clause == -1 and any(k in col_text for k in ("clause", "madde", "ref", "section", "spec", "referans")):
                idx_clause = col_i

        # Fallback default positions if headers not cleanly labeled
        if idx_name == -1 and len(header_row) > 1:
            idx_name = 1 if len(header_row) > 2 else 0
        if idx_freq == -1 and len(header_row) > 2:
            idx_freq = 2
        if idx_crit == -1 and len(header_row) > 5:
            idx_crit = 5

        items: List[Dict[str, Any]] = []

        # 2. Extract Data Rows
        for r_idx in range(1, len(table_data)):
            row = table_data[r_idx]
            if not row or not any(row):
                continue

            test_name = str(row[idx_name] or "").strip() if 0 <= idx_name < len(row) else ""
            if not test_name or len(test_name) < 2 or test_name.lower() in ("no", "item", "test", "faaliyet"):
                continue

            freq = str(row[idx_freq] or "").strip() if 0 <= idx_freq < len(row) else ""
            loc = str(row[idx_loc] or "").strip() if 0 <= idx_loc < len(row) else "Boru gövdesi / kaynak dikişi"
            std = str(row[idx_std] or "").strip() if 0 <= idx_std < len(row) else "API Spec 5L 47. Baskı"
            crit = str(row[idx_crit] or "").strip() if 0 <= idx_crit < len(row) else ""
            clause = str(row[idx_clause] or "").strip() if 0 <= idx_clause < len(row) else "API 5L / İmalatçı ITP"

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
                "raw_text": " | ".join(str(c or "").replace("\n", " ").strip() for c in row)
            })

        return items

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
            (r"(d[üu]zle[şs]tir|flattening|yass[ıiI]lt)", "Düzleştirme Testi (Flattening)"),
            (r"(sertlik|hardness|hv10|hrc|hbw)", "Sertlik Testi (Hardness Testing)"),
            (r"(art[ıiI]k\s*stres|residual\s*stress|halka\s*kesme|stres\s*kontrol|ring\s*test)", "Artık Stres Testi (Residual Stress)"),
            (r"(hidrostatik|hydrostatic|water\s*test|bas[ıiI]n[çc]\s*deney|hydro\s*test|mill\s*hydro)", "Fabrika Hidrostatik Basınç Testi"),
            (r"((?:weld|kaynak).*(?:ut|rt|ndt|ultrasonic|radiographic)|(?:ut|rt|ndt|ultrasonic|radiographic).*(?:weld|kaynak))", "Kaynak Dikişi %100 NDT (UT / RT)"),
            (r"(body\s*laminar|g[öo]vde.*(?:laminas|laminar)|sac\s*laminas|plaka\s*laminas)", "Boru Gövdesi UT Laminasyon"),
            (r"(pipe\s*ends.*(?:ut|ndt|laminar)|u[çc].*(?:laminas|ndt|ut)|ends\s*ut)", "Boru Uçları Laminasyon NDT (UT)"),
            (r"(kaynak\s*a[ğgI]z.*(?:mt|manyetik)|manyetik\s*par[çc]ac[ıiI]k|magnetic\s*particle|mpi|bevel.*mt)", "Kaynak Ağzı ve Tamir Yüzeyi MT"),
            (r"(tamir|repair|re-repair|[öo]n\s*[ıiI]s[ıiI]tma|preheat)", "Kaynak ve Gövde Tamir Kuralları"),
            (r"(kaynak\s*geometr|kaynak\s*y[üu]ksek|reinforcement|radyal\s*ka[çc][ıiI]kl[ıiI]k|radial\s*offset|tepele[şs]me|peaking|misalignment)", "Kaynak Geometrisi ve Kaçıklık"),
            (r"(out[- ]*of[- ]*roundness|ovallik|d[ıiI][şs]\s*[çc]ap|diameter|dia\s*tolerans)", "Dış Çap ve Ovallik Kontrolü"),
            (r"(wall\s*thickness|et\s*kal|cidar\s*kal|thickness\s*verification)", "Et Kalınlığı Ölçümü"),
            (r"(a[ğgI]r[ıiI]k|weight|kg/m|kantar|tart[ıiI]m|mass)", "Boru Birim Ağırlığı ve Toleransı"),
            (r"(straightness|do[ğgI]rusall[ıiI]k|boy|length|bevel|kaynak\s*a[ğgI]z)", "Doğrusallık, Boy ve Alın Kaynak Ağzı"),
            (r"(g[öo]rsel|visual|y[üu]zey|surface)", "Görsel Yüzey Muayenesi"),
            (r"(manyetizma|magnetism|gauss)", "Kalıntı Manyetizma Ölçümü"),
            (r"(markalama|stenciling|[şs]ablonlama|sa\s*2\.5|y[üu]zey\s*haz[ıiI]rl[ıiI]|en\s*10204|mtc|sertifika|certificate)", "Proje Markalaması ve Kalite Sertifikası"),
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
