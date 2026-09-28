"""Write SHA-256 hashes for distributable release and analysis files."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = [
    "README.md",
    "PROJECT_PLAN.md",
    "PROTOCOL_v1_20260927.md",
    "PROTOCOL_v2_20260927.md",
    "PROTOCOL_v3_HELDOUT_20260927.md",
    "PROTOCOL_v3A_DEVIATION_20260927.md",
    "requirements.txt",
    "run_pipeline.ps1",
    "LICENSE",
    "DATA_LICENSE.md",
    "config",
    "src",
    "tests",
    "release",
    "release_v2",
    "reports",
    "manuscript",
    "figures",
    "data/heldout/heldout_crossplatform_candidates.csv",
    "data/heldout/heldout_crossplatform_controls.csv",
    "data/heldout/heldout_crossplatform_summary.json",
    "data/heldout/heldout_crossplatform_probe_ids.txt",
    "data/heldout/source_files.json",
    "tools/build_manual_audit_workbook.mjs",
]

EXCLUDE_RELATIVE = {
    "reports/validation/final_pipeline_run.log",
}


def distributable(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    return (
        relative not in EXCLUDE_RELATIVE
        and "__pycache__" not in path.parts
        and "workbook_preview" not in path.parts
        and not path.name.endswith(".inspect.ndjson")
    )


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    files: list[Path] = []
    for name in INCLUDE:
        path = ROOT / name
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and distributable(p))
    manifest = ROOT / "MANIFEST.sha256"
    lines = [f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in sorted(set(files))]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} hashes to {manifest}")


if __name__ == "__main__":
    main()
