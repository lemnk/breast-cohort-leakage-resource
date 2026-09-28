# Public Breast Cancer Cohort Identity and Leakage Audit

## Objective

Create a reusable, versioned resource that identifies documented and probable
patient/sample reuse across public breast-cancer transcriptomic cohorts. The
scientific question is whether datasets described as separate external cohorts
are genuinely patient-independent enough to support validation claims.

The intended publication is a JCO Clinical Cancer Informatics Resource Report.
The project will not claim that a new predictor improves treatment decisions.

## Non-negotiable protections

1. The existing `C:\cancer\breast_response` project is read-only source material.
2. Original source files and metadata are retained with hashes and provenance.
3. Identity matching is performed without using model outcomes or performance.
4. Exact identifiers, documented source relationships, aliases, raw-file hashes,
   and expression fingerprints are reported as distinct evidence classes.
5. A separate GEO accession is never assumed to represent independent patients.
6. Ambiguous matches remain ambiguous; they are not forced into duplicate or
   independent categories.
7. Restricted or unclear source material will be referenced by accession and
   download instructions rather than redistributed.

## Study design

### Phase 1 — source and feasibility audit

- Search GEO and source publications using fixed breast-cancer/neoadjuvant/
  transcriptomic queries.
- Record accession, platform, sample count, processed/raw availability,
  publication identifiers, treatment setting, outcome availability, and known
  parent/subseries relationships.
- Estimate storage before downloading expression matrices.
- Freeze an inclusion rule and an initial candidate inventory.

**Gate:** continue to matrix acquisition only if at least 15 potentially relevant
series and at least 2,000 deposited samples are identified. Otherwise broaden the
scope transparently to prognostic as well as neoadjuvant cohorts.

### Phase 2 — metadata registry

- Download SOFT/series-matrix metadata in stages.
- Normalize GSM/GSE identifiers, titles, patient aliases, institutions,
  treatments, and source-publication links.
- Construct an accession and source-study relationship graph.
- Preserve raw strings alongside normalized fields.

### Phase 3 — identity evidence

- Exact GSM and accession reuse.
- Documented SuperSeries/subseries and publication-level reuse.
- Conservative normalized patient aliases.
- Raw-file content hashes where files are already available or small enough.
- Expression fingerprints on common probes/genes, with platform-aware thresholds.
- Match tiers: documented, exact, high-confidence probable, possible, or no
  detected evidence. “No detected evidence” is not proof of independence.

### Phase 4 — validation of the audit method

- Use known Hatzis reuse across GSE25055/GSE25065/GSE20194/GSE20271 as positive
  controls.
- Create negative controls from clearly unrelated cohorts/platform samples.
- Prespecify thresholds using controls, then freeze them before applying the
  method to the remaining registry.
- Manually verify high-confidence pairs against deposited metadata and source
  publications.

### Phase 5 — resource and impact analysis

- Release a cohort registry, overlap edge list, evidence table, and interactive
  or static overlap map.
- Quantify how many nominal external-validation pairings are affected by known or
  probable reuse.
- Demonstrate, on selected public examples, how leakage changes uncertainty or
  apparent validation performance. These demonstrations remain secondary.

### Phase 6 — publication package

- Reproducibility tests, environment lock, checksums, and clean rerun.
- Figures: discovery flow, cohort relationship graph, evidence concordance,
  platform/sample coverage, and validation-case studies.
- JCO CCI Resource Report, data supplement, cover letter, reporting checklist,
  and public-archive manifest.

## Primary deliverables

- `data/discovery/geo_candidates.csv`
- `data/registry/cohorts.csv` and `samples.parquet`
- `data/overlap/edges.csv` with evidence classes
- Tested command-line audit software
- Versioned computational report and reproducibility log
- Submission manuscript and supplement

## Resource limits

- Maintain at least 1 GB free on drive C.
- Prefer metadata and processed matrices; stage and delete reproducible temporary
  downloads after hashing and extraction.
- Raw arrays are acquired only when they resolve a specific identity question.

## Publication decision rule

Proceed to a Resource Report only if the completed registry is broad enough to be
useful beyond the original four cohorts and the identity method recovers known
reuse without an unacceptable false-positive rate. If that standard is not met,
report the audit as an internal feasibility result rather than manufacturing a
paper-sized claim.
