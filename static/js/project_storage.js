/**
 * Project Storage, JSON Import/Export & Revision Management
 */
class ProjectStorage {
    static STORAGE_KEY = "api5l_active_project";

    static saveToLocalStorage(projectData) {
        try {
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
            return raw ? JSON.parse(raw) : null;
        } catch (e) {
            console.error("Failed to load project from LocalStorage:", e);
            return null;
        }
    }

    static downloadProjectJSON(projectData) {
        const jsonStr = JSON.stringify(projectData, null, 4);
        const blob = new Blob([jsonStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        const filename = `${projectData.project_info.project_no || 'API5L_Project'}_${projectData.project_info.revision || 'Rev0'}.pipeproj`;
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
                    resolve(parsed);
                } catch (err) {
                    reject(new Error("Geçersiz proje dosyası formatı (Invalid JSON)!"));
                }
            };
            reader.onerror = () => reject(new Error("Dosya okunamadı!"));
            reader.readAsText(file);
        });
    }
}
