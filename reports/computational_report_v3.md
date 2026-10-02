# Release 3 computational report

Date: October 2, 2026

## Correction implemented

Release 3 preserves releases 1 and 2 but supersedes their operational evidence
labels. Exact sharing of a GEO sample accession is now the only class called
direct accession overlap. Expression results for different GSM accessions are
retained as candidates; they do not establish same-specimen or same-patient
identity and cannot promote a series pair to a confirmed or high-confidence
identity class.

The 385 development candidates were relabeled without changing their measured
correlations or ranks: 304 exceeded the stronger candidate-corroboration rule,
12 exceeded only the weaker rule, and 69 were not corroborated. All 304 stronger-
rule candidates were reciprocal top-1 matches. Their minimum Spearman
correlation was 0.732169, and 113 were below 0.95. These facts motivate the
semantic correction; they do not prove that any candidate is false.

Among 1,925 dependent, study-family-specific presumed nonmatch controls, zero
exceeded the stronger rule and four exceeded only the weaker rule. These are
descriptive development-set counts. Release 3 reports no rule-of-three bound,
binomial confidence interval, false-discovery estimate, or extrapolated number
of false confirmations.

## Release composition

The corrected lookup contains 1,950 series pairs:

- 1,165 with direct GSM accession overlap;
- 2 with explicit GEO normalization/reuse relationships but no direct GSM edge
  in the comprehensive lookup; and
- 783 with title or expression candidate evidence requiring manual review.

Seven expression-only series pairs previously promoted into the release-2
high-confidence tier are now review-required candidates. The two explicit GEO
reuse pairs were added as a separate provenance class, increasing the lookup
from 1,948 to 1,950 rows. No historical output was deleted or overwritten.

## Prespecified bounded resource evaluation

The evaluation protocol was committed before results were generated. From the
frozen 5,931-series inventory, a metadata-only rule selected the 15 largest
eligible array series and 15 largest eligible sequencing series with clinical-
cohort terms and without prespecified laboratory-only terms. This produced 30
studies and 435 unordered study pairs.

Direct GSM lists were reconstructed from the frozen GEO JSON independently of
the release-3 lookup. The checker found the same two direct-overlap pairs with
identical counts and zero mismatches:

- GSE81538–GSE81540 shared 405 GSMs; and
- GSE81540–GSE96058 shared 3,409 GSMs.

Public GEO quick records explicitly describe GSE81540 as the SuperSeries of
GSE81538 and GSE96058, and the two constituents as SubSeries of GSE81540. These
are declared repository organization, not hidden leakage. A cohort-selection
workflow should not use the SuperSeries and either constituent as independent
development and validation cohorts.

The corrected registry added one pair beyond direct GSM intersection:
GSE115577–GSE93601 had 1,110 identical specific-title candidates but no exact
GSM intersection or documented GEO series relationship in the evaluated
sources. This is an unresolved identity candidate. The proper action is manual
source review, not automatic exclusion and not a claim of duplicate patients.

Thus, 432 of 435 pairs had no detected evidence, two had direct and declared
SuperSeries/subseries overlap, and one was a review-required title candidate.
The incremental scientific finding beyond direct intersection was modest. The
demonstrated practical value is a versioned, auditable consolidation of exact
GSM overlap, explicit provenance, and uncertainty-aware candidate triage. The
evaluation does not establish that the checker discovers hidden patient reuse
beyond accession lists.

## Verification

The release-3 unit suite contains 25 tests. It verifies that expression-only
pairs are not labeled direct overlap, exact-overlap pairs retain their GSM
counts, the corrected control summary contains no probability bound, the
bounded evaluation contains 435 pairs with zero direct-count mismatches, and
the checker retains cautious wording for absent evidence. Release-3 figures are
written separately under `figures_v3`; release-2 figures remain available for
provenance.

## Publication interpretation

The corrected work supports only a narrow resource claim: it is a frozen
accession-overlap registry and evidence lookup for a query-defined breast-cancer
GEO universe. It does not validate a new patient-identity classifier. Whether
that narrow, convenience-and-provenance contribution is sufficient for a given
journal remains an editorial judgment. The bounded evaluation does not justify
restoring the stronger release-2 language.
