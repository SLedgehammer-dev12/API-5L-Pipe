/**
 * API 5L Specimen Schematic Drawings (SVG).
 * Simplified engineering schematics closely modeled on API 5L 47th Ed.
 * Figures 4/5/6 and standard specimen shapes (Charpy, tensile, guided-bend,
 * flattening, DWTT, hardness). Rendered inline — works offline and prints.
 */
// ----------------------------------------------------------------------
// Table 21 (API 5L 47th Ed.) — transverse round-bar test-piece diameter.
// Thresholds mirror core/pipe_qaqc_engine.py::_TABLE21_ROUNDBAR (keep in sync).
// ----------------------------------------------------------------------
const RS_TABLE21_ROUNDBAR = [
    [219.1, null, 28.1], [273.1, 36.1, 25.5], [323.9, 33.5, 23.9], [355.6, 32.3, 23.2],
    [406.4, 30.9, 22.2], [457.0, 29.7, 21.5], [508.0, 28.8, 21.0], [559.0, 28.1, 20.5],
    [610.0, 27.5, 20.1], [660.0, 27.0, 19.8], [711.0, 26.5, 19.5], [762.0, 26.2, 19.3],
    [813.0, 25.8, 19.1], [864.0, 25.5, 18.9], [914.0, 25.3, 18.7], [965.0, 25.1, 18.6],
    [1016.0, 24.9, 18.5], [1067.0, 24.7, 18.3], [1118.0, 24.5, 18.2], [1168.0, 24.4, 18.1],
    [1219.0, 24.2, 18.1], [1321.0, 24.0, 17.9], [1422.0, 23.8, 17.8], [1524.0, 23.6, 17.6],
    [1626.0, 23.4, 17.5], [1727.0, 23.3, 17.4], [1829.0, 23.1, 17.4], [1930.0, 23.0, 17.3],
    [Infinity, 22.9, 17.2]
];
function rsRoundBarDia(dMm, tMm) {
    const d = parseFloat(dMm) || 1219.0;
    const t = parseFloat(tMm) || 14.3;
    for (const [dMax, t12, t89] of RS_TABLE21_ROUNDBAR) {
        if (d <= dMax) {
            if (t12 !== null && t >= t12) return 12.7;
            if (t89 !== null && t >= t89) return 8.9;
            return 6.4;
        }
    }
    return 6.4;
}

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
    // Charpy V-notch specimen (10 × 10 × 55 mm) — API 5L 9.8 / Table 22
    // Orthographic views + magnified notch detail + 40 mm anvil span.
    // Selected sub-size (Table 22) highlighted from the pipe's CVN size.
    // ------------------------------------------------------------------
    // ------------------------------------------------------------------
    // Charpy V-notch specimen (10 × 10 × 55 mm) — API 5L 9.8 / Table 22
    // Photorealistic 2.5D orthographic views + optical comparator notch detail + 40 mm anvil span.
    // ------------------------------------------------------------------
    charpy: (pd) => {
        const tt = (pd && pd.toughness_and_tests) || {};
        const sizeLabel = String(tt.notch_specimen_size || '');
        const cvnReq = tt.cvn_required !== false;
        const sel = sizeLabel.includes('10 x 10') ? 'full'
            : (sizeLabel.includes('7.5') ? '34'
            : (sizeLabel.includes('6.67') ? '23'
            : (sizeLabel.includes('5 x 10') ? '12' : 'full')));
        const hlFill = (k) => (!cvnReq ? 'url(#cvn-steel-flat)' : (sel === k ? 'url(#cvn-sel-grad)' : 'url(#cvn-sub-grad)'));
        const hlStroke = (k) => (cvnReq && sel === k ? '#b45309' : '#475569');
        const hlW = (k) => (cvnReq && sel === k ? 2.5 : 1.2);
        const tag = (k, y) => (cvnReq && sel === k
            ? `<text x="404" y="${y}" text-anchor="end" class="sd-note" fill="#b45309" font-weight="700">seçili ▶</text>` : '');

        return `
    <svg viewBox="0 0 640 430" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[430px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#2563eb;stroke-width:1.2;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;fill:#1d4ed8}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#475569}
      </style>
      <defs>
        <marker id="sd-arr-cvn" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#2563eb"/>
        </marker>
        <filter id="sd-drop-shadow" x="-5%" y="-5%" width="115%" height="120%">
          <feDropShadow dx="2" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.18"/>
        </filter>
        <!-- Steel ground finish gradient -->
        <linearGradient id="cvn-steel-bar" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f8fafc"/>
          <stop offset="15%" stop-color="#e2e8f0"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="85%" stop-color="#94a3b8"/>
          <stop offset="100%" stop-color="#64748b"/>
        </linearGradient>
        <linearGradient id="cvn-steel-end" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f1f5f9"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="100%" stop-color="#94a3b8"/>
        </linearGradient>
        <linearGradient id="cvn-anvil-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#334155"/><stop offset="50%" stop-color="#64748b"/><stop offset="100%" stop-color="#1e293b"/>
        </linearGradient>
        <linearGradient id="cvn-sel-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#fef3c7"/><stop offset="100%" stop-color="#fde68a"/>
        </linearGradient>
        <linearGradient id="cvn-sub-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#f1f5f9"/><stop offset="100%" stop-color="#e2e8f0"/>
        </linearGradient>
      </defs>

      <!-- Title Header -->
      <rect x="12" y="6" width="616" height="26" rx="4" fill="#f8fafc" stroke="#e2e8f0"/>
      <text x="320" y="23" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12" fill="#0f172a">
        Charpy V-Çentik Numunesi — API 5L 9.8 / Çizelge 22 (ISO 148-1 / ASTM A370)
      </text>

      <!-- ============ A) Side Elevation ============ -->
      <text x="24" y="52" class="sd-lbl">A) Yan Görünüş (55 × 10 mm) • Taşlanmış Yüzey</text>
      <!-- Specimen Bar with Shadow -->
      <g filter="url(#sd-drop-shadow)">
        <rect x="40" y="70" width="302" height="55" rx="1.5" fill="url(#cvn-steel-bar)" stroke="#334155" stroke-width="1.8"/>
        <!-- Bevel highlights -->
        <line x1="41" y1="71" x2="341" y2="71" stroke="#ffffff" stroke-width="1" opacity="0.85"/>
        <line x1="41" y1="124" x2="341" y2="124" stroke="#475569" stroke-width="1" opacity="0.6"/>
        <!-- Notch cut (45 deg, 2mm deep) -->
        <path d="M 185 70 L 191 82 L 197 70 Z" fill="#ffffff" stroke="#334155" stroke-width="1.4"/>
        <path d="M 185 70 L 191 82 L 197 70" fill="none" stroke="#b45309" stroke-width="1.6"/>
        <circle cx="191" cy="82" r="1.5" fill="#f59e0b" stroke="#b45309" stroke-width="0.8"/>
      </g>
      <!-- 45 deg callout -->
      <text x="191" y="62" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="10" fill="#b45309">45° V-Çentik</text>
      <line x1="206" y1="70" x2="206" y2="82" class="sd-dim"/>
      <text x="210" y="79" class="sd-dimtxt">2,0 mm</text>
      <line x1="222" y1="82" x2="222" y2="125" class="sd-dim"/>
      <line x1="218" y1="82" x2="226" y2="82" class="sd-dim"/>
      <line x1="218" y1="125" x2="226" y2="125" class="sd-dim"/>
      <text x="228" y="106" class="sd-dimtxt">8,0 mm</text>
      <!-- Root radius pointer -->
      <line x1="189" y1="83" x2="162" y2="105" stroke="#2563eb" stroke-width="1.2"/>
      <circle cx="162" cy="105" r="2" fill="#2563eb"/>
      <text x="158" y="118" text-anchor="end" class="sd-dimtxt">r = 0,25 ± 0,025 mm</text>
      <!-- Total Length L=55mm -->
      <line x1="40" y1="145" x2="342" y2="145" class="sd-dim" marker-start="url(#sd-arr-cvn)" marker-end="url(#sd-arr-cvn)"/>
      <line x1="40" y1="139" x2="40" y2="151" class="sd-dim"/>
      <line x1="342" y1="139" x2="342" y2="151" class="sd-dim"/>
      <text x="191" y="163" text-anchor="middle" class="sd-dimtxt">L = 55,0 ± 0,60 mm</text>
      <!-- Height 10mm -->
      <line x1="358" y1="70" x2="358" y2="125" class="sd-dim"/>
      <line x1="352" y1="70" x2="364" y2="70" class="sd-dim"/>
      <line x1="352" y1="125" x2="364" y2="125" class="sd-dim"/>
      <text x="366" y="102" class="sd-dimtxt">10,0 mm</text>
      <text x="191" y="190" text-anchor="middle" class="sd-note">V-çentik: 45° ± 1° dahil açı • Derinlik: 2,00 ± 0,05 mm • Kök: r = 0,25 mm</text>

      <!-- ============ B) End Section & Optical Reticle ============ -->
      <text x="24" y="226" class="sd-lbl">B) Kesit (10 × 10) ve Optik Komparatör Detayı (25×)</text>
      <g filter="url(#sd-drop-shadow)">
        <rect x="50" y="244" width="60" height="60" rx="1" fill="url(#cvn-steel-end)" stroke="#334155" stroke-width="1.8"/>
        <path d="M 74 244 L 80 256 L 86 244 Z" fill="#ffffff" stroke="#b45309" stroke-width="1.4"/>
      </g>
      <line x1="118" y1="244" x2="118" y2="304" class="sd-dim"/>
      <line x1="114" y1="244" x2="122" y2="244" class="sd-dim"/>
      <line x1="114" y1="304" x2="122" y2="304" class="sd-dim"/>
      <text x="126" y="278" class="sd-dimtxt">10 mm</text>
      <line x1="50" y1="316" x2="110" y2="316" class="sd-dim" marker-start="url(#sd-arr-cvn)" marker-end="url(#sd-arr-cvn)"/>
      <text x="80" y="330" text-anchor="middle" class="sd-dimtxt">10 mm</text>

      <!-- Optical Reticle / Magnifier -->
      <g transform="translate(236, 282)">
        <circle cx="0" cy="0" r="48" fill="#f8fafc" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="5,3"/>
        <circle cx="0" cy="0" r="45" fill="none" stroke="#cbd5e1" stroke-width="0.8"/>
        <!-- Reticle Crosshair -->
        <line x1="-42" y1="0" x2="42" y2="0" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2"/>
        <line x1="0" y1="-42" x2="0" y2="42" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2"/>
        <!-- Precision notch profile magnified -->
        <path d="M -26 -28 L 0 20 L 26 -28" fill="none" stroke="#b45309" stroke-width="2.6" stroke-linejoin="round"/>
        <!-- Root radius arc -->
        <path d="M -5 10 Q 0 22 5 10" fill="none" stroke="#2563eb" stroke-width="2"/>
        <text x="0" y="-32" text-anchor="middle" class="sd-note" font-weight="bold" fill="#1e3a8a">25× Optik Şablon</text>
        <text x="12" y="-10" class="sd-dimtxt" font-size="9px">45°</text>
        <text x="8" y="32" class="sd-dimtxt" font-size="9px">r = 0,25 mm</text>
      </g>

      <!-- ============ D) Sub-size Variants (Table 22) ============ -->
      <text x="380" y="52" class="sd-lbl">D) Alt Boyutlar (Çizelge 22)</text>
      <g filter="url(#sd-drop-shadow)">
        <rect x="410" y="64" width="120" height="27" rx="2" fill="${hlFill('full')}" stroke="${hlStroke('full')}" stroke-width="${hlW('full')}"/>
        <rect x="410" y="104" width="120" height="20" rx="2" fill="${hlFill('34')}" stroke="${hlStroke('34')}" stroke-width="${hlW('34')}"/>
        <rect x="410" y="138" width="120" height="18" rx="2" fill="${hlFill('23')}" stroke="${hlStroke('23')}" stroke-width="${hlW('23')}"/>
        <rect x="410" y="170" width="120" height="14" rx="2" fill="${hlFill('12')}" stroke="${hlStroke('12')}" stroke-width="${hlW('12')}"/>
      </g>
      <text x="538" y="82" class="sd-note" font-size="10.5px" font-weight="600">Tam boy 10 × 10 × 55</text>
      ${tag('full', 82)}
      <text x="538" y="118" class="sd-note" font-size="10.5px">3/4 boy 7,5 × 10 × 55</text>
      ${tag('34', 118)}
      <text x="538" y="151" class="sd-note" font-size="10.5px">2/3 boy 6,67 × 10 × 55</text>
      ${tag('23', 151)}
      <text x="538" y="181" class="sd-note" font-size="10.5px">1/2 boy 5 × 10 × 55</text>
      ${tag('12', 181)}
      <text x="380" y="206" class="sd-note">Alt boyutta enerji oranı: 9.8.1.1</text>
      <text x="380" y="220" class="sd-note">Tek değer ≥ ortalamanın %75'i (9.8.1.2)</text>
      ${cvnReq ? '' : '<text x="380" y="238" class="sd-note" fill="#b45309" font-weight="700">PSL1: CVN zorunlu değil (Çizelge 17).</text>'}

      <!-- ============ C) Impact Rig (3-Point Bending) ============ -->
      <text x="380" y="258" class="sd-lbl">C) Darbe Test Düzeni (3 Nokta Eğilme)</text>
      <!-- Striker tup hammer -->
      <path d="M 452 268 L 478 268 L 465 292 Z" fill="#ef4444" stroke="#991b1b" stroke-width="1.2"/>
      <line x1="465" y1="258" x2="465" y2="268" stroke="#ef4444" stroke-width="2"/>
      <text x="484" y="278" class="sd-note" font-weight="bold" fill="#b91c1c">Vurucu (Sarkaç)</text>
      <!-- Specimen bar on anvils -->
      <rect x="402" y="294" width="126" height="14" rx="1" fill="url(#cvn-steel-bar)" stroke="#334155" stroke-width="1.2"/>
      <path d="M 461 308 L 465 301 L 469 308 Z" fill="#ffffff" stroke="#b45309" stroke-width="1"/>
      <!-- Hardened Anvils -->
      <rect x="398" y="308" width="24" height="16" rx="2" fill="url(#cvn-anvil-grad)" stroke="#1e293b" stroke-width="1"/>
      <rect x="506" y="308" width="24" height="16" rx="2" fill="url(#cvn-anvil-grad)" stroke="#1e293b" stroke-width="1"/>
      <text x="472" y="322" class="sd-note" fill="#b45309" font-size="9px">V-çentik</text>
      <!-- Anvil Span 40 mm -->
      <line x1="410" y1="334" x2="518" y2="334" class="sd-dim" marker-start="url(#sd-arr-cvn)" marker-end="url(#sd-arr-cvn)"/>
      <text x="464" y="347" text-anchor="middle" class="sd-dimtxt">40,0 ± 0,2 mm Örs Açıklığı</text>
      <text x="380" y="364" class="sd-note">Çentik, vurucunun zıt yüzünde (çekme gerilmesi tarafında) yer alır.</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="382" x2="624" y2="382" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="398" class="sd-note">Çentik, boru dış yüzeyine dik işlenir (API 5L 9.8.2) • Test sıcaklığı: 0 °C (Standart) / -20 °C (BOTAŞ Madde 3.3.4).</text>
      <text x="16" y="412" class="sd-note">Kaynak/ITAB numunelerinde çentik ekseni, kaynak merkez çizgisine veya füzyon hattına konumlandırılır.</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // GÖVDE Çekme Şerit Numunesi (38,1 mm × t, Dog-Bone) — ASTM A370 Şekil 3 / Şekil A2.1 & API 5L 10.2.3.2.1
    // Boru GÖVDESİNDEN (kaynaktan uzakta) alınır, bu sebeple üzerinde KAYNAK DİKİŞİ BULUNMAZ.
    // ------------------------------------------------------------------
    tensile_strip: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const isSmls = proc.includes('SMLS') || proc.includes('SEAMLESS') || proc.includes('DIKISSIZ') || proc.includes('DİKİŞSİZ');
        const tStr = t.toFixed(2);
        const hpx = Math.max(16, Math.min(48, Math.round(t * 1.5)));

        return `
    <svg viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[400px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#2563eb;stroke-width:1.2;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;fill:#1d4ed8}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#475569}
      </style>
      <defs>
        <marker id="sd-arr-ts" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#2563eb"/>
        </marker>
        <filter id="sd-ts-shadow" x="-5%" y="-5%" width="115%" height="120%">
          <feDropShadow dx="2" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.18"/>
        </filter>
        <!-- Homogeneous brushed steel body -->
        <linearGradient id="ts-steel-body" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f8fafc"/>
          <stop offset="15%" stop-color="#e2e8f0"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="85%" stop-color="#94a3b8"/>
          <stop offset="100%" stop-color="#64748b"/>
        </linearGradient>
        <!-- Serrated clamp grip texture -->
        <pattern id="ts-knurl" width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M0,8 L8,0 M0,0 L8,8" stroke="#64748b" stroke-width="0.9" opacity="0.45"/>
        </pattern>
      </defs>

      <!-- Title Header -->
      <rect x="12" y="6" width="616" height="26" rx="4" fill="#f8fafc" stroke="#e2e8f0"/>
      <text x="320" y="23" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12" fill="#0f172a">
        Boru Gövdesi Çekme Şerit Numunesi — ASTM A370 Şekil 3 (Omuzlu / Köpek Kemiği) &amp; API 5L 10.2.3.2.1
      </text>

      <!-- ============ A) Plan View (Dog-Bone Specimen) ============ -->
      <text x="24" y="52" class="sd-lbl">A) Üst Görünüş: ASTM A370 İndirgenmiş Kesitli Şerit (Gövde Malzemesi — Kaynaksız)</text>

      <g filter="url(#sd-ts-shadow)">
        <!-- Dog-Bone Specimen Outline (Concave Fillet Radius R >= 25 mm) -->
        <!-- Grip Width = 72px (C ~ 50 mm), Gauge Width = 48px (W = 38.1 mm), Fillet R = 25 mm (İçbükey / Concave) -->
        <path d="M 50 62 
                 L 145 62 
                 Q 165 74, 185 74 
                 L 435 74 
                 Q 455 74, 475 62 
                 L 570 62 
                 L 570 134 
                 L 475 134 
                 Q 455 122, 435 122 
                 L 185 122 
                 Q 165 122, 145 134 
                 L 50 134 Z" 
              fill="url(#ts-steel-body)" stroke="#334155" stroke-width="1.8"/>

        <!-- Longitudinal rolled steel texture lines -->
        <line x1="185" y1="88" x2="435" y2="88" stroke="#94a3b8" stroke-width="0.9" stroke-dasharray="12,8" opacity="0.6"/>
        <line x1="185" y1="108" x2="435" y2="108" stroke="#94a3b8" stroke-width="0.9" stroke-dasharray="12,8" opacity="0.6"/>

        <!-- Knurled grip pads on widened ends -->
        <rect x="50" y="62" width="80" height="72" fill="#94a3b8" stroke="#334155" stroke-width="1"/>
        <rect x="50" y="62" width="80" height="72" fill="url(#ts-knurl)"/>
        <rect x="490" y="62" width="80" height="72" fill="#94a3b8" stroke="#334155" stroke-width="1"/>
        <rect x="490" y="62" width="80" height="72" fill="url(#ts-knurl)"/>
      </g>

      <!-- Grip Labels -->
      <text x="90" y="102" text-anchor="middle" class="sd-txt" font-weight="bold" fill="#0f172a">Çene (B ≥ 75)</text>
      <text x="530" y="102" text-anchor="middle" class="sd-txt" font-weight="bold" fill="#0f172a">Çene (B ≥ 75)</text>

      <!-- Fillet Radius Callout (R >= 25 mm - İçbükey / Concave) -->
      <path d="M 160 52 L 170 60 L 174 72" fill="none" stroke="#2563eb" stroke-width="1.2" marker-end="url(#sd-arr-ts)"/>
      <text x="165" y="48" class="sd-dimtxt">R ≥ 25 mm (İçbükey Omuz Radyüsü)</text>

      <!-- Gauge Marks & Gauge Length (G = 50.0 mm) -->
      <line x1="260" y1="66" x2="260" y2="130" stroke="#2563eb" stroke-width="1.6"/>
      <line x1="360" y1="66" x2="360" y2="130" stroke="#2563eb" stroke-width="1.6"/>
      <circle cx="260" cy="98" r="2.5" fill="#2563eb"/>
      <circle cx="360" cy="98" r="2.5" fill="#2563eb"/>

      <line x1="260" y1="150" x2="360" y2="150" class="sd-dim" marker-start="url(#sd-arr-ts)" marker-end="url(#sd-arr-ts)"/>
      <line x1="260" y1="144" x2="260" y2="156" class="sd-dim"/>
      <line x1="360" y1="144" x2="360" y2="156" class="sd-dim"/>
      <text x="310" y="164" text-anchor="middle" class="sd-dimtxt">G = 50,0 ± 0,10 mm (2,000 inç Ölçüm Mastarı)</text>

      <!-- Reduced Section Length (A >= 60 mm) -->
      <line x1="185" y1="172" x2="435" y2="172" class="sd-dim" marker-start="url(#sd-arr-ts)" marker-end="url(#sd-arr-ts)"/>
      <text x="310" y="184" text-anchor="middle" class="sd-dimtxt">A ≥ 60 mm (Paralel İndirgenmiş Bölge Boyu)</text>

      <!-- Reduced Width Dimension (W = 38.1 mm) -->
      <line x1="450" y1="74" x2="450" y2="122" class="sd-dim"/>
      <line x1="444" y1="74" x2="456" y2="74" class="sd-dim"/>
      <line x1="444" y1="122" x2="456" y2="122" class="sd-dim"/>
      <text x="460" y="102" class="sd-dimtxt">W = 38,1 ± 0,25 mm (1,50 in)</text>

      <!-- Grip Width Dimension (C ~ 50 mm) -->
      <line x1="582" y1="62" x2="582" y2="134" class="sd-dim"/>
      <line x1="576" y1="62" x2="588" y2="62" class="sd-dim"/>
      <line x1="576" y1="134" x2="588" y2="134" class="sd-dim"/>
      <text x="592" y="102" class="sd-dimtxt">C ≈ 50 mm</text>

      <!-- ============ B) End Section ============ -->
      <text x="24" y="214" class="sd-lbl">B) Uç Kesiti (38,1 × t mm)</text>
      <g filter="url(#sd-ts-shadow)">
        <rect x="50" y="228" width="120" height="${hpx}" rx="2" fill="url(#ts-steel-body)" stroke="#334155" stroke-width="1.8"/>
        <path d="M 50 228 Q 110 216 170 228" fill="none" stroke="#2563eb" stroke-width="1.2" stroke-dasharray="4,3"/>
      </g>
      <line x1="184" y1="228" x2="184" y2="${228 + hpx}" class="sd-dim"/>
      <line x1="178" y1="228" x2="190" y2="228" class="sd-dim"/>
      <line x1="178" y1="${228 + hpx}" x2="190" y2="${228 + hpx}" class="sd-dim"/>
      <text x="194" y="${228 + Math.round(hpx / 2) + 4}" class="sd-dimtxt">t = ${tStr} mm</text>
      <line x1="50" y1="${228 + hpx + 16}" x2="170" y2="${228 + hpx + 16}" class="sd-dim" marker-start="url(#sd-arr-ts)" marker-end="url(#sd-arr-ts)"/>
      <text x="110" y="${228 + hpx + 30}" text-anchor="middle" class="sd-dimtxt">W = 38,1 mm</text>

      <!-- ============ C) Extraction Inset ============ -->
      <text x="270" y="214" class="sd-lbl">C) Gövdeden Numune Alımı (Kaynak Dikişinden Uzakta)</text>
      <g transform="translate(460, 268)">
        <circle cx="0" cy="0" r="50" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <circle cx="0" cy="0" r="42" fill="#0f172a"/>
        <!-- Weld seam at top 12 o'clock -->
        <circle cx="0" cy="-46" r="3.5" fill="#d97706"/>
        <text x="0" y="-53" text-anchor="middle" class="sd-note" font-size="8.5px" fill="#b45309">kaynak dikişi (0°)</text>
        <!-- Body specimen at 90 deg / 180 deg in pipe wall -->
        <path d="M 40 -16 A 50 50 0 0 1 47.4 16 L 39.6 14 A 42 42 0 0 0 33.6 -13.5 Z"
              fill="#3b82f6" stroke="#1d4ed8" stroke-width="1.4"/>
        <text x="56" y="4" class="sd-dimtxt">gövde numunesi (90°)</text>
        <text x="0" y="68" text-anchor="middle" class="sd-note">Gövde mekanik testlerinde numune ana metalden alınır; dikiş içermez.</text>
      </g>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="360" x2="624" y2="360" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="376" class="sd-note">ASTM A370 Şekil 3 / Şekil A2.1: Gövde çekme numunesi paralel omuzlu (dog-bone) işlenir; akma (Rt0,5), çekme (Rm) ve uzama gövdeden belirlenir.</text>
      <text x="16" y="390" class="sd-note">Boru cidar eğriliği standart çene kavisleriyle kavranır; düzleştirme yalnızca soğuk deformasyon sınırlarında uygulanabilir.</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // GÖVDE Çekme Yuvarlak Çubuk Numunesi — ASTM A370 Şekil 4 / Şekil 5 & API 5L 10.2.3.2.5 / Tablo 21
    // Boru GÖVDESİNDEN (dikişsiz veya kaynaktan uzakta) cidar ortasından alınır; KAYNAK İÇERMEZ.
    // ------------------------------------------------------------------
    tensile_round: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const isSmls = proc.includes('SMLS') || proc.includes('SEAMLESS') || proc.includes('DIKISSIZ') || proc.includes('DİKİŞSİZ');
        const dBar = isSmls ? (t >= 19.0 ? 12.7 : 6.4) : rsRoundBarDia(s.diameter_mm || 1219.0, t);
        const dStr = dBar.toFixed(1);
        const barH = Math.round(dBar * 2.8);
        const gripH = Math.round(barH * 1.8);
        const cy = 100;
        const gTop = cy - Math.round(barH / 2);
        const gBot = cy + Math.round(barH / 2);
        const pTop = cy - Math.round(gripH / 2);
        const pBot = cy + Math.round(gripH / 2);
        const thk = Math.max(16, Math.min(48, Math.round(t * 1.5)));
        const barR = Math.max(4, Math.min(Math.round(dBar * 1.6), Math.round(thk / 2) - 1));

        return `
    <svg viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[400px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#2563eb;stroke-width:1.2;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;fill:#1d4ed8}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#475569}
      </style>
      <defs>
        <marker id="sd-arr-tr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#2563eb"/>
        </marker>
        <filter id="sd-tr-shadow" x="-5%" y="-5%" width="115%" height="120%">
          <feDropShadow dx="2" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.18"/>
        </filter>
        <linearGradient id="tr-cyl-body" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#cbd5e1"/>
          <stop offset="20%" stop-color="#f8fafc"/>
          <stop offset="50%" stop-color="#f1f5f9"/>
          <stop offset="80%" stop-color="#94a3b8"/>
          <stop offset="100%" stop-color="#475569"/>
        </linearGradient>
        <linearGradient id="tr-cyl-grip" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#94a3b8"/>
          <stop offset="25%" stop-color="#e2e8f0"/>
          <stop offset="60%" stop-color="#cbd5e1"/>
          <stop offset="100%" stop-color="#334155"/>
        </linearGradient>
        <pattern id="tr-thread" width="8" height="16" patternUnits="userSpaceOnUse">
          <line x1="0" y1="0" x2="8" y2="8" stroke="#334155" stroke-width="1.2"/>
          <line x1="0" y1="8" x2="8" y2="16" stroke="#ffffff" stroke-width="0.8" opacity="0.6"/>
        </pattern>
      </defs>

      <!-- Title Header -->
      <rect x="12" y="6" width="616" height="26" rx="4" fill="#f8fafc" stroke="#e2e8f0"/>
      <text x="320" y="23" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12" fill="#0f172a">
        Boru Gövdesi Yuvarlak Çubuk Çekme Numunesi — ASTM A370 Şekil 4/5 (Standart 0.500 in) &amp; API 5L Tablo 21
      </text>

      <!-- ============ A) Elevation View ============ -->
      <text x="24" y="52" class="sd-lbl">A) Görünüş: Dişli Uçlar + R Radyüslü Omuz + Silindirik Mastar (Gövde — Kaynaksız)</text>

      <g filter="url(#sd-tr-shadow)">
        <!-- Left Threaded Grip -->
        <rect x="40" y="${pTop}" width="95" height="${gripH}" rx="2" fill="url(#tr-cyl-grip)" stroke="#334155" stroke-width="1.8"/>
        <rect x="40" y="${pTop}" width="95" height="${gripH}" fill="url(#tr-thread)" opacity="0.35"/>

        <!-- Left Transition Shoulder (R >= 10 mm) -->
        <path d="M 135 ${pTop} C 152 ${pTop}, 152 ${gTop}, 165 ${gTop} L 165 ${gBot} C 152 ${gBot}, 152 ${pBot}, 135 ${pBot} Z"
              fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.8"/>

        <!-- Parallel Reduced Section (Pure Base Metal) -->
        <rect x="165" y="${gTop}" width="310" height="${barH}" fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.8"/>
        <line x1="165" y1="${cy - Math.round(barH / 4)}" x2="475" y2="${cy - Math.round(barH / 4)}" stroke="#ffffff" stroke-width="1.2" opacity="0.9"/>

        <!-- Right Transition Shoulder -->
        <path d="M 475 ${gTop} C 488 ${gTop}, 488 ${pTop}, 505 ${pTop} L 505 ${pBot} C 488 ${pBot}, 488 ${gBot}, 475 ${gBot} Z"
              fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.8"/>

        <!-- Right Threaded Grip -->
        <rect x="505" y="${pTop}" width="95" height="${gripH}" rx="2" fill="url(#tr-cyl-grip)" stroke="#334155" stroke-width="1.8"/>
        <rect x="505" y="${pTop}" width="95" height="${gripH}" fill="url(#tr-thread)" opacity="0.35"/>
      </g>

      <text x="320" y="${gTop - 12}" text-anchor="middle" class="sd-lbl" fill="#1e3a8a">Gövde Malzemesi (Torna Finişi Ra ≤ 0,8 µm — Kaynak Dikişsiz)</text>

      <!-- Gauge Diameter d Callout -->
      <line x1="205" y1="${gTop}" x2="205" y2="${gTop - 16}" class="sd-dim"/>
      <line x1="205" y1="${gBot}" x2="205" y2="${gBot + 16}" class="sd-dim"/>
      <text x="210" y="${gTop - 18}" class="sd-dimtxt">d = ${dStr} mm (Tablo 21)</text>

      <!-- Gauge Length Marks (G = 50.0 mm) -->
      <line x1="275" y1="${gTop - 6}" x2="275" y2="${gBot + 6}" stroke="#2563eb" stroke-width="1.6"/>
      <line x1="365" y1="${gTop - 6}" x2="365" y2="${gBot + 6}" stroke="#2563eb" stroke-width="1.6"/>
      <line x1="275" y1="${gBot + 24}" x2="365" y2="${gBot + 24}" class="sd-dim" marker-start="url(#sd-arr-tr)" marker-end="url(#sd-arr-tr)"/>
      <text x="320" y="${gBot + 38}" text-anchor="middle" class="sd-dimtxt">G = 50,0 ± 0,10 mm (veya 4d)</text>

      <!-- Thread labels -->
      <text x="87" y="${cy + 4}" text-anchor="middle" class="sd-txt" font-weight="bold" fill="#0f172a">Dişli Başlık</text>
      <text x="552" y="${cy + 4}" text-anchor="middle" class="sd-txt" font-weight="bold" fill="#0f172a">Dişli Başlık</text>

      <line x1="150" y1="${pBot}" x2="175" y2="${pBot + 14}" stroke="#2563eb" stroke-width="1.2"/>
      <text x="178" y="${pBot + 18}" class="sd-dimtxt">R ≥ 10 mm (Omuz Radyüsü)</text>

      <!-- ============ B) Wall Extraction Inset ============ -->
      <text x="24" y="218" class="sd-lbl">B) Boru Cidarından Çıkarma (d ≤ t Kriteri)</text>
      <g filter="url(#sd-tr-shadow)">
        <rect x="50" y="238" width="240" height="${thk}" rx="2" fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.8"/>
        <line x1="50" y1="${238 + Math.round(thk / 2)}" x2="290" y2="${238 + Math.round(thk / 2)}" stroke="#2563eb" stroke-width="1" stroke-dasharray="4,3"/>
        <circle cx="170" cy="${238 + Math.round(thk / 2)}" r="${barR}" fill="url(#tr-cyl-grip)" stroke="#b45309" stroke-width="2"/>
      </g>
      <text x="170" y="230" text-anchor="middle" class="sd-dimtxt">d = ${dStr} mm</text>
      <text x="298" y="${238 + Math.round(thk / 2) + 4}" class="sd-dimtxt">t = ${t.toFixed(2)} mm</text>
      <text x="170" y="${238 + thk + 18}" text-anchor="middle" class="sd-note">Gövde cidar ortasından (t/2) çıkarılır; d ≤ t sağlanır.</text>

      <!-- ============ C) Shoulder Detail ============ -->
      <text x="350" y="218" class="sd-lbl">C) Hassas Torna Geçiş Profili</text>
      <g filter="url(#sd-tr-shadow)" transform="translate(360, 240)">
        <rect x="0" y="0" width="60" height="60" rx="2" fill="url(#tr-cyl-grip)" stroke="#334155" stroke-width="1.5"/>
        <path d="M 60 0 C 80 0, 95 15, 95 30 L 95 30 C 95 45, 80 60, 60 60 Z"
              fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.5"/>
        <rect x="95" y="16" width="120" height="28" fill="url(#tr-cyl-body)" stroke="#334155" stroke-width="1.5"/>
      </g>
      <text x="490" y="274" class="sd-dimtxt">Mastar d = ${dStr} mm</text>
      <text x="440" y="322" class="sd-note">ASTM A370: R kavis geçişi gerilme yığılmasını önler.</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="358" x2="624" y2="358" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="374" class="sd-note">ASTM A370 Şekil 4 / Şekil 5: D = 12,7 mm (0.500 in) veya Çizelge 21 alt boyutları (8,9 mm / 6,4 mm); gövdeden alınır.</text>
      <text x="16" y="388" class="sd-note">SMLS borularda t ≥ 19,0 mm ise 12,7 mm boyuna yuvarlak çubuk testi zorunludur.</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // KAYNAK Çekme Testi Numunesi (Enine Kaynak) — ASTM A370 Şekil A2.3 & API 5L 10.2.3.3 / Çizelge 18 #6/#7
    // Kaynak dikişi tam ortada ENİNE yönde yer alır; kaynak bağlantısının çekme dayanımını (Rm) ölçer.
    // ------------------------------------------------------------------
    tensile_weld: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const tStr = t.toFixed(2);
        const hpx = Math.max(16, Math.min(48, Math.round(t * 1.5)));

        return `
    <svg viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[400px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#2563eb;stroke-width:1.2;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;fill:#1d4ed8}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#475569}
      </style>
      <defs>
        <marker id="sd-arr-tw" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#2563eb"/>
        </marker>
        <filter id="sd-tw-shadow" x="-5%" y="-5%" width="115%" height="120%">
          <feDropShadow dx="2" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.18"/>
        </filter>
        <linearGradient id="tw-steel-body" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f8fafc"/>
          <stop offset="20%" stop-color="#e2e8f0"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="80%" stop-color="#94a3b8"/>
          <stop offset="100%" stop-color="#64748b"/>
        </linearGradient>
        <linearGradient id="tw-weld-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#b45309"/>
          <stop offset="30%" stop-color="#f59e0b"/>
          <stop offset="50%" stop-color="#fde68a"/>
          <stop offset="70%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#b45309"/>
        </linearGradient>
        <linearGradient id="tw-haz-l" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#64748b" stop-opacity="0"/>
          <stop offset="40%" stop-color="#6366f1" stop-opacity="0.6"/>
          <stop offset="70%" stop-color="#d97706" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.95"/>
        </linearGradient>
        <linearGradient id="tw-haz-r" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.95"/>
          <stop offset="30%" stop-color="#d97706" stop-opacity="0.8"/>
          <stop offset="60%" stop-color="#6366f1" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#64748b" stop-opacity="0"/>
        </linearGradient>
        <pattern id="tw-knurl" width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M0,8 L8,0 M0,0 L8,8" stroke="#64748b" stroke-width="0.9" opacity="0.45"/>
        </pattern>
      </defs>

      <!-- Title Header -->
      <rect x="12" y="6" width="616" height="26" rx="4" fill="#f8fafc" stroke="#e2e8f0"/>
      <text x="320" y="23" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12" fill="#0f172a">
        Kaynak Çekme Testi Numunesi (Enine Kaynak) — ASTM A370 Şekil A2.3 &amp; API 5L 10.2.3.3
      </text>

      <!-- ============ A) Plan View (Transverse Weld Specimen) ============ -->
      <text x="24" y="52" class="sd-lbl">A) Üst Görünüş: Enine Kaynak Dikişi (Tam Ortada) + ITAB + Çekme Ekseni</text>

      <g filter="url(#sd-tw-shadow)">
        <!-- Specimen Strip -->
        <rect x="50" y="64" width="530" height="66" rx="2" fill="url(#tw-steel-body)" stroke="#334155" stroke-width="1.8"/>

        <!-- Knurled Grip Ends -->
        <rect x="50" y="64" width="85" height="66" fill="#94a3b8" stroke="#334155" stroke-width="1.2"/>
        <rect x="50" y="64" width="85" height="66" fill="url(#tw-knurl)"/>
        <rect x="495" y="64" width="85" height="66" fill="#94a3b8" stroke="#334155" stroke-width="1.2"/>
        <rect x="495" y="64" width="85" height="66" fill="url(#tw-knurl)"/>

        <!-- HAZ Heat-Affected Zone Bands (Enine Şerit Ortasında) -->
        <rect x="294" y="64" width="14" height="66" fill="url(#tw-haz-l)"/>
        <rect x="326" y="64" width="14" height="66" fill="url(#tw-haz-r)"/>

        <!-- Central Transverse Weld Seam (Enine Dikiş, Çekme Eksenine Dik) -->
        <rect x="306" y="64" width="22" height="66" fill="url(#tw-weld-grad)" stroke="#b45309" stroke-width="1.4"/>
        <!-- Multi-pass ripple scales running transversely across width -->
        <path d="M 306 72 Q 317 76 328 72 M 306 82 Q 317 86 328 82 M 306 92 Q 317 96 328 92 M 306 102 Q 317 106 328 102 M 306 112 Q 317 116 328 112 M 306 122 Q 317 126 328 122"
              stroke="#78350f" stroke-width="1.2" fill="none" opacity="0.8"/>
      </g>

      <!-- Tension Load Arrows -->
      <g stroke="#b91c1c" stroke-width="2.4" fill="#b91c1c">
        <!-- Left pull arrow -->
        <line x1="42" y1="97" x2="16" y2="97"/>
        <polygon points="16,93 16,101 8,97"/>
        <text x="24" y="86" class="sd-lbl" fill="#b91c1c" font-size="10px">◀ F</text>
        <!-- Right pull arrow -->
        <line x1="588" y1="97" x2="614" y2="97"/>
        <polygon points="614,93 614,101 622,97"/>
        <text x="600" y="86" class="sd-lbl" fill="#b91c1c" font-size="10px">F ▶</text>
      </g>

      <text x="317" y="58" text-anchor="middle" class="sd-lbl" fill="#b45309">Kaynak Dikişi (Enine / Transverse) + ITAB</text>

      <!-- Gauge / Weld Centerline -->
      <line x1="317" y1="60" x2="317" y2="138" stroke="#b45309" stroke-width="1.2" stroke-dasharray="4,3"/>
      <text x="317" y="152" text-anchor="middle" class="sd-dimtxt">Kaynak Merkez Hattı (Çekme Eksenine Dik)</text>

      <!-- Width 38.1 mm -->
      <line x1="592" y1="64" x2="592" y2="130" class="sd-dim"/>
      <text x="602" y="101" class="sd-dimtxt">W = 38,1 mm</text>

      <!-- Total Length ~ 250 mm -->
      <line x1="50" y1="168" x2="580" y2="168" class="sd-dim" marker-start="url(#sd-arr-tw)" marker-end="url(#sd-arr-tw)"/>
      <text x="315" y="182" text-anchor="middle" class="sd-dimtxt">Numune Boyu L ≈ 250 - 300 mm (Enine Alınmış Numune)</text>

      <!-- ============ B) End Section ============ -->
      <text x="24" y="214" class="sd-lbl">B) Uç Kesiti ve Taşlanmış Kaynak Yüzeyi</text>
      <g filter="url(#sd-tw-shadow)">
        <rect x="50" y="228" width="120" height="${hpx}" rx="2" fill="url(#tw-steel-body)" stroke="#334155" stroke-width="1.8"/>
        <!-- Weld flush machined indication -->
        <rect x="95" y="228" width="30" height="${hpx}" fill="url(#tw-weld-grad)" opacity="0.8" stroke="#b45309" stroke-width="1"/>
      </g>
      <line x1="184" y1="228" x2="184" y2="${228 + hpx}" class="sd-dim"/>
      <text x="194" y="${228 + Math.round(hpx / 2) + 4}" class="sd-dimtxt">t = ${tStr} mm</text>
      <text x="110" y="${228 + hpx + 24}" text-anchor="middle" class="sd-note">API 5L 10.2.3.3: Kaynak takviyesi ana metale kadar taşlanabilir.</text>

      <!-- ============ C) Extraction Inset ============ -->
      <text x="270" y="214" class="sd-lbl">C) Boru Kaynağından Enine Çıkarma Yönü</text>
      <g transform="translate(460, 268)">
        <circle cx="0" cy="0" r="50" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
        <circle cx="0" cy="0" r="42" fill="#0f172a"/>
        <!-- Weld seam at top -->
        <rect x="-4" y="-50" width="8" height="8" fill="#d97706"/>
        <!-- Transverse strip cutting across the weld -->
        <path d="M -18 -46.5 A 50 50 0 0 1 18 -46.5 L 15.5 -38.8 A 42 42 0 0 0 -15.5 -38.8 Z"
              fill="#f59e0b" stroke="#b45309" stroke-width="1.4"/>
        <text x="0" y="-55" text-anchor="middle" class="sd-note" font-size="8.5px" fill="#b45309">kaynak dikişi</text>
        <text x="36" y="-36" class="sd-dimtxt">enine kaynak numunesi</text>
        <text x="0" y="68" text-anchor="middle" class="sd-note">Numune kaynağa dik alınır; kaynak dikişi numunenin tam ortasından geçer.</text>
      </g>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="360" x2="624" y2="360" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="376" class="sd-note">API 5L 9.3.2 &amp; 10.2.3.3 / ASTM A370 Şekil A2.3: Kaynak dikişi enine çekme testinde yalnızca çekme dayanımı Rm belirlenir.</text>
      <text x="16" y="390" class="sd-note">Kabul şartı: Kaynak dikişi çekme dayanımı Rm, belirtilen minimum gövde çekme dayanımından (SMTS) az olamaz.</text>
    </svg>`;
    },

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
    // ------------------------------------------------------------------
    // Flattening test (ring between plates) — API 5L 10.2.4.3 & BOTAŞ 3.3.3
    // Dynamic 2D SVG driven by diameter, wall thickness & steel grade
    // ------------------------------------------------------------------
    flattening: (pd) => {
        const d = (pd && pd.input_summary && pd.input_summary.diameter_mm) || 323.9;
        const dInch = (pd && pd.input_summary && pd.input_summary.diameter_inch) || '12"';
        const t = (pd && pd.input_summary && pd.input_summary.wall_thickness_mm) || 9.53;
        const grade = (pd && pd.input_summary && pd.input_summary.material_grade) || 'X52';
        const psl = (pd && pd.input_summary && pd.input_summary.psl_level) || 'PSL2';

        // Deformation factor e (API 5L 10.2.4.3)
        let e = 0.07;
        const gUpper = String(grade).toUpperCase();
        if (gUpper.includes('80')) e = 0.04;
        else if (gUpper.includes('70')) e = 0.05;
        else if (gUpper.includes('65') || gUpper.includes('60') || gUpper.includes('56')) e = 0.06;
        else if (gUpper.includes('52') || gUpper.includes('46')) e = 0.07;
        else if (gUpper.includes('42') || gUpper.includes('B') || gUpper.includes('245') || gUpper.includes('290')) e = 0.08;

        const t_over_d = t / d;
        const H = ((1.0 + e) * t) / (e + t_over_d);
        const H_duct = 0.33 * d;
        const H_sound = 2.0 * t;

        return `
    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm max-w-[720px] mx-auto">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-2 mb-2">
        <div>
          <span class="text-xs font-bold text-slate-900">API 5L Madde 10.2.4.3 & BOTAŞ 3.3.3 Yassıltma Testi (Flattening Test)</span>
          <span class="text-[11px] text-slate-500 block">ERW / HFW Borularda Kaynak ve Gövde Süneklik Denetimi</span>
        </div>
        <div class="flex items-center gap-1.5 text-[11px] font-mono">
          <span class="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-bold border border-blue-200">${dInch} (${d.toFixed(1)} mm) x ${t.toFixed(2)} mm</span>
          <span class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-bold border border-indigo-200">${grade} (${psl})</span>
        </div>
      </div>

      <svg viewBox="0 0 680 300" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto bg-slate-950 rounded-lg border border-slate-800 shadow-inner">
        <defs>
          <marker id="fl-arr-down" markerWidth="6" markerHeight="6" refX="3" refY="6" orient="auto">
            <path d="M0,0 L3,6 L6,0 Z" fill="#ef4444" />
          </marker>
          <marker id="fl-arr-up" markerWidth="6" markerHeight="6" refX="3" refY="0" orient="auto">
            <path d="M0,6 L3,0 L6,6 Z" fill="#3b82f6" />
          </marker>
          <marker id="fl-dim-arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
            <path d="M0,1 L3,3 L0,5 Z" fill="#38bdf8" />
          </marker>
          <linearGradient id="fl-platen-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#475569" />
            <stop offset="50%" stop-color="#334155" />
            <stop offset="100%" stop-color="#1e293b" />
          </linearGradient>
        </defs>

        <!-- Center Line -->
        <line x1="270" y1="20" x2="270" y2="280" stroke="#334155" stroke-dasharray="4,4" stroke-width="1" />
        <line x1="70" y1="150" x2="470" y2="150" stroke="#334155" stroke-dasharray="4,4" stroke-width="1" />

        <!-- Original Circular Pipe Contour (Dashed Cyan) -->
        <circle cx="270" cy="150" r="100" fill="none" stroke="#0ea5e9" stroke-dasharray="5,5" stroke-width="1.5" opacity="0.45" />
        <text x="375" y="80" font-size="10" fill="#38bdf8" font-family="'JetBrains Mono', monospace" opacity="0.8">Başlangıç Çapı: D = ${d.toFixed(1)} mm</text>

        <!-- Upper Press Platen (Hidrolik Pres Üst Tabla) -->
        <rect x="70" y="60" width="400" height="22" rx="3" fill="url(#fl-platen-grad)" stroke="#64748b" stroke-width="1.5" />
        <rect x="235" y="26" width="70" height="34" rx="2" fill="#334155" stroke="#475569" stroke-width="1.5" />
        <text x="270" y="47" font-size="10" font-weight="bold" fill="#f8fafc" text-anchor="middle" font-family="sans-serif">HİDROLİK KOÇ</text>
        <line x1="170" y1="42" x2="170" y2="58" stroke="#ef4444" stroke-width="2.5" marker-end="url(#fl-arr-down)" />
        <line x1="370" y1="42" x2="370" y2="58" stroke="#ef4444" stroke-width="2.5" marker-end="url(#fl-arr-down)" />
        <text x="170" y="34" font-size="9" font-weight="bold" fill="#f87171" text-anchor="middle">Bası Yükü (F)</text>
        <text x="370" y="34" font-size="9" font-weight="bold" fill="#f87171" text-anchor="middle">Bası Yükü (F)</text>

        <!-- Lower Stationary Platen (Sabit Alt Tabla) -->
        <rect x="70" y="218" width="400" height="22" rx="3" fill="url(#fl-platen-grad)" stroke="#64748b" stroke-width="1.5" />
        <line x1="170" y1="258" x2="170" y2="242" stroke="#3b82f6" stroke-width="2" marker-end="url(#fl-arr-up)" />
        <line x1="370" y1="258" x2="370" y2="242" stroke="#3b82f6" stroke-width="2" marker-end="url(#fl-arr-up)" />
        <text x="270" y="262" font-size="10" font-weight="bold" fill="#94a3b8" text-anchor="middle">SABİT REAKSİYON TABLASI</text>

        <!-- Flattened Ring Specimen (Deformed Ellipse) -->
        <ellipse cx="270" cy="150" rx="145" ry="68" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5" />
        <ellipse cx="270" cy="150" rx="131" ry="54" fill="#020617" stroke="#0ea5e9" stroke-width="1.5" />

        <!-- ERW Weld Seam Symbol (at 90° - Saat 9 Pozisyonu) -->
        <path d="M 119 136 L 131 164 M 131 136 L 119 164" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" />
        <circle cx="125" cy="150" r="5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5" />
        
        <!-- Weld Seam Callout Line -->
        <line x1="125" y1="150" x2="65" y2="150" stroke="#f59e0b" stroke-width="1.5" />
        <circle cx="65" cy="150" r="2.5" fill="#f59e0b" />
        <text x="60" y="142" font-size="10" font-weight="bold" fill="#fbbf24" text-anchor="end">ERW Kaynak Dikişi</text>
        <text x="60" y="156" font-size="9" fill="#fde68a" text-anchor="end">Saat 9 Konumu (90°)</text>
        <text x="60" y="170" font-size="8.5" fill="#fca5a5" font-weight="bold" text-anchor="end">⚠️ Çatlak / Açılma YASAK</text>

        <!-- Top & Bottom Crown Callouts (Saat 12 ve 6 noktaları) -->
        <circle cx="270" cy="82" r="3" fill="#38bdf8" />
        <circle cx="270" cy="218" r="3" fill="#38bdf8" />

        <!-- Dimension: Platen Distance H (Right side) -->
        <line x1="485" y1="82" x2="485" y2="218" stroke="#38bdf8" stroke-width="2" />
        <line x1="475" y1="82" x2="495" y2="82" stroke="#38bdf8" stroke-width="1.5" />
        <line x1="475" y1="218" x2="495" y2="218" stroke="#38bdf8" stroke-width="1.5" />
        
        <rect x="495" y="130" width="175" height="40" rx="4" fill="#0f172a" stroke="#0284c7" stroke-width="1" />
        <text x="502" y="146" font-size="11" font-weight="bold" fill="#38bdf8" font-family="'JetBrains Mono', monospace">H = ${H.toFixed(2)} mm</text>
        <text x="502" y="160" font-size="9" fill="#94a3b8" font-family="sans-serif">H = (1+e)·t / (e + t/D)</text>

        <!-- Right Specs Panel -->
        <rect x="495" y="26" width="175" height="95" rx="4" fill="#0f172a" stroke="#334155" stroke-width="1" />
        <text x="502" y="42" font-size="9.5" font-weight="bold" fill="#e2e8f0">YASSILTMA KRİTERLERİ</text>
        <text x="502" y="58" font-size="9" fill="#94a3b8">e Katsayısı: <tspan fill="#f8fafc" font-weight="bold">${e.toFixed(2)}</tspan></text>
        <text x="502" y="73" font-size="9" fill="#94a3b8">1. Aşama (Kaynak): <tspan fill="#34d399" font-weight="bold">${H.toFixed(1)} mm</tspan></text>
        <text x="502" y="88" font-size="9" fill="#94a3b8">2. Aşama (0.33D): <tspan fill="#60a5fa" font-weight="bold">${H_duct.toFixed(1)} mm</tspan></text>
        <text x="502" y="103" font-size="9" fill="#94a3b8">3. Aşama (2t): <tspan fill="#f59e0b" font-weight="bold">${H_sound.toFixed(1)} mm</tspan></text>
        <text x="502" y="116" font-size="8.5" fill="#cbd5e1">Numune: L ≥ 60 mm</text>

        <!-- Bottom Legend -->
        <text x="70" y="290" font-size="9" fill="#94a3b8" font-family="sans-serif">
          API 5L 10.2.4.3: H mesafesine kadar kaynakta (saat 9/3) açılma olmamalı, 0.33D'ye kadar gövdede çatlak olmamalıdır.
        </text>
      </svg>
    </div>`;
    },
    flattening_test: (pd) => SPECIMEN_DRAWINGS.flattening(pd),

    // ------------------------------------------------------------------
    // Pipe End Geometry & Bevel Preparation (API 5L 9.12.5 & BOTAŞ 3.3.8)
    // 30° (+5°/-0°) Bevel Angle, 1.6 ± 0.8 mm Root Face, Out-of-Squareness e <= 1.6 mm
    // ------------------------------------------------------------------
    pipe_bevel: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 1219.0;
        const dInch = s.diameter_inch || '48"';
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const grade = s.material_grade || "X65";
        const std = s.standard_type || "BOTAŞ";
        const c_nom = 1.6;
        const theta_nom = 30.0;
        const h_bev = Math.max(0.0, t - c_nom);

        return `
    <div class="relative w-full overflow-hidden rounded-lg bg-slate-950 p-2 border border-slate-800 text-slate-200">
      <svg viewBox="0 0 680 380" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto">
        <defs>
          <linearGradient id="bev-steel-pipe" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#334155" />
            <stop offset="30%" stop-color="#64748b" />
            <stop offset="70%" stop-color="#475569" />
            <stop offset="100%" stop-color="#1e293b" />
          </linearGradient>
          <linearGradient id="bev-chamfer-face" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.8" />
            <stop offset="50%" stop-color="#fbbf24" stop-opacity="0.9" />
            <stop offset="100%" stop-color="#d97706" stop-opacity="0.8" />
          </linearGradient>
          <marker id="bev-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8" />
          </marker>
          <marker id="bev-arr-amber" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f59e0b" />
          </marker>
          <marker id="bev-arr-rose" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f43f5e" />
          </marker>
        </defs>

        <!-- Background & Title -->
        <rect x="0" y="0" width="680" height="380" fill="#020617" />
        <text x="20" y="24" font-size="12" font-weight="bold" fill="#f8fafc">
          ALIN KAYNAK AĞZI, KÖK YÜZEYİ &amp; UÇ DİKLİK DETAYI (API 5L 9.12.5 &amp; BOTAŞ 3.3.8)
        </text>
        <text x="20" y="38" font-size="9.5" fill="#94a3b8">
          Boru Ebadı: ${dInch} (OD ${d.toFixed(1)} mm) • Et Kalınlığı t = ${t.toFixed(2)} mm • Çelik: ${grade} (${std})
        </text>

        <!-- ================= LEFT PIPE WALL SECTION ================= -->
        <path d="M 40 80 L 165 80 L 230 175 L 230 200 L 40 200 Z" fill="url(#bev-steel-pipe)" stroke="#64748b" stroke-width="1.8" />
        <path d="M 165 80 L 230 175 L 230 200" stroke="#f59e0b" stroke-width="2.5" fill="none" />

        <!-- Machined Bevel Face Glow Overlay -->
        <line x1="165" y1="80" x2="230" y2="175" stroke="#fbbf24" stroke-width="3.5" stroke-linecap="round" />
        <!-- Vertical Root Face (Landing) Line -->
        <line x1="230" y1="175" x2="230" y2="200" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round" />

        <!-- Reference Centerline / Abutting Axis at x = 245 -->
        <line x1="245" y1="60" x2="245" y2="225" stroke="#475569" stroke-width="1.2" stroke-dasharray="6,4" />

        <!-- ================= RIGHT PIPE WALL SECTION ================= -->
        <path d="M 450 80 L 325 80 L 260 175 L 260 200 L 450 200 Z" fill="url(#bev-steel-pipe)" stroke="#64748b" stroke-width="1.8" />
        <path d="M 325 80 L 260 175 L 260 200" stroke="#f59e0b" stroke-width="2.5" fill="none" />
        <line x1="325" y1="80" x2="260" y2="175" stroke="#fbbf24" stroke-width="3.5" stroke-linecap="round" />
        <line x1="260" y1="175" x2="260" y2="200" stroke="#f43f5e" stroke-width="3.5" stroke-linecap="round" />

        <!-- ================= DIMENSIONS & CALLOUTS ================= -->
        <!-- 1. Wall Thickness t Dimension -->
        <line x1="25" y1="80" x2="25" y2="200" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#bev-arr)" marker-end="url(#bev-arr)" />
        <line x1="18" y1="80" x2="38" y2="80" stroke="#38bdf8" stroke-width="1" />
        <line x1="18" y1="200" x2="38" y2="200" stroke="#38bdf8" stroke-width="1" />
        <text x="20" y="145" font-size="10" font-weight="bold" fill="#38bdf8" text-anchor="end" font-family="'JetBrains Mono', monospace">t = ${t.toFixed(2)} mm</text>

        <!-- 2. Vertical Root Face Landing (c = 1.6 mm) Callout -->
        <line x1="238" y1="175" x2="238" y2="200" stroke="#f43f5e" stroke-width="1.5" marker-start="url(#bev-arr-rose)" marker-end="url(#bev-arr-rose)" />
        <line x1="230" y1="175" x2="242" y2="175" stroke="#f43f5e" stroke-width="1" />
        <line x1="230" y1="200" x2="242" y2="200" stroke="#f43f5e" stroke-width="1" />
        <text x="210" y="222" font-size="9.5" font-weight="bold" fill="#fb7185">Kök Yüzeyi c = 1.6 ± 0.8 mm</text>

        <!-- 3. Bevel Angle θ = 30° Arc Indicator -->
        <line x1="230" y1="80" x2="230" y2="175" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3,3" />
        <path d="M 230 115 A 60 60 0 0 0 205 125" fill="none" stroke="#f59e0b" stroke-width="1.8" marker-end="url(#bev-arr-amber)" />
        <text x="215" y="108" font-size="10" font-weight="bold" fill="#fbbf24">θ = 30°</text>
        <text x="215" y="120" font-size="8" fill="#fde68a">(+5° / -0°)</text>

        <!-- 4. Total Included Groove Angle (2θ = 60°) Arc -->
        <path d="M 210 95 A 45 45 0 0 1 280 95" fill="none" stroke="#f59e0b" stroke-width="1.8" marker-start="url(#bev-arr-amber)" marker-end="url(#bev-arr-amber)" />
        <text x="245" y="88" font-size="10.5" font-weight="bold" fill="#f59e0b" text-anchor="middle">2θ = 60°</text>

        <!-- 5. Root Gap Fit-up (b = 1.6 - 2.4 mm) -->
        <line x1="230" y1="210" x2="260" y2="210" stroke="#38bdf8" stroke-width="1.2" marker-start="url(#bev-arr)" marker-end="url(#bev-arr)" />
        <text x="245" y="224" font-size="8.5" fill="#38bdf8" text-anchor="middle">Kök Boşluğu: 1.6 - 2.4 mm</text>

        <!-- 6. Out-of-Squareness (e <= 1.6 mm) Reference Box -->
        <line x1="165" y1="65" x2="165" y2="95" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="3,3" />
        <text x="100" y="72" font-size="9" fill="#f87171">Uç Dikliği e ≤ 1.6 mm</text>

        <!-- Surface Labels -->
        <text x="60" y="96" font-size="8.5" fill="#94a3b8">Boru Dış Yüzeyi (OD)</text>
        <text x="60" y="192" font-size="8.5" fill="#94a3b8">Boru İç Yüzeyi (ID)</text>
        <text x="360" y="96" font-size="8.5" fill="#94a3b8">Boru Dış Yüzeyi (OD)</text>

        <!-- ================= RIGHT SIDE CRITERIA PANEL ================= -->
        <rect x="475" y="55" width="195" height="235" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1" />
        <text x="485" y="74" font-size="10" font-weight="bold" fill="#f8fafc">STANDART KABUL KRİTERLERİ</text>
        <line x1="485" y1="80" x2="660" y2="80" stroke="#334155" stroke-width="1" />

        <text x="485" y="96" font-size="9" fill="#94a3b8">Ağız Açısı (θ): <tspan fill="#fbbf24" font-weight="bold">30° (+5° / -0°)</tspan></text>
        <text x="485" y="112" font-size="9" fill="#94a3b8">İzin Verilen Açı: <tspan fill="#f8fafc">30.0° - 35.0°</tspan></text>
        
        <text x="485" y="132" font-size="9" fill="#94a3b8">Kök Yüzeyi (c): <tspan fill="#f43f5e" font-weight="bold">1.60 ± 0.80 mm</tspan></text>
        <text x="485" y="148" font-size="9" fill="#94a3b8">İzin Verilen Kök: <tspan fill="#f8fafc">0.80 - 2.40 mm</tspan></text>

        <text x="485" y="168" font-size="9" fill="#94a3b8">Uç Diklik Sapması (e): <tspan fill="#38bdf8" font-weight="bold">≤ 1.60 mm</tspan></text>
        
        <text x="485" y="188" font-size="9" fill="#94a3b8">Boru Uç Ovalitesi: <tspan fill="#34d399" font-weight="bold">≤ 3.0 mm</tspan></text>
        <text x="485" y="202" font-size="8.5" fill="#64748b">(D > 610 mm &amp; D/t ≤ 75 için)</text>

        <text x="485" y="222" font-size="9" fill="#94a3b8">İç Talaş (Counterbore): <tspan fill="#a78bfa" font-weight="bold">Maks 1:4 (14°)</tspan></text>
        <text x="485" y="238" font-size="8.5" fill="#64748b">ASME B31.8 Şekil I-4 kuralı</text>

        <rect x="485" y="250" width="175" height="28" rx="4" fill="#022c22" stroke="#059669" stroke-width="1" />
        <text x="572" y="268" font-size="9.5" font-weight="bold" fill="#34d399" text-anchor="middle">✓ API 5L &amp; BOTAŞ UYUMLU</text>

        <!-- Bottom Explanatory Bar -->
        <rect x="15" y="300" width="650" height="65" rx="4" fill="#0f172a" stroke="#1e293b" />
        <text x="25" y="318" font-size="9" fill="#94a3b8">
          ℹ️ <tspan fill="#f8fafc" font-weight="bold">Alın Kaynağı Prensibi (API 5L Madde 9.12.5):</tspan> Saha hattı kaynağında kök pasosunun (root pass) nüfuziyeti için kök yüzeyi 1.6 mm tutulur.
        </text>
        <text x="25" y="334" font-size="9" fill="#94a3b8">
          Kök yüzeyinin 0.8 mm altına düşmesi delinmeye (burn-through), 2.4 mm'yi aşması ise yetersiz nüfuziyete (lack of penetration) neden olur.
        </text>
        <text x="25" y="350" font-size="8.5" fill="#64748b">
          Boru ucu diklikten sapma (out-of-squareness e ≤ 1.6 mm) toleransı hassas çelik gönye ve sentil mastarı ile her iki uçta %100 doğrulanır.
        </text>
      </svg>
    </div>`;
    },
    bevel: (pd) => SPECIMEN_DRAWINGS.pipe_bevel(pd),

    // ------------------------------------------------------------------
    // Pipe Straightness & End Camber Verification (API 5L 9.11.3 & BOTAŞ 5.5, 8.1.2.4)
    // Full-Length Sweep / Camber (<= 0.15% or 0.20% L) & End Straightness (<= 3.0 or 4.0 mm)
    // ------------------------------------------------------------------
    pipe_straightness: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 1219.0;
        const dInch = s.diameter_inch || '48"';
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const l_m = parseFloat(s.pipe_length_m) || 12.0;
        const grade = s.material_grade || "X65";
        const std = s.standard_type || "BOTAŞ";
        const isBotas = String(std).toUpperCase().includes("BOTAŞ") || String(std).toUpperCase().includes("BOTAS");

        const ratioPct = isBotas ? 0.15 : 0.20;
        const totLimitMm = ((ratioPct / 100.0) * l_m * 1000.0).toFixed(1);
        const endLimitMm = isBotas ? 3.0 : 4.0;

        return `
    <div class="relative w-full overflow-hidden rounded-lg bg-slate-950 p-2 border border-slate-800 text-slate-200">
      <svg viewBox="0 0 740 380" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto">
        <defs>
          <linearGradient id="str-pipe-grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#334155" />
            <stop offset="40%" stop-color="#64748b" />
            <stop offset="70%" stop-color="#475569" />
            <stop offset="100%" stop-color="#1e293b" />
          </linearGradient>
          <marker id="str-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8" />
          </marker>
          <marker id="str-arr-green" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#10b981" />
          </marker>
          <marker id="str-arr-rose" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f43f5e" />
          </marker>
          <marker id="str-arr-amber" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f59e0b" />
          </marker>
          <filter id="str-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        <!-- Canvas Background -->
        <rect x="0" y="0" width="740" height="380" fill="#020617" />

        <!-- Title & Spec Header -->
        <text x="24" y="24" font-size="12.5" font-weight="bold" fill="#f8fafc">
          BORU DÜZLÜK VE UÇ SAPMASI (STRAIGHTNESS &amp; END CAMBER) DENETİM ŞEMASI
        </text>
        <text x="24" y="40" font-size="9.5" fill="#94a3b8">
          Standart: ${isBotas ? 'BOTAŞ Madde 5.5 &amp; 8.1.2.4' : 'API Spec 5L Madde 9.11.3 &amp; Tablo 12'} • L = ${l_m.toFixed(1)} m • ${dInch} (OD ${d.toFixed(1)} mm) • t = ${t.toFixed(2)} mm • ${grade}
        </text>

        <!-- 1. STRAIGHT REFERENCE DATUM LINE (Taut Wire / Laser Beam) -->
        <line x1="50" y1="100" x2="690" y2="100" stroke="#10b981" stroke-width="2" stroke-dasharray="8,4" filter="url(#str-glow)" />
        <circle cx="60" cy="100" r="4" fill="#10b981" />
        <circle cx="680" cy="100" r="4" fill="#10b981" />
        <text x="70" y="92" font-size="9" font-weight="bold" fill="#34d399">
          REFERANS HİZALAMA HATTI (Piyano Teli / Lazer Kolimatör Datum Ekseni)
        </text>

        <!-- 2. DEFLECTED PIPE BODY (Boru Gövdesi Sehim / Yaylanma Eğrisi) -->
        <path d="M 60 100 Q 370 148 680 100 L 680 134 Q 370 182 60 134 Z"
              fill="url(#str-pipe-grad)" stroke="#64748b" stroke-width="1.8" />

        <path d="M 60 106 Q 370 154 680 106" stroke="#475569" stroke-width="1.2" stroke-dasharray="4,4" fill="none" />
        <path d="M 60 128 Q 370 176 680 128" stroke="#475569" stroke-width="1.2" stroke-dasharray="4,4" fill="none" />
        <path d="M 60 100 Q 370 148 680 100" stroke="#f59e0b" stroke-width="2.2" fill="none" />

        <!-- 3. PIPE END CHORD GAUGES (1.0 m Hassas Çelik Mastar Bölgeleri) -->
        <rect x="58" y="78" width="94" height="6" rx="2" fill="#38bdf8" opacity="0.9" />
        <text x="105" y="72" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">
          1.0 m Çelik Mastar
        </text>
        <line x1="60" y1="78" x2="60" y2="100" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2" />
        <line x1="152" y1="78" x2="152" y2="107" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2" />
        <line x1="105" y1="84" x2="105" y2="104" stroke="#f43f5e" stroke-width="1.5" marker-start="url(#str-arr-rose)" marker-end="url(#str-arr-rose)" />
        <text x="110" y="96" font-size="8" font-weight="bold" fill="#f43f5e">
          f_sol ≤ ${endLimitMm.toFixed(1)} mm
        </text>

        <rect x="588" y="78" width="94" height="6" rx="2" fill="#38bdf8" opacity="0.9" />
        <text x="635" y="72" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">
          1.0 m Çelik Mastar
        </text>
        <line x1="588" y1="78" x2="588" y2="107" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2" />
        <line x1="680" y1="78" x2="680" y2="100" stroke="#38bdf8" stroke-width="1" stroke-dasharray="2,2" />
        <line x1="635" y1="84" x2="635" y2="104" stroke="#f43f5e" stroke-width="1.5" marker-start="url(#str-arr-rose)" marker-end="url(#str-arr-rose)" />
        <text x="640" y="96" font-size="8" font-weight="bold" fill="#f43f5e">
          f_sağ ≤ ${endLimitMm.toFixed(1)} mm
        </text>

        <!-- 4. MID-SPAN MAXIMUM SAGITTA / DEFLECTION (f_max) -->
        <line x1="370" y1="100" x2="370" y2="148" stroke="#ef4444" stroke-width="2.2" marker-start="url(#str-arr-rose)" marker-end="url(#str-arr-rose)" />
        <text x="380" y="128" font-size="10.5" font-weight="bold" fill="#f87171">
          f_toplam ≤ ${totLimitMm} mm (Maksimum Sehim L/2)
        </text>

        <!-- 5. FULL LENGTH L DIMENSION LINE -->
        <line x1="60" y1="210" x2="680" y2="210" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#str-arr)" marker-end="url(#str-arr)" />
        <line x1="60" y1="134" x2="60" y2="218" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3,3" />
        <line x1="680" y1="134" x2="680" y2="218" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3,3" />
        <text x="370" y="204" font-size="10" font-weight="bold" fill="#38bdf8" text-anchor="middle">
          Tam Boru Boyu: L = ${l_m.toFixed(2)} m (${(l_m*1000).toFixed(0)} mm)
        </text>

        <!-- 6. 7 QA/QC INSPECTION STATIONS -->
        <line x1="60" y1="236" x2="680" y2="236" stroke="#475569" stroke-width="1" />
        <g font-size="8" font-family="'JetBrains Mono', monospace" fill="#94a3b8" text-anchor="middle">
          <circle cx="60" cy="236" r="3" fill="#38bdf8" />
          <text x="60" y="250">0.0 m</text>
          <text x="60" y="260" font-size="7.5" fill="#64748b">Sol Uç</text>

          <circle cx="152" cy="236" r="3" fill="#38bdf8" />
          <text x="152" y="250">1.0 m</text>
          <text x="152" y="260" font-size="7.5" fill="#64748b">Mastar</text>

          <circle cx="215" cy="236" r="3" fill="#64748b" />
          <text x="215" y="250">${(l_m*0.25).toFixed(1)} m</text>
          <text x="215" y="260" font-size="7.5" fill="#64748b">L/4</text>

          <circle cx="370" cy="236" r="3" fill="#ef4444" />
          <text x="370" y="250" font-weight="bold" fill="#f87171">${(l_m*0.50).toFixed(1)} m</text>
          <text x="370" y="260" font-size="7.5" fill="#f87171">L/2 (Zirve)</text>

          <circle cx="525" cy="236" r="3" fill="#64748b" />
          <text x="525" y="250">${(l_m*0.75).toFixed(1)} m</text>
          <text x="525" y="260" font-size="7.5" fill="#64748b">3L/4</text>

          <circle cx="588" cy="236" r="3" fill="#38bdf8" />
          <text x="588" y="250">${(l_m-1.0).toFixed(1)} m</text>
          <text x="588" y="260" font-size="7.5" fill="#64748b">Mastar</text>

          <circle cx="680" cy="236" r="3" fill="#38bdf8" />
          <text x="680" y="250">${l_m.toFixed(1)} m</text>
          <text x="680" y="260" font-size="7.5" fill="#64748b">Sağ Uç</text>
        </g>

        <!-- 7. ENGINEERING CRITERIA & QA/QC COMPLIANCE SUMMARY CARD -->
        <rect x="24" y="278" width="692" height="88" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
        
        <text x="40" y="298" font-size="10" font-weight="bold" fill="#38bdf8">
          KABUL VE DENETİM KRİTERLERİ (QA/QC INSPECTION CRITERIA):
        </text>

        <text x="40" y="316" font-size="9" fill="#e2e8f0">
          • <tspan font-weight="bold" fill="#fbbf24">Tam Boy Düzlük Sapması (Total Sweep/Camber):</tspan> ${isBotas ? 'BOTAŞ Madde 5.5 (≤ %0.15 × L)' : 'API 5L Tablo 12 (≤ %0.20 × L)'} → <tspan font-weight="bold" fill="#34d399">Maks. ${totLimitMm} mm</tspan>
        </text>
        <text x="40" y="332" font-size="9" fill="#e2e8f0">
          • <tspan font-weight="bold" fill="#fbbf24">Boru Uç Düzlük Sapması (End Straightness):</tspan> Her iki uçta 1.0 m mastar boyunca → <tspan font-weight="bold" fill="#34d399">Maks. ${endLimitMm.toFixed(1)} mm</tspan> ${isBotas ? '(BOTAŞ 8.1.2.4)' : '(API 5L 9.11.3.2)'}
        </text>
        <text x="40" y="348" font-size="8.5" fill="#94a3b8">
          • <tspan fill="#cbd5e1">Ölçüm Metodu:</tspan> Boru eksenine paralel gerdirilmiş çelik tel veya lazer optik hiza düzlemi ve uçlarda 1.0 m hassas çelik mastar + sentil mastarı.
        </text>
      </svg>
    </div>`;
    },
    straightness: (pd) => SPECIMEN_DRAWINGS.pipe_straightness(pd),

    // ------------------------------------------------------------------
    // Wall Thickness Underflow & Barlow Derating (API 5L Table 11 & ASME B31.8)
    // ------------------------------------------------------------------
    pipe_derating: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const d = parseFloat(s.diameter_mm) || 1219.0;
        const dInch = s.diameter_inch || '48"';
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const grade = s.material_grade || "X65";
        const std = s.standard_type || "BOTAŞ";
        const isBotas = String(std).toUpperCase().includes("BOTAŞ") || String(std).toUpperCase().includes("BOTAS");

        const tolNegPct = (isBotas && t >= 15.0) ? 8.0 : 10.0;
        const tolPosPct = 10.0;
        const tMin = (t * (1.0 - tolNegPct / 100.0)).toFixed(2);
        const tMax = (t * (1.0 + tolPosPct / 100.0)).toFixed(2);
        const deltaT = (t - parseFloat(tMin)).toFixed(2);

        // Demo bar calculations (F = 0.72, SMYS = 450 MPa)
        const pNom = (((2.0 * 450.0 * t) / d) * 0.72 * 10.0).toFixed(1);
        const pMin = (((2.0 * 450.0 * parseFloat(tMin)) / d) * 0.72 * 10.0).toFixed(1);
        const deltaP = (parseFloat(pNom) - parseFloat(pMin)).toFixed(1);

        const hydroStressNom = isBotas ? 95.0 : 90.0;
        const hydroStressMin = (hydroStressNom * (t / parseFloat(tMin))).toFixed(1);

        return `
    <div class="relative w-full overflow-hidden rounded-lg bg-slate-950 p-2 border border-slate-800 text-slate-200">
      <svg viewBox="0 0 740 380" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto">
        <defs>
          <linearGradient id="der-steel-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#334155" />
            <stop offset="50%" stop-color="#475569" />
            <stop offset="100%" stop-color="#1e293b" />
          </linearGradient>
          <linearGradient id="der-risk-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#f43f5e" stop-opacity="0.8" />
            <stop offset="100%" stop-color="#be123c" stop-opacity="0.9" />
          </linearGradient>
          <marker id="der-arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8" />
          </marker>
          <marker id="der-arr-rose" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
            <path d="M0,0 L6,3 L0,6 Z" fill="#f43f5e" />
          </marker>
        </defs>

        <!-- Canvas Background -->
        <rect x="0" y="0" width="740" height="380" fill="#020617" />

        <!-- Title & Spec Header -->
        <text x="24" y="24" font-size="12.5" font-weight="bold" fill="#f8fafc">
          ET KALINLIĞI TOLERANS ALTI (UNDERFLOW) &amp; BASINÇ İNDİRGEME (DERATING) ŞEMASI
        </text>
        <text x="24" y="40" font-size="9.5" fill="#94a3b8">
          Standart: API 5L Çizelge 11 &amp; ASME B31.8 • ${dInch} (OD ${d.toFixed(1)} mm) • Nominal t = ${t.toFixed(2)} mm • ${grade} (${std})
        </text>

        <!-- ================= LEFT: MAGNIFIED WALL CROSS-SECTION ================= -->
        <!-- Wall thickness slice: X outer surface at 300, inner surfaces to the left -->
        <rect x="30" y="60" width="310" height="205" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
        <text x="42" y="80" font-size="10" font-weight="bold" fill="#38bdf8">
          Boru Cidar Kesiti &amp; Tolerans Katmanları:
        </text>

        <!-- Outer Pipe Surface (Dış Yüzey) at x = 280 -->
        <line x1="280" y1="95" x2="280" y2="245" stroke="#38bdf8" stroke-width="3" />
        <text x="280" y="90" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">Dış Yüzey (OD)</text>

        <!-- Wall Steel Body (Nominal t Zone: from 280 to 140) -->
        <rect x="140" y="100" width="140" height="140" fill="url(#der-steel-grad)" stroke="#64748b" stroke-width="1.2" />

        <!-- Underflow Negative Tolerance Zone (from 140 to 175) -->
        <rect x="140" y="100" width="35" height="140" fill="url(#der-risk-grad)" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="3,3" />

        <!-- Upper Tolerance Extension Zone (from 105 to 140) -->
        <rect x="105" y="100" width="35" height="140" fill="#f59e0b" fill-opacity="0.15" stroke="#f59e0b" stroke-width="1.2" stroke-dasharray="4,4" />

        <!-- Labels on slices -->
        <!-- t_max line at x = 105 -->
        <line x1="105" y1="95" x2="105" y2="245" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="4,4" />
        <text x="105" y="90" font-size="8" fill="#fbbf24" text-anchor="middle">t_max (+%${tolPosPct})</text>

        <!-- t_nom line at x = 140 -->
        <line x1="140" y1="95" x2="140" y2="245" stroke="#38bdf8" stroke-width="2" />
        <text x="140" y="90" font-size="8" font-weight="bold" fill="#38bdf8" text-anchor="middle">t_nom (${t.toFixed(1)}mm)</text>

        <!-- t_min line at x = 175 -->
        <line x1="175" y1="95" x2="175" y2="245" stroke="#f43f5e" stroke-width="2.5" />
        <text x="175" y="90" font-size="8" font-weight="bold" fill="#f43f5e" text-anchor="middle">t_min (-%${tolNegPct})</text>

        <!-- Dimension arrows below slice at y = 252 -->
        <!-- Nominal t dimension (140 to 280) -->
        <line x1="140" y1="252" x2="280" y2="252" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#der-arr)" marker-end="url(#der-arr)" />
        <text x="210" y="264" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">t_nom = ${t.toFixed(2)} mm</text>

        <!-- Underflow delta t (140 to 175) -->
        <line x1="140" y1="170" x2="175" y2="170" stroke="#f43f5e" stroke-width="2" marker-start="url(#der-arr-rose)" marker-end="url(#der-arr-rose)" />
        <text x="157" y="162" font-size="7.5" font-weight="bold" fill="#fecdd3" text-anchor="middle">Δt = ${deltaT}mm</text>
        <text x="157" y="185" font-size="7" fill="#fecdd3" text-anchor="middle">Kayıp Cidar</text>

        <!-- ================= RIGHT: BARLOW CAPACITY & STRESS JUMP GAUGES ================= -->
        <rect x="360" y="60" width="355" height="205" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
        <text x="375" y="80" font-size="10" font-weight="bold" fill="#38bdf8">
          Basınç Kapasitesi ve Gerilme Değerlendirmesi:
        </text>

        <!-- 1. Barlow Design Pressure Gauge -->
        <text x="375" y="105" font-size="9" font-weight="bold" fill="#e2e8f0">
          1. Barlow Tasarım Basıncı (ASME B31.8 F=0.72):
        </text>
        <!-- Background track -->
        <rect x="375" y="112" width="320" height="14" rx="4" fill="#1e293b" />
        <!-- Nominal bar (100% width = 320 px) -->
        <rect x="375" y="112" width="320" height="14" rx="4" fill="#0284c7" />
        <text x="535" y="123" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Nominal P_nom = ${pNom} bar</text>
        <!-- Derated bar overlay -->
        <rect x="375" y="130" width="288" height="14" rx="4" fill="#d97706" />
        <text x="519" y="141" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">İndirgenmiş P_min = ${pMin} bar (-${deltaP} bar / -%${tolNegPct})</text>

        <!-- 2. Hydrostatic Test Hoop Stress Jump Gauge -->
        <text x="375" y="165" font-size="9" font-weight="bold" fill="#e2e8f0">
          2. Fabrika Hidrostatik Test Çeper Gerilmesi (Hoop Stress):
        </text>
        <rect x="375" y="172" width="320" height="14" rx="4" fill="#1e293b" />
        <!-- Nominal Stress (%95 SMYS = 280 px) -->
        <rect x="375" y="172" width="280" height="14" rx="4" fill="#059669" />
        <text x="515" y="183" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Nominal t'de Gerilme: %${hydroStressNom.toFixed(1)} SMYS</text>

        <!-- 100% Yield Stress Marker Line at x = 670 -->
        <line x1="670" y1="168" x2="670" y2="212" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,3" />
        <text x="670" y="166" font-size="8" font-weight="bold" fill="#ef4444" text-anchor="middle">%100 SMYS (Akma Sınırı)</text>

        <!-- Stress Jump Bar at t_min -->
        <rect x="375" y="190" width="305" height="14" rx="4" fill="#e11d48" />
        <text x="527" y="201" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Alt Sınır t_min'de: %${hydroStressMin} SMYS (Sıçrama: +%${(parseFloat(hydroStressMin) - hydroStressNom).toFixed(1)})</text>

        <!-- Warning Callout Badge -->
        <rect x="375" y="214" width="320" height="38" rx="4" fill="#450a0a" stroke="#b91c1c" stroke-width="1" />
        <text x="385" y="228" font-size="8" font-weight="bold" fill="#fca5a5">
          ⚠️ KALİTE GÜVENCE UYARISI:
        </text>
        <text x="385" y="242" font-size="7.8" fill="#fecdd3">
          Boru alt toleransta (%-${tolNegPct}) üretilirse, fabrika hidrostatik testinde akma sınırı aşılabilir veya hat tasarım basıncı %${tolNegPct} düşer!
        </text>

        <!-- ================= BOTTOM: ENGINEERING CRITERIA CARD ================= -->
        <rect x="24" y="280" width="692" height="85" rx="6" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
        <text x="40" y="300" font-size="10" font-weight="bold" fill="#38bdf8">
          STANDART KABUL VE İNDİRGEME KRİTERLERİ (QA/QC CRITERIA):
        </text>
        <text x="40" y="318" font-size="9" fill="#e2e8f0">
          • <tspan font-weight="bold" fill="#fbbf24">İmalat Cidar Toleransı (API 5L Tablo 11):</tspan> Nominal ${t.toFixed(2)} mm → Alt Sınır: <tspan font-weight="bold" fill="#f43f5e">${tMin} mm</tspan> / Üst Sınır: <tspan font-weight="bold" fill="#34d399">${tMax} mm</tspan>
        </text>
        <text x="40" y="334" font-size="9" fill="#e2e8f0">
          • <tspan font-weight="bold" fill="#fbbf24">ASME B31.8 Basınç İndirgemesi:</tspan> Hat güvenli işletme basıncı <tspan font-weight="bold" fill="#f59e0b">${pNom} bar</tspan> yerine <tspan font-weight="bold" fill="#f87171">${pMin} bar</tspan> olarak baz alınmalıdır.
        </text>
        <text x="40" y="350" font-size="8.5" fill="#94a3b8">
          • <tspan fill="#cbd5e1">BOTAŞ Şartnamesi Madde 8.1.2.4:</tspan> D ≥ 20" borularda et kalınlığı her boru boyunca ultrasonik kalınlık ölçerle %100 taranır.
        </text>
      </svg>
    </div>`;
    },
    derating: (pd) => SPECIMEN_DRAWINGS.pipe_derating(pd),


    // ------------------------------------------------------------------
    // Residual Stress Ring Test (BOTAŞ Madde 3.3.9) — 150 mm ring cut +
    // slit at the point opposite the weld + ring springing open (gap Δ).
    // Animated 2.5D SVG: cylindrical pipe end (A) + axonometric ring (B).
    // Weld seam symbol follows the selected manufacturing process.
    // Dimensions driven by the selected pipe.
    // ------------------------------------------------------------------
    residual_stress_ring: (pd) => {
        const d = (pd && pd.input_summary && pd.input_summary.diameter_mm) || 1219.0;
        const dInch = (pd && pd.input_summary && pd.input_summary.diameter_inch) || '48"';
        const t = (pd && pd.input_summary && pd.input_summary.wall_thickness_mm) || 14.30;
        const delta = (pd && pd.toughness_and_tests && typeof pd.toughness_and_tests.residual_stress_max_mm === 'number')
            ? pd.toughness_and_tests.residual_stress_max_mm : 3.5;
        const dMean = Math.max(0, d - t);
        const proc = ((pd && pd.input_summary && pd.input_summary.manufacturing_process) || 'SAWH').toUpperCase();
        const isSawh = proc.includes('SAWH');
        const isCow = proc.includes('COW');
        const seamLabel = isCow ? 'kombine kaynak dikişi' : (isSawh ? 'spiral kaynak dikişi' : 'boyuna kaynak dikişi');
        const seamPath = isSawh
            ? 'M 516 244 Q 546 232 562 208'
            : (isCow ? 'M 522 240 L 558 218 M 534 236 L 552 224' : 'M 522 240 L 558 218');
        const bodySeam = isSawh
            ? 'M 118 116 C 150 122, 176 178, 218 186'
            : (isCow ? 'M 108 126 L 228 126 M 150 126 L 163 143' : 'M 108 126 L 228 126');
        return `
    <svg viewBox="0 0 640 400" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[400px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
        .rs-step{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;fill:#475569}
        .rs-pipe-piece{animation:rsPiece 8s linear infinite}
        .rs-torch{transform-origin:0px 0px;animation:rsTorchA 8s linear infinite}
        .rs-spark{animation:rsSparkA 8s linear infinite}
        .rs-kerf-a{animation:rsKerfA 8s linear infinite}
        .rs-kerf-b{animation:rsKerfB 8s linear infinite}
        .rs-ring-body{transform-origin:455px 266px;animation:rsSpring 8s linear infinite}
        .rs-gap{transform-origin:455px 168px;animation:rsGapOpen 8s linear infinite}
        .rs-face-l{animation:rsFaceL 8s linear infinite}
        .rs-face-r{animation:rsFaceR 8s linear infinite}
        .rs-gapdim{animation:rsGapDim 8s linear infinite}
        @keyframes rsPiece{0%,26%{transform:translateX(0);opacity:1}38%,100%{transform:translateX(-30px);opacity:.35}}
        @keyframes rsTorchA{0%{transform:translate(0,0) rotate(0deg);opacity:0}5%{opacity:1}25%{transform:translate(-12px,26px) rotate(-45deg)}50%{transform:translate(-15px,44px) rotate(-90deg)}75%{transform:translate(-12px,66px) rotate(-135deg)}100%{transform:translate(0,88px) rotate(-180deg);opacity:1}}
        @keyframes rsSparkA{0%,4%{opacity:0}8%,26%{opacity:1}30%,100%{opacity:0}}
        @keyframes rsKerfA{0%{opacity:0}6%,28%{opacity:1}36%,100%{opacity:0}}
        @keyframes rsKerfB{0%,36%{opacity:0}46%,54%{opacity:1}64%,100%{opacity:0}}
        @keyframes rsSpring{0%,54%{transform:scale(1)}80%,100%{transform:scale(1.018)}}
        @keyframes rsGapOpen{0%,54%{transform:scaleX(.04)}74%,100%{transform:scaleX(1)}}
        @keyframes rsFaceL{0%,54%{transform:translateX(0)}74%,100%{transform:translateX(-12px)}}
        @keyframes rsFaceR{0%,54%{transform:translateX(0)}74%,100%{transform:translateX(12px)}}
        @keyframes rsGapDim{0%,72%{opacity:0}82%,100%{opacity:1}}
      </style>
      <defs>
        <marker id="rs-arr" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
        <linearGradient id="rs-pipe-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#cbd5e1"/><stop offset="45%" stop-color="#e2e8f0"/><stop offset="100%" stop-color="#94a3b8"/>
        </linearGradient>
        <linearGradient id="rs-face-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f1f5f9"/><stop offset="55%" stop-color="#cbd5e1"/><stop offset="100%" stop-color="#94a3b8"/>
        </linearGradient>
        <linearGradient id="rs-band-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#64748b"/><stop offset="55%" stop-color="#94a3b8"/><stop offset="100%" stop-color="#475569"/>
        </linearGradient>
        <linearGradient id="rs-bore-wall-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#475569"/><stop offset="100%" stop-color="#1e293b"/>
        </linearGradient>
      </defs>

      <!-- ============ A) Pipe end — 150 mm ring cut ============ -->
      <text x="16" y="26" class="sd-txt" font-weight="bold" font-size="12">A) Boru Ucu — 150 mm Halka Kesimi</text>

      <!-- far end cap -->
      <ellipse cx="230" cy="150" rx="15" ry="44" fill="#94a3b8" stroke="#334155" stroke-width="1.5"/>
      <!-- body (remaining pipe) -->
      <rect x="96" y="106" width="134" height="88" fill="url(#rs-pipe-grad)" stroke="#334155" stroke-width="1.5"/>
      <!-- body cut face at x=96 (revealed when the ring slides off) -->
      <ellipse cx="96" cy="150" rx="15" ry="44" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
      <ellipse cx="96" cy="150" rx="9.5" ry="28" fill="#0f172a" stroke="#334155" stroke-width="1"/>
      <!-- weld seam on body -->
      <path d="${bodySeam}" fill="none" stroke="#d97706" stroke-width="5" opacity="0.85" stroke-linecap="round"/>

      <!-- ring piece (short hollow tube — slides off) -->
      <g class="rs-pipe-piece">
        <rect x="40" y="106" width="56" height="88" fill="url(#rs-pipe-grad)" stroke="#334155" stroke-width="1.5"/>
        <!-- inner bore wall seen through the hollow ring -->
        <path d="M 40 122 A 9.5 28 0 0 0 40 178 L 96 178 A 9.5 28 0 0 1 96 122 Z" fill="url(#rs-bore-wall-grad)" opacity="0.95"/>
        <!-- right cut face — ring cross-section (hollow) -->
        <ellipse cx="96" cy="150" rx="15" ry="44" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
        <ellipse cx="96" cy="150" rx="9.5" ry="28" fill="#0f172a" stroke="#334155" stroke-width="1"/>
        <!-- left open end face — wall thickness -->
        <ellipse cx="40" cy="150" rx="15" ry="44" fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
        <ellipse cx="40" cy="150" rx="9.5" ry="28" fill="#0f172a" stroke="#475569" stroke-width="1"/>
      </g>
      <!-- kerf (cut plane) -->
      <path class="rs-kerf-a" d="M 96 106 A 15 44 0 0 0 96 194" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="5,3"/>
      <!-- cutting torch travelling around the circumference -->
      <g transform="translate(96 106)">
        <g class="rs-torch">
          <rect x="-3" y="-14" width="10" height="12" rx="1.5" fill="#94a3b8" stroke="#334155" stroke-width="1"/>
          <path d="M 2 -14 L -1 -24 L 5 -24 Z" fill="#475569"/>
          <path d="M 2 -2 L -2 4 L 6 4 Z" fill="#ef4444"/>
          <g class="rs-spark" fill="#f59e0b">
            <circle cx="4" cy="7" r="2.2"/><circle cx="-3" cy="9" r="1.7"/><circle cx="9" cy="10" r="1.8"/>
          </g>
          <g class="rs-spark" fill="#fbbf24" style="animation-delay:.18s">
            <circle cx="-5" cy="3" r="1.6"/><circle cx="10" cy="5" r="2"/>
          </g>
        </g>
      </g>
      <text x="130" y="84" class="sd-lbl" fill="#b91c1c">Kesme ocağı (plazma/oksijen)</text>
      <!-- t callout -->
      <line x1="32" y1="112" x2="18" y2="98" class="sd-line" stroke="#f59e0b" stroke-width="1"/>
      <text x="16" y="94" class="sd-dimtxt" text-anchor="start">t = ${t.toFixed(2)} mm</text>
      <!-- 150 mm dimension -->
      <line x1="40" y1="212" x2="96" y2="212" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
      <line x1="40" y1="206" x2="40" y2="218" class="sd-dim"/>
      <line x1="96" y1="206" x2="96" y2="218" class="sd-dim"/>
      <text x="68" y="228" text-anchor="middle" class="sd-dimtxt">150 mm</text>

      <!-- ============ B) Standing ring — slit & opening (Δ) ============ -->
      <text x="300" y="26" class="sd-txt" font-weight="bold" font-size="12">B) Halka Üzerinde Çentik &amp; Açılma (Δ)</text>

      <g class="rs-ring-body">
        <!-- outer cylindrical surface (band between the front & back outer rims) -->
        <path fill-rule="evenodd" fill="url(#rs-band-grad)" stroke="#334155" stroke-width="1.5"
              d="M 391 149 A 98 98 0 1 0 587 149 A 98 98 0 1 0 391 149 Z M 403 149 A 86 86 0 1 1 575 149 A 86 86 0 1 1 403 149 Z"/>
        <!-- far (back) bore rim -->
        <circle cx="489" cy="149" r="86" fill="none" stroke="#64748b" stroke-width="1.1" opacity="0.9"/>
        <!-- outer surface silhouette lines (tube depth) -->
        <line x1="407.2" y1="82.5" x2="441.2" y2="63.5" stroke="#334155" stroke-width="1.2" opacity="0.7"/>
        <line x1="502.8" y1="253.5" x2="536.8" y2="234.5" stroke="#334155" stroke-width="1.2" opacity="0.7"/>
        <!-- weld seam on the outer surface (process dependent) -->
        <path d="${seamPath}" fill="none" stroke="#f59e0b" stroke-width="6" opacity="0.92" stroke-linecap="round"/>
        <!-- inner cylindrical wall seen through the hollow bore (through-hole stays open) -->
        <path d="M 431.1 85.4 A 86 86 0 1 0 512.9 231.6 A 86 86 0 0 1 431.1 85.4 Z"
              fill="url(#rs-bore-wall-grad)" stroke="#334155" stroke-width="1"/>
        <line x1="400" y1="228" x2="352" y2="248" class="sd-line" stroke="#64748b" stroke-width="0.8"/>
        <text x="350" y="252" text-anchor="end" class="sd-note" fill="#1e3a8a">İç cidar — ring içi boştur</text>
        <!-- front machined face — annulus shows wall thickness -->
        <path fill-rule="evenodd" fill="url(#rs-face-grad)" stroke="#334155" stroke-width="1.5"
              d="M 357 168 A 98 98 0 1 0 553 168 A 98 98 0 1 0 357 168 Z M 369 168 A 86 86 0 1 1 541 168 A 86 86 0 1 1 369 168 Z"/>
        <!-- slit → opening: gap through the wall AND through the 150 mm width -->
        <g class="rs-gap">
          <path d="M 443.1 70 L 466.9 70 L 500.9 51 L 477.1 51 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.8"/>
          <path d="M 443.1 70 L 466.9 70 L 465.5 82 L 444.5 82 Z" fill="#f1f5f9" stroke="#94a3b8" stroke-width="0.8"/>
        </g>
        <!-- exposed wall cut faces (t) on both opened edges -->
        <path class="rs-face-r" d="M 455 70 L 455 82 L 460 79.2 L 460 67.2 Z" fill="#b45309" opacity="0.92" stroke="#7c2d12" stroke-width="0.8"/>
        <path class="rs-face-l" d="M 455 70 L 455 82 L 460 79.2 L 460 67.2 Z" fill="#b45309" opacity="0.92" stroke="#7c2d12" stroke-width="0.8"/>
      </g>

      <!-- kerf line through the wall at the slit (before opening) -->
      <g class="rs-kerf-b">
        <line x1="455" y1="62" x2="455" y2="90" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,3"/>
        <line x1="455" y1="76" x2="489" y2="57" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.8"/>
      </g>

      <!-- slit label -->
      <text x="430" y="46" text-anchor="end" class="sd-lbl" fill="#b91c1c">Çentik (kaynağın karşısı)</text>
      <!-- gap dimension (Δ) -->
      <g class="rs-gapdim">
        <line x1="441" y1="56" x2="469" y2="56" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
        <line x1="441" y1="52" x2="441" y2="60" class="sd-dim"/>
        <line x1="469" y1="52" x2="469" y2="60" class="sd-dim"/>
        <text x="474" y="60" text-anchor="start" class="sd-dimtxt">Δ ≤ ${delta.toFixed(2)} mm</text>
      </g>

      <!-- OD diameter across the front face -->
      <line x1="357" y1="168" x2="553" y2="168" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
      <text x="455" y="298" text-anchor="middle" class="sd-dimtxt">OD (D) = ${d.toFixed(1)} mm (${dInch})</text>
      <text x="455" y="314" text-anchor="middle" class="sd-dimtxt">Dₘ = D − t = ${dMean.toFixed(1)} mm (Ortalama Çap)</text>

      <!-- 150 mm ring width along the depth axis -->
      <line x1="556" y1="166" x2="590" y2="147" class="sd-dim" marker-start="url(#rs-arr)" marker-end="url(#rs-arr)"/>
      <text x="596" y="156" class="sd-dimtxt" transform="rotate(-29 596 156)">150 mm</text>

      <!-- wall thickness callout on the front face -->
      <line x1="390" y1="103" x2="344" y2="84" class="sd-line" stroke="#f59e0b" stroke-width="1"/>
      <text x="340" y="82" text-anchor="end" class="sd-dimtxt">t = ${t.toFixed(2)} mm</text>

      <!-- weld seam label -->
      <line x1="548" y1="228" x2="578" y2="270" class="sd-line" stroke="#d97706" stroke-width="1"/>
      <text x="620" y="288" text-anchor="end" class="sd-lbl" fill="#b45309">${seamLabel}</text>

      <!-- ============ Steps & acceptance caption ============ -->
      <line x1="16" y1="340" x2="624" y2="340" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="356" class="rs-step">1) Boru ucundan 150 mm halka kesilir • 2) Kaynağın karşısından tek noktadan çentilir • 3) Halka kendiliğinden açılır, Δ ölçülür</text>
      <text x="16" y="372" class="sd-dimtxt">Kabul: S = (E·t·Δ) / (12.566·Dₘ²) ≤ %10 SMYS, Dₘ = D − t (BOTAŞ Madde 3.3.9) • Δ ≤ ${delta.toFixed(2)} mm</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // DWTT specimen (API 5L 9.9 / ASTM E436)
    // Photorealistic 2.5D plate (305 × 76 mm × t) + cold press-notch + 254 mm anvil span
    // + fracture surface ductile shear area evaluation zone.
    // ------------------------------------------------------------------
    dwtt: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const tStr = t.toFixed(2);
        const grade = s.material_grade || 'X65';

        return `
    <svg viewBox="0 0 640 420" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[420px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#2563eb;stroke-width:1.2;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;fill:#1d4ed8}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#475569}
      </style>
      <defs>
        <marker id="sd-arr-dwtt" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#2563eb"/>
        </marker>
        <filter id="sd-dwtt-shadow" x="-5%" y="-5%" width="115%" height="120%">
          <feDropShadow dx="2" dy="3" stdDeviation="2.5" flood-color="#0f172a" flood-opacity="0.18"/>
        </filter>
        <!-- Steel heavy plate gradient -->
        <linearGradient id="dwtt-steel-plate" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#f8fafc"/>
          <stop offset="15%" stop-color="#e2e8f0"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="85%" stop-color="#94a3b8"/>
          <stop offset="100%" stop-color="#64748b"/>
        </linearGradient>
        <linearGradient id="dwtt-tup-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fbbf24"/>
          <stop offset="50%" stop-color="#d97706"/>
          <stop offset="100%" stop-color="#78350f"/>
        </linearGradient>
        <linearGradient id="dwtt-roller-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#334155"/>
          <stop offset="50%" stop-color="#64748b"/>
          <stop offset="100%" stop-color="#1e293b"/>
        </linearGradient>
        <linearGradient id="dwtt-fracture-shear" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#bbf7d0"/>
          <stop offset="50%" stop-color="#86efac"/>
          <stop offset="100%" stop-color="#4ade80"/>
        </linearGradient>
      </defs>

      <!-- Title Header -->
      <rect x="12" y="6" width="616" height="26" rx="4" fill="#f8fafc" stroke="#e2e8f0"/>
      <text x="320" y="23" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12" fill="#0f172a">
        DWTT Numunesi (Drop Weight Tear Test) — API 5L 9.9 / ASTM E436
      </text>

      <!-- ============ A) Test Rig & Specimen Setup ============ -->
      <text x="24" y="52" class="sd-lbl">A) Test Düzeneği (305 × 76 mm × t) • 254 mm Mesnet Açıklığı</text>

      <!-- Drop Weight Tup Hammer -->
      <g transform="translate(320, 52)">
        <path d="M -22 0 L 22 0 L 12 28 L -12 28 Z" fill="url(#dwtt-tup-grad)" stroke="#92400e" stroke-width="1.4"/>
        <path d="M -12 28 Q 0 38 12 28 Z" fill="#b45309"/>
        <!-- Impact Arrow -->
        <line x1="0" y1="-14" x2="0" y2="-2" stroke="#b91c1c" stroke-width="2.5"/>
        <polygon points="-4,-2 4,-2 0,6" fill="#b91c1c"/>
        <text x="32" y="16" class="sd-lbl" fill="#b91c1c">Düşen Ağırlık (Tup)</text>
      </g>

      <!-- Specimen Plate with Shadow -->
      <g filter="url(#sd-dwtt-shadow)">
        <!-- Main Plate Body -->
        <rect x="70" y="96" width="500" height="96" rx="2" fill="url(#dwtt-steel-plate)" stroke="#334155" stroke-width="1.8"/>
        <!-- Specular Highlight -->
        <line x1="71" y1="97" x2="569" y2="97" stroke="#ffffff" stroke-width="1.2" opacity="0.9"/>

        <!-- Press-Notch (Center Bottom) -->
        <path d="M 312 192 L 320 178 L 328 192 Z" fill="#ffffff" stroke="#b45309" stroke-width="1.5"/>
        <!-- Plastic deformation halo -->
        <circle cx="320" cy="178" r="4" fill="#f59e0b" opacity="0.45"/>
        <line x1="312" y1="192" x2="320" y2="178" stroke="#b45309" stroke-width="1.8"/>
        <line x1="328" y1="192" x2="320" y2="178" stroke="#b45309" stroke-width="1.8"/>

        <!-- Anvils (Rollers) -->
        <!-- Left Anvil (x = 111, span = 254 mm scaled) -->
        <rect x="99" y="192" width="24" height="24" rx="4" fill="url(#dwtt-roller-grad)" stroke="#1e293b" stroke-width="1.4"/>
        <!-- Right Anvil (x = 505) -->
        <rect x="517" y="192" width="24" height="24" rx="4" fill="url(#dwtt-roller-grad)" stroke="#1e293b" stroke-width="1.4"/>
      </g>

      <!-- Press-notch label & callout -->
      <text x="320" y="214" text-anchor="middle" class="sd-lbl" fill="#b45309">Pres Çentik (Press-Notch)</text>
      <text x="320" y="228" text-anchor="middle" class="sd-dimtxt">45° Açılı Bıçak • Derinlik = 5,08 ± 0,19 mm</text>

      <!-- Span Dimension: 254 mm -->
      <line x1="111" y1="236" x2="529" y2="236" class="sd-dim" marker-start="url(#sd-arr-dwtt)" marker-end="url(#sd-arr-dwtt)"/>
      <line x1="111" y1="228" x2="111" y2="244" class="sd-dim"/>
      <line x1="529" y1="228" x2="529" y2="244" class="sd-dim"/>
      <text x="320" y="250" text-anchor="middle" class="sd-dimtxt">Örs Açıklığı = 254,0 ± 1,5 mm (10 inç)</text>

      <!-- Length Dimension: 305 mm -->
      <line x1="70" y1="84" x2="570" y2="84" class="sd-dim" marker-start="url(#sd-arr-dwtt)" marker-end="url(#sd-arr-dwtt)"/>
      <line x1="70" y1="78" x2="70" y2="90" class="sd-dim"/>
      <line x1="570" y1="78" x2="570" y2="90" class="sd-dim"/>
      <text x="320" y="80" text-anchor="middle" class="sd-dimtxt">L = 305 ± 5,0 mm (12 inç)</text>

      <!-- Height Dimension: 76 mm -->
      <line x1="586" y1="96" x2="586" y2="192" class="sd-dim"/>
      <line x1="580" y1="96" x2="592" y2="96" class="sd-dim"/>
      <line x1="580" y1="192" x2="592" y2="192" class="sd-dim"/>
      <text x="596" y="148" class="sd-dimtxt">W = 76 mm</text>

      <!-- Thickness Callout -->
      <line x1="70" y1="144" x2="36" y2="144" class="sd-dim" marker-end="url(#sd-arr-dwtt)"/>
      <text x="32" y="140" text-anchor="end" class="sd-dimtxt">t = ${tStr} mm</text>
      <text x="32" y="152" text-anchor="end" class="sd-note">(tam cidar)</text>

      <!-- ============ B) Fracture Surface Evaluation Region ============ -->
      <text x="24" y="278" class="sd-lbl">B) Kırılma Yüzeyi ve Sünek Kırılma Alanı Değerlendirme Bölgesi (API 5L 9.9)</text>

      <!-- Fracture bar diagram -->
      <g filter="url(#sd-dwtt-shadow)">
        <rect x="70" y="292" width="500" height="42" rx="2" fill="#e2e8f0" stroke="#334155" stroke-width="1.5"/>
        <!-- Notch side excluded zone (first 19 mm / 0.75 in) -->
        <rect x="70" y="292" width="70" height="42" fill="#fecaca" opacity="0.75"/>
        <text x="105" y="316" text-anchor="middle" class="sd-note" font-size="9px" fill="#991b1b">Hariç (19 mm)</text>

        <!-- Valid Shear Evaluation Area (Middle) -->
        <rect x="140" y="292" width="360" height="42" fill="url(#dwtt-fracture-shear)" stroke="#16a34a" stroke-width="1.2"/>
        <text x="320" y="312" text-anchor="middle" class="sd-lbl" fill="#14532d">Geçerli Değerlendirme Bölgesi (%85 Sünek Kırılma Alanı Sınırı)</text>
        <text x="320" y="326" text-anchor="middle" class="sd-dimtxt" fill="#166534">Mat / Fibröz Kesme Kırılması Yüzdesi Ölçülür</text>

        <!-- Tup side excluded zone (19 mm) -->
        <rect x="500" y="292" width="70" height="42" fill="#fecaca" opacity="0.75"/>
        <text x="535" y="316" text-anchor="middle" class="sd-note" font-size="9px" fill="#991b1b">Hariç (19 mm)</text>
      </g>

      <line x1="70" y1="344" x2="140" y2="344" class="sd-dim"/>
      <text x="105" y="356" text-anchor="middle" class="sd-dimtxt">19 mm</text>
      <line x1="500" y1="344" x2="570" y2="344" class="sd-dim"/>
      <text x="535" y="356" text-anchor="middle" class="sd-dimtxt">19 mm</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="372" x2="624" y2="372" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="388" class="sd-note">API 5L Madde 9.9: D ≥ 508 mm (20 in) hat borularında her test birimi için iki numunede ortalama sünek kırılma alanı ≥ %85 olmalıdır.</text>
      <text x="16" y="402" class="sd-note">Kırılma yüzeyinde çentik ucundan 19 mm ve vuruş kenarından 19 mm olan ezilme bölgeleri değerlendirmeye dahil edilmez (ASTM E436).</text>
    </svg>`;
    },

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