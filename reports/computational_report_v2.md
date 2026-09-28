# Computational Report: Comprehensive Release 2

## Outcome

The metadata-only expansion was feasible within the storage limit and materially
improved the resource. A frozen query retrieved 5,931 human breast-cancer
expression series containing 282,989 sample mentions. These represented 238,252
unique GSM accessions.

Direct repository reuse was extensive: 41,428 GSM accessions appeared in more
than one GSE. They connected 1,622 series across 1,165 series pairs. Of those
pairs, 952 showed complete containment of the smaller series, 59 near
containment, and 154 partial overlap. Partial relationships included 359 shared
records between GSE22133 and GSE25307 and 307 between GSE10893 and GSE26338.

The strict specific-title rule produced 2,125 alias groups, 4,279 different-GSM
candidate links, and 787 series pairs. These remain review evidence; they are not
counted as confirmed duplicate patients.

After merging comprehensive metadata with the unchanged seed expression
evaluation, the release-2 lookup contains 1,948 pairs: 1,172 high-confidence and
776 manual-review pairs. High-confidence evidence involves 1,626 series. The
seven high-confidence pairs beyond the 1,165 exact-GSM pairs arise from confirmed
seed-family expression links under different GSM identifiers.

## Method validation retained from release 1

The 11 seed matrices include 1,947 samples. Among seven GPL96 series, 385
identifier candidates were evaluated on 2,048 prespecified probes against 1,925
deterministic nonmatches. There were 304 confirmed, 12 supported, and 69
uncorroborated links. All confirmed links were reciprocal top-1 expression
matches. GSE20194–GSE25055 contributed 188 candidates, of which 187 were
confirmed; median rank correlation was 0.9999997.

The 69 failures are retained. They show why a shared identifier is evidence for
review, not automatic proof.

## Post-audit validation findings

The strict title rule was tested against 55,895 cross-series mention pairs that
reuse the same GSM. Although normalized titles matched in every pair, the strict
rule recovered 26,426 (47.3%). This is recovery only within exact-GSM reuse, not
sensitivity for detecting the same patient or material under different GSM
accessions. It produced zero collisions in 100,000 deterministic cross-series,
different-GSM background pairs. Those pairs are presumed nonmatches rather than
identity-verified negatives, so this is not a precision estimate. Only 350 of
4,279 title links had added study-context support.

A structured Codex-assisted public-record review classified all 100 links in the
frozen audit sample: 40 confirmed same patient/sample/material, two probable,
34 related study/model without established identity, 23 with evidence against
identity, and one indeterminate. Confirmed plus probable yielded 42/100
affirmative support in this deterministic sample; 35 unresolved links were not
treated as negatives. This 42% support fraction is not title-rule precision
because links are clustered within 57 series pairs (33/100 arise from one pair)
and were not sampled as independent random observations. Formal binomial
confidence intervals are therefore not used. Sole author Naol Beyene manually
verified all 100 classifications and cited sources.

An explicit-metadata audit found 27 series labeled “Third-party reanalysis.” Of
135 GSM accessions named in series-level metadata, 35 mapped across two in-scope
series relationships: GSE65314 cited 33 GSE32124 profiles for normalization and
GSE22664 cited two GSE3156 profiles as normalization references. These are data-
use relationships, not proof of shared patients or specimens, and were kept
separate from overlap evidence tiers.

The expression rules were applied to all 1,925 deterministic nonmatches. Four
met the support rule, but none met the confirmation rule. The observed control-
confirmation rate was 0/1,925. A rule-of-three approximation gives an approximate
95% upper bound of 3/1,925 on that rate, corresponding to approximately 0.6
control confirmations per 385 comparisons under this design. This is an internal
calibration bound, not a multiplicity-adjusted false-discovery estimate.

Platform coverage is the main scope limitation. The registry includes 630
platform identifiers, with 2,896 high-throughput-sequencing series and 2,265
array series as sole listed data types. GPL96 occurs in 138 series, while only
seven GPL96 series entered expression-rule evaluation—0.12% of the 5,931-series
universe. No RNA-seq or general cross-platform accuracy claim is supportable.

## Held-out cross-platform extension

The frozen registry contained one nonseed title-candidate pair in which both
series listed GPL96: GSE16795–GSE21217. Before expression download, this pair
and the unchanged fingerprint rules were frozen. Candidate-level matrix metadata
then showed that the three candidates were on GPL96 in GSE16795 and GPL570 in
GSE21217. The failed same-platform attempt was retained, and the deviation was
recorded before downloading the GPL570 matrix.

Using 2,048 of 22,277 common probes, UACC812 and ZR-75-30 were reciprocal top-1
matches and confirmed. ZR-75-1 ranked first in one direction but ninth in the
other and was not corroborated. None of 15 deterministic controls met the
confirmation or support rule. This mixed 2/3 result is an untouched pair-level
transport check across GPL96 and GPL570. It involves cell lines, not patient
specimens, and is far too small to estimate general sensitivity or specificity.

The author-verified 100-link review is supplied as a controlled workbook with
five-category decisions, evidence, source links, reviewer identity, review date,
author sign-off, and summary counts.

The manuscript now positions the resource against prior work instead of claiming
novel duplicate detection. Bgee previously identified duplicated Affymetrix
content, doppelgangR performs expression-based cross-study and cross-platform
matching, and Gemma removes repeated GSMs during curation. The present
contribution is the comprehensive breast-cancer-specific, metadata-first GEO
registry and preanalysis pair checker.

## Reproducibility and storage

- The comprehensive raw API response is 41.3 MB; no additional expression data
  were needed.
- Twenty unit tests pass.
- The release-1 local rerun left 24 analytic files byte-for-byte unchanged.
- Release-2 regeneration was repeated after manuscript revision; all seven
  comprehensive analytic files were byte-for-byte unchanged.
- Approximately 2.34 GB remained free after the expansion.

## Interpretation

Different GSE accessions frequently share exact GEO sample records. Most pairs
show complete containment compatible with ordinary repository organization, but
154 partial-overlap pairs are operationally harder to recognize and directly
relevant to cohort independence checks.

The resource does not show that 1,172 published validations are leaked. It shows
that those series pairs contain direct or strongly corroborated overlap and
should not be assumed independent without patient-level review. Title candidates
are kept separate to prevent speculative matches from inflating the primary
result.

## Remaining submission dependencies

1. Publish the code and versioned release at a stable URL and archive DOI.
2. Add a patient-level or RNA-seq held-out validation if broader fingerprint
   performance claims are desired.
3. Add a small prospective usability evaluation or worked cohort-selection case
   study to demonstrate how the checker changes an analysis decision.
4. Add Naol Beyene's affiliation and contact details and complete the required
   disclosure. The sole-author and no-external-funding statements are populated.

These are real limitations. The comprehensive exact-GSM registry is now a
credible Resource Report foundation, but it is not submission-complete until the
resource is publicly accessible.
