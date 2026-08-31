"""
Generator script for 12 authentic API 5L, BOTAŞ, and international line pipe Inspection & Test Plan (ITP) PDF documents.
Saves all generated ITP PDFs into the itp_sample_library/ directory.
"""

import os
import sys
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
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'ITPSubTitle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )
    table_hdr_style = ParagraphStyle(
        'ITPHdr',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    table_cell_style = ParagraphStyle(
        'ITPCell',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1e293b')
    )
    
    story = []
    
    # Header
    story.append(Paragraph(f'<b>{project_title}</b>', title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f'<b>Pipe Description:</b> {pipe_info} &nbsp;|&nbsp; <b>Governing Standard:</b> {standard_info}', subtitle_style))
    story.append(Spacer(1, 10))
    
    # Table Data
    table_data = [
        [
            Paragraph('<b>No</b>', table_hdr_style),
            Paragraph('<b>Inspection / Test Activity</b>', table_hdr_style),
            Paragraph('<b>Frequency & Extent</b>', table_hdr_style),
            Paragraph('<b>Sampling Location & Specimen</b>', table_hdr_style),
            Paragraph('<b>Test Method / Standard</b>', table_hdr_style),
            Paragraph('<b>Acceptance Criteria & Specified Limits</b>', table_hdr_style),
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
    
    col_widths = [22, 130, 110, 110, 85, 175, 75, 55]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(t)
    doc.build(story)
    print(f'Generated: {filepath} ({os.path.getsize(filepath)} bytes)')


def generate_all_12_itps():
    # 1. BOTAŞ 48" X65 SAWH Pipeline ITP
    build_itp_pdf(
        filename='01_BOTAS_48in_X65_SAWH_Mainline_ITP.pdf',
        project_title='BOTAŞ DOĞAL GAZ İLETİM HATTI PROJESİ - İMALATÇI ITP PLANI',
        pipe_info='48" (1219 mm) x 14.30 mm, Grade X65 PSL 2, SAWH (Helisel Tozaltı Kaynaklı)',
        standard_info='BOTAŞ 4-NGTL-0-GN-P-002-5120 Rev. 7 / API Spec 5L 47th Ed.',
        items=[
            ['1', 'Hammadde Döküm Analizi (Ladle Heat Analysis)', 'Hammadde için her dökümde (per heat) 1 analiz', 'Pota / Çelik döküm numunesi', 'ASTM A751 / ISO 14284', 'C <= 0.16%, P <= 0.025%, S <= 0.010%, N <= 0.009%, Nb+V+Ti <= 0.15%, CE_IIW <= 0.40', 'Madde 3.2.1', 'H/W'],
            ['2', 'Boru Ürün Analizi (Product Chemical Analysis)', 'Ebat bazında her test ünitesi (lot) için 2 analiz', 'Boru gövdesinden 2 ayrı numune', 'ISO 14284 / OES', 'C <= 0.16%, P <= 0.025%, S <= 0.010%, CE_Pcm <= 0.22', 'Madde 3.2.2.4', 'W'],
            ['3', 'Gövde Çekme Testi (Body Tensile Test)', 'Her test ünitesi (lot) için 2 set (1 set test, 1 set 5 yıl saklama)', 'Enine gövde numunesi (kaynaktan 90°)', 'ISO 6892-1 / ASTM A370', 'Rt0.5 >= 450 MPa, Rm: 535-760 MPa, Af >= 19.5%, Y/T <= 0.90 (unexpanded)', 'Madde 3.3.1.4 & Tablo 2', 'H/W'],
            ['4', 'Kaynak Çekme Testi (Weld Tensile Test)', 'Her test ünitesi (lot) için 2 set numune', 'Enine kaynak dikişi numunesi', 'ISO 6892-1 / ASTM A370', 'Rm >= 535 MPa (Gövde asgari dayanımını karşılamalıdır), Kopma uzaması >= %10', 'Madde 3.3.2.1 & Tablo 2', 'W'],
            ['5', 'Gövde Çentik Darbe Testi (CVN Body Impact)', 'Her test ünitesi için 1 set (3 numune) -20 °C', 'Gövde enine V-çentik numune (10x10 mm)', 'ISO 148-1 / ASTM A370', 'Test Sıcaklığı: -20 °C. Asgari Ortalama: 60 Joule, Münferit Tekil: 45 Joule', 'Madde 3.3.5 & Tablo 3', 'H/W'],
            ['6', 'Kaynak & ITAB Çentik Darbe (CVN Weld & HAZ)', 'Her test ünitesi için 1 set kaynak + 1 set ITAB -20 °C', 'Kaynak ekseni ve ITAB füzyon hattı', 'ISO 148-1 / ASTM A370', 'Test Sıcaklığı: -20 °C. Asgari Ortalama: 45 Joule, Münferit Tekil: 34 Joule', 'Madde 3.3.5 & Tablo 3', 'H/W'],
            ['7', 'DWTT (Düşen Ağırlık Yırtılma Testi)', 'Her döküm / test ünitesi için 1 test (2 numune) 0 °C', 'Enine tam kalınlık DWTT numunesi', 'API RP 5L3 / ASTM E436', 'Test Sıcaklığı: 0 °C. Ortalama sünek kırılma >= %85, Münferit tekil numune >= %60', 'Madde 3.3.6.4', 'H/W'],
            ['8', 'Kılavuzlu Bükme Testi (Guided-Bend)', 'Her test ünitesi için 1 set (1 kök + 1 kapak)', 'Enine kaynak dikişi bükme numunesi', 'ISO 5173 / ASTM A370', '180° bükme sonrası kaynak ve ITAB da > 3.2 mm çatlak/kusur oluşmayacaktır', 'API 5L 9.9 / BOTAŞ 3.1.6', 'W'],
            ['9', 'Sertlik Testi (Hardness Testing)', 'Her test ünitesi için 1 enine kesit makro sertlik', 'Gövde, ITAB ve Kaynak dikişi (HV10)', 'ISO 6507-1 / ASTM E384', 'Maksimum 300 HV10. (Aşılması halinde dökümdeki boruların %100 ü test edilir)', 'Madde 3.3.7', 'H/W'],
            ['10', 'Artık Stres Testi (Residual Stress Ring Test)', 'Her çap ve et kalınlığı ve HER DÖKÜMDE (HEAT) zorunlu', '150 mm genişlikte halka kesme', 'BOTAŞ Madde 3.3.9', 'S = (E*t*C) / (12.566*D^2) <= 0.10 x SMYS (Maksimum 45 MPa)', 'Madde 3.3.9', 'H/W'],
            ['11', 'Fabrika Hidrostatik Basınç Testi', 'İstisnasız her boru (%100 tüm borular)', 'Tüm boru gövdesi ve kaynakları', 'API 5L 10.2.6 / BOTAŞ 8.4', 'Test Basıncı: SMYS %100 (109.8 bar). Tutma Süresi: EN AZ 20 SANİYE (+0/-2 bar)', 'Madde 8.4.1 & 8.4.2', 'H/W'],
            ['12', 'Kaynak Dikişi %100 NDT (Online UT + Offline RT)', 'Her boru tam boy kaynak dikişi (%100)', 'Online UT + Tamir/Hidro sonrası Offline RT', 'ISO 10893-11 / ISO 10893-6', 'Tam boy Online UT + Onaylı NDT seviyesi. Uçlarda ve şüpheli yerlerde RT', 'Madde 8.8.4.2 & 8.8.4.3', 'H/W'],
            ['13', 'Boru Gövdesi UT Laminasyon Muayenesi', 'Boru gövdesi yüzeyinin EN AZ %40 ı taranacak şekilde', 'Boru gövde yüzeyi', 'ISO 12094 B1 / BOTAŞ 8.8.4.4', 'Gövde yüzeyinin en az %40 ı taranacak, laminasyon hataları reddedilir', 'Madde 8.8.4.4.1', 'W'],
            ['14', 'Boru Uçları Laminasyon NDT (UT)', 'İstisnasız her boru (%100) uç kısımları', 'Boru uçlarında asgari 50 mm genişlikte bant', 'ISO 10893-8 / ISO 12094', 'Boru uçlarında en az 50 mm çevre boyunca laminasyon kusuru bulunmayacaktır', 'Madde 8.8.4.4.2', 'W'],
            ['15', 'Dış Çap, Ovallik ve Geometrik Muayene', 'Her boruda %100 boyutsal ve dairesellik ölçümü', 'Boru gövdesi ve boru uçları', 'API 5L 10.2.8 / BOTAŞ 5.1', 'Boru ucu ovallik: API 5L Çizelge 10 limitlerinin %50 si (Yarısı). Dış çap: +- %0.5', 'Madde 5.1 & 8.1.2', 'W'],
            ['16', 'Et Kalınlığı Ölçümü (Wall Thickness)', 'İstisnasız her boruda (%100 ultrasonik/ölçer)', 'Boru gövdesi ve boru uçları', 'API 5L Tablo 11 / BOTAŞ 5.2', 'Nominal et kalınlığı: 14.30 mm. Tolerans: API 5L Tablo 11 (-%8.0 / +%15.0)', 'Madde 5.2 (Tablo 4)', 'W'],
            ['17', 'Doğrusallık, Boy ve Alın Kaynak Ağzı', 'İstisnasız her boruda (%100)', 'Tam boy ve boru uçları', 'BOTAŞ Madde 5.4, 5.5, 7.2', 'Doğrusallıktan sapma <= %0.10 x L. Ağız açısı: 30° (+5°/-0°), Kök yüzeyi: 1.6 +- 0.8 mm', 'Madde 5.4 & 5.5', 'W'],
            ['18', 'Görsel Yüzey Muayenesi (Visual Inspection)', 'İstisnasız her boruda (%100 iç ve dış yüzey)', 'İç ve dış tüm boru yüzeyi', 'API 5L 10.2.7 / BOTAŞ 8.1.2', 'D >= 20" borularda %100 iç ve dış görsel kontrol; çatlak, katmer, kabuk yasaktır', 'Madde 8.1.2', 'W'],
            ['19', 'Kalıntı Manyetizma Ölçümü', 'Vardiyada EN AZ İKİ DEFA ve sevkiyat öncesi her boru', 'Boru uçları (çevresel 4 nokta)', 'API 5L 10.2.8.5 / BOTAŞ 8.1.1', 'Vardiyada min 2 kez ölçüm. Ortalama <= 3.0 mT (30 Gauss), Tekil <= 3.5 mT (35 Gauss)', 'Madde 8.1.1', 'W'],
            ['20', 'Proje Markalaması ve Boyama Kontrolü', 'Her boruda (%100)', 'Boru dış yüzeyi orta kısmı ve iç uçlar', 'BOTAŞ Madde 10.1 & 10.2', 'API şablonuna ek olarak BOTAŞ / PROJE ADI / FİRMA ADI şablonu (100/150 mm)', 'Madde 10.1 & 10.2', 'W']
        ]
    )

    # 2. BOTAŞ 24" X60 Station Pipe ITP (82.5 Bar Station)
    build_itp_pdf(
        filename='02_BOTAS_24in_X60_Station_Pipe_ITP.pdf',
        project_title='BOTAŞ KOMPRESÖR & ÖLÇÜM İSTASYONU BORU ALIMI - ITP',
        pipe_info='24" (610 mm) x 12.70 mm, Grade X60 PSL 2, SAWH/LSAW (F=0.50 İstasyon Borusu)',
        standard_info='BOTAŞ 4-NGTL-0-GN-P-002-5120 Rev. 7 (82.5 Bar İstasyon)',
        items=[
            ['1', 'Ladle Heat Analysis', 'Once per heat of steel', 'Ladle test sample', 'ASTM A751', 'C <= 0.16%, P <= 0.025%, S <= 0.010%, CE_IIW <= 0.40', 'BOTAŞ 3.2.1', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit', 'Pipe body sample', 'ISO 14284', 'C <= 0.16%, P <= 0.025%, S <= 0.010%, CE_Pcm <= 0.22', 'BOTAŞ 3.2.2.4', 'W'],
            ['3', 'Pipe Body Tensile Test', '2 sets per test unit (1 for IDARE 5 yrs)', 'Transverse body specimen', 'ISO 6892-1', 'Rt0.5 >= 415 MPa, Rm: 520-760 MPa, Af >= 21%, Y/T <= 0.90', 'BOTAŞ 3.3.1.4', 'H/W'],
            ['4', 'Weld Seam Tensile Test', '2 sets per test unit', 'Transverse weld specimen', 'ASTM A370', 'Rm >= 520 MPa across weld, Elongation >= 10%', 'BOTAŞ 3.3.2.1', 'W'],
            ['5', 'CVN Impact Test (Body) at -20 °C', '1 set (3 specimens) per lot at -20 °C', 'Transverse body Charpy V', 'ISO 148-1', 'At -20 °C: Min Avg 60 Joules, Min Individual 45 Joules', 'BOTAŞ 3.3.5', 'H/W'],
            ['6', 'CVN Impact Test (Weld & HAZ) at -20 °C', '1 set weld + 1 set HAZ at -20 °C', 'Weld centerline and HAZ', 'ISO 148-1', 'At -20 °C: Min Avg 45 Joules, Min Individual 34 Joules', 'BOTAŞ 3.3.5', 'H/W'],
            ['7', 'Drop Weight Tear Test (DWTT)', 'Once per heat at 0 °C', 'Transverse DWTT specimen', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%, No single specimen < 60%', 'BOTAŞ 3.3.6.4', 'H/W'],
            ['8', 'Residual Stress Ring Test', 'Every heat (per heat mandatory)', '150 mm ring opposite weld', 'BOTAŞ 3.3.9', 'S <= 0.10 x SMYS (Max 41.5 MPa)', 'BOTAŞ 3.3.9', 'H/W'],
            ['9', 'Hydrostatic Pressure Test', 'Each pipe (100% all pipes)', 'Full pipe length', 'BOTAŞ 8.4', 'Pressure: 100% SMYS (170 bar), Duration: MINIMUM 20 SECONDS', 'BOTAŞ 8.4.1', 'H/W'],
            ['10', 'Weld Seam 100% NDT (UT + RT)', '100% full length of weld', 'Online UT + Offline RT', 'ISO 10893-11/6', '100% Online UT inspection plus RT verification of ends', 'BOTAŞ 8.8.4', 'H/W'],
            ['11', 'Pipe Ends UT Laminar Testing', '100% of all pipe ends', '50 mm band on pipe ends', 'ISO 10893-8', '100% pipe ends scanned (min 50 mm band, no defect)', 'BOTAŞ 8.8.4.4.2', 'W'],
            ['12', 'Dimensional & Wall Thickness Verification', '100% of all pipes (D, t, L)', 'Pipe body and pipe ends', 'BOTAŞ 5.1/5.2', 'End ovality <= 50% API 5L Table 10; Straightness <= 0.10% L; t=12.70 mm (-8/+15%)', 'BOTAŞ 5.1 & 5.5', 'W'],
            ['13', 'Visual Surface Inspection', '100% internal and external', 'Full body visual', 'BOTAŞ 8.1.2', '100% visual inspection, no crack, no sliver, no lamination', 'BOTAŞ 8.1.2', 'W']
        ]
    )

    # 3. API 5L 48" X70 PSL2 SAWH Standard ITP
    build_itp_pdf(
        filename='03_API_5L_48in_X70_PSL2_SAWH_Standard_ITP.pdf',
        project_title='INTERNATIONAL GAS TRANSMISSION PIPELINE - QUALITY & INSPECTION PLAN',
        pipe_info='48" (1219 mm) x 18.40 mm, Grade X70M PSL 2, SAWH (Helical Submerged Arc Welded)',
        standard_info='API Specification 5L 47th Edition / ISO 3183 PSL 2',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.12%, P <= 0.020%, S <= 0.010%, CE_Pcm <= 0.23', 'API 5L 9.2 & Tablo 5', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per heat (different pipes)', 'Pipe body coupon', 'ISO 14284', 'C <= 0.12%, P <= 0.020%, S <= 0.010%, CE_Pcm <= 0.23', 'API 5L 9.2 & Tablo 5', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit (lot of <= 100 pipes)', 'Transverse body strap', 'ASTM A370', 'Rt0.5: 485-635 MPa, Rm: 570-760 MPa, Af >= 18.5%, Y/T <= 0.93', 'API 5L 9.3 & Tablo 7', 'H/W'],
            ['4', 'Weld Seam Tensile Test', 'Once per test unit (lot)', 'Transverse weld specimen', 'ASTM A370', 'Rm >= 570 MPa across weld seam', 'API 5L 9.4 & Tablo 7', 'W'],
            ['5', 'CVN Charpy Impact Test (Body) at 0 °C', '1 set (3 specimens) per test unit', 'Transverse body Charpy V', 'ASTM A370', 'At 0 °C: Min Average 45 Joules, Min Individual 35 Joules', 'API 5L 9.8 & Tablo 8', 'H/W'],
            ['6', 'CVN Charpy Impact Test (Weld & HAZ)', '1 set weld + 1 set HAZ per test unit', 'Weld centerline and HAZ', 'ASTM A370', 'At 0 °C: Min Average 27 Joules, Min Individual 20 Joules', 'API 5L 9.8 & Tablo 8', 'H/W'],
            ['7', 'Drop Weight Tear Test (DWTT)', 'Once per heat (2 specimens) at 0 °C', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear fracture area >= 85%', 'API 5L 9.9 & Tablo 18', 'H/W'],
            ['8', 'Guided-Bend Test', '1 root + 1 face bend per test unit', 'Transverse weld coupon', 'ASTM A370', 'No defect or crack opening > 3.2 mm in weld/HAZ', 'API 5L 9.10 & Tablo 18', 'W'],
            ['9', 'Hardness Testing', 'Once per test unit', 'Transverse cross section', 'ASTM E384', 'Maximum 300 HV10 (Body, HAZ, Weld)', 'API 5L 10.2.4.8', 'W'],
            ['10', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% of all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 135.5 bar (95% SMYS), Duration: MINIMUM 10 SECONDS', 'API 5L 10.2.6.2', 'H/W'],
            ['11', 'Ultrasonic Weld Seam Testing (UT)', '100% full length of weld seam', 'Full weld seam', 'API 5L Annex E', '100% automatic UT per ISO 10893-11 acceptance level U2', 'API 5L Ek E', 'H/W'],
            ['12', 'Pipe Ends UT Laminar Testing', '100% of pipe ends (100 mm band)', 'Both pipe ends', 'API 5L Annex E.8', '100 mm circumferential band on both ends; no defect > 6.0 mm', 'API 5L Ek E.8', 'W'],
            ['13', 'Diameter and Out-of-Roundness', 'Once per 4 hours and 100% pipe ends', 'Pipe body & ends', 'API 5L 10.2.8.1', 'Body diameter: +- 0.50% (Max +-4.0 mm); End ovality: per Table 10', 'API 5L Tablo 10', 'W'],
            ['14', 'Wall Thickness Verification', '100% of all pipes (Ultrasonic / Gauge)', 'Pipe body & ends', 'API 5L 10.2.8.2', 't = 18.40 mm; Tolerance: -8.0% / +15.0% (API 5L Table 11)', 'API 5L Tablo 11', 'W'],
            ['15', 'Visual Surface Inspection', '100% internal and external surface', 'Full pipe surface', 'API 5L 10.2.7', 'No crack, no laminate, no sliver; imperfections <= 12.5% t', 'API 5L 9.12', 'W'],
            ['16', 'Residual Magnetism Measurement', 'At least once per 4 hours on pipe ends', 'Pipe ends (4 points)', 'API 5L 10.2.8.5', 'Average <= 3.0 mT (30 Gauss), Maximum individual <= 3.5 mT', 'API 5L 10.2.8.5', 'W']
        ]
    )

    # 4. API 5L 36" X65 PSL2 LSAW Pipeline ITP (IOGP S-616)
    build_itp_pdf(
        filename='04_API_5L_36in_X65_PSL2_LSAW_ITP.pdf',
        project_title='OFFSHORE / ONSHORE CRUDE OIL PIPELINE - LSAW QUALITY PLAN',
        pipe_info='36" (914.4 mm) x 15.90 mm, Grade X65MO PSL 2, LSAW (Longitudinal Submerged Arc Welded)',
        standard_info='IOGP S-616 / API Spec 5L 47th Ed. (Cold Expanded)',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.08%, P <= 0.015%, S <= 0.003%, CE_Pcm <= 0.19', 'IOGP S-616 / API 5L', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit', 'Pipe body coupon', 'ISO 14284', 'C <= 0.08%, P <= 0.015%, S <= 0.003%, CE_Pcm <= 0.19', 'API 5L Tablo 5', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit after cold expansion', 'Transverse body coupon', 'ASTM A370', 'Rt0.5: 450-600 MPa, Rm: 535-760 MPa, Af >= 19.5%, Y/T <= 0.93', 'API 5L Tablo 7', 'H/W'],
            ['4', 'Weld Seam Tensile Test', 'Once per test unit', 'Transverse weld coupon', 'ASTM A370', 'Rm >= 535 MPa across longitudinal weld seam', 'API 5L Tablo 7', 'W'],
            ['5', 'CVN Charpy Impact Test (Body) at -10 °C', '1 set (3 specimens) per test unit', 'Transverse body Charpy V', 'ASTM A370', 'At -10 °C: Min Average 50 Joules, Min Individual 38 Joules', 'IOGP S-616', 'H/W'],
            ['6', 'CVN Charpy Impact Test (Weld & HAZ)', '1 set weld + 1 set HAZ per test unit', 'Weld centerline and fusion line', 'ASTM A370', 'At -10 °C: Min Average 35 Joules, Min Individual 25 Joules', 'IOGP S-616', 'H/W'],
            ['7', 'Drop Weight Tear Test (DWTT)', 'Once per heat at 0 °C', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%', 'API 5L Tablo 18', 'H/W'],
            ['8', 'Guided-Bend Test', '1 root + 1 face bend per test unit', 'Transverse weld coupon', 'ASTM A370', 'No defect > 3.2 mm in weld or HAZ after 180° bend', 'API 5L 9.10', 'W'],
            ['9', 'Hardness Testing', 'Once per test unit (13-point survey)', 'Cross section macro', 'ASTM E384', 'Maximum 275 HV10 (Body, Cap, Root, HAZ)', 'IOGP S-616', 'W'],
            ['10', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% of all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 100% SMYS (156 bar), Duration: MINIMUM 10 SECONDS', 'API 5L 10.2.6.2', 'H/W'],
            ['11', 'Ultrasonic Weld Seam Testing (UT)', '100% full length of longitudinal weld', 'Full weld seam', 'ISO 10893-11', '100% automated multi-channel UT per ISO 10893-11 Level U2', 'API 5L Ek E', 'H/W'],
            ['12', 'Pipe Body & Ends UT Laminar Testing', '100% plate scan and 100% pipe ends', 'Plate body & pipe ends', 'ISO 10893-8/9', 'Plate body: ISO 10893-9 Class E2; Pipe ends: 100 mm band, no defect > 6 mm', 'IOGP S-616', 'W'],
            ['13', 'Dimensional & Wall Thickness Verification', '100% of all pipes (D, t, L, Ovality)', 'Pipe body and pipe ends', 'API 5L 10.2.8', 'Diameter: +-0.5%; Ovality <= 0.6% D; Wall thickness: -8.0% / +15.0%', 'API 5L Tablo 10/11', 'W'],
            ['14', 'Visual Surface & Marking Inspection', '100% internal and external surface', 'Full pipe surface', 'API 5L 10.2.7', '100% visual inspection; stencil and stamp marking verification', 'API 5L Madde 11', 'W']
        ]
    )

    # 5. API 5L 20" X52 PSL2 HFW/ERW Pipeline ITP
    build_itp_pdf(
        filename='05_API_5L_20in_X52_PSL2_HFW_ERW_ITP.pdf',
        project_title='REGIONAL GAS DISTRIBUTION MAINLINE - HFW/ERW QUALITY PLAN',
        pipe_info='20" (508 mm) x 9.53 mm, Grade X52N PSL 2, HFW / ERW (High-Frequency Welded)',
        standard_info='API Specification 5L 47th Edition / ISO 3183 PSL 2',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.16%, P <= 0.020%, S <= 0.010%, CE_IIW <= 0.43', 'API 5L Tablo 5', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit', 'Pipe body coupon', 'ISO 14284', 'C <= 0.16%, P <= 0.020%, S <= 0.010%, CE_IIW <= 0.43', 'API 5L Tablo 5', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit (lot <= 100 pipes)', 'Transverse body strap', 'ASTM A370', 'Rt0.5: 360-530 MPa, Rm: 460-760 MPa, Af >= 23%, Y/T <= 0.93', 'API 5L Tablo 7', 'H/W'],
            ['4', 'Weld Seam Tensile Test', 'Once per test unit', 'Transverse weld coupon', 'ASTM A370', 'Rm >= 460 MPa across electric resistance weld seam', 'API 5L Tablo 7', 'W'],
            ['5', 'Flattening Test (Düzleştirme Testi)', 'Crop ends of each coil (first and last pipe of lot)', 'Full pipe section ring', 'API 5L 9.10.2', 'Step 1: Weld at 90° to 67% D (no opening); Step 2: to 33% D (no cracks)', 'API 5L 9.10.2 & Tablo 18', 'H/W'],
            ['6', 'CVN Charpy Impact Test (Body & Weld) at 0 °C', '1 set body + 1 set weld per test unit', 'Body & weld Charpy V', 'ASTM A370', 'Body: Min Avg 40 J, Min Ind 30 J; Weld: Min Avg 27 J, Min Ind 20 J (0 °C)', 'API 5L Tablo 8', 'H/W'],
            ['7', 'Drop Weight Tear Test (DWTT)', 'Once per heat at 0 °C (D=508 mm threshold)', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%', 'API 5L Tablo 18', 'H/W'],
            ['8', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 104 bar (90% SMYS), Duration: MINIMUM 10 SECONDS', 'API 5L 10.2.6.2', 'H/W'],
            ['9', 'Electric Weld Seam UT Inspection', '100% full length of HFW weld seam', 'HFW weld line', 'ISO 10893-10', '100% automated Ultrasonic Testing of weld seam after seam heat treatment', 'API 5L Ek E', 'H/W'],
            ['10', 'Pipe Ends UT Laminar Testing', '100% of pipe ends', 'Both pipe ends', 'API 5L Annex E.8', '100 mm band on pipe ends; no defect > 6.0 mm', 'API 5L Ek E.8', 'W'],
            ['11', 'Dimensional & Wall Thickness Verification', '100% of all pipes', 'Pipe body and ends', 'API 5L 10.2.8', 'Diameter: +-0.50%; Ovality: per Table 10; Wall thickness: -10.0% / +15.0%', 'API 5L Tablo 10/11', 'W'],
            ['12', 'Visual Surface & Magnetism Inspection', '100% internal and external', 'Full pipe surface', 'API 5L 10.2.7', 'No defect > 12.5% t; Residual magnetism <= 3.0 mT (30 Gauss)', 'API 5L 9.12 & 10.2.8.5', 'W']
        ]
    )

    # 6. API 5L 12" X52 PSL2 SMLS Seamless ITP
    build_itp_pdf(
        filename='06_API_5L_12in_X52_PSL2_SMLS_Seamless_ITP.pdf',
        project_title='HIGH-PRESSURE GATHERING LINE - SEAMLESS PIPE QUALITY PLAN',
        pipe_info='12.75" (323.9 mm) x 12.70 mm, Grade X52Q PSL 2, SMLS (Seamless Pipe)',
        standard_info='API Specification 5L 47th Edition / ISO 3183 PSL 2',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.16%, P <= 0.020%, S <= 0.010%, CE_IIW <= 0.43', 'API 5L Tablo 5', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit (lot <= 100 pipes)', 'Pipe body sample', 'ISO 14284', 'C <= 0.16%, P <= 0.020%, S <= 0.010%, CE_IIW <= 0.43', 'API 5L Tablo 5', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit after Q&T heat treatment', 'Transverse body coupon', 'ASTM A370', 'Rt0.5: 360-530 MPa, Rm: 460-760 MPa, Af >= 23%, Y/T <= 0.93', 'API 5L Tablo 7', 'H/W'],
            ['4', 'CVN Charpy Impact Test (Body) at 0 °C', '1 set (3 specimens) per test unit at 0 °C', 'Transverse body Charpy V', 'ASTM A370', 'At 0 °C: Min Average 40 Joules, Min Individual 30 Joules', 'API 5L Tablo 8', 'H/W'],
            ['5', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all seamless pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 240 bar, Duration: MINIMUM 5 SECONDS (D < 457 mm)', 'API 5L 10.2.6.2', 'H/W'],
            ['6', 'Seamless Pipe Body Full NDT (Flux Leakage / UT)', '100% full length and 360° circumference', 'Full pipe body', 'ISO 10893-1 / 10893-3', '100% automated Ultrasonic or Magnetic Flux Leakage for longitudinal/transverse flaws', 'API 5L Ek E', 'H/W'],
            ['7', 'Pipe Ends UT Laminar Testing', '100% of pipe ends (50 mm band)', 'Both pipe ends', 'API 5L Annex E.8', '50 mm circumferential band on both ends; no laminar defect > 6.0 mm', 'API 5L Ek E.8', 'W'],
            ['8', 'Dimensional & Wall Thickness Verification', '100% of all pipes (Ultrasonic wall check)', 'Pipe body & ends', 'API 5L 10.2.8', 'Diameter: +-0.75%; Wall thickness: -12.5% / +15.0% (SMLS Table 11)', 'API 5L Tablo 10/11', 'W'],
            ['9', 'Visual Surface & Bevel Geometry', '100% internal and external surface', 'Full pipe length', 'API 5L 10.2.7', 'No crack, no gouge, no defect > 12.5% t; Bevel: 30° (+5°/-0°), root face 1.6 mm', 'API 5L 9.12 & 9.14', 'W']
        ]
    )

    # 7. API 5L 16" Grade B PSL1 SMLS ITP
    build_itp_pdf(
        filename='07_API_5L_16in_Grade_B_PSL1_SMLS_ITP.pdf',
        project_title='INDUSTRIAL UTILITY & GENERAL SERVICE PIPING - PSL 1 QUALITY PLAN',
        pipe_info='16" (406.4 mm) x 9.53 mm, Grade B PSL 1, SMLS (Seamless Pipe)',
        standard_info='API Specification 5L 47th Edition PSL 1',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.28%, P <= 0.030%, S <= 0.030% (PSL 1 limits)', 'API 5L Tablo 4', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per heat of steel', 'Pipe body coupon', 'ISO 14284', 'C <= 0.28%, P <= 0.030%, S <= 0.030%', 'API 5L Tablo 4', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit (lot <= 400 pipes)', 'Longitudinal body strap', 'ASTM A370', 'Rt0.5 >= 245 MPa (35.5 ksi), Rm >= 415 MPa (60.2 ksi), Af >= 27.5%', 'API 5L Tablo 6', 'H/W'],
            ['4', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% of all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 70 bar, Duration: MINIMUM 5 SECONDS (D < 457 mm)', 'API 5L 10.2.6.2', 'H/W'],
            ['5', 'Dimensional & Wall Thickness Verification', 'Sample per lot and 100% pipe ends', 'Pipe body & ends', 'API 5L 10.2.8', 'Diameter: +-0.75%; Wall thickness: -12.5% / +15.0% (PSL 1 Table 11)', 'API 5L Tablo 10/11', 'W'],
            ['6', 'Visual Surface & Marking Inspection', '100% of all pipes', 'Full pipe surface', 'API 5L 10.2.7', 'Visual surface free from defects; API 5L Grade B PSL 1 paint stencil marking', 'API 5L Madde 11', 'W']
        ]
    )

    # 8. Vendor Discrepancy Test ITP (With Inadequate Frequencies & Limits)
    build_itp_pdf(
        filename='08_Vendor_ITP_With_Defects_Discrepancy_Test.pdf',
        project_title='VENDOR QUALITY CONTROL PLAN (AUDIT TEST CASE - WITH DISCREPANCIES)',
        pipe_info='48" (1219 mm) x 14.30 mm, Grade X65 PSL 2, SAWH Pipe',
        standard_info='Manufacturer Proposed Standard (Subject to Engineer Review)',
        items=[
            ['1', 'Ladle Heat Analysis', '1 per 5 heats (Inadequate frequency)', 'Ladle sample', 'ASTM A751', 'C <= 0.22%, P <= 0.035%, S <= 0.025% (Violates PSL 2)', 'Vendor QA', 'W'],
            ['2', 'Product Chemical Analysis', '1 analysis per lot (Inadequate frequency)', 'Pipe sample', 'OES', 'C <= 0.20%, P <= 0.030%', 'Vendor QA', 'W'],
            ['3', 'Pipe Body Tensile Test', '1 set per 200 pipes', 'Transverse strap', 'ASTM A370', 'Rt0.5 >= 450 MPa, Rm >= 535 MPa', 'Vendor QA', 'W'],
            ['4', 'Weld Seam Tensile Test', '1 set per 200 pipes', 'Transverse weld', 'ASTM A370', 'Rm >= 535 MPa across weld', 'Vendor QA', 'W'],
            ['5', 'CVN Body Impact Test', '1 set per lot at 0 °C', 'Transverse Charpy V', 'ASTM A370', 'At 0 °C: Min Average 27 Joules (Insufficient for X65 / BOTAŞ)', 'Vendor QA', 'W'],
            ['6', 'CVN Weld Impact Test', '1 set per lot at 0 °C', 'Weld Charpy V', 'ASTM A370', 'At 0 °C: Min Average 20 Joules (Insufficient)', 'Vendor QA', 'W'],
            ['7', 'Mill Hydrostatic Pressure Test', 'Each pipe (100%)', 'Full length', 'Vendor Test', 'Pressure 100 bar, Duration: 5 SECONDS (Violates 10s API & 20s BOTAŞ)', 'Vendor QA', 'W'],
            ['8', 'Weld Seam NDT Inspection', '1 in 10 pipes sample (Violates 100% NDT rule)', 'Spot check', 'UT', 'Spot ultrasonic check on 10% of pipes', 'Vendor QA', 'W'],
            ['9', 'Dimensional Verification', 'Sample 1 per shift', 'Spot check', 'Tape', 'Diameter +-1.0%, Wall thickness +-15%', 'Vendor QA', 'W'],
            ['10', 'Visual Surface Inspection', 'Sample 5% of pipes (Violates 100% visual rule)', 'Spot check', 'Visual', 'General visual check', 'Vendor QA', 'W']
        ]
    )

    # 9. ADNOC 42" X65 Sour Service ITP (Annex H)
    build_itp_pdf(
        filename='09_ADNOC_Spec_42in_X65_Sour_Service_ITP.pdf',
        project_title='ADNOC OFFSHORE SOUR GAS TRANSMISSION - ANNEX H QUALITY PLAN',
        pipe_info='42" (1067 mm) x 20.60 mm, Grade X65MS PSL 2, SAWH Sour Service',
        standard_info='ADNOC DGS-1300-001 / API 5L Annex H (NACE MR0175 / ISO 15156)',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.06%, P <= 0.010%, S <= 0.0010%, Ca/S: 1.5-3.0, CE_Pcm <= 0.18', 'ADNOC DGS / Annex H', 'H/W'],
            ['2', 'HIC Test (Hydrogen Induced Cracking)', '1 set (3 specimens) per heat / 3 heats', 'Pipe body, weld & HAZ', 'NACE TM0284 Sol A', 'CLR <= 10%, CTR <= 3.0%, CSR <= 1.0% in Solution A (pH 2.7)', 'API 5L Ek H.7', 'H/W'],
            ['3', 'SSC Test (Sulfide Stress Cracking)', '1 set (3 specimens) per qualification heat', 'Four-point bend or tensile', 'NACE TM0177 Method A', 'No failure at 90% AYS after 720 hours in 1 bar H2S', 'API 5L Ek H.7', 'H/W'],
            ['4', 'Pipe Body & Weld Tensile Test', 'Once per test unit', 'Transverse body & weld', 'ASTM A370', 'Rt0.5: 450-600 MPa, Rm: 535-760 MPa, Y/T <= 0.90', 'API 5L Tablo H.1', 'H/W'],
            ['5', 'CVN Charpy Impact Test (-20 °C)', '1 set body + 1 set weld at -20 °C', 'Transverse Charpy V', 'ASTM A370', 'At -20 °C: Min Average 60 Joules, Min Individual 45 Joules', 'ADNOC DGS', 'H/W'],
            ['6', 'Hardness Testing (100% Survey)', 'Once per test unit (16-point survey)', 'Cross section macro', 'ASTM E384', 'MAXIMUM 250 HV10 (Body, HAZ, Weld Cap & Root - Sour Limit)', 'NACE MR0175 / API 5L Ek H', 'H/W'],
            ['7', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 100% SMYS (185 bar), Duration: MINIMUM 15 SECONDS', 'ADNOC DGS', 'H/W'],
            ['8', 'Weld Seam & Plate Full NDT', '100% automated UT + 100% plate scan', 'Full weld & plate body', 'ISO 10893-11/9', '100% automated UT + 100% laminar scan (Class E1); no defect > 4 mm', 'API 5L Ek H & E', 'H/W'],
            ['9', 'Pipe Ends UT Laminar Testing', '100% of pipe ends (100 mm band)', 'Both pipe ends', 'API 5L Annex E.8', '100 mm band on pipe ends; no defect > 4.0 mm', 'API 5L Ek E.8', 'W'],
            ['10', 'Dimensional, Wall Thickness & Marking', '100% of all pipes', 'Pipe body & ends', 'API 5L 10.2.8', 'Diameter: +-0.5%; Wall thickness: -5.0% / +12.5%; Marking with suffix "MS"', 'ADNOC DGS', 'W']
        ]
    )

    # 10. Saudi Aramco 30" X60 ITP (01-SAMSS-035)
    build_itp_pdf(
        filename='10_Aramco_01_SAMSS_035_30in_X60_ITP.pdf',
        project_title='SAUDI ARAMCO GAS PIPELINE PROJECT - 01-SAMSS-035 QUALITY PLAN',
        pipe_info='30" (762 mm) x 14.30 mm, Grade X60 PSL 2, SAWH Pipe',
        standard_info='Saudi Aramco 01-SAMSS-035 / API Spec 5L 47th Edition',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.10%, P <= 0.015%, S <= 0.005%, CE_Pcm <= 0.20', '01-SAMSS-035', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit', 'Pipe body coupon', 'ISO 14284', 'C <= 0.10%, P <= 0.015%, S <= 0.005%, CE_Pcm <= 0.20', '01-SAMSS-035', 'W'],
            ['3', 'Pipe Body & Weld Tensile Test', 'Once per test unit (lot <= 100 pipes)', 'Transverse strap', 'ASTM A370', 'Rt0.5: 415-565 MPa, Rm: 520-760 MPa, Af >= 21%, Y/T <= 0.90', 'API 5L Tablo 7', 'H/W'],
            ['4', 'CVN Charpy Impact Test at -10 °C', '1 set body + 1 set weld at -10 °C', 'Transverse Charpy V', 'ASTM A370', 'At -10 °C: Min Average 50 Joules, Min Individual 38 Joules', '01-SAMSS-035', 'H/W'],
            ['5', 'Drop Weight Tear Test (DWTT)', 'Once per heat at 0 °C', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%, No single < 60%', '01-SAMSS-035', 'H/W'],
            ['6', 'Guided-Bend Test', '1 root + 1 face bend per test unit', 'Transverse weld coupon', 'ASTM A370', 'No defect > 3.2 mm in weld/HAZ after 180° bend', 'API 5L 9.10', 'W'],
            ['7', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 95% SMYS (149 bar), Duration: MINIMUM 15 SECONDS', '01-SAMSS-035', 'H/W'],
            ['8', 'Weld Seam 100% Automated UT', '100% full length of helical weld seam', 'Full weld seam', 'ISO 10893-11', '100% automated multi-channel UT per ISO 10893-11 Level U2', 'API 5L Ek E', 'H/W'],
            ['9', 'Strip & Pipe Ends UT Laminar Testing', '100% strip edges and 100% pipe ends', 'Strip edges & ends', 'ISO 10893-8/9', '100 mm band on pipe ends; strip edges 25 mm band; no defect > 6 mm', '01-SAMSS-035', 'W'],
            ['10', 'Dimensional, Straightness & Magnetism', '100% of all pipes', 'Pipe body & ends', '01-SAMSS-035', 'Straightness <= 0.10% L; Ovality <= 0.75% D; Residual magnetism <= 2.0 mT', '01-SAMSS-035', 'W']
        ]
    )

    # 11. Shell DEP 28" X70 Offshore Subsea ITP (Annex J)
    build_itp_pdf(
        filename='11_Shell_DEP_31_40_20_37_28in_X70_Offshore_ITP.pdf',
        project_title='SHELL DEEPWATER SUBSEA GAS PIPELINE - ANNEX J QUALITY PLAN',
        pipe_info='28" (711.2 mm) x 17.50 mm, Grade X70MO PSL 2, LSAW (Offshore Subsea)',
        standard_info='Shell DEP 31.40.20.37 / API 5L Annex J / DNV-OS-F101',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.08%, P <= 0.012%, S <= 0.002%, CE_Pcm <= 0.19', 'Shell DEP / Annex J', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit', 'Pipe body coupon', 'ISO 14284', 'C <= 0.08%, P <= 0.012%, S <= 0.002%, CE_Pcm <= 0.19', 'API 5L Tablo J.1', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit (lot <= 50 pipes)', 'Transverse body coupon', 'ASTM A370', 'Rt0.5: 485-605 MPa, Rm: 570-760 MPa, Af >= 19%, Y/T <= 0.90', 'API 5L Tablo J.2', 'H/W'],
            ['4', 'CTOD Fracture Toughness Test', '1 set (3 specimens) per qualification heat', 'Full thickness weld & HAZ', 'BS 7448 / ISO 12135', 'At -10 °C: Minimum CTOD δ >= 0.25 mm (No unstable brittle fracture)', 'Shell DEP / Annex J', 'H/W'],
            ['5', 'CVN Charpy Impact Test (-20 °C)', '1 set body + 1 set weld at -20 °C', 'Transverse Charpy V', 'ASTM A370', 'At -20 °C: Min Average 65 Joules, Min Individual 50 Joules', 'Shell DEP 31.40.20.37', 'H/W'],
            ['6', 'DWTT (Düşen Ağırlık Testi) at 0 °C', 'Once per heat at 0 °C', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%, No single specimen < 70%', 'API 5L Tablo J.2', 'H/W'],
            ['7', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 100% SMYS (210 bar), Duration: MINIMUM 15 SECONDS', 'Shell DEP', 'H/W'],
            ['8', 'Weld Seam 100% Automated UT + RT', '100% longitudinal weld seam', 'Full weld seam', 'ISO 10893-11/6', '100% Automated UT + Real-Time Radioscopy of full weld', 'Shell DEP / Annex J', 'H/W'],
            ['9', 'Plate Body & Pipe Ends UT Laminar Scan', '100% plate scan and 100% pipe ends', 'Full plate & pipe ends', 'ISO 10893-9/8', '100% full plate UT (Class E1); 100 mm pipe ends (no defect > 4 mm)', 'API 5L Ek J & E', 'W'],
            ['10', 'Strict Offshore Dimensional Tolerances', '100% of all pipes (D, t, Ovality, L)', 'Pipe body & ends', 'API 5L Annex J.6', 'Diameter: +-0.30%; Out-of-roundness <= 0.50% D; Wall thickness: -5.0% / +10.0%', 'API 5L Tablo J.3', 'W']
        ]
    )

    # 12. TANAP Style 56" X70 Mainline ITP
    build_itp_pdf(
        filename='12_TANAP_Style_56in_X70_Mainline_ITP.pdf',
        project_title='TRANS-ANATOLIAN NATURAL GAS PIPELINE (TANAP) - 56" MAINLINE ITP',
        pipe_info='56" (1422 mm) x 19.45 mm, Grade X70M PSL 2, SAWH Pipe',
        standard_info='TANAP Quality Specification / API Spec 5L 47th Edition PSL 2',
        items=[
            ['1', 'Ladle Heat Chemical Analysis', 'One analysis per heat of steel', 'Ladle sample', 'ASTM A751', 'C <= 0.10%, P <= 0.015%, S <= 0.004%, Nb+V+Ti <= 0.15%, CE_Pcm <= 0.20', 'TANAP Spec / API 5L', 'H/W'],
            ['2', 'Product Chemical Analysis', 'Two analyses per test unit (lot <= 100 pipes)', 'Pipe body coupon', 'ISO 14284', 'C <= 0.10%, P <= 0.015%, S <= 0.004%, CE_Pcm <= 0.20', 'API 5L Tablo 5', 'W'],
            ['3', 'Pipe Body Tensile Test', 'Once per test unit', 'Transverse body coupon', 'ASTM A370', 'Rt0.5: 485-635 MPa, Rm: 570-760 MPa, Af >= 19.0%, Y/T <= 0.90', 'API 5L Tablo 7', 'H/W'],
            ['4', 'Weld Seam Tensile Test', 'Once per test unit', 'Transverse weld coupon', 'ASTM A370', 'Rm >= 570 MPa across helical weld seam', 'API 5L Tablo 7', 'W'],
            ['5', 'CVN Charpy Impact Test (-20 °C)', '1 set body + 1 set weld at -20 °C', 'Transverse Charpy V', 'ASTM A370', 'At -20 °C: Min Average 80 Joules, Min Individual 60 Joules', 'TANAP Spec', 'H/W'],
            ['6', 'DWTT (Düşen Ağırlık Yırtılma Testi) at 0 °C', 'Once per heat at 0 °C', 'Transverse DWTT coupon', 'API RP 5L3', 'At 0 °C: Average shear area >= 85%, No single specimen < 60%', 'API 5L Tablo 18', 'H/W'],
            ['7', 'Guided-Bend Test', '1 root + 1 face bend per test unit', 'Transverse weld coupon', 'ASTM A370', 'No defect or opening > 3.2 mm after 180° bend', 'API 5L 9.10', 'W'],
            ['8', 'Hardness Testing (HV10)', 'Once per test unit', 'Cross section macro', 'ASTM E384', 'Maximum 280 HV10 across Body, HAZ and Weld', 'TANAP Spec', 'W'],
            ['9', 'Residual Stress Ring Test', 'Every heat (per heat mandatory)', '150 mm ring opposite weld', 'TANAP Spec', 'S <= 0.10 x SMYS (Max 48.5 MPa)', 'TANAP Spec', 'H/W'],
            ['10', 'Mill Hydrostatic Pressure Test', 'Each pipe (100% all 56" pipes)', 'Full pipe length', 'API 5L 10.2.6', 'Test Pressure: 100% SMYS (134 bar), Duration: MINIMUM 10 SECONDS', 'API 5L 10.2.6.2', 'H/W'],
            ['11', 'Weld Seam 100% Automated UT + RT', '100% full length of helical weld seam', 'Full weld seam', 'ISO 10893-11/6', '100% Online UT + Real-time Radioscopy of weld seam ends & repairs', 'API 5L Ek E', 'H/W'],
            ['12', 'Strip Body & Pipe Ends UT Laminar Scan', '100% strip scan and 100% pipe ends', 'Full strip & pipe ends', 'ISO 10893-9/8', '100% strip UT (Class E2); 100 mm pipe ends (no defect > 6.0 mm)', 'API 5L Ek E', 'W'],
            ['13', 'Dimensional, Straightness & Marking', '100% automated laser measuring station', 'Pipe body & ends', 'TANAP Spec', 'Diameter: +-0.50%; End ovality <= 50% Tablo 10; Straightness <= 0.10% L', 'TANAP Spec', 'W'],
            ['14', 'Visual Surface & Coating Surface Prep', '100% internal and external surface', 'Full pipe surface', 'API 5L 10.2.7', '100% visual inspection; surface cleanliness ISO 8501-1 Sa 2.5 for 3LPE', 'TANAP Spec', 'W']
        ]
    )

if __name__ == '__main__':
    generate_all_12_itps()
