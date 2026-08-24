/**
 * Main Frontend Application Logic for API 5L Pipe QA/QC & Design Suite
 * - Multi-pipe 2D & 3D real-time synchronization
 * - Top Executive KPI Summary Cards
 * - Sticky & Collapsible Accordion Parameter Matrix
 * - Live Parameter Search Filter
 * - 3D PNG Snapshot Export
 * - Clean start with BOTAŞ auto-populate
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
        language: "tr",
        heat_number: "",
        certificate_number: "",
        quantity: "",
        purchase_order_number: "",
        inspection_company: ""
    },
    pipes: []
};

let calculatedPipes = [];
let selectedPipeIndex = 0;
let visualizer3DInstance = null;
let lastVerification = null;

document.addEventListener("DOMContentLoaded", async () => {
    const savedLang = localStorage.getItem("api5l_lang") || "tr";
    setLanguage(savedLang);

    const cachedProj = ProjectStorage.loadFromLocalStorage();
    if (cachedProj && cachedProj.pipes) {
        activeProject = cachedProj;
    } else {
        activeProject.pipes = [];
    }

    await calculateAndRenderAll();
    loadTestPlan();

    setTimeout(() => {
        visualizer3DInstance = new PipeVisualizer3D("viewport-3d");
        visualizer3DInstance.init();
        if (calculatedPipes.length > 0) {
            updateVisualizers(calculatedPipes[selectedPipeIndex] || calculatedPipes[0]);
        }
    }, 400);

    setupEventListeners();

    // Automatic update check on startup (runs asynchronously in background)
    setTimeout(() => {
        checkForAppUpdates(true);
    }, 1200);
});

async function checkForAppUpdates(isSilent = false) {
    try {
        const resp = await fetch("/api/check-update");
        const data = await resp.json();
        const banner = document.getElementById("app-update-banner");
        const statusSpan = document.getElementById("manual-update-status");

        if (data.update_available) {
            if (banner) {
                document.getElementById("update-banner-version").innerText = `v${data.latest_version}`;
                document.getElementById("update-banner-link").href = data.html_url;
                
                // Set direct asset download links if available
                const winLink = document.getElementById("update-win-download-link");
                const macLink = document.getElementById("update-mac-download-link");
                if (winLink && data.download_assets.windows_exe) {
                    winLink.href = data.download_assets.windows_exe;
                    winLink.classList.remove("hidden");
                }
                if (macLink && data.download_assets.macos_dmg) {
                    macLink.href = data.download_assets.macos_dmg;
                    macLink.classList.remove("hidden");
                }

                banner.classList.remove("hidden");
            }
            if (statusSpan) {
                statusSpan.innerHTML = `<span class="text-emerald-700 font-bold">🎉 Yeni bir sürüm mevcut: v${data.latest_version}</span> <a href="${data.html_url}" target="_blank" class="underline text-blue-600 font-bold ml-2">İndir</a>`;
            }
            if (!isSilent) {
                showToast(`Yeni güncelleme mevcut: v${data.latest_version}`, "info");
            }
        } else {
            if (statusSpan) {
                statusSpan.innerHTML = `<span class="text-slate-600 font-medium">✓ Uygulamanız güncel (v${data.current_version}).</span>`;
            }
            if (!isSilent) {
                showToast("Uygulamanız en güncel sürümdedir.", "success");
            }
        }
    } catch (e) {
        console.warn("Update check note:", e);
        const statusSpan = document.getElementById("manual-update-status");
        if (statusSpan && !isSilent) {
            statusSpan.innerHTML = `<span class="text-slate-400">Çevrimdışı (Güncelleme kontrolü yapılamadı).</span>`;
        }
    }
}

async function calculateAndRenderAll() {
    try {
        if (!activeProject.pipes || activeProject.pipes.length === 0) {
            calculatedPipes = [];
            renderEmptyState();
            renderPipesManagementList();
            render3DPipeChips();
            hideKPICards();
            return;
        }

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
            if (selectedPipeIndex >= calculatedPipes.length) selectedPipeIndex = 0;
            renderKPICards(calculatedPipes[selectedPipeIndex]);
            renderMatrixTable();
            renderPipesManagementList();
            render3DPipeChips();
            if (calculatedPipes.length > 0) {
                updateVisualizers(calculatedPipes[selectedPipeIndex]);
            }
        }
    } catch (e) {
        console.error("Calculation error:", e);
    }
}

function renderEmptyState() {
    const tableBody = document.getElementById("matrix-table-body");
    if (!tableBody) return;
    tableBody.innerHTML = `
        <tr>
            <td colspan="12" class="py-16 text-center text-slate-400">
                <svg class="w-12 h-12 mx-auto mb-3 opacity-40 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <h4 class="text-base font-bold text-slate-700 mb-1">Matriste Henüz Boru Sütunu Bulunmuyor</h4>
                <p class="text-xs text-slate-500 max-w-md mx-auto mb-4">Yukarıdaki <strong>"Yeni Boru Sütunu Ekle"</strong> butonuna basarak boru ekleyebilir veya BOTAŞ otomatik doldurma ile tüm dizayn faktörlerini tek tıkla matrise yerleştirebilirsiniz.</p>
                <button onclick="document.getElementById('btn-open-add-pipe-modal').click()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold px-4 py-2 rounded-lg text-xs shadow transition">
                    + Yeni Boru Sütunu Ekle
                </button>
            </td>
        </tr>
    `;
}

function renderKPICards(pipeData) {
    const panel = document.getElementById("kpi-cards-panel");
    if (!panel || !pipeData) return;

    panel.classList.remove("hidden");
    const p = pipeData;

    document.getElementById("kpi-active-pipe-title").innerText = `${p.input_summary.diameter_inch} (${p.input_summary.diameter_mm} mm) - ${p.input_summary.material_grade} | ${p.input_summary.manufacturing_process} | t = ${p.input_summary.wall_thickness_mm.toFixed(2)} mm`;
    document.getElementById("kpi-hydro-val").innerText = `${p.hydrostatic_test.hydro_test_max_bar.toFixed(1)} Bar`;
    document.getElementById("kpi-hydro-sub").innerText = `Min: ${p.hydrostatic_test.hydro_test_min_bar.toFixed(1)} | Std: ${p.hydrostatic_test.api_5l_std_test_bar.toFixed(1)} Bar`;
    
    document.getElementById("kpi-weight-val").innerText = `${p.weights_and_safety.weight_nominal_kg_m.toFixed(1)} kg/m`;
    document.getElementById("kpi-weight-sub").innerText = `Tolerans: [${p.weights_and_safety.weight_min_kg_m.toFixed(1)} - ${p.weights_and_safety.weight_max_kg_m.toFixed(1)}] kg/m`;
    
    document.getElementById("kpi-dt-val").innerText = `D/t = ${p.weights_and_safety.d_over_t.toFixed(1)}`;
    document.getElementById("kpi-dt-sub").innerText = p.weights_and_safety.design_formula_asme_841_1_1;
    
    document.getElementById("kpi-fracture-val").innerText = p.weights_and_safety.fracture_control_asme_841_1_2.includes("Annex G") ? "Annex G Zorunlu" : "Normal Emniyet";
    document.getElementById("kpi-fracture-sub").innerText = `Gerilme: ${p.weights_and_safety.operating_press_over_smys_percent}`;
}

function hideKPICards() {
    const panel = document.getElementById("kpi-cards-panel");
    if (panel) panel.classList.add("hidden");
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

    const isColActive = (idx) => idx === selectedPipeIndex;

    // SECTION 0: COLUMN SELECTOR & FOCUS INDICATOR ROW (Sticky Top)
    html += `<tr class="border-b-2 border-slate-400 bg-slate-100 sticky-top-header">
        <td class="th-main sticky-left text-left font-bold px-3 py-2 min-w-[210px] text-xs uppercase tracking-wider">
            ⚡ BORU ODAK / SEÇİM
        </td>`;
    calculatedPipes.forEach((p, idx) => {
        const active = isColActive(idx);
        const headerClass = active ? 'active-pipe-header' : 'bg-slate-100 hover:bg-blue-100';
        html += `
            <td onclick="selectPipe(${idx})" class="pipe-header-cell text-center p-2 cursor-pointer ${headerClass}" title="Bu boruya odaklanmak için tıklayın">
                <div class="flex flex-col items-center justify-center">
                    ${active ? '<span class="active-col-indicator-badge mb-1">★ SEÇİLİ BORU</span>' : `<span class="text-[10px] text-slate-500 font-semibold mb-0.5">Sütun ${idx + 1}</span>`}
                    <span class="text-xs font-bold ${active ? 'text-white' : 'text-blue-700 hover:underline'}">
                        ${active ? `Boru ${idx + 1}` : 'Odaklan ➔'}
                    </span>
                </div>
            </td>`;
    });
    html += `<td class="sticky-right bg-slate-100 text-slate-600 text-[11px] px-3 py-1 font-bold italic text-left max-w-[280px] border-l-2 border-slate-300">
        Standart & Mühendislik Açıklamaları
    </td></tr>`;

    // SECTION 1: HEADER PARAMETERS (Always visible / uncollapsed)
    const headerRows = [
        { label: "ÇAP (inch)", exp: getExp('diameter'), extractor: p => `<strong>${p.input_summary.diameter_inch}</strong>` },
        { label: "ÇAP (mm)", exp: "Boru Gerçek Dış Çapı (OD mm)", extractor: p => `${p.input_summary.diameter_mm.toFixed(2)} mm` },
        { label: "Design Basıncı / Faktör", exp: getExp('design_factor'), extractor: p => `${p.input_summary.design_factor_str}` },
        { label: "Et Kalınlığı (mm)", exp: getExp('wall_thickness'), extractor: p => `<strong>${p.input_summary.wall_thickness_mm.toFixed(2)} mm</strong>` },
        { label: "Üretim Yöntemi", exp: getExp('process'), extractor: p => `${p.input_summary.manufacturing_process}` },
        { label: "Malzeme Kalitesi", exp: getExp('grade'), extractor: p => `<strong>${p.input_summary.material_grade}</strong>` },
        { label: "SMYS (Psi)", exp: getExp('smys'), extractor: p => `${Number(p.mechanical_properties.smys_psi).toFixed(0)} psi` },
    ];

    headerRows.forEach((hr, rIdx) => {
        html += `<tr class="border-b border-gray-300 searchable-row">
            <td class="th-main sticky-left text-left font-bold px-3 py-1.5 min-w-[210px]">${hr.label}</td>`;
        calculatedPipes.forEach((p, idx) => {
            const active = isColActive(idx);
            const activeHeaderClass = active ? 'active-pipe-header' : (rIdx <= 3 ? 'th-sub' : '');
            const activeColClass = active ? 'active-pipe-col' : '';
            html += `<td onclick="selectPipe(${idx})" class="pipe-header-cell text-center px-2 py-1.5 ${activeHeaderClass} ${activeColClass}" title="3D/2D Modelde Odaklamak için Tıklayın">${hr.extractor(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left max-w-[280px] border-l-2 border-slate-300">${hr.exp}</td></tr>`;
    });

    // Helper for Accordion Section Headers
    const renderAccordionSectionHeader = (secId, title, count) => {
        const totalCols = calculatedPipes.length + 2;
        return `
            <tr class="accordion-header bg-slate-200 border-y-2 border-slate-400" onclick="toggleAccordion('${secId}')">
                <td colspan="${totalCols}" class="text-left px-3 py-2 font-bold text-slate-800 flex items-center justify-between text-xs tracking-wide">
                    <div class="flex items-center space-x-2">
                        <span id="icon-${secId}" class="accordion-icon text-slate-600 font-bold">▼</span>
                        <span>${title}</span>
                        <span class="bg-slate-300 text-slate-700 text-[10px] px-2 py-0.5 rounded-full font-semibold">${count} Parametre</span>
                    </div>
                    <span class="text-[11px] text-blue-700 font-semibold hover:underline">Genişlet / Daralt</span>
                </td>
            </tr>
        `;
    };

    // SECTION 2: CHEMICAL ANALYSIS BLOCK
    html += renderAccordionSectionHeader("sec-chem", "🧪 KİMYASAL BİLEŞİM ANALİZİ (PSL2 LİMİTLERİ)", "8");
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

    chemRows.forEach((cr) => {
        html += `<tr class="row-sec-chem border-b border-gray-300 searchable-row">`;
        html += `<td class="th-side sticky-left text-left font-bold px-3 py-1.5 text-xs">${cr.elem} (${cr.limitType})</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            html += `<td onclick="selectPipe(${cIdx})" class="text-center font-mono text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${cr.ext(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${getExp('chemical')}</td></tr>`;
    });

    // SECTION 3: MECHANICAL & HYDROSTATIC PRESSURE
    html += renderAccordionSectionHeader("sec-mech", "💥 MEKANİK MUKAVEMET & HİDROSTATİK FABRİKA BASINCI", "8");
    const mechRows = [
        { label: "Yield Min. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_min_psi.toFixed(0)} psi / ${p.mechanical_properties.yield_min_mpa.toFixed(1)} MPa` },
        { label: "Yield Max. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_max_psi.toFixed(0)} psi / ${p.mechanical_properties.yield_max_mpa.toFixed(1)} MPa` },
        { label: "Tensile Min. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_min_psi.toFixed(0)} psi / ${p.mechanical_properties.tensile_min_mpa.toFixed(1)} MPa` },
        { label: "Tensile Max. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_max_psi.toFixed(0)} psi / ${p.mechanical_properties.tensile_max_mpa.toFixed(1)} MPa` },
        { label: "Akma / Çekme Oranı Max. (Y/T)", exp: getExp('yt_ratio'), ext: p => p.mechanical_properties.yield_to_tensile_ratio_max.toFixed(2) },
        { label: "Hydro Test Basıncı Max. (Bar)", exp: getExp('hydro_test'), ext: p => `<span class="font-bold text-blue-700">${p.hydrostatic_test.hydro_test_max_bar.toFixed(2)} Bar</span>` },
        { label: "Hydro Test Basıncı Min. (Bar)", exp: "P_max - 2.0 Bar (Fabrika Test Alt Sınırı)", ext: p => `${p.hydrostatic_test.hydro_test_min_bar.toFixed(2)} Bar` },
        { label: "API 5L Standart Test Pressure (Bar)", exp: getExp('api_std_test'), ext: p => `${p.hydrostatic_test.api_5l_std_test_bar.toFixed(2)} Bar` },
    ];
    mechRows.forEach(mr => {
        html += `<tr class="row-sec-mech border-b border-gray-300 searchable-row">
            <td class="label-cell sticky-left text-left px-3 py-1.5 font-semibold">${mr.label}</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            html += `<td onclick="selectPipe(${cIdx})" class="text-center text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${mr.ext(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${mr.exp}</td></tr>`;
    });

    // SECTION 4: DIMENSIONAL & WELD TOLERANCES
    html += renderAccordionSectionHeader("sec-dim", "📐 BOYUTSAL & KAYNAK TOLERANSLARI", "11");
    const dimRows = [
        { label: "Et Kalınlığı: Min. (mm)", exp: getExp('wall_thickness_tol'), ext: p => `<span class="font-bold text-red-700">${p.wall_thickness_tolerance.min_mm.toFixed(2)} mm</span>` },
        { label: "Et Kalınlığı: Max. (mm)", exp: getExp('wall_thickness_tol'), ext: p => `<span class="font-bold text-emerald-700">${p.wall_thickness_tolerance.max_mm.toFixed(2)} mm</span>` },
        { label: "Boru Çap Toleransı - Boru Ucu Max/Min", exp: getExp('diameter_tol'), ext: p => `[${p.dimensional_tolerances.diameter_end_min_mm.toFixed(2)} - ${p.dimensional_tolerances.diameter_end_max_mm.toFixed(2)}] mm` },
        { label: "Boru Çap Toleransı - Gövde Max/Min", exp: getExp('diameter_tol'), ext: p => `[${p.dimensional_tolerances.diameter_body_min_mm.toFixed(2)} - ${p.dimensional_tolerances.diameter_body_max_mm.toFixed(2)}] mm` },
        { label: "Boru Çevre Toleransı - Boru Ucu (mm)", exp: getExp('circumference_tol'), ext: p => `[${typeof p.dimensional_tolerances.circ_end_min_mm === 'number' ? p.dimensional_tolerances.circ_end_min_mm.toFixed(2) : p.dimensional_tolerances.circ_end_min_mm} - ${typeof p.dimensional_tolerances.circ_end_max_mm === 'number' ? p.dimensional_tolerances.circ_end_max_mm.toFixed(2) : p.dimensional_tolerances.circ_end_max_mm}] mm` },
        { label: "Boru Çevre Toleransı - Gövde (mm)", exp: getExp('circumference_tol'), ext: p => `[${typeof p.dimensional_tolerances.circ_body_min_mm === 'number' ? p.dimensional_tolerances.circ_body_min_mm.toFixed(2) : p.dimensional_tolerances.circ_body_min_mm} - ${typeof p.dimensional_tolerances.circ_body_max_mm === 'number' ? p.dimensional_tolerances.circ_body_max_mm.toFixed(2) : p.dimensional_tolerances.circ_body_max_mm}] mm` },
        { label: "Ovalite - Boru Ucu / Gövde (mm)", exp: getExp('ovality'), ext: p => `Uç: ${p.dimensional_tolerances.ovality_end_mm} mm | Gövde: ${p.dimensional_tolerances.ovality_body_mm} mm` },
        { label: "Radial Offset Max. (mm)", exp: getExp('radial_offset'), ext: p => `${p.weld_and_geometry.radial_offset_max_mm} mm` },
        { label: "Kaynak Yüksekliği - İç / Dış (mm)", exp: getExp('weld_height'), ext: p => `İç: ${p.weld_and_geometry.weld_height_inside_mm} mm | Dış: ${p.weld_and_geometry.weld_height_outside_mm} mm` },
        { label: "Misalignment (mm)", exp: getExp('misalignment'), ext: p => `${p.weld_and_geometry.misalignment_max_mm} mm` },
        { label: "Boru Ucu Kaynak Çatılaşma / Diklik", exp: `${getExp('peaking')} / ${getExp('squareness')}`, ext: p => `Çatı: ${p.dimensional_tolerances.pipe_end_peaking_max_mm} mm | Diklik: ${p.dimensional_tolerances.pipe_end_squareness_max_mm} mm` },
    ];
    dimRows.forEach(dr => {
        html += `<tr class="row-sec-dim border-b border-gray-300 searchable-row">
            <td class="label-cell sticky-left text-left px-3 py-1.5 font-semibold">${dr.label}</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            html += `<td onclick="selectPipe(${cIdx})" class="text-center text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${dr.ext(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${dr.exp}</td></tr>`;
    });

    // SECTION 5: TOUGHNESS & SPECIAL FACTORY TESTS
    html += renderAccordionSectionHeader("sec-tests", "🔬 TOKLUK & ÖZEL FABRİKA KABUL TESTLERİ", "9");
    const testRows = [
        { label: "Minimum Uzama - Malzeme (%)", exp: getExp('elongation'), ext: p => `<span class="font-bold text-teal-800">${p.toughness_and_tests.elongation_mat_min_percent.toFixed(2)}%</span>` },
        { label: "Minimum Uzama - Kaynak (%)", exp: "Kaynak Dikişi Min. %10 Uzama", ext: p => `${typeof p.toughness_and_tests.elongation_weld_min_percent === 'number' ? p.toughness_and_tests.elongation_weld_min_percent.toFixed(2) : p.toughness_and_tests.elongation_weld_min_percent}%` },
        { label: "Çentik Darbe (J) - Malzeme / Kaynak", exp: getExp('cvn'), ext: p => `Gövde: ${p.toughness_and_tests.notch_impact_mat_j} J | Kaynak: ${p.toughness_and_tests.notch_impact_weld_j} J` },
        { label: "Artık Gerilme Testi Max (mm)", exp: getExp('residual_stress'), ext: p => `${typeof p.toughness_and_tests.residual_stress_max_mm === 'number' ? p.toughness_and_tests.residual_stress_max_mm.toFixed(2) + ' mm' : p.toughness_and_tests.residual_stress_max_mm}` },
        { label: "Yırtılma Testi (DWTT)", exp: getExp('dwtt'), ext: p => p.toughness_and_tests.dwtt_test === "Var" ? `<span class="badge-pass font-bold">Var (D ≥ 508mm)</span>` : `<span class="text-slate-400">TEST YOK</span>` },
        { label: "Sertlik TESTİ", exp: getExp('hardness'), ext: p => p.toughness_and_tests.hardness_test_max },
        { label: "Mandrel Çapı / Çene Açıklığı (mm)", exp: getExp('mandrel_jaw'), ext: p => `${typeof p.toughness_and_tests.mandrel_dia_max_mm === 'number' ? p.toughness_and_tests.mandrel_dia_max_mm.toFixed(2) : p.toughness_and_tests.mandrel_dia_max_mm} / ${typeof p.toughness_and_tests.jaw_opening_max_mm === 'number' ? p.toughness_and_tests.jaw_opening_max_mm.toFixed(2) : p.toughness_and_tests.jaw_opening_max_mm} mm` },
        { label: "FLATTENING - Kaynak / Çatlak Açılma", exp: getExp('flattening'), ext: p => `Kaynak: ${p.flattening.weld_opening_height_mm} mm | Çatlak: ${p.flattening.material_crack_height_mm} mm` },
        { label: "Tamir Kaynağı Uzunluğu & Ön Isıtma", exp: getExp('weld_repair'), ext: p => `${p.weld_and_geometry.weld_repair_length_max_mm} mm (${p.weld_and_geometry.weld_repair_preheat})` },
    ];
    testRows.forEach(tr => {
        html += `<tr class="row-sec-tests border-b border-gray-300 searchable-row">
            <td class="label-cell sticky-left text-left px-3 py-1.5 font-semibold">${tr.label}</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            html += `<td onclick="selectPipe(${cIdx})" class="text-center text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${tr.ext(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${tr.exp}</td></tr>`;
    });

    // SECTION 6: WEIGHT & ASME FRACTURE CONTROL
    html += renderAccordionSectionHeader("sec-weight", "⚖️ BORU AĞIRLIĞI & ASME KIRILMA EMNİYETİ", "4");
    const weightRows = [
        { label: "Ağırlık Nominal (Min / Max) Kg/m", exp: getExp('weight'), ext: p => `<strong>${p.weights_and_safety.weight_nominal_kg_m.toFixed(2)}</strong> (${p.weights_and_safety.weight_min_kg_m.toFixed(2)} - ${p.weights_and_safety.weight_max_kg_m.toFixed(2)}) kg/m` },
        { label: "Operating pressure / SMYS", exp: "İşletme Gerilmesi / SMYS Oranı", ext: p => `<span class="font-semibold text-blue-800">${p.weights_and_safety.operating_press_over_smys_percent}</span>` },
        { label: "841.1.2 Fracture Control and Arrest", exp: getExp('fracture_control'), ext: p => p.weights_and_safety.fracture_control_asme_841_1_2.includes("Annex G") ? `<span class="badge-pass font-bold">${p.weights_and_safety.fracture_control_asme_841_1_2}</span>` : `<span class="text-slate-600">${p.weights_and_safety.fracture_control_asme_841_1_2}</span>` },
        { label: "D/t Oranı & Tasarım Formülü", exp: getExp('thick_wall_alt'), ext: p => `<strong>D/t = ${p.weights_and_safety.d_over_t.toFixed(2)}</strong> (${p.weights_and_safety.design_formula_asme_841_1_1})` },
    ];
    weightRows.forEach(wr => {
        html += `<tr class="row-sec-weight border-b border-gray-300 searchable-row">
            <td class="label-cell sticky-left text-left px-3 py-1.5 font-semibold">${wr.label}</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            html += `<td onclick="selectPipe(${cIdx})" class="text-center text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${wr.ext(p)}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${wr.exp}</td></tr>`;
    });

    tableBody.innerHTML = html;
}

function toggleAccordion(secId) {
    const rows = document.querySelectorAll(`.row-${secId}`);
    const icon = document.getElementById(`icon-${secId}`);
    let isCollapsed = false;
    rows.forEach(r => {
        r.classList.toggle("hidden");
        if (r.classList.contains("hidden")) isCollapsed = true;
    });
    if (icon) {
        if (isCollapsed) icon.classList.add("collapsed");
        else icon.classList.remove("collapsed");
    }
}

function toggleAllAccordions(expand) {
    const sections = ["sec-chem", "sec-mech", "sec-dim", "sec-tests", "sec-weight"];
    sections.forEach(secId => {
        const rows = document.querySelectorAll(`.row-${secId}`);
        const icon = document.getElementById(`icon-${secId}`);
        rows.forEach(r => {
            if (expand) r.classList.remove("hidden");
            else r.classList.add("hidden");
        });
        if (icon) {
            if (expand) icon.classList.remove("collapsed");
            else icon.classList.add("collapsed");
        }
    });
}

function filterMatrixRows() {
    const query = (document.getElementById("matrix-search-input")?.value || "").toLowerCase().trim();
    const rows = document.querySelectorAll(".searchable-row");
    if (!query) {
        rows.forEach(r => r.style.display = "");
        return;
    }
    rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        if (text.includes(query)) {
            r.style.display = "";
            r.classList.remove("hidden");
        } else {
            r.style.display = "none";
        }
    });
}

function render3DPipeChips() {
    const container = document.getElementById("schematic-pipe-chips");
    if (!container) return;

    if (!calculatedPipes || calculatedPipes.length === 0) {
        container.innerHTML = `<span class="text-xs text-slate-400 italic">Görüntülenecek boru bulunmuyor.</span>`;
        return;
    }

    let html = "";
    calculatedPipes.forEach((p, idx) => {
        const isActive = idx === selectedPipeIndex;
        html += `
            <div onclick="selectPipe(${idx})" class="pipe-chip px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center space-x-2 ${isActive ? 'active' : 'bg-white border-slate-200 text-slate-700'}">
                <span class="w-5 h-5 rounded-full ${isActive ? 'bg-white text-blue-600' : 'bg-slate-800 text-white'} text-[10px] flex items-center justify-center font-bold">${idx + 1}</span>
                <div>
                    <div>${p.input_summary.diameter_inch} - ${p.input_summary.material_grade}</div>
                    <p class="text-[10px] ${isActive ? 'text-blue-100' : 'text-slate-500'}">t=${p.input_summary.wall_thickness_mm.toFixed(2)} mm | ${p.input_summary.design_factor_str}</p>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderPipesManagementList() {
    const list = document.getElementById("pipes-management-list");
    if (!list) return;

    if (!activeProject.pipes || activeProject.pipes.length === 0) {
        list.innerHTML = `<p class="text-xs text-slate-400 italic py-2 col-span-full">Listelenecek boru bulunmuyor.</p>`;
        return;
    }

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
    if (idx < 0 || idx >= calculatedPipes.length) return;
    selectedPipeIndex = idx;
    renderMatrixTable();
    renderPipesManagementList();
    render3DPipeChips();
    
    // Update navigator status
    const statusEl = document.getElementById("matrix-col-status");
    if (statusEl && calculatedPipes.length > 0) {
        statusEl.innerText = `Boru ${idx + 1} / ${calculatedPipes.length}`;
    }

    if (calculatedPipes[idx]) {
        renderKPICards(calculatedPipes[idx]);
        updateVisualizers(calculatedPipes[idx]);
    }
    loadTestPlan();
}

function selectNextPipe() {
    if (!calculatedPipes || calculatedPipes.length === 0) return;
    const next = (selectedPipeIndex + 1) % calculatedPipes.length;
    selectPipe(next);
}

function selectPrevPipe() {
    if (!calculatedPipes || calculatedPipes.length === 0) return;
    const prev = (selectedPipeIndex - 1 + calculatedPipes.length) % calculatedPipes.length;
    selectPipe(prev);
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
    activeProject.pipes.splice(idx, 1);
    if (selectedPipeIndex >= activeProject.pipes.length) selectedPipeIndex = Math.max(0, activeProject.pipes.length - 1);
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
    const autoPopulateSection = document.getElementById("botas-auto-populate-section");
    const manualFieldsSection = document.getElementById("manual-fields-section");
    const autoCheckbox = document.getElementById("chk-auto-populate-botas");

    if (isBotas) {
        if (autoPopulateSection) autoPopulateSection.classList.remove("hidden");
        const isAutoChecked = autoCheckbox ? autoCheckbox.checked : true;
        if (manualFieldsSection) {
            if (isAutoChecked) manualFieldsSection.classList.add("hidden");
            else manualFieldsSection.classList.remove("hidden");
        }
    } else {
        if (autoPopulateSection) autoPopulateSection.classList.add("hidden");
        if (manualFieldsSection) manualFieldsSection.classList.remove("hidden");
    }

    if (isBotas && (!autoCheckbox || !autoCheckbox.checked)) {
        const diaSelect = document.getElementById("new-pipe-dia");
        const factorSelect = document.getElementById("new-pipe-factor");
        const gradeSelect = document.getElementById("new-pipe-grade");
        const thkInput = document.getElementById("new-pipe-thk");
        const hintDiv = document.getElementById("botas-hint-msg");

        if (diaSelect && factorSelect) {
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
        }
    } else {
        const hintDiv = document.getElementById("botas-hint-msg");
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
    const autoCheckbox = document.getElementById("chk-auto-populate-botas");

    if (diaSelect) diaSelect.addEventListener("change", updateBotasDefaultsInModal);
    if (factorSelect) factorSelect.addEventListener("change", updateBotasDefaultsInModal);
    if (stdSelect) stdSelect.addEventListener("change", updateBotasDefaultsInModal);
    if (autoCheckbox) autoCheckbox.addEventListener("change", updateBotasDefaultsInModal);

    // 3D Snapshot Button
    const btnSnapshot = document.getElementById("btn-snapshot-3d");
    if (btnSnapshot) {
        btnSnapshot.addEventListener("click", () => {
            if (visualizer3DInstance) {
                visualizer3DInstance.exportSnapshotPNG();
                showToast("3D model görüntüsü PNG olarak indirildi!", "success");
            }
        });
    }

    // Export Excel Button
    const btnExcel = document.getElementById("btn-export-excel");
    if (btnExcel) {
        btnExcel.addEventListener("click", async () => {
            if (!activeProject.pipes || activeProject.pipes.length === 0) {
                showToast("Dışa aktarmak için en az bir boru bulunmalıdır!", "error");
                return;
            }
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
        setupWallThicknessDynamicUI();
        wtForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(wtForm);
            const stdCode = formData.get("standard_code") || "BOTAŞ";
            const matGrade = formData.get("material_grade") || "X65";
            const isStainless = matGrade.includes("SS") || matGrade.includes("Duplex");
            
            // Negative tolerance handling
            let applyTol = true;
            let manualTol = parseFloat(formData.get("manual_negative_tolerance_percent") || "12.5");
            
            if (stdCode.includes("B31.3")) {
                applyTol = true;
            } else if (stdCode.includes("B31.8") || stdCode.includes("B31.4")) {
                if (isStainless) {
                    const chk = document.getElementById("chk-apply-stainless-tol");
                    applyTol = chk ? chk.checked : false;
                } else {
                    applyTol = true; // API 5L Table 11
                }
            }

            const reqData = {
                standard_code: stdCode,
                diameter_inch: formData.get("diameter_inch"),
                material_grade: matGrade,
                manufacturing_process: formData.get("manufacturing_process") || "SAWH",
                psl_level: formData.get("psl_level") || "PSL2",
                apply_negative_tolerance: applyTol,
                manual_negative_tolerance_percent: manualTol,
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
            if (!selectedPipe) {
                showToast("Doğrulama için önce bir boru sütunu ekleyin!", "error");
                return;
            }
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
                lastVerification = res.verification;
                renderVerificationResult(res.verification);
            }
        });
    }

    // Keyboard Arrow Navigation for Pipe Columns
    document.addEventListener("keydown", (e) => {
        if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
        if (e.key === "ArrowRight") {
            selectNextPipe();
        } else if (e.key === "ArrowLeft") {
            selectPrevPipe();
        }
    });
}

function setupWallThicknessDynamicUI() {
    const stdSelect = document.querySelector("#wall-thickness-calc-form select[name='standard_code']");
    const gradeSelect = document.getElementById("wt-material-grade");
    const procSelect = document.getElementById("wt-manufacturing-process");
    const diaSelect = document.querySelector("#wall-thickness-calc-form select[name='diameter_inch']");
    const chkStainlessTol = document.getElementById("chk-apply-stainless-tol");
    
    if (!stdSelect) return;
    
    function updateVisibility() {
        const std = stdSelect.value;
        const grade = gradeSelect ? gradeSelect.value : "X65";
        const isStainless = grade.includes("SS") || grade.includes("Duplex");
        const procContainer = document.getElementById("wt-process-container");
        const pslTolRow = document.getElementById("wt-psl-tol-row");
        const pslBox = document.getElementById("wt-psl-box");
        const manualTolBox = document.getElementById("wt-manual-tol-box");
        const tolApi5lText = document.getElementById("wt-tol-api5l-text");
        const tolStainlessOpt = document.getElementById("wt-tol-stainless-opt");
        const tolB313Info = document.getElementById("wt-tol-b313-info");
        const tolDescSpan = document.getElementById("wt-tol-desc-span");
        
        if (std.includes("B31.3")) {
            // ASME B31.3
            if (procContainer) procContainer.classList.add("hidden");
            if (pslTolRow) pslTolRow.classList.remove("hidden");
            if (pslBox) pslBox.classList.add("hidden");
            if (manualTolBox) manualTolBox.classList.remove("hidden");
            if (tolApi5lText) tolApi5lText.classList.add("hidden");
            if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
            if (tolB313Info) tolB313Info.classList.remove("hidden");
        } else if (std.includes("B31.8") || std.includes("B31.4")) {
            // ASME B31.8 / ASME B31.4
            if (isStainless) {
                if (procContainer) procContainer.classList.add("hidden");
                if (pslTolRow) pslTolRow.classList.remove("hidden");
                if (pslBox) pslBox.classList.add("hidden");
                if (manualTolBox) manualTolBox.classList.remove("hidden");
                if (tolApi5lText) tolApi5lText.classList.add("hidden");
                if (tolStainlessOpt) tolStainlessOpt.classList.remove("hidden");
                if (tolB313Info) tolB313Info.classList.add("hidden");
            } else {
                // API 5L Carbon Steel
                if (procContainer) procContainer.classList.remove("hidden");
                if (pslTolRow) pslTolRow.classList.remove("hidden");
                if (pslBox) pslBox.classList.remove("hidden");
                if (manualTolBox) manualTolBox.classList.add("hidden");
                if (tolApi5lText) tolApi5lText.classList.remove("hidden");
                if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
                if (tolB313Info) tolB313Info.classList.add("hidden");
                
                // Calculate live API 5L Tablo 11 description
                const proc = procSelect ? procSelect.value : "SAWH";
                const diaText = diaSelect ? diaSelect.value : "24\"";
                const isLargeDia = !diaText.includes("1/") && !diaText.includes("3/") && parseFloat(diaText) > 20;
                
                if (proc.includes("SMLS")) {
                    if (tolDescSpan) tolDescSpan.innerText = "Dikişsiz (SMLS) borular için API 5L Tablo 11 gereği -%12.5 imalat toleransı uygulanır.";
                } else if (proc.includes("ERW") || proc.includes("HFW")) {
                    if (tolDescSpan) tolDescSpan.innerText = "Boyuna kaynaklı (ERW/HFW) borular için API 5L Tablo 11 gereği -%10.0 imalat toleransı uygulanır.";
                } else {
                    if (isLargeDia) {
                        if (tolDescSpan) tolDescSpan.innerText = `Tozaltı kaynaklı (SAWH/SAWL) D > 20" borular için API 5L Tablo 11 gereği -%8.0 imalat toleransı uygulanır.`;
                    } else {
                        if (tolDescSpan) tolDescSpan.innerText = `Tozaltı kaynaklı (SAWH/SAWL) D ≤ 20" borular için API 5L Tablo 11 gereği -%10.0 imalat toleransı uygulanır.`;
                    }
                }
            }
        } else {
            // BOTAŞ
            if (procContainer) procContainer.classList.remove("hidden");
            if (pslTolRow) pslTolRow.classList.add("hidden");
            if (tolApi5lText) tolApi5lText.classList.remove("hidden");
            if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
            if (tolB313Info) tolB313Info.classList.add("hidden");
            if (tolDescSpan) tolDescSpan.innerText = "BOTAŞ Şartnamesi: Hat borularında şartname tablosu, istasyon borularında %12.5 emniyet payı uygulanır.";
        }
    }
    
    stdSelect.addEventListener("change", updateVisibility);
    if (gradeSelect) gradeSelect.addEventListener("change", updateVisibility);
    if (procSelect) procSelect.addEventListener("change", updateVisibility);
    if (diaSelect) diaSelect.addEventListener("change", updateVisibility);
    if (chkStainlessTol) chkStainlessTol.addEventListener("change", updateVisibility);
    
    updateVisibility();
}

function renderWallThicknessResult(data) {
    const resDiv = document.getElementById("wt-results-panel");
    if (!resDiv) return;

    resDiv.classList.remove("hidden");
    const r = data.calculation_results;
    const inp = data.input_parameters;

    const tolPct = r.tolerance_percent_used || 0;
    const tolLabel = tolPct > 0 ? `Negatif Tolerans Sınırı (-%${tolPct.toFixed(1)}):` : `Nominal Sınır:`;

    resDiv.innerHTML = `
        <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg shadow-sm">
            <div class="flex items-center justify-between pb-2 mb-3 border-b border-blue-200">
                <h4 class="text-md font-bold text-blue-950 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    ${r.formula_name || 'Standart Et Kalınlığı Hesabı'}
                </h4>
                <span class="bg-indigo-100 text-indigo-800 text-xs font-bold px-2.5 py-0.5 rounded">
                    ${r.schedule_standard_used}
                </span>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">Teorik Et Kalınlığı (t):</span>
                    <span class="font-bold text-gray-900 text-lg">${Number(r.t_theoretical_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">Gereken Et Kalınlığı (t_req):</span>
                    <span class="font-bold text-indigo-700 text-lg">${Number(r.t_required_asme_b31_8_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-blue-300 bg-blue-50/50">
                    <span class="text-xs text-blue-800 font-semibold block">Seçilen Nominal (${inp.is_stainless ? 'ASME B36.19M' : 'ASME B36.10M'}):</span>
                    <span class="font-bold text-blue-900 text-lg">${Number(r.selected_nominal_thickness_asme_b36_10_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-xs text-gray-500 block">${tolLabel}</span>
                    <span class="font-bold text-gray-900 text-lg">${Number(r.negative_tolerance_min_mm).toFixed(2)} mm</span>
                </div>
            </div>

            <div class="mt-3 p-2 bg-white/80 rounded border border-blue-100 text-xs text-slate-700 flex flex-wrap items-center justify-between gap-1">
                <span><strong>Tolerans Kuralı:</strong> ${r.tolerance_rule_description || 'Standart Tolerans Kuralı'}</span>
                <span class="font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">${inp.manufacturing_process || 'SAWH'} | ${inp.psl_level || 'PSL2'}</span>
            </div>

            <div class="mt-2 flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-blue-100 text-xs">
                <span class="text-gray-600">
                    ${!inp.is_stainless && r.botas_standard_thickness_mm > 0 ? `BOTAŞ Standart Tavsiyesi: <strong>${Number(r.botas_standard_thickness_mm).toFixed(2)} mm</strong>` : `Tasarım Kriteri: <strong>${r.design_factor_used}</strong>`}
                </span>
                <span class="${r.is_nominal_sufficient ? 'badge-pass' : 'badge-fail'}">
                    ${r.is_nominal_sufficient ? '✓ Seçilen Schedule Et Kalınlığı Güvenli ve Uygun' : '⚠ Et Kalınlığı Yetersiz!'}
                </span>
            </div>
        </div>
    `;
}

function renderVerificationResult(data) {
    const resDiv = document.getElementById("verification-results-panel");
    const placeholder = document.getElementById("verification-placeholder");
    if (!resDiv) return;

    if (placeholder) placeholder.classList.add("hidden");
    resDiv.classList.remove("hidden");

    let html = `
        <div class="p-4 ${data.overall_status === 'ACCEPTED' ? 'bg-emerald-50 border-emerald-300' : 'bg-red-50 border-red-300'} border rounded-lg shadow-sm">
            <div class="flex items-center justify-between mb-3">
                <h4 class="text-base font-bold ${data.overall_status === 'ACCEPTED' ? 'text-emerald-900' : 'text-red-900'}">
                    Genel Fabrika Kabul Kararı: ${data.overall_badge}
                </h4>
                <span class="text-xs font-semibold px-2.5 py-1 rounded ${data.overall_status === 'ACCEPTED' ? 'bg-emerald-200 text-emerald-900' : 'bg-red-200 text-red-900'}">
                    ${data.passed_count} / ${data.checks_count} Parametre Uygun
                </span>
            </div>
            <div class="flex items-center gap-2 mb-3">
                <button onclick="generateOfficialReport()" class="bg-slate-800 hover:bg-slate-700 text-white font-bold px-3 py-1.5 rounded text-xs transition flex items-center">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                    Resmi Rapor / PDF
                </button>
            </div>
            <div class="overflow-x-auto max-h-[500px] overflow-y-auto">
                <table class="w-full text-xs text-left border-collapse bg-white rounded border border-gray-300">
                    <thead class="bg-gray-100 text-gray-700 font-bold border-b border-gray-300 sticky top-0">
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

async function generateOfficialReport() {
    if (!activeProject.pipes || activeProject.pipes.length === 0) {
        showToast("Rapor için en az bir boru bulunmalıdır!", "error");
        return;
    }
    try {
        const resp = await fetch("/api/report-view", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                project_info: activeProject.project_info,
                pipes: activeProject.pipes,
                lang: currentLang,
                verification: lastVerification
            })
        });
        const html = await resp.text();
        const w = window.open("", "_blank");
        if (w) {
            w.document.write(html);
            w.document.close();
        } else {
            showToast("Açılır pencere engellendi. Lütfen izin verin.", "error");
        }
    } catch (e) {
        console.error("Report generation error:", e);
        showToast("Rapor oluşturulurken hata oluştu!", "error");
    }
}

function saveProjectMetadata() {
    const map = {
        "meta-project-name": "project_name",
        "meta-project-no": "project_no",
        "meta-line-name": "line_name",
        "meta-client": "client",
        "meta-prepared": "prepared_by",
        "meta-checked": "checked_by",
        "meta-revision": "revision",
        "meta-date": "revision_date",
        "meta-heat-number": "heat_number",
        "meta-cert-number": "certificate_number",
        "meta-quantity": "quantity",
        "meta-order-number": "purchase_order_number",
        "meta-inspection-company": "inspection_company"
    };
    for (const [id, key] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) activeProject.project_info[key] = el.value;
    }
    ProjectStorage.saveToLocalStorage(activeProject);
    showToast("Proje ve revizyon bilgileri kaydedildi!", "success");
}

async function loadTestPlan() {
    const panel = document.getElementById("test-plan-panel");
    if (!panel) return;
    const pipe = (activeProject.pipes && activeProject.pipes.length > 0)
        ? (activeProject.pipes[selectedPipeIndex] || activeProject.pipes[0])
        : null;
    if (!pipe) {
        panel.innerHTML = `<p class="text-xs text-slate-400 italic">Test planı için önce bir boru ekleyin.</p>`;
        return;
    }
    try {
        const resp = await fetch("/api/test-plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pipe_config: pipe })
        });
        const res = await resp.json();
        if (res.status !== "success") return;
        let html = `<p class="text-[11px] text-slate-500 mb-2">Seçili boru: <strong>${pipe.diameter_inch} - ${pipe.material_grade} (${pipe.manufacturing_process})</strong> — API 5L 46th Ed.</p>`;
        html += `<div class="overflow-x-auto"><table class="w-full text-xs text-left border-collapse bg-white rounded border border-gray-300">`;
        html += `<thead class="bg-gray-100 text-gray-700 font-bold border-b border-gray-300"><tr>
            <th class="p-2">Test</th><th class="p-2">Madde</th><th class="p-2">Sıklık / Adet</th><th class="p-2">Alınma Yeri</th><th class="p-2">Numune Boyutu</th></tr></thead><tbody>`;
        res.test_plan.forEach(tp => {
            html += `<tr class="border-b border-gray-200">
                <td class="p-2 font-bold">${tp.test}</td>
                <td class="p-2 text-slate-600">${tp.clause}</td>
                <td class="p-2">${tp.frequency}</td>
                <td class="p-2">${tp.location}</td>
                <td class="p-2">${tp.specimen}</td></tr>`;
        });
        html += `</tbody></table></div>`;
        panel.innerHTML = html;
    } catch (e) {
        console.error("Test plan load error:", e);
    }
}

// --- FEEDBACK & DEVELOPER CONTACT MODULE ---
const DEVELOPER_EMAIL = "omer.erbas@botas.gov.tr";

function openFeedbackModal(type = "bug") {
    const modal = document.getElementById("feedback-modal");
    if (!modal) return;
    
    const typeSelect = document.getElementById("feedback-type");
    if (typeSelect && type) {
        typeSelect.value = type;
    }
    
    const subjInput = document.getElementById("feedback-subject");
    if (subjInput && !subjInput.value) {
        const activePipe = (activeProject && activeProject.pipes) ? (activeProject.pipes[selectedPipeIndex] || activeProject.pipes[0]) : null;
        if (type === "bug") {
            subjInput.value = activePipe ? `[Hata Bildirimi] ${activePipe.diameter_inch} ${activePipe.material_grade} Boru Hesabı` : "[Hata Bildirimi] Boru Kalite Güvence";
        } else if (type === "feature") {
            subjInput.value = "[Öneri] Yeni Boru Standardı / Özellik Talebi";
        } else {
            subjInput.value = "[Danışma] API 5L / BOTAŞ Boru Kalite Danışma";
        }
    }
    
    modal.classList.remove("hidden");
}

function closeFeedbackModal() {
    const modal = document.getElementById("feedback-modal");
    if (modal) modal.classList.add("hidden");
}

function generateFeedbackDiagnostics() {
    const activePipe = (activeProject && activeProject.pipes) ? (activeProject.pipes[selectedPipeIndex] || activeProject.pipes[0]) : null;
    let diag = `\n=== SİSTEM VE TANI BİLGİLERİ ===\n`;
    diag += `Uygulama Sürümü: v${window.APP_VERSION || '1.5.0'}\n`;
    diag += `Kullanıcı Tarayıcısı / OS: ${navigator.userAgent}\n`;
    diag += `Tarih / Saat: ${new Date().toISOString()}\n`;
    diag += `Mevcut Dil: ${currentLang}\n`;
    diag += `Aktif Proje: ${(activeProject && activeProject.project_name) || "API 5L Projesi"}\n`;
    diag += `Toplam Boru Sayısı: ${(activeProject && activeProject.pipes) ? activeProject.pipes.length : 0}\n`;
    
    if (activePipe) {
        diag += `\n--- AKTİF SEÇİLİ BORU PARAMETRELERİ ---\n`;
        diag += `Çap: ${activePipe.diameter_inch} (${activePipe.diameter_mm} mm)\n`;
        diag += `Et Kalınlığı: ${activePipe.wall_thickness_mm} mm\n`;
        diag += `Malzeme Kalitesi: ${activePipe.material_grade}\n`;
        diag += `Tasarım Faktörü: ${activePipe.design_factor_str}\n`;
        diag += `Standart / Şartname: ${activePipe.standard_type}\n`;
        diag += `İmalat Yöntemi: ${activePipe.manufacturing_process}\n`;
        diag += `Dizayn Basıncı: ${activePipe.design_pressure_bar} bar\n`;
    }
    diag += `================================\n`;
    return diag;
}

function handleSendFeedback(e) {
    e.preventDefault();
    const type = document.getElementById("feedback-type")?.value || "bug";
    const name = document.getElementById("feedback-name")?.value?.trim() || "Anonim Kullanıcı";
    const userEmail = document.getElementById("feedback-email")?.value?.trim() || "";
    const subject = document.getElementById("feedback-subject")?.value?.trim() || "API 5L Suite Bildirimi";
    const message = document.getElementById("feedback-message")?.value?.trim() || "";
    const includeDiag = document.getElementById("chk-include-diagnostics")?.checked;
    
    let body = `Kimden: ${name}${userEmail ? ` <${userEmail}>` : ""}\n`;
    body += `Bildirim Türü: ${type.toUpperCase()}\n\n`;
    body += `Mesaj / Açıklama:\n${message}\n\n`;
    
    if (includeDiag) {
        body += generateFeedbackDiagnostics();
    }
    
    const mailtoUrl = `mailto:${DEVELOPER_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoUrl;
    
    showToast("E-posta istemciniz açılıyor...", "success");
    closeFeedbackModal();
}

async function copyFeedbackReport() {
    const type = document.getElementById("feedback-type")?.value || "bug";
    const name = document.getElementById("feedback-name")?.value?.trim() || "Anonim Kullanıcı";
    const userEmail = document.getElementById("feedback-email")?.value?.trim() || "";
    const subject = document.getElementById("feedback-subject")?.value?.trim() || "API 5L Suite Bildirimi";
    const message = document.getElementById("feedback-message")?.value?.trim() || "";
    const includeDiag = document.getElementById("chk-include-diagnostics")?.checked;
    
    let fullReport = `=== API 5L & BOTAŞ BORU SUITE - GERİ BİLDİRİM RAPORU ===\n`;
    fullReport += `Hedef: ${DEVELOPER_EMAIL}\n`;
    fullReport += `Gönderen: ${name} ${userEmail ? `(${userEmail})` : ""}\n`;
    fullReport += `Tür: ${type.toUpperCase()}\n`;
    fullReport += `Konu: ${subject}\n\n`;
    fullReport += `AÇIKLAMA:\n${message || "(Açıklama girilmedi)"}\n\n`;
    
    if (includeDiag) {
        fullReport += generateFeedbackDiagnostics();
    }
    
    try {
        await navigator.clipboard.writeText(fullReport);
        showToast("Tanı raporu panoya kopyalandı!", "success");
    } catch (err) {
        console.error("Clipboard copy failed:", err);
        showToast("Panoya kopyalanamadı.", "error");
    }
}
