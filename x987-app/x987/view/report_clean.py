"""
Clean report generation module for View-from-CSV

PROVIDES: Professional report generation with clean architecture
DEPENDS: rich, schema, theme, utils
CONSUMED BY: Main pipeline and CLI
CONTRACT: Generates beautifully formatted reports
TECH CHOICE: Modular design with separated concerns
RISK: Low - focused on display only
"""

import re
import math
from pathlib import Path
from typing import List, Optional, Any, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from ..schema import NormalizedListing
from ..utils.log import get_logger
from .theme import (
    THEME, theme_style, price_style_key, miles_style_key,
    model_style_key, transmission_style_key, PRICE_W, MILES_W
)

logger = get_logger("view.report_clean")

# =========================
# CONSTANTS
# =========================
SWATCH_HALF = 2  # Half-width color swatch

# =========================
# COLOR PROCESSING
# =========================
def get_paint_hex(color_name: str) -> Optional[str]:
    """Get hex color for paint name"""
    if not color_name:
        return None
    
    # Color mappings from original code
    EXTERIOR_COLORS = {
        "arctic silver metallic": "#C9CCCE",
        "classic silver metallic": "#C6C9CB",
        "meteor gray": "#6E7479",
        "gray": "#8F969C",
        "black": "#0C0E10",
        "white": "#E9EAEA",
        "guards red": "#D0191A",
        "red": "#B0201B",
        "carrara white": "#EDEDED",
        "aqua blue metallic": "#2E6C8E",
        "malachite green metallic": "#2C5F51",
        "silver": "#C9CCCE",
        "midnight blue metallic": "#1A2C4E",
        "basalt black metallic": "#0B0F14",
    }
    
    color_lower = color_name.lower().strip()
    return EXTERIOR_COLORS.get(color_lower)

def guess_interior_hex(color_name: str) -> str:
    """Guess hex color for interior color"""
    if not color_name:
        return "#777777"
    
    # Interior color patterns
    INTERIOR_PATTERNS = [
        (r"black|anthracite|graphite|charcoal", "#0E1114"),
        (r"sand\s*beige|beige", "#CBB68B"),
        (r"tan|camel|savanna", "#B48A60"),
        (r"cocoa|espresso|chocolate|brown", "#6B4A2B"),
        (r"stone|platinum\s*gray|platinum\s*grey|gray|grey", "#A7ADB5"),
        (r"red|carmine|bordeaux", "#7E1C1C"),
        (r"blue|navy", "#2F3A56"),
        (r"white|ivory|alabaster", "#E8E8E8"),
    ]
    
    color_lower = color_name.lower().strip()
    for pattern, hex_color in INTERIOR_PATTERNS:
        if re.search(pattern, color_lower):
            return hex_color
    
    return "#777777"  # Default gray

def render_color_swatches_cell(value: str) -> Text:
    """Render color swatches for exterior/interior colors"""
    s = (value or "").strip()
    ext, intn = "", ""
    
    if "/" in s:
        ext, intn = [p.strip() for p in s.split("/", 1)]
    elif s:
        ext = s
    
    ext_hex = get_paint_hex(ext) or "#6E7479"
    int_hex = guess_interior_hex(intn) if intn else "#777777"
    
    t = Text()
    t.append(" " * SWATCH_HALF, style=theme_style(None, bg=ext_hex))
    t.append(" " * SWATCH_HALF, style=theme_style(None, bg=int_hex))
    return t

# =========================
# DATA FORMATTING
# =========================
def format_price(price_int: Optional[int]) -> str:
    """Format price as rounded k value"""
    if price_int is None:
        return ""
    
    # Round up to nearest 1k
    k_value = math.ceil(price_int / 1000)
    return f"${k_value}k"

def format_miles(miles_val: Optional[int]) -> str:
    """Format mileage as rounded k value"""
    if miles_val is None:
        return ""
    
    # Round up to nearest 1k
    k_value = math.ceil(miles_val / 1000)
    return f"{k_value}k"

def format_deal_delta(delta: Optional[int]) -> str:
    """Format deal delta with sign and optional $ prefix"""
    if delta is None:
        return ""
    
    if delta >= 0:
        return f"+{delta}"
    else:
        return f"-${abs(delta):,}"

def format_year_model_trim(year: Optional[int], model: str, trim: str) -> str:
    """Format year, model, and trim combination"""
    if not year or not model:
        return "Unknown"
    
    # Omit "Base" trim
    if not trim or trim.lower() == "base":
        return f"{year} {model}"
    else:
        return f"{year} {model} {trim}"

def format_transmission(transmission: str) -> str:
    """Format transmission display"""
    if not transmission:
        return ""
    
    # Normalize to "Automatic" or "Manual"
    if transmission.lower() in ["automatic", "pdk", "tiptronic"]:
        return "Automatic"
    elif transmission.lower() == "manual":
        return "Manual"
    else:
        return transmission

def format_colors(ext_color: str, int_color: str) -> str:
    """Format exterior/interior color combination"""
    if not ext_color and not int_color:
        return ""
    
    if ext_color and int_color:
        return f"{ext_color} / {int_color}"
    elif ext_color:
        return ext_color
    else:
        return int_color

# =========================
# TABLE GENERATION
# =========================
def create_report_table(listings: List[NormalizedListing]) -> Table:
    """Create the main report table"""
    table = Table(
        title="Porsche 987.2 Listings - Ranked by Deal Value",
        title_style=theme_style("text"),
        box=box.ROUNDED,
        show_header=True,
        header_style=theme_style("text_muted"),
        border_style=theme_style("gray_700"),
        row_styles=["", theme_style("stripe_1")]
    )
    
    # Add columns
    table.add_column("Deal Δ ($)", style=theme_style("text"), justify="right")
    table.add_column("Price", style=theme_style("text"), justify="right", width=PRICE_W)
    table.add_column("Miles", style=theme_style("text"), justify="right", width=MILES_W)
    table.add_column("Year/Model/Trim", style=theme_style("text"), justify="left")
    table.add_column("Transmission", style=theme_style("text"), justify="left")
    table.add_column("Colors (Ext/Int)", style=theme_style("text"), justify="left")
    table.add_column("Top Options", style=theme_style("text"), justify="left")
    table.add_column("Source", style=theme_style("text_muted"), justify="left")
    
    return table

def add_listing_row(table: Table, listing: NormalizedListing, row_index: int) -> None:
    """Add a listing row to the table"""
    # Get styling keys
    price_val = getattr(listing, 'asking_price_usd', None)
    price_style = price_style_key(price_val)
    miles_style = miles_style_key(listing.mileage)
    model_style = model_style_key(listing.model, listing.trim)
    transmission_style = transmission_style_key(listing.transmission_raw)
    
    # Format values
    deal_delta = format_deal_delta(listing.deal_delta)
    price = format_price(price_val)
    miles = format_miles(listing.mileage)
    year_model_trim = format_year_model_trim(listing.year, listing.model, listing.trim)
    transmission = format_transmission(listing.transmission_raw)
    ext = getattr(listing, 'exterior', None)
    intr = getattr(listing, 'interior', None)
    colors = format_colors(ext, intr)
    options = listing.top_options or ""
    source = listing.source or "unknown"
    
    # Create row with styling
    row_style = table.row_styles[row_index % len(table.row_styles)]
    
    table.add_row(
        deal_delta,
        price,
        miles,
        year_model_trim,
        transmission,
        render_color_swatches_cell(colors),
        options,
        source,
        style=row_style
    )

# =========================
# MAIN REPORT GENERATION
# =========================
def generate_report(listings: List[NormalizedListing], output_file: Optional[str] = None) -> str:
    """
    Generate a formatted report from normalized listings
    
    Args:
        listings: List of normalized listing data
        output_file: Optional file path to save report
        
    Returns:
        Formatted report string
    """
    logger.info(f"Generating report for {len(listings)} listings")
    
    if not listings:
        return "No listings to display"
    
    # Sort listings by deal delta (best deals first)
    sorted_listings = sorted(
        listings,
        key=lambda x: (x.transmission_raw != "Automatic", -(x.deal_delta or 0), x.price_usd or 0)
    )
    
    # Create table
    table = create_report_table(sorted_listings)
    
    # Add rows
    for i, listing in enumerate(sorted_listings):
        add_listing_row(table, listing, i)
    
    # Generate output
    console = Console(record=True, width=120)
    console.print(table)
    
    # Get output as string
    report_output = console.export_text()
    
    # Save to file if specified
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_output, encoding='utf-8')
        logger.info(f"Report saved to {output_file}")
    
    return report_output

def generate_summary_stats(listings: List[NormalizedListing]) -> Dict[str, Any]:
    """Generate summary statistics for listings"""
    if not listings:
        return {}
    
    # Basic counts
    total_listings = len(listings)
    automatic_count = len([l for l in listings if l.transmission_raw == "Automatic"])
    manual_count = total_listings - automatic_count
    
    # Price statistics
    prices = [l.price_usd for l in listings if l.price_usd]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    # Deal delta statistics
    deltas = [l.deal_delta for l in listings if l.deal_delta]
    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    
    # Best deals
    best_deals = sorted(listings, key=lambda x: -(x.deal_delta or 0))[:5]
    
    return {
        "total_listings": total_listings,
        "automatic_count": automatic_count,
        "manual_count": manual_count,
        "average_price": avg_price,
        "average_deal_delta": avg_delta,
        "best_deals": best_deals
    }
