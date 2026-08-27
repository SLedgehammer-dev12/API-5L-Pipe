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
    // Guided-bend test (root & cap) — mandrel + die
    // ------------------------------------------------------------------
    guided_bend: () => `
    <svg viewBox="0 0 640 260" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[260px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
      </style>
      <g transform="translate(40,30)">
        <!-- die rollers -->
        <circle cx="80" cy="170" r="34" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
        <circle cx="300" cy="170" r="34" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
        <circle cx="80" cy="170" r="6" fill="#475569"/>
        <circle cx="300" cy="170" r="6" fill="#475569"/>
        <!-- mandrel -->
        <circle cx="170" cy="150" r="36" fill="#fbbf24" stroke="#b45309" stroke-width="2.5"/>
        <circle cx="170" cy="150" r="8" fill="#92400e"/>
        <!-- bent specimen wrapped around mandrel -->
        <path d="M 46 172 A 34 34 0 0 1 108 148 L 170 120 L 210 130 L 252 148 A 34 34 0 0 1 314 172"
              fill="none" stroke="#ef4444" stroke-width="9" stroke-linecap="round"/>
        <!-- weld position marks -->
        <rect x="164" y="112" width="12" height="14" fill="#b91c1c"/>
        <text x="170" y="104" text-anchor="middle" class="sd-lbl" fill="#b91c1c">Kaynak (kök/kapak)</text>
        <!-- labels -->
        <text x="170" y="230" text-anchor="middle" class="sd-lbl">Mandrel Çapı (ra)</text>
        <text x="80" y="225" text-anchor="middle" class="sd-lbl" fill="#475569">Çene / Kalıp</text>
        <text x="300" y="225" text-anchor="middle" class="sd-lbl" fill="#475569">Çene / Kalıp</text>
        <!-- mandrel radius dim -->
        <line x1="170" y1="150" x2="205" y2="132" class="sd-dim"/>
        <text x="212" y="128" class="sd-dimtxt">ra</text>
      </g>
      <text x="320" y="24" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Kılavuzlu Bükme Testi (API 5L 9.7 / ISO 5173)</text>
      <text x="320" y="48" text-anchor="middle" class="sd-txt" fill="#64748b" font-size="10">Kök bükme: kaynak dış (gerilme) yüzeyde • Kapak bükme: kaynak iç yüzeyde</text>
    </svg>`,

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
 */
function getSpecimenDrawing(key) {
    const fn = SPECIMEN_DRAWINGS[key];
    return fn ? fn() : "";
}