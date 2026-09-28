# Cover Letter Draft

Dear Editor-in-Chief,

Please consider our Resource Report, “A Reproducible Registry of Sample Reuse
Across 5,931 Public GEO Breast Cancer Expression Series,” for publication in
*JCO Clinical Cancer Informatics*.

Selecting different repository accessions is often treated as sufficient proof
that development and validation cohorts are independent. Our resource shows why
that assumption is unsafe and provides a practical preanalysis check. Across
5,931 human breast-cancer expression series in GEO, we identified 41,428 GSM
accessions reused across 1,622 series and 1,165 series pairs. Importantly, 154
pairs showed partial overlap rather than obvious complete containment. The
validated core product is this deterministic exact-GSM registry. The versioned
checker reports direct record reuse separately from uncertain title candidates;
expression fingerprints are supplemental corroboration, and absence of detected
evidence is never equated with independence.

We evaluated the more difficult different-accession matching problem in 11
method-development series. Of 385 identifier candidates, expression fingerprints
confirmed 304, supported 12, and did not corroborate 69. We report those failures
because they define the limits of identifier-only matching and support the
resource’s tiered evidence design. We then selected a nonseed series pair from
frozen metadata before accessing candidate expression profiles. With unchanged
rules, two of three GPL96–GPL570 cell-line candidates were confirmed, one was
not corroborated, and none of 15 controls triggered. We present this as a small
held-out transport check, not a patient-level accuracy estimate.

We also completed a structured public-record review of 100 deterministic title
candidates: 40 were confirmed, two probable, 35 unresolved, and 23 had evidence
against identity. We report this as a descriptive support audit—not a precision
estimate. I manually verified every row and cited source.
A second human verifier cross-checked all 100 links and agreed with every
classification. Because the verifier could see the existing classifications
and evidence, we report this as unblinded verification rather than independent
inter-reviewer reliability.

The submission is intended as an informatics safeguard for investigators,
reviewers, and editors designing or evaluating public-data biomarker studies. It
does not allege misconduct or automatically invalidate prior analyses. Code,
tests, versioned tables, and documentation are available at
**https://github.com/lemnk/breast-cohort-leakage-resource** under open licenses.
The frozen version 2.0.0 release is archived at
**https://doi.org/10.5281/zenodo.23004247**.

This work was performed independently using public data and received no external
funding or institutional sponsorship. I am the sole author and have no potential
conflicts of interest to disclose. My affiliation identifies my current status
as a Jackson State University student; the views expressed are my own and do not
necessarily represent the university.

I confirm that this manuscript is original and is not under consideration by
another journal.

Sincerely,

**Naol Beyene**

**Jackson State University**

**1400 John R. Lynch Street, Jackson, MS 39217, USA**

**naolzed6@gmail.com**
