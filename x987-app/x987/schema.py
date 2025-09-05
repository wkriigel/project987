"""
Data schema definitions for normalized listings.

PROVIDES: Dataclass models used across the app and tests
CONTRACT: Primary fields follow CSV_SCHEMA.md; legacy aliases maintained during transition
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict


@dataclass
class NormalizedListing:
    # Core identifiers
    timestamp_run_id: Optional[str] = None
    source: Optional[str] = None
    listing_url: Optional[str] = None

    # Vehicle basics
    year: Optional[int] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    transmission_norm: Optional[str] = None
    transmission_raw: Optional[str] = None
    mileage: Optional[int] = None

    # Pricing
    asking_price_usd: Optional[int] = None

    # Colors (separate fields per schema)
    exterior: Optional[str] = None
    interior: Optional[str] = None
    color_ext_bucket: Optional[str] = None
    color_int_bucket: Optional[str] = None

    # Options
    raw_options: Optional[str] = None
    options_list: Optional[List[str]] = field(default_factory=list)
    # deprecated legacy fields removed: options_value
    options_summary: Optional[Dict[str, Any]] = None
    options_detected: Optional[List[str]] = None
    options_by_category: Optional[Dict[str, Any]] = None
    top_options: Optional[str] = None

    # Other
    vin: Optional[str] = None
    location: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        # Basic normalization can be added here if needed in future
        pass

# Lightweight typed mapping for generic listing records
try:
    from typing import TypedDict  # py3.8+

    class ListingData(TypedDict, total=False):
        year: Optional[int]
        model: Optional[str]
        trim: Optional[str]
        asking_price_usd: Optional[int]
        mileage: Optional[int]
        total_options_msrp: Optional[int]
        options_list: Optional[List[str]]
        exterior: Optional[str]
        interior: Optional[str]
        listing_url: Optional[str]
        source_url: Optional[str]
        # deal_delta_usd removed
except Exception:
    # Fallback if TypedDict unavailable
    ListingData = Dict[str, Any]  # type: ignore
