/**
 * Project Storage, JSON Import/Export & Schema Migration
 * Ensures full backward compatibility across application versions.
 */
class ProjectStorage {
    static STORAGE_KEY = "api5l_active_project";
    static CURRENT_SCHEMA_VERSION = "2.7.0";

    static saveToLocalStorage(projectData) {
        try {
            if (projectData && projectData.project_info) {
                projectData.project_info.schema_version = this.CURRENT_SCHEMA_VERSION;
            }
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(projectData));
            return true;
        } catch (e) {
            console.error("Failed to save project to LocalStorage:", e);
            return false;
        }
    }

    static loadFromLocalStorage() {
        try {
            const raw = localStorage.getItem(this.STORAGE_KEY);
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            return this.migrateProjectSchema(parsed);
        } catch (e) {
            console.error("Failed to load project from LocalStorage:", e);
            return null;
        }
    }

    static downloadProjectJSON(projectData) {
        const migrated = this.migrateProjectSchema(projectData);
        migrated.project_info.schema_version = this.CURRENT_SCHEMA_VERSION;
        const jsonStr = JSON.stringify(migrated, null, 4);
        const blob = new Blob([jsonStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        const filename = `${migrated.project_info.project_no || 'API5L_Project'}_${migrated.project_info.revision || 'Rev0'}.pipeproj`;
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    static readProjectJSONFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const parsed = JSON.parse(e.target.result);
                    const migrated = this.migrateProjectSchema(parsed);
                    resolve(migrated);
                } catch (err) {
                    reject(new Error("Geçersiz proje dosyası formatı (Invalid JSON)!"));
                }
            };
            reader.onerror = () => reject(new Error("Dosya okunamadı!"));
            reader.readAsText(file);
        });
    }

    /**
     * Backward-compatibility migration logic.
     * Safely upgrades older project formats (v1.0.0, v1.6.2) to the latest schema (v2.0.0).
     */
    static migrateProjectSchema(data) {
        if (!data || typeof data !== 'object') {
            return { project_info: {}, pipes: [] };
        }

        const project_info = Object.assign({
            project_name: "Doğal Gaz Boru Hattı Projesi",
            project_no: "PRJ-2026-API5L-001",
            line_name: "İletim Hattı",
            client: "BOTAŞ A.Ş.",
            contractor: "Yüklenici Firma",
            prepared_by: "Boru Tasarım Mühendisi",
            checked_by: "Kalite Şefi",
            approved_by: "Baş Denetçi",
            revision: "Rev. 0",
            revision_date: new Date().toISOString().split('T')[0],
            standard: "BOTAŞ Şartnamesi",
            language: "tr",
            heat_number: "",
            certificate_number: "",
            quantity: "",
            purchase_order_number: "",
            inspection_company: "",
            schema_version: this.CURRENT_SCHEMA_VERSION
        }, data.project_info || {});

        const rawPipes = Array.isArray(data.pipes) ? data.pipes : [];
        const migratedPipes = rawPipes.map((p, idx) => {
            return {
                id: p.id || `pipe_${Date.now()}_${idx}`,
                diameter_inch: p.diameter_inch || "48\"",
                diameter_mm: typeof p.diameter_mm === 'number' ? p.diameter_mm : 1219.0,
                wall_thickness_mm: typeof p.wall_thickness_mm === 'number' ? p.wall_thickness_mm : 14.30,
                design_factor_str: p.design_factor_str || "0.72 (Hat)",
                material_grade: p.material_grade || "X65",
                manufacturing_process: p.manufacturing_process || (p.diameter_mm >= 406.4 ? "SAWH" : (p.diameter_mm >= 114.3 ? "ERW HFW" : "SMLS")),
                standard_type: p.standard_type || "BOTAŞ",
                design_pressure_bar: typeof p.design_pressure_bar === 'number' ? p.design_pressure_bar : 75.0,
                psl_level: p.psl_level || "PSL2",
                delivery_condition: p.delivery_condition || "M",
                heat_number: p.heat_number || "",
                latest_itp_audit: p.latest_itp_audit || null
            };
        });

        return {
            project_info: project_info,
            pipes: migratedPipes
        };
    }
}
