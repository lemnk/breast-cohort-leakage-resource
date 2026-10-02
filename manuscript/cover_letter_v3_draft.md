Dear Editors of JCO Clinical Cancer Informatics,

Please consider the Resource Report, “An Auditable Registry for Screening Public
GEO Breast Cancer Expression Cohorts for Accession Overlap,” by Naol Beyene.

The resource addresses a practical error in public-data cancer research: a
different GEO series accession is often treated as evidence that a validation
cohort is independent, although the same GEO sample record can occur in multiple
series. Across a frozen, query-defined universe of 5,931 human breast cancer
expression series, the registry reconstructs sample membership and identifies
1,165 GSE pairs that directly share GSM accessions.

The revised release uses deliberately narrow evidence language. Only an exact
shared GSM is called direct accession overlap. Explicit GEO reuse statements and
different-accession title or expression candidates are reported separately;
candidate evidence does not establish patient or specimen identity. Seven
expression-only pairs promoted by the prior release were returned to a manual-
review class, and an unsupported rare-event probability bound was removed.

We also conducted a prespecified practical evaluation. A metadata-only rule
selected 30 large clinical-context breast expression studies, creating 435
possible development/validation pairs. The checker exactly reproduced the two
direct GSM intersections with no count mismatch. GEO declared both as
SuperSeries/subseries relationships. The registry added one unresolved title
candidate beyond direct intersection. This is a modest result: the resource
demonstrates reproducible provenance screening and review triage, not a new
patient-identity classifier or hidden leakage in a published model.

The code, frozen inputs, protocols, row-level evidence, tests, and figures are
public at https://github.com/lemnk/breast-cohort-leakage-resource. Release 3 will
be deposited under a new immutable archive DOI before submission. The manuscript
is original, is not under consideration elsewhere, received no external
funding, and the author has no potential conflicts of interest.

Sincerely,

Naol Beyene  
Jackson State University  
1400 John R. Lynch Street  
Jackson, MS 39217, USA  
naolzed6@gmail.com
