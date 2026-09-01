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

// HTML-escape helper to prevent XSS via user-supplied strings injected into innerHTML.
function esc(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// Number/string/null-safe formatting for matrix cells ("—" for missing, keeps strings verbatim).
function fmtNum(v, dec) {
    if (v === null || v === undefined || v === "") return "—";
    if (typeof v === "number") return v.toFixed(dec === undefined ? 2 : dec);
    return String(v);
}

// Edition-comparison (46th vs 47th) info button for a matrix row.
function noteBtn(key) {
    return `<button type="button" onclick="openEditionNote('${key}')" title="46. vs 47. baskı karşılaştırması"
        class="inline-flex items-center justify-center w-4 h-4 ml-1 rounded-full bg-indigo-100 text-indigo-700 text-[10px] font-bold hover:bg-indigo-200 align-middle">ⓘ</button>`;
}

// Renders the 46th/47th edition comparison note for a row into the ITP info modal.
function openEditionNote(key) {
    const pipe = calculatedPipes[selectedPipeIndex] || (calculatedPipes[0] || null);
    if (!pipe || !pipe.edition_notes || !pipe.edition_notes[key]) {
        showToast("Bu satır için baskı karşılaştırma notu tanımlı değil.", "info");
        return;
    }
    const n = pipe.edition_notes[key];
    const changedBadge = n.changed_46_47
        ? '<span class="inline-block bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded">47. BASKIDA DEĞİŞTİ</span>'
        : '<span class="inline-block bg-emerald-100 text-emerald-700 text-[10px] font-bold px-2 py-0.5 rounded">46. = 47. BASKI</span>';
    const programNote = n.program_note
        ? `<div class="p-3 bg-amber-50 border border-amber-200 rounded-lg text-[11px] text-amber-900"><b>Program notu:</b> ${esc(n.program_note)}</div>`
        : "";
    document.getElementById("itp-info-title").innerText = `Baskı Karşılaştırması — ${n.title}`;
    document.getElementById("itp-info-body").innerHTML = `
        <div class="flex items-center space-x-2">${changedBadge}<span class="text-[11px] text-slate-500">${esc(n.source)}</span></div>
        <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div class="font-bold text-xs text-slate-700 mb-1">📘 46. Baskı (orijinal)</div>
            <div class="text-[11px] text-slate-700">${esc(n.edition_46)}</div>
        </div>
        <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="font-bold text-xs text-blue-900 mb-1">📗 47. Baskı (güncel — hesaplamada kullanılır)</div>
            <div class="text-[11px] text-blue-900">${esc(n.edition_47)}</div>
        </div>
        ${programNote}`;
    document.getElementById("itp-info-modal").classList.remove("hidden");
}

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
    loadSavedITPAuditFromStorage();

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
            renderITPPipeChips();
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
            renderITPPipeChips();
            if (typeof updateITPTargetPipes === "function") updateITPTargetPipes();
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
    document.getElementById("kpi-hydro-val").innerText = `${p.hydrostatic_test.hydro_test_max_bar.toFixed(2)} Bar`;
    document.getElementById("kpi-hydro-sub").innerText = `Min: ${p.hydrostatic_test.hydro_test_min_bar.toFixed(2)} | Std: ${p.hydrostatic_test.api_5l_std_test_bar.toFixed(2)} Bar`;
    
    document.getElementById("kpi-weight-val").innerText = `${p.weights_and_safety.weight_nominal_kg_m.toFixed(2)} kg/m`;
    document.getElementById("kpi-weight-sub").innerText = `Tolerans: [${p.weights_and_safety.weight_min_kg_m.toFixed(2)} - ${p.weights_and_safety.weight_max_kg_m.toFixed(2)}] kg/m`;
    
    document.getElementById("kpi-dt-val").innerText = `D/t = ${p.weights_and_safety.d_over_t.toFixed(2)}`;
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
        { label: "ÇAP (inch)", exp: getExp('diameter'), extractor: p => `<strong>${esc(p.input_summary.diameter_inch)}</strong>` },
        { label: "ÇAP (mm)", exp: "Boru Gerçek Dış Çapı (OD mm)", extractor: (p, idx) => `<span class="font-semibold">${p.input_summary.diameter_mm}</span>` },
        { label: "Design Basıncı / Faktör", exp: getExp('design_factor'), extractor: p => `<span class="font-medium text-blue-900">${esc(p.input_summary.design_factor_str)}</span>` },
        { label: "Et Kalınlığı (mm)", exp: getExp('wall_thickness'), extractor: (p, idx) => `<span class="font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">${p.input_summary.wall_thickness_mm.toFixed(2)}</span>` },
        { label: "Üretim Yöntemi", exp: getExp('process'), extractor: p => `<span class="font-semibold text-amber-900">${esc(p.input_summary.manufacturing_process)}</span>` },
        { label: "Malzeme Kalitesi", exp: getExp('grade'), extractor: p => `<strong>${esc(p.input_summary.material_grade)}</strong>` },
        { label: "PSL / Teslim Koşulu", exp: "API 5L Ürün Spesifikasyon Seviyesi ve Teslim Koşulu (R/N/Q/M)", extractor: p => {
            if (p.input_summary.standard_type && String(p.input_summary.standard_type).toUpperCase().includes("API")) {
                const psl = p.input_summary.psl_level || "PSL2";
                const dlv = p.input_summary.delivery_condition && p.input_summary.delivery_condition !== "—" ? p.input_summary.delivery_condition : "";
                return `<span class="font-bold text-purple-800">${esc(psl)}${dlv ? " / " + esc(dlv) : ""}</span>`;
            }
            return `<span class="text-slate-400">BOTAŞ</span>`;
        } },
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
    const chemTitle = (calculatedPipes[0]?.input_summary.psl_level || "PSL2") === "PSL1"
        ? "🧪 KİMYASAL BİLEŞİM ANALİZİ (PSL1 LİMİTLERİ — Tablo 4)"
        : "🧪 KİMYASAL BİLEŞİM ANALİZİ (PSL2 LİMİTLERİ — Tablo 5)";
    html += renderAccordionSectionHeader("sec-chem", chemTitle, "9");
    const chemRows = [
        { elem: "C", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.C_max, 2) },
        { elem: "Mn", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.Mn_max, 2) },
        { elem: "P", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.P_max, 3) },
        { elem: "S", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.S_max, 3) },
        { elem: "Nb", limitType: "Min%-Max%", ext: p => p.chemical_analysis.Nb_min_max === null || p.chemical_analysis.Nb_min_max === undefined ? "—" : esc(p.chemical_analysis.Nb_min_max) },
        { elem: "V", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.V_max, 2) },
        { elem: "Ti", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.Ti_max, 2) },
        { elem: "N", limitType: "Max %", ext: p => fmtNum(p.chemical_analysis.N_max, 3) },
        { elem: "CE", limitType: "IIW / Pcm", ext: p => `IIW: ${fmtNum(p.chemical_analysis.CE_IIW_max, 2)} | Pcm: ${fmtNum(p.chemical_analysis.CE_Pcm_max, 2)}` },
    ];

    chemRows.forEach((cr) => {
        const isAsAgreed = calculatedPieces => calculatedPieces.chemical_analysis.as_agreed === true;
        html += `<tr class="row-sec-chem border-b border-gray-300 searchable-row">`;
        html += `<td class="th-side sticky-left text-left font-bold px-3 py-1.5 text-xs">${cr.elem} (${cr.limitType})${cr.elem === "CE" ? noteBtn("chem_m_grade") : ""}</td>`;
        calculatedPipes.forEach((p, cIdx) => {
            const activeColClass = isColActive(cIdx) ? 'active-pipe-col font-bold' : '';
            const cell = isAsAgreed(p) ? '<span class="text-amber-600 italic">Anlaşmaya bağlı</span>' : cr.ext(p);
            html += `<td onclick="selectPipe(${cIdx})" class="text-center font-mono text-xs px-2 py-1.5 cursor-pointer ${activeColClass}">${cell}</td>`;
        });
        html += `<td class="sticky-right bg-slate-50 text-slate-600 text-[11px] px-3 py-1 italic text-left border-l-2 border-slate-300">${getExp('chemical')}</td></tr>`;
    });
    if (calculatedPipes.some(p => p.chemical_analysis.as_agreed === true)) {
        html += `<tr class="row-sec-chem border-b border-gray-200">
            <td class="th-side sticky-left text-left font-bold px-3 py-1.5 text-xs text-amber-700" colspan="${calculatedPipes.length + 2}">
                ⚠️ t > 25.0 mm: kimyasal bileşim anlaşmaya bağlıdır (API 5L 9.2.3).
            </td></tr>`;
    }

    // SECTION 3: MECHANICAL & HYDROSTATIC PRESSURE
    html += renderAccordionSectionHeader("sec-mech", "💥 MEKANİK MUKAVEMET & HİDROSTATİK FABRİKA BASINCI", "8");
    const mechRows = [
        { label: "Yield Min. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_min_psi.toFixed(0)} psi / ${p.mechanical_properties.yield_min_mpa.toFixed(2)} MPa` },
        { label: "Yield Max. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.yield_max_psi.toFixed(0)} psi / ${p.mechanical_properties.yield_max_mpa.toFixed(2)} MPa` },
        { label: "Tensile Min. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_min_psi.toFixed(0)} psi / ${p.mechanical_properties.tensile_min_mpa.toFixed(2)} MPa` },
        { label: "Tensile Max. (Psi / MPa)", exp: getExp('yield_tensile'), ext: p => `${p.mechanical_properties.tensile_max_psi.toFixed(0)} psi / ${p.mechanical_properties.tensile_max_mpa.toFixed(2)} MPa` },
        { label: `Akma / Çekme Oranı Max. (Y/T)${noteBtn("yt_ratio")}`, exp: getExp('yt_ratio'), ext: p => p.mechanical_properties.yield_to_tensile_ratio_max > 0 ? p.mechanical_properties.yield_to_tensile_ratio_max.toFixed(2) : "<span class='text-slate-400'>— (PSL1)</span>" },
        { label: `Hydro Test Basıncı Max. (Bar)${noteBtn("hydro_factor")}`, exp: getExp('hydro_test'), ext: p => `<span class="font-bold text-blue-700">${p.hydrostatic_test.hydro_test_max_bar.toFixed(2)} Bar</span>` },
        { label: `Hydro Test Basıncı Min. (Bar)${noteBtn("hydro_factor")}`, exp: "Fabrika Test Alt Sınırı (API: Standart Test Basıncı / BOTAŞ: P_max - 2.0 Bar)", ext: p => `${p.hydrostatic_test.hydro_test_min_bar.toFixed(2)} Bar` },
        { label: `API 5L Standart Test Pressure (Bar)${noteBtn("hydro_factor")}`, exp: getExp('api_std_test'), ext: p => `${p.hydrostatic_test.api_5l_std_test_bar.toFixed(2)} Bar` },
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
        { label: `Et Kalınlığı: Min. (mm)${noteBtn("smls_wall_tol")}`, exp: getExp('wall_thickness_tol'), ext: p => `<span class="font-bold text-red-700">${p.wall_thickness_tolerance.min_mm.toFixed(2)} mm</span>` },
        { label: `Et Kalınlığı: Max. (mm)${noteBtn("smls_wall_tol")}`, exp: getExp('wall_thickness_tol'), ext: p => `<span class="font-bold text-emerald-700">${p.wall_thickness_tolerance.max_mm.toFixed(2)} mm</span>` },
        { label: `Boru Çap Toleransı - Boru Ucu Max/Min${noteBtn("diameter_tol")}`, exp: getExp('diameter_tol'), ext: p => `[${fmtNum(p.dimensional_tolerances.diameter_end_min_mm, 2)} - ${fmtNum(p.dimensional_tolerances.diameter_end_max_mm, 2)}] mm` },
        { label: `Boru Çap Toleransı - Gövde Max/Min${noteBtn("diameter_tol")}`, exp: getExp('diameter_tol'), ext: p => `[${fmtNum(p.dimensional_tolerances.diameter_body_min_mm, 2)} - ${fmtNum(p.dimensional_tolerances.diameter_body_max_mm, 2)}] mm` },
        { label: "Boru Çevre Toleransı - Boru Ucu (mm)", exp: getExp('circumference_tol'), ext: p => `[${typeof p.dimensional_tolerances.circ_end_min_mm === 'number' ? p.dimensional_tolerances.circ_end_min_mm.toFixed(2) : p.dimensional_tolerances.circ_end_min_mm} - ${typeof p.dimensional_tolerances.circ_end_max_mm === 'number' ? p.dimensional_tolerances.circ_end_max_mm.toFixed(2) : p.dimensional_tolerances.circ_end_max_mm}] mm` },
        { label: "Boru Çevre Toleransı - Gövde (mm)", exp: getExp('circumference_tol'), ext: p => `[${typeof p.dimensional_tolerances.circ_body_min_mm === 'number' ? p.dimensional_tolerances.circ_body_min_mm.toFixed(2) : p.dimensional_tolerances.circ_body_min_mm} - ${typeof p.dimensional_tolerances.circ_body_max_mm === 'number' ? p.dimensional_tolerances.circ_body_max_mm.toFixed(2) : p.dimensional_tolerances.circ_body_max_mm}] mm` },
        { label: "Ovalite - Boru Ucu / Gövde (mm)", exp: getExp('ovality'), ext: p => `Uç: ${p.dimensional_tolerances.ovality_end_mm} mm | Gövde: ${p.dimensional_tolerances.ovality_body_mm} mm` },
        { label: "Radial Offset Max. (mm)", exp: getExp('radial_offset'), ext: p => `${p.weld_and_geometry.radial_offset_max_mm} mm` },
        { label: "Kaynak Yüksekliği - İç / Dış (mm)", exp: getExp('weld_height'), ext: p => `İç: ${p.weld_and_geometry.weld_height_inside_mm} mm | Dış: ${p.weld_and_geometry.weld_height_outside_mm} mm` },
        { label: "Misalignment (mm)", exp: getExp('misalignment'), ext: p => `${p.weld_and_geometry.misalignment_max_mm} mm` },
        { label: `Boru Ucu Kaynak Çatılaşma / Diklik${noteBtn("peaking")}`, exp: `${getExp('peaking')} / ${getExp('squareness')}`, ext: p => `Çatı: ${fmtNum(p.dimensional_tolerances.pipe_end_peaking_max_mm, 2)} mm | Diklik: ${fmtNum(p.dimensional_tolerances.pipe_end_squareness_max_mm, 2)} mm` },
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
        { label: `Minimum Uzama - Malzeme (%)${noteBtn("elongation")}`, exp: getExp('elongation'), ext: p => p.toughness_and_tests.tensile_dual_option
            ? `Şerit: <span class="font-bold text-teal-800">${p.toughness_and_tests.elongation_strip_percent.toFixed(2)}%</span> | Yuvarlak: <span class="font-bold text-teal-800">${p.toughness_and_tests.elongation_round_percent.toFixed(2)}%</span>`
            : `<span class="font-bold text-teal-800">${p.toughness_and_tests.elongation_mat_min_percent.toFixed(2)}%</span>` },
        { label: "Minimum Uzama - Kaynak (%)", exp: "Kaynak Dikişi Min. %10 Uzama", ext: p => `${typeof p.toughness_and_tests.elongation_weld_min_percent === 'number' ? p.toughness_and_tests.elongation_weld_min_percent.toFixed(2) : p.toughness_and_tests.elongation_weld_min_percent}%` },
        { label: `Çentik Darbe (J) - Malzeme / Kaynak${noteBtn("cvn_body")}`, exp: getExp('cvn'), ext: p => `Gövde: ${p.toughness_and_tests.notch_impact_mat_j} J | Kaynak: ${p.toughness_and_tests.notch_impact_weld_j} J` },
        { label: "Artık Gerilme Testi Max (mm)", exp: getExp('residual_stress'), ext: p => `${typeof p.toughness_and_tests.residual_stress_max_mm === 'number' ? p.toughness_and_tests.residual_stress_max_mm.toFixed(2) + ' mm' : p.toughness_and_tests.residual_stress_max_mm}` },
        { label: `Yırtılma Testi (DWTT)${noteBtn("dwtt")}`, exp: getExp('dwtt'), ext: p => p.toughness_and_tests.dwtt_test === "Var" ? `<span class="badge-pass font-bold">Var (D ≥ 508mm)</span>` : `<span class="text-slate-400">${esc(p.toughness_and_tests.dwtt_test)}</span>` },
        { label: "Sertlik TESTİ", exp: getExp('hardness'), ext: p => p.toughness_and_tests.hardness_test_max },
        { label: "Mandrel Çapı / Çene Açıklığı (mm)", exp: getExp('mandrel_jaw'), ext: p => `${typeof p.toughness_and_tests.mandrel_dia_max_mm === 'number' ? p.toughness_and_tests.mandrel_dia_max_mm.toFixed(2) : p.toughness_and_tests.mandrel_dia_max_mm} / ${typeof p.toughness_and_tests.jaw_opening_max_mm === 'number' ? p.toughness_and_tests.jaw_opening_max_mm.toFixed(2) : p.toughness_and_tests.jaw_opening_max_mm} mm` },
        { label: `FLATTENING - Kaynak / Çatlak Açılma${noteBtn("flattening")}`, exp: getExp('flattening'), ext: p => `Kaynak: ${p.flattening.weld_opening_height_mm} mm | Çatlak: ${p.flattening.material_crack_height_mm} mm` },
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
                    <div>${esc(p.input_summary.diameter_inch)} - ${esc(p.input_summary.material_grade)}</div>
                    <p class="text-[10px] ${isActive ? 'text-blue-100' : 'text-slate-500'}">t=${p.input_summary.wall_thickness_mm.toFixed(2)} mm | ${esc(p.input_summary.design_factor_str)}</p>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// ITP pipe selector chips (same pattern as the 3D/2D selector; syncs global selectedPipeIndex)
function renderITPPipeChips() {
    const container = document.getElementById("itp-pipe-chips");
    if (!container) return;

    if (!calculatedPipes || calculatedPipes.length === 0) {
        container.innerHTML = `<span class="text-xs text-slate-400 italic">Test planı için önce bir boru ekleyin.</span>`;
        return;
    }

    let html = "";
    calculatedPipes.forEach((p, idx) => {
        const isActive = idx === selectedPipeIndex;
        html += `
            <div onclick="selectPipe(${idx})" class="pipe-chip px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center space-x-2 ${isActive ? 'active' : 'bg-white border-slate-200 text-slate-700'}">
                <span class="w-5 h-5 rounded-full ${isActive ? 'bg-white text-blue-600' : 'bg-slate-800 text-white'} text-[10px] flex items-center justify-center font-bold">${idx + 1}</span>
                <div>
                    <div>${esc(p.input_summary.diameter_inch)} - ${esc(p.input_summary.material_grade)}</div>
                    <p class="text-[10px] ${isActive ? 'text-blue-100' : 'text-slate-500'}">t=${p.input_summary.wall_thickness_mm.toFixed(2)} mm | ${esc(p.input_summary.design_factor_str)}</p>
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
                    <h4 class="text-sm font-bold text-gray-800">${esc(p.diameter_inch)} - ${esc(p.material_grade)} (${esc(p.manufacturing_process)})</h4>
                    <p class="text-xs text-gray-500">t = ${p.wall_thickness_mm} mm | F = ${esc(p.design_factor_str)}</p>
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
    renderITPPipeChips();
    
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
    renderSawhCard(pipeData);
}

// ============================================================================
// SAWH Spiral Strip Width, Helix Angle & Submerged Arc Welding (SAW) Simulation Engine
// Visuals: Real-time 60fps 3D isometric helical forming + 2D developed geometry + SAW torches
// ============================================================================

class SawhSimulationEngine {
    constructor() {
        this.canvas3D = null;
        this.ctx3D = null;
        this.canvas2D = null;
        this.ctx2D = null;
        this.animId = null;
        this.lastTime = 0;

        // Physical & Mathematical Parameters
        this.d = 1219.0;
        this.t = 14.30;
        this.B = 2170.0;
        this.dm = 1204.7;
        this.piD = Math.PI * this.dm;
        this.alphaDeg = 45.0;
        this.alphaRad = Math.PI / 4;
        this.pitch = 2676.0;
        this.bMin = 1599.0;
        this.bMax = 3277.0;

        // Animation State
        this.isPlaying = true;
        this.speed = 1.0;
        this.phase = 0.0;
        this.viewMode = '3d'; // '3d' | '2d' | 'split'

        // Visual Layer Toggles
        this.showSparks = true;
        this.showDims = true;
        this.showRolls = true;
        this.showXray = false;

        // Spark Particle System
        this.sparks = [];
        this.maxSparks = 35;

        this.initialized = false;
    }

    init() {
        this.canvas3D = document.getElementById("sawh-anim-canvas");
        this.canvas2D = document.getElementById("sawh-2d-canvas");
        if (!this.canvas3D || !this.canvas2D) return;

        this.ctx3D = this.canvas3D.getContext("2d");
        this.ctx2D = this.canvas2D.getContext("2d");

        this.bindEvents();
        this.resize();
        window.addEventListener("resize", () => this.resize());

        this.initialized = true;
        this.start();
    }

    resize() {
        const resizeSingle = (cv) => {
            if (!cv) return;
            const rect = cv.getBoundingClientRect();
            const dpr = window.devicePixelRatio || 1;
            const w = Math.max(300, Math.round(rect.width || 600));
            const h = Math.max(250, Math.round(rect.height || 460));
            if (cv.width !== w * dpr || cv.height !== h * dpr) {
                cv.width = w * dpr;
                cv.height = h * dpr;
            }
        };
        resizeSingle(this.canvas3D);
        resizeSingle(this.canvas2D);
    }

    updateParameters(d, t, B) {
        this.d = Math.max(10, parseFloat(d) || 1219.0);
        this.t = Math.max(0.5, parseFloat(t) || 14.30);
        this.dm = Math.max(1, this.d - this.t);
        this.piD = Math.PI * this.dm;
        this.B = Math.max(10, parseFloat(B) || 2000.0);

        const r = Math.min(1.0, Math.max(0.0, this.B / this.piD));
        this.alphaRad = Math.acos(r);
        this.alphaDeg = this.alphaRad * 180 / Math.PI;

        const sinA = Math.sin(this.alphaRad);
        const tanA = Math.tan(this.alphaRad);
        this.pitch = (sinA > 1e-6 && Math.abs(tanA) > 1e-6) ? (this.piD / tanA) : 99999;

        this.bMin = this.piD * Math.cos(65 * Math.PI / 180);
        this.bMax = this.piD * Math.cos(30 * Math.PI / 180);

        // Update DOM HUD and status elements
        this.updateDOM();
    }

    updateDOM() {
        const elAlpha = document.getElementById("sawh-alpha");
        const elPitch = document.getElementById("sawh-pitch");
        const elRange = document.getElementById("sawh-range");
        const elBadge = document.getElementById("sawh-badge");
        const elNote = document.getElementById("sawh-note");
        const elHudAlpha = document.getElementById("sawh-hud-alpha");
        const elHudPitch = document.getElementById("sawh-hud-pitch");
        const elStatus = document.getElementById("sawh-alpha-status");
        const elPiD = document.getElementById("sawh-pid-val");

        if (elAlpha) elAlpha.innerText = this.alphaDeg.toFixed(1) + "°";
        if (elPitch) elPitch.innerText = isFinite(this.pitch) && this.pitch < 90000 ? this.pitch.toFixed(0) : "—";
        if (elRange) elRange.innerText = `${this.bMin.toFixed(0)} – ${this.bMax.toFixed(0)}`;
        if (elPiD) elPiD.innerText = Math.round(this.piD);

        const valid = this.alphaDeg >= 30.0 && this.alphaDeg <= 65.0;

        if (elBadge) {
            elBadge.className = "text-xs font-bold px-3 py-1 rounded-md border " +
                (valid ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-red-50 text-red-700 border-red-200");
            elBadge.innerText = valid ? "UYGUN (α ∈ [30°, 65°])" : "ARALIK DIŞI (UYARI)";
        }

        if (elStatus) {
            elStatus.className = "text-[10px] font-bold px-2 py-0.5 rounded " +
                (valid ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800");
            elStatus.innerText = valid ? "✓ Standart Aralık" : "⚠️ Özel Tasarım";
        }

        if (elNote) {
            elNote.innerHTML = valid
                ? `<span class="text-emerald-700 font-bold">✓ Optimum Helis Açısı:</span> ${this.alphaDeg.toFixed(1)}° açısı, spiral gerilmeleri ve kaynak dikiş yükünü ideal dağıtır.`
                : `<span class="text-amber-700 font-bold">⚠️ Pratik Aralık Dışı:</span> Helis açısının 30° ile 65° arasında olması önerilir (Mevcut: ${this.alphaDeg.toFixed(1)}°).`;
        }

        if (elHudAlpha) elHudAlpha.innerText = `α = ${this.alphaDeg.toFixed(1)}°`;
        if (elHudPitch) elHudPitch.innerText = `P = ${isFinite(this.pitch) && this.pitch < 90000 ? this.pitch.toFixed(0) : "—"} mm`;

        if (visualizer3DInstance) visualizer3DInstance.setHelixAngle(this.alphaDeg);
    }

    bindEvents() {
        const toggleBtn = document.getElementById("sawh-anim-toggle");
        const resetBtn = document.getElementById("sawh-anim-reset");
        const icon = document.getElementById("sawh-anim-icon");
        const label = document.getElementById("sawh-anim-label");

        if (toggleBtn) {
            toggleBtn.onclick = () => {
                this.isPlaying = !this.isPlaying;
                if (icon) icon.innerText = this.isPlaying ? "⏸️" : "▶️";
                if (label) label.innerText = this.isPlaying ? "Durdur" : "Oynat";
            };
        }

        if (resetBtn) {
            resetBtn.onclick = () => {
                this.phase = 0.0;
                this.sparks = [];
            };
        }

        // Speed buttons
        document.querySelectorAll(".sawh-speed-btn").forEach(btn => {
            btn.onclick = (e) => {
                document.querySelectorAll(".sawh-speed-btn").forEach(b => {
                    b.classList.remove("bg-white", "text-blue-600", "shadow-2xs");
                    b.classList.add("text-slate-600");
                });
                btn.classList.add("bg-white", "text-blue-600", "shadow-2xs");
                btn.classList.remove("text-slate-600");
                this.speed = parseFloat(btn.dataset.speed || 1.0);
            };
        });

        // Layer Toggles
        const chkSparks = document.getElementById("sawh-opt-sparks");
        const chkDims = document.getElementById("sawh-opt-dims");
        const chkRolls = document.getElementById("sawh-opt-rolls");
        const chkXray = document.getElementById("sawh-opt-xray");

        if (chkSparks) chkSparks.onchange = (e) => { this.showSparks = e.target.checked; };
        if (chkDims) chkDims.onchange = (e) => { this.showDims = e.target.checked; };
        if (chkRolls) chkRolls.onchange = (e) => { this.showRolls = e.target.checked; };
        if (chkXray) chkXray.onchange = (e) => { this.showXray = e.target.checked; };

        // View Mode buttons
        const btn3d = document.getElementById("sawh-view-anim-btn");
        const btn2d = document.getElementById("sawh-view-2d-btn");
        const btnSplit = document.getElementById("sawh-view-split-btn");

        const updateViewButtons = (activeBtn) => {
            [btn3d, btn2d, btnSplit].forEach(b => {
                if (!b) return;
                b.classList.remove("bg-white", "text-blue-600", "shadow-xs");
                b.classList.add("text-slate-600");
            });
            if (activeBtn) {
                activeBtn.classList.add("bg-white", "text-blue-600", "shadow-xs");
                activeBtn.classList.remove("text-slate-600");
            }
        };

        if (btn3d) btn3d.onclick = () => {
            this.viewMode = '3d';
            updateViewButtons(btn3d);
            this.updateCanvasVisibility();
        };

        if (btn2d) btn2d.onclick = () => {
            this.viewMode = '2d';
            updateViewButtons(btn2d);
            this.updateCanvasVisibility();
        };

        if (btnSplit) btnSplit.onclick = () => {
            this.viewMode = 'split';
            updateViewButtons(btnSplit);
            this.updateCanvasVisibility();
        };

        // Quick Preset B buttons
        const btnMin = document.getElementById("sawh-btn-bmin");
        const btnNom = document.getElementById("sawh-btn-bnom");
        const btnMax = document.getElementById("sawh-btn-bmax");
        const range = document.getElementById("sawh-strip-range");
        const input = document.getElementById("sawh-strip-input");

        const setBValue = (val) => {
            const v = Math.round(val);
            if (range) range.value = v;
            if (input) input.value = v;
            this.updateParameters(this.d, this.t, v);
        };

        if (btnMin) btnMin.onclick = () => setBValue(this.bMin);
        if (btnNom) btnNom.onclick = () => setBValue(this.piD * Math.cos(55 * Math.PI / 180));
        if (btnMax) btnMax.onclick = () => setBValue(this.bMax);
    }

    updateCanvasVisibility() {
        if (!this.canvas3D || !this.canvas2D) return;
        if (this.viewMode === '3d') {
            this.canvas3D.classList.remove("hidden", "w-1/2");
            this.canvas3D.classList.add("w-full");
            this.canvas2D.classList.add("hidden");
            this.canvas2D.classList.remove("w-1/2");
        } else if (this.viewMode === '2d') {
            this.canvas3D.classList.add("hidden");
            this.canvas3D.classList.remove("w-1/2", "w-full");
            this.canvas2D.classList.remove("hidden", "w-1/2");
            this.canvas2D.classList.add("w-full");
        } else if (this.viewMode === 'split') {
            this.canvas3D.classList.remove("hidden", "w-full");
            this.canvas3D.classList.add("w-1/2");
            this.canvas2D.classList.remove("hidden", "w-full");
            this.canvas2D.classList.add("w-1/2");
        }
        this.resize();
    }

    start() {
        const loop = (timestamp) => {
            if (!this.lastTime) this.lastTime = timestamp;
            const dt = Math.min(0.1, (timestamp - this.lastTime) / 1000);
            this.lastTime = timestamp;

            if (this.isPlaying) {
                // Advance translation & rotation phase
                const advanceSpeed = 0.55 * this.speed;
                this.phase = (this.phase + dt * advanceSpeed) % (Math.PI * 2);

                // Update sparks
                if (this.showSparks) {
                    this.updateSparks(dt);
                }
            }

            // Render active view mode
            if (this.viewMode === '3d' || this.viewMode === 'split') {
                this.render3D();
            }
            if (this.viewMode === '2d' || this.viewMode === 'split') {
                this.render2D();
            }

            this.animId = requestAnimationFrame(loop);
        };
        this.animId = requestAnimationFrame(loop);
    }

    updateSparks(dt) {
        // Spawn sparks from welding torch
        if (Math.random() < 0.65) {
            const count = Math.floor(Math.random() * 3) + 1;
            for (let i = 0; i < count; i++) {
                if (this.sparks.length < this.maxSparks) {
                    const angle = -Math.PI / 2 + (Math.random() - 0.5) * 1.6;
                    const spd = 60 + Math.random() * 110;
                    this.sparks.push({
                        x: 0,
                        y: 0,
                        vx: Math.cos(angle) * spd,
                        vy: Math.sin(angle) * spd,
                        life: 0.3 + Math.random() * 0.45,
                        maxLife: 0.7,
                        size: 1.0 + Math.random() * 1.8,
                        color: Math.random() > 0.3 ? '#fef08a' : '#f97316'
                    });
                }
            }
        }

        // Update existing sparks
        for (let i = this.sparks.length - 1; i >= 0; i--) {
            const s = this.sparks[i];
            s.x += s.vx * dt;
            s.y += s.vy * dt;
            s.vy += 180 * dt; // gravity
            s.life -= dt;
            if (s.life <= 0) {
                this.sparks.splice(i, 1);
            }
        }
    }

    render3D() {
        const cv = this.canvas3D;
        const ctx = this.ctx3D;
        if (!cv || !ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const W = cv.width / dpr;
        const H = cv.height / dpr;

        ctx.save();
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, W, H);

        // --- 1. Background Grid & Machine Vignette ---
        const bgGrad = ctx.createRadialGradient(W * 0.5, H * 0.45, 40, W * 0.5, H * 0.5, Math.max(W, H) * 0.7);
        bgGrad.addColorStop(0, "#0f172a");
        bgGrad.addColorStop(1, "#020617");
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, W, H);

        // Perspective Floor Guide Lines
        ctx.strokeStyle = "rgba(51, 65, 85, 0.25)";
        ctx.lineWidth = 1;
        const floorY = H * 0.78;
        for (let x = -W; x < W * 2; x += 60) {
            ctx.beginPath();
            ctx.moveTo(x, floorY);
            ctx.lineTo(x + (x - W * 0.5) * 0.6, H);
            ctx.stroke();
        }

        // --- 2. Geometry Setup ---
        const R = Math.max(42, Math.min(105, (H * 0.22) * (this.d / 1219.0) * 0.9 + 40));
        const cx = W * 0.52;
        const cy = H * 0.48;
        const pipeLen = W * 0.42;

        // Helix geometry on screen
        const pitchPx = Math.max(40, (this.pitch / this.dm) * (R * 2));
        const alpha = this.alphaRad;

        // --- 3. Forming Rolls / Roll Stand (Under & Behind) ---
        if (this.showRolls) {
            ctx.fillStyle = "#1e293b";
            ctx.strokeStyle = "#475569";
            ctx.lineWidth = 1.5;

            // Lower Bending Support Rolls
            [-R * 0.8, 0, R * 0.8].forEach(ox => {
                const rx = cx + ox;
                const ry = cy + R + 18;
                ctx.beginPath();
                ctx.arc(rx, ry, 12, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
                // Roll Axle
                ctx.fillStyle = "#64748b";
                ctx.beginPath();
                ctx.arc(rx, ry, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#1e293b";
            });
        }

        // --- 4. Incoming Steel Strip Plate (Entering from Bottom-Right at Angle alpha) ---
        ctx.save();
        const stripW = Math.max(25, (this.B / this.piD) * (R * Math.PI * 1.1));
        const stripLen = W * 0.55;

        // Translate to forming confluence point
        ctx.translate(cx, cy);
        ctx.rotate(alpha);

        // Strip Gradient (Metallic Brushed Steel)
        const stripGrad = ctx.createLinearGradient(0, -stripW / 2, 0, stripW / 2);
        stripGrad.addColorStop(0, "#475569");
        stripGrad.addColorStop(0.2, "#94a3b8");
        stripGrad.addColorStop(0.5, "#cbd5e1");
        stripGrad.addColorStop(0.8, "#64748b");
        stripGrad.addColorStop(1, "#334155");

        ctx.fillStyle = stripGrad;
        ctx.strokeStyle = "#0ea5e9";
        ctx.lineWidth = 1.5;

        // Draw entry plate
        ctx.beginPath();
        ctx.rect(0, -stripW / 2, stripLen, stripW);
        ctx.fill();
        ctx.stroke();

        // Moving feed stripes along strip
        ctx.strokeStyle = "rgba(14, 165, 233, 0.4)";
        ctx.lineWidth = 2;
        const feedOffset = (this.phase * 45) % 35;
        for (let fx = feedOffset; fx < stripLen; fx += 35) {
            ctx.beginPath();
            ctx.moveTo(fx, -stripW / 2);
            ctx.lineTo(fx, stripW / 2);
            ctx.stroke();
        }

        // Strip Feed Direction Arrow
        ctx.fillStyle = "#38bdf8";
        ctx.beginPath();
        const arrowX = stripLen * 0.5;
        ctx.moveTo(arrowX + 20, 0);
        ctx.lineTo(arrowX - 10, -10);
        ctx.lineTo(arrowX - 4, 0);
        ctx.lineTo(arrowX - 10, 10);
        ctx.closePath();
        ctx.fill();

        ctx.restore();

        // --- 5. Formed Cylindrical Pipe Body (3D Cylinder Shading) ---
        const pipeLeft = cx - pipeLen;

        // Outer Cylinder Shading
        const cylGrad = ctx.createLinearGradient(0, cy - R, 0, cy + R);
        if (this.showXray) {
            cylGrad.addColorStop(0, "rgba(30, 58, 138, 0.45)");
            cylGrad.addColorStop(0.3, "rgba(56, 189, 248, 0.35)");
            cylGrad.addColorStop(0.7, "rgba(14, 116, 144, 0.25)");
            cylGrad.addColorStop(1, "rgba(15, 23, 42, 0.65)");
        } else {
            cylGrad.addColorStop(0, "#334155");
            cylGrad.addColorStop(0.18, "#94a3b8");
            cylGrad.addColorStop(0.35, "#e2e8f0");
            cylGrad.addColorStop(0.65, "#475569");
            cylGrad.addColorStop(0.9, "#1e293b");
            cylGrad.addColorStop(1, "#0f172a");
        }

        ctx.fillStyle = cylGrad;
        ctx.beginPath();
        ctx.rect(pipeLeft, cy - R, pipeLen, R * 2);
        ctx.fill();

        // Cylinder Outline
        ctx.strokeStyle = this.showXray ? "rgba(56, 189, 248, 0.8)" : "#64748b";
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(pipeLeft, cy - R);
        ctx.lineTo(cx, cy - R);
        ctx.moveTo(pipeLeft, cy + R);
        ctx.lineTo(cx, cy + R);
        ctx.stroke();

        // --- 6. Spiral Weld Seam (Helical Curves around the Cylinder) ---
        const numTurns = Math.ceil(pipeLen / Math.max(1, pitchPx)) + 2;

        for (let pass = 0; pass < 2; pass++) {
            // Pass 0: Back seam (drawn only in X-Ray mode)
            // Pass 1: Front seam (glowing golden weld bead)
            if (pass === 0 && !this.showXray) continue;

            for (let i = -1; i <= numTurns; i++) {
                const turnX = cx - (i * pitchPx) - ((this.phase / (Math.PI * 2)) * pitchPx);

                ctx.beginPath();
                let started = false;

                const stepCount = 36;
                for (let s = 0; s <= stepCount; s++) {
                    const theta = (s / stepCount) * Math.PI * 2;
                    const isFront = (theta <= Math.PI);

                    if ((pass === 1 && isFront) || (pass === 0 && !isFront)) {
                        const px = turnX + (theta / (Math.PI * 2)) * pitchPx;
                        const py = cy - Math.cos(theta) * R;

                        if (px >= pipeLeft && px <= cx) {
                            if (!started) {
                                ctx.moveTo(px, py);
                                started = true;
                            } else {
                                ctx.lineTo(px, py);
                            }
                        }
                    }
                }

                if (started) {
                    if (pass === 1) {
                        // Golden Glowing Weld Seam
                        ctx.strokeStyle = "#f59e0b";
                        ctx.lineWidth = 3.5;
                        ctx.stroke();

                        ctx.strokeStyle = "#fef08a";
                        ctx.lineWidth = 1.2;
                        ctx.stroke();
                    } else {
                        // Back X-Ray Seam
                        ctx.strokeStyle = "rgba(245, 158, 11, 0.35)";
                        ctx.lineWidth = 1.8;
                        ctx.setLineDash([3, 3]);
                        ctx.stroke();
                        ctx.setLineDash([]);
                    }
                }
            }
        }

        // --- 7. Pipe Open Exit Face (Front Ellipse on the Left) ---
        const rx = R * 0.28;
        const ry = R;
        const wallThkPx = Math.max(3, (this.t / this.d) * R * 2.2);

        // Inner Bore Background
        ctx.fillStyle = "#020617";
        ctx.beginPath();
        ctx.ellipse(pipeLeft, cy, rx - wallThkPx * 0.28, ry - wallThkPx, 0, 0, Math.PI * 2);
        ctx.fill();

        // Metallic Pipe End Ring (Steel Wall Thickness Face)
        ctx.fillStyle = "#94a3b8";
        ctx.strokeStyle = "#cbd5e1";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(pipeLeft, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.ellipse(pipeLeft, cy, rx - wallThkPx * 0.28, ry - wallThkPx, 0, 0, Math.PI * 2, true);
        ctx.fill("evenodd");
        ctx.stroke();

        // Pipe Exit Translation Velocity Arrow
        ctx.fillStyle = "#10b981";
        ctx.beginPath();
        const exitArrowX = pipeLeft - 30;
        ctx.moveTo(exitArrowX - 25, cy);
        ctx.lineTo(exitArrowX - 5, cy - 8);
        ctx.lineTo(exitArrowX - 10, cy);
        ctx.lineTo(exitArrowX - 5, cy + 8);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = "#10b981";
        ctx.font = "bold 10px Inter, sans-serif";
        ctx.fillText("Boru Çıkışı (v_pipe)", exitArrowX - 75, cy - 14);

        // --- 8. Submerged Arc Welding (SAW) Torches & Plasma Arcs ---
        // OD Welding Head (Outside Torch at Top Forming Point)
        const torchX = cx - 12;
        const torchY = cy - R;

        ctx.fillStyle = "#334155";
        ctx.strokeStyle = "#94a3b8";
        ctx.lineWidth = 1.5;

        // Torch Body & Flux Nozzle
        ctx.beginPath();
        ctx.rect(torchX - 8, torchY - 36, 16, 26);
        ctx.fill();
        ctx.stroke();

        // Copper Contact Tip
        ctx.fillStyle = "#b45309";
        ctx.beginPath();
        ctx.moveTo(torchX - 5, torchY - 10);
        ctx.lineTo(torchX + 5, torchY - 10);
        ctx.lineTo(torchX + 2, torchY);
        ctx.lineTo(torchX - 2, torchY);
        ctx.closePath();
        ctx.fill();

        // OD SAW Arc & Molten Pool Glow
        const arcPulse = 0.85 + Math.sin(Date.now() * 0.02) * 0.15;
        const arcGrad = ctx.createRadialGradient(torchX, torchY, 1, torchX, torchY, 18 * arcPulse);
        arcGrad.addColorStop(0, "rgba(255, 255, 255, 1)");
        arcGrad.addColorStop(0.3, "rgba(254, 240, 138, 0.9)");
        arcGrad.addColorStop(0.65, "rgba(245, 158, 11, 0.6)");
        arcGrad.addColorStop(1, "rgba(239, 68, 68, 0)");

        ctx.fillStyle = arcGrad;
        ctx.beginPath();
        ctx.arc(torchX, torchY, 18 * arcPulse, 0, Math.PI * 2);
        ctx.fill();

        // ID Welding Head Indicator (Inside Torch)
        const idTorchX = cx - 35;
        const idTorchY = cy + R * 0.35;
        const idGlow = ctx.createRadialGradient(idTorchX, idTorchY, 1, idTorchX, idTorchY, 12);
        idGlow.addColorStop(0, "rgba(251, 146, 60, 0.8)");
        idGlow.addColorStop(1, "rgba(234, 88, 12, 0)");
        ctx.fillStyle = idGlow;
        ctx.beginPath();
        ctx.arc(idTorchX, idTorchY, 12, 0, Math.PI * 2);
        ctx.fill();

        // Render Sparks
        if (this.showSparks) {
            this.sparks.forEach(spk => {
                ctx.fillStyle = spk.color;
                ctx.beginPath();
                ctx.arc(torchX + spk.x, torchY + spk.y, spk.size, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // --- 9. Live Engineering Dimension & Angle Overlays ---
        if (this.showDims) {
            // A. Helix Angle alpha Arc
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(cx, cy, 55, 0, alpha);
            ctx.stroke();

            // Horizontal Reference Line
            ctx.strokeStyle = "rgba(56, 189, 248, 0.5)";
            ctx.setLineDash([4, 3]);
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + 85, cy);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.fillStyle = "#38bdf8";
            ctx.font = "bold 13px Inter, sans-serif";
            const midA = alpha * 0.5;
            ctx.fillText(`α = ${this.alphaDeg.toFixed(1)}°`, cx + 65 * Math.cos(midA), cy + 65 * Math.sin(midA));

            // B. Strip Width B Dimension Line
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(alpha);
            const dimBx = stripLen * 0.75;
            ctx.strokeStyle = "#f59e0b";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(dimBx, -stripW / 2);
            ctx.lineTo(dimBx, stripW / 2);
            ctx.stroke();

            // End ticks
            ctx.beginPath();
            ctx.moveTo(dimBx - 5, -stripW / 2);
            ctx.lineTo(dimBx + 5, -stripW / 2);
            ctx.moveTo(dimBx - 5, stripW / 2);
            ctx.lineTo(dimBx + 5, stripW / 2);
            ctx.stroke();

            ctx.fillStyle = "#f59e0b";
            ctx.font = "bold 11px Inter, sans-serif";
            ctx.fillText(`B = ${this.B.toFixed(0)} mm`, dimBx + 8, 4);
            ctx.restore();

            // C. Spiral Pitch P Dimension Line (on Top of Pipe)
            if (isFinite(this.pitch) && pitchPx > 25) {
                const pDimY = cy - R - 18;
                const pX1 = cx - pitchPx;
                const pX2 = cx;

                ctx.strokeStyle = "#fbbf24";
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(pX1, pDimY);
                ctx.lineTo(pX2, pDimY);
                // End ticks
                ctx.moveTo(pX1, pDimY - 4);
                ctx.lineTo(pX1, pDimY + 4);
                ctx.moveTo(pX2, pDimY - 4);
                ctx.lineTo(pX2, pDimY + 4);
                ctx.stroke();

                ctx.fillStyle = "#fbbf24";
                ctx.font = "bold 11px Inter, sans-serif";
                ctx.fillText(`Adım P = ${this.pitch.toFixed(0)} mm`, (pX1 + pX2) / 2 - 45, pDimY - 6);
            }

            // D. Outer Diameter D Callout (Left Face)
            const dLineX = pipeLeft - 18;
            ctx.strokeStyle = "#e2e8f0";
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.moveTo(dLineX, cy - R);
            ctx.lineTo(dLineX, cy + R);
            ctx.moveTo(dLineX - 4, cy - R);
            ctx.lineTo(dLineX + 4, cy - R);
            ctx.moveTo(dLineX - 4, cy + R);
            ctx.lineTo(dLineX + 4, cy + R);
            ctx.stroke();

            ctx.fillStyle = "#e2e8f0";
            ctx.font = "bold 11px Inter, sans-serif";
            ctx.fillText(`D = ${this.d.toFixed(1)} mm`, dLineX - 95, cy + 4);
        }

        ctx.restore();
    }

    render2D() {
        const cv = this.canvas2D;
        const ctx = this.ctx2D;
        if (!cv || !ctx) return;

        const dpr = window.devicePixelRatio || 1;
        const W = cv.width / dpr;
        const H = cv.height / dpr;

        ctx.save();
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, W, H);

        // Blueprint Background
        ctx.fillStyle = "#020617";
        ctx.fillRect(0, 0, W, H);

        // Grid lines
        ctx.strokeStyle = "rgba(30, 41, 59, 0.6)";
        ctx.lineWidth = 1;
        for (let x = 0; x < W; x += 30) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += 30) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        const pad = 36;
        const alphaRad = this.alphaRad;
        const alphaDeg = this.alphaDeg;
        const piD = this.piD;
        const pitch = isFinite(this.pitch) ? this.pitch : 2000;

        // --- Top: Developed Cylinder Rectangle (One Full Turn) ---
        const topH = H * 0.44;
        const scale = Math.min((W - pad * 2) / piD, (topH - pad) / Math.max(pitch, 60));
        const rw = piD * scale;
        const rh = Math.max(24, pitch * scale);
        const ox = pad + (W - pad * 2 - rw) / 2;
        const oy = pad + topH - rh;

        ctx.fillStyle = "rgba(30, 41, 59, 0.4)";
        ctx.fillRect(ox, oy, rw, rh);
        ctx.strokeStyle = "#64748b";
        ctx.lineWidth = 2;
        ctx.strokeRect(ox, oy, rw, rh);

        // Helical Seam Diagonal
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(ox, oy + rh);
        ctx.lineTo(ox + rw, oy);
        ctx.stroke();

        // Angle alpha Arc
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(ox, oy + rh, Math.min(30, rh * 0.6), -Math.PI / 2, -Math.PI / 2 + alphaRad);
        ctx.stroke();

        ctx.fillStyle = "#38bdf8";
        ctx.font = "bold 12px Inter, sans-serif";
        ctx.fillText(`α = ${alphaDeg.toFixed(1)}°`, ox + 36, oy + rh - 12);

        // Labels
        ctx.fillStyle = "#e2e8f0";
        ctx.font = "11px Inter, sans-serif";
        ctx.fillText(`Çevre π·D_mid = ${piD.toFixed(0)} mm`, ox + rw / 2 - 70, oy + rh + 18);
        ctx.fillText(`Adım P = ${pitch.toFixed(0)} mm`, ox + 8, oy + rh / 2);

        ctx.fillStyle = "#94a3b8";
        ctx.font = "bold 11px Inter, sans-serif";
        ctx.fillText("Açılmış Boru Yüzeyi (1 Helis Turu)", ox + rw / 2 - 80, oy - 10);

        // --- Bottom: Unrolled Strip Band (Parallelogram) ---
        const botY = H * 0.54;
        const botH = H - botY - pad;
        const s2 = Math.min((W - pad * 2) / piD, (botH - pad) / Math.max(pitch, 60));
        const bw = piD * s2;
        const bh = Math.max(24, pitch * s2);
        const bx = pad + (W - pad * 2 - bw) / 2;

        const P1x = bx, P1y = botY + bh;
        const P2x = bx + bw, P2y = botY;
        const off = Math.min(this.B * s2, bw * 0.95);
        const qx = off * Math.cos(alphaRad);
        const qy = off * (-Math.sin(alphaRad));
        const Q1x = P1x + qx, Q1y = P1y + qy;
        const Q2x = P2x + qx, Q2y = P2y + qy;

        ctx.fillStyle = "rgba(245, 158, 11, 0.22)";
        ctx.strokeStyle = "#f59e0b";
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(P1x, P1y);
        ctx.lineTo(P2x, P2y);
        ctx.lineTo(Q2x, Q2y);
        ctx.lineTo(Q1x, Q1y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Strip Width B measurement line
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 1.8;
        ctx.setLineDash([4, 3]);
        ctx.beginPath();
        ctx.moveTo(P1x, P1y);
        ctx.lineTo(Q1x, Q1y);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = "#38bdf8";
        ctx.font = "bold 12px Inter, sans-serif";
        ctx.fillText(`B = ${this.B.toFixed(0)} mm`, (P1x + Q1x) / 2 + 10, (P1y + Q1y) / 2 - 8);

        ctx.fillStyle = "#94a3b8";
        ctx.font = "bold 11px Inter, sans-serif";
        ctx.fillText("Açılmış Sac Şerit (B = π·D_mid·cos α)", bx + bw / 2 - 100, botY + bh + 20);

        ctx.restore();
    }
}

// Global Singleton Instance
let sawhSimulatorInstance = null;

function renderSawhCard(pipeData) {
    const card = document.getElementById("sawh-card");
    const na = document.getElementById("sawh-not-applicable");
    if (!card || !na) return;

    const process = (pipeData.input_summary.manufacturing_process || "").toUpperCase();
    const isSawh = process.includes("SAWH") || process.includes("SAWL");
    if (!isSawh) {
        card.classList.add("hidden");
        na.classList.remove("hidden");
        const p = document.getElementById("sawh-na-process");
        if (p) p.innerText = pipeData.input_summary.manufacturing_process || "—";
        return;
    }

    na.classList.add("hidden");
    card.classList.remove("hidden");

    const d = pipeData.input_summary.diameter_mm || 1219.0;
    const t = pipeData.input_summary.wall_thickness_mm || 14.30;
    const dm = d - t;
    const piD = Math.PI * dm;
    const B55 = piD * Math.cos(55 * Math.PI / 180);
    const bMin = piD * Math.cos(65 * Math.PI / 180);

    const dEl = document.getElementById("sawh-d");
    const tEl = document.getElementById("sawh-t");
    const dmEl = document.getElementById("sawh-dmid");
    if (dEl) dEl.innerText = d.toFixed(1);
    if (tEl) tEl.innerText = t.toFixed(2);
    if (dmEl) dmEl.innerText = dm.toFixed(1);

    const range = document.getElementById("sawh-strip-range");
    const input = document.getElementById("sawh-strip-input");
    if (range && input) {
        range.min = Math.round(bMin * 0.85);
        range.max = Math.round(piD);
        range.value = Math.round(B55);
        input.value = Math.round(B55);

        range.oninput = (e) => {
            input.value = e.target.value;
            if (sawhSimulatorInstance) sawhSimulatorInstance.updateParameters(d, t, e.target.value);
        };
        input.oninput = (e) => {
            range.value = e.target.value;
            if (sawhSimulatorInstance) sawhSimulatorInstance.updateParameters(d, t, e.target.value);
        };
    }

    // Initialize or update simulator
    if (!sawhSimulatorInstance) {
        sawhSimulatorInstance = new SawhSimulationEngine();
        sawhSimulatorInstance.init();
    }

    sawhSimulatorInstance.updateParameters(d, t, B55);
}

function sawhRedraw() {
    if (sawhSimulatorInstance) {
        const range = document.getElementById("sawh-strip-range");
        const dEl = document.getElementById("sawh-d");
        const tEl = document.getElementById("sawh-t");
        if (range && dEl && tEl) {
            const d = parseFloat(dEl.innerText) || 1219.0;
            const t = parseFloat(tEl.innerText) || 14.30;
            const B = parseFloat(range.value) || 2170.0;
            sawhSimulatorInstance.updateParameters(d, t, B);
        }
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
    }
    setupITPAuditUI();

    if (wtForm) {
        wtForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(wtForm);
            const stdCode = formData.get("standard_code") || "BOTAŞ";
            const matGrade = formData.get("material_grade") || "X65";
            const isStainless = matGrade.includes("SS") || matGrade.includes("Duplex");
            
            // Negative tolerance handling
            let manualTolRaw = formData.get("manual_negative_tolerance_percent");
            let manualTol = (manualTolRaw !== null && manualTolRaw !== "" && !isNaN(parseFloat(manualTolRaw))) ? parseFloat(manualTolRaw) : null;
            let applyTol = true;
            
            if (stdCode.includes("BOTAŞ") || stdCode.includes("BOTAS")) {
                applyTol = false;
                manualTol = 0.0;
            } else if (stdCode.includes("B31.8") || stdCode.includes("B31.4")) {
                if (isStainless) {
                    const chk = document.getElementById("chk-apply-stainless-tol");
                    applyTol = chk ? chk.checked : (manualTol !== null && manualTol > 0);
                } else {
                    applyTol = manualTol === null || manualTol > 0;
                }
            } else if (stdCode.includes("B31.3")) {
                applyTol = manualTol === null || manualTol > 0;
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
                corrosion_allowance_mm: parseFloat(formData.get("corrosion_allowance_mm") || "0.0"),
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
        const isBotas = std.includes("BOTAŞ") || std.includes("BOTAS");
        const isB313 = std.includes("B31.3");
        const procContainer = document.getElementById("wt-process-container");
        const pslTolRow = document.getElementById("wt-psl-tol-row");
        const pslBox = document.getElementById("wt-psl-box");
        const manualTolBox = document.getElementById("wt-manual-tol-box");
        const tolApi5lText = document.getElementById("wt-tol-api5l-text");
        const tolStainlessOpt = document.getElementById("wt-tol-stainless-opt");
        const tolB313Info = document.getElementById("wt-tol-b313-info");
        const tolDescSpan = document.getElementById("wt-tol-desc-span");
        
        if (isBotas) {
            // BOTAŞ Specification: No negative tolerance input
            if (procContainer) procContainer.classList.remove("hidden");
            if (pslTolRow) pslTolRow.classList.add("hidden");
            if (pslBox) pslBox.classList.add("hidden");
            if (manualTolBox) manualTolBox.classList.add("hidden");
            if (tolApi5lText) tolApi5lText.classList.remove("hidden");
            if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
            if (tolB313Info) tolB313Info.classList.add("hidden");
            if (tolDescSpan) tolDescSpan.innerText = "BOTAŞ Şartnamesi: Et kalınlıkları BOTAŞ standart şartname çizelgesinden doğrudan belirlenir (negatif tolerans düşümü yapılmaz).";
        } else if (isB313) {
            // ASME B31.3
            if (procContainer) procContainer.classList.add("hidden");
            if (pslTolRow) pslTolRow.classList.remove("hidden");
            if (pslBox) pslBox.classList.add("hidden");
            if (manualTolBox) manualTolBox.classList.remove("hidden");
            if (tolApi5lText) tolApi5lText.classList.add("hidden");
            if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
            if (tolB313Info) tolB313Info.classList.remove("hidden");
            if (tolDescSpan) tolDescSpan.innerText = "ASME B31.3 Para. 304.1.2: Negatif imalat toleransı uygulanır (%12.5 standart; dilediğiniz oranı veya %0 seçebilirsiniz).";
        } else {
            // ASME B31.8 / ASME B31.4
            if (pslTolRow) pslTolRow.classList.remove("hidden");
            if (manualTolBox) manualTolBox.classList.remove("hidden");
            
            if (isStainless) {
                if (procContainer) procContainer.classList.add("hidden");
                if (pslBox) pslBox.classList.add("hidden");
                if (tolApi5lText) tolApi5lText.classList.add("hidden");
                if (tolStainlessOpt) tolStainlessOpt.classList.remove("hidden");
                if (tolB313Info) tolB313Info.classList.add("hidden");
            } else {
                // API 5L Carbon Steel
                if (procContainer) procContainer.classList.remove("hidden");
                if (pslBox) pslBox.classList.remove("hidden");
                if (tolApi5lText) tolApi5lText.classList.remove("hidden");
                if (tolStainlessOpt) tolStainlessOpt.classList.add("hidden");
                if (tolB313Info) tolB313Info.classList.add("hidden");
                
                // Calculate live API 5L Tablo 11 description
                const proc = procSelect ? procSelect.value : "SAWH";
                const diaText = diaSelect ? diaSelect.value : "24\"";
                const isLargeDia = !diaText.includes("1/") && !diaText.includes("3/") && parseFloat(diaText) > 20;
                
                if (proc.includes("SMLS")) {
                    if (tolDescSpan) tolDescSpan.innerText = "Dikişsiz (SMLS) borular için API 5L Tablo 11 gereği standart -%12.5 veya yukarıdaki kutudan %0 ya da özel tolerans uygulanır.";
                } else if (proc.includes("ERW") || proc.includes("HFW")) {
                    if (tolDescSpan) tolDescSpan.innerText = "Boyuna kaynaklı (ERW/HFW) borular için API 5L Tablo 11 gereği standart -%10.0 veya yukarıdaki kutudan %0 ya da özel tolerans uygulanır.";
                } else {
                    if (isLargeDia) {
                        if (tolDescSpan) tolDescSpan.innerText = `Tozaltı kaynaklı (SAWH/SAWL) D > 20" borular için API 5L Tablo 11 gereği standart -%8.0 veya yukarıdaki kutudan %0 ya da özel tolerans uygulanır.`;
                    } else {
                        if (tolDescSpan) tolDescSpan.innerText = `Tozaltı kaynaklı (SAWH/SAWL) D ≤ 20" borular için API 5L Tablo 11 gereği standart -%10.0 veya yukarıdaki kutudan %0 ya da özel tolerans uygulanır.`;
                    }
                }
            }
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
    const tolLabel = tolPct > 0 ? `Tolerans Sınırı (-%${tolPct.toFixed(2)}):` : `Nominal Sınır:`;
    const corrVal = Number(r.corrosion_allowance_mm !== undefined ? r.corrosion_allowance_mm : (inp.corrosion_allowance_mm || 0)).toFixed(2);

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

            <div class="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-[11px] text-gray-500 block">Teorik Kalınlık (t):</span>
                    <span class="font-bold text-gray-900 text-base">${Number(r.t_theoretical_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-amber-200 bg-amber-50/30">
                    <span class="text-[11px] text-amber-800 font-semibold block">Korozyon Payı (c):</span>
                    <span class="font-bold text-amber-900 text-base">+${corrVal} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-indigo-200 bg-indigo-50/30">
                    <span class="text-[11px] text-indigo-800 font-semibold block">Gereken (t_req):</span>
                    <span class="font-bold text-indigo-700 text-base">${Number(r.t_required_asme_b31_8_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-blue-300 bg-blue-50/50">
                    <span class="text-[11px] text-blue-800 font-semibold block">Seçilen Nominal:</span>
                    <span class="font-bold text-blue-900 text-base">${Number(r.selected_nominal_thickness_asme_b36_10_mm).toFixed(2)} mm</span>
                </div>
                <div class="bg-white p-2.5 rounded border border-gray-200">
                    <span class="text-[11px] text-gray-500 block">${tolLabel}</span>
                    <span class="font-bold text-gray-900 text-base">${Number(r.negative_tolerance_min_mm).toFixed(2)} mm</span>
                </div>
            </div>

            <div class="mt-3 p-2 bg-white/80 rounded border border-blue-100 text-xs text-slate-700 flex flex-wrap items-center justify-between gap-1">
                <span><strong>Tolerans Kuralı:</strong> ${r.tolerance_rule_description || 'Standart Tolerans Kuralı'}</span>
                <span class="font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">${esc(inp.manufacturing_process || 'SAWH')} | ${esc(inp.psl_level || 'PSL2')}</span>
            </div>

            <div class="mt-2 flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-blue-100 text-xs">
                <span class="text-gray-600">
                    ${!inp.is_stainless && r.botas_standard_thickness_mm > 0 ? `${r.botas_standard_label ? r.botas_standard_label + ' Tavsiyesi' : 'BOTAŞ Standart Tavsiyesi'}: <strong>${Number(r.botas_standard_thickness_mm).toFixed(2)} mm</strong>` : `Tasarım Kriteri: <strong>${r.design_factor_used}</strong>`}
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
                    ${data.passed_count} / ${data.total_applicable} Parametre Uygun
                </span>
            </div>
            <div class="text-[11px] text-slate-600 mb-3">
                Kontrol edilen: <strong>${data.checks_count}</strong> &nbsp;•&nbsp; Uygun: <strong class="text-emerald-700">${data.passed_count}</strong>
                &nbsp;•&nbsp; Red: <strong class="text-red-700">${data.failed_count}</strong>
                &nbsp;•&nbsp; Bekleyen: <strong>${data.unchecked_count}</strong>
                ${data.checks_count === 0 ? '<span class="text-amber-700 font-semibold">— Lütfen yukarıdaki forma ölçüm verisi girin.</span>' : ''}
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
                <td class="p-2 font-medium text-gray-600">${esc(c.category)}</td>
                <td class="p-2 font-bold text-gray-800">${esc(c.parameter)}</td>
                <td class="p-2 text-center font-mono font-semibold">${esc(c.actual_value)}</td>
                <td class="p-2 text-center font-mono text-gray-600">${esc(c.required_limit)}</td>
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
    renderITPPipeChips();

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

        // Store plan for modal lookups
        window._itpData = res.test_plan;

        const isBotasPipe = pipe.standard_type && (pipe.standard_type.includes("BOTAŞ") || pipe.standard_type.includes("BOTAS"));
        const stdLabel = isBotasPipe ? "BOTAŞ Çelik Boru Şartnamesi (4-NGTL-0-GN-P-002-5120 R7)" : "API Spec 5L 47. Baskı / ISO 3183";

        let html = `<p class="text-[11px] text-slate-500 mb-2">Seçili boru: <strong>${esc(pipe.diameter_inch)} - ${esc(pipe.material_grade)} (${esc(pipe.manufacturing_process)})</strong> — <span class="text-indigo-700 font-semibold">${stdLabel}</span> (satıra tıklayın: standart metni + numune çizimi)</p>`;
        html += `<div class="overflow-x-auto"><table class="w-full text-xs text-left border-collapse bg-white rounded border border-gray-300">`;
        html += `<thead class="bg-gray-100 text-gray-700 font-bold border-b border-gray-300"><tr>
            <th class="p-2">Test</th><th class="p-2">Madde</th><th class="p-2">Sıklık / Adet</th><th class="p-2">Alınma Yeri</th><th class="p-2">Numune Boyutu</th></tr></thead><tbody>`;

        res.test_plan.forEach((tp, i) => {
            const hasFig = !!tp.specimen_figure;
            html += `
            <tr class="itp-test-row border-b border-gray-200 cursor-pointer hover:bg-blue-50" onclick="toggleItpRow('itp-detail-${i}')">
                <td class="p-2 font-bold">${esc(tp.test)}</td>
                <td class="p-2 text-slate-600">
                    ${esc(tp.clause)}
                    <button onclick="event.stopPropagation(); openItpInfoModal('clause', ${i})" class="itp-info-btn" title="Standart maddesini göster (ℹ)">ℹ️</button>
                </td>
                <td class="p-2">${esc(tp.frequency)}</td>
                <td class="p-2">${esc(tp.location)}</td>
                <td class="p-2">
                    ${esc(tp.specimen)}
                    ${hasFig ? `<button onclick="event.stopPropagation(); openItpInfoModal('figure', ${i})" class="itp-info-btn" title="Numune çizimini göster (ℹ)">ℹ️</button>` : ''}
                </td>
            </tr>
            <tr id="itp-detail-${i}" class="hidden bg-slate-50 border-b border-gray-200">
                <td colspan="5" class="p-3">
                    <div class="text-[11px] text-slate-700 whitespace-pre-line mb-2 leading-relaxed">${esc(tp.clause_ref || '')}</div>
                    ${hasFig ? `<div class="border border-slate-200 rounded bg-white p-2">${getSpecimenDrawing(tp.specimen_figure)}</div>` : ''}
                </td>
            </tr>`;
        });
        html += `</tbody></table></div>`;
        panel.innerHTML = html;
    } catch (e) {
        console.error("Test plan load error:", e);
    }
}

function toggleItpRow(id) {
    const row = document.getElementById(id);
    if (row) row.classList.toggle("hidden");
}

function openItpInfoModal(type, idx) {
    const data = (window._itpData || [])[idx];
    if (!data) return;
    const modal = document.getElementById("itp-info-modal");
    const title = document.getElementById("itp-info-title");
    const body = document.getElementById("itp-info-body");
    if (!modal || !title || !body) return;
    if (type === "clause") {
        title.innerText = data.clause;
        body.innerHTML = `<div class="whitespace-pre-line text-sm text-slate-700 leading-relaxed">${esc(data.clause_ref || 'Standart metni bulunamadı.')}</div>`;
    } else {
        title.innerText = `${data.test} — Numune Çizimi`;
        body.innerHTML = getSpecimenDrawing(data.specimen_figure) || '<p class="text-xs text-slate-400">Çizim bulunamadı.</p>';
    }
    modal.classList.remove("hidden");
}

function closeItpInfoModal() {
    const modal = document.getElementById("itp-info-modal");
    if (modal) modal.classList.add("hidden");
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

// ============================================================================
// ITP SMART AUDITOR (UNLIMITED-OCR & API 5L 47TH EDITION / BOTAŞ)
// ============================================================================

let currentITPAuditResult = null;
let currentITPFilter = "ALL";
let currentITPExtractedItems = [];
let currentITPDetectedMeta = null;
let currentITPEffectiveConfig = null;
let currentITPVariantAudits = [];
let currentITPScopeVariants = [];

function setupITPAuditUI() {
    const fileInput = document.getElementById("itp-file-input");
    const dropzoneLabel = document.getElementById("itp-dropzone-label");
    const statusText = document.getElementById("itp-upload-status-text");
    const btnStart = document.getElementById("btn-start-itp-audit");
    const btnDemo = document.getElementById("btn-load-demo-itp");
    const btnExportExcel = document.getElementById("btn-export-itp-excel");
    const btnExportPdf = document.getElementById("btn-export-itp-pdf");
    const btnReAudit = document.getElementById("btn-re-audit-itp");
    const btnAddPipe = document.getElementById("btn-add-detected-pipe-to-project");
    const selStandard = document.getElementById("itp-override-standard");

    if (fileInput && dropzoneLabel) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files && fileInput.files.length > 0) {
                const f = fileInput.files[0];
                dropzoneLabel.innerHTML = `📄 <strong>${esc(f.name)}</strong> (${(f.size / 1024).toFixed(1)} KB)`;
                if (statusText) statusText.innerText = `Seçildi: ${f.name}. "Unlimited-OCR ile Oku & Denetle" butonuna basın.`;
            }
        });
    }

    if (btnDemo) {
        btnDemo.addEventListener("click", async () => {
            await startITPAudit(null, true);
        });
    }

    if (btnStart) {
        btnStart.addEventListener("click", async () => {
            const file = fileInput?.files?.[0];
            if (!file) {
                showToast("Lütfen önce bir ITP PDF dokümanı seçin veya örnek doküman yükleyin.", "warning");
                return;
            }
            await startITPAudit(file, false);
        });
    }

    if (selStandard) {
        selStandard.addEventListener("change", () => {
            const gapAlert = document.getElementById("itp-botas-gap-alert");
            if (gapAlert) {
                if (selStandard.value === "BOTAŞ") {
                    gapAlert.classList.remove("hidden");
                } else {
                    gapAlert.classList.add("hidden");
                }
            }
        });
    }

    if (btnReAudit) {
        btnReAudit.addEventListener("click", async () => {
            if (!currentITPExtractedItems || currentITPExtractedItems.length === 0) {
                showToast("Önce bir ITP dokümanı yükleyin.", "warning");
                return;
            }
            const stdVal = document.getElementById("itp-override-standard")?.value || "BOTAŞ";
            const scopeVal = document.getElementById("itp-override-scope")?.value || "COMBINED";

            const updatedConfig = Object.assign({}, currentITPEffectiveConfig || {}, {
                standard_type: stdVal.startsWith("API") ? "API" : stdVal,
                psl_level: stdVal === "API_PSL1" ? "PSL1" : "PSL2",
                scope_mode: scopeVal
            });

            btnReAudit.disabled = true;
            try {
                const resp = await fetch("/api/itp/audit-manual", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        items: currentITPExtractedItems,
                        pipe_config: updatedConfig
                    })
                });
                const res = await resp.json();
                if (res.status === "success" && res.audit_result) {
                    currentITPAuditResult = res.audit_result;
                    currentITPEffectiveConfig = updatedConfig;
                    renderITPAuditResult(res.audit_result);
                    showToast(`Denetim '${stdVal}' standardı ve '${scopeVal}' kapsamına göre güncellendi!`, "success");
                }
            } catch (err) {
                showToast("Yeniden denetim hatası: " + err.message, "error");
            } finally {
                btnReAudit.disabled = false;
            }
        });
    }

    if (btnAddPipe) {
        btnAddPipe.addEventListener("click", () => {
            if (!currentITPEffectiveConfig) {
                showToast("Algılanan boru parametresi bulunamadı.", "warning");
                return;
            }
            const newPipe = {
                diameter_mm: currentITPEffectiveConfig.diameter_mm || 1219.0,
                diameter_inch: currentITPEffectiveConfig.diameter_inch || '48"',
                wall_thickness_mm: currentITPEffectiveConfig.wall_thickness_mm || 14.30,
                material_grade: currentITPEffectiveConfig.material_grade || "X65",
                manufacturing_process: currentITPEffectiveConfig.manufacturing_process || "SAWH",
                psl_level: currentITPEffectiveConfig.psl_level || "PSL2",
                standard_type: currentITPEffectiveConfig.standard_type || "BOTAŞ",
                standard_code: currentITPEffectiveConfig.standard_type || "BOTAŞ",
                design_factor_str: "0.72 (Hat)",
                delivery_condition: "M"
            };

            if (!activeProject.pipes) activeProject.pipes = [];
            activeProject.pipes.push(newPipe);

            if (typeof renderProjectPipes === "function") renderProjectPipes();
            if (typeof updatePipeTabs === "function") updatePipeTabs();
            if (typeof renderITPPipeChips === "function") renderITPPipeChips();
            if (typeof updateITPTargetPipes === "function") updateITPTargetPipes();
            if (typeof ProjectStorage !== "undefined" && ProjectStorage.saveToLocalStorage) {
                ProjectStorage.saveToLocalStorage(activeProject);
            }

            showToast(`✓ '${newPipe.diameter_inch} x ${newPipe.wall_thickness_mm} mm ${newPipe.material_grade} ${newPipe.manufacturing_process}' projenize eklendi!`, "success");
        });
    }

    if (btnExportExcel) {
        btnExportExcel.addEventListener("click", async () => {
            if (!currentITPAuditResult) return;
            try {
                const resp = await fetch("/api/itp/export-audit-report", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        audit_result: currentITPAuditResult,
                        lang: localStorage.getItem("api5l_lang") || "tr"
                    })
                });
                if (!resp.ok) throw new Error("Excel raporu oluşturulamadı.");
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `ITP_Audit_Report_${Date.now()}.xlsx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                showToast("Excel ITP Sapma Raporu başarıyla indirildi!", "success");
            } catch (err) {
                console.error("Export error:", err);
                showToast("Rapor indirme hatası: " + err.message, "error");
            }
        });
    }

    if (btnExportPdf) {
        btnExportPdf.addEventListener("click", async () => {
            if (!currentITPAuditResult) return;
            const originalText = btnExportPdf.innerHTML;
            btnExportPdf.disabled = true;
            btnExportPdf.innerHTML = `<span>⏳ PDF Hazırlanıyor...</span>`;
            try {
                const payload = Object.assign({}, currentITPAuditResult, {
                    customer: currentITPDetectedMeta?.customer || (currentITPEffectiveConfig?.standard_type === 'BOTAŞ' ? 'BOTAŞ' : 'Genel Müşteri'),
                    project_name: currentITPDetectedMeta?.project_name || 'Doğalgaz Boru Hattı Projesi',
                    source_filename: currentITPDetectedMeta?.source_filename || 'İmalatçı ITP Dokümanı'
                });

                const resp = await fetch("/api/itp/export-audit-pdf", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        audit_result: payload,
                        lang: localStorage.getItem("api5l_lang") || "tr"
                    })
                });
                if (!resp.ok) throw new Error("PDF raporu oluşturulamadı.");
                const blob = await resp.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `ITP_Audit_Report_${Date.now()}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                showToast("✓ PDF ITP Denetim Raporu başarıyla indirildi!", "success");
            } catch (err) {
                console.error("PDF Export error:", err);
                showToast("PDF Rapor indirme hatası: " + err.message, "error");
            } finally {
                btnExportPdf.disabled = false;
                btnExportPdf.innerHTML = originalText;
            }
        });
    }

    updateITPTargetPipes();
}

function updateITPTargetPipes() {
    const select = document.getElementById("itp-target-pipe-select");
    if (!select) return;
    select.innerHTML = "";

    if (!activeProject.pipes || activeProject.pipes.length === 0) {
        const opt = document.createElement("option");
        opt.value = "default";
        opt.text = '48" (1219.0 mm) x 14.30 mm - X65 PSL2 SAWH (Varsayılan Referans)';
        select.appendChild(opt);
        return;
    }

    activeProject.pipes.forEach((p, idx) => {
        const opt = document.createElement("option");
        opt.value = idx;
        const dStr = p.diameter_inch || `${p.diameter_mm} mm`;
        const tStr = p.wall_thickness_mm ? `${p.wall_thickness_mm} mm` : "";
        const gStr = p.material_grade || "X65";
        const pStr = p.manufacturing_process || "SAWH";
        const pslStr = p.psl_level || "PSL2";
        opt.text = `${idx + 1}. Boru: ${dStr} x ${tStr} | ${gStr} ${pslStr} ${pStr}`;
        if (idx === selectedPipeIndex) opt.selected = true;
        select.appendChild(opt);
    });
}

function renderITPAlignmentPanel(meta, effectiveConfig) {
    const panel = document.getElementById("itp-alignment-panel");
    if (!panel || !meta) return;

    panel.classList.remove("hidden");

    const elConf = document.getElementById("itp-det-conf-badge");
    const elCust = document.getElementById("itp-det-customer-badge");
    const elProj = document.getElementById("itp-det-project-name");
    const elStd = document.getElementById("itp-det-standard-label");
    const elScope = document.getElementById("itp-det-scope-label");
    const elPipe = document.getElementById("itp-det-pipe-label");
    const selStd = document.getElementById("itp-override-standard");
    const selScope = document.getElementById("itp-override-scope");

    if (elConf) elConf.innerText = `%${meta.confidence_score || 95} Güven`;
    if (elCust) elCust.innerText = `Müşteri: ${meta.customer || 'BOTAŞ'}`;
    if (elProj) elProj.innerText = meta.project_name || 'BOTAŞ Doğalgaz Boru Hattı Projesi';
    if (elStd) elStd.innerText = meta.detected_standard_label || meta.detected_standard || 'BOTAŞ';
    if (elScope) elScope.innerText = meta.detected_scope_label || meta.detected_scope_mode || 'Bütünsel';

    const dStr = meta.detected_diameter_inch || `${meta.detected_diameter_mm} mm`;
    const tStr = meta.detected_wall_thickness_mm ? `${meta.detected_wall_thickness_mm} mm` : '';
    const gStr = meta.detected_grade || 'X65';
    const pStr = meta.detected_process || 'SAWH';
    const pslStr = meta.detected_psl || 'PSL2';
    if (elPipe) elPipe.innerText = `${dStr} (${meta.detected_diameter_mm || ''} mm) x ${tStr} | ${gStr} ${pslStr} ${pStr}`;

    if (selStd && effectiveConfig) {
        if (effectiveConfig.standard_type === 'BOTAŞ') selStd.value = 'BOTAŞ';
        else if (effectiveConfig.psl_level === 'PSL1') selStd.value = 'API_PSL1';
        else selStd.value = 'API';
    }
    if (selScope && effectiveConfig) {
        selScope.value = effectiveConfig.scope_mode || 'COMBINED';
    }
}

async function startITPAudit(file = null, useDemo = false) {
    const statusText = document.getElementById("itp-upload-status-text");
    const btnStart = document.getElementById("btn-start-itp-audit");
    const select = document.getElementById("itp-target-pipe-select");

    let pipeConfig = {
        diameter_mm: 1219.0,
        diameter_inch: '48"',
        wall_thickness_mm: 14.30,
        material_grade: "X65",
        manufacturing_process: "SAWH",
        psl_level: "PSL2",
        standard_type: "API"
    };

    if (activeProject.pipes && activeProject.pipes.length > 0) {
        const pipeIdx = parseInt(select?.value || "0");
        pipeConfig = activeProject.pipes[isNaN(pipeIdx) ? 0 : pipeIdx] || pipeConfig;
    }

    if (statusText) statusText.innerText = "⏳ Unlimited-OCR dokümanı okuyor ve tabloları analiz ediyor...";
    if (btnStart) btnStart.disabled = true;

    try {
        const formData = new FormData();
        if (file) formData.append("file", file);
        formData.append("use_demo", useDemo ? "true" : "false");
        formData.append("pipe_config_json", JSON.stringify(pipeConfig));

        const resp = await fetch("/api/itp/upload-and-audit", {
            method: "POST",
            body: formData
        });
        const res = await resp.json();

        if (res.status === "success" || res.status === "warning") {
            currentITPAuditResult = res.audit_result;
            currentITPExtractedItems = res.extracted_items || [];
            currentITPDetectedMeta = res.detected_metadata || null;
            currentITPEffectiveConfig = res.effective_config || pipeConfig;
            currentITPVariantAudits = res.variant_audits || [];
            currentITPScopeVariants = res.scope_variants || (res.detected_metadata?.scope_variants || []);

            renderITPAlignmentPanel(res.detected_metadata, res.effective_config);
            renderITPVariantTabs(currentITPVariantAudits, currentITPScopeVariants);
            renderITPAuditResult(res.audit_result);

            // Persist latest audit in browser LocalStorage (R3 Solution)
            try {
                localStorage.setItem("api5l_latest_itp_audit", JSON.stringify({
                    source: res.source || "ITP Document",
                    timestamp: new Date().toISOString(),
                    detected_metadata: res.detected_metadata,
                    effective_config: res.effective_config,
                    audit_result: res.audit_result
                }));
            } catch (e) {
                console.warn("LocalStorage save error for ITP audit:", e);
            }

            if (res.is_fallback) {
                if (statusText) statusText.innerHTML = `<span class="text-amber-600 font-semibold">${res.warning_message}</span>`;
                showToast(res.warning_message || "Referans ITP şablonu yüklendi.", "warning");
            } else {
                if (statusText) statusText.innerText = `✓ Denetim tamamlandı (${res.source || "ITP"}).`;
                showToast("ITP dokümanı başarıyla okundu ve denetlendi!", "success");
            }
        } else {
            throw new Error(res.message || "Denetim başarısız oldu.");
        }
    } catch (err) {
        console.error("ITP Audit error:", err);
        if (statusText) statusText.innerText = "❌ Hata: " + err.message;
        showToast("ITP Denetim hatası: " + err.message, "error");
    } finally {
        if (btnStart) btnStart.disabled = false;
    }
}

function renderITPVariantTabs(variantAudits, scopeVariants) {
    const container = document.getElementById("itp-variant-tabs");
    const buttonsDiv = document.getElementById("itp-variant-buttons");
    const countSpan = document.getElementById("itp-variant-count");
    if (!container || !buttonsDiv) return;
    if (!variantAudits || variantAudits.length <= 1) {
        container.classList.add("hidden");
        return;
    }
    container.classList.remove("hidden");
    if (countSpan) countSpan.innerText = `${variantAudits.length} varyant`;
    buttonsDiv.innerHTML = "";
    variantAudits.forEach((va, idx) => {
        const cfg = va.pipe_config || {};
        const label = `${cfg.diameter_inch || cfg.diameter_mm} × ${cfg.wall_thickness_mm} mm`;
        const isActive = idx === 0;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = isActive ? "px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-600 text-white shadow" : "px-2.5 py-1 rounded-full text-xs font-semibold bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-100";
        btn.innerText = label;
        btn.onclick = () => switchITPVariant(idx);
        buttonsDiv.appendChild(btn);
    });
}

function switchITPVariant(idx) {
    if (!currentITPVariantAudits || !currentITPVariantAudits[idx]) return;
    const va = currentITPVariantAudits[idx];
    currentITPAuditResult = va.audit_result;
    // Update active styling
    const buttonsDiv = document.getElementById("itp-variant-buttons");
    if (buttonsDiv) {
        Array.from(buttonsDiv.children).forEach((b, i) => {
            b.className = i === idx ? "px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-600 text-white shadow" : "px-2.5 py-1 rounded-full text-xs font-semibold bg-white border border-indigo-200 text-indigo-700 hover:bg-indigo-100";
        });
    }
    renderITPAuditResult(va.audit_result);
    showToast(`Varyant ${idx+1}: ${va.pipe_config.diameter_inch} × ${va.pipe_config.wall_thickness_mm} mm denetimi gösteriliyor`, "info");
}

function renderITPAuditResult(auditData) {
    if (!auditData) return;
    const kpi = auditData.kpi || {};
    const rows = auditData.audit_rows || [];

    // KPI Cards
    const elTotal = document.getElementById("itp-kpi-total");
    const elPass = document.getElementById("itp-kpi-pass");
    const elMore = document.getElementById("itp-kpi-more");
    const elFail = document.getElementById("itp-kpi-fail");
    const elScore = document.getElementById("itp-score-percent");
    const elBar = document.getElementById("itp-score-bar");
    const elVerdict = document.getElementById("itp-verdict-badge");
    const btnExcel = document.getElementById("btn-export-itp-excel");

    if (elTotal) elTotal.innerText = kpi.total_tests_audited || rows.length;
    if (elPass) elPass.innerText = kpi.compliant_count || 0;
    if (elMore) elMore.innerText = kpi.more_stringent_count || 0;
    if (elFail) elFail.innerText = kpi.non_compliant_count || 0;
    
    const score = kpi.compliance_score_percent !== undefined ? kpi.compliance_score_percent : 100.0;
    if (elScore) elScore.innerText = `%${score.toFixed(1)}`;
    if (elBar) elBar.style.width = `${score}%`;

    if (elVerdict) {
        if (kpi.non_compliant_count > 0) {
            elVerdict.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200";
            elVerdict.innerText = `⚠ ${kpi.non_compliant_count} Sapma Tespit Edildi (Revizyon Gerekli)`;
        } else if (kpi.more_stringent_count > 0) {
            elVerdict.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200";
            elVerdict.innerText = "✓ Şartnameye Uygun (Üstün Taahhütler Var)";
        } else {
            elVerdict.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200";
            elVerdict.innerText = "✓ Tam Uyumlu (%100 Standart Uyumu)";
        }
    }

    if (btnExcel) btnExcel.disabled = false;
    const btnPdf = document.getElementById("btn-export-itp-pdf");
    if (btnPdf) btnPdf.disabled = false;

    renderITPAuditTable(rows);
}

function renderITPAuditTable(rows) {
    const tbody = document.getElementById("itp-audit-table-body");
    const countLabel = document.getElementById("itp-table-count-label");
    if (!tbody) return;

    let filteredRows = rows;
    if (currentITPFilter && currentITPFilter !== "ALL") {
        filteredRows = rows.filter(r => r.status === currentITPFilter);
    }

    if (countLabel) {
        countLabel.innerText = `Gösterilen: ${filteredRows.length} / ${rows.length} test maddesi`;
    }

    if (filteredRows.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-8 text-slate-400 text-xs">
                    Bu filtreleme kriterine uygun test maddesi bulunamadı.
                </td>
            </tr>`;
        return;
    }

    let html = "";
    filteredRows.forEach((row, i) => {
        const st = row.status || "COMPLIANT";
        let badgeHtml = "";
        let rowBg = i % 2 === 0 ? "bg-white" : "bg-slate-50/50";

        if (st === "NON_COMPLIANT") {
            badgeHtml = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-200">🔴 Uyumsuz / Hata</span>`;
            rowBg = "bg-rose-50/40";
        } else if (st === "MORE_STRINGENT") {
            badgeHtml = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">🟡 Daha Sıkı</span>`;
            rowBg = "bg-amber-50/30";
        } else {
            badgeHtml = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 Uyumlu</span>`;
        }

        html += `
            <tr class="${rowBg} hover:bg-indigo-50/30 transition">
                <td class="py-2.5 px-3 align-top border-b border-slate-100">
                    <span class="font-bold text-slate-900 block">${esc(row.test_name)}</span>
                    <span class="text-[10px] text-slate-500 font-semibold">${esc(row.category || "Muayene")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-indigo-950 bg-indigo-50/40 border-x border-indigo-100/60 font-bold">
                    <span class="block leading-snug text-indigo-900">${esc(row.calculated_target || "—")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-blue-950 bg-blue-50/30">
                    <span class="font-semibold text-[11px] block text-blue-900">${esc(row.ndt_method_standard || "—")}</span>
                    ${row.ndt_acceptance_level ? `<span class="text-[10px] text-blue-700 block mt-0.5">${esc(row.ndt_acceptance_level)}</span>` : ""}
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-slate-700">
                    <span class="font-semibold block">${esc(row.uploaded_frequency || "—")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-slate-800 bg-slate-50/50 font-semibold">
                    <span class="block">${esc(row.standard_frequency || "—")}</span>
                    <span class="text-[10px] text-slate-500 font-normal block mt-0.5">${esc(row.table_ref || "")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-slate-700">
                    <span class="font-semibold block">${esc(row.uploaded_criteria || "—")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100 text-blue-950 bg-blue-50/20 font-semibold">
                    <span class="block leading-snug">${esc(row.standard_criteria || "—")}</span>
                </td>
                <td class="py-2.5 px-3 align-top border-b border-slate-100">
                    <div class="mb-1">${badgeHtml}</div>
                    <p class="text-[11px] leading-snug font-normal ${st === 'NON_COMPLIANT' ? 'text-rose-900 font-semibold' : 'text-slate-600'}">${esc(row.audit_remarks || "")}</p>
                    <span class="text-[10px] text-slate-400 block mt-1 font-mono">${esc(row.clause_ref || "")}</span>
                </td>
            </tr>`;
    });

    tbody.innerHTML = html;
}

function filterITPTable(filterType) {
    currentITPFilter = filterType;

    const btnAll = document.getElementById("filter-btn-all");
    const btnFail = document.getElementById("filter-btn-fail");
    const btnMore = document.getElementById("filter-btn-more");
    const btnPass = document.getElementById("filter-btn-pass");

    const btns = [
        { el: btnAll, active: filterType === "ALL", cls: "bg-slate-800 text-white" },
        { el: btnFail, active: filterType === "NON_COMPLIANT", cls: "bg-rose-700 text-white" },
        { el: btnMore, active: filterType === "MORE_STRINGENT", cls: "bg-amber-700 text-white" },
        { el: btnPass, active: filterType === "COMPLIANT", cls: "bg-emerald-700 text-white" }
    ];

    btns.forEach(b => {
        if (!b.el) return;
        if (b.active) {
            b.el.className = `px-2 py-0.5 rounded-md font-bold text-[11px] shadow ${b.cls}`;
        } else {
            b.el.className = "px-2 py-0.5 rounded-md font-semibold text-[11px] text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200";
        }
    });

    if (currentITPAuditResult && currentITPAuditResult.audit_rows) {
        renderITPAuditTable(currentITPAuditResult.audit_rows);
    }
}

function loadSavedITPAuditFromStorage() {
    try {
        const saved = localStorage.getItem("api5l_latest_itp_audit");
        if (saved) {
            const data = JSON.parse(saved);
            if (data && data.audit_result) {
                currentITPAuditResult = data.audit_result;
                currentITPDetectedMeta = data.detected_metadata || null;
                currentITPEffectiveConfig = data.effective_config || null;
                if (data.detected_metadata) {
                    renderITPAlignmentPanel(data.detected_metadata, data.effective_config);
                }
                renderITPAuditResult(data.audit_result);
                const statusText = document.getElementById("itp-upload-status-text");
                if (statusText) statusText.innerText = `📁 Kayıtlı denetim yüklendi (${data.source || "ITP"}).`;
            }
        }
    } catch (e) {
        console.warn("Could not load saved ITP audit from localStorage:", e);
    }
}

