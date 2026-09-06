"""
Generator script for authentic Natural Gas Pipeline API 5L ITP PDF documents:
1. 18_API_5L_42in_X70_3LPE_Polyethylene_Coated_Gas_Mainline_ITP.pdf (3LPE External Coating per ISO 21809-1 / DIN 30670)
2. 19_API_RP_5L2_Internal_Flow_Efficiency_Epoxy_Coated_Gas_Pipe_ITP.pdf (Internal Flow Coating per API RP 5L2 / ISO 15741)
3. 20_API_5L_Dual_Layer_FBE_Coated_Gas_Pipeline_ITP.pdf (Dual-Layer FBE / ARO Coating per CSA Z245.20 / NACE SP0394)
4. 21_API_5L_56in_X80_Heavy_Wall_Gas_Mainline_ITP.pdf (56" X80 Ultra-High Pressure Gas Transmission Bare Pipe per API 5L PSL 2)
"""

import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def build_itp_pdf(filename: str, project_title: str, pipe_info: str, standard_info: str, items: list):
    os.makedirs('itp_sample_library', exist_ok=True)
    filepath = os.path.join('itp_sample_library', filename)
    
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(letter),
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ITPTitle',
        parent=styles['Heading1'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'ITPSubTitle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )
    table_hdr_style = ParagraphStyle(
        'ITPHdr',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    table_cell_style = ParagraphStyle(
        'ITPCell',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1e293b')
    )
    
    story = []
    
    # Header
    story.append(Paragraph(f'<b>{project_title}</b>', title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'<b>Pipe & Coating Description:</b> {pipe_info} &nbsp;|&nbsp; <b>Governing Codes:</b> {standard_info}', subtitle_style))
    story.append(Spacer(1, 8))
    
    # Table Data
    table_data = [
        [
            Paragraph('<b>No</b>', table_hdr_style),
            Paragraph('<b>Inspection / Test Stage</b>', table_hdr_style),
            Paragraph('<b>Frequency & Sampling</b>', table_hdr_style),
            Paragraph('<b>Location & Specimen</b>', table_hdr_style),
            Paragraph('<b>Test Standard & Procedure</b>', table_hdr_style),
            Paragraph('<b>Specified Acceptance Criteria & Tolerances</b>', table_hdr_style),
            Paragraph('<b>Governing Clause</b>', table_hdr_style),
            Paragraph('<b>Hold / Witness</b>', table_hdr_style),
        ]
    ]
    
    for row in items:
        table_data.append([
            Paragraph(str(row[0]), table_cell_style),
            Paragraph(f'<b>{row[1]}</b>', table_cell_style),
            Paragraph(row[2], table_cell_style),
            Paragraph(row[3], table_cell_style),
            Paragraph(row[4], table_cell_style),
            Paragraph(row[5], table_cell_style),
            Paragraph(row[6], table_cell_style),
            Paragraph(row[7], table_cell_style),
        ])
    
    col_widths = [20, 125, 105, 105, 90, 185, 75, 55]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    story.append(t)
    doc.build(story)
    print(f'Generated: {filepath} ({os.path.getsize(filepath)} bytes)')


def generate_gas_pipeline_itps():
    # 18. 3LPE External Polyethylene Coated Gas Line Pipe ITP
    build_itp_pdf(
        filename='18_API_5L_42in_X70_3LPE_Polyethylene_Coated_Gas_Mainline_ITP.pdf',
        project_title='NATURAL GAS TRANSMISSION MAINLINE - 3LPE EXTERNAL COATING QUALITY PLAN (ITP)',
        pipe_info='42" (1067 mm) x 15.90 mm, Grade X70M PSL 2 SAWH/LSAW with 3LPE External Coating (Class v Reinforced)',
        standard_info='ISO 21809-1 / DIN 30670 / API Spec 5L 47th Ed. / BOTAŞ Specification',
        items=[
            ['1', 'Raw Material Verification (HDPE, Adhesive, FBE)', 'Every batch/delivery lot of coating materials', 'Manufacturer raw batch samples', 'ISO 21809-1 Table 1 & DIN 30670', 'FBE: Gel time, moisture <= 0.5%, DSC Tg; Adhesive: MFR, density; PE: Density >= 0.940 g/cm3, MFR 0.2-0.7 g/10min, carbon black 2.0-2.5%, EN 10204 3.1 certs', 'ISO 21809-1 Cl. 6', 'H/R'],
            ['2', 'Bare Pipe Receipt & Pre-Washing', '100% bare pipe joints before entry', 'External pipe surface', 'SSPC-SP 1 / ISO 8504', 'No oil, grease, salt, lacquers, slivers or surface gouges; high-pressure potable water wash to remove contaminants', 'ISO 21809-1 Cl. 8.1', 'W'],
            ['3', 'Pipe Pre-Heating Prior to Blasting', 'Continuous monitoring all pipes', 'Pipe exterior surface', 'Optical Pyrometer', 'Steel temperature 40 °C - 60 °C and minimum 3 °C above ambient dew point to ensure completely dry surface', 'DIN 30670 Cl. 4.2', 'W'],
            ['4', 'Abrasive Blast Cleaning', '100% of all pipes (continuous run)', 'Full external steel surface', 'ISO 8501-1 / SSPC-SP 10', 'Cleanliness: Sa 2.5 (Near-White Metal). Steel grit/shot mix; free of mill scale, rust, and surface defects', 'ISO 21809-1 Cl. 8.2', 'H/W'],
            ['5', 'Surface Anchor Profile Measurement', 'Twice per 8-hour shift (3 pipes each)', 'Replica Tape (Press-O-Film)', 'ISO 8503-2 / ASTM D4417 Method C', 'Surface roughness profile: Rz 60 µm - 100 µm with sharp angular profile for optimal FBE mechanical interlock', 'ISO 21809-1 Table 2', 'W'],
            ['6', 'Residual Dust Level Inspection', 'At start of shift and every 2 hours', 'Dust tape on blasted surface', 'ISO 8502-3', 'Dust rating: Maximum Class 1 or Class 2; blown clean with dry oil-free compressed air', 'ISO 8502-3', 'W'],
            ['7', 'Water-Soluble Salt Contamination Test', '3 tests per shift (at pipe ends & middle)', 'Bresle Patch & conductivity meter', 'ISO 8502-6 / ISO 8502-9', 'Residual chloride/salt level: <= 20 mg/m² (2.0 µg/cm²). If exceeded, re-wash with DI water and re-blast', 'ISO 21809-1 Cl. 8.2.3', 'H/W'],
            ['8', 'Chemical Surface Pre-Treatment', 'Continuous monitoring of bath & pipe', 'Acid wash or chromate spray', 'Supplier Spec / Deionised rinse', 'Phosphoric acid or chromate pre-treatment followed by DI water rinse; surface conductivity < 50 µS/cm', 'ISO 21809-1 Cl. 8.2.4', 'W'],
            ['9', 'Induction Heating for FBE Coating', 'Continuous pyrometer & infrared logger', 'Full pipe circumference', 'Multi-point optical pyrometer', 'Steel temperature 190 °C - 220 °C (maximum allowable 230 °C). Overheating > 240 °C causes rejection', 'ISO 21809-1 Cl. 8.3', 'H/W'],
            ['10', 'Fusion Bonded Epoxy (FBE) Application', 'Continuous electrostatic powder spray', 'First layer on pre-heated steel', 'Electrostatic spray guns', 'Dry film thickness (DFT): 150 µm - 250 µm (target 200 µm). Uniform cloud, partial cure verification', 'ISO 21809-1 Table 2', 'W'],
            ['11', 'Grafted Copolymer Adhesive Extrusion', 'Continuous side-wrap extrusion', 'Second layer over partially cured FBE', 'Flat die / crosshead extruder', 'Adhesive thickness: 150 µm - 250 µm (target 200 µm). Full fusion with FBE before epoxy full cure', 'ISO 21809-1 Table 2', 'W'],
            ['12', 'Polyethylene (HDPE) Topcoat Application', 'Continuous circumferential wrapping', 'Outer third protective layer', 'Side extrusion + silicone roller', 'Total 3LPE thickness: Minimum 3.0 mm (Reinforced Class v / Class C); weld seam min 85% of nominal body', 'DIN 30670 / ISO 21809-1', 'H/W'],
            ['13', 'Water Quench Cooling & Temperature', '100% coated pipes through quench trough', 'Full pipe length', 'Infrared Thermometer', 'Controlled water cooling; pipe surface temperature reduced to < 60 °C before conveyor handling and stenciling', 'DIN 30670 Cl. 4.4', 'W'],
            ['14', '100% Online Holiday Detection', 'Every coated pipe (100% full surface)', 'Full 360° coating surface', 'NACE SP0188 / ISO 21809-1', 'High-voltage spark testing: 25 kV (or 5 kV/mm). ZERO holidays / pinholes permitted per pipe length', 'DIN 30670 Cl. 5.3', 'H/W'],
            ['15', 'Total Coating Thickness (DFT) Scanning', '100% of all pipes (4 points per length)', 'Clock positions 12, 3, 6, 9 o clock', 'Magnetic/Eddy-current thickness gauge', 'Minimum total thickness: >= 3.0 mm on body, >= 2.5 mm on weld seam. No under-thickness permitted', 'DIN 30670 Table 3', 'W'],
            ['16', 'Peel Adhesion (Peel Strength) Testing', '1 test per 50 pipes (or 1 per 4 hours)', 'Test ring from cutback or pipe end', 'ISO 21809-1 Annex C / DIN 30670', 'At 23 °C: Minimum 35 N/cm; At 50 °C: Minimum 15 N/cm. Failure mode: Cohesive within adhesive/PE (no steel disbond)', 'ISO 21809-1 Annex C', 'H/W'],
            ['17', 'Cathodic Disbondment Test', '1 test per lot / qualification batch', 'Laboratory coupon from production pipe', 'ISO 21809-1 Annex H / ASTM G8', '28 days at 23 °C: Disbondment radius <= 7.0 mm; 48 hours at 65 °C: Disbondment radius <= 7.0 mm', 'ISO 21809-1 Table 4', 'H/W'],
            ['18', 'Impact Resistance & Indentation Hardness', '1 test per lot / shift', 'Production pipe sample', 'ISO 21809-1 Annex E & F', 'Impact resistance: >= 7.0 J/mm (zero holiday at 25 kV after impact); Indentation depth: <= 0.2 mm at 23 °C', 'DIN 30670 Cl. 5.5', 'W'],
            ['19', 'Elongation at Break (PE Layer)', '1 test per raw material lot', 'Dumbbell specimen from outer PE', 'ISO 527-2 / DIN 30670', 'Tensile elongation at break: Minimum >= 400% at 23 °C (demonstrating cold-bending ductile flexibility)', 'DIN 30670 Table 2', 'W'],
            ['20', 'End Cutback & Bevel Chamfer Geometry', '100% both ends of each pipe', 'Pipe ends (internal & external)', 'Vernier Caliper / Depth Gauge', 'Cutback length: 150 mm +- 20 mm; Chamfer angle: <= 30°; bare steel free of coating residue, bevel protector installed', 'ISO 21809-1 Cl. 8.4', 'W'],
            ['21', 'Coating Repair Inspection', 'All repaired areas (if applicable)', 'Repaired defect patches', 'ISO 21809-1 Cl. 8.5 / DIN 30670', 'Max defect size <= 100 cm2, max 2 repairs per pipe. Melt stick + PE patch; 100% holiday re-tested at 25 kV', 'DIN 30670 Cl. 5.6', 'W'],
            ['22', 'Final Visual, Stenciling & Release', '100% of all finished coated pipes', 'Pipe body and internal bore', 'Visual / Project Stencil Spec', '100% visual inspection; UV-resistant white paint stencil; heavy-duty end caps fitted; EN 10204 3.1 3LPE cert', 'ISO 21809-1 Cl. 11', 'H/W']
        ]
    )

    # 19. Internal Flow Efficiency Liquid Epoxy Coating ITP
    build_itp_pdf(
        filename='19_API_RP_5L2_Internal_Flow_Efficiency_Epoxy_Coated_Gas_Pipe_ITP.pdf',
        project_title='HIGH-PRESSURE GAS TRANSMISSION - INTERNAL FLOW COATING QUALITY PLAN (ITP)',
        pipe_info='36" (914.4 mm) x 14.30 mm, Grade X65M PSL 2 with Internal Flow Efficiency Liquid Epoxy Coating',
        standard_info='API RP 5L2 4th Ed. / ISO 15741 / BOTAŞ / Shell DEP 31.40.20.37',
        items=[
            ['1', 'Liquid Epoxy Material Verification', 'Every incoming batch of base & curing agent', 'Manufacturer QC batch certificate', 'API RP 5L2 / ISO 15741', 'Two-pack polyamide/amine cured epoxy. Non-volatile solids >= 60% by vol, pot life >= 2 hrs, flash point > 25 °C, EN 10204 3.1 cert', 'API RP 5L2 Cl. 2', 'H/R'],
            ['2', 'Internal Surface Pre-Cleaning', '100% pipe internal bore', 'Full inside surface', 'SSPC-SP 1 Solvent Wipe', 'Internal bore free of rust lumps, grease, lubricants, protective lacquers; washed with clean solvent or alkaline wash', 'ISO 15741 Cl. 6.1', 'W'],
            ['3', 'Internal Abrasive Blast Cleaning', '100% of all pipes (automated lance)', 'Full internal pipe wall', 'ISO 8501-1 / SSPC-SP 10', 'Cleanliness: Sa 2.5 (Near-White Metal). Free from all mill scale, oxides, and rust stains; uniform matte finish', 'API RP 5L2 Cl. 3.1', 'H/W'],
            ['4', 'Internal Surface Roughness & Profile', 'At start of shift and every 2 hours', 'Replica Tape (Press-O-Film)', 'ISO 8503-2 / ASTM D4417', 'Anchor pattern profile: Rz 25 µm - 50 µm (target 35 µm). Sharp profile without rolled-over steel peaks', 'ISO 15741 Cl. 6.2', 'W'],
            ['5', 'Internal Dust & Soluble Salt Removal', '100% pipes air blow + 2 Bresle tests/shift', 'Internal bore & pipe ends', 'ISO 8502-3 / ISO 8502-6/9', 'Dust level Class 1 max (vacuum cleaned); Residual soluble salts <= 20 mg/m² (conductance check)', 'ISO 15741 Cl. 6.3', 'W'],
            ['6', 'Environmental Application Conditions', 'Continuous logging during application', 'Coating bay environment', 'Digital Psychrometer / Dew Check', 'Substrate temp >= 10 °C and MINIMUM 3 °C above dew point; Relative Humidity (RH) <= 80%; ambient temp 10-40 °C', 'API RP 5L2 Cl. 3.2', 'W'],
            ['7', 'Automated Internal Spray Application', '100% of all pipes (automated lance boom)', 'Full internal length', 'Airless Spray System', 'Uniform travel speed and rotation; wet film thickness (WFT) monitored continuously during application pass', 'API RP 5L2 Cl. 3.3', 'W'],
            ['8', 'Dry Film Thickness (DFT) Verification', '100% of all pipes (12 points per pipe)', 'Clock positions at ends and center', 'ISO 2808 / SSPC-PA 2', 'Dry film thickness (DFT): Nominal 50 µm - 75 µm (minimum 40 µm, maximum 100 µm). Zero runs, sags, or blisters', 'API RP 5L2 Cl. 3.4', 'H/W'],
            ['9', 'Surface Roughness of Cured Coating', '1 pipe per 50 pipes (or 1 per shift)', 'Internal coated surface', 'Stylus Profilometer (ISO 4287)', 'Cured coating surface roughness: Rz <= 25 µm, Ra <= 3.0 µm (guaranteeing >= 5% gas throughput increase)', 'ISO 15741 Cl. 7.2', 'H/W'],
            ['10', 'Degree of Cure (Solvent Rub Test)', '1 pipe per shift / test unit', 'Cured internal coating surface', 'ASTM D4752 / ISO 15741 Annex C', '50 double rubs with MEK (Methyl Ethyl Ketone) soaked rag; no coating softening, stickiness, or pigment removal', 'ISO 15741 Annex C', 'H/W'],
            ['11', 'Cross-Hatch Adhesion Test', '1 test per shift (on cutback ring)', 'Internal coated test coupon', 'ISO 2409 / ASTM D3359 Method B', 'Cross-cut adhesion rating: Class 0 (100% lattice squares completely intact, no flaking along incisions)', 'API RP 5L2 Cl. 4.2', 'H/W'],
            ['12', 'Resistance to Gas Decompression (Blistering)', 'Qualification test per paint system', 'Pressure autoclave laboratory cell', 'ISO 15741 Annex D', 'Decompression from 100 bar natural gas/nitrogen at 10 bar/min; 10 cycles; ZERO blistering or loss of adhesion', 'ISO 15741 Annex D', 'H/R'],
            ['13', 'Internal Cutback & Bevel Protection', '100% both ends of each pipe', 'Both internal pipe ends', 'Steel rule / masking gauge', 'Internal coating cutback: 50 mm +- 10 mm from pipe face for field girth welding; edges feathered smoothly', 'API RP 5L2 Cl. 3.5', 'W'],
            ['14', 'Internal Holiday & Pinhole Inspection', 'Spot check 1 pipe per 10 pipes (or 100%)', 'Full internal coated length', 'Low-voltage sponge tester (67.5 V)', 'Low voltage wet-sponge detector; zero continuous pinholes or conductive defects through to steel substrate', 'NACE SP0188', 'W'],
            ['15', 'Internal Cleanliness & Cap Installation', '100% of finished line pipes', 'Internal bore & bevels', 'Visual / End cap verification', 'Internal bore blown completely clean and dry; UV-stabilized heavy duty polyethylene bevel caps strapped securely', 'API RP 5L2 Cl. 5', 'W']
        ]
    )

    # 20. Dual-Layer Fusion Bonded Epoxy (2L-FBE / ARO) Coated Gas Pipeline ITP
    build_itp_pdf(
        filename='20_API_5L_Dual_Layer_FBE_Coated_Gas_Pipeline_ITP.pdf',
        project_title='HDD & ROAD CROSSING GAS PIPELINE - DUAL-LAYER FBE (FBE+ARO) QUALITY PLAN (ITP)',
        pipe_info='30" (762 mm) x 12.70 mm, Grade X60M PSL 2 with Dual-Layer FBE Coating (Corrosion Base + Abrasion Overcoat ARO)',
        standard_info='CSA Z245.20 / NACE SP0394 / ISO 21809-2 / API Spec 5L 47th Ed.',
        items=[
            ['1', 'FBE Powder & ARO Overcoat Verification', 'Each batch lot of Base FBE & ARO powder', 'Manufacturer quality certificates', 'CSA Z245.20 / ISO 21809-2', 'Base FBE: Gel time, moisture <= 0.50%, Delta Tg (-2 °C to +3 °C); ARO: High-abrasion/gouge resistant resin, EN 10204 3.1 cert', 'CSA Z245.20 Cl. 6', 'H/R'],
            ['2', 'Bare Pipe Incoming & Blast Cleaning', '100% of all pipes', 'External steel surface', 'ISO 8501-1 / SSPC-SP 10', 'Solvent clean (SSPC-SP 1) + Near-White Blast Sa 2.5; Sharp angular profile Rz 60 µm - 90 µm; Chlorides <= 20 mg/m²', 'CSA Z245.20 Cl. 8', 'H/W'],
            ['3', 'Chemical Pre-Treatment & Induction Heating', 'Continuous monitoring all pipes', 'Full pipe circumference', 'Optical Pyrometer', 'Deionised water rinse + Chromate/Silane pre-treatment; Medium frequency induction heat: 230 °C - 245 °C (max 250 °C)', 'NACE SP0394 Cl. 4', 'H/W'],
            ['4', 'Dual-Layer Electrostatic Spray Application', 'Continuous tandem spray booths', 'Outer pipe surface', 'Electrostatic powder guns', 'Booth 1: Base corrosion FBE (350 - 450 µm) -> Immediate Booth 2: Tough ARO overcoat (400 - 550 µm) before base gelation', 'CSA Z245.20 Cl. 9', 'W'],
            ['5', 'Water Quench Cooling & Cure Assessment', '100% pipes quench trough + DSC on sample', 'Pipe surface / cure sample', 'DSC Thermal Analysis (Tg)', 'Quench to < 90 °C; Thermal analysis DSC: Glass transition Delta Tg within -2 °C to +3 °C (confirming full cure)', 'CSA Z245.20 Cl. 12.7', 'H/W'],
            ['6', '100% High-Voltage Holiday Detection', 'Every coated pipe (100% full surface)', 'Full 360° coating exterior', 'NACE SP0188 / CSA Z245.20', 'High voltage spark tester: 5.0 V/µm of total thickness (approx 4.0 kV - 4.5 kV). ZERO holidays allowed per pipe', 'CSA Z245.20 Cl. 12.8', 'H/W'],
            ['7', 'Total Coating Thickness (DFT) Verification', '100% of all pipes (12 points around body)', 'Both ends, quarter points, middle', 'SSPC-PA 2 / CSA Z245.20', 'Total DFT: 750 µm - 1000 µm (Base FBE >= 350 µm, ARO Overcoat >= 400 µm). Minimum individual reading >= 700 µm', 'CSA Z245.20 Table 2', 'W'],
            ['8', 'Cross-Section Porosity & Interface Rating', '1 test per shift (on ring coupon)', 'Microscope cross section (30x)', 'CSA Z245.20 Cl. 12.10', 'Cross section foam porosity rating <= 3; Steel-to-coating interface porosity rating <= 2 (no continuous voids)', 'CSA Z245.20 Cl. 12.10', 'W'],
            ['9', 'Cold Flexibility / Mandrel Bend Test', '1 test per shift / lot', 'Laboratory bend strap at -30 °C', 'CSA Z245.20 Cl. 12.11', 'Bend deflection: 2.5° per pipe diameter at -30 °C; ZERO cracking, tearing, or disbonding on tension surface', 'CSA Z245.20 Table 4', 'H/W'],
            ['10', 'Gouge Resistance & Impact Testing', 'Qualification / 1 test per 100 pipes', 'Laboratory coupon', 'ASTM G14 / CSA Z245.20', 'Impact resistance: >= 3.0 Joules at -30 °C (no holiday); Gouge depth: <= 0.25 mm under 50 kg hardened stylus load', 'CSA Z245.20 Cl. 12.12', 'H/W'],
            ['11', 'Cathodic Disbondment Testing (28d & 24h)', '1 test per lot / qualification batch', 'Laboratory electrochemical cell', 'CSA Z245.20 Cl. 12.9', '28 days at 20 °C: Disbondment radius <= 6.5 mm; 24 hours accelerated at 95 °C: Disbondment radius <= 5.0 mm', 'CSA Z245.20 Table 4', 'H/W'],
            ['12', 'Cutback, Stenciling & Final Acceptance', '100% of all finished coated pipes', 'Pipe ends & exterior surface', 'Visual & Gauge check', 'Coating cutback: 75 mm +- 15 mm; bevels clean and rust-inhibited; color coded green/blue band; EN 10204 3.1 cert', 'CSA Z245.20 Cl. 13', 'H/W']
        ]
    )

    # 21. 56" X80 Ultra-High Pressure Gas Transmission Bare Pipe ITP
    build_itp_pdf(
        filename='21_API_5L_56in_X80_Heavy_Wall_Gas_Mainline_ITP.pdf',
        project_title='MEGA-GAS TRANSMISSION SYSTEM (120 BAR) - 56" X80M PSL 2 QUALITY PLAN (ITP)',
        pipe_info='56" (1422 mm) x 25.40 mm, Grade X80M PSL 2, SAWL / SAWH (Heavy-Wall Ultra-High Pressure Mainline)',
        standard_info='API Spec 5L 47th Ed. / ISO 3183 PSL 2 / High-Pressure Gas Pipeline Code',
        items=[
            ['1', 'Ladle Heat Chemical Analysis (Ultra-Clean)', 'One analysis per heat of steel', 'Ladle vacuum sample', 'ASTM A751 / ISO 14284', 'C <= 0.07%, Si <= 0.35%, Mn: 1.65-1.90%, P <= 0.012%, S <= 0.0020%, Nb+V+Ti <= 0.15%, CE_Pcm <= 0.19, CE_IIW <= 0.40', 'API 5L Tablo 5', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit (lot <= 50 pipes)', 'Pipe body coupon', 'ISO 14284 / OES', 'C <= 0.07%, P <= 0.012%, S <= 0.0020%, CE_Pcm <= 0.19 (verifying strict low-carbon weldability)', 'API 5L Tablo 5', 'W'],
            ['3', 'Pipe Body Heavy-Wall Tensile Test', 'Once per test unit (lot of <= 50 pipes)', 'Transverse rectangular strap', 'ISO 6892-1 / ASTM A370', 'Rt0.5: 555 - 705 MPa (80.5-102.2 ksi), Rm: 625 - 825 MPa, Af >= 18.0%, Yield-to-Tensile Ratio Y/T <= 0.90', 'API 5L Tablo 7', 'H/W'],
            ['4', 'Weld Seam Tensile Test', 'Once per test unit', 'Transverse weld coupon', 'ASTM A370', 'Tensile strength Rm >= 625 MPa across submerged arc weld seam (failure must occur outside weld)', 'API 5L Tablo 7', 'W'],
            ['5', 'Ultra-Tough CVN Charpy Impact Test at -20 °C', '1 set body + 1 set weld + 1 set HAZ at -20 °C', 'Transverse Charpy V (10x10 mm)', 'ISO 148-1 / ASTM A370', 'At -20 °C: Body Min Avg 100 Joules, Min Ind 80 Joules; Weld & HAZ: Min Avg 60 Joules, Min Ind 45 Joules', 'API 5L Tablo 8 & Spec', 'H/W'],
            ['6', 'Drop Weight Tear Test (DWTT) at -10 °C', 'Once per heat at -10 °C (2 specimens)', 'Transverse full thickness DWTT', 'API RP 5L3 / ASTM E436', 'At -10 °C: Average shear fracture area >= 85%, No single specimen < 70% (arresting brittle running fractures)', 'API 5L Tablo 18', 'H/W'],
            ['7', 'Guided-Bend Test (Side Bend for Heavy-Wall)', '2 side-bend specimens per test unit', 'Transverse weld cross section', 'ISO 5173 / ASTM A370', '180° bend around mandrel; ZERO crack opening > 3.2 mm in weld metal or fusion boundary HAZ', 'API 5L 9.10', 'W'],
            ['8', 'Macro Hardness Survey (HV10)', 'Once per test unit (16-point survey)', 'Cross section macro etch', 'ISO 6507-1 / ASTM E384', 'Maximum 280 HV10 across Body, HAZ, Inner weld and Outer weld cap (preventing hard spot cracking)', 'API 5L 10.2.4.8', 'W'],
            ['9', 'Residual Stress Slitting Ring Test', 'Mandatory 1 test per heat', '150 mm wide ring opposite weld', 'Project Specification', 'Slitting ring opening: Internal hoop stress <= 0.10 x SMYS (Maximum 55.5 MPa)', 'API 5L / BOTAŞ Spec', 'H/W'],
            ['10', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all 56" heavy-wall pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 100% SMYS (190.5 bar), Tutma Süresi: MINIMUM 20 SECONDS (+0 / -2 bar calibration)', 'API 5L 10.2.6.2', 'H/W'],
            ['11', 'Weld Seam 100% Multi-Probe Automated UT', '100% full length of SAW weld seam', 'Full weld seam & HAZ', 'ISO 10893-11 Level U2', '100% multi-channel phased array / pulse-echo AUT + TOFD for mid-wall defect sizing and root fusion', 'API 5L Ek E', 'H/W'],
            ['12', 'Offline Radiographic Testing (RT)', 'Pipe ends (200 mm) & repair locations', 'Weld seam ends and weld repairs', 'ISO 10893-6 Class B', '100% digital radioscopy or X-ray film Class B; no cracks, lack of fusion, or slag exceeding Class B limits', 'API 5L Ek E', 'H/W'],
            ['13', 'Full Body Plate & Pipe Ends Laminar AUT', '100% full plate area + 100% pipe ends', 'Plate body & 100 mm pipe ends', 'ISO 10893-9 / ISO 10893-8', 'Plate body: 100% scanned (ISO 10893-9 Class E1); Pipe ends: 100 mm circumferential band (no defect > 4 mm)', 'API 5L Ek E.8', 'W'],
            ['14', 'Automated Laser Geometry & Ovality Station', '100% of all pipes (continuous laser)', 'Pipe body, ends, and weld crown', 'Optical Laser Profiler', 'Body OD: +-0.35%; End Out-of-Roundness (Ovality) <= 2.5 mm; Straightness <= 0.10% L; Radial offset <= 1.5 mm', 'API 5L Tablo 10/16', 'W'],
            ['15', 'Wall Thickness Verification (Heavy-Wall)', '100% of all pipes (automated UT scanning)', 'Pipe body & ends', 'API 5L 10.2.8.2', 'Nominal t = 25.40 mm; Tolerance: -5.0% / +10.0% (Acceptance: 24.13 mm to 27.94 mm)', 'API 5L Tablo 11', 'W'],
            ['16', 'Weighing & Mass Tolerance', '100% of all pipes (certified load cells)', 'Pipe scale', 'API 5L 9.11.2', 'Single pipe mass tolerance: -3.5% / +10.0% of theoretical calculated mass (876.3 kg/m)', 'API 5L 9.11.2', 'W'],
            ['17', 'Visual Surface Inspection & Weld Seam Cap', '100% internal and external surface', 'Full inside & outside pipe', 'API 5L 10.2.7', '100% visual inspection; weld crown height <= 3.0 mm; zero arc burns, scabs, gouges, or slivers', 'API 5L 9.12', 'W'],
            ['18', 'Residual Magnetism & Final Release', '100% of all pipe ends before loadout', 'Pipe ends (4 quadrature points)', 'Gaussmeter / Hall effect probe', 'Residual magnetism: Maximum average <= 2.0 mT (20 Gauss), individual <= 2.5 mT; EN 10204 3.2 cert', 'API 5L 10.2.8.5', 'H/W']
        ]
    )


if __name__ == '__main__':
    generate_gas_pipeline_itps()
