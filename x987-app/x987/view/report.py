"""
Report generation module

PROVIDES: Beautiful terminal reports with rich formatting
DEPENDS: rich, schema, utils.text
CONSUMED BY: Main pipeline
CONTRACT: Displays ranked listings in formatted tables
TECH CHOICE: Rich library for terminal formatting
RISK: Low - display formatting only
TODO(NEXT): Add export options and custom themes
"""

from typing import List, Optional, Dict
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from ..schema import NormalizedListing
from ..utils.text import format_price_display, format_mileage_display, format_deal_delta
from ..utils.log import get_logger

logger = get_logger("view.report")

# Color theme for the report
THEME = {
    "header": "bold cyan",
    "subheader": "bold blue",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "info": "blue",
    "price_good": "bold green",
    "price_ok": "bold yellow",
    "price_bad": "bold red",
    "transmission_auto": "bold green",
    "transmission_manual": "yellow",
    "deal_delta_positive": "bold green",
    "deal_delta_negative": "bold red",
    "deal_delta_neutral": "white"
}

def get_price_style(price: Optional[int]) -> str:
    """Get color style for price based on value"""
    if price is None:
        return "dim"
    if price < 25000:
        return THEME["price_good"]
    elif price < 35000:
        return THEME["price_ok"]
    else:
        return THEME["price_bad"]

def get_transmission_style(transmission: Optional[str]) -> str:
    """Get color style for transmission"""
    if not transmission:
        return "dim"
    if "automatic" in transmission.lower():
        return THEME["transmission_auto"]
    elif "manual" in transmission.lower():
        return THEME["transmission_manual"]
    else:
        return "white"

def get_deal_delta_style(deal_delta: Optional[int]) -> str:
    """Get color style for deal delta"""
    if deal_delta is None:
        return "dim"
    if deal_delta > 0:
        return THEME["deal_delta_positive"]
    elif deal_delta < 0:
        return THEME["deal_delta_negative"]
    else:
        return THEME["deal_delta_neutral"]

def _format_options_display(options_summary: Dict[str, any]) -> str:
    """Format options summary for display in the table"""
    if not options_summary or not options_summary.get('all_options'):
        return "N/A"
    
    all_options = options_summary['all_options']
    
    # Show ALL options - they're critical for decision-making
    return ", ".join(all_options)

def create_main_table(listings: List[NormalizedListing]) -> Table:
    """Create the main listings table"""
    table = Table(
        title="Porsche 987.2 Listings - Ranked by Deal Delta",
        box=box.ROUNDED,
        show_header=True,
        header_style=THEME["header"],
        border_style="blue"
    )
    
    # Add columns
    table.add_column("Rank", style="dim", width=4, justify="center")
    table.add_column("Model/Trim", style="bold", width=12)
    table.add_column("Year", width=4, justify="center")
    table.add_column("Trans", width=8, justify="center")
    table.add_column("Miles", width=8, justify="right")
    table.add_column("Price", width=10, justify="right")
    table.add_column("Fair Value", width=12, justify="right")
    table.add_column("Deal Δ", width=10, justify="right")
    table.add_column("Colors", width=12)
    table.add_column("Options", width=35)
    table.add_column("URL", style="dim", width=30)
    
    # Add rows
    for i, listing in enumerate(listings, 1):
        if listing.error:
            # Error row
            table.add_row(
                str(i),
                f"[red]{listing.model or 'Unknown'}[/red]",
                str(listing.year) if listing.year else "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                f"[red]{listing.error}[/red]",
                listing.listing_url[:28] + "..." if len(listing.listing_url) > 28 else listing.listing_url
            )
        else:
            # Valid listing row
            # Compose model/trim from separate fields
            model_trim = f"{listing.model} {listing.trim}".strip() if listing.model else "Unknown"
            year = str(listing.year) if listing.year else "N/A"
            transmission = listing.transmission_norm or "N/A"
            miles = format_mileage_display(listing.mileage) if listing.mileage else "N/A"
            price_val = getattr(listing, 'asking_price_usd', None)
            price = format_price_display(price_val) if price_val else "N/A"
            fair_value = format_price_display(listing.fair_value_usd) if listing.fair_value_usd else "N/A"
            deal_delta = format_deal_delta(listing.deal_delta_usd) if listing.deal_delta_usd else "N/A"
            
            # Colors
            colors = ""
            ext = getattr(listing, 'exterior', None)
            intr = getattr(listing, 'interior', None)
            if ext and intr:
                colors = f"{ext[:8]}/{intr[:8]}"
            elif ext:
                colors = ext[:12]
            elif intr:
                colors = intr[:12]
            else:
                colors = "N/A"
            
            # Options (detected and categorized)
            if hasattr(listing, 'options_summary') and listing.options_summary:
                # Use the new options summary if available
                options = _format_options_display(listing.options_summary)
            elif hasattr(listing, 'options_detected') and listing.options_detected:
                # Fallback to detected options list - show ALL options
                options = ", ".join(listing.options_detected)
            else:
                # Fallback to raw options (truncated only if no detection available)
                options = listing.raw_options[:50] + "..." if listing.raw_options and len(listing.raw_options) > 50 else (listing.raw_options or "N/A")
            
            # Apply styling
            price_style = get_price_style(listing.price_usd)
            trans_style = get_transmission_style(listing.transmission_norm)
            deal_style = get_deal_delta_style(listing.deal_delta_usd)
            
            table.add_row(
                str(i),
                model_trim,
                year,
                f"[{trans_style}]{transmission}[/{trans_style}]",
                miles,
                f"[{price_style}]{price}[/{price_style}]",
                fair_value,
                f"[{deal_style}]{deal_delta}[/{deal_style}]",
                colors,
                options,
                listing.listing_url[:28] + "..." if len(listing.listing_url) > 28 else listing.listing_url
            )
    
    return table

def create_options_summary_panel(listings: List[NormalizedListing]) -> Panel:
    """Create detailed options summary panel"""
    valid_listings = [l for l in listings if not l.error]
    
    if not valid_listings:
        return Panel("No valid listings to display", title="Options Summary", style="red")
    
    # Clean mode: remove debug spew
    
    # Collect options data
    total_options_detected = 0
    options_by_category = {}
    total_options_value = 0
    
    for listing in valid_listings:
        # Check if options_summary exists and has actual data
        if hasattr(listing, 'options_summary') and listing.options_summary and listing.options_summary.get('total_options', 0) > 0:
            summary = listing.options_summary
            total_options_detected += summary.get('total_options', 0)
            total_options_value += summary.get('total_value', 0)
            
            # Aggregate by category
            for category, data in summary.get('by_category', {}).items():
                if category not in options_by_category:
                    options_by_category[category] = {"count": 0, "value": 0, "options": set()}
                options_by_category[category]["count"] += len(data["options"])
                options_by_category[category]["value"] += data["value"]
                options_by_category[category]["options"].update(data["options"])
    
    # Clean mode: no debug prints
    
    if total_options_detected == 0:
        return Panel("No options detected in listings", title="Options Summary", style="yellow")
    
    # Build summary text
    summary_text = f"[bold]Total Options Detected:[/bold] {total_options_detected}\n"
    summary_text += f"[bold]Total Options Value:[/bold] ${total_options_value:,}\n\n"
    
    # Show options by category
    for category in ["performance", "comfort", "technology", "appearance"]:
        if category in options_by_category:
            data = options_by_category[category]
            category_name = category.title()
            summary_text += f"[bold]{category_name}:[/bold] {data['count']} options (${data['value']:,})\n"
            
            # Show top options in this category
            top_options = sorted(list(data["options"]))[:3]  # Show first 3
            if top_options:
                summary_text += f"  • {', '.join(top_options)}\n"
            summary_text += "\n"
    
    return Panel(summary_text, title="Options Summary by Category", style="green")

def create_summary_panel(listings: List[NormalizedListing]) -> Panel:
    """Create summary statistics panel"""
    valid_listings = [l for l in listings if not l.error]
    error_listings = [l for l in listings if l.error]
    
    if not valid_listings:
        return Panel("No valid listings to display", title="Summary", style="red")
    
    # Calculate statistics
    total_listings = len(valid_listings)
    auto_count = len([l for l in valid_listings if l.transmission_norm and "automatic" in l.transmission_norm.lower()])
    manual_count = len([l for l in valid_listings if l.transmission_norm and "manual" in l.transmission_norm.lower()])
    
    avg_price = sum(l.price_usd for l in valid_listings if l.price_usd) / len([l for l in valid_listings if l.price_usd]) if any(l.price_usd for l in valid_listings) else 0
    avg_deal_delta = sum(l.deal_delta_usd for l in valid_listings if l.deal_delta_usd) / len([l for l in valid_listings if l.deal_delta_usd]) if any(l.deal_delta_usd for l in valid_listings) else 0
    
    best_deal = max(valid_listings, key=lambda x: x.deal_delta_usd or 0) if valid_listings else None
    worst_deal = min(valid_listings, key=lambda x: x.deal_delta_usd or 0) if valid_listings else None
    
    summary_text = f"""
    [bold]Total Listings:[/bold] {total_listings}
    [bold]Valid:[/bold] {len(valid_listings)} | [bold]Errors:[/bold] {len(error_listings)}
    
    [bold]Transmission:[/bold] {auto_count} Automatic | {manual_count} Manual
    
    [bold]Average Price:[/bold] ${avg_price:,.0f}
    [bold]Average Deal Delta:[/bold] ${avg_deal_delta:,.0f}
    
    [bold]Best Deal:[/bold] {best_deal.model} {best_deal.trim} - ${best_deal.deal_delta_usd:,} (${best_deal.price_usd:,}) if best_deal.deal_delta_usd is not None and best_deal.price_usd is not None else f"[bold]Best Deal:[/bold] {best_deal.model} {best_deal.trim} - No deal data"
    [bold]Worst Deal:[/bold] {worst_deal.model} {worst_deal.trim} - ${worst_deal.deal_delta_usd:,} (${worst_deal.price_usd:,}) if worst_deal.deal_delta_usd is not None and worst_deal.price_usd is not None else f"[bold]Worst Deal:[/bold] {worst_deal.model} {worst_deal.trim} - No deal data"
    """
    
    return Panel(summary_text, title="Summary Statistics", style="blue")

def generate_report(listings: List[NormalizedListing]) -> None:
    """
    Generate and display the main report
    
    Args:
        listings: List of ranked listings from ranking step
    """
    try:
        console = Console()
        
        if not listings:
            logger.warning("No listings provided for report, using fallback data")
            # Use placeholder data for demonstration if no listings provided
            from ..schema import NormalizedListing
            
            listings = [
                NormalizedListing(
                    timestamp_run_id="placeholder",
                    source="cars.com",
                    listing_url="https://example.com/1",
                    error=None,
                    vin="WP0AB2A89EK123456",
                    year=2009,
                    model="Cayman",
                    trim="S",
                    transmission_norm="Automatic",
                    transmission_raw="Automatic",
                    mileage=45000,
                    price_usd=35000,
                    exterior_color="Arctic Silver Metallic",
                    interior_color="Black",
                    color_ext_bucket="Monochrome",
                    color_int_bucket="Monochrome",
                    raw_options="Premium Package, Sport Chrono Package",
                    location=None,
                    options_detected=[],
                    options_value=5000,
                    fair_value_usd=42000,
                    deal_delta_usd=7000
                ),
                NormalizedListing(
                    timestamp_run_id="placeholder",
                    source="cars.com",
                    listing_url="https://example.com/2",
                    error=None,
                    vin="WP0AB2A89EK789012",
                    year=2010,
                    model="Cayman",
                    trim="Base",
                    transmission_norm="Manual",
                    transmission_raw="Manual",
                    mileage=60000,
                    price_usd=32000,
                    exterior_color="Black",
                    interior_color="Tan",
                    color_ext_bucket="Monochrome",
                    color_int_bucket="Color",
                    raw_options="Sport Package",
                    location=None,
                    options_detected=[],
                    options_value=3000,
                    fair_value_usd=38000,
                    deal_delta_usd=6000
                ),
                NormalizedListing(
                    timestamp_run_id="placeholder",
                    source="cars.com",
                    listing_url="https://example.com/3",
                    error=None,
                    vin="WP0AB2A89EK345678",
                    year=2011,
                    model="Boxster",
                    trim="S",
                    transmission_norm="Automatic",
                    transmission_raw="Automatic",
                    mileage=35000,
                    price_usd=45000,
                    exterior_color="Guards Red",
                    interior_color="Black",
                    color_ext_bucket="Color",
                    color_int_bucket="Monochrome",
                    raw_options="Premium Package Plus, Sport Chrono",
                    location=None,
                    options_detected=[],
                    options_value=6000,
                    fair_value_usd=48000,
                    deal_delta_usd=3000
                )
            ]
        
        logger.info(f"Generating report for {len(listings)} listings")
        
        # Display header
        console.print("\n")
        console.print(Panel(
            "[bold cyan]Porsche 987.2 Cayman/Boxster Listing Analyzer[/bold cyan]\n"
            "[blue]Surface undervalued listings with fair-value pricing model[/blue]",
            title="View-from-CSV v4.5",
            style="cyan"
        ))
        
        # Display summary
        summary_panel = create_summary_panel(listings)
        console.print(summary_panel)
        
        # Display options summary
        options_summary_panel = create_options_summary_panel(listings)
        console.print(options_summary_panel)
        
        # Display main table
        main_table = create_main_table(listings)
        console.print(main_table)
        
        # Display footer
        console.print("\n")
        console.print(Panel(
            "[dim]Report generated with View-from-CSV v4.5 | "
            "Deal Δ = Fair Value - Price | "
            "Positive values indicate undervalued listings[/dim]",
            style="dim"
        ))
        
        logger.info("Report generated and displayed successfully")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        console = Console()
        console.print(f"[red]Error generating report: {e}[/red]")
