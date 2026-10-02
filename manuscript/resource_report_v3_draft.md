# An Auditable Registry for Screening Public GEO Breast Cancer Expression Cohorts for Accession Overlap

**Article type:** Resource Report

**Running title:** GEO Breast Cohort Overlap Registry

**Author:** Naol Beyene

**Affiliation:** Jackson State University, Jackson, Mississippi, United States

**Corresponding author:** Naol Beyene; Jackson State University; 1400 John R.
Lynch Street, Jackson, MS 39217, USA; naolzed6@gmail.com

**Originality statement:** This manuscript is original and is not under
consideration by another journal.

## Abstract

### Background and Scope

Selecting a different Gene Expression Omnibus (GEO) series accession does not
guarantee a sample-independent validation cohort. We developed a reproducible
registry to screen public breast cancer expression studies before assigning
development and validation roles.

### Solution

A frozen GEO query defined 5,931 human breast cancer expression series. The
registry reconstructs sample membership and reports exact cross-series sharing
of GEO sample accessions (GSMs). Explicit GEO reuse statements, specific-title
candidates, and expression-corroborated different-accession candidates are
reported separately. Only shared GSMs are labeled direct accession overlap;
candidate evidence does not establish patient or specimen identity. Historical
outputs are retained, and corrected evidence semantics are implemented in
release 3.

### Evaluation

The universe contained 282,989 sample mentions representing 238,252 unique
GSMs. Of these, 41,428 GSMs recurred across series, producing 1,165 directly
overlapping series pairs. Release 3 contains 1,165 direct-overlap pairs, two
explicit GEO reuse relationships without a direct-overlap edge, and 783
candidate relationships requiring review. In development data, 304 of 385
different-accession candidates exceeded the stronger expression rule, 12
exceeded only the weaker rule, and 69 were not corroborated. Among 1,925
dependent presumed-nonmatch controls, zero exceeded the stronger rule and four
exceeded only the weaker rule; no probability bound was estimated. In a
prespecified evaluation of 30 metadata-selected studies (435 pairs), the checker
exactly reproduced the two direct GSM intersections with zero count mismatches.
Both were declared SuperSeries/subseries relationships. The registry added one
unresolved title candidate beyond direct intersection.

### Relevance

The resource provides a reproducible preanalysis provenance check and an
explicit review queue. Its incremental value beyond GSM intersection is modest,
and it does not validate a patient-identity classifier or demonstrate hidden
leakage in a published model.

### Access

Code, release tables, protocols, tests, and row-level evidence are available at
https://github.com/lemnk/breast-cohort-leakage-resource. The prior frozen
version 2 archive is available at https://doi.org/10.5281/zenodo.23004247;
release 3 should receive a new immutable archive DOI before submission.

## Background and Scope

External validation asks whether a model performs beyond the data used to
develop it. In public transcriptomic studies, investigators often operationalize
independence by choosing a different repository accession. GEO organization
makes that shortcut unsafe: a GSM can belong both to a focused SubSeries and a
SuperSeries, and public records can also represent reanalysis, repeated assays,
or related biological material.

This is a provenance problem, not necessarily misconduct. Declared reuse may be
scientifically appropriate, but a development/validation analysis becomes
misleading if the reused records are treated as independent. Breast cancer
biomarker studies are especially sensitive when validation cohorts contain few
outcome events.

Prior work has detected duplicated transcriptomic content and supplied general
tools including doppelgangR, while curated resources such as Gemma reconcile
some repeated content. Our narrower contribution is a frozen, breast-query-
specific GEO accession registry with a command-line checker and row-level
evidence. The validated core is deterministic GSM intersection. The resource
does not claim a new general duplicate-expression algorithm.

## Solution

### Frozen discovery universe

On September 27, 2026, we queried the NCBI GEO DataSets database for human GSE
records containing “breast cancer” and expression profiling by array or
high-throughput sequencing. The 5,931 returned series formed the frozen
universe. We archived the exact query, API response, inventory, checksums, and
code. This query-defined resource is not all breast cancer transcriptomics and
includes clinical and laboratory studies.

### Evidence classes

For every GSM, we reconstructed all containing GSE records. Two GSEs sharing at
least one GSM were classified as **direct accession overlap**. Complete
containment means that all GSMs in the smaller series occurred in the larger;
near containment means at least 80% occurred; other sharing is partial. These
labels describe repository structure, not disclosure quality or patient
identity beyond the shared GEO record.

Public GEO statements that one series reused or normalized data from another
were classified as **documented GEO reuse**. These relationships were retained
separately because a cited data source does not necessarily imply a duplicated
specimen in the intended analytic cohorts.

Different-accession candidates were generated using a deliberately narrow title
rule. Normalized titles had to contain a namespaced alphanumeric token of at
least six characters, be unique within each implicated series, and recur across
series under different GSM accessions. Generic patient, tumor, and sample
numbers and common cell-line identifiers were excluded. These links are
**candidates requiring review**, not confirmed identities.

### Expression candidate corroboration

Seven compatible GPL96 seed series underwent an expression experiment. The
seed series were method-development data selected because relationships were
known or suspected. We intersected probes, selected 2,048 probes by SHA-256
ordering with a fixed seed, converted values within each sample to ranks, and
correlated rank vectors. Five deterministic presumed-nonmatch controls were
generated per identifier candidate.

The original rule labeled a candidate stronger when it was reciprocal top-1 or
when correlation was at least 0.98 and exceeded the pair-specific control 99th
percentile by 0.02. A weaker rule required reciprocal top-3 ranks or correlation
of at least 0.95 with a 0.01 margin. Release 3 preserves the measured values and
rules but corrects their meaning: the outputs are **expression-corroborated
candidates**, **weaker-rule candidates**, and **not corroborated**. Reciprocal
nearest-neighbor status is not treated as verification of specimen identity.

Controls share anchor samples and study families, the rules were developed in
the same families, and the controls were presumed rather than identity-verified
nonmatches. Control exceedances are therefore descriptive. We did not estimate
a binomial confidence bound, false-discovery rate, or expected number of false
confirmations.

### Corrected checker and versioning

Release 3 uses three operational classes: `direct_accession_overlap`,
`documented_geo_reuse`, and `candidate_relationship_review_required`. The
checker reports the evidence counts and a corresponding action. Pairs with no
edge return “no detected evidence—not proof of independence.” Releases 1 and 2
and their original outputs remain available for provenance, but their stronger
expression-based identity labels are superseded.

### Prespecified practical evaluation

Before inspecting evaluation results, we froze a metadata-only selection rule.
Eligible series contained at least 100 samples, included a prespecified clinical
cohort term in the title, and excluded prespecified laboratory-only terms. We
ranked eligible series within array and sequencing strata by sample count and
selected the first 15 from each stratum. All 435 unordered pairs among these 30
studies formed a proposed development/validation screening set.

For each pair, we compared: (1) GSM intersection reconstructed directly from the
frozen GEO JSON, (2) documented GEO SuperSeries/subseries or explicit reuse
relationships, and (3) the corrected registry. We distinguished direct GEO
record overlap, declared SuperSeries/subseries organization, explicit
reanalysis or reuse, expression-corroborated repeated-material candidates, and
unresolved title candidates. Ordinary declared reuse was not called hidden
leakage.

OpenAI Codex (GPT-5.6 Sol; OpenAI; accessed September 27-October 2, 2026)
assisted with software development and automated retrieval and processing of
public GEO data. The author verified source records, classifications, and
analytical outputs. The system was not treated as an author or independent
reviewer.

## Evaluation

### Registry coverage

The 5,931 series contained 282,989 sample mentions and 238,252 unique GSMs.
Among them, 41,428 GSMs occurred in more than one series, involving 1,622 GSEs
and 1,165 series pairs. There were 952 complete-containment, 59 near-containment,
and 154 partial-overlap pairs.

The largest overlap joined GSE81540 and GSE96058: all 3,409 GSMs in GSE96058
also occurred in GSE81540. Other large overlaps included 2,090 shared GSMs for
GSE210283–GSE211146 and partial overlaps of 359 for GSE22133–GSE25307 and 307
for GSE10893–GSE26338. These counts show why different GSE accessions alone do
not establish independence.

### Candidate evidence and corrected release

The title rule generated 2,125 candidate alias groups and 4,279 cross-series
links under different GSMs. In the seed-family expression experiment, 304 of
385 identifier candidates exceeded the stronger rule, 12 exceeded only the
weaker rule, and 69 were not corroborated. All 304 stronger-rule candidates were
reciprocal top-1 matches; their minimum correlation was 0.732169 and 113 were
below 0.95. These measurements are retained as candidate evidence but cannot
establish identity without independent source evidence.

Among the 1,925 development controls, zero exceeded the stronger rule, four
exceeded only the weaker rule, and 1,921 exceeded neither. These dependent
control counts do not support a rule-of-three or false-confirmation probability
bound.

Release 3 contains 1,950 series pairs: 1,165 direct accession overlaps, two
documented GEO reuse relationships without a direct-overlap edge, and 783
candidate relationships requiring review. Seven expression-only pairs that
release 2 had promoted to high confidence are now review-required. No candidate
is described by the software as a confirmed same specimen.

### Practical cohort-selection evaluation

The prespecified rule selected 15 array and 15 sequencing studies. Direct GSM
intersection found two overlapping pairs. The release-3 checker returned the
same two pairs with identical counts and no mismatch across all 435 comparisons.

GSE81538 shared 405 GSMs with GSE81540, and GSE96058 shared 3,409 with GSE81540.
GEO explicitly identifies GSE81540 as a SuperSeries of GSE81538 and GSE96058,
and identifies both constituents as SubSeries of GSE81540. These are declared
organizational relationships, not hidden leakage. A user proposing GSE81540 as
development data and either constituent as validation data should choose one
cohort definition or deduplicate the shared GSMs.

The registry added one pair beyond direct GSM intersection. GSE115577 and
GSE93601 had 1,110 specific-title candidates but no shared GSM and no documented
GEO relationship among the evaluated sources. This result changes the workflow
only by triggering source review; it does not justify automatic exclusion or a
claim of duplicate patients.

Overall, 432 pairs had no detected evidence, two had direct and declared
SuperSeries/subseries overlap, and one had an unresolved candidate relationship.
The checker therefore reproduced the simple accession-intersection baseline and
consolidated GEO provenance and candidate triage. Its incremental finding beyond
direct intersection was modest.

### Verification

All exact-overlap rows had previously been independently reconstructed from the
frozen JSON with zero count mismatches, and all archived manifest hashes matched
their local files. The release-3 suite contains 25 tests, including explicit
checks that expression-only evidence cannot become direct overlap, that the
control summary contains no probability bound, and that the practical
evaluation agrees with reconstructed GSM intersection.

## Relevance

The intended user is a cancer researcher selecting public cohorts. Before model
fitting, the researcher supplies proposed GSE accessions and receives direct GSM
counts, documented reuse evidence, review-required candidates, source links,
and an allowable interpretation. A direct overlap requires de-duplication or a
change in cohort assignment. A candidate requires manual review. No detected
evidence does not certify independence.

The evaluation also defines the resource's limit. For the metadata-selected
studies, direct GSM intersection found the two actionable overlaps and GEO had
already declared both as SuperSeries/subseries relationships. The registry made
the check reproducible and convenient but did not uncover a hidden verified
patient overlap. This restrained result is the appropriate basis for a narrow
resource claim.

Limitations include the frozen query rather than all GEO, heterogeneous clinical
and laboratory records, incomplete public source disclosure, and no externally
validated different-accession identity classifier. Expression work covered only
seven GPL96 development series and a three-candidate held-out cell-line pair;
it cannot estimate patient-level sensitivity, specificity, or false-discovery
rates. Title candidates can denote related studies, aliquots, repeated assays,
or unrelated local identifiers. The practical evaluation sampled 30 large
metadata-selected studies and found only one unresolved candidate beyond direct
intersection. The registry does not estimate performance inflation, identify
misconduct, or replace raw-file hashes and patient-level identifiers when those
are available.

## How to Access and Use

The intended command is:

```text
python src/check_cohort_overlap.py GSE20194 GSE25055 GSE25065
```

The repository contains the frozen inventories, release tables, protocols,
source code, tests, cached public relationship records, evaluation outputs, and
figures. Code is MIT licensed; derived tables and documentation are CC BY 4.0.

## Data Sharing Statement

All source data are public through NCBI GEO. The derived registry and software
are available at https://github.com/lemnk/breast-cohort-leakage-resource. The
frozen version 2 release is archived at
https://doi.org/10.5281/zenodo.23004247. A new immutable DOI for release 3 is the
remaining archival dependency before submission.

## Author Contributions

Naol Beyene: Conceptualization, methodology, software, validation, formal
analysis, data curation, writing—original draft, writing—review and editing, and
visualization.

## Support

No external funding was received. The author conducted the work independently.
Jackson State University did not provide financial support or endorsement.

## Disclosures

The author has no potential conflicts of interest to disclose. OpenAI Codex
(GPT-5.6 Sol; OpenAI; accessed September 27-October 2, 2026) assisted with
software development and automated retrieval and processing of public GEO data.
The author verified source records and outputs and accepts responsibility for
the work. The AI system is not an author.

## References

1. Edgar R, Domrachev M, Lash AE. Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. *Nucleic Acids Res*. 2002;30:207-210. doi:10.1093/nar/30.1.207.
2. Barrett T, Wilhite SE, Ledoux P, et al. NCBI GEO: archive for functional genomics data sets—update. *Nucleic Acids Res*. 2013;41:D991-D995. doi:10.1093/nar/gks1193.
3. Rosikiewicz M, Comte A, Niknejad A, Robinson-Rechavi M, Bastian FB. Uncovering hidden duplicated content in public transcriptomics data. *Database (Oxford)*. 2013;2013:bat010. doi:10.1093/database/bat010.
4. Waldron L, Riester M, Ramos M, Parmigiani G, Birrer M. The Doppelgänger Effect: Hidden Duplicates in Databases of Transcriptome Profiles. *J Natl Cancer Inst*. 2016;108:djw146. doi:10.1093/jnci/djw146.
5. Lim N, Tesar S, Belmadani M, et al. Curation of over 10,000 transcriptomic studies to enable data reuse. *Database (Oxford)*. 2021;2021:baab006. doi:10.1093/database/baab006.
6. Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management and stewardship. *Sci Data*. 2016;3:160018. doi:10.1038/sdata.2016.18.
7. Warner JL. Announcing a new article type in JCO Clinical Cancer Informatics: the Resource Report. *JCO Clin Cancer Inform*. 2026;10:e2600053. doi:10.1200/CCI-26-00053.
