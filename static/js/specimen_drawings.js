/**
 * API 5L Specimen Schematic Drawings (SVG).
 * Simplified engineering schematics closely modeled on API 5L 47th Ed.
 * Figures 4/5/6 and standard specimen shapes (Charpy, tensile, guided-bend,
 * flattening, DWTT, hardness). Rendered inline — works offline and prints.
 */
const SPECIMEN_DRAWINGS = {
    // ------------------------------------------------------------------
    // Figure 5/6 style: sample & test piece locations on the pipe
    // ------------------------------------------------------------------
    sampling_location: () => `
    <svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[300px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <defs>
        <marker id="sd-arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <!-- Pipe barrel (longitudinal section) -->
      <rect x="30" y="70" width="580" height="90" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <!-- Wall thickness -->
      <rect x="30" y="70" width="580" height="30" fill="#cbd5e1" stroke="#334155" stroke-width="1"/>
      <!-- Weld seam (helical) -->
      <path d="M 150 70 L 110 160 M 400 70 L 360 160" stroke="#d97706" stroke-width="6" opacity="0.7"/>

      <!-- Body transverse sample (pipe body) -->
      <rect x="220" y="70" width="44" height="90" fill="none" stroke="#ef4444" stroke-width="2"/>
      <rect x="220" y="88" width="44" height="26" fill="#fee2e2" stroke="#ef4444" stroke-width="1.5"/>
      <text x="242" y="184" text-anchor="middle" class="sd-lbl" fill="#b91c1c">Gövde (enine)</text>
      <line x1="242" y1="168" x2="242" y2="163" stroke="#ef4444" stroke-width="1"/>

      <!-- Weld sample (seam) -->
      <circle cx="360" cy="115" r="16" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
      <text x="360" y="120" text-anchor="middle" class="sd-txt" fill="#92400e" font-size="9">K</text>
      <text x="360" y="150" text-anchor="middle" class="sd-lbl" fill="#b45309">Kaynak</text>

      <!-- HAZ sample -->
      <circle cx="405" cy="115" r="13" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
      <text x="405" y="120" text-anchor="middle" class="sd-txt" fill="#92400e" font-size="8">H</text>
      <text x="405" y="150" text-anchor="middle" class="sd-lbl" fill="#b45309">ITAB</text>

      <!-- Dimension: wall thickness -->
      <line x1="600" y1="70" x2="600" y2="160" class="sd-dim"/>
      <line x1="596" y1="70" x2="604" y2="70" class="sd-dim"/>
      <line x1="596" y1="160" x2="604" y2="160" class="sd-dim"/>
      <text x="607" y="118" class="sd-dimtxt">t</text>

      <!-- Dimension: OD -->
      <line x1="30" y1="200" x2="610" y2="200" class="sd-dim" marker-start="url(#sd-arr)" marker-end="url(#sd-arr)"/>
      <text x="320" y="214" text-anchor="middle" class="sd-dimtxt">Boru Dış Çapı (OD)</text>

      <!-- Labels -->
      <text x="320" y="30" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">API 5L Şekil 5/6 — Numune ve Test Parçası Yönleri/Yerleri</text>
      <text x="320" y="48" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">Gövde (enine/boyuna) • Kaynak merkez hattı • ITAB</text>
    </svg>`,

    // ------------------------------------------------------------------
    // Charpy V-notch specimen (10 x 10 x 55 mm) — Table 22
    // ------------------------------------------------------------------
    charpy: () => `
    <svg viewBox="0 0 640 320" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[320px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <defs>
        <marker id="sd-arr2" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <!-- Side elevation -->
      <g transform="translate(20,40)">
        <rect x="40" y="40" width="520" height="50" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <!-- V-notch at mid-length -->
        <path d="M 285 40 L 300 68 L 315 40 Z" fill="#fff" stroke="#334155" stroke-width="1.5"/>
        <text x="300" y="80" text-anchor="middle" class="sd-txt" font-weight="bold">45°</text>
        <!-- length dimension -->
        <line x1="40" y1="110" x2="560" y2="110" class="sd-dim" marker-start="url(#sd-arr2)" marker-end="url(#sd-arr2)"/>
        <text x="300" y="128" text-anchor="middle" class="sd-dimtxt">L = 55 mm</text>
        <!-- height dimension -->
        <line x1="575" y1="40" x2="575" y2="90" class="sd-dim"/>
        <text x="580" y="70" class="sd-dimtxt">10</text>
        <text x="40" y="24" class="sd-lbl">Yan Görünüş</text>
      </g>

      <!-- Cross-section (10 x 10 with notch) -->
      <g transform="translate(20,180)">
        <rect x="40" y="40" width="110" height="110" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <path d="M 95 40 L 95 68 M 95 68 L 112 92 M 78 92 L 95 68" fill="#fff" stroke="#334155" stroke-width="1.5"/>
        <text x="95" y="24" text-anchor="middle" class="sd-lbl">Kesit</text>
        <!-- 10x10 dimensions -->
        <line x1="40" y1="170" x2="150" y2="170" class="sd-dim" marker-start="url(#sd-arr2)" marker-end="url(#sd-arr2)"/>
        <text x="95" y="188" text-anchor="middle" class="sd-dimtxt">10 mm</text>
        <line x1="170" y1="40" x2="170" y2="150" class="sd-dim"/>
        <text x="175" y="98" class="sd-dimtxt">10 mm</text>
        <!-- notch depth -->
        <line x1="185" y1="40" x2="185" y2="68" class="sd-dim"/>
        <text x="192" y="56" class="sd-dimtxt">2 mm</text>
      </g>

      <!-- Sub-size variants (Table 22) -->
      <g transform="translate(360,180)">
        <text x="0" y="16" class="sd-lbl">Alt Boyutlar (Çizelge 22)</text>
        <g transform="translate(0,30)">
          <rect x="0" y="0" width="120" height="20" fill="#e2e8f0" stroke="#334155"/>
          <text x="128" y="14" class="sd-txt">Tam boy 10×10</text>
        </g>
        <g transform="translate(0,60)">
          <rect x="0" y="0" width="120" height="15" fill="#e2e8f0" stroke="#334155"/>
          <text x="128" y="11" class="sd-txt">3/4 — 7,5×10</text>
        </g>
        <g transform="translate(0,86)">
          <rect x="0" y="0" width="120" height="13" fill="#e2e8f0" stroke="#334155"/>
          <text x="128" y="10" class="sd-txt">2/3 — 6,67×10</text>
        </g>
        <g transform="translate(0,110)">
          <rect x="0" y="0" width="120" height="10" fill="#e2e8f0" stroke="#334155"/>
          <text x="128" y="9" class="sd-txt">1/2 — 5×10</text>
        </g>
      </g>
    </svg>`,

    // ------------------------------------------------------------------
    // Tensile strip specimen (38.1 mm wide, full wall thickness)
    // API 5L 10.2.3.2.1 — rectangular test piece, full wall, ISO 6892-1 / ASTM A370
    // ------------------------------------------------------------------
    tensile_strip: () => `
    <svg viewBox="0 0 640 250" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[250px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <defs>
        <marker id="sd-arr3" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <!-- Parallel-sided full-wall strip (top view: length x width) -->
      <rect x="50" y="66" width="540" height="64" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <!-- gauge section -->
      <rect x="270" y="66" width="120" height="64" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,3"/>
      <line x1="270" y1="58" x2="270" y2="138" class="sd-line" stroke="#3b82f6" stroke-width="1.5"/>
      <line x1="390" y1="58" x2="390" y2="138" class="sd-line" stroke="#3b82f6" stroke-width="1.5"/>
      <!-- gauge length dimension -->
      <line x1="270" y1="152" x2="390" y2="152" class="sd-dim" marker-start="url(#sd-arr3)" marker-end="url(#sd-arr3)"/>
      <text x="330" y="170" text-anchor="middle" class="sd-dimtxt">Mastar Boyu L0 = 50 mm</text>
      <!-- width dimension (across the strip) -->
      <line x1="606" y1="66" x2="606" y2="130" class="sd-dim"/>
      <line x1="600" y1="66" x2="612" y2="66" class="sd-dim"/>
      <line x1="600" y1="130" x2="612" y2="130" class="sd-dim"/>
      <text x="612" y="102" class="sd-dimtxt">38,1 mm</text>
      <!-- grip labels -->
      <text x="150" y="102" text-anchor="middle" class="sd-lbl" fill="#475569">Tutma</text>
      <text x="510" y="102" text-anchor="middle" class="sd-lbl" fill="#475569">Tutma</text>
      <!-- end view (thickness) inset -->
      <g transform="translate(420,180)">
        <text x="0" y="12" class="sd-lbl">Uç görünümü (tam cidar)</text>
        <rect x="0" y="22" width="46" height="16" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <line x1="54" y1="22" x2="54" y2="38" class="sd-dim"/>
        <text x="60" y="34" class="sd-dimtxt">t</text>
        <line x1="-6" y1="46" x2="52" y2="46" class="sd-dim" marker-start="url(#sd-arr3)" marker-end="url(#sd-arr3)"/>
        <text x="23" y="60" text-anchor="middle" class="sd-dimtxt">38,1 mm</text>
      </g>
      <!-- caption -->
      <text x="320" y="24" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Çekme Şerit Numunesi — Dikdörtgen, tam cidar (API 5L 10.2.3.2.1)</text>
      <text x="320" y="44" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">ISO 6892-1 / ASTM A370 — genişlik 38,1 mm x t (et kalınlığı); uzama 50 mm esası</text>
    </svg>`,

    // ------------------------------------------------------------------
    // Tensile round-bar specimen — API 5L 10.2.3.2.5 / Table 21 (6.4 / 8.9 / 12.7 mm)
    // ------------------------------------------------------------------
    tensile_round: () => `
    <svg viewBox="0 0 640 240" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[240px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <defs>
        <marker id="sd-arr4" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <!-- Left threaded grip -->
      <rect x="40" y="70" width="110" height="60" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <!-- left shoulder -->
      <path d="M 150 70 L 172 85 L 172 115 L 150 130 Z" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
      <!-- gauge (single reduced cylinder) -->
      <rect x="172" y="85" width="156" height="30" fill="#fef3c7" stroke="#b45309" stroke-width="2"/>
      <!-- right shoulder -->
      <path d="M 328 85 L 350 70 L 350 130 L 328 115 Z" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
      <!-- right threaded grip -->
      <rect x="350" y="70" width="210" height="60" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>

      <!-- thread ticks -->
      <g stroke="#64748b" stroke-width="1.5">
        <line x1="58" y1="72" x2="58" y2="128"/><line x1="74" y1="72" x2="74" y2="128"/>
        <line x1="90" y1="72" x2="90" y2="128"/><line x1="106" y1="72" x2="106" y2="128"/>
        <line x1="122" y1="72" x2="122" y2="128"/><line x1="138" y1="72" x2="138" y2="128"/>
        <line x1="372" y1="72" x2="372" y2="128"/><line x1="392" y1="72" x2="392" y2="128"/>
        <line x1="412" y1="72" x2="412" y2="128"/><line x1="432" y1="72" x2="432" y2="128"/>
        <line x1="452" y1="72" x2="452" y2="128"/><line x1="472" y1="72" x2="472" y2="128"/>
        <line x1="492" y1="72" x2="492" y2="128"/><line x1="512" y1="72" x2="512" y2="128"/>
        <line x1="532" y1="72" x2="532" y2="128"/><line x1="552" y1="72" x2="552" y2="128"/>
      </g>

      <!-- gauge diameter dimension -->
      <line x1="250" y1="85" x2="250" y2="82" class="sd-dim"/>
      <line x1="248" y1="82" x2="252" y2="82" class="sd-dim"/>
      <line x1="252" y1="82" x2="272" y2="82" class="sd-dim" marker-end="url(#sd-arr4)"/>
      <text x="280" y="79" class="sd-dimtxt">d = 6,4 / 8,9 / 12,7 mm (Çizelge 21)</text>

      <!-- gauge length dimension -->
      <line x1="172" y1="158" x2="328" y2="158" class="sd-dim" marker-start="url(#sd-arr4)" marker-end="url(#sd-arr4)"/>
      <text x="250" y="176" text-anchor="middle" class="sd-dimtxt">Mastar Boyu L0 = 50 mm</text>

      <!-- labels -->
      <text x="95" y="100" text-anchor="middle" class="sd-lbl" fill="#475569">Dişli uç</text>
      <text x="250" y="132" text-anchor="middle" class="sd-lbl" fill="#b45309">Mastar (gauge)</text>
      <text x="505" y="100" text-anchor="middle" class="sd-lbl" fill="#475569">Dişli uç</text>

      <!-- caption -->
      <text x="320" y="26" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Yuvarlak Çubuk Çekme Numunesi (API 5L 10.2.3.2.5 / Tablo 21)</text>
      <text x="320" y="46" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">ISO 6892-1 / ASTM A370 — çap Tablo 21'e göre; uzama 50 mm esası</text>
    </svg>`,

    // ------------------------------------------------------------------
    // Guided-bend test — API 5L Şekil 9 (test aparatları) + Şekil 8 (numune parçaları)
    // Orijinal standard şekilleri static/img altından çevrimdışı gösterilir.
    // ------------------------------------------------------------------
    guided_bend: () => `
    <div class="space-y-3">
      <div class="border border-slate-200 rounded bg-white p-2">
        <div class="text-[11px] font-bold text-slate-700 mb-1">API 5L Şekil 9 — Kılavuzlu Bükme Test Aparatları (plunger tip)</div>
        <img src="/static/img/fig9_guided_bend_jigs.png" alt="API 5L Şekil 9 — Jigs for Guided-bend Test" class="w-full h-auto" />
        <div class="text-[10px] text-slate-500 mt-1">B = Agb + 2t + 3,2 mm • ra: mandrel yarıçapı • rb: kalıp yarıçapı (API 5L 10.2.4.6.2 / ISO 5173, ASTM A370)</div>
      </div>
      <div class="border border-slate-200 rounded bg-white p-2">
        <div class="text-[11px] font-bold text-slate-700 mb-1">API 5L Şekil 8 — Kılavuzlu Bükme Numune Parçaları (kök/kapak bükme)</div>
        <img src="/static/img/fig8_guided_bend_pieces.png" alt="API 5L Şekil 8 — Guided-bend Test Pieces" class="w-full h-auto" />
        <div class="text-[10px] text-slate-500 mt-1">a) SAW/COW • b) LW (D ≥ 323,9 mm) • c/d) indirgenmiş kalınlık (t &gt; 19,0 mm) — kök bükme: kaynak dış yüzeyde, kapak bükme: kaynak iç yüzeyde</div>
      </div>
    </div>`,

    // ------------------------------------------------------------------
    // Flattening test (ring between plates) — H distance
    // ------------------------------------------------------------------
    flattening: () => `
    <svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[260px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <!-- top plate -->
      <rect x="40" y="50" width="560" height="18" fill="#94a3b8" stroke="#334155" stroke-width="2"/>
      <!-- bottom plate -->
      <rect x="40" y="180" width="560" height="18" fill="#94a3b8" stroke="#334155" stroke-width="2"/>
      <!-- flattened ring (ellipse = deformed pipe ring) -->
      <ellipse cx="320" cy="124" rx="150" ry="46" fill="none" stroke="#ef4444" stroke-width="8"/>
      <ellipse cx="320" cy="124" rx="130" ry="34" fill="none" stroke="#fca5a5" stroke-width="3"/>
      <!-- weld mark on ring -->
      <rect x="312" y="70" width="16" height="14" fill="#b91c1c"/>
      <!-- H dimension between plates -->
      <line x1="500" y1="68" x2="500" y2="180" class="sd-dim"/>
      <line x1="496" y1="68" x2="504" y2="68" class="sd-dim"/>
      <line x1="496" y1="180" x2="504" y2="180" class="sd-dim"/>
      <text x="508" y="128" class="sd-dimtxt">H</text>
      <!-- load arrows -->
      <text x="320" y="30" text-anchor="middle" class="sd-lbl" fill="#b91c1c">▼ Yük (F)</text>
      <text x="320" y="226" text-anchor="middle" class="sd-lbl" fill="#b91c1c">▲ Yük (F)</text>
      <text x="320" y="248" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">Plakalar arası mesafe H — kaynak belirtilen mesafeye ulaşmadan çatlamamalı</text>
    </svg>`,

    // ------------------------------------------------------------------
    // Residual Stress Ring Test (BOTAŞ Madde 3.3.9) — 150 mm ring cut +
    // slit at the point opposite the weld + ring springing open (gap Δ).
    // Animated SVG; dimensions driven by the selected pipe.
    // ------------------------------------------------------------------
    residual_stress_ring: (pd) => {
        const d = (pd && pd.input_summary && pd.input_summary.diameter_mm) || 1219.0;
        const dInch = (pd && pd.input_summary && pd.input_summary.diameter_inch) || '48"';
        const t = (pd && pd.input_summary && pd.input_summary.wall_thickness_mm) || 14.30;
        const delta = (pd && pd.toughness_and_tests && typeof pd.toughness_and_tests.residual_stress_max_mm === 'number')
            ? pd.toughness_and_tests.residual_stress_max_mm : 3.5;
        return `
    <svg viewBox="0 0 640 360" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[360px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
        .rs-half-l{transform-origin:460px 265px;animation:rsOpenL 8s linear infinite}
        .rs-half-r{transform-origin:460px 265px;animation:rsOpenR 8s linear infinite}
        .rs-ring-piece{animation:rsSeparate 8s linear infinite}
        .rs-torch{animation:rsTorch 8s linear infinite}
        .rs-spark{animation:rsSpark 8s linear infinite}
        .rs-slit{animation:rsFadeIn 8s linear infinite}
        .rs-gapdim{animation:rsGapDim 8s linear infinite}
        .rs-step{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;fill:#475569}
        @keyframes rsOpenL{0%,48%{transform:rotate(0deg)}72%,100%{transform:rotate(-11deg)}}
        @keyframes rsOpenR{0%,48%{transform:rotate(0deg)}72%,100%{transform:rotate(11deg)}}
        @keyframes rsSeparate{0%,32%{transform:translateX(0)}44%,100%{transform:translateX(32px)}}
        @keyframes rsTorch{0%{transform:translateY(-26px);opacity:0}8%{opacity:1}30%{transform:translateY(20px);opacity:1}38%,100%{transform:translateY(20px);opacity:0}}
        @keyframes rsSpark{0%,6%{opacity:0}12%,28%{opacity:1}32%,100%{opacity:0}}
        @keyframes rsFadeIn{0%,52%{opacity:0}64%,100%{opacity:1}}
        @keyframes rsGapDim{0%,58%{opacity:0}78%,100%{opacity:1}}
      </style>
      <defs>
        <marker id="rs-arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <!-- ============ A) Side view: 150 mm ring cut from pipe end ============ -->
      <text x="20" y="26" class="sd-txt" font-weight="bold" font-size="12">A) Boru Ucu — 150 mm Halka Kesimi</text>
      <!-- pipe body remaining after cut -->
      <rect x="190" y="120" width="125" height="70" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <line x1="190" y1="120" x2="315" y2="120" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="190" y1="190" x2="315" y2="190" stroke="#cbd5e1" stroke-width="1"/>
      <!-- cut line -->
      <line x1="183" y1="112" x2="183" y2="198" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,3"/>
      <!-- cutting torch moving along the cut -->
      <g class="rs-torch">
        <path d="M 183 138 L 176 130 L 190 130 Z" fill="#ef4444"/>
        <rect x="178" y="120" width="10" height="10" fill="#94a3b8" stroke="#334155" stroke-width="1"/>
        <line x1="183" y1="118" x2="183" y2="106" stroke="#475569" stroke-width="2"/>
      </g>
      <!-- sparks -->
      <g class="rs-spark" fill="#f59e0b">
        <circle cx="176" cy="132" r="2.4"/>
        <circle cx="192" cy="128" r="2"/>
        <circle cx="169" cy="140" r="1.8"/>
      </g>
      <g class="rs-spark" fill="#fbbf24" style="animation-delay:.15s">
        <circle cx="200" cy="134" r="2.2"/>
        <circle cx="172" cy="124" r="1.8"/>
      </g>
      <!-- ring piece cut off (150 mm wide) -->
      <g class="rs-ring-piece">
        <rect x="32" y="120" width="148" height="70" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
        <line x1="70" y1="120" x2="70" y2="190" stroke="#94a3b8" stroke-width="1"/>
        <line x1="110" y1="120" x2="110" y2="190" stroke="#94a3b8" stroke-width="1"/>
        <line x1="150" y1="120" x2="150" y2="190" stroke="#94a3b8" stroke-width="1"/>
      </g>
      <!-- ring width dimension -->
      <line x1="32" y1="208" x2="180" y2="208" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
      <line x1="32" y1="202" x2="32" y2="214" class="sd-dim"/>
      <line x1="180" y1="202" x2="180" y2="214" class="sd-dim"/>
      <text x="106" y="224" text-anchor="middle" class="sd-dimtxt">150 mm</text>
      <!-- wall thickness callout -->
      <line x1="240" y1="120" x2="240" y2="190" class="sd-dim"/>
      <line x1="236" y1="120" x2="244" y2="120" class="sd-dim"/>
      <line x1="236" y1="190" x2="244" y2="190" class="sd-dim"/>
      <text x="246" y="158" class="sd-dimtxt">t = ${t.toFixed(2)} mm</text>
      <text x="106" y="102" text-anchor="middle" class="sd-lbl" fill="#b91c1c">Kesme ocağı (plazma/oksijen)</text>

      <!-- ============ B) Top view: slit + ring opening (Δ) ============ -->
      <text x="330" y="26" class="sd-txt" font-weight="bold" font-size="12">B) Halka Üst Görünüşü — Çentik &amp; Açılma (Δ)</text>
      <!-- right half (rotates clockwise) -->
      <g class="rs-half-r">
        <path d="M 460 95 A 85 85 0 1 1 460 265 L 460 235 A 55 55 0 1 1 460 125 Z" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
        <!-- spiral weld seam symbol (SAWH) -->
        <path d="M 514 150 A 70 70 0 0 1 484 130" fill="none" stroke="#d97706" stroke-width="7" opacity="0.85"/>
      </g>
      <!-- left half (rotates counter-clockwise) -->
      <g class="rs-half-l">
        <path d="M 460 95 A 85 85 0 1 0 460 265 L 460 235 A 55 55 0 1 0 460 125 Z" fill="#e2e8f0" stroke="#334155" stroke-width="1.5"/>
      </g>
      <!-- slit cut at the point opposite the weld (top) -->
      <g class="rs-slit">
        <line x1="460" y1="95" x2="460" y2="72" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="4,3"/>
        <text x="460" y="62" text-anchor="middle" class="sd-lbl" fill="#b91c1c">Çentik (kaynak karşısı)</text>
      </g>
      <!-- gap dimension (Δ) shown after the ring springs open -->
      <g class="rs-gapdim">
        <line x1="413" y1="96" x2="507" y2="96" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
        <line x1="413" y1="92" x2="413" y2="100" class="sd-dim"/>
        <line x1="507" y1="92" x2="507" y2="100" class="sd-dim"/>
        <text x="460" y="88" text-anchor="middle" class="sd-dimtxt">Δ ≤ ${delta.toFixed(2)} mm</text>
      </g>
      <!-- OD dimension -->
      <line x1="375" y1="292" x2="545" y2="292" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
      <line x1="375" y1="285" x2="375" y2="299" class="sd-dim"/>
      <line x1="545" y1="285" x2="545" y2="299" class="sd-dim"/>
      <text x="460" y="310" text-anchor="middle" class="sd-dimtxt">OD (D) = ${d.toFixed(1)} mm (${dInch})</text>
      <text x="398" y="150" class="sd-lbl" fill="#b45309">spiral kaynak dikişi</text>

      <!-- ============ Steps & acceptance caption ============ -->
      <line x1="20" y1="326" x2="620" y2="326" stroke="#cbd5e1" stroke-width="1"/>
      <text x="20" y="344" class="rs-step">1) Boru ucundan 150 mm halka kesilir • 2) Kaynağın karşısından tek noktadan çentilir • 3) Halka kendiliğinden açılır, Δ ölçülür</text>
      <text x="20" y="358" class="sd-dimtxt">Kabul: S = (E·t·Δ) / (12.566·Dₘ²) ≤ %10 SMYS, Dₘ = D - t (BOTAŞ Madde 3.3.9) • Δ ≤ ${delta.toFixed(2)} mm</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // DWTT specimen (full-thickness, press-notch)
    // ------------------------------------------------------------------
    dwtt: () => `
    <svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[260px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <g transform="translate(60,40)">
        <!-- specimen plate -->
        <rect x="0" y="60" width="500" height="90" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <!-- press notch -->
        <path d="M 250 60 L 262 96 L 274 60 Z" fill="#fff" stroke="#334155" stroke-width="1.5"/>
        <!-- drop weight -->
        <rect x="210" y="0" width="110" height="34" fill="#94a3b8" stroke="#334155" stroke-width="2"/>
        <text x="265" y="22" text-anchor="middle" class="sd-txt" fill="#1e293b" font-weight="bold" font-size="10">Ağırlık</text>
        <line x1="265" y1="34" x2="265" y2="58" stroke="#475569" stroke-width="2" stroke-dasharray="4,3"/>
        <path d="M 230 58 L 300 58" stroke="#475569" stroke-width="2"/>
        <text x="262" y="120" text-anchor="middle" class="sd-lbl" fill="#b91c1c">Press-notch</text>
        <!-- length dim -->
        <line x1="0" y1="172" x2="500" y2="172" class="sd-dim"/>
        <text x="250" y="190" text-anchor="middle" class="sd-dimtxt">Numune uzunluğu (örn. 305 mm)</text>
        <!-- thickness dim -->
        <line x1="516" y1="60" x2="516" y2="150" class="sd-dim"/>
        <text x="521" y="110" class="sd-dimtxt">t (tam cidar)</text>
        <text x="250" y="210" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">Kırılma yüzeyi sünek alan oranı değerlendirilir</text>
      </g>
      <text x="340" y="26" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">DWTT Numunesi (API 5L 9.9)</text>
    </svg>`,

    // ------------------------------------------------------------------
    // Hardness indentation positions (body / weld / HAZ)
    // ------------------------------------------------------------------
    hardness: () => `
    <svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[260px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <!-- pipe wall cross-section -->
      <g transform="translate(60,50)">
        <!-- weld reinforcement -->
        <path d="M 300 40 L 320 70 L 340 40 Z" fill="#fbbf24" stroke="#b45309" stroke-width="2"/>
        <!-- weld seam / body -->
        <rect x="300" y="70" width="40" height="90" fill="#fde68a" stroke="#334155" stroke-width="1.5"/>
        <rect x="0" y="70" width="300" height="90" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <rect x="340" y="70" width="300" height="90" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <!-- hardness indentation marks -->
        <g fill="#ef4444">
          <circle cx="80" cy="115" r="5"/><circle cx="130" cy="115" r="5"/>
          <circle cx="285" cy="115" r="5"/><circle cx="320" cy="115" r="5"/>
          <circle cx="355" cy="115" r="5"/><circle cx="500" cy="115" r="5"/><circle cx="560" cy="115" r="5"/>
        </g>
        <!-- labels -->
        <text x="130" y="196" text-anchor="middle" class="sd-lbl" fill="#1e3a8a">Gövde</text>
        <text x="320" y="196" text-anchor="middle" class="sd-lbl" fill="#b45309">Kaynak + ITAB</text>
        <text x="560" y="196" text-anchor="middle" class="sd-lbl" fill="#1e3a8a">Gövde</text>
        <!-- HV marks -->
        <text x="320" y="28" text-anchor="middle" class="sd-lbl" fill="#b91c1c">HV10 / HV5 izleri (gövde-kaynak-ITAB)</text>
        <text x="320" y="48" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">ISO 6506 / ISO 6507 / ISO 6508 / ASTM A370</text>
      </g>
    </svg>`,
};

/**
 * Returns the SVG string for a specimen figure key, or empty string if unknown.
 * Optional pipeData (calculated pipe result) drives dimension-specific figures.
 */
function getSpecimenDrawing(key, pipeData) {
    const fn = SPECIMEN_DRAWINGS[key];
    return fn ? fn(pipeData) : "";
}