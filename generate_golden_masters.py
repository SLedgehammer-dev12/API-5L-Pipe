#!/usr/bin/env python3
"""
Golden Master Test Generator for ITP Evaluation.

Generates baseline expected outputs for all 17 ITP files in the sample library.
Run this script to create/update golden master test files.
"""
import os
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, "/Users/macbook/Documents/Kodlama/API 5L Pipe")

from core.unlimited_ocr_engine import UnlimitedOCREngine
from core.itp_audit_engine import ITPAuditEngine


def generate_golden_masters():
    """Generate golden master JSON files for all ITPs in sample library."""
    
    itp_dir = Path("/Users/macbook/Documents/Kodlama/API 5L Pipe/itp_sample_library")
    output_dir = Path("/Users/macbook/Documents/Kodlama/API 5L Pipe/tests/golden_master")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    itp_files = sorted([f for f in os.listdir(itp_dir) if f.lower().endswith('.pdf')])
    
    print(f"Generating golden masters for {len(itp_files)} ITP files...")
    
    summary = []
    
    for fname in itp_files:
        path = Path("/Users/macbook/Documents/Kodlama/API 5L Pipe/itp_sample_library") / fname
        print(f"\nProcessing: {fname}")
        
        try:
            data = open(path, "rb").read()
            res = UnlimitedOCREngine.parse_pdf_or_image(data, fname)
            
            meta = res.get('detected_metadata', {})
            scope_variants = meta.get('scope_variants', [])
            if scope_variants:
                pipe_cfg = scope_variants[0].copy()
            else:
                pipe_cfg = {
                    'diameter_mm': meta.get('detected_diameter_mm', 1219.0),
                    'diameter_inch': meta.get('detected_diameter_inch', '48"'),
                    'wall_thickness_mm': meta.get('detected_wall_thickness_mm', 14.30),
                    'material_grade': meta.get('detected_grade', 'X65'),
                    'manufacturing_process': meta.get('detected_process', 'SAWH'),
                    'standard_type': meta.get('detected_standard', 'BOTAŞ'),
                    'psl_level': meta.get('detected_psl', 'PSL2'),
                    'delivery_condition': meta.get('detected_delivery_condition', 'M'),
                }
            
            if meta.get('detected_scope_mode') == 'COATING_ONLY':
                pipe_cfg['scope_mode'] = 'COATING_ONLY'
            
            audit = ITPAuditEngine.audit_itp(res['items'], pipe_cfg)
            kpi = audit['kpi']
            
            # Create golden master record
            golden = {
                "file": fname,
                "metadata": {
                    "detected_diameter_mm": res['detected_metadata'].get('detected_diameter_mm'),
                    "detected_diameter_inch": res['detected_metadata'].get('detected_diameter_inch'),
                    "detected_wall_thickness_mm": res['detected_metadata'].get('detected_wall_thickness_mm'),
                    "detected_grade": res['detected_metadata'].get('detected_grade'),
                    "detected_process": res['detected_metadata'].get('detected_process'),
                    "detected_standard": res['detected_metadata'].get('detected_standard'),
                    "detected_psl": res['detected_metadata'].get('detected_psl'),
                    "detected_scope_mode": res['detected_metadata'].get('detected_scope_mode'),
                    "scope_variants_count": len(res['detected_metadata'].get('scope_variants', [])),
                },
                "parse_result": {
                    "status": res.get('status'),
                    "is_fallback": res.get('is_fallback', False),
                    "items_count": res.get('total_items_found', 0),
                },
                "pipe_config_used": pipe_cfg,
                "kpi": {
                    "total_tests_audited": kpi.get('total_tests_audited', 0),
                    "compliant_count": kpi.get('compliant_count', 0),
                    "more_stringent_count": kpi.get('more_stringent_count', 0),
                    "non_compliant_count": kpi.get('non_compliant_count', 0),
                    "bare_pipe_score_percent": kpi.get('bare_pipe_score_percent', 0),
                    "coating_score_percent": kpi.get('coating_score_percent', 0),
                    "overall_verdict": kpi.get('overall_verdict', 'UNKNOWN'),
                },
                "audit_rows": [
                    {
                        "test_name": r.get('test_name'),
                        "status": r.get('status'),
                        "issue_type": r.get('issue_type'),
                        "uploaded_frequency": r.get('uploaded_frequency'),
                        "standard_frequency": r.get('standard_frequency'),
                        "uploaded_criteria": r.get('uploaded_criteria'),
                        "standard_criteria": r.get('standard_criteria'),
                        "audit_remarks": r.get('audit_remarks'),
                    }
                    for r in audit['audit_rows']
                ],
                "findings": audit.get('findings', []),
            }
            
            # Save golden master
            safe_name = fname.replace('.pdf', '').replace(' ', '_').replace('/', '_')
            output_file = output_dir / f"{safe_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(golden, f, ensure_ascii=False, indent=2, default=str)
            
            kpi = audit['kpi']
            print(f"  ✓ {fname}: {kpi['total_tests_audited']} tests, "
                  f"ok={kpi['compliant_count']}, more={kpi['more_stringent_count']}, "
                  f"non={kpi['non_compliant_count']}, verdict={kpi['overall_verdict']}")
            
            summary.append({
                'file': fname,
                'total': kpi['total_tests_audited'],
                'compliant': kpi['compliant_count'],
                'more': kpi['more_stringent_count'],
                'non': kpi['non_compliant_count'],
                'verdict': kpi['overall_verdict']
            })
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": str(__import__('datetime').datetime.now()),
            "total_files": len(summary),
            "total_checks": sum(s['total'] for s in summary),
            "total_compliant": sum(s['compliant'] for s in summary),
            "total_more": sum(s['more'] for s in summary),
            "total_non": sum(s['non'] for s in summary),
            "files": summary
        }, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✅ Golden masters generated in: {output_dir}")
    print(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    generate_golden_masters()