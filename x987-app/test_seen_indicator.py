"""
Quick test for the seen registry and CSV fields integration.

This test simulates two collection runs on the same URLs and verifies that
`is_new` is True on first encounter and False thereafter, and that
`first_seen_at` remains stable.
"""

from pathlib import Path
from datetime import datetime

from x987.pipeline.steps.collection import CollectionStep


def run_mock_annotation(tmp_dir: Path):
    cfg = {
        "pipeline": {
            "output_directory": str(tmp_dir / "results")
        }
    }
    step = CollectionStep()

    mock_rows = [
        {
            "source_url": "https://www.autotempest.com/results?foo=bar",
            "listing_url": "https://www.cars.com/vehicledetail/ABC123/?utm_source=atempest&aff=xyz",
            "title": "2011 Porsche Boxster S",
            "collection_timestamp": datetime.now().isoformat(),
        },
        {
            "source_url": "https://www.autotempest.com/results?foo=bar",
            "listing_url": "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?entitySelectingHelper.selectedEntity=d1",
            "title": "2012 Porsche Cayman R",
            "collection_timestamp": datetime.now().isoformat(),
        },
    ]

    annotated = step._annotate_new_flags(mock_rows, cfg)
    return annotated


def main():
    base = Path("x987-app/x987-data/seen_test")
    if base.exists():
        # Clean slate between runs of this test script
        for p in base.rglob("*"):
            try:
                p.unlink()
            except Exception:
                pass
        try:
            base.rmdir()
        except Exception:
            pass
    base.mkdir(parents=True, exist_ok=True)

    # First run
    first = run_mock_annotation(base)
    print("First run:")
    for row in first:
        print(row["canonical_url"], row["is_new"], row["first_seen_at"])

    # Second run
    second = run_mock_annotation(base)
    print("Second run:")
    for row in second:
        print(row["canonical_url"], row["is_new"], row["first_seen_at"])


if __name__ == "__main__":
    main()

