# Computational Report: Breast Cancer Cohort-Overlap Resource, Release 1

## Executive result

Release 1 is a functioning, query-defined audit resource rather than a new
prediction model. Across 540 GEO series returned by four frozen breast cancer
treatment-response searches, the registry contains 40,734 sample mentions and
35,654 unique GSM accessions. A total of 4,331 GSM accessions occurred in more
than one series. These exact records connected 56 series across 48 series pairs.

The reuse was not uniform: 33 pairs showed complete containment of the smaller
series, six showed at least 80% containment, and nine showed partial overlap.
Partial overlap is the most operationally important pattern because two series
can appear distinct while sharing only part of their samples.

Exact, specific sample titles linked a further 331 alias groups across different
GSM accessions, producing 340 candidate links across 18 series pairs. These are
review candidates, not confirmed duplicate patients.

An initial engineering rule also admitted generic labels such as “patient 10,”
“tumor 1,” and “sample_001,” creating implausible links between unrelated
studies. Those patterns, common cell-line identifiers, and normalization that
collapsed terminal positive/negative signs were removed before release 1. The
correction reduced manual-review pairs from 43 to nine without changing the 55
high-confidence pairs.

## Seed-family validation

Eleven seed matrices (1,947 deposited samples) were downloaded with hashes and
parsed directly from gzip files. Conservative identifiers yielded 385
cross-series candidate links involving 660 deposited sample records.

Expression fingerprints used 2,048 probes selected by a fixed cryptographic
ordering from 22,283 probes common to seven GPL96 series. Each candidate was
compared with five deterministic nonmatched controls (1,925 controls total).
The median candidate correlation was 0.8893, versus 0.7666 for controls; the
overall control 99th percentile was 0.8968. Because preprocessing differed by
series, absolute correlations varied substantially by pair.

Under the frozen evidence rules, 304 links were confirmed, 12 supported, and 69
not corroborated. All 304 confirmed links were reciprocal top-1 expression
matches. In the largest comparison, GSE20194–GSE25055 had 188 identifier links;
187 were confirmed and one was not corroborated. Their median correlation was
0.9999997. GSE23988–GSE42822 had 60 identifier links; 57 were confirmed, one
supported, and two were not corroborated.

The unfavorable finding is important: identifiers alone were not uniformly
reliable across differently processed matrices. The 69 uncorroborated links
remain visible and are not counted as confirmed identities.

## Release artifact

The merged lookup contains 64 series pairs with some detected evidence:

- 55 high-confidence overlap pairs;
- 9 pairs requiring manual review;
- zero pairs assigned to the intermediate probable-only tier in release 1.

The command-line checker accepts two or more GSE accessions and reports the
evidence class and counts. For an in-scope pair absent from the lookup, it returns
“no detected evidence—not proof of independence.”

## Verification

- Twelve unit tests pass, including identifier normalization, namespace handling,
  rejection of short aliases, known GSE20194–GSE25055 overlap, and cautious
  wording for an edge-free pair.
- All 11 downloaded matrices were checksum-recorded.
- Matrix parsing and fingerprinting are streaming; no decompressed expression
  copies are retained.
- Four figures are generated in both PNG and vector PDF formats.
- Free disk space remained above the predeclared 1-GB floor.

## Interpretation

GSE accession inequality is not a sufficient independence check. Much of the
exact reuse reflects legitimate GEO organization such as parent/subseries
containment, but partial overlap and different-GSM aliases require deliberate
screening before cohorts are split into development and validation roles.

This release does **not** estimate how often published validation claims are
invalid, prove that any author concealed overlap, or establish clinical harm.
It supplies auditable evidence that researchers can check before analysis.

## Limitations and remaining work

1. The 540-series universe is search-defined and contains laboratory and
   non-neoadjuvant records; manual clinical-cohort adjudication is incomplete.
2. Exact-title matches with different GSM accessions can reflect different
   assays, aliquots, time points, or coincidental local identifiers.
3. Expression thresholds were developed on known seed relationships and require
   held-out cross-platform validation.
4. Expression corroboration is currently limited to compatible GPL96 matrices.
5. An active public repository/DOI is required before a JCO CCI Resource Report
   submission; local files alone do not satisfy the journal's access requirement.
6. A clinician/researcher usability evaluation would materially strengthen the
   claim that the checker improves cohort selection in practice.

## Journal fit

JCO Clinical Cancer Informatics introduced the Resource Report format for tools,
repositories, knowledge bases, and services. The current ASCO specification
allows 3,000 words, six figures/tables, and 75 references; it requires a
five-part structured abstract, data-sharing statement, clear licensing/access,
FAIR accessibility, and experimental or clinical validation. The resource is
aligned with the format, but the public link, manual adjudication, and held-out
validation remain submission dependencies.

Official sources: [JCO CCI scope](https://ascopubs.org/cci/about), [ASCO article
types](https://ascopubs.org/authors/article-types), and [GEO download
policy](https://www.ncbi.nlm.nih.gov/geo/info/download.html).
