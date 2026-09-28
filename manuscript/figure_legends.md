# Figure Legends

**Figure 1. Construction of the breast cancer cohort-overlap resource.** The
frozen GEO query supplied the platform-agnostic registry. Exact GSM reuse and
specific-title candidates were supplemented by a seven-series GPL96 expression-
fingerprint experiment. Expression corroboration affected evidence strength but
did not remove uncorroborated candidates from review.

**Figure 2. Largest exact-accession overlaps between GEO series.** Bars show the
20 series pairs with the largest numbers of shared GSM accessions. Complete
containment means that every GSM in the smaller series occurred in the larger;
near containment denotes 80% to less than 100%; partial overlap denotes less
than 80%.

**Figure 3. Expression fingerprints distinguish many candidate reuses from
nonmatched controls.** Box plots compare within-sample probe-rank correlations
for study-aware identifier candidates and five deterministic nonmatched controls
per candidate within each eligible GPL96 series pair. Boxes show interquartile
ranges and medians; whiskers use the standard 1.5-interquartile-range rule;
outliers are omitted from the display but retained in analysis. This is internal
seed-family corroboration, not an external accuracy estimate.

**Figure 4. Evidence tier in release 2.** Counts are series pairs, not patients
or publications. High-confidence evidence requires exact GSM reuse or a
confirmed seed expression link. Manual-review pairs contain title or
uncorroborated identifier evidence only.

**Figure 5. Validation findings and scope limits.** (A) The frozen strict title
rule recovered 47.3% of 55,895 known exact-GSM reuse mention pairs and collided
in none of 100,000 presumed-background pairs. The background pairs were not
identity-verified negatives, so the zero collision count is not a precision
estimate. The 47.3% is recovery conditional on exact-GSM reuse, not sensitivity
for same-patient/material identity under different GSM accessions. (B) The
registry contains 5,931 series and 138 GPL96 series, but only
seven GPL96 series entered expression-rule evaluation (0.12% of the registry).

**Figure 6. Held-out GPL96–GPL570 cell-line fingerprint check.** The pair was
selected from frozen metadata before the candidate expression profiles were
accessed. Points show probe-rank correlations for 15 deterministic controls and
three title candidates. UACC812 and ZR-75-30 were reciprocal top-1 matches and
met the frozen confirmation rule. ZR-75-1 ranked first in one direction but
ninth in the reverse direction and was not corroborated. The dashed line is the
control 99th percentile. This cell-line result does not estimate patient-level
or RNA-sequencing accuracy.
