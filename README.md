# Breast Cancer Cohort-Overlap Resource

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23004247.svg)](https://doi.org/10.5281/zenodo.23004247)

Public repository: https://github.com/lemnk/breast-cohort-leakage-resource

Version 2.0.0 archive: https://doi.org/10.5281/zenodo.23004247

This project builds a reproducible sample/patient identity registry across public
breast cancer transcriptomic cohorts. Its purpose is to catch accidental reuse
between model-development and external-validation data before model fitting.

## Release-2 results

- 5,931 human breast-cancer expression series in the frozen query universe
- 282,989 sample mentions and 238,252 unique GSM accessions
- 41,428 GSM accessions reused across 1,622 series
- 1,948 series pairs with detected evidence: 1,172 high-confidence and 776
  requiring manual review
- 304 confirmed and 12 supported expression-fingerprint links in the seed-family
  evaluation; 69 identifier candidates were not corroborated
- 0 of 1,925 deterministic nonmatches met the expression-confirmation rule
- The strict title rule recovered 47.3% within known exact-GSM reuse; this is not
  sensitivity for different-GSM patient identity
- Structured review of 100 title candidates found 40 confirmed, 2 probable, 35
  unresolved, and 23 with evidence against identity; sole author Naol Beyene
  manually verified all rows, and an unblinded second human verifier agreed on
  all 100 classifications. This sample does not estimate rule precision or
  independent inter-reviewer reliability
- An explicit GEO-metadata audit found two in-universe normalization-data reuse
  relationships involving 35 cited GSMs; these remain separate from overlap tiers
- In a metadata-selected held-out GPL96–GPL570 cell-line pair, frozen rules
  confirmed two of three candidates; none of 15 controls triggered

These counts describe a query-defined breast-cancer expression resource, not all of GEO. “No detected
evidence” is not proof that two cohorts are independent.

## Quick check

From this directory:

```powershell
python src\check_cohort_overlap.py GSE20194 GSE25055 GSE25065
```

The tool reports every requested series pair and separates direct/confirmed
overlap from manual-review evidence.

## Reproduce

Python 3.11 or newer is recommended. Install the pinned packages in
`requirements.txt`, then run:

```powershell
.\run_pipeline.ps1
```

Use `-SkipDiscovery -SkipDownload` to rebuild all derived results from the
already archived inputs. The protocol and evidence thresholds are frozen in
`PROTOCOL_v2_20260927.md`.

## Main files

- `release_v2/cohort_overlap_lookup.csv`: comprehensive pair-level evidence lookup
- `release_v2/series_inventory.csv`: 5,931 in-scope accessions
- `data/overlap/expression_validated_edges.csv`: sample-level seed validation
- `reports/computational_report_v2.md`: actual findings and limitations
- `reports/validation/`: metadata-rule and platform-scope audits
- `reports/validation/explicit_geo_reuse_relationships.csv`: explicit
  normalization-data reuse references kept separate from identity evidence
- `data/heldout/heldout_crossplatform_summary.json`: held-out transport result
- `manuscript/manual_title_audit_workbook.xlsx`: structured author-review file
- `manuscript/resource_report_draft.md`: JCO CCI Resource Report draft

Source expression files are not part of the distributable release. They remain
available from NCBI GEO; accession and checksum provenance are recorded under
`data/discovery`.

## Licensing

Code is offered under the MIT License. Derived release tables and documentation
are offered under CC BY 4.0. Source GEO data retain their original provenance and
terms.
