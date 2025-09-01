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
    fair_value_usd: Optional[int] = None
    deal_delta_usd: Optional[int] = None

    # Colors (separate fields per schema)
    exterior: Optional[str] = None
    interior: Optional[str] = None
    color_ext_bucket: Optional[str] = None
    color_int_bucket: Optional[str] = None

    # Options
    raw_options: Optional[str] = None
    options_list: Optional[List[str]] = field(default_factory=list)
    options_value: Optional[int] = None
    options_summary: Optional[Dict[str, Any]] = None
    options_detected: Optional[List[str]] = None
    options_by_category: Optional[Dict[str, Any]] = None
    top_options: Optional[str] = None

    # Other
    vin: Optional[str] = None
    location: Optional[str] = None
    error: Optional[str] = None

    # Transitional legacy aliases (accepted on input; not authoritative)
    model_trim: Optional[str] = None
    price_usd: Optional[int] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None

    def __post_init__(self):
        # Derive model/trim from model_trim if separate fields missing
        if (not self.model) and self.model_trim:
            try:
                parts = str(self.model_trim).strip().split(" ", 1)
                self.model = parts[0] if parts and parts[0] else self.model
                if len(parts) > 1 and parts[1]:
                    self.trim = parts[1]
            except Exception:
                pass

        # Keep aliases in sync (asking_price_usd <-> price_usd)
        if self.asking_price_usd is None and self.price_usd is not None:
            self.asking_price_usd = self.price_usd
        if self.price_usd is None and self.asking_price_usd is not None:
            self.price_usd = self.asking_price_usd

        # Colors: prefer exterior/interior; map legacy if needed
        if (not self.exterior) and self.exterior_color:
            self.exterior = self.exterior_color
        if (not self.interior) and self.interior_color:
            self.interior = self.interior_color
        # Maintain legacy mirrors for compatibility
        if (not self.exterior_color) and self.exterior:
            self.exterior_color = self.exterior
        if (not self.interior_color) and self.interior:
            self.interior_color = self.interior


# Lightweight typed mapping for generic listing records
try:
    from typing import TypedDict  # py3.8+

    class ListingData(TypedDict, total=False):
        year: Optional[int]
        model: Optional[str]
        trim: Optional[str]
        model_trim: Optional[str]
        asking_price_usd: Optional[int]
        mileage: Optional[int]
        total_options_msrp: Optional[int]
        options_list: Optional[List[str]]
        exterior: Optional[str]
        interior: Optional[str]
        listing_url: Optional[str]
        source_url: Optional[str]
        deal_delta_usd: Optional[int]
except Exception:
    # Fallback if TypedDict unavailable
    ListingData = Dict[str, Any]  # type: ignore

