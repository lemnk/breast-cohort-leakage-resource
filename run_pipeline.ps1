param(
    [switch]$SkipDiscovery,
    [switch]$SkipDownload
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (-not $SkipDiscovery) {
    python src\geo_discovery.py
    python src\screen_candidates.py
    python src\audit_remote_files.py
    python src\comprehensive_geo_discovery.py
}
if (-not $SkipDownload) {
    python src\download_seed_matrices.py
}

python src\parse_seed_metadata.py
python src\build_identity_edges.py
python src\validate_expression_fingerprints.py
python src\build_geo_reuse_registry.py
python src\build_title_alias_candidates.py
python src\build_release.py
python src\build_manual_review_queue.py
python src\build_comprehensive_registry.py
python src\build_release_v2.py
python src\validate_metadata_rules.py
if (Test-Path reports\validation\audit_sample_geo_headers.json) {
    python src\adjudicate_title_audit.py
}
python src\audit_explicit_geo_reuse.py
python src\summarize_platform_coverage.py
if (Test-Path data\heldout\series_matrix\GSE21217-GPL570_series_matrix.txt.gz) {
    python src\validate_heldout_gpl96.py
}
python src\make_figures.py
python src\relabel_expression_candidates_v3.py
python src\build_release_v3.py
python src\evaluate_cohort_selection_utility.py
python src\make_figures_v3.py
python -m unittest discover -s tests -v

Write-Host "Pipeline completed successfully."
