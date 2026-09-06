"""
Golden Master Regression Tests for ITP Evaluation.

Ensures that changes to the ITP evaluation pipeline don't break
existing behavior. Compares current output against golden master baselines.
"""
import os
import json
import pytest
from pathlib import Path
import sys

sys.path.insert(0, "/Users/macbook/Documents/Kodlama/API 5L Pipe")

from core.unlimited_ocr_engine import UnlimitedOCREngine
from core.itp_audit_engine import ITPAuditEngine


GOLDEN_DIR = Path("/Users/macbook/Documents/Kodlama/API 5L Pipe/tests/golden_master")
ITP_DIR = Path("/Users/macbook/Documents/Kodlama/API 5L Pipe/itp_sample_library")


def load_golden_master(filename: str) -> dict:
    """Load golden master JSON for a given ITP file."""
    safe_name = filename.replace('.pdf', '').replace(' ', '_').replace('/', '_')
    golden_file = GOLDEN_DIR / f"{safe_name}.json"
    if not golden_file.exists():
        pytest.skip(f"Golden master not found for {filename}")
    with open(golden_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_full_pipeline(fname: str) -> dict:
    """Run the full ITP evaluation pipeline for a given file."""
    path = ITP_DIR / fname
    data = open(path, "rb").read()
    
    res = UnlimitedOCREngine.parse_pdf_or_image(open(path, "rb").read(), fname)
    
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
    
    # For coating-only ITPs, use the first variant's dimensions but with coating scope
    if meta.get('detected_scope_mode') == 'COATING_ONLY' and meta.get('scope_variants'):
        first_var = meta['scope_variants'][0]
        pipe_cfg = first_var.copy()
        pipe_cfg['scope_mode'] = 'COATING_ONLY'
    
    audit = ITPAuditEngine.audit_itp(res['items'], pipe_cfg)
    return audit


def get_itp_files():
    """Get list of ITP files to test."""
    return sorted([f for f in os.listdir(ITP_DIR) if f.lower().endswith('.pdf')])


def assert_kpi_match(actual_kpi: dict, expected_kpi: dict, tolerance: float = 0.2):
    """Compare KPIs with tolerance."""
    for key in ['total_tests_audited', 'compliant_count', 'more_stringent_count', 'non_compliant_count']:
        actual_val = actual_kpi.get(key, 0)
        expected_val = expected_kpi.get(key, 0)
        if expected_val > 0:
            assert abs(actual_val - expected_val) <= max(1, expected_val * 0.2), \
                f"KPI {key}: actual={actual_val}, expected={expected_val} (tolerance 20%)"
    
    for key in ['bare_pipe_score_percent', 'coating_score_percent']:
        actual_val = actual_kpi.get(key, 0)
        expected_val = expected_kpi.get(key, 0)
        if expected_val > 0:
            assert abs(actual_val - expected_val) <= 5.0, \
                f"Score {key}: actual={actual_val}, expected={expected_val} (tolerance 5%)"
    
    assert actual_kpi.get('overall_verdict') == expected_kpi.get('overall_verdict'), \
        f"Verdict mismatch: actual={actual_kpi.get('overall_verdict')}, expected={expected_kpi.get('overall_verdict')}"


def load_golden_master(filename: str) -> dict:
    """Load golden master JSON for a given ITP file."""
    safe_name = filename.replace('.pdf', '').replace(' ', '_').replace('/', '_')
    golden_file = GOLDEN_DIR / f"{safe_name}.json"
    if not golden_file.exists():
        pytest.skip(f"Golden master not found for {filename}")
    with open(golden_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_full_pipeline(fname: str) -> dict:
    """Run the full ITP evaluation pipeline for a given file."""
    path = ITP_DIR / fname
    data = open(path, "rb").read()
    
    res = UnlimitedOCREngine.parse_pdf_or_image(open(path, "rb").read(), fname)
    
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
    
    # For coating-only ITPs, use the first variant's dimensions but with coating scope
    if meta.get('detected_scope_mode') == 'COATING_ONLY' and meta.get('scope_variants'):
        first_var = meta['scope_variants'][0]
        pipe_cfg = first_var.copy()
        pipe_cfg['scope_mode'] = 'COATING_ONLY'
    
    audit = ITPAuditEngine.audit_itp(res['items'], pipe_cfg)
    return audit


def get_itp_files():
    """Get list of ITP files to test."""
    return sorted([f for f in os.listdir(ITP_DIR) if f.lower().endswith('.pdf')])


@pytest.mark.parametrize("fname", get_itp_files())
def test_golden_master_regression(fname):
    """Test that current output matches golden master for each ITP."""
    golden = load_golden_master(fname)
    if not golden:
        pytest.skip(f"Golden master not found for {fname}")
    
    actual = run_full_pipeline(fname)
    
    # Compare KPIs
    assert_kpi_match(actual.get('kpi', {}), golden.get('kpi', {}))


def test_all_itp_files_exist():
    """Verify all ITP files exist."""
    files = list(ITP_DIR.glob("*.pdf"))
    assert len([f for f in files if f.suffix.lower() == '.pdf']) >= 17, \
        f"Expected at least 17 ITP files, found {len([f for f in files if f.suffix.lower() == '.pdf'])}"


def test_golden_masters_exist():
    """Verify all golden master files exist."""
    files = [f for f in GOLDEN_DIR.glob("*.json") if f.name != "summary.json"]
    assert len(files) >= 17, f"Expected at least 17 golden masters, found {len(files)}"


def test_summary_matches():
    """Verify summary.json matches individual golden masters."""
    summary_file = GOLDEN_DIR / "summary.json"
    assert summary_file.exists(), "Summary file missing"
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    assert summary['total_files'] == len(summary['files'])
    assert summary['total_files'] >= 17
    assert summary['total_checks'] == sum(f['total'] for f in summary['files'])
    assert summary['total_compliant'] == sum(f['compliant'] for f in summary['files'])
    assert summary['total_more'] == sum(f['more'] for f in summary['files'])
    assert summary['total_non'] == sum(f['non'] for f in summary['files'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])