# View-from-CSV Project Requirements Document v4

## Project Overview

**View-from-CSV** is a data processing and visualization application that transforms scraped CSV data of 987.2 Cayman/Boxster listings into a ranked, scannable table with a fair-value pricing model. The application provides quick visual scanning of car listings ranked by deal value (fair value minus asking price).

**Version 4 Focus**: Streamlined architecture with universal scraper, multi-source support (Cars.com, TrueCar, Carvana), and optimized iteration efficiency.

## Core Objectives

1. **Input Processing**: Handle multiple sources via AutoTempest collector + universal VDP scraper
2. **Data Normalization**: Apply consistent formatting, abbreviations, and categorization rules
3. **Fair Value Calculation**: Implement a dollar-based pricing model with configurable parameters
4. **Ranked Display**: Present results in a terminal-style table ranked by deal delta
5. **Quick Scanning**: Enable users to identify the best deals at a glance
6. **Iteration Efficiency**: Lean codebase with fast rebuild cycles and isolated testing

## Functional Requirements

### 1. Data Input & Processing

#### 1.1 Multi-Source Collection
- **Primary Collector**: AutoTempest-based URL collection from multiple sources
- **Supported Sources**: Cars.com, TrueCar, Carvana (expandable)
- **Collection Method**: Headful Playwright for reliability over speed
- **Input Format**: AutoTempest search URLs (configurable)
- **Output**: `{ "source": "<host>", "listing_url": "<url>" }` pairs

#### 1.2 Universnal VDP Scraper
- **Single Engine**: `universal_vdp` processes all vehicle detail pages
- **Site Profiles**: Minimal per-site selectors and wait conditions
- **Shared Patterns**: Common regex/core patterns for consistent extraction
- **Output Schema**: Identical across all sources:
  ```
  source, listing_url, vin, year, model, trim, transmission_raw,
  mileage, price_usd, exterior_color, interior_color, raw_options, location
  ```

#### 1.3 CSV Schema Support
- **Required Fields**: timestamp_run_id, source, listing_url, vin, year, model, trim, transmission_raw, price_usd, mileage, exterior_color, interior_color, raw_options, location
- **Optional Fields**: All fields except timestamp_run_id, source, listing_url are optional
- **Data Types**: Support for string, integer, and list/string fields
- **Error Handling**: Partial failure tolerance with `error` field for failed scrapes

#### 1.4 Data Deduplication
- **Primary Key**: VIN-based deduplication
- **Fallback**: Exact mileage + URL match (optional)
- **Conflict Resolution**: Prefer rows with more complete fields
- **No Fuzzy Merging**: Strict matching only

### 2. Data Normalization

#### 2.1 Transmission Normalization
- **Automatic Category**: PDK, Automatic, Tiptronic → "Automatic"
- **Manual Category**: Manual → "Manual"
- **Display**: Show exactly "Automatic" or "Manual"

#### 2.2 Color Processing
- **Color Buckets**: 
  - Monochrome: white, black, gray, silver (case/variant tolerant)
  - Color: everything else
- **Display**: Keep original color names (e.g., "Arctic Silver Metallic")
- **Format**: "Exterior / Interior" (e.g., "White / Tan")

#### 2.3 Model/Trim Display
- **Format**: "YYYY Model Trim" (e.g., "2010 Cayman S")
- **Base Trim**: Omit "Base" or blank trim values
- **Special Trims**: Support S, R, Black Edition, Boxster Spyder

### 3. Options Detection & Valuation

#### 3.1 Options v2 System
- **Detection Method**: Case-insensitive regex matching with synonyms
- **Catalog Structure**: ID, Display Label, Value ($), Synonyms, Standard-on Suppression
- **Default Options**:
  - LSD: $1,200 (limited-slip, LSD, locking diff)
  - Chrono: $1,000 (Sport Chrono, Chrono Package)
  - Exhaust: $800 (PSE, Sport Exhaust, Switchable exhaust)
  - PASM: $800 (PASM, adaptive suspension)
  - 19" Wheels: $400 (19", 235/35R19, 265/35R19)
  - BOSE: $300 (BOSE)
  - PCM/Nav: $300 (PCM, navigation, nav system)
  - Bi-Xenon: $250 (bi-xenon, Litronic, cornering lights)
  - Heated Seats: $150 (heated seats, seat heating)
  - Cooled Seats: $150 (cooled seats, ventilated seats)
  - Sport Seats: $500 (sport seats, adaptive sport seats)
  - PDK: $0 (stored but not displayed)

#### 3.2 Standard-on Suppression
- **Trim-based Rules**: Don't credit options standard on specific trims
- **Example**: Cayman R gets no credit for LSD or 19" wheels
- **Configurable**: Editable trim list for suppression rules

#### 3.3 Options Display
- **Order**: Descending value order (highest value first)
- **Format**: Comma-separated labels (e.g., "LSD, chrono, exhaust, PASM")
- **No Limit**: Show all detected options by default

### 4. Fair Value Model

#### 4.1 Calculation Formula
```
Fair Value = Base + Trim Premium + Year Step + Mileage Bonus + Color Bonus + Options Total
Deal Δ = Fair Value - Asking Price
```

#### 4.2 Base Values (Configurable)
- **Base Car**: $30,500 (2009 Base, Automatic, 60-79k miles, mono/mono, no options)
- **Year Step**: +$500 per year from 2009
- **Trim Premiums**:
  - Base: $0
  - S: $7,000
  - R: $30,000
  - Black Edition: $1,500
  - Boxster Spyder: $30,000

#### 4.3 Mileage Bands & Bonuses
- <40k: +$3,000
- 40-59k: +$1,500
- 60-79k: +$0 (neutral)
- 80-99k: -$4,000
- 100k-119: -$9,000
- ≥119k: -$15,000
- **Missing Mileage**: Use 60-79k band for processing, show blank in view

#### 4.4 Color Bonuses
- **Interior Color**: +$300
- **Exterior Color**: +$300
- **Monochrome**: +$0

#### 4.5 Options Total
- **Sum**: All detected Options v2 values (after standard-on suppression)
- **Fallback**: If Options v2 disabled, use `top5_count × $600`

### 5. Display & Output

#### 5.1 Column Order (Left to Right)
1. **Deal Δ ($)** - Positive means undervalued
2. **Price** - Rounded up to nearest $1k (e.g., "$29k", "$33k")
3. **Miles** - Rounded up to nearest 1k (e.g., "79k", "36k")
4. **Year/Model/Trim** - "2010 Cayman S" format
5. **Transmission** - "Automatic" or "Manual"
6. **Colors (Ext / Int)** - "White / Tan" format
7. **Top Options** - Value-ordered, comma-separated
8. **Source** - Clear host identification (cars.com, truecar.com, carvana.com)

#### 5.2 Formatting Rules
- **Price**: Round up to nearest $1k, show as "$31k", "$24k"
- **Miles**: Round up to nearest 1k, show as "61k", "36k"
- **Deal Δ**: Signed number with optional $ prefix (e.g., "+2801", "-$8,373")
- **Missing Values**: Show blank in view (no fake data)
- **String Casing**: Preserve factory color names when reasonable

#### 5.3 Sorting & Grouping
1. **Primary Group**: Automatic transmissions first, Manual transmissions second
2. **Within Groups**: Sort by Deal Δ descending (best deals first)
3. **Tie-break**: Price ascending (lower price wins ties)

#### 5.4 Color Theme
- **Old code to use as a baseline for handling color display**: Color mappings, Exterior and Interior column display.
```
# =========================
# THEME
# =========================
THEME = {
    "bg":            "#0B0F14",
    "surface":       "#121820",
    "surface_alt":   "#0E141B",

    "text":          "#C9D1D9",
    "text_muted":    "#8A97A6",
    "text_dim":      "#55616E",

    "gray_900": "#1A222C",
    "gray_800": "#252F3A",
    "gray_700": "#3A4654",
    "gray_600": "#4D5967",
    "gray_500": "#6B7785",
    "gray_400": "#8794A2",
    "gray_300": "#A5AFBA",
    "gray_200": "#C2CBD6",
    "gray_100": "#DEE4EC",

    # Teal ramp (cheap = bright, low miles = bright)
    "teal_1": "#5FFBF1",
    "teal_2": "#37E9DF",
    "teal_3": "#19E1D6",
    "teal_4": "#3FB8B0",
    "teal_5": "#5E8F91",
    "teal_6": "#6F7F82",

    # Oranges
    "orange_cayman_s":  "#FF6A1A",
    "orange_cayman":    "#FFC04D",
    "orange_boxster_s": "#FFD137",
    "orange_boxster":   "#FFE394",
    "orange_special_1": "#FF3B1A",
    "orange_special_2": "#E62500",

    # Warm dim ramp (manual de-emphasis)
    "warm_dim_1": "#6E5A4E",
    "warm_dim_2": "#665247",
    "warm_dim_3": "#5D4B41",
    "warm_dim_4": "#54443B",
    "warm_dim_5": "#4B3C35",
    "warm_dim_6": "#43362F",

    # Row stripe (subtle; only used on every 2nd row)
    "stripe_1": "#18212B",
}

# =========================
# Car Exterior and Interior colors
# =========================
EXTERIOR = {
    "arctic silver metallic":"#C9CCCE",
    "classic silver metallic":"#C6C9CB",
    "meteor gray":"#6E7479",
    "gray":"#8F969C",
    "black":"#0C0E10",
    "white":"#E9EAEA",
    "guards red":"#D0191A",
    "red":"#B0201B",
    "carrara white":"#EDEDED",
    "aqua blue metallic":"#2E6C8E",
    "malachite green metallic":"#2C5F51",
    "silver":"#C9CCCE",
    "midnight blue metallic":"#1A2C4E",
    "basalt black metallic":"#0B0F14",
}
INTERIOR = [
    (r"black|anthracite|graphite|charcoal", "#0E1114"),
    (r"sand\s*beige|beige",                  "#CBB68B"),
    (r"tan|camel|savanna",                   "#B48A60"),
    (r"cocoa|espresso|chocolate|brown",      "#6B4A2B"),
    (r"stone|platinum\s*gray|platinum\s*grey|gray|grey", "#A7ADB5"),
    (r"red|carmine|bordeaux",                "#7E1C1C"),
    (r"blue|navy",                            "#2F3A56"),
    (r"white|ivory|alabaster",                "#E8E8E8"),
]
def price_style_key(price_int: Optional[int])->str:
    if price_int is None: return "text_muted"
    if price_int < 20_000:  return "teal_1"
    if price_int < 25_000:  return "teal_2"
    if price_int < 30_000:  return "teal_3"
    if price_int < 35_000:  return "teal_4"
    if price_int < 40_000:  return "teal_5"
    return "teal_6"
def miles_style_key(miles_val: Optional[int])->str:
    if miles_val is None: return "text_muted"
    if miles_val < 30_000:  return "teal_1"
    if miles_val < 45_000:  return "teal_2"
    if miles_val < 60_000:  return "teal_3"
    if miles_val < 80_000:  return "teal_4"
    if miles_val < 100_000: return "teal_5"
    return "teal_6"
# =========================
# Colors (Ext/Int) — two 5-char blocks
# =========================
def render_color_swatches_cell(value: str) -> Text:
    s=(value or "").strip()
    ext,intn="",""
    if "/" in s: ext,intn=[p.strip() for p in s.split("/",1)]
    elif s: ext=s
    ext_hex=get_paint_hex(ext) or "#6E7479"
    int_hex=guess_interior_hex(intn) if intn else "#777777"
    t=Text()
    t.append(" "*SWATCH_HALF, style=theme_style(None, bg=ext_hex))
    t.append(" "*SWATCH_HALF, style=theme_style(None, bg=int_hex))
    return t    
```

### 6. Configuration & Customization

#### 6.1 Editable Parameters
- **Search URLs**: AutoTempest search URLs for different sources
- **Fair Value Model**: Base values, premiums, bonuses, color preferences
- **Options Catalog**: Values, synonyms, standard-on rules
- **Display Preferences**: Colorization, formatting options
- **Processing Options**: Caching, deduplication rules, concurrency settings

#### 6.2 Configuration File Structure
```toml
[search]
urls = [
    "https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214"
]

[fair_value]
base_value_usd = 30500
year_step_usd = 500
s_premium_usd = 7000
exterior_color_usd = 300
interior_color_usd = 300
special_trim_premiums = { "Cayman R" = 30000, "Boxster Spyder" = 30000 }

[scraping]
concurrency = 2
polite_delay_ms = 1000
cap_listings = 150
debug = true
```

## Non-Functional Requirements

### 1. Performance
- **Processing Speed**: Handle 1000+ listings in under 5 seconds
- **Memory Usage**: Efficient memory usage for large datasets
- **Scalability**: Support for multiple CSV files and growing datasets
- **Scraping Speed**: Conservative pacing (5+ minutes for ~150 listings) for reliability

### 2. Usability
- **Quick Scanning**: Results should be scannable in under 10 seconds
- **Intuitive Display**: Clear visual hierarchy and consistent formatting
- **Minimal Configuration**: Sensible defaults with easy customization
- **Error Tolerance**: Partial failures don't crash the pipeline

### 3. Reliability
- **Data Integrity**: No data loss during processing
- **Error Handling**: Graceful handling of malformed CSV data and failed scrapes
- **Validation**: Input validation and error reporting
- **Headful Scraping**: Predictable results over headless quirks

### 4. Maintainability
- **Data-Driven**: Options catalog and rules should be configurable without code changes
- **Modular Design**: Clear separation of concerns between collection, scraping, processing, and display
- **Documentation**: Clear implementation guide for future modifications
- **Lean Dependencies**: Minimal external packages for faster iteration

## Technical Architecture

### 1. Core Components
- **Collector**: AutoTempest-based URL collection from multiple sources
- **Universal Scraper**: Single VDP processing engine with site-specific profiles
- **Data Normalizer**: Apply transformation rules consistently
- **Valuation Engine**: Calculate fair values and deal deltas
- **Options Detector**: Match and value options from raw text
- **Display Renderer**: Generate formatted output tables

### 2. Data Flow
1. **Collection**: AutoTempest URLs → Collector
2. **Scraping**: URLs → Universal VDP Scraper → Raw Data
3. **Processing**: Raw Data → Normalizer → Options Detector → Valuation Engine
4. **Output**: Valuation Engine → Display Renderer → Formatted Table

### 3. Technology Stack
- **User Environment**: Powershell on Windows 10
- **Language**: Python 3.10-3.12
- **Core Dependencies**: 
  - `playwright` (headful scraping)
  - `rich` (terminal formatting)
  - `tomli`/`tomllib` (configuration)
- **Configuration**: TOML files for human-friendly editing


### 4. File Structure
```
x987-app/
├── x987/                    # Package code (small modules)
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── settings.py
│   ├── doctor.py
│   ├── schema.py
│   ├── utils/
│   ├── collectors/
│   ├── scrapers/
│   ├── pipeline/
│   └── view/
├── scripts/                 # Setup scripts
├── tests/                   # Minimal testing
└── docs/                    # Documentation

x987-config/             # Persistent user state
├── config.toml
├── rules/
├── input/manual-csv/
├── fixtures/
└── backups/

x987-data/                   # Outputs (regenerated each run)
├── raw/
├── normalized/
└── meta/
```

## Success Criteria

### 1. Functional Success
- From multiple sources, the table ranks cars so top three PDK picks emerge immediately
- Manual cars appear below automatics, still ranked by deal delta for reference
- Adjusting configuration numbers updates rankings predictably
- Table is readable at a glance with clean formatting
- Source column clearly identifies the listing origin

### 2. User Experience Success
- Simple run command, all options and configs are handled in the configuration file
- Users can identify the best deals within 10 seconds of viewing results
- Configuration changes produce expected and explainable results
- Display format supports quick scanning without information overload
- Partial scraping failures don't interrupt the user experience

### 3. Technical Success
- Application processes 1000+ listings efficiently
- Configuration is data-driven and easily modifiable
- Code is maintainable and well-documented
- Edge cases are handled gracefully
- Fast iteration cycles with isolated testing capabilities

### 4. Iteration Efficiency Success
- Each pipeline step can run standalone for debugging
- Fixtures-first approach enables offline testing
- Lean codebase with minimal dependencies
- Clear contracts and small, focused modules

## Development Phases

### Phase 1: Core Infrastructure
- Universal VDP scraper with site profiles
- AutoTempest collector implementation
- Basic normalization rules implementation
- Configuration file system (TOML)

### Phase 2: Multi-Source Support
- Cars.com, TrueCar, and Carvana profiles
- Error handling and partial failure tolerance
- Pipeline integration and testing

### Phase 3: Valuation Engine
- Fair value calculation model
- Options detection system
- Mileage and color bonus logic

### Phase 4: Display & Output
- Table formatting and sorting
- Column organization and alignment
- Basic colorization (optional)

### Phase 5: Refinement & Testing
- Edge case handling
- Performance optimization
- User testing and feedback integration

## Risk Mitigation

### 1. Data Quality Risks
- **Risk**: Malformed CSV data causing processing errors
- **Mitigation**: Robust input validation and error handling

### 2. Scraping Reliability Risks
- **Risk**: Site DOM changes or anti-bot measures
- **Mitigation**: Headful Playwright, site profiles, fixtures for testing

### 3. Performance Risks
- **Risk**: Large datasets causing slow processing
- **Mitigation**: Efficient algorithms and optional caching

### 4. Configuration Complexity
- **Risk**: Too many configuration options overwhelming users
- **Mitigation**: Sensible defaults with progressive disclosure

### 5. Maintenance Risks
- **Risk**: Hard-coded rules making updates difficult
- **Mitigation**: Data-driven configuration and clear documentation

### 6. Iteration Risks
- **Risk**: Complex dependencies slowing development cycles
- **Mitigation**: Lean codebase, isolated testing, fixtures-first approach

## Testing & Verification Strategy

### 1. Testing Approach
- **Smoke Test**: End-to-end pipeline with mixed sources
- **Parser Micro-Test**: HTML snippet parsing validation
- **Fixtures-First**: Offline testing with saved HTML snapshots
- **Golden Outputs**: Regression detection for pricing/scoring/view

### 2. Verification Methods
- **Standalone Testing**: Each pipeline step can run independently
- **Manual Verification**: Compare outputs with v2 baseline
- **Error Tolerance**: Partial failures don't crash the system

### 3. Quality Gates
- **Core Functionality**: App runs end-to-end with correct outputs
- **Iteration Efficiency**: Codebase remains lean and fast to iterate
- **Dependency Management**: Only essential packages included

## Future Enhancements

### 1. Advanced Features
- Web interface for easier CSV upload and viewing
- Export functionality (PDF, Excel, etc.)
- Historical price tracking and trends
- Additional car listing sources

### 2. Integration Opportunities
- Direct API integration with car listing sites
- Automated CSV scraping and updates
- Mobile-friendly responsive design

### 3. Analytics & Insights
- Market trend analysis
- Price prediction models
- Comparative market analysis

---

*This document serves as the development plan for the View-from-CSV project v4. It incorporates refinements from previous versions and focuses on streamlined architecture, multi-source support, and iteration efficiency.*
