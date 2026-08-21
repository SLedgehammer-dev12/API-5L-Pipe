/**
 * Main Frontend Application Logic for API 5L Pipe QA/QC & Design Suite
 * Includes BOTAŞ automatic lookup, API 5L mode, and engineering remarks for every row.
 */

let activeProject = {
    project_info: {
        project_name: "Doğal Gaz Boru Hattı Fabrika Kabul ve Kalite Güvence Projesi",
        project_no: "PRJ-2026-API5L-001",
        line_name: "Ana İletim Hattı & İstasyon Bağlantıları",
        client: "BOTAŞ Boru Hatları ile Petrol Taşıma A.Ş.",
        contractor: "Boru İmalat ve Denetim San. A.Ş.",
        prepared_by: "Boru Tasarım & Kalite Mühendisi",
        checked_by: "Kalite Kontrol Şefi",
        approved_by: "Baş Denetçi / Proje Müdürü",
        revision: "Rev. 0",
        revision_date: "2026-08-21",
        standard: "BOTAŞ Şartnamesi",
        language: "tr"
    },
    pipes: []
};

let calculatedPipes = [];
let selectedPipeIndex = 0;
let visualizer3DInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
    const savedLang = localStorage.getItem("api5l_lang") || "tr";
    setLanguage(savedLang);

    const cachedProj = ProjectStorage.loadFromLocalStorage();
    if (cachedProj && cachedProj.pipes && cachedProj.pipes.length > 0) {
        activeProject = cachedProj;
    } else {
        await loadPreset("reference");
    }

    await calculateAndRenderAll();

    setTimeout(() => {
        visualizer3DInstance = new PipeVisualizer3D("viewport-3d");
        visualizer3DInstance.init();
        if (calculatedPipes.length > 0) {
            updateVisualizers(calculatedPipes[selectedPipeIndex] || calculatedPipes[0]);
        }
    }, 400);

    setupEventListeners();
});

async function loadPreset(type) {
    try {
        let url = "/api/presets/reference";
        if (type === "botas-10") url = "/api/presets/botas-10";
        else if (type === "api5l-10") url = "/api/presets/api5l-10";

        const resp = await fetch(url);
        const data = await resp.json();
        activeProject = data;
        ProjectStorage.saveToLocalStorage(activeProject);
        await calculateAndRenderAll();
        showToast("Şablon başarıyla yüklendi!", "success");
    } catch (e) {
        console.error("Preset load error:", e);
        showToast("Şablon yüklenirken hata oluştu!", "error");
    }
}

async function calculateAndRenderAll() {
    try {
        const resp = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pipes: activeProject.pipes,
                standard_type: activeProject.project_info.standard
            })
        });
        const res = await resp.json();
        if (res.status === "success") {
            calculatedPipes = res.data;
            renderMatrixTable();
            renderPipesManagementList();
            if (calculatedPipes.length > 0) {
                if (selectedPipeIndex >= calculatedPipes.length) selectedPipeIndex = 0;
                updateVisualizers(calculatedPipes[selectedPipeIndex]);
            }
        }
    } catch (e) {
        console.error("Calculation error:", e);
    }
}

function renderMatrixTable() {
    const tableBody = document.getElementById("matrix-table-body");
    if (!tableBody || calculatedPipes.length === 0) return;

    let html = "";
    const explanations = calculatedPipes[0].explanations || {};

    const getExp = (key) => {
        const expObj = explanations[key];
        if (!expObj) return "";
        return currentLang === "en" ? expObj.en : expObj.tr;
    };

    // Header parameters
    const headerRows = [
        { label: "ÇAP (inch)", exp: getExp('diameter'), extractor: p => `<span class="font-bold text-gray-900">${p.input_summary.diameter_inch}</span>` },
        { label: "ÇAP (mm)", exp: "Boru Gerçek Dış Çapı (OD mm)", extractor: p => `<span class="font-semibold text-gray-800">${p.input_summary.diameter_mm}</span>` },
        { label: "Design Basıncı / Faktör", exp: getExp('design_factor'), extractor: p => `<span class="text-blue-900 font-medium">${p.input_summary.design_factor_str}</span>` },
        { label: "Et Kalınlığı (mm)", exp: getExp('wall_thickness'), extractor: p => `<span class="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">${p.input_summary.wall_thickness_mm.toFixed(2)}</span>` },
        { label: "Üretim Yöntemi", exp: getExp('process'), extractor: p => `<span class="font-semibold text-amber-800">${p.input_summary.manufacturing_process}</span>` },
        { label: "Malzeme Kalitesi", exp: getExp('grade'), extractor: p => `<span class="font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">${p.input_summary.material_grade}</span>` },
        { label: "SMYS (Psi)", exp: getExp('smys'), extractor: p => `<span class="font-mono font-bold">${p.mechanical_properties.smys_psi}</span>` },
    ];

    headerRows.forEach(hr => {
        html += `<tr class="border-b border-gray-400">
            <td class="th-main text-left font-bold px-3 py-1.5 min-w-[170px]">${hr.label}</td>
            <td class="bg-slate-100 text-slate-600 text-[11px] px-2 py-1 italic text-left max-w-[280px]">${hr.exp}</td>`;
        calculatedPipes.forEach(p => {
            html += `<td class="text-center font-semibold th-sub px-2 py-1.5">${hr.extractor(p)}</td>`;
        });
        html += `</tr>`;
    });

    // Chemical Block
    const chemRows = [
        { elem: "C", limitType: "Max %", ext: p => p.chemical_analysis.C_max.toFixed(2) },
        { elem: "Mn", limitType: "Max %", ext: p => p.chemical_analysis.Mn_max.toFixed(2) },
        { elem: "P", limitType: "Max %", ext: p => p.chemical_analysis.P_max.toFixed(3) },
        { elem: "S", limitType: "Max %", ext: p => p.chemical_analysis.S_max.toFixed(3) },
        { elem: "Nb", limitType: "Min%-Max%", ext: p => p.chemical_analysis.Nb_min_max },
        { elem: "V", limitType: "Max %", ext: p => p.chemical_analysis.V_max.toFixed(2) },
        { elem: "Ti", limitType: "Max %", ext: p => p.chemical_analysis.Ti_max.toFixed(2) },
        { elem: "N", limitType: "Max %", ext: p => p.chemical_analysis.N_max.toFixed(3) }
    ];

    chemRows.forEach((cr, idx) => {
        html += `<tr class="border-b border-gray-300">`;
        if (idx === 0) {
            html += `<td rowspan="${chemRows.length}" class="th-side text-center font-bold px-2 py-1 border-r border-gray-400">Kimyasal Analiz</td>
                     <td rowspan="${chemRows.length}" class="bg-slate-50 text-slate-600 text-[11px] px-2 py-1 italic text-left border-r border-gray-300">${getExp('chemical')}</td>`;
        }
        html += `<td class="font-bold text-center bg-gray-100 px-1 py-1 hidden"></td>`; // dummy
        html += ``;
        calculatedPipes.forEach(p => {
            html += `<td class="text-center font-mono text-xs px-2 py-1">${cr.elem} (${cr.limitType}): <strong>${cr.ext(p)}</strong></td>`;
        });
        html += `</tr>`;
    });

    // Wall Thickness Tolerance Block
    html += `<tr class="border-b border-gray-300">
        <td class="th-side text-left font-bold px-3 py-1 text-xs">Et Kalınlığı: Min. (mm)</td>
        <td class="bg-slate-100 text-slate-600 text-[11px] px-2 py-1 italic text-left">${getExp('wall_thickness_tol')}</td>`;
    calculatedPipes.forEach(p => {
        html += `<td class="text-center font-mono font-bold text-red-700 px-2 py-1">${p.wall_thickness_tolerance.min_mm.toFixed(2)}</td>`;
    });
    html += `</tr>`;

    html += `<tr class="border-b border-gray-400">
        <td class="th-side text-left font-bold px-3 py-1 text-xs">Et Kalınlığı: Max. (mm)</td>
        <td class="bg-slate-100 text-slate-600 text-[11px] px-2 py-1 italic text-left">${getExp('wall_thickness_tol')}</td>`;
    calculatedPipes.forEach(p => {
        html += `<td class="text-center font-mono font-bold text-emerald-700 px-2 py-1">${p.wall_thickness_tolerance.max_mm.toFixed(2)}</td>`;
    });
    html += `</tr>`;

    // Remaining Inspection Parameters
    const standardRows = [
        { label: "Yield Min. (Psi-Mpa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_min_psi} / ${p.mechanical_properties.yield_min_mpa}` },
        { label: "Yield Max. (Psi-Mpa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_max_psi} / ${p.mechanical_properties.yield_max_mpa}` },
        { label: "Tensile Min (Psi-Mpa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_min_psi} / ${p.mechanical_properties.tensile_min_mpa}` },
        { label: "Tensile Max (Psi-Mpa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_max_psi} / ${p.mechanical_properties.tensile_max_mpa}` },
        { label: "Hydro Test Basıncı Max.(Bar)", exp: getExp('hydro_test'), ext: p => `<span class="font-bold text-blue-700">${p.hydrostatic_test.hydro_test_max_bar.toFixed(2)}</span>` },
        { label: "Hydro Test Basıncı Min.(Bar)", exp: "P_max - 2.0 Bar (Test Alt Sınırı)", ext: p => p.hydrostatic_test.hydro_test_min_bar.toFixed(2) },
        { label: "API 5L Standart Test Pressure (Bar)", exp: getExp('api_std_test'), ext: p => `<span class="font-semibold text-slate-800">${p.hydrostatic_test.api_5l_std_test_bar.toFixed(2)}</span>` },
        { label: "API 5L Alternative Test Pressure (Bar)", exp: "D/t < 30 Alternatif Basınç", ext: p => p.hydrostatic_test.api_5l_alt_test_bar },
        { label: "Boru Çap Toleransı - Boru Ucu Max / Min", exp: getExp('diameter_tol'), ext: p => `[${p.dimensional_tolerances.diameter_end_min_mm.toFixed(1)} - ${p.dimensional_tolerances.diameter_end_max_mm.toFixed(1)}] mm` },
        { label: "Boru Çap Toleransı - Gövde Max / Min", exp: getExp('diameter_tol'), ext: p => `[${p.dimensional_tolerances.diameter_body_min_mm.toFixed(1)} - ${p.dimensional_tolerances.diameter_body_max_mm.toFixed(1)}] mm` },
        { label: "Boru Çevre Toleransı - Boru Ucu (mm)", exp: getExp('circumference_tol'), ext: p => `[${p.dimensional_tolerances.circ_end_min_mm.toFixed(1)} - ${p.dimensional_tolerances.circ_end_max_mm.toFixed(1)}]` },
        { label: "Boru Çevre Toleransı - Gövde (mm)", exp: getExp('circumference_tol'), ext: p => `[${p.dimensional_tolerances.circ_body_min_mm.toFixed(1)} - ${p.dimensional_tolerances.circ_body_max_mm.toFixed(1)}]` },
        { label: "Ovalite - Boru Ucu / Gövde (mm)", exp: getExp('ovality'), ext: p => `${p.dimensional_tolerances.ovality_end_mm} / ${p.dimensional_tolerances.ovality_body_mm}` },
        { label: "Minimum Uzama - Malzeme (%)", exp: getExp('elongation'), ext: p => `<span class="font-bold text-teal-800">${p.toughness_and_tests.elongation_mat_min_percent.toFixed(2)}%</span>` },
        { label: "Minimum Uzama - Kaynak (%)", exp: "Kaynak Dikişi Min. %10 Uzama", ext: p => `${p.toughness_and_tests.elongation_weld_min_percent.toFixed(1)}%` },
        { label: "Radial Offset Max. (mm)", exp: getExp('radial_offset'), ext: p => p.weld_and_geometry.radial_offset_max_mm },
        { label: "Kaynak Yüksekliği - İç / Dış (mm)", exp: getExp('weld_height'), ext: p => `İç: ${p.weld_and_geometry.weld_height_inside_mm} | Dış: ${p.weld_and_geometry.weld_height_outside_mm}` },
        { label: "Misalignment (mm)", exp: getExp('misalignment'), ext: p => p.weld_and_geometry.misalignment_max_mm },
        { label: "Çentik Darbe (J) - Malzeme / Kaynak", exp: getExp('cvn'), ext: p => `${p.toughness_and_tests.notch_impact_mat_j} J / ${p.toughness_and_tests.notch_impact_weld_j} J` },
        { label: "Çentik Numunesi Boyutu", exp: "API 5L Tablo 22", ext: p => p.toughness_and_tests.notch_specimen_size },
        { label: "Akma Çekme Oranı Max.", exp: getExp('yt_ratio'), ext: p => p.mechanical_properties.yield_to_tensile_ratio_max },
        { label: "Artık Sress Testi Max (mm)", exp: getExp('residual_stress'), ext: p => `<span class="font-bold text-indigo-900">${typeof p.toughness_and_tests.residual_stress_max_mm === 'number' ? p.toughness_and_tests.residual_stress_max_mm.toFixed(1) : p.toughness_and_tests.residual_stress_max_mm}</span>` },
        { label: "Yırtılma Testi (DWTT)", exp: getExp('dwtt'), ext: p => p.toughness_and_tests.dwtt_test === "Var" ? `<span class="badge-pass font-bold">Var (D>=508mm)</span>` : `<span class="text-gray-500">TEST YOK</span>` },
        { label: "Sertlik TESTİ", exp: getExp('hardness'), ext: p => p.toughness_and_tests.hardness_test_max },
        { label: "Mandrel Çapı / Çene Açıklığı (mm)", exp: getExp('mandrel_jaw'), ext: p => `${typeof p.toughness_and_tests.mandrel_dia_max_mm === 'number' ? p.toughness_and_tests.mandrel_dia_max_mm.toFixed(1) : p.toughness_and_tests.mandrel_dia_max_mm} / ${typeof p.toughness_and_tests.jaw_opening_max_mm === 'number' ? p.toughness_and_tests.jaw_opening_max_mm.toFixed(1) : p.toughness_and_tests.jaw_opening_max_mm}` },
        { label: "FLATTENING - Kaynak / Çatlak Açılma", exp: getExp('flattening'), ext: p => `${p.flattening.weld_opening_height_mm} / ${p.flattening.material_crack_height_mm}` },
        { label: "Boru Ucu Kaynak Çatılaşma / Diklik", exp: `${getExp('peaking')} / ${getExp('squareness')}`, ext: p => `Çatı: ${p.dimensional_tolerances.pipe_end_peaking_max_mm} mm | Diklik: ${p.dimensional_tolerances.pipe_end_squareness_max_mm} mm` },
        { label: "Tamir Kaynağı Uzunluğu & Ön Isıtma", exp: getExp('weld_repair'), ext: p => `${p.weld_and_geometry.weld_repair_length_max_mm} mm (${p.weld_and_geometry.weld_repair_preheat})` },
        { label: "Ağırlık Nominal (Min / Max) Kg/m", exp: getExp('weight'), ext: p => `<strong>${p.weights_and_safety.weight_nominal_kg_m.toFixed(1)}</strong> (${p.weights_and_safety.weight_min_kg_m.toFixed(1)} - ${p.weights_and_safety.weight_max_kg_m.toFixed(1)})` },
        { label: "Operating pressure/ SMYS", exp: "İşletme Gerilmesi / SMYS Oranı", ext: p => `<span class="font-semibold text-blue-800">${p.weights_and_safety.operating_press_over_smys_percent}</span>` },
        { label: "841.1.2 Fracture Control and Arrest", exp: getExp('fracture_control'), ext: p => p.weights_and_safety.fracture_control_asme_841_1_2.includes("Annex G") && p.weights_and_safety.fracture_control_asme_841_1_2.includes("Bakınız") ? `<span class="text-amber-800 font-semibold">${p.weights_and_safety.fracture_control_asme_841_1_2}</span>` : `<span class="text-gray-600">${p.weights_and_safety.fracture_control_asme_841_1_2}</span>` },
        { label: "D/t Oranı & Tasarım Formülü", exp: getExp('thick_wall_alt'), ext: p => `<strong>D/t = ${p.weights_and_safety.d_over_t.toFixed(1)}</strong> (${p.weights_and_safety.design_formula_asme_841_1_1})` },
        { label: "Alternative Design Pressure", exp: "ASME B31.8 841.1.1 Alternatif Basınç", ext: p => typeof p.weights_and_safety.alternative_design_pressure_bar === 'number' ? `<span class="font-bold text-purple-800">${p.weights_and_safety.alternative_design_pressure_bar.toFixed(2)} Bar</span>` : p.weights_and_safety.alternative_design_pressure_bar }
    ];

    standardRows.forEach(sr => {
        html += `<tr class="border-b border-gray-300 hover:bg-blue-50">
            <td class="label-cell text-left px-3 py-1 font-semibold">${sr.label}</td>
            <td class="bg-slate-100 text-slate-600 text-[11px] px-2 py-1 italic text-left">${sr.exp}</td>`;
        calculatedPipes.forEach(p => {
            html += `<td class="text-center text-xs px-2 py-1">${sr.ext(p)}</td>`;
        });
        html += `</tr>`;
    });

    tableBody.innerHTML = html;
}

function renderPipesManagementList() {
    const list = document.getElementById("pipes-management-list");
    if (!list) return;

    let html = "";
    activeProject.pipes.forEach((p, idx) => {
        const isSelected = idx === selectedPipeIndex;
        html += `
        <div class="flex items-center justify-between p-2.5 rounded-lg border ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'} shadow-sm transition">
            <div class="flex items-center space-x-3 cursor-pointer flex-1" onclick="selectPipe(${idx})">
                <span class="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">${idx + 1}</span>
                <div>
                    <h4 class="text-sm font-bold text-gray-800">${p.diameter_inch} - ${p.material_grade} (${p.manufacturing_process})</h4>
                    <p class="text-xs text-gray-500">t = ${p.wall_thickness_mm} mm | F = ${p.design_factor_str}</p>
                </div>
            </div>
            <div class="flex items-center space-x-1">
                <button onclick="clonePipe(${idx})" class="p-1.5 text-gray-500 hover:text-blue-600 rounded hover:bg-gray-100" title="Klonla">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                </button>
                <button onclick="deletePipe(${idx})" class="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-gray-100" title="Sil">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </div>
        </div>
        `;
    });
    list.innerHTML = html;
}

function selectPipe(idx) {
    selectedPipeIndex = idx;
    renderPipesManagementList();
    if (calculatedPipes[idx]) {
        updateVisualizers(calculatedPipes[idx]);
    }
}

function clonePipe(idx) {
    const pipe = JSON.parse(JSON.stringify(activeProject.pipes[idx]));
    pipe.id = "pipe_" + Date.now();
    activeProject.pipes.splice(idx + 1, 0, pipe);
    ProjectStorage.saveToLocalStorage(activeProject);
    calculateAndRenderAll();
    showToast("Boru başarıyla klonlandı!", "success");
}

function deletePipe(idx) {
    if (activeProject.pipes.length <= 1) {
        showToast("En az bir boru bulunmalıdır!", "error");
        return;
    }
    activeProject.pipes.splice(idx, 1);
    if (selectedPipeIndex >= activeProject.pipes.length) selectedPipeIndex = 0;
    ProjectStorage.saveToLocalStorage(activeProject);
    calculateAndRenderAll();
    showToast("Boru silindi.", "info");
}

function updateVisualizers(pipeData) {
    if (!pipeData) return;
    PipeVisualizer2D.render("viewport-2d", pipeData);
    if (visualizer3DInstance) {
        visualizer3DInstance.renderPipe(pipeData);
    }
}

// BOTAŞ auto-lookup for modal inputs
async function updateBotasDefaultsInModal() {
    const stdSelect = document.getElementById("new-pipe-standard");
    const isBotas = stdSelect ? stdSelect.value === "BOTAŞ" : true;
    const diaSelect = document.getElementById("new-pipe-dia");
    const factorSelect = document.getElementById("new-pipe-factor");
    const gradeSelect = document.getElementById("new-pipe-grade");
    const thkInput = document.getElementById("new-pipe-thk");
    const hintDiv = document.getElementById("botas-hint-msg");

    if (isBotas && diaSelect && factorSelect) {
        const dia = diaSelect.value;
        const factor = factorSelect.value;
        try {
            const resp = await fetch(`/api/botas-lookup?diameter_inch=${encodeURIComponent(dia)}&factor=${encodeURIComponent(factor)}`);
            const data = await resp.json();
            if (data.status === "success") {
                if (gradeSelect) gradeSelect.value = data.material;
                if (thkInput) thkInput.value = data.thickness.toFixed(2);
                if (hintDiv) {
                    hintDiv.innerHTML = `ℹ BOTAŞ Standardı: <strong>${data.material}</strong> malzeme ve <strong>${data.thickness} mm</strong> et kalınlığı otomatik uygulandı.`;
                    hintDiv.classList.remove("hidden");
                }
            }
        } catch (e) {
            console.error("Botas lookup error:", e);
        }
    } else {
        if (hintDiv) hintDiv.classList.add("hidden");
    }
}

function setupEventListeners() {
    // Add Pipe Form Modal
    const addBtn = document.getElementById("btn-open-add-pipe-modal");
    const addModal = document.getElementById("add-pipe-modal");
    if (addBtn && addModal) {
        addBtn.addEventListener("click", () => {
            addModal.classList.remove("hidden");
            updateBotasDefaultsInModal();
        });
    }

    const diaSelect = document.getElementById("new-pipe-dia");
    const factorSelect = document.getElementById("new-pipe-factor");
    const stdSelect = document.getElementById("new-pipe-standard");
    if (diaSelect) diaSelect.addEventListener("change", updateBotasDefaultsInModal);
    if (factorSelect) factorSelect.addEventListener("change", updateBotasDefaultsInModal);
    if (stdSelect) stdSelect.addEventListener("change", updateBotasDefaultsInModal);

    // Export Excel Button
    const btnExcel = document.getElementById("btn-export-excel");
    if (btnExcel) {
        btnExcel.addEventListener("click", async () => {
            btnExcel.disabled = true;
            btnExcel.innerHTML = "Excel Hazırlanıyor...";
            try {
                const resp = await fetch("/api/export-excel", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        project_info: activeProject.project_info,
                        pipes: activeProject.pipes,
                        lang: currentLang
                    })
                });
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `Boru_Kabul_Matrisi_${activeProject.project_info.project_no || 'API5L'}.xlsx`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                showToast("Excel dosyası başarıyla indirildi!", "success");
            } catch (e) {
                console.error("Excel export error:", e);
                showToast("Excel oluşturulurken hata oluştu!", "error");
            } finally {
                btnExcel.disabled = false;
                btnExcel.innerHTML = `
                    <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    Excel (.xlsx) Olarak İndir
                `;
            }
        });
    }

    // Save Project Button
    const btnSaveProj = document.getElementById("btn-save-project-json");
    if (btnSaveProj) {
        btnSaveProj.addEventListener("click", () => {
            ProjectStorage.downloadProjectJSON(activeProject);
            showToast("Proje dosyası (.pipeproj) indirildi!", "success");
        });
    }

    // Load Project Input
    const fileInput = document.getElementById("input-load-project-file");
    if (fileInput) {
        fileInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (file) {
                try {
                    const loaded = await ProjectStorage.readProjectJSONFile(file);
                    activeProject = loaded;
                    ProjectStorage.saveToLocalStorage(activeProject);
                    await calculateAndRenderAll();
                    showToast("Proje başarıyla yüklendi!", "success");
                } catch (err) {
                    showToast(err.message, "error");
                }
            }
        });
    }

    // Wall Thickness Calculator Form
    const wtForm = document.getElementById("wall-thickness-calc-form");
    if (wtForm) {
        wtForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(wtForm);
            const reqData = {
                diameter_inch: formData.get("diameter_inch"),
                material_grade: formData.get("material_grade"),
                design_pressure_bar: parseFloat(formData.get("design_pressure_bar")),
                design_factor_f: parseFloat(formData.get("design_factor_f")),
                longitudinal_joint_factor_e: parseFloat(formData.get("longitudinal_joint_factor_e")),
                temperature_derating_factor_t: parseFloat(formData.get("temperature_derating_factor_t")),
                corrosion_allowance_mm: parseFloat(formData.get("corrosion_allowance_mm")),
                location_type: formData.get("location_type")
            };

            const resp = await fetch("/api/wall-thickness", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(reqData)
            });
            const res = await resp.json();
            if (res.status === "success") {
                renderWallThicknessResult(res.data);
            }
        });
    }

    // Verification Form
    const verForm = document.getElementById("pipe-verification-form");
    if (verForm) {
        verForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const selectedPipe = activeProject.pipes[selectedPipeIndex] || activeProject.pipes[0];
            const formData = new FormData(verForm);
            const actualData = {};
            formData.forEach((val, key) => {
                if (val !== "") actualData[key] = parseFloat(val);
            });

            const resp = await fetch("/api/verify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    pipe_config: selectedPipe,
                    actual_data: actualData
                })
            });
            const res = await resp.json();
            if (res.status === "success") {
                renderVerificationResult(res.verification);
            }
        });
    }
}

function renderWallThicknessResult(data) {
    const resDiv = document.getElementById("wt-results-panel");
    if (!resDiv) return;

    resDiv.classList.remove("hidden");
    const r = data.calculation_results;
    resDiv.innerHTML = `
        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg shadow-sm">
            <h4 class="text-md font-bold text-blue-950 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                ASME B31.8 & BOTAŞ Hesaplama Sonuçları
            </h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">Teorik Et Kalınlığı (t):</span>
                    <span class="font-bold text-gray-900 text-lg">${r.t_theoretical_mm} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">Gereken Et Kalınlığı (t_req):</span>
                    <span class="font-bold text-indigo-700 text-lg">${r.t_required_asme_b31_8_mm} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-blue-300 bg-blue-50/50">
                    <span class="text-xs text-blue-800 font-semibold block">Seçilen Nominal (ASME B36.10):</span>
                    <span class="font-bold text-blue-900 text-lg">${r.selected_nominal_thickness_asme_b36_10_mm} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">Negatif Tolerans Sınırı (%12.5):</span>
                    <span class="font-bold text-gray-900 text-lg">${r.negative_tolerance_min_mm} mm</span>
                </div>
            </div>
            <div class="mt-3 flex items-center justify-between">
                <span class="text-xs text-gray-600">BOTAŞ Standart Tavsiyesi: <strong>${r.botas_standard_thickness_mm > 0 ? r.botas_standard_thickness_mm + ' mm' : 'Özel Hesaplama'}</strong></span>
                <span class="${r.is_nominal_sufficient ? 'badge-pass' : 'badge-fail'}">
                    ${r.is_nominal_sufficient ? '✓ Seçilen Et Kalınlığı Güvenli ve Uygun' : '⚠ Et Kalınlığı Yetersiz!'}
                </span>
            </div>
        </div>
    `;
}

function renderVerificationResult(data) {
    const resDiv = document.getElementById("verification-results-panel");
    if (!resDiv) return;

    resDiv.classList.remove("hidden");
    let html = `
        <div class="p-4 ${data.overall_status === 'ACCEPTED' ? 'bg-emerald-50 border-emerald-300' : 'bg-red-50 border-red-300'} border rounded-lg shadow-sm">
            <div class="flex items-center justify-between mb-3">
                <h4 class="text-lg font-bold ${data.overall_status === 'ACCEPTED' ? 'text-emerald-900' : 'text-red-900'}">
                    Genel Fabrika Kabul Kararı: ${data.overall_badge}
                </h4>
                <span class="text-sm font-semibold text-gray-700">
                    ${data.passed_count} / ${data.checks_count} Parametre Uygun
                </span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-xs text-left border-collapse bg-white rounded border border-gray-300">
                    <thead class="bg-gray-100 text-gray-700 font-bold border-b border-gray-300">
                        <tr>
                            <th class="p-2">Kategori</th>
                            <th class="p-2">Parametre</th>
                            <th class="p-2 text-center">Ölçülen Değer</th>
                            <th class="p-2 text-center">Şartname Limiti</th>
                            <th class="p-2 text-center">Sonuç</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    data.checks.forEach(c => {
        html += `
            <tr class="border-b border-gray-200 hover:bg-gray-50">
                <td class="p-2 font-medium text-gray-600">${c.category}</td>
                <td class="p-2 font-bold text-gray-800">${c.parameter}</td>
                <td class="p-2 text-center font-mono font-semibold">${c.actual_value}</td>
                <td class="p-2 text-center font-mono text-gray-600">${c.required_limit}</td>
                <td class="p-2 text-center">
                    <span class="${c.status === 'PASS' ? 'badge-pass' : 'badge-fail'} font-bold">
                        ${c.status === 'PASS' ? 'UYGUN' : 'RED'}
                    </span>
                </td>
            </tr>
        `;
    });

    html += `</tbody></table></div></div>`;
    resDiv.innerHTML = html;
}

function showToast(msg, type = "info") {
    const toast = document.getElementById("app-toast");
    if (!toast) return;
    toast.innerText = msg;
    toast.className = `fixed bottom-5 right-5 px-4 py-2.5 rounded-lg shadow-lg text-white font-medium text-sm transition-all duration-300 z-50 ${type === 'success' ? 'bg-emerald-600' : (type === 'error' ? 'bg-red-600' : 'bg-blue-600')}`;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 3000);
}
