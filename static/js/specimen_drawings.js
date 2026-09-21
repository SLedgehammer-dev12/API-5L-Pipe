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
    charpy: (pd) => {
        const tt = (pd && pd.toughness_and_tests) || {};
        const sizeLabel = String(tt.notch_specimen_size || '');
        const cvnReq = tt.cvn_required !== false;
        const sel = sizeLabel.includes('10 x 10') ? 'full'
            : (sizeLabel.includes('7.5') ? '34'
            : (sizeLabel.includes('6.67') ? '23'
            : (sizeLabel.includes('5 x 10') ? '12' : '')));
        const hlFill = (k) => (!cvnReq ? '#e2e8f0' : (sel === k ? '#fde68a' : '#e2e8f0'));
        const hlStroke = (k) => (cvnReq && sel === k ? '#b45309' : '#334155');
        const hlW = (k) => (cvnReq && sel === k ? 2.5 : 1);
        const tag = (k, y) => (cvnReq && sel === k
            ? `<text x="404" y="${y}" text-anchor="end" class="sd-note" fill="#b45309" font-weight="700">seçili ▶</text>` : '');
        return `
    <svg viewBox="0 0 640 420" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[420px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#64748b}
      </style>
      <defs>
        <marker id="sd-arr2" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <text x="320" y="22" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Charpy V-Çentik Numunesi — API 5L 9.8 / Çizelge 22 (ISO 148-1 / ASTM A370)</text>

      <!-- ============ A) Side elevation ============ -->
      <text x="24" y="48" class="sd-lbl">A) Yan görünüş (55 × 10 mm)</text>
      <rect x="40" y="70" width="302" height="55" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <path d="M 186 70 L 191 81 L 196 70" fill="#fff" stroke="#334155" stroke-width="1.4"/>
      <circle cx="191" cy="81" r="1.4" fill="#fff" stroke="#334155" stroke-width="0.9"/>
      <text x="191" y="61" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="10">45°</text>
      <line x1="206" y1="70" x2="206" y2="81" class="sd-dim"/>
      <text x="210" y="78" class="sd-dimtxt">2 mm</text>
      <line x1="222" y1="81" x2="222" y2="125" class="sd-dim"/>
      <line x1="218" y1="81" x2="226" y2="81" class="sd-dim"/>
      <line x1="218" y1="125" x2="226" y2="125" class="sd-dim"/>
      <text x="228" y="106" class="sd-dimtxt">8 mm</text>
      <line x1="188" y1="84" x2="166" y2="104" stroke="#3b82f6" stroke-width="0.8"/>
      <text x="164" y="116" text-anchor="end" class="sd-dimtxt">r = 0,25 mm</text>
      <line x1="40" y1="145" x2="342" y2="145" class="sd-dim" marker-start="url(#sd-arr2)" marker-end="url(#sd-arr2)"/>
      <line x1="40" y1="139" x2="40" y2="151" class="sd-dim"/>
      <line x1="342" y1="139" x2="342" y2="151" class="sd-dim"/>
      <text x="191" y="163" text-anchor="middle" class="sd-dimtxt">L = 55 mm</text>
      <line x1="358" y1="70" x2="358" y2="125" class="sd-dim"/>
      <line x1="352" y1="70" x2="364" y2="70" class="sd-dim"/>
      <line x1="352" y1="125" x2="364" y2="125" class="sd-dim"/>
      <text x="366" y="102" class="sd-dimtxt">10 mm</text>
      <text x="191" y="192" text-anchor="middle" class="sd-note">V-çentik: 45° dahil açı • 2 mm derinlik • r = 0,25 mm kök</text>

      <!-- ============ B) Cross-section + magnified notch ============ -->
      <text x="24" y="228" class="sd-lbl">B) Kesit (10 × 10) ve çentik detayı</text>
      <rect x="50" y="245" width="60" height="60" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <path d="M 74 245 L 80 256 L 86 245" fill="#fff" stroke="#334155" stroke-width="1.4"/>
      <line x1="118" y1="245" x2="118" y2="305" class="sd-dim"/>
      <line x1="114" y1="245" x2="122" y2="245" class="sd-dim"/>
      <line x1="114" y1="305" x2="122" y2="305" class="sd-dim"/>
      <text x="126" y="278" class="sd-dimtxt">10 mm</text>
      <line x1="50" y1="318" x2="110" y2="318" class="sd-dim" marker-start="url(#sd-arr2)" marker-end="url(#sd-arr2)"/>
      <text x="80" y="332" text-anchor="middle" class="sd-dimtxt">10 mm</text>
      <!-- magnifier -->
      <circle cx="240" cy="272" r="52" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="4,3"/>
      <text x="240" y="214" text-anchor="middle" class="sd-note">Büyütülmüş çentik detayı</text>
      <line x1="214" y1="246" x2="266" y2="246" stroke="#94a3b8" stroke-width="1"/>
      <path d="M 214 246 L 240 298 L 266 246" fill="none" stroke="#334155" stroke-width="2"/>
      <line x1="240" y1="246" x2="240" y2="298" class="sd-dim"/>
      <text x="248" y="268" class="sd-dimtxt">2 mm</text>
      <text x="254" y="292" class="sd-dimtxt">45°</text>
      <circle cx="240" cy="298" r="2.2" fill="#fff" stroke="#334155" stroke-width="1"/>
      <line x1="242" y1="300" x2="282" y2="316" stroke="#3b82f6" stroke-width="0.8"/>
      <text x="285" y="321" class="sd-dimtxt">r = 0,25 mm</text>

      <!-- ============ D) Sub-size variants (Table 22) ============ -->
      <text x="380" y="48" class="sd-lbl">D) Alt boyutlar (Çizelge 22)</text>
      <rect x="410" y="64" width="120" height="27" fill="${hlFill('full')}" stroke="${hlStroke('full')}" stroke-width="${hlW('full')}"/>
      <text x="538" y="82" class="sd-note" font-size="10.5px">Tam boy 10 × 10 × 55</text>
      ${tag('full', 82)}
      <rect x="410" y="106" width="120" height="20" fill="${hlFill('34')}" stroke="${hlStroke('34')}" stroke-width="${hlW('34')}"/>
      <text x="538" y="120" class="sd-note" font-size="10.5px">3/4 boy 7,5 × 10 × 55</text>
      ${tag('34', 120)}
      <rect x="410" y="142" width="120" height="18" fill="${hlFill('23')}" stroke="${hlStroke('23')}" stroke-width="${hlW('23')}"/>
      <text x="538" y="155" class="sd-note" font-size="10.5px">2/3 boy 6,67 × 10 × 55</text>
      ${tag('23', 155)}
      <rect x="410" y="176" width="120" height="14" fill="${hlFill('12')}" stroke="${hlStroke('12')}" stroke-width="${hlW('12')}"/>
      <text x="538" y="188" class="sd-note" font-size="10.5px">1/2 boy 5 × 10 × 55</text>
      ${tag('12', 188)}
      <text x="380" y="214" class="sd-note">Alt boyutta enerji ölçeklenir (9.8.1.1);</text>
      <text x="380" y="228" class="sd-note">tek değer ≥ ortalamanın %75'i (9.8.1.2).</text>
      ${cvnReq ? '' : '<text x="380" y="248" class="sd-note" fill="#b45309" font-weight="700">PSL1: CVN zorunlu değil (Çizelge 17).</text>'}

      <!-- ============ C) Impact rig (3-point bending) ============ -->
      <text x="380" y="270" class="sd-lbl">C) Darbe düzeni (3 nokta eğilme)</text>
      <line x1="465" y1="272" x2="465" y2="284" stroke="#475569" stroke-width="2"/>
      <path d="M 461 277 L 469 277 L 465 285 Z" fill="#475569"/>
      <path d="M 450 285 L 480 285 L 465 306 Z" fill="#94a3b8" stroke="#334155" stroke-width="1.2"/>
      <text x="486" y="292" class="sd-note">Vurucu (sarkaç)</text>
      <rect x="405" y="306" width="125" height="12" fill="#e2e8f0" stroke="#334155" stroke-width="1.5"/>
      <path d="M 461 318 L 465 324 L 469 318" fill="#fff" stroke="#334155" stroke-width="1.2"/>
      <rect x="400" y="324" width="40" height="14" fill="#475569" stroke="#334155" stroke-width="1"/>
      <rect x="490" y="324" width="40" height="14" fill="#475569" stroke="#334155" stroke-width="1"/>
      <text x="474" y="337" class="sd-note">çentik</text>
      <line x1="440" y1="348" x2="490" y2="348" class="sd-dim" marker-start="url(#sd-arr2)" marker-end="url(#sd-arr2)"/>
      <text x="496" y="352" class="sd-note" font-size="10px">40 mm örs açıklığı</text>
      <text x="380" y="366" class="sd-note">Çentik, vurucunun karşı yüzünde (altta).</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="378" x2="624" y2="378" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="392" class="sd-note">Çentik, boru dış yüzeyine dik açılacak şekilde işlenir (API 5L 9.8.2) • Test sıcaklığı ve kabul enerjileri Çizelge 8 / BOTAŞ Tablo 3.</text>
      <text x="16" y="408" class="sd-note">Kaynak/ITAB numunesinde çentik, kaynak merkez hattına veya füzyon hattına +2 mm konumlandırılır.</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // Tensile strip specimen (38.1 mm wide, full wall thickness)
    // API 5L 10.2.3.2.1 — rectangular test piece, ISO 6892-1 / ASTM A370.
    // Plan + end section + extraction inset; weld + HAZ for welded pipe.
    // ------------------------------------------------------------------
    tensile_strip: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const isSmls = proc.includes('SMLS') || proc.includes('SEAMLESS') || proc.includes('DIKISSIZ') || proc.includes('DİKİŞSİZ');
        const tStr = t.toFixed(2);
        const hpx = Math.max(16, Math.min(48, Math.round(t * 1.5)));
        const gripTicks = (x0, x1) => {
            let out = '';
            for (let x = x0; x <= x1; x += 15) out += `<line x1="${x}" y1="62" x2="${x}" y2="126"/>`;
            return out;
        };
        return `
    <svg viewBox="0 0 640 380" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[380px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#64748b}
      </style>
      <defs>
        <marker id="sd-arr3" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <text x="320" y="22" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Çekme Şerit Numunesi — 38,1 mm × t (API 5L 10.2.3.2.1; ISO 6892-1 / ASTM A370)</text>

      <!-- ============ A) Plan view ============ -->
      <text x="24" y="48" class="sd-lbl">A) Üst görünüş (tam cidar şerit)</text>
      <rect x="60" y="62" width="520" height="64" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <rect x="60" y="62" width="80" height="64" fill="#cbd5e1" stroke="#334155" stroke-width="1"/>
      <rect x="500" y="62" width="80" height="64" fill="#cbd5e1" stroke="#334155" stroke-width="1"/>
      <g stroke="#94a3b8" stroke-width="1">
        ${gripTicks(75, 135)}
        ${gripTicks(515, 575)}
      </g>
      <text x="100" y="98" text-anchor="middle" class="sd-lbl" fill="#475569">Tutma</text>
      <text x="540" y="98" text-anchor="middle" class="sd-lbl" fill="#475569">Tutma</text>
      <line x1="278" y1="54" x2="278" y2="134" stroke="#3b82f6" stroke-width="1.5"/>
      <line x1="362" y1="54" x2="362" y2="134" stroke="#3b82f6" stroke-width="1.5"/>
      ${isSmls ? `
      <line x1="70" y1="94" x2="570" y2="94" stroke="#d97706" stroke-width="3" opacity="0.75"/>
      <text x="320" y="150" text-anchor="middle" class="sd-lbl" fill="#b45309">Boyuna numune — dikişsiz gövde</text>` : `
      <rect x="304" y="62" width="6" height="64" fill="#fcd34d" opacity="0.6"/>
      <rect x="312" y="62" width="16" height="64" fill="#fbbf24" opacity="0.65"/>
      <rect x="330" y="62" width="6" height="64" fill="#fcd34d" opacity="0.6"/>
      <text x="320" y="150" text-anchor="middle" class="sd-lbl" fill="#b45309">Kaynak (enine, ortada) + ITAB</text>`}
      <line x1="278" y1="170" x2="362" y2="170" class="sd-dim" marker-start="url(#sd-arr3)" marker-end="url(#sd-arr3)"/>
      <line x1="278" y1="164" x2="278" y2="176" class="sd-dim"/>
      <line x1="362" y1="164" x2="362" y2="176" class="sd-dim"/>
      <text x="320" y="186" text-anchor="middle" class="sd-dimtxt">L0 = 50 mm (uzama esası)</text>
      <line x1="596" y1="62" x2="596" y2="126" class="sd-dim"/>
      <line x1="590" y1="62" x2="602" y2="62" class="sd-dim"/>
      <line x1="590" y1="126" x2="602" y2="126" class="sd-dim"/>
      <text x="600" y="98" class="sd-dimtxt">38,1 mm</text>
      <text x="320" y="206" text-anchor="middle" class="sd-note">${isSmls ? 'Dikişsiz boruda numune boyuna (eksenel) alınır.' : 'Kaynaklı boruda numune kaynağa dik (enine) alınır; kaynak mastar ortasındadır.'}</text>

      <!-- ============ B) End section ============ -->
      <text x="24" y="228" class="sd-lbl">B) Uç kesiti (38,1 × t)</text>
      <rect x="50" y="240" width="120" height="${hpx}" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <path d="M 50 240 Q 110 226 170 240" fill="none" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
      <line x1="186" y1="240" x2="186" y2="${240 + hpx}" class="sd-dim"/>
      <line x1="180" y1="240" x2="192" y2="240" class="sd-dim"/>
      <line x1="180" y1="${240 + hpx}" x2="192" y2="${240 + hpx}" class="sd-dim"/>
      <text x="196" y="${240 + Math.round(hpx / 2) + 4}" class="sd-dimtxt">t = ${tStr} mm</text>
      <line x1="50" y1="${240 + hpx + 18}" x2="170" y2="${240 + hpx + 18}" class="sd-dim" marker-start="url(#sd-arr3)" marker-end="url(#sd-arr3)"/>
      <text x="110" y="${240 + hpx + 32}" text-anchor="middle" class="sd-dimtxt">38,1 mm</text>

      <!-- ============ C) Extraction inset ============ -->
      <text x="250" y="228" class="sd-lbl">C) Numune alımı (boru kesiti)</text>
      <circle cx="450" cy="272" r="54" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <circle cx="450" cy="272" r="46" fill="#0f172a"/>
      <path d="M 431.5 221.2 A 54 54 0 0 1 468.5 221.2 L 465.7 228.8 A 46 46 0 0 0 434.3 228.8 Z"
            fill="#f59e0b" opacity="0.9" stroke="#b45309" stroke-width="1"/>
      <circle cx="450" cy="218" r="3.5" fill="#d97706"/>
      <text x="466" y="214" class="sd-note">kaynak</text>
      <text x="496" y="226" class="sd-lbl" fill="#b45309">şerit</text>
      <text x="450" y="344" text-anchor="middle" class="sd-note">${isSmls ? 'Boyuna numune (eksenel)' : 'Enine numune (kaynak ortada)'}</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="352" x2="624" y2="352" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="366" class="sd-note">API 5L 10.2.3.2.1 — dikdörtgen test parçası, tam cidar; genişlik 38,1 mm; uzama 50 mm esası.</text>
      <text x="16" y="376" class="sd-note">ISO 6892-1 / ASTM A370 — paralel kenarlı, işlenmiş veya hadde yüzeyli şerit numune.</text>
    </svg>`;
    },

    // ------------------------------------------------------------------
    // Tensile round-bar specimen — API 5L 10.2.3.2.5 / Table 21
    // Grip ends + shoulders with radius + parallel gauge with the transverse
    // weld at mid-length. Bar diameter (6.4 / 8.9 / 12.7 mm) per Table 21.
    // ------------------------------------------------------------------
    tensile_round: (pd) => {
        const s = (pd && pd.input_summary) || {};
        const t = parseFloat(s.wall_thickness_mm) || 14.30;
        const proc = String(s.manufacturing_process || 'SAWH').toUpperCase();
        const isSmls = proc.includes('SMLS') || proc.includes('SEAMLESS') || proc.includes('DIKISSIZ') || proc.includes('DİKİŞSİZ');
        const dBar = isSmls ? (t >= 19.0 ? 12.7 : 6.4) : rsRoundBarDia(s.diameter_mm || 1219.0, t);
        const dStr = dBar.toFixed(1);
        const barH = Math.round(dBar * 2.6);
        const gripH = Math.round(barH * 1.9);
        const cy = 100;
        const gTop = cy - Math.round(barH / 2);
        const gBot = cy + Math.round(barH / 2);
        const pTop = cy - Math.round(gripH / 2);
        const pBot = cy + Math.round(gripH / 2);
        const threadTicks = (x0, x1) => {
            let out = '';
            for (let x = x0; x <= x1; x += 12) out += `<line x1="${x}" y1="${pTop + 2}" x2="${x}" y2="${pBot - 2}"/>`;
            return out;
        };
        const thk = Math.max(16, Math.min(48, Math.round(t * 1.5)));
        const barR = Math.max(4, Math.min(Math.round(dBar * 1.6), Math.round(thk / 2) - 1));
        return `
    <svg viewBox="0 0 640 380" xmlns="http://www.w3.org/2000/svg" class="w-full h-auto max-h-[380px]">
      <style>
        .sd-line{stroke:#334155;stroke-width:1.5;fill:none}
        .sd-dim{stroke:#3b82f6;stroke-width:1;stroke-dasharray:3,3}
        .sd-txt{font-family:'JetBrains Mono',monospace;font-size:11px;fill:#0f172a}
        .sd-lbl{font-family:'Inter',sans-serif;font-size:10.5px;font-weight:600;fill:#1e3a8a}
        .sd-dimtxt{font-family:'JetBrains Mono',monospace;font-size:10px;fill:#2563eb}
        .sd-note{font-family:'Inter',sans-serif;font-size:9.5px;fill:#64748b}
      </style>
      <defs>
        <marker id="sd-arr4" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
          <path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/>
        </marker>
      </defs>

      <text x="320" y="22" text-anchor="middle" class="sd-txt" font-weight="bold" font-size="12">Yuvarlak Çubuk Çekme Numunesi (API 5L 10.2.3.2.5 / Tablo 21)</text>

      <!-- ============ A) Elevation ============ -->
      <text x="24" y="48" class="sd-lbl">A) Görünüş (dişli uçlar + omuz + mastar)</text>
      <g stroke="#64748b" stroke-width="1.3">${threadTicks(52, 132)}${threadTicks(512, 592)}</g>
      <rect x="40" y="${pTop}" width="100" height="${gripH}" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <path d="M 140 ${pTop} C 158 ${pTop}, 158 ${gTop}, 168 ${gTop} L 168 ${gBot} C 158 ${gBot}, 158 ${pBot}, 140 ${pBot} Z"
            fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
      <rect x="168" y="${gTop}" width="304" height="${barH}" fill="#fef3c7" stroke="#b45309" stroke-width="2"/>
      <path d="M 472 ${gTop} C 482 ${gTop}, 482 ${pTop}, 500 ${pTop} L 500 ${pBot} C 482 ${pBot}, 482 ${gBot}, 472 ${gBot} Z"
            fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
      <rect x="500" y="${pTop}" width="100" height="${gripH}" fill="#e2e8f0" stroke="#334155" stroke-width="2"/>
      <line x1="278" y1="${gTop - 4}" x2="278" y2="${gBot + 4}" stroke="#3b82f6" stroke-width="1.3"/>
      <line x1="362" y1="${gTop - 4}" x2="362" y2="${gBot + 4}" stroke="#3b82f6" stroke-width="1.3"/>
      ${isSmls ? `
      <text x="320" y="${gTop - 10}" text-anchor="middle" class="sd-lbl" fill="#b45309">Boyuna numune (dikişsiz)</text>` : `
      <rect x="312" y="${gTop}" width="16" height="${barH}" fill="#fbbf24" opacity="0.65"/>
      <rect x="304" y="${gTop}" width="6" height="${barH}" fill="#fcd34d" opacity="0.6"/>
      <rect x="330" y="${gTop}" width="6" height="${barH}" fill="#fcd34d" opacity="0.6"/>
      <text x="320" y="${gTop - 10}" text-anchor="middle" class="sd-lbl" fill="#b45309">Kaynak (enine, ortada) + ITAB</text>`}
      <line x1="200" y1="${gTop}" x2="200" y2="${gTop - 16}" class="sd-dim"/>
      <text x="204" y="${gTop - 18}" class="sd-dimtxt">d = ${dStr} mm (Tablo 21)</text>
      <line x1="278" y1="${gBot + 22}" x2="362" y2="${gBot + 22}" class="sd-dim" marker-start="url(#sd-arr4)" marker-end="url(#sd-arr4)"/>
      <line x1="278" y1="${gBot + 16}" x2="278" y2="${gBot + 28}" class="sd-dim"/>
      <line x1="362" y1="${gBot + 16}" x2="362" y2="${gBot + 28}" class="sd-dim"/>
      <text x="320" y="${gBot + 38}" text-anchor="middle" class="sd-dimtxt">L0 = 50 mm</text>
      <text x="90" y="${cy + 4}" text-anchor="middle" class="sd-lbl" fill="#475569">Dişli uç</text>
      <text x="550" y="${cy + 4}" text-anchor="middle" class="sd-lbl" fill="#475569">Dişli uç</text>
      <line x1="152" y1="${pBot}" x2="180" y2="${pBot + 12}" stroke="#3b82f6" stroke-width="0.8"/>
      <text x="182" y="${pBot + 16}" class="sd-dimtxt">r (omuz yarıçapı)</text>

      <!-- ============ B) Extraction from the wall (d ≤ t) ============ -->
      <text x="24" y="196" class="sd-lbl">B) Cidardan alım (d ≤ t)</text>
      <rect x="50" y="220" width="240" height="${thk}" fill="#cbd5e1" stroke="#334155" stroke-width="2"/>
      <line x1="50" y1="${220 + Math.round(thk / 2)}" x2="290" y2="${220 + Math.round(thk / 2)}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3"/>
      <circle cx="170" cy="${220 + Math.round(thk / 2)}" r="${barR}" fill="#fef3c7" stroke="#b45309" stroke-width="2"/>
      <text x="170" y="212" text-anchor="middle" class="sd-dimtxt">d = ${dStr} mm</text>
      <text x="298" y="${220 + Math.round(thk / 2) + 4}" class="sd-dimtxt">t = ${t.toFixed(2)} mm</text>
      <text x="170" y="${220 + thk + 16}" text-anchor="middle" class="sd-note">${isSmls ? 'Boyuna çubuk (eksenel) — d ≤ t' : 'Enine çubuk (cidar boyunca) — d ≤ t'}</text>

      <!-- ============ C) Shoulder / gauge detail ============ -->
      <text x="340" y="196" class="sd-lbl">C) Omuz ve mastar detayı</text>
      <rect x="350" y="238" width="60" height="74" fill="#e2e8f0" stroke="#334155" stroke-width="1.5"/>
      <path d="M 410 238 C 428 238, 440 250, 440 266 L 440 284 C 440 300, 428 312, 410 312 Z"
            fill="#cbd5e1" stroke="#334155" stroke-width="1.5"/>
      <rect x="440" y="266" width="150" height="18" fill="#fef3c7" stroke="#b45309" stroke-width="1.5"/>
      <line x1="416" y1="246" x2="452" y2="226" stroke="#3b82f6" stroke-width="0.8"/>
      <text x="455" y="223" class="sd-dimtxt">r</text>
      <text x="515" y="278" text-anchor="middle" class="sd-dimtxt">mastar d = ${dStr} mm</text>
      <text x="380" y="326" text-anchor="middle" class="sd-note">işlenmiş omuz geçişi</text>

      <!-- ============ Captions ============ -->
      <line x1="16" y1="340" x2="624" y2="340" stroke="#cbd5e1" stroke-width="1"/>
      <text x="16" y="354" class="sd-note">API 5L 10.2.3.2.5 / Tablo 21 — mastar çapı d: 6,4 / 8,9 / 12,7 mm (D ve t'ye göre); ISO 6892-1 / ASTM A370.</text>
      <text x="16" y="370" class="sd-note">Kaynaklı boruda enine numune (kaynak mastar ortasında); SMLS'te t ≥ 19,0 mm ise boyuna 12,7 mm çubuk zorunludur.</text>
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