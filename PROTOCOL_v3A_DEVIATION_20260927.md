# Protocol v3A Deviation: Candidate-Level Platform Correction

**Recorded before downloading or inspecting the GPL570 expression matrix.**

Protocol v3 selected GSE16795–GSE21217 because both series-level records list
GPL96. The downloaded GSE21217 GPL96 matrix did not contain the three frozen
candidate GSMs. Matrix metadata showed that its GPL96 samples are BT01–BT12,
whereas candidates GSM530553–GSM530555 belong to the GPL570 component. The v3
same-platform analysis was therefore not runnable and produced no candidate
results.

The held-out test is amended to compare the GSE16795 GPL96 matrix with the
GSE21217 GPL570 matrix. Candidate selection remains unchanged and was made
without expression access. The fingerprint seed, 2,048-probe selection,
rank-correlation calculation, deterministic controls, and all confirmation and
support thresholds remain unchanged. Probe selection uses only identifiers in
the two-platform intersection.

This amendment creates a held-out cross-platform cell-line transport check. It
still cannot establish patient-level or RNA-seq performance. The failed v3
attempt and this deviation are retained for auditability.
