# Source and dataset feasibility audit

## Status

The project is feasible as a metadata and processed-matrix resource within the
available disk budget. The initial reproducible GEO search returned 540 unique
records. A deliberately broad automated screen placed 11 known/suspected
source-related series in a mandatory review group, 109 in priority review, and 22
in secondary review. These review groups contain 16,916 deposited samples before
manual exclusion of repeated time points, nonbaseline specimens, irrelevant
cancers, and other false positives.

The planned resource therefore passes the prospective feasibility gate of at
least 15 candidate series and 2,000 deposited samples. Passing this gate does not
mean that every record is eligible or independent.

## Storage audit

For the 11 mandatory seed series, the remote inventory identified approximately:

- 0.23 GiB of compressed series matrices;
- 0.47 GiB of MINiML family archives; and
- 5.11 GiB of supplementary files, dominated by raw-array archives.

Downloading every supplementary archive would exceed the safe local budget once
working files are included. The acquisition plan is therefore to download the
processed series matrices first, retain hashes and URLs, and obtain raw files only
for specific ambiguous identity comparisons. This decision is based on storage,
not on model outcomes.

## Access and reuse

NCBI GEO describes itself as a public repository and permits public records to be
downloaded without login. NCBI places no general restrictions on GEO data use or
distribution, while warning that submitters may assert rights over particular
materials. Consequently, the resource will release accession-based provenance,
derived identity evidence, and retrieval scripts. Redistribution of source files
will be reviewed series by series rather than assumed.

Official documentation:

- https://www.ncbi.nlm.nih.gov/geo/info/faq.html
- https://www.ncbi.nlm.nih.gov/geo/info/download.html
- https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html

## Immediate acquisition set

The first processed-matrix layer comprises GSE20194, GSE20271, GSE22093,
GSE23988, GSE25055, GSE25065, GSE32646, GSE34138, GSE41998, GSE42822, and
GSE50948. These accessions include known positive controls for cohort reuse and
several distinct comparator cohorts. Inclusion in this acquisition set is not a
claim of patient independence or final analytical eligibility.

## Next scientific gate

The next step is to parse sample metadata without outcome-dependent matching,
construct exact and normalized alias edges, and compare the recovered Hatzis
relationships with documented source relationships. Expression fingerprints will
be introduced only after identifiers and source-publication evidence are frozen.
