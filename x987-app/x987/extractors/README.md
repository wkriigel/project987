# Modular Extraction System

This directory contains the new modular extraction system that follows the same "one file per field" approach as the options system. Each extraction field has its own dedicated file with extraction logic.

## Architecture

### Individual Extractor Files

Each field has its own dedicated file:

- **`year.py`** - Extracts vehicle year from text
- **`price.py`** - Extracts vehicle price from text  
- **`mileage.py`** - Extracts vehicle mileage from text
- **`model_trim.py`** - Extracts model and trim as combined field (ModelTrim)
- **`colors.py`** - Extracts exterior and interior colors
- **`source.py`** - Extracts source/website from URLs or text
- **`deal.py`** - Calculates deal delta (fair value minus asking price)

### Base Classes

- **`base.py`** - Abstract base classes and data structures
- **`registry.py`** - Automatic discovery and aggregation system
- **`unified.py`** - Backward-compatible unified interface

## Key Features

### 1. Automatic Discovery
The `ExtractorsRegistry` automatically:
- Scans the extractors directory for all `.py` files
- Imports each extractor module dynamically
- Discovers extractor instances (files export `EXTRACTOR_NAME_EXTRACTOR`)
- Validates that each extractor has required methods
- Aggregates all extractors into a unified interface

### 2. Modular Design
Each extractor is completely self-contained:
- **Independent**: Can be modified without affecting others
- **Testable**: Each extractor can be tested in isolation
- **Extensible**: Easy to add new extractors by creating new files
- **Configurable**: Each extractor can have its own configuration

### 3. Consistent Interface
All extractors implement the same interface:
- `get_field_name()` - Returns the field name this extractor handles
- `get_patterns()` - Returns the regex patterns for extraction
- `extract(text, **kwargs)` - Extracts data from text
- `_process_match(match, **kwargs)` - Processes regex matches

### 4. Backward Compatibility
The `UnifiedExtractor` provides the same interface as the current extraction functions:
- `extract_year_from_text(text)`
- `extract_price_from_text(text)`
- `extract_mileage_from_text(text)`
- `extract_model_trim_from_text(text)`
- `extract_colors_from_text(text)`
- `extract_source_from_text(text, url)`
- `extract_deal_delta(fair_value, asking_price)`

## Usage

### Basic Usage

```python
from x987.extractors import EXTRACTORS_REGISTRY, UNIFIED_EXTRACTOR

# Get a specific extractor
year_extractor = EXTRACTORS_REGISTRY.get_extractor_by_field("year")
result = year_extractor.extract("2010 Porsche Cayman S")

# Use the unified interface
year = UNIFIED_EXTRACTOR.extract_year("2010 Porsche Cayman S")
price = UNIFIED_EXTRACTOR.extract_price("Price: $32,500")
mileage = UNIFIED_EXTRACTOR.extract_mileage("45,000 miles")
```

### Extract All Fields

```python
# Extract all available fields
results = UNIFIED_EXTRACTOR.extract_all(text)

# Get detailed extraction summary
summary = UNIFIED_EXTRACTOR.get_extraction_summary(text, url)
```

### Individual Extractors

```python
# Use individual extractors directly
from x987.extractors.year import YEAR_EXTRACTOR
from x987.extractors.price import PRICE_EXTRACTOR

year_result = YEAR_EXTRACTOR.extract(text)
price_result = PRICE_EXTRACTOR.extract(text)
```

## Adding New Extractors

To add a new extraction field:

1. **Create a new file** (e.g., `vin.py`)
2. **Inherit from BaseExtractor**:
   ```python
   from .base import BaseExtractor, ExtractionResult
   
   class VINExtractor(BaseExtractor):
       def get_field_name(self) -> str:
           return "vin"
       
       def get_patterns(self) -> List[str]:
           return [r'VIN\s*:?\s*([A-HJ-NPR-Z0-9]{17})']
   ```

3. **Export an instance**:
   ```python
   VIN_EXTRACTOR = VINExtractor()
   ```

4. **The registry will automatically discover it** on next import

## Testing

Run the test script to verify all extractors work:

```bash
python test_modular_extractors.py
```

This will test:
- Individual extractor functionality
- Unified extractor interface
- Automatic discovery system
- Detailed extraction summaries

## Benefits

### 1. Maintainability
- **Clear separation**: Each field has its own file
- **Easy debugging**: Issues are isolated to specific extractors
- **Simple modifications**: Change one field without affecting others

### 2. Extensibility
- **Add new fields**: Just create new files
- **Modify patterns**: Update regex patterns in individual files
- **Custom logic**: Each extractor can have specialized processing

### 3. Testing
- **Unit testing**: Test each extractor independently
- **Pattern validation**: Verify regex patterns work correctly
- **Integration testing**: Test the unified interface

### 4. Performance
- **Compiled patterns**: Regex patterns are compiled once
- **Efficient matching**: Uses compiled patterns for fast extraction
- **Lazy loading**: Extractors are loaded only when needed

## Migration from Old System

The new system is designed to be a drop-in replacement:

1. **Import the unified extractor**:
   ```python
   from x987.extractors.unified import extract_year_from_text
   ```

2. **Use the same function calls**:
   ```python
   year = extract_year_from_text(text)  # Same as before
   ```

3. **Gradually migrate** to the new modular approach as needed

## Future Enhancements

- **Configuration files**: Per-extractor configuration
- **Machine learning**: Confidence scoring based on pattern matches
- **Validation rules**: Field-specific validation logic
- **Performance metrics**: Extraction speed and accuracy tracking
