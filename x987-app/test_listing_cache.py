"""
Simple unit test for ListingCache behavior.
"""

from pathlib import Path
from datetime import datetime, timedelta

from x987.pipeline.listing_cache import ListingCache


def main():
    base = Path('x987-app/x987-data/cache_unit')
    if base.exists():
        for p in base.rglob('*'):
            try:
                p.unlink()
            except Exception:
                pass
        try:
            base.rmdir()
        except Exception:
            pass
    base.mkdir(parents=True, exist_ok=True)
    fp = base / 'listing_cache.json'
    cache = ListingCache(fp)

    url = 'https://www.cars.com/vehicledetail/ABC123/'
    # No record yet
    print(cache.should_skip(url))
    # Save record
    cache.save_result(url, data_blob={'make': 'porsche', 'model': 'boxster'})
    cache.save()
    # Should skip now
    print(cache.should_skip(url))


if __name__ == '__main__':
    main()
