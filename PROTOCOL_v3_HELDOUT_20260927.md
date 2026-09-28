# Protocol v3: Metadata-Selected Held-Out GPL96 Check

**Freeze date:** 2026-09-27  
**Relationship to prior work:** Release 2, its evidence tiers, and all seed-family
results remain unchanged. This is a post-release validation extension.

## Selection before expression access

The frozen 5,931-series registry was searched for series pairs meeting all of
the following conditions:

1. both series list GPL96;
2. neither series belongs to the 11-series method-development seed set;
3. the frozen strict title rule identifies at least one different-GSM candidate;
4. both series have downloadable processed series matrices.

Before either expression matrix was downloaded, exactly one registry pair met
criteria 1–3: GSE16795–GSE21217, with three candidate identifiers (UACC812,
ZR751, and ZR7530). The pair contains breast-cancer cell lines, not patient
specimens. It is therefore a held-out same-platform transport check only.

## Locked analysis

- Use the same 2,048-probe SHA-256 ordering and seed
  `breast-cohort-leakage-resource-v1` on the held-out common-probe intersection.
- Convert each sample to within-sample ordinal probe ranks.
- Compare all samples across the two matrices.
- For each of the three metadata candidates, generate five deterministic
  noncandidate controls using the existing seed and exclusion rule.
- Apply the frozen seed-family rules without retuning:
  - confirmed: reciprocal top-1, or rho >= 0.98 and at least 0.02 above the
    pair-specific control 99th percentile;
  - supported: both directional ranks <= 3, or rho >= 0.95 and at least 0.01
    above that percentile;
  - otherwise not corroborated.

The primary held-out result is the number of the three candidates assigned to
each tier. Control-rule exceedance and individual ranks/correlations are also
reported. No threshold will be changed after matrix inspection.

## Interpretation constraints

This check is independent of threshold setting at the series-pair level, but
small (three positives) and limited to cell lines on GPL96. It cannot estimate
clinical-sample sensitivity, specificity, RNA-seq performance, or cross-platform
accuracy. Failure will be reported without changing the original rules.
