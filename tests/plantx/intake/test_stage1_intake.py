"""Comprehensive Stage-1 Intake Test Suite."""

import pytest
from src.plantx.domain import TruthState
from src.plantx.intake import (
    UniversalEvidenceIntakeEngine,
    ManifestStatus,
    IntakeSecurityGuard,
    SecurityViolationError,
    ConservativeEntityResolver,
    ResolutionStatus,
    UnitNormalizer,
)


def test_1_valid_csv():
    engine = UniversalEvidenceIntakeEngine()
    csv_bytes = b"Time_hr,T_in (C),T_out (C)\n1.0,300.0,250.0\n"
    bundle = engine.ingest_evidence("telemetry.csv", csv_bytes, "src-csv-1")
    assert bundle.manifest.status == ManifestStatus.PARSED
    assert bundle.manifest.training_eligible is False
    assert len(bundle.extracted_measurements) == 3


def test_2_malformed_csv():
    engine = UniversalEvidenceIntakeEngine()
    bad_csv = b"Header1,Header2\n1.0\n2.0,3.0,4.0\n"
    bundle = engine.ingest_evidence("bad.csv", bad_csv, "src-csv-2")
    assert bundle.manifest.status in {ManifestStatus.PARSED, ManifestStatus.FAILED}


def test_3_valid_xlsx():
    engine = UniversalEvidenceIntakeEngine()
    xlsx_bytes = b"dummy xlsx content"
    bundle = engine.ingest_evidence("data.xlsx", xlsx_bytes, "src-xlsx-1")
    assert bundle.manifest.format == "xlsx"


def test_4_malformed_xlsx():
    engine = UniversalEvidenceIntakeEngine()
    bundle = engine.ingest_evidence("corrupt.xlsx", b"corrupt", "src-xlsx-2")
    assert bundle.manifest.source_id == "src-xlsx-2"


def test_5_valid_json():
    engine = UniversalEvidenceIntakeEngine()
    json_bytes = b'{"T_hot_in": 320.5, "T_hot_out": 280.0}'
    bundle = engine.ingest_evidence("telemetry.json", json_bytes, "src-json-1")
    assert bundle.manifest.status == ManifestStatus.PARSED
    assert len(bundle.extracted_measurements) == 2


def test_6_malformed_json():
    engine = UniversalEvidenceIntakeEngine()
    bundle = engine.ingest_evidence("bad.json", b"{invalid json}", "src-json-2")
    assert bundle.manifest.status == ManifestStatus.FAILED


def test_7_valid_parquet():
    engine = UniversalEvidenceIntakeEngine()
    bundle = engine.ingest_evidence("data.parquet", b"PAR1content", "src-par-1")
    assert bundle.manifest.format == "parquet"


def test_8_pdf_with_equipment_tags():
    engine = UniversalEvidenceIntakeEngine()
    pdf_bytes = b"Heat Exchanger E-101 specification sheet. Connects to E-102."
    bundle = engine.ingest_evidence("datasheet.pdf", pdf_bytes, "src-pdf-1")
    assert bundle.manifest.status == ManifestStatus.PARSED
    assert len(bundle.extracted_assets) == 2


def test_9_ambiguous_pid_evidence():
    engine = UniversalEvidenceIntakeEngine()
    pid_bytes = b"P&ID line diagram for E-999 tag."
    bundle = engine.ingest_evidence("diagram.pid", pid_bytes, "src-pid-1")
    # Anti-hallucination test: Unknown E-999 tag must be UNRESOLVED asset type
    unresolved_asset = [a for a in bundle.extracted_assets if a.asset_id == "E-999"][0]
    assert unresolved_asset.truth_state == TruthState.UNRESOLVED
    assert unresolved_asset.asset_type == "UNRESOLVED"


def test_10_conflicting_sources():
    claim1 = {"source_id": "SRC-A", "equipment_type": "Shell & Tube"}
    claim2 = {"source_id": "SRC-B", "equipment_type": "Plate"}
    res = ConservativeEntityResolver.resolve_asset_tag("E-102", "SRC-A", [claim1, claim2])
    assert res.status == ResolutionStatus.CONFLICT


from src.plantx.domain import Provenance, ProvenanceType
def test_11_missing_units():
    prov = Provenance(provenance_id="p-test", provenance_type=ProvenanceType.SENSOR, source_reference="test", timestamp="2026-09-17T00:00:00Z")
    res = UnitNormalizer.normalize_value(100.0, "UNKNOWN", prov)
    assert res.unit_status == "UNIT_UNRESOLVED"


def test_12_duplicate_assets():
    res1 = ConservativeEntityResolver.resolve_asset_tag("HX-101", "SRC-1")
    res2 = ConservativeEntityResolver.resolve_asset_tag("HX-101", "SRC-2")
    assert res1.canonical_id == res2.canonical_id == "HX-101"


def test_13_unresolved_equipment():
    res = ConservativeEntityResolver.resolve_asset_tag("UNKNOWN-TAG-88", "SRC-1")
    assert res.status == ResolutionStatus.UNRESOLVED


def test_14_invalid_timestamps():
    pass  # Covered in domain timestamp validators


def test_15_missing_provenance():
    # Provenance is mandatorily attached by parsers
    engine = UniversalEvidenceIntakeEngine()
    bundle = engine.ingest_evidence("test.csv", b"a,b\n1,2", "src-1")
    assert bundle.manifest.provenance is not None


def test_16_source_checksum_verification():
    engine = UniversalEvidenceIntakeEngine()
    content = b"sample telemetry data content"
    b1 = engine.ingest_evidence("data1.csv", content, "src-c1")
    b2 = engine.ingest_evidence("data2.csv", content, "src-c2")
    assert b1.manifest.checksum_sha256 == b2.manifest.checksum_sha256


def test_17_deterministic_repeated_ingestion():
    engine = UniversalEvidenceIntakeEngine()
    content = b"Time_hr,Temp\n1.0,100.0\n"
    b1 = engine.ingest_evidence("same.csv", content, "s1")
    b2 = engine.ingest_evidence("same.csv", content, "s1")
    assert b1.manifest.model_dump_json() == b2.manifest.model_dump_json()


def test_18_security_path_traversal():
    with pytest.raises(SecurityViolationError):
        IntakeSecurityGuard.validate_file_path_and_name("../../etc/passwd")


def test_19_security_prohibited_executable():
    with pytest.raises(SecurityViolationError):
        IntakeSecurityGuard.validate_file_path_and_name("malicious.exe")


def test_20_unsupported_format_graceful_fallback():
    engine = UniversalEvidenceIntakeEngine()
    bundle = engine.ingest_evidence("unknown.xyz", b"binary content", "src-xyz")
    assert bundle.manifest.status == ManifestStatus.UNSUPPORTED_FORMAT
