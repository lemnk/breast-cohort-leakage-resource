# Release 3 corrected lookup

Release 3 supersedes the operational evidence labels in release 2. It does not
delete or overwrite prior frozen outputs.

- `direct_accession_overlap`: at least one exact GSM is shared.
- `documented_geo_reuse`: GEO explicitly describes reuse or normalization, but
  the pair has no exact-GSM edge in the comprehensive lookup.
- `candidate_relationship_review_required`: title or expression evidence exists,
  but patient/specimen identity is unresolved.

Expression-only evidence cannot establish verified identity. The protocol is
`PROTOCOL_v3_20261002.md` at repository root. Release 3 requires its own
immutable archive DOI before manuscript submission.
