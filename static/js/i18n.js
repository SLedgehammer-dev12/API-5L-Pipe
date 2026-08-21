/**
 * Client-side i18n dictionary and helper functions
 */
const I18N_DICTIONARY = {
    tr: {
        app_title: "API 5L PSL2 & BOTAŞ Boru Kalite Güvence ve Kabul Yazılımı",
        app_subtitle: "Boru Seçim, Kabul Kriterleri, Fabrika Test Denetimi & Et Kalınlığı Tasarım Motoru",
        nav_qaqc: "Boru Kalite Güvence & Kabul Matrisi",
        nav_verification: "Fabrika Test Doğrulama (PASS/FAIL)",
        nav_wall_thickness: "Et Kalınlığı Tasarım Aracı (ASME B31.8)",
        nav_schematic_2d: "2D Enkesit & Tolerans Şeması",
        nav_schematic_3d: "3D İnteraktif Boru & Kaynak Modeli",
        nav_projects: "Proje & Revizyon Yönetimi",
        nav_reports: "Rapor Oluşturucu & Dışa Aktar",
        
        btn_add_pipe: "Yeni Boru Ekle",
        btn_load_preset_48_18: "Referans Şablonu Yükle (48\" + 18\" X65)",
        btn_load_botas_std: "BOTAŞ Standart Şablonu",
        btn_export_excel: "Excel (.xlsx) Olarak İndir",
        btn_export_pdf: "Resmi Rapor / PDF Yazdır",
        btn_save_project: "Projeyi Kaydet (JSON)",
        btn_load_project: "Proje Yükle",
        btn_verify: "Test Verilerini Doğrula",
        btn_calculate_design: "Et Kalınlığı Hesapla",
        
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
        nav_schematic_2d: "2D Cross-Section & Tolerance Diagram",
        nav_schematic_3d: "3D Interactive Pipe & Weld Model",
        nav_projects: "Project & Revision Management",
        nav_reports: "Report Generator & Export",
        
        btn_add_pipe: "Add New Pipe",
        btn_load_preset_48_18: "Load Reference Preset (48\" + 18\" X65)",
        btn_load_botas_std: "BOTAŞ Standard Preset",
        btn_export_excel: "Download Excel (.xlsx)",
        btn_export_pdf: "Print Official Report / PDF",
        btn_save_project: "Save Project (JSON)",
        btn_load_project: "Load Project",
        btn_verify: "Verify Inspection Test Data",
        btn_calculate_design: "Calculate Wall Thickness",
        
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
        localStorage.setItem("api5l_lang", lang);
    }
}

function t(key) {
    return I18N_DICTIONARY[currentLang][key] || key;
}
