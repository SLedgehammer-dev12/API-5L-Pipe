/**
 * 2D Interactive SVG Pipe Cross-Section & Tolerance Diagram Generator
 */
class PipeVisualizer2D {
    static render(containerId, pipeData) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const d_mm = pipeData.input_summary.diameter_mm || 1219.0;
        const t_mm = pipeData.input_summary.wall_thickness_mm || 14.30;
        const d_inch = pipeData.input_summary.diameter_inch || "48\"";
        const grade = pipeData.input_summary.material_grade || "X65";
        const process = pipeData.input_summary.manufacturing_process || "SAWH";
        const t_min = pipeData.wall_thickness_tolerance.min_mm || (t_mm - 0.15);
        const t_max = pipeData.wall_thickness_tolerance.max_mm || (t_mm + 1.5);
        const weld_in = pipeData.weld_and_geometry.weld_height_inside_mm || 2.6;
        const weld_out = pipeData.weld_and_geometry.weld_height_outside_mm || 3.4;

        const width = 600;
        const height = 450;
        const cx = 250;
        const cy = 225;

        // Scaling to fit 400px circle
        const maxR = 180;
        const r_od = maxR;
        const r_id = maxR * ((d_mm - (2 * t_mm)) / d_mm);
        const r_id_min = maxR * ((d_mm - (2 * t_max)) / d_mm);
        const r_id_max = maxR * ((d_mm - (2 * t_min)) / d_mm);

        const isSawh = process.toUpperCase().includes("SAWH");

        const svg = `
        <svg viewBox="0 0 ${width} ${height}" class="w-full h-full select-none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="pipeSteelGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#475569" />
                    <stop offset="50%" stop-color="#94a3b8" />
                    <stop offset="100%" stop-color="#334155" />
                </linearGradient>
                <linearGradient id="weldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#d97706" />
                    <stop offset="50%" stop-color="#f59e0b" />
                    <stop offset="100%" stop-color="#b45309" />
                </linearGradient>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#334155" stroke-width="0.5" opacity="0.3" />
                </pattern>
            </defs>

            <!-- Background Grid -->
            <rect width="100%" height="100%" fill="#0f172a" rx="8" />
            <rect width="100%" height="100%" fill="url(#grid)" rx="8" />

            <!-- Center Axes -->
            <line x1="${cx}" y1="20" x2="${cx}" y2="${height - 20}" stroke="#64748b" stroke-dasharray="4,4" stroke-width="1" />
            <line x1="20" y1="${cy}" x2="480" y2="${cy}" stroke="#64748b" stroke-dasharray="4,4" stroke-width="1" />

            <!-- Outer Wall Circle -->
            <circle cx="${cx}" cy="${cy}" r="${r_od}" fill="url(#pipeSteelGrad)" stroke="#cbd5e1" stroke-width="2" />

            <!-- Inner Wall Circle (Subtracted Hollow) -->
            <circle cx="${cx}" cy="${cy}" r="${r_id}" fill="#0f172a" stroke="#cbd5e1" stroke-width="2" />

            <!-- Tolerance Envelope (Dashed lines) -->
            <circle cx="${cx}" cy="${cy}" r="${r_id_min}" fill="none" stroke="#ef4444" stroke-dasharray="3,3" stroke-width="1" opacity="0.8" />
            <circle cx="${cx}" cy="${cy}" r="${r_id_max}" fill="none" stroke="#22c55e" stroke-dasharray="3,3" stroke-width="1" opacity="0.8" />

            <!-- Weld Reinforcement Bevel (Top Sector) -->
            <path d="M ${cx - 14} ${cy - r_od} Q ${cx} ${cy - r_od - (isSawh ? 10 : 7)} ${cx + 14} ${cy - r_od} L ${cx + 8} ${cy - r_id} Q ${cx} ${cy - r_id + (isSawh ? 8 : 5)} ${cx - 8} ${cy - r_id} Z" 
                  fill="url(#weldGrad)" stroke="#fbbf24" stroke-width="1.5" />

            <!-- Dimensional Annotations -->
            <!-- Outer Diameter Dimension -->
            <line x1="${cx - r_od}" y1="${cy + r_od + 20}" x2="${cx + r_od}" y2="${cy + r_od + 20}" stroke="#38bdf8" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)" />
            <line x1="${cx - r_od}" y1="${cy}" x2="${cx - r_od}" y2="${cy + r_od + 25}" stroke="#38bdf8" stroke-dasharray="2,2" stroke-width="1" />
            <line x1="${cx + r_od}" y1="${cy}" x2="${cx + r_od}" y2="${cy + r_od + 25}" stroke="#38bdf8" stroke-dasharray="2,2" stroke-width="1" />
            <text x="${cx}" y="${cy + r_od + 35}" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">OD = ${d_mm} mm (${d_inch})</text>

            <!-- Wall Thickness Callout -->
            <line x1="${cx + r_id}" y1="${cy}" x2="${cx + r_od}" y2="${cy}" stroke="#fbbf24" stroke-width="3" />
            <line x1="${cx + (r_od + r_id)/2}" y1="${cy}" x2="${cx + (r_od + r_id)/2 + 40}" y2="${cy - 40}" stroke="#fbbf24" stroke-width="1" />
            <text x="${cx + (r_od + r_id)/2 + 45}" y="${cy - 40}" fill="#fbbf24" font-size="12" font-weight="bold">t = ${t_mm} mm</text>
            <text x="${cx + (r_od + r_id)/2 + 45}" y="${cy - 25}" fill="#94a3b8" font-size="10">Tol: [${t_min} - ${t_max}] mm</text>

            <!-- Weld Reinforcement Callout -->
            <line x1="${cx}" y1="${cy - r_od - 6}" x2="${cx + 60}" y2="${cy - r_od - 35}" stroke="#f59e0b" stroke-width="1" />
            <text x="${cx + 65}" y="${cy - r_od - 40}" fill="#f59e0b" font-size="11" font-weight="bold">Kaynak Dikişi (${process})</text>
            <text x="${cx + 65}" y="${cy - r_od - 26}" fill="#cbd5e1" font-size="10">Dış Yükseklik: ${weld_out} mm | İç: ${weld_in} mm</text>

            <!-- Specification Legend Card (Right Side) -->
            <g transform="translate(460, 25)">
                <rect width="125" height="155" fill="#1e293b" rx="6" stroke="#475569" />
                <text x="10" y="20" fill="#f8fafc" font-size="12" font-weight="bold">Boru Bilgisi</text>
                <line x1="10" y1="26" x2="115" y2="26" stroke="#475569" />
                <text x="10" y="45" fill="#94a3b8" font-size="10">Çap: <tspan fill="#f8fafc" font-weight="bold">${d_inch}</tspan></text>
                <text x="10" y="65" fill="#94a3b8" font-size="10">Kalite: <tspan fill="#38bdf8" font-weight="bold">${grade}</tspan></text>
                <text x="10" y="85" fill="#94a3b8" font-size="10">Yöntem: <tspan fill="#fbbf24" font-weight="bold">${process}</tspan></text>
                <text x="10" y="105" fill="#94a3b8" font-size="10">Et Kalınlığı: <tspan fill="#f8fafc" font-weight="bold">${t_mm} mm</tspan></text>
                <text x="10" y="125" fill="#94a3b8" font-size="10">Min Tol: <tspan fill="#ef4444" font-weight="bold">${t_min} mm</tspan></text>
                <text x="10" y="145" fill="#94a3b8" font-size="10">Max Tol: <tspan fill="#22c55e" font-weight="bold">${t_max} mm</tspan></text>
            </g>
        </svg>
        `;

        container.innerHTML = svg;
    }
}
