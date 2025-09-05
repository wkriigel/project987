"""
View Step - Displays processed data in styled tables

This step implements the final display step in the pipeline, showing all processed data
in beautifully formatted Rich tables using the enhanced report system.

PROVIDES: Data visualization and display of pipeline results
DEPENDS: x987.pipeline.steps.transformation:TransformationStep and x987.pipeline.steps.ranking:RankingStep
CONSUMED BY: End users and analysts
CONTRACT: Provides formatted output and reports with Rich library styling
TECH CHOICE: Rich library for terminal formatting
RISK: Low - display changes don't affect data
"""

import time
from pathlib import Path
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .base import BasePipelineStep, StepResult

# Import color styling functions from theme module
from x987.view.theme import (
    price_style_key, 
    miles_style_key, 
    model_style_key, 
    transmission_style_key,
    THEME
)


class ViewStep(BasePipelineStep):
    """View step implementing data display and visualization"""

    def get_step_name(self) -> str:
        return "view"

    def get_description(self) -> str:
        return "Displays processed data in styled tables and reports"

    def get_dependencies(self) -> List[str]:
        return ["transformation", "ranking"]  # Needs transformed data and rankings

    def get_required_config(self) -> List[str]:
        return []  # No specific config required

    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the view step to display all processed data"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        print("🔍 Starting data display and visualization...")
        print(f"📁 Working directory: {Path.cwd()}")
        print(f"⏰ View started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Get the ranking results to display
            ranking_result = previous_results.get('ranking')
            if not ranking_result or not ranking_result.is_success:
                print("❌ No ranking data available for display")
                return {
                    "displayed": False,
                    "error": "No ranking data available",
                    "view_timestamp": datetime.now().isoformat()
                }

            # Get the listings from ranking results - the ranking step returns the data directly
            listings = ranking_result.data.get('ranked_data', [])
            if not listings:
                print("❌ No listings found in ranking data")
                return {
                    "displayed": False,
                    "error": "No listings found in ranking data",
                    "view_timestamp": datetime.now().isoformat()
                }

            print(f"📊 Displaying {len(listings)} ranked listings...")

            # Determine ranked CSV path/name (from ranking result or latest on disk)
            ranked_csv_path = None
            try:
                data_dict = ranking_result.data if isinstance(ranking_result.data, dict) else {}
                fc = data_dict.get('files_created') or []
                if isinstance(fc, list) and fc:
                    # Prefer the main ranking file
                    for p in fc:
                        if isinstance(p, str) and 'ranking_main_' in p and p.endswith('.csv'):
                            ranked_csv_path = p
                            break
                    if not ranked_csv_path:
                        ranked_csv_path = fc[0]
                if not ranked_csv_path:
                    # Fallback: pick latest ranking_main_*.csv on disk
                    results_dir = Path('x987-data/results')
                    if results_dir.exists():
                        files = sorted(results_dir.glob('ranking_main_*.csv'))
                        if files:
                            ranked_csv_path = str(files[-1])
            except Exception:
                ranked_csv_path = None

            # Generate and display the enhanced report
            self._generate_enhanced_report(listings, ranked_csv_path)

            # Generate view summary
            view_summary = self._generate_view_summary(listings)

            print("✅ Data display completed successfully!")
            print(f"📊 Displayed data for {len(listings)} listings")

            return view_summary

        except Exception as e:
            print(f"❌ View step failed: {e}")
            return {
                "displayed": False,
                "error": str(e),
                "view_timestamp": datetime.now().isoformat()
            }
        finally:
            builtins.print = _orig_print

    def _generate_enhanced_report(self, listings: List[Dict[str, Any]], ranked_csv_path: Optional[str] = None) -> None:
        """Generate and display the enhanced report with professional styling"""
        try:
            console = Console()

            if not listings:
                console.print("[red]No listings available for report generation[/red]")
                return

            # Split listings into displayable (known year) and unknown-year (skipped)
            def _year_known(l: Dict[str, Any]) -> bool:
                y = str(l.get('year') or '').strip()
                return y.isdigit()

            display_listings = [l for l in listings if _year_known(l)]
            unknown_listings = [l for l in listings if not _year_known(l)]
            unknown_urls: List[str] = []
            for l in unknown_listings:
                u = l.get('listing_url') or l.get('source_url')
                if u:
                    unknown_urls.append(str(u))

            # Display detailed table
            listings_table = self._create_listings_table(display_listings)
            console.print(listings_table)

            # Add concise summary after table (items count + clickable config links)
            try:
                summary_panel = self._create_post_table_summary(len(display_listings), unknown_urls, ranked_csv_path)
                if summary_panel:
                    console.print("")
                    console.print(summary_panel)
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Error generating enhanced report: {e}")
            raise

    def _create_post_table_summary(self, displayed_count: int, unknown_urls: List[str], ranked_csv_path: Optional[str]) -> Panel:
        """Create a compact summary showing item count, unknown-year links, and config links."""
        count = int(displayed_count or 0)

        # Resolve config search URLs (try config manager)
        urls: List[str] = []
        try:
            from x987.config import get_config
            cfg = get_config()
            try:
                urls = list(cfg.get_search_urls() or [])
            except Exception:
                data = getattr(cfg, 'config', {}) or {}
                urls = list((data.get('search', {}) or {}).get('urls', []) or [])
        except Exception:
            urls = []

        # Build table content
        table = Table(show_header=False, box=box.SIMPLE, pad_edge=False, expand=True)
        table.add_column("Summary", no_wrap=False)
        table.add_row(f"Items displayed: [bold]{count}[/bold]")

        # Source CSV filename
        try:
            if ranked_csv_path:
                csv_name = Path(ranked_csv_path).name
                table.add_row(f"Source CSV: [bold]{csv_name}[/bold]")
        except Exception:
            pass

        # Unknown-year links (hidden from table)
        if unknown_urls:
            line = Text()
            for i, u in enumerate(unknown_urls):
                label = (urlparse(u).netloc or u).lower()
                if label.startswith('www.'):
                    label = label[4:]
                try:
                    line.append(label, style=f"link {u}")
                except Exception:
                    line.append(label)
                if i < len(unknown_urls) - 1:
                    line.append("  •  ")
            table.add_row(Text("Unknown year: ") + line)

        if urls:
            # Convert URLs to clickable short host labels
            def _host_label(u: str) -> str:
                host = urlparse(u).netloc.lower() if u else ''
                host = host[4:] if host.startswith('www.') else host
                parts = host.split('.')
                if len(parts) >= 2:
                    host = '.'.join(parts[-2:])
                return host or 'source'

            line = Text()
            for i, u in enumerate(urls):
                label = _host_label(u)
                try:
                    line.append(label, style=f"link {u}")
                except Exception:
                    line.append(label)
                if i < len(urls) - 1:
                    line.append("  •  ")
            table.add_row(Text("Config links: ") + line)

        return Panel(table, title="Summary", style="blue")

    def _create_summary_panel(self, listings: List[Dict[str, Any]]) -> Panel:
        """Create enhanced summary statistics panel"""

        if not listings:
            return Panel("No listings available", title="Summary Statistics", style="red")

        total_listings = len(listings)

        # Helper to safely coerce to int
        def _to_int(val):
            try:
                if val is None:
                    return None
                if isinstance(val, (int, float)):
                    return int(val)
                s = str(val)
                digits = ''.join(ch for ch in s if ch.isdigit() or ch == '-')
                return int(digits) if digits not in ('', '-') else None
            except Exception:
                return None

        # Count transmissions - extract from raw_text since it's not a separate field
        auto_count = 0
        manual_count = 0
        for listing in listings:
            raw_text = listing.get('raw_text', '').lower()
            if 'automatic' in raw_text or 'auto' in raw_text or 'pdk' in raw_text:
                auto_count += 1
            elif 'manual' in raw_text:
                manual_count += 1

        # Calculate averages safely using the correct field names
        valid_prices = []
        for l in listings:
            v = _to_int(l.get('asking_price_usd'))
            if v is not None:
                valid_prices.append(v)
        # MSRP stats (Options MSRP Total)
        msrp_values = []
        for l in listings:
            mv = _to_int(l.get('total_options_msrp'))
            if mv is not None:
                msrp_values.append(mv)
        avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
        avg_msrp = sum(msrp_values) / len(msrp_values) if msrp_values else 0

        # Highest/lowest MSRP rows
        def _mt(listing: Dict[str, Any]) -> str:
            best_model = (listing.get('model') or '').strip()
            best_trim = (listing.get('trim') or '').strip()
            combined = f"{best_model} {best_trim}".strip()
            return self._normalize_model_trim_text(combined)

        best_msrp = max(listings, key=lambda x: _to_int(x.get('total_options_msrp')) or 0) if listings else None
        worst_msrp = min(listings, key=lambda x: _to_int(x.get('total_options_msrp')) or 0) if listings else None

        if best_msrp:
            bm = _to_int(best_msrp.get('total_options_msrp'))
            best_msrp_text = f"${bm:,}" if bm is not None else "—"
            best_msrp_model = f"{best_msrp.get('year', 'N/A')} {_mt(best_msrp) or 'N/A'}"
        else:
            best_msrp_text = "—"
            best_msrp_model = "N/A"

        if worst_msrp:
            wm = _to_int(worst_msrp.get('total_options_msrp'))
            worst_msrp_text = f"${wm:,}" if wm is not None else "—"
            worst_msrp_model = f"{worst_msrp.get('year', 'N/A')} {_mt(worst_msrp) or 'N/A'}"
        else:
            worst_msrp_text = "—"
            worst_msrp_model = "N/A"

        summary_text = f"""
        [bold]Total Listings:[/bold] {total_listings}

        [bold]Transmission:[/bold] {auto_count} Automatic | {manual_count} Manual

        [bold]Average Price:[/bold] ${avg_price:,.0f}
        [bold]Average Options MSRP:[/bold] ${avg_msrp:,.0f}

        [bold]Highest MSRP:[/bold] {best_msrp_model} - {best_msrp_text}
        [bold]Lowest MSRP:[/bold] {worst_msrp_model} - {worst_msrp_text}
        """

        return Panel(summary_text, title="Summary Statistics", style="blue")

    def _normalize_model_trim_text(self, src: str) -> str:
        """Normalize model/trim text for display: hide 'Base' and uppercase single-letter 'S'."""
        s = (src or "").strip()
        if not s:
            return ""
        # Remove the word 'base'
        s = re.sub(r"\bbase\b", "", s, flags=re.I)
        # Ensure proper model casing
        s = re.sub(r"\bcayman\b", "Cayman", s, flags=re.I)
        s = re.sub(r"\bboxster\b", "Boxster", s, flags=re.I)
        # Shorten specific trims
        s = re.sub(r"\bblack\s+edition\b", "BE", s, flags=re.I)
        # Ensure single-letter S trim is uppercase after model name
        s = re.sub(r"\b(Cayman|Boxster)\s+s\b", r"\1 S", s, flags=re.I)
        # Collapse spaces
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _create_listings_table(self, listings: List[Dict[str, Any]]) -> Table:
        """Create enhanced listings table with professional styling and dynamic coloring"""

        try:
            table = Table(
                show_header=True,
                header_style=f"bold {THEME.get('orange_cayman', '#FF6A1A')}",
                expand=True,
                show_lines=False,
                show_edge=False,
                box=box.SIMPLE,
                border_style="black",
                padding=(0, 1),
                row_styles=["", f"on {THEME.get('stripe_1', '#11151B')}"]
            )

            # Add columns (separate fields; no merged columns)
            table.add_column("Year", no_wrap=True, min_width=4)
            table.add_column("Model", no_wrap=True, min_width=8)
            table.add_column("Trim", no_wrap=True, min_width=6)
            table.add_column("Price", justify="right", no_wrap=True, min_width=6)
            table.add_column("Miles", justify="right", no_wrap=True, min_width=5)
            table.add_column("MSRP", justify="right", no_wrap=True, min_width=5)
            table.add_column("Top Options", no_wrap=False, overflow="fold", min_width=22)
            table.add_column("Exterior", no_wrap=True, min_width=8)
            table.add_column("Interior", no_wrap=True, min_width=8)
            table.add_column("Source", no_wrap=False, min_width=10)

            # Add rows
            for i, listing in enumerate(listings):
                try:
                    # Determine if this is a manual transmission for styling
                    raw_text = listing.get('raw_text', '').lower()
                    is_manual = 'manual' in raw_text

                    # Numeric coercion helpers
                    def _to_int_local(v):
                        try:
                            if v is None:
                                return None
                            if isinstance(v, (int, float)):
                                return int(v)
                            s = str(v)
                            digits = ''.join(ch for ch in s if ch.isdigit() or ch == '-')
                            return int(digits) if digits not in ('', '-') else None
                        except Exception:
                            return None

                    # Deal delta
                    deal_delta = _to_int_local(listing.get('deal_delta_usd'))
                    if deal_delta is not None:
                        # With Deal Δ = fair - asking: positive is undervalued
                        if deal_delta > 0:
                            deal_text = f"+${deal_delta:,}"
                            deal_style = "green"
                        elif deal_delta < 0:
                            deal_text = f"-${abs(deal_delta):,}"
                            deal_style = "red"
                        else:
                            deal_text = "$0"
                            deal_style = "white"
                        if is_manual:
                            deal_style = "dim " + deal_style
                    else:
                        deal_text = "N/A"
                        deal_style = "dim"

                    # Price (compact $k) with background highlight only if miles < 90,000
                    price = _to_int_local(listing.get('asking_price_usd'))
                    miles_for_price = _to_int_local(listing.get('mileage'))
                    price_bg = False
                    if price is not None and price > 0:
                        k = (price + 999) // 1000
                        price_text = f"${k}k"
                        price_color_key = price_style_key(price)
                        price_hex = THEME.get(price_color_key, "#C9D1D9")
                        if price_color_key in ("teal_1", "teal_2") and (miles_for_price is not None and miles_for_price < 90_000):
                            bg_hex = THEME.get("gray_700", "#3A4654")
                            price_style = f"{price_hex} on {bg_hex}"
                            price_bg = True
                        else:
                            price_style = price_hex
                        if is_manual:
                            price_style = f"dim {price_style}"
                    else:
                        price_text = ""
                        price_style = "dim"

                    # MSRP total for options (compact $k); highlight background if >$9,999 or if options include PASM+PSE+LSD
                    msrp_total = _to_int_local(listing.get('total_options_msrp'))
                    msrp_bg = False
                    # Detect PASM+PSE+LSD presence from options_list/raw text
                    opts_list = listing.get('options_list')
                    def _has(token: str, text: str) -> bool:
                        import re
                        return re.search(rf"\b{re.escape(token)}\b", text, flags=re.I) is not None
                    opt_text_all = ''
                    if isinstance(opts_list, list):
                        try:
                            opt_text_all = ' '.join([str(x) for x in opts_list])
                        except Exception:
                            opt_text_all = ' '.join([str(x) for x in opts_list if x])
                    elif isinstance(opts_list, str):
                        opt_text_all = opts_list
                    else:
                        opt_text_all = ''
                    # Check presence across common variants
                    has_pasm = _has('pasm', opt_text_all) or 'adaptive suspension' in opt_text_all.lower()
                    has_pse = _has('pse', opt_text_all) or 'sport exhaust' in opt_text_all.lower() or _has('xlf', opt_text_all)
                    has_lsd = _has('lsd', opt_text_all) or 'limited slip' in opt_text_all.lower() or _has('220', opt_text_all)
                    combo_all = has_pasm and has_pse and has_lsd

                    if msrp_total is not None and msrp_total > 0:
                        msrp_k = (msrp_total + 999) // 1000
                        msrp_text = f"${msrp_k}k"
                        msrp_hex = THEME.get('msrp_green', '#0F7B47')
                        # Apply background highlight when threshold or combo condition is met
                        if msrp_total > 3_999 or combo_all:
                            fg_hex = THEME.get('text', '#C9D1D9')
                            bg_hex = THEME.get('msrp_bg', THEME.get('gray_700', '#3A4654'))
                            msrp_style = f"{fg_hex} on {bg_hex}"
                            msrp_bg = True
                        else:
                            msrp_style = msrp_hex
                        if is_manual:
                            msrp_style = f"dim {msrp_style}"
                    else:
                        msrp_text = ""
                        msrp_style = "dim"

                    # Miles (compact k) – highlight background only if mileage < 70,000
                    mileage_val = _to_int_local(listing.get('mileage'))
                    miles_bg = False
                    if mileage_val is not None and mileage_val >= 0:
                        miles_k = (mileage_val + 999) // 1000
                        mileage_text = f"{miles_k}k"
                        miles_color_key = miles_style_key(int(mileage_val))
                        miles_hex = THEME.get(miles_color_key, "#C9D1D9")
                        if mileage_val < 70_000:
                            bg_hex = THEME.get("gray_700", "#3A4654")
                            miles_style = f"{miles_hex} on {bg_hex}"
                            miles_bg = True
                        else:
                            miles_style = miles_hex
                        if is_manual:
                            miles_style = f"dim {miles_style}"
                    else:
                        mileage_text = ""
                        miles_style = "dim"

                    # Year, Model, Trim in separate columns
                    year = listing.get('year', '')
                    model_text = (listing.get('model') or '').strip()
                    trim_text = (listing.get('trim') or '').strip()
                    # Simple style dimming for manual if needed
                    if is_manual:
                        model_text = f"[dim]{model_text}[/dim]" if model_text else ""
                        trim_text = f"[dim]{trim_text}[/dim]" if trim_text else ""
                    year_str = str(year or '').strip()

                    # Color swatches (ext/int)
                    def _norm(s: str) -> str:
                        import re
                        return re.sub(r"[^a-z0-9]+", " ", (s or '').lower()).strip()
                    BUILTIN_PAINTS = {
                        "arctic silver metallic": "#C9CCCE",
                        "meteor gray": "#6E7479",
                        "gray": "#8F969C",
                        "black": "#0C0E10",
                        "white": "#E9EAEA",
                        "guards red": "#D0191A",
                        "red": "#B0201B",
                        "aqua blue metallic": "#2E6C8E",
                        "midnight blue metallic": "#1A2C4E",
                        "silver": "#C9CCCE",
                        "gt silver metallic": "#BFC4C9",
                    }
                    def _paint_hex(name: str) -> str:
                        key = _norm(name)
                        return BUILTIN_PAINTS.get(key, "#6E7479")
                    def _interior_hex(name: str) -> str:
                        s = _norm(name)
                        import re
                        if re.search(r"black|anthracite|graphite|charcoal", s): return "#0E1114"
                        if re.search(r"sand\s*beige|beige", s): return "#CBB68B"
                        if re.search(r"tan|camel|savanna", s): return "#B48A60"
                        if re.search(r"cocoa|espresso|chocolate|brown", s): return "#6B4A2B"
                        if re.search(r"stone|platinum\s*gray|platinum\s*grey|gray|grey", s): return "#A7ADB5"
                        if re.search(r"red|carmine|bordeaux", s): return "#7E1C1C"
                        if re.search(r"blue|navy", s): return "#2F3A56"
                        if re.search(r"white|ivory|alabaster", s): return "#E8E8E8"
                        return "#777777"
                    def _swatch(style_hex: str) -> Text:
                        t = Text()
                        t.append(" " * 5, style=f"on {style_hex}")
                        return t
                    # Use new schema fields with legacy fallback
                    ext_color = listing.get('exterior') or ""
                    int_color = listing.get('interior') or ""
                    exterior_cell = _swatch(_paint_hex(ext_color))
                    interior_cell = _swatch(_interior_hex(int_color))

                    # Options: cleaned, full list
                    raw_text_full = listing.get('raw_text', '')
                    raw_text_low = str(raw_text_full).lower()
                    def _cap_phrase(s: str) -> str:
                        import re
                        t = re.sub(r"\s+", " ", (s or "").strip()).title()
                        fixes = [(r"\bPcm/Nav\b","PCM/Nav"),(r"\bPcm\b","PCM"),(r"\bPdk\b","PDK"),
                                 (r"\bLsd\b","LSD"),(r"\bBose\b","BOSE"),(r"\bPccb\b","PCCB"),(r"\bPasm\b","PASM")]
                        for pat, rep in fixes:
                            t = re.sub(pat, rep, t, flags=re.I)
                        return t
                    def _shorten_option_name(s: str) -> str:
                        """Return a compact, single-word/code label for an option."""
                        import re
                        src = (s or '').strip()
                        low = src.lower()
                        # Known compact mappings
                        # Audio/Tech
                        if 'bose' in low:
                            return 'BOSE'
                        if 'pcm' in low and ('nav' in low or 'navigation' in low or 'w/' in low):
                            return 'Nav'
                        # Performance
                        if 'sport chrono' in low or re.search(r'\bchrono\b', low):
                            return 'Chrono'
                        if 'pasm' in low or 'active suspension' in low or 'adaptive suspension' in low:
                            return 'PASM'
                        if 'sport exhaust' in low or 'pse' in low:
                            return 'Exhaust'
                        if 'limited slip' in low or re.search(r'\blsd\b', low):
                            return 'LSD'
                        if re.search(r'\bpdk\b', low):
                            return 'PDK'
                        # Seats
                        if 'heated seat' in low or 'heated seats' in low:
                            return 'Heated'
                        if 'ventilated' in low or 'cooled seat' in low or 'cooled seats' in low:
                            return 'Cooled'
                        if 'sport seat' in low or 'adaptive sport' in low:
                            return 'Seats'
                        # Lighting
                        if 'bi-xenon' in low or 'xenon' in low or 'litronic' in low:
                            return 'Xenon'
                        # Driver assist
                        if 'park assist' in low or 'parking assist' in low:
                            return 'Park'
                        # Wheels (prefer reading size from full raw text, else from label)
                        if 'wheel' in low or 'wheels' in low:
                            if re.search(r"\b19\s*(?:inch|\"|in)\b", raw_text_low) or re.search(r'\b19\b', low) or '19"' in low:
                                return '19"'
                            if re.search(r"\b18\s*(?:inch|\"|in)\b", raw_text_low) or re.search(r'\b18\b', low) or '18"' in low:
                                return '18"'
                            return 'Wheels'
                        # Default: take a meaningful single token
                        # Try last word if it looks like a code, else first significant word
                        tokens = [t for t in re.split(r"[^a-z0-9]+", low) if t]
                        if tokens:
                            # Prefer short tokens/codes
                            tokens_sorted = sorted(tokens, key=len)
                            choice = tokens_sorted[0]
                            return _cap_phrase(choice)
                        return _cap_phrase(src)
                    options_text = ""
                    opts_list = listing.get('options_list')
                    if isinstance(opts_list, list) and opts_list:
                        options_text = ", ".join(_shorten_option_name(p) for p in opts_list)
                    elif isinstance(opts_list, str) and opts_list.strip():
                        parts = [p.strip() for p in opts_list.split(',') if p.strip()]
                        options_text = ", ".join(_shorten_option_name(p) for p in parts)
                    else:
                        if 'Features:' in raw_text_full:
                            try:
                                f_start = raw_text_full.find('Features:') + len('Features:')
                                f_text = raw_text_full[f_start:].strip()
                                if f_text:
                                    features = [f.strip('- ').strip() for f in f_text.split('\n') if f.strip().startswith('-')]
                                    if features:
                                        options_text = ", ".join(_shorten_option_name(p) for p in features)
                            except Exception:
                                options_text = ""
                    if is_manual and options_text:
                        options_text = "Manual, " + options_text

                    # Source: clickable hyperlink with short host label (e.g., cars.com, carvana.com)
                    url = listing.get('listing_url') or listing.get('source_url') or ''
                    def _host_label(u: str) -> str:
                        try:
                            host = urlparse(u).netloc or ''
                            host = host.lower()
                            if host.startswith('www.'):
                                host = host[4:]
                            # Normalize some known hosts
                            known = [
                                'cars.com', 'carvana.com', 'truecar.com', 'ebay.com',
                                'autotrader.com', 'autotempest.com', 'cargurus.com', 'carmax.com'
                            ]
                            for k in known:
                                if host.endswith(k):
                                    return k
                            # Fallback: last two labels when possible
                            parts = host.split('.')
                            if len(parts) >= 2:
                                return '.'.join(parts[-2:])
                            return host or 'source'
                        except Exception:
                            return 'source'
                    if url:
                        label = _host_label(url)
                        try:
                            source_text = Text(label, style=f"link {url}")
                        except Exception:
                            source_text = label
                    else:
                        source_text = ""

                    # Add row (Deal Δ omitted in display)
                    table.add_row(
                        str(year or ''),
                        model_text,
                        trim_text,
                        Text(price_text, style=price_style),
                        Text(mileage_text, style=miles_style),
                        Text(msrp_text, style=msrp_style),
                        options_text,
                        exterior_cell,
                        interior_cell,
                        source_text
                    )

                except Exception as e:
                    print(f"⚠️  Error processing listing {i+1}: {e}")
                    # Add error row as fallback
                    table.add_row(
                        "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR", "ERROR"
                    )

            return table

        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            raise

    def _generate_view_summary(self, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of what was displayed"""

        # Count listings
        total_listings = len(listings)

        # Extract key metrics from listings using correct field names (with coercion)
        def _to_int(v):
            try:
                if v is None:
                    return None
                if isinstance(v, (int, float)):
                    return int(v)
                s = str(v)
                digits = ''.join(ch for ch in s if ch.isdigit() or ch == '-')
                return int(digits) if digits not in ('', '-') else None
            except Exception:
                return None

        price_values = []
        for l in listings:
            pv = _to_int(l.get('asking_price_usd'))
            if pv is not None:
                price_values.append(pv)
        total_value = sum(price_values) if price_values else 0
        avg_price = total_value / len(price_values) if price_values else 0

        # Count options and other metrics
        total_options = 0
        for listing in listings:
            raw_text = listing.get('raw_text', '')
            if 'Features:' in raw_text:
                features_start = raw_text.find('Features:') + len('Features:')
                features_text = raw_text[features_start:].strip()
                if features_text:
                    features = [f.strip('- ').strip() for f in features_text.split('\n') if f.strip().startswith('-')]
                    total_options += len(features)

        summary = {
            "displayed": True,
            "total_listings": total_listings,
            "total_value": total_value,
            "avg_price": avg_price,
            "total_options": total_options,
            "view_timestamp": datetime.now().isoformat()
        }

        return summary


# Export the view step instance
VIEW_STEP = ViewStep()
