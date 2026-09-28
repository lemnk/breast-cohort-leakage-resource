# A Reproducible Registry of Sample Reuse Across 5,931 Public Breast Cancer Transcriptomic Studies

**Article type:** Resource Report  
**Running title:** Breast Cancer Cohort-Overlap Resource  
**Author:** Naol Beyene  
**Affiliation:** [AFFILIATION REQUIRED]  
**Corresponding author:** Naol Beyene; naolzed6@gmail.com; [POSTAL ADDRESS REQUIRED]

## Abstract

### Background and Scope

Different GEO series accessions do not guarantee different patients or
biospecimens, and undetected reuse can compromise external validation. We built
a reproducible overlap registry for breast cancer transcriptomic series.

### Solution

A frozen GEO search defined 5,931 human breast-cancer expression series. We
recorded exact GSM reuse, conservative recurring-title candidates, and outcome-
blind expression fingerprints in 11 development series. A command-line checker
reports pairwise evidence while distinguishing “no detected evidence” from proof
of independence. Fingerprint rules developed in the GPL96 seed family provide
internal corroboration, not an independent accuracy estimate.

### Evaluation

Among 282,989 sample mentions (238,252 unique GSMs), 41,428 GSMs recurred,
connecting 1,622 series and 1,165 pairs. Specific titles produced 2,125 additional
alias groups. Expression evidence confirmed 304 of 385 seed-family identifier
candidates and supported 12; none of 1,925 deterministic nonmatches met the
confirmation rule. Within exact-GSM reuse, the title rule recovered 47.3% and
had no collisions among 100,000 presumed-background pairs, which were not
verified negatives. Structured review of 100 title candidates classified 40 as
confirmed, two probable, 35 unresolved, and 23 against identity; the sole author
verified all rows. Release 2 contains 1,172 high-confidence and 776
review-required pairs. In a held-out GPL96–GPL570 cell-line pair, unchanged rules
confirmed two of three candidates; none of 15 controls triggered.

### Relevance

The registry is a preanalysis safeguard, not evidence of misconduct or proof
that unlinked cohorts are independent.

### How to Access/Use

Code, tables, tests, and documentation are available at
**https://github.com/lemnk/breast-cohort-leakage-resource**; an archive DOI will
be added before submission.

## Background and Scope

External validation is meant to test whether a model retains value beyond the
data used to develop it. In public transcriptomic research, independence is
often operationalized by choosing a different repository accession. This is
convenient but unsafe. GEO permits the same GSM record to belong to a focused
series and a SuperSeries; investigators may also redeposit or remeasure material
under a new GSM identifier. A publication can therefore describe an apparently
new cohort while sharing patients, specimens, or assays with data used earlier.

This distinction matters in breast cancer treatment-response modeling. The
number of pathologic complete responses in a public validation cohort is often
small, and even modest overlap can narrow uncertainty or exaggerate performance.
The problem is not limited to intentional or inappropriate reuse. Legitimate
study organization, secondary assays, serial biopsies, and public data
reanalysis all create repeated records. The practical failure occurs when those
relationships are not recognized before development and validation roles are
assigned.

GEO exposes accession-level metadata, but it does not provide a cohort-
independence certificate. Existing reporting guidance emphasizes clear cohort
definitions and independent validation, yet a researcher planning an analysis
still has to reconcile sample identifiers across series manually. We therefore
built the Breast Cancer Cohort-Overlap Resource, a versioned registry and checker
that answers a narrow operational question: what evidence of shared samples or
patients is detectable between proposed public cohorts before a model is fit?

The resource is deliberately conservative. It separates direct record reuse,
specific-title candidates, study-aware aliases, and expression corroboration.
It never interprets the absence of an edge as proof of independence. Release 2
focuses on human breast cancer expression series, with an intensively evaluated seed set containing
known related series. The objective is a reusable informatics safeguard, not a
new response predictor and not an estimate of misconduct.

### Relationship to prior work

This resource is not the first duplicate-expression detector. Rosikiewicz et al.
identified duplicated Affymetrix content using file and expression signatures,
and Waldron et al. introduced doppelgangR, including pair-specific expression
outlier detection across microarray platforms and between microarray and RNA-
sequencing data. Gemma also removes repeated GSM accessions during curation and
manually resolves some different-accession duplicates. Our narrower contribution
is a frozen, breast-cancer-specific GEO registry that checks exact GSM reuse
across thousands of series before analysis, exposes pair-level evidence through
a simple command, and separates uncertain metadata links from confirmed reuse.
The GPL96 fingerprint experiment is supporting evidence, not a replacement for
doppelgangR or curated cross-platform review.

## Solution

### Discovery universe and source provenance

On September 27, 2026, we queried the NCBI GEO DataSets database for records
containing “breast cancer,” restricted to human GSE records with expression
profiling by array or high-throughput sequencing. All 5,931 returned series
constituted the frozen release-2 universe. The exact query, date, raw API
response, and series inventory are retained with the release. Earlier
treatment-response searches were used only for feasibility and seed selection.

Eleven series were designated before matrix processing as mandatory method-
development seeds: GSE20194, GSE20271, GSE22093, GSE23988, GSE25055, GSE25065,
GSE32646, GSE34138, GSE41998, GSE42822, and GSE50948. They included 1,947
deposited samples and were selected because source or derivative relationships
were known or suspected from prior work. They were not treated as an independent
test set.

### Evidence classes

The primary and highest-fidelity registry operation was exact GSM reuse. For each
GSM accession in the query universe, we recorded every containing GSE. At the
series-pair level, overlap was classified as complete containment when all
samples from the smaller series were shared, near containment when at least 80%
were shared, and partial overlap otherwise. These labels describe repository
structure and do not judge whether the relationship was adequately disclosed.

Different GSM accessions may still refer to related material. We therefore
created an intentionally narrow title rule. Unicode-normalized titles were
case-folded and stripped of punctuation. A title formed a cross-series candidate
only when it contained a namespaced alphanumeric token, was at least six
characters long, was unique within each implicated series, and occurred under
different GSM accessions. Generic constructions such as “patient 10,” “tumor
1,” and “sample_001” were excluded, as were common cell-line identifiers.
Terminal positive/negative signs were retained so biologically distinct labels
did not collapse during normalization.

For the seed set, we extracted aliases from sample titles, explicit source-name
identifiers, and characteristics labeled as sample, patient, subject, or case
identifiers. Numeric values were never matched globally. They were interpreted
only when an explicit study namespace or a known deposited naming convention
was present. Aliases duplicated within a series were excluded from edge
generation.

### Expression corroboration

Identifier candidates among seven compatible GPL96 series underwent expression
corroboration. We intersected probe identifiers across matrices and selected
2,048 probes by SHA-256 ordering using the fixed seed
`breast-cohort-leakage-resource-v1`. This made feature choice independent of
clinical outcomes and observed correlations. Within each sample, expression
values were converted to ordinal probe ranks. Candidate similarity was the
Pearson correlation between rank vectors.

For every candidate link, five deterministic nonmatched controls were drawn from
the corresponding series, excluding known candidate partners. A link was called
confirmed if it was the reciprocal top-1 fingerprint match across the two
series, or if its correlation was at least 0.98 and exceeded the pair-specific
control 99th percentile by at least 0.02. A link was supported when both
directional ranks were within the top three, or correlation was at least 0.95
and exceeded that percentile by 0.01. All other links remained not corroborated.
The rules were developed on the known seed relationships and should not be
interpreted as externally estimated sensitivity and specificity.

We also applied the rules to every deterministic nonmatch. These are
classifications rather than independent hypothesis tests, so we did not attach
a conventional multiplicity correction to each edge. We instead report the
observed control-rule exceedance and a conservative rare-event bound across 385
comparisons. Because controls were presumed rather than identity-verified
nonmatches and the rule was developed in the same seed family, this is internal
calibration, not an external false-discovery-rate estimate.

### Held-out cross-platform check

Before accessing additional expression data, we searched the frozen registry
for different-GSM title candidates joining nonseed series that listed GPL96.
GSE16795–GSE21217 was the only eligible pair. Downloaded matrix metadata showed
that the three candidates were on GPL96 in GSE16795 but GPL570 in GSE21217; the
initial same-platform test was therefore not runnable. We recorded the deviation
before downloading the GPL570 matrix and applied the unchanged probe-selection,
rank-correlation, control-generation, and classification rules to the 22,277
common probes. The pair contains breast-cancer cell lines, not patient samples.

### Metadata-rule validation and structured public-record review

Exact GSM reuse supplied an outcome-independent positive set for the strict
title rule: 55,895 cross-series mentions of the same GSM. We also generated
100,000 deterministic cross-series, different-GSM presumed-background pairs;
these were not gold-standard negatives. A SHA-256-ordered sample of 100 title
candidates underwent structured public-record review of GEO headers and linked
publications. Five classes were predefined: confirmed, probable, related but
identity not established, evidence against identity, and indeterminate. The sole
author manually verified every classification and cited source. Confirmed plus
probable defined affirmative support; unresolved cases were not negatives. We
report counts and a support fraction rather than precision or a binomial interval
because 33/100 links arose from one series pair.

Separately, we searched titles, summaries, subset, and processing fields for
“Third-party reanalysis” labels and explicit GSMs, then mapped GSMs to containing
GSEs. Normalization-reference use does not establish identity, so these
relationships remained separate from overlap tiers.

### User-facing checker

Evidence was aggregated to a series-pair lookup. A pair was high-confidence if
it contained exact GSM reuse or a confirmed expression link, probable if it had
supported expression evidence only, and manual-review-required when evidence
was limited to title or uncorroborated identifier candidates. A pair with no
edge returns “no detected evidence—not proof of independence.” Accessions beyond
the 5,931-series inventory are reported as outside release scope.

## Evaluation

### Registry coverage and exact reuse

The 5,931 series contained 282,989 sample mentions representing 238,252 unique
GSM accessions. A total of 41,428 GSM accessions appeared in multiple series.
Exact reuse involved 1,622 series and 1,165 distinct series pairs. Nine hundred
fifty-two pairs showed complete containment, 59 near containment, and 154
partial overlap.

The largest complete-containment examples reflected recognizable repository
organization. All 3,409 records in GSE96058 occurred in GSE81540, and all 2,090
records in GSE211146 occurred in GSE210283. However, several large relationships
were partial: GSE22133 and GSE25307 shared 359 records, GSE10893 and GSE26338
shared 307, and GSE18229 and GSE20624 shared 184.
These findings illustrate why neither different accessions nor incomplete
containment can be ignored during validation design.

### Different-accession candidates

The specific-title rule found 2,125 alias groups and 4,279 cross-series links
under different GSM accessions. They connected 270 series across 787 pairs.
These results were retained as
candidates because an identical local identifier can denote repeated assays,
aliquots, time points, or, less commonly, unrelated local numbering.

Among 55,895 cross-series mention pairs known to reuse the same GSM, normalized
titles were identical in all pairs, but the strict candidate rule recovered
26,426 (47.3%). This is recovery conditional on exact-GSM record reuse, not the
sensitivity of the rule for detecting the same patient or material deposited
under different GSM accessions. The result shows that the deliberately narrow
identifier requirement omits many exact-reuse title matches.
The rule produced zero collisions among 100,000 presumed-background pairs; this
does not establish precision because the background lacks patient-identity
adjudication. Only 350 of 4,279 title links (8.2%) had additional study-context
support from a shared PubMed record or identical series summary. Such context
indicates related studies, not shared identity.

In the structured public-record review of 100 title candidates, 40 links were
classified as confirmed same patient/sample/material and two as probable.
Thirty-four linked related studies or models without establishing physical
identity, 23 had evidence against identity, and one was indeterminate. Thus 42
of 100 links had affirmative public-record support in this deterministic sample,
while 35 remained unresolved and were not treated as negatives. This 42%
support fraction is not a precision estimate: the link sample was clustered
within 57 series pairs and was not an independent random sample. Sole author
Naol Beyene manually verified all 100 row-level classifications and sources.

Twenty-seven series were labeled “Third-party reanalysis.” Of 135 GSMs named in
series metadata, 35 mapped across two normalization-data relationships: GSE65314
cited 33 GSE32124 profiles and GSE22664 cited two GSE3156 profiles. These remained
separate from overlap tiers.

### Fingerprint evaluation

Study-aware metadata rules generated 385 seed-family identifier links involving
660 deposited records. Fingerprints used 22,283 common probes before deterministic
selection of 2,048. Candidate median rank correlation was 0.8893, compared with
0.7666 among 1,925 nonmatched controls; the overall control 99th percentile was
0.8968. Pair-specific distributions differed, consistent with heterogeneous
upstream processing.

Expression evidence confirmed 304 links and supported 12. Sixty-nine identifier
links were not corroborated and remained visible as uncertain. All confirmed
links were reciprocal top-1 matches. GSE20194 and GSE25055 contributed 188
identifier candidates; 187 were confirmed, with median correlation 0.9999997.
Of 60 GSE23988–GSE42822 candidates, 57 were confirmed, one supported, and two
not corroborated. Conversely, several pairs had moderate absolute correlations
and incomplete nearest-neighbor recovery, demonstrating that a single universal
correlation threshold would be misleading.

No deterministic nonmatch met the confirmation rule; four met only the
supported rule. The observed control-confirmation rate was 0/1,925. A
rule-of-three approximation gives an approximate 95% upper bound of 3/1,925 on
the control-confirmation rate, corresponding to approximately 0.6 control
confirmations per 385 comparisons under this control design. This is an internal
calibration bound, not a multiplicity-adjusted false-discovery estimate.

The registry spans 630 platform identifiers. High-throughput sequencing was the
sole listed data type for 2,896 series and arrays for 2,265. GPL96 appeared in
138 series (2.3% of the universe), whereas expression-rule evaluation covered
seven GPL96 series (0.12%). Thus the platform-agnostic exact-GSM registry is
comprehensive within the frozen search, but expression corroboration has not
been evaluated for RNA-sequencing or clinical samples outside the seed family.

### Held-out transport result

The metadata-selected GSE16795–GSE21217 comparison joined GPL96 and GPL570
matrices. UACC812 (rho=0.8972) and ZR-75-30 (rho=0.9070) were reciprocal top-1
matches and met the frozen confirmation rule. ZR-75-1 had rho=0.8631, ranked
first from GSE16795 to GSE21217 but ninth in the reverse direction, and was not
corroborated. None of 15 deterministic controls met the confirmation or support
rule. These three cell-line candidates provide a small held-out cross-platform
transport check, not a patient-level accuracy estimate.

### Release composition and software checks

After evidence aggregation, release 2 contained 1,948 GSE pairs with detected
evidence: 1,172 high-confidence and 776 requiring manual review. No pair occupied
the probable-only tier. Twenty unit tests evaluated accession parsing, title
normalization, study-aware numeric handling, rejection of short identifiers,
recovery of the principal GSE20194–GSE25055 relationship, held-out result
integrity, and cautious reporting when no edge was present. All tests passed. The complete pipeline regenerates the
registry, evidence tables, lookup, validation summaries, and six figures from
frozen inputs.

## Relevance

The immediate use case is protocol design for public-data biomarker studies. A
researcher can check candidate development and validation GSEs before outcomes
are examined, document detected overlap, and either remove shared patients,
redefine the cohorts, or qualify the validation claim. Reviewers and editors can
use the same evidence table to evaluate cohort provenance without reconstructing
every sample mapping from scratch.

The clinical relevance is indirect but concrete: an “external” cohort containing
development patients weakens evidence for downstream clinical or trial use. A
provenance check can prevent that error before model evaluation.

Several limitations constrain release 2. The search-defined universe is not all
of GEO and includes laboratory, serial-biopsy, and nonclinical studies.
Manual clinical-context adjudication of the 776 review-tier pairs is incomplete.
Exact titles do not prove patient identity. Fingerprint thresholds were developed
and evaluated on related GPL96 seed series; only 0.12% of the series universe
entered that analysis. One held-out GPL96–GPL570 cell-line pair yielded two
confirmations among three candidates, but this is too small and biologically
narrow to estimate patient-level, general cross-platform, or RNA-sequencing
accuracy. The title rule recovered 47.3% within exact-GSM reuse, which is not a
general identity-detection sensitivity. The structured 100-link review provides
descriptive support counts but not title-rule precision. Processed matrices can preserve or distort similarity, and
our method does not replace raw-file hashes when those files are available. The
resource does not establish that any published analysis was leaked, quantify
bias in a specific model, or assign intent.

The main result is therefore operational: separate GSE accessions cannot safely
serve as the sole evidence of patient independence. Release 2 turns that warning
into an auditable lookup with explicit uncertainty. The next release should add
patient-level and RNA-sequencing validation, publication-level manual adjudication, and a
prospective usability study in which analysts select cohorts with and without
the checker.

## How to Access/Use

The local release includes a series inventory, pair-level lookup, sample-level
evidence files, checksums, source code, tests, protocol, and figures. After public
archiving, the permanent URL and DOI must replace the placeholder in the
abstract. The intended command is:

```text
python src/check_cohort_overlap.py GSE20194 GSE25055 GSE25065
```

The checker returns one row per pair. Users should inspect high-confidence and
review-tier evidence, follow the linked GEO records, and document any exclusion
or cohort redefinition. A “no detected evidence” result should be supplemented
with publication review and, when feasible, raw-file or expression-fingerprint
checks. Release tables are licensed under CC BY 4.0 and code under MIT.

## Data Sharing Statement

All source data are publicly available from NCBI GEO under the accessions listed
in the release. The derived registry, code, frozen configuration, hashes, and
reproducibility instructions are available at
**https://github.com/lemnk/breast-cohort-leakage-resource**. A numbered release
archive DOI will be added before submission.
The project redistributes identifiers and derived evidence; users should consult
GEO records and original publications for source-specific terms.

## Author Contributions

Naol Beyene: Conceptualization, Methodology, Software, Validation, Formal
analysis, Data curation, Writing—original draft, Writing—review and editing, and
Visualization.

## Support

No external funding was received for this work.

## Disclosures

**Conflicts of interest:** [REQUIRED: complete the ASCO disclosure process and
insert the applicable statement.]  
**Generative-AI assistance:** OpenAI Codex using the gpt-5.6-sol model assisted
with code development and automated retrieval and processing of public data. It
was not an author. The sole author manually verified the classifications,
analytical outputs, and cited sources and accepts full responsibility for the
work.

## References

1. Edgar R, Domrachev M, Lash AE. Gene Expression Omnibus: NCBI gene expression and hybridization array data repository. *Nucleic Acids Res*. 2002;30:207-210. doi:10.1093/nar/30.1.207.
2. Barrett T, Wilhite SE, Ledoux P, et al. NCBI GEO: archive for functional genomics data sets—update. *Nucleic Acids Res*. 2013;41:D991-D995. doi:10.1093/nar/gks1193.
3. Hatzis C, Pusztai L, Valero V, et al. A genomic predictor of response and survival following taxane-anthracycline chemotherapy for invasive breast cancer. *JAMA*. 2011;305:1873-1881. doi:10.1001/jama.2011.593.
4. Popovici V, Chen W, Gallas BG, et al. Effect of training-sample size and classification difficulty on the accuracy of genomic predictors. *Breast Cancer Res*. 2010;12:R5. doi:10.1186/bcr2468.
5. Shi L, Campbell G, Jones WD, et al. The MicroArray Quality Control (MAQC)-II study of common practices for the development and validation of microarray-based predictive models. *Nat Biotechnol*. 2010;28:827-838. doi:10.1038/nbt.1665.
6. Shen K, Song N, Kim Y, et al. A systematic evaluation of multi-gene predictors for the pathological response of breast cancer patients to chemotherapy. *PLoS One*. 2012;7:e49529. doi:10.1371/journal.pone.0049529.
7. Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management and stewardship. *Sci Data*. 2016;3:160018. doi:10.1038/sdata.2016.18.
8. Warner JL. Announcing a new article type in JCO Clinical Cancer Informatics: the Resource Report. *JCO Clin Cancer Inform*. 2026;10:e2600053. doi:10.1200/CCI-26-00053.
9. Rosikiewicz M, Comte A, Niknejad A, Robinson-Rechavi M, Bastian FB. Uncovering hidden duplicated content in public transcriptomics data. *Database (Oxford)*. 2013;2013:bat010. doi:10.1093/database/bat010.
10. Waldron L, Riester M, Ramos M, Parmigiani G, Birrer M. The Doppelgänger Effect: Hidden Duplicates in Databases of Transcriptome Profiles. *J Natl Cancer Inst*. 2016;108:djw146. doi:10.1093/jnci/djw146.
11. Lim N, Tesar S, Belmadani M, et al. Curation of over 10,000 transcriptomic studies to enable data reuse. *Database (Oxford)*. 2021;2021:baab006. doi:10.1093/database/baab006.
