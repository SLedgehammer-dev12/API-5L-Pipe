/**
 * Client-side i18n dictionary and helper functions
 */
const I18N_DICTIONARY = {
    tr: {
        app_title: "API 5L PSL2 & BOTAŞ Boru Kalite Güvence Yazılımı",
        app_subtitle: "Boru Seçim, Kabul Kriterleri, Fabrika Test Denetimi & Et Kalınlığı Tasarım Motoru",
        nav_qaqc: "Boru Kalite Güvence & Kabul Matrisi",
        nav_verification: "Fabrika Test Doğrulama (PASS/FAIL)",
        nav_wall_thickness: "Et Kalınlığı Tasarım Aracı (ASME B31.8)",
        nav_schematic_3d: "2D / 3D Şematik Gösterim",
        nav_projects: "Proje & Revizyon",
        nav_about: "Hakkında & Yasal Uyarı",
        
        btn_add_pipe: "Yeni Boru Sütunu Ekle",
        btn_export_excel: "Excel (.xlsx) Olarak İndir",
        btn_export_pdf: "Resmi Rapor / PDF Yazdır",
        btn_save_project: "Projeyi Kaydet (JSON)",
        btn_load_project: "Proje Yükle",
        btn_verify: "Uygunluğu Doğrula (PASS/FAIL)",
        btn_calculate_design: "Et Kalınlığı Hesapla",
        btn_snapshot_3d: "📷 3D Görüntüyü Kaydet (PNG)",
        btn_collapse_all: "Tümünü Daralt",
        btn_expand_all: "Tümünü Genişlet",
        btn_feedback: "💬 Geri Bildirim & İletişim",
        
        search_placeholder: "Tabloda parametre veya standart ara (örn: uzama, ovalite, hydro, C)...",
        kpi_hydro_press: "Maks. Fabrika Test Basıncı",
        kpi_weight: "Nominal Birim Ağırlık",
        kpi_dt_ratio: "D/t Oranı & Tasarım",
        kpi_fracture: "ASME 841.1.2 Kırılma Emniyeti",
        
        footer_copyright: "© 2026 API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite. Tüm Hakları Saklıdır.",
        footer_disclaimer_short: "Bu yazılım boru kalite güvence ve ön kabul hesaplamalarını hızlandırmak amacıyla hazırlanmıştır; projelerde nihai onay lisanslı baş mühendis sorumluluğundadır.",
        
        diameter: "Çap",
        wall_thickness: "Et Kalınlığı",
        manufacturing_process: "Üretim Yöntemi",
        material_grade: "Malzeme Kalitesi",
        design_factor: "Tasarım Faktörü",
        standard: "Şartname / Standart",
        design_pressure: "Tasarım Basıncı (Bar)"
    },
    en: {
        app_title: "API 5L PSL2 & BOTAŞ Pipe QA/QC & Inspection Suite",
        app_subtitle: "Pipe Selection, Acceptance Criteria, Factory Acceptance Testing & Wall Thickness Design",
        nav_qaqc: "Pipe QA/QC & Acceptance Matrix",
        nav_verification: "Factory Test Verification (PASS/FAIL)",
        nav_wall_thickness: "Wall Thickness Design Tool (ASME B31.8)",
        nav_schematic_3d: "2D / 3D Schematic Models",
        nav_projects: "Project & Revision",
        nav_about: "About & Legal Disclaimer",
        
        btn_add_pipe: "Add New Pipe Column",
        btn_export_excel: "Download Excel (.xlsx)",
        btn_export_pdf: "Print Official Report / PDF",
        btn_save_project: "Save Project (JSON)",
        btn_load_project: "Load Project",
        btn_verify: "Verify Inspection Data (PASS/FAIL)",
        btn_calculate_design: "Calculate Wall Thickness",
        btn_snapshot_3d: "📷 Export 3D Snapshot (PNG)",
        btn_collapse_all: "Collapse All",
        btn_expand_all: "Expand All",
        btn_feedback: "💬 Feedback & Contact",
        
        search_placeholder: "Search parameter or standard in table (e.g. elongation, ovality, hydro, C)...",
        kpi_hydro_press: "Max Factory Hydro Pressure",
        kpi_weight: "Nominal Unit Weight",
        kpi_dt_ratio: "D/t Ratio & Design",
        kpi_fracture: "ASME 841.1.2 Fracture Control",
        
        footer_copyright: "© 2026 API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite. All Rights Reserved.",
        footer_disclaimer_short: "This software is developed for engineering QA/QC and pre-acceptance calculations; final project approvals are the sole responsibility of the licensed chief engineer.",
        
        diameter: "Diameter",
        wall_thickness: "Wall Thickness",
        manufacturing_process: "Manufacturing Process",
        material_grade: "Material Grade",
        design_factor: "Design Factor",
        standard: "Specification / Standard",
        design_pressure: "Design Pressure (Bar)"
    }
};

let currentLang = "tr";

function setLanguage(lang) {
    if (I18N_DICTIONARY[lang]) {
        currentLang = lang;
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            if (I18N_DICTIONARY[lang][key]) {
                el.innerText = I18N_DICTIONARY[lang][key];
            }
        });
        document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
            const key = el.getAttribute("data-i18n-placeholder");
            if (I18N_DICTIONARY[lang][key]) {
                el.setAttribute("placeholder", I18N_DICTIONARY[lang][key]);
            }
        });
        localStorage.setItem("api5l_lang", lang);
    }
}

function t(key) {
    return I18N_DICTIONARY[currentLang][key] || key;
}
