# Reproducibility Verification Log

Date: 2026-09-27

## Release 1

The complete local derivation was rerun from the saved discovery response and 11
compressed seed matrices, without redownloading. All 12 current unit tests passed.
The 24 analytic CSV/JSON/TXT files present at the start of the comparison were
byte-for-byte unchanged after regeneration.

## Release 2

The comprehensive registry and merged release were regenerated from the saved
5,931-record API response. All seven analytic files in `data/comprehensive` and
`release_v2` were byte-for-byte unchanged.

## Post-audit validation rebuild

After adding metadata-rule validation, control-rule exceedance, platform-scope
analysis, and Figure 5, the complete local pipeline was rerun from frozen inputs
with discovery and download disabled. All 12 unit tests passed. Twelve audited
analytic and figure outputs—including the expression edge and control tables,
release-2 lookup, three validation outputs, and five PNG figures—were
byte-for-byte unchanged after regeneration.

## Held-out extension rebuild

After adding the metadata-selected GSE16795–GSE21217 GPL96–GPL570 extension,
the complete local pipeline was rerun from frozen inputs with discovery and
download disabled. All 20 tests passed. Five targeted outputs—the held-out
candidate table, control table, summary, Figure 6 PNG, and unchanged release-2
lookup—were byte-for-byte identical after regeneration. The held-out result
remained two confirmed, zero supported, and one not corroborated; no control
triggered either rule.

## Structured-review rebuild

After adding the five-category 100-link public-record review and correcting the
47.3% interpretation, metadata validation, adjudication, tests, and figures were
regenerated from frozen inputs. All 20 tests passed. The adjudication CSV,
adjudication summary, metadata-rule summary, and Figure 5 PNG were byte-for-byte
unchanged on immediate regeneration. Their SHA-256 hashes were, respectively,
`91318ee7c26beecc81dbf7b8e89aa017b739b0c8c92eb236d93d24a8f9953b64`,
`2fcbfeffb96734fde8627eaf3adfaa73235efec4b8bfa78d785e6d3ecec5e819`,
`83ec93fcde9764b61dc2700cf4005b722e1c7cd766cdb89a58b195931fc4d517`,
and `a6e51624cf58081a5b39744d6a9e6fc3f7c1a4f9c28ad0da50252c72fd93c785`.
The PDF renderer embeds variable document metadata, so PNG—not PDF—was used for
the byte-level figure check.

## Final author-verification and explicit-metadata audit

The full pipeline was rerun from frozen inputs with discovery and downloads
disabled after recording Naol Beyene's verification of all 100 adjudication rows,
adding the explicit GEO reuse audit, and correcting the rule-of-three wording.
All 20 tests passed. The explicit audit recovered two normalization-data reuse
relationships containing 35 mapped GSM references; these remained separate from
the overlap evidence tiers.

## Environment

- Python: local Python 3.12 runtime
- NumPy: 2.4.2
- Matplotlib: 3.10.8
- Operating system: Windows
- Source matrices: 11 gzip-compressed GEO series matrices with hashes recorded in
  `data/discovery/downloaded_seed_matrices.json`

The final distributable-file hashes are listed in `MANIFEST.sha256`.
