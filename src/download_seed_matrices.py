"""Download the small processed-matrix layer for mandatory seed cohorts."""
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "data" / "discovery"
TARGET = ROOT / "data" / "source" / "series_matrix"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    with (DISCOVERY / "mandatory_seed_remote_files.csv").open(encoding="utf-8-sig") as handle:
        sources = [r for r in csv.DictReader(handle) if r["category"] == "matrix" and r["url"].endswith(".gz")]
    TARGET.mkdir(parents=True, exist_ok=True)
    manifest = []
    for row in sources:
        output = TARGET / Path(row["url"]).name
        expected = int(row["bytes"] or 0)
        if not output.exists() or (expected and output.stat().st_size != expected):
            partial = output.with_suffix(output.suffix + ".partial")
            request = urllib.request.Request(row["url"], headers={"User-Agent": "breast-cohort-audit/0.1"})
            with urllib.request.urlopen(request, timeout=120) as source, partial.open("wb") as sink:
                while chunk := source.read(1024 * 1024):
                    sink.write(chunk)
            if expected and partial.stat().st_size != expected:
                raise RuntimeError(f"Size mismatch for {row['accession']}")
            partial.replace(output)
        manifest.append({
            "accession": row["accession"], "source_url": row["url"],
            "bytes": output.stat().st_size, "sha256": sha256(output),
            "local_path": str(output.relative_to(ROOT)),
        })
        print(f"{row['accession']}: {output.stat().st_size / 2**20:.1f} MiB")
    (DISCOVERY / "downloaded_seed_matrices.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Downloaded/verified {len(manifest)} matrices")


if __name__ == "__main__":
    main()
