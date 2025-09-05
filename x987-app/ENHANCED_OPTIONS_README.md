# Enhanced Options Detection System

## Overview

The enhanced options detection system provides comprehensive detection and categorization of Porsche 987.2 options from listing text. It uses pattern matching with multiple synonyms to identify options even when they're described in different ways.

## Features

### 1. Comprehensive Options Catalog

The system detects all the key options you requested:

#### Performance Options
- **Sport Chrono Package Plus** ($1,000) - Detects: "sport chrono", "chrono package", "chrono plus", etc.
- **PASM** ($800) - Detects: "pasm", "adaptive suspension", "active suspension", etc.
- **Limited Slip Differential (LSD)** ($1,200) - Detects: "limited slip", "lsd", "locking diff", etc.
- **Sport Exhaust (PSE)** ($800) - Detects: "pse", "sport exhaust", "switchable exhaust", etc.

#### Comfort & Interior Options
- **Sport Seats / Adaptive Sport Seats** ($500) - Detects: "sport seats", "adaptive sport seats", "bucket seats", etc.
- **Heated Seats** ($150) - Detects: "heated seats", "seat heating", "heated front seats", etc.
- **Ventilated Seat** ($150) - Detects: "ventilated seats", "cooled seats", "seat ventilation", etc.

#### Technology Options
- **PCM w/ Navigation** ($300) - Detects: "pcm", "navigation", "nav system", etc.
- **BOSE Surround Sound** ($300) - Detects: "bose", "bose sound system", "bose audio", etc.
- **Park Assist** ($200) - Detects: "park assist", "parking sensors", "parking aid", etc.

#### Appearance Options
- **Bi-Xenon Headlights with Dynamic Cornering** ($250) - Detects: "bi-xenon", "litronic", "cornering lights", etc.
- **18–19" Upgraded Wheels** ($400) - Detects: "19\"", "18\"", "19 inch wheels", etc.

### 2. Smart Pattern Matching

The system uses multiple detection strategies:

- **Exact matches**: "Sport Chrono Package Plus"
- **Abbreviations**: "PSE", "LSD", "PASM"
- **Synonyms**: "switchable exhaust" = "sport exhaust"
- **Technical terms**: "litronic" = "bi-xenon headlights"
- **Descriptive phrases**: "seat heating" = "heated seats"

### 3. Trim-Aware Detection

Some options are standard on certain trims and won't be counted as additional value:

- **Cayman R**: LSD and 19" wheels are standard (not counted)
- **Other trims**: These options add to the total value

### 4. Categorized Output

Options are automatically grouped into categories:

- **Performance**: Engine, suspension, drivetrain options
- **Comfort**: Seating, climate, interior options  
- **Technology**: Audio, navigation, safety features
- **Appearance**: Wheels, lighting, visual enhancements

## Usage

### Basic Options Detection

```python
from x987.options_v2 import OptionsDetector

detector = OptionsDetector()

# Detect options from text
options = detector.detect_options("Sport Chrono Package, PASM, PSE exhaust")
# Returns: [("Sport Chrono Package Plus", 1000, "performance"), 
#          ("PASM", 800, "performance"), 
#          ("Sport Exhaust (PSE)", 800, "performance")]

# Get total MSRP (sum of per-option MSRP)
total_value = detector.get_options_value("Sport Chrono Package, PASM, PSE exhaust")
# Returns: 2600 (represents MSRP total in MSRP-only mode)

# Get categorized options
by_category = detector.get_options_by_category("Sport Chrono Package, PASM, PSE exhaust")
# Returns: {"performance": ["Sport Chrono Package Plus", "PASM", "Sport Exhaust (PSE)"]}
```

### Detailed Options Summary

```python
# Get comprehensive summary
summary = detector.get_detailed_options_summary("Sport Chrono Package, PASM, PSE exhaust")

# Summary contains:
# {
#     "total_options": 3,
#     "total_value": 2600,  # MSRP total in MSRP-only mode
#     "by_category": {
#         "performance": {
#             "options": ["Sport Chrono Package Plus", "PASM", "Sport Exhaust (PSE)"],
#             "value": 2600
#         }
#     },
#     "all_options": ["Sport Chrono Package Plus", "PASM", "Sport Exhaust (PSE)"]
# }
```

### Integration with Listings

```python
from x987.schema import NormalizedListing

# Create listing with options
listing = NormalizedListing(
    timestamp_run_id="test",
    source="cars.com",
    listing_url="https://example.com",
    year=2010,
    model="Cayman",
    trim="S",
    raw_options="Sport Chrono Package, PASM, PSE exhaust, Sport Seats"
)

# Process options
detector = OptionsDetector()
summary = detector.get_detailed_options_summary(listing.raw_options, listing.trim)

# Update listing with options data
listing.options_summary = summary
listing.options_detected = summary['all_options']
listing.options_value = summary['total_value']  # MSRP total in MSRP-only mode
listing.options_by_category = summary['by_category']
```

## Configuration

The options system is configured via `x987-config/config.toml`:

```toml
[options_v2]
enabled = true

# Enhanced options catalog configuration
[options_v2.catalog]
# Performance Options
[[options_v2.catalog.performance]]
id = "639/640"
display = "Sport Chrono Package Plus"
value_usd = 1000
patterns = [
    "sport chrono", "chrono package", "chrono plus", "sport chrono plus",
    "chrono package plus", "sport chrono package", "chrono", "sport chrono package plus"
]
standard_on_trims = []
```

### Generation MSRP Overrides

You can override option MSRP per model/generation using `[options_per_generation]`:

```toml
[options_per_generation.defaults]
top_options = ["639/640", "PASM", "PSE", "LSD", "Sport Seats", "HTD", "PCM", "BOSE", "BIX", "19W", "PARK"]

[options_per_generation.911]
  [options_per_generation.911."996".msrp]
  PASM = 1990
  "639/640" = 920
  PSE = 2400
  X51 = 15000
  "Sport Seats" = 1550
  HTD = 500
  BOSE = 1390
  PCM = 3070
  LSD = 950
  SHORT_SHIFTER = 765
  BIX = 1090
  DIM_RAIN = 690
  SPORT_WHEEL = 330
  "19W" = 2000
```

## Testing

Run the test script to see the system in action:

```bash
cd x987-app
python test_enhanced_options.py
```

This will demonstrate:
- Pattern matching with various text formats
- Options categorization
- Value calculations
- Trim-aware detection

## Report Display

The enhanced options system integrates with the report display:

1. **Options Summary Panel**: Shows total options detected and values by category
2. **Main Table**: Displays detected options and Options MSRP Total in a clean, readable format
3. **Fallback Support**: Gracefully handles cases where options aren't detected

## Benefits

1. **Accurate Detection**: Multiple patterns catch options even with different wording
2. **MSRP Aggregation**: Automatic aggregation of Options MSRP Total
3. **Categorization**: Logical grouping makes it easy to understand what's included
4. **Trim Awareness**: Correctly handles standard equipment on special trims
5. **Extensible**: Easy to add new options and patterns via configuration
6. **Transmission Assumption**: Transmissions (PDK/Tiptronic) are assumed and not counted as options.

## Future Enhancements

- **Machine Learning**: Train on real listing data to improve pattern recognition
- **Dynamic Pricing**: Adjust option values based on market conditions
- **Option Dependencies**: Handle cases where options require other options
- **Market Analysis**: Track which options are most valuable in current market

## Troubleshooting

### Common Issues

1. **Options not detected**: Check if the text uses different terminology
2. **Incorrect values**: Verify the option is not standard on the trim
3. **Pattern conflicts**: Ensure patterns are specific enough to avoid false matches

### Debug Mode

Enable debug logging to see pattern matching in action:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For questions or issues with the options detection system:

1. Check the test script for examples
2. Review the configuration file for pattern definitions
3. Examine the options_v2.py source code for implementation details
4. Run tests to verify the system is working correctly
