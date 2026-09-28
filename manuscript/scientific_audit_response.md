# Scientific Audit Response

This document records changes made after critique of the draft. It is not a
claim that the remaining limitations have been solved.

## Threshold circularity

The abstract, Methods, Results, and limitations now state that expression rules
were developed and evaluated in the same GPL96 seed family. The analysis is
described as internal corroboration, not an external sensitivity, specificity,
or false-discovery estimate.

## Held-out transport and platform scope

A registry-wide platform audit was added. Expression-rule evaluation covers
seven GPL96 seed series, or 0.12% of the 5,931-series universe. A nonseed pair
was then selected from metadata before expression access. Candidate-level
platform inspection required a recorded amendment from GPL96–GPL96 to
GPL96–GPL570. Frozen rules confirmed two of three cell-line candidates; one was
not corroborated, and none of 15 controls triggered. This is held-out transport
evidence, not a patient-level, general cross-platform, or RNA-seq accuracy estimate.

## Multiplicity and false confirmations

The unchanged expression rules were applied to all 1,925 deterministic
nonmatches. Zero controls met the confirmation rule and four met the support
rule. A rule-of-three approximation gives an approximate 95% upper control-
confirmation-rate bound corresponding to 0.6 confirmations per 385 comparisons.
The manuscript explains why this internal calibration bound,
rather than a per-edge multiple-testing correction, is reported and why it is
not an external FDR estimate.

## Title-rule evaluation

The frozen rule recovered 26,426 of 55,895 known exact-GSM reuse mention pairs
(47.3%) and collided in none of 100,000 deterministic presumed-background pairs.
The manuscript now identifies 47.3% as recovery conditional on exact-GSM reuse,
not sensitivity for same-patient/material identity under different GSM
accessions, and it does not interpret the background as an identity-verified
negative set. A structured public-record review classified all 100 deterministic
audit links: 40 confirmed, two probable, 34 related/model-only without established
identity, 23 with evidence against identity, and one indeterminate. Evidence,
source URLs, reviewer, and date are populated. The 42/100 affirmative-support
fraction is explicitly not called precision; unresolved cases are not negatives,
and clustering within series pairs precludes a simple binomial interval.
Sole author Naol Beyene manually verified all 100 classifications and sources.

## Explicit GEO reuse metadata

The frozen series metadata contained 27 “Third-party reanalysis” labels and two
in-universe cross-series relationships with explicit GSM references: GSE65314
cited 33 GSE32124 profiles and GSE22664 cited two GSE3156 profiles. Both were
normalization-data uses, not shared-patient evidence, and remain separate from
the overlap tiers.

## Prior work and novelty

The Background now discusses the Bgee duplicate-content analysis, doppelgangR,
and Gemma. The novelty claim is narrowed to a comprehensive, breast-cancer-
specific, metadata-first GEO registry and preanalysis GSE-pair checker. The
manuscript no longer implies that expression-based duplicate detection is new.

## Reproducibility

The local pipeline regenerates the added validation outputs and six figures.
All 20 tests passed. A new full reproducibility audit covers the held-out outputs
and sixth figure.

## Remaining dependencies

Before submission, sole author Naol Beyene must add affiliation and contact details, complete the
required disclosure, publish the repository, and create an archived DOI. No
external funding was received. Patient-level and RNA-seq benchmarks remain necessary for any
broader expression-fingerprint accuracy claim.
