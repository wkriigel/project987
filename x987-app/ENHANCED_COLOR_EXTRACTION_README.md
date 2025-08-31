# Enhanced Color Extraction System

## Overview

This document describes the comprehensive color extraction system implemented from `idea.txt`, which provides robust, multi-strategy color extraction for vehicle listings across multiple websites.

## Key Features

### 1. Multi-Strategy Extraction
The system uses a layered approach to maximize color extraction success:

- **Strategy 1: DOM-Based Extraction** (Most Reliable)
  - Uses CSS selectors to find color elements
  - Targets specific HTML structures (dt/dd pairs, class-based selectors)
  - Highest accuracy when selectors are properly configured

- **Strategy 2: Labeled Pattern Matching**
  - Searches for "Exterior color: [value]" patterns
  - Handles variations in labeling and formatting
  - Good fallback when DOM selectors fail

- **Strategy 3: Advanced Pattern Recognition**
  - Recognizes "Color1 Exterior Color2 Interior" patterns
  - Handles "Color1 on Color2" constructions
  - Uses sophisticated regex patterns for Porsche-specific colors

### 2. Advanced Color Normalization

#### Color Core Patterns
The system recognizes standard automotive colors:
```
Black, White, Gray, Grey, Silver, Red, Blue, Green, Tan, Beige, 
Brown, Gold, Purple, Burgundy, Yellow, Orange, Ivory, Cream, Pearl, Metallic
```

#### Color Adjective Patterns
Supports Porsche-specific color modifiers:
```
Arctic, Meteor, Classic, Carrera, Basalt, Carmine, Aqua, Racing, 
Guards, Seal, Sand, Sapphire, Slate, Midnight, Jet, Polar, 
Macadamia, Champagne
```

#### Pattern Examples
- `Arctic Silver Metallic` → Extracted as-is
- `Guards Red` → Extracted as-is  
- `Basalt Black Metallic` → Extracted as-is
- `Macadamia` → Extracted as-is

### 3. Intelligent Fallbacks

The system gracefully degrades through multiple extraction strategies:

1. **Primary**: DOM selector extraction
2. **Secondary**: Labeled pattern matching
3. **Tertiary**: Advanced pattern recognition
4. **Quaternary**: Text-based heuristics

## Implementation Details

### Core Functions

#### `clean_color(val: str | None) -> str | None`
- Validates color values
- Removes whitespace
- Filters out invalid/short values

#### `none_if_na(s: str | None) -> str | None`
- Detects N/A equivalents: `-`, `–`, `—`, `n/a`, `na`, `notspecified`
- Returns `None` for invalid values
- Preserves valid color text

#### `normalize_color_phrase(s: str | None) -> str | None`
- Applies advanced regex patterns
- Extracts valid color phrases
- Handles complex color constructions

#### `extract_colors_from_text(body_text: str) -> tuple[str | None, str | None]`
- Main extraction function
- Implements all fallback strategies
- Returns (exterior_color, interior_color) tuple

### Integration Points

#### Universal Scraper (`x987/scrapers/universal.py`)
- Enhanced `_extract_exterior_color()` and `_extract_interior_color()` methods
- DOM-first extraction with text-based fallbacks
- Comprehensive error handling

#### Streamlined Scraper (`x987/pipeline/scrape_streamlined.py`)
- Enhanced section-based extraction
- Multiple color extraction strategies
- Improved reliability for cars.com and similar sites

#### Text Utils (`x987/utils/text.py`)
- Core color processing functions
- Advanced pattern matching
- Color categorization (Monochrome vs Color)

## Usage Examples

### Basic Color Extraction
```python
from x987.utils.text import extract_colors_from_text

text = "Exterior color: Arctic Silver Metallic\nInterior color: Black"
ext_color, int_color = extract_colors_from_text(text)
# Result: ("Arctic Silver Metallic", "Black")
```

### Advanced Pattern Recognition
```python
text = "Arctic Silver Metallic Exterior Black Interior"
ext_color, int_color = extract_colors_from_text(text)
# Result: ("Arctic Silver Metallic", "Black")
```

### On/Over Patterns
```python
text = "Guards Red on Black"
ext_color, int_color = extract_colors_from_text(text)
# Result: ("Guards Red", "Black")
```

## Testing

Run the comprehensive test suite:

```bash
cd x987-app
python test_enhanced_color_extraction.py
```

The test suite validates:
- Color cleaning and validation
- N/A detection
- Color phrase normalization
- Comprehensive extraction strategies
- Color categorization
- Edge cases and error handling

## Benefits Over Previous System

### 1. **Higher Success Rate**
- Multiple extraction strategies increase success probability
- DOM failures don't result in complete extraction failure

### 2. **Better Color Quality**
- Preserves full color names (e.g., "Arctic Silver Metallic")
- Handles Porsche-specific color terminology
- Filters out invalid/N/A values

### 3. **Improved Reliability**
- Graceful degradation through fallback strategies
- Robust error handling
- Consistent output format

### 4. **Enhanced Maintainability**
- Centralized color processing logic
- Clear separation of concerns
- Comprehensive testing coverage

## Configuration

### Site Profiles
Color extraction can be customized per site through profile configurations:

```python
# Example site profile
{
    "exterior_selector": [".exterior-color", ".vehicle-exterior"],
    "interior_selector": [".interior-color", ".vehicle-interior"],
    "color_patterns": ["arctic silver", "guards red", "basalt black"]
}
```

### Color Patterns
Custom color patterns can be added to the regex constants:

```python
_COLOR_CORE = r"(?:Black|White|Gray|Grey|Silver|Red|Blue|Green|Tan|Beige|Brown|Gold|Purple|Burgundy|Yellow|Orange|Ivory|Cream|Pearl|Metallic|CustomColor)"

_COLOR_ADJ = r"(?:[A-Z][a-z]+|Arctic|Meteor|Classic|Carrera|Basalt|Carmine|Aqua|Racing|Guards|Seal|Sand|Sapphire|Slate|Midnight|Jet|Polar|Macadamia|Champagne|CustomModifier)"
```

## Performance Considerations

### Optimization Strategies
1. **DOM-First Approach**: Most reliable extraction method used first
2. **Early Exit**: Stops processing once colors are found
3. **Cached Patterns**: Regex patterns compiled once and reused
4. **Selective Text Processing**: Only processes relevant text sections

### Memory Usage
- Minimal memory overhead
- No large data structures
- Efficient string processing

## Future Enhancements

### Potential Improvements
1. **Machine Learning**: Train models on color extraction patterns
2. **Image Analysis**: Extract colors from vehicle photos
3. **Color Validation**: Cross-reference with known automotive color databases
4. **Internationalization**: Support for non-English color terms

### Extensibility
The system is designed to be easily extensible:
- New extraction strategies can be added
- Color patterns can be updated
- Site-specific customizations are supported

## Troubleshooting

### Common Issues

#### No Colors Extracted
1. Check if DOM selectors are working
2. Verify text content contains color information
3. Review regex patterns for site-specific variations

#### Incorrect Color Extraction
1. Validate color normalization patterns
2. Check for site-specific color terminology
3. Review fallback strategy priorities

#### Performance Issues
1. Monitor DOM selector performance
2. Optimize regex patterns
3. Consider caching strategies

### Debug Mode
Enable debug logging to see extraction strategy details:

```python
import logging
logging.getLogger("x987.utils.text").setLevel(logging.DEBUG)
```

## Conclusion

The enhanced color extraction system provides a robust, maintainable solution for extracting vehicle colors across multiple websites. By implementing multiple fallback strategies and advanced pattern matching, it significantly improves extraction success rates while maintaining high accuracy and performance.

The system successfully incorporates the best practices from `idea.txt` while maintaining compatibility with the existing codebase architecture.
