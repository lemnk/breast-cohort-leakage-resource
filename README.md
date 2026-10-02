# Breast Cancer GEO Accession-Overlap Registry

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23004247.svg)](https://doi.org/10.5281/zenodo.23004247)

Public repository: https://github.com/lemnk/breast-cohort-leakage-resource

The registry screens proposed public breast cancer expression cohorts before
development and validation roles are assigned. Release 3 corrects the evidence
semantics used in release 2 while retaining all prior frozen outputs.

## Release 3 results

- 5,931 human breast cancer expression series in the frozen query universe
- 282,989 sample mentions and 238,252 unique GSM accessions
- 41,428 GSM accessions reused across 1,622 series and 1,165 series pairs
- 1,950 lookup rows: 1,165 direct GSM overlaps, 2 documented GEO reuse
  relationships without a direct-overlap edge, and 783 candidate relationships
  requiring manual review
- 7 expression-only pairs formerly promoted to high confidence are now
  review-required candidates
- 304 of 385 development candidates exceeded the stronger expression rule, 12
  exceeded only the weaker rule, and 69 were not corroborated; these are
  candidate results, not verified identities
- 0 of 1,925 dependent presumed-nonmatch controls exceeded the stronger rule;
  4 exceeded only the weaker rule. No probability bound or false-confirmation
  estimate is claimed
- In a prespecified 30-study evaluation (435 pairs), the checker exactly matched
  the two direct GSM intersections with zero count mismatches. Both were declared
  SuperSeries/subseries relationships; one unresolved title candidate was added
  beyond direct intersection

These counts describe a query-defined GEO resource, not all breast cancer
transcriptomics. No detected evidence is not proof that cohorts are independent.

## Quick check

```powershell
python src\check_cohort_overlap.py GSE20194 GSE25055 GSE25065
```

The checker distinguishes `direct_accession_overlap`, `documented_geo_reuse`,
`candidate_relationship_review_required`, and `no_detected_evidence`.
Expression-only evidence is never reported as verified same-specimen identity.

## Reproduce

Python 3.11 or newer is recommended. Install `requirements.txt`, then run:

```powershell
.\run_pipeline.ps1
```

Use `-SkipDiscovery -SkipDownload` to rebuild derived results from archived
inputs. Release-3 correction and evaluation rules were frozen in
`PROTOCOL_v3_20261002.md` before evaluation results were generated.

## Main files

- `release_v3/cohort_overlap_lookup.csv`: corrected pair-level evidence lookup
- `release_v3/series_inventory.csv`: the 5,931 in-scope accessions
- `reports/resource_evaluation/`: prespecified 30-study evaluation
- `data/overlap_v3/`: relabeled expression-candidate and control results
- `reports/computational_report_v3.md`: findings, corrections, and limitations
- `manuscript/resource_report_v3_draft.md`: revised Resource Report draft
- `figures_v3/`: corrected publication figures
- `release_v2/`: preserved historical release

The frozen version 2 archive remains at
https://doi.org/10.5281/zenodo.23004247. Release 3 needs a new immutable archive
DOI before manuscript submission.

## Licensing

Code is MIT licensed. Derived tables and documentation are CC BY 4.0. Source GEO
data retain their original provenance and terms.
