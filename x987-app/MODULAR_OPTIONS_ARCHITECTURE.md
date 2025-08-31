# Modular Options Architecture

## Overview
The options detection system has been refactored from a monolithic approach to a modular, maintainable architecture where each option has its own file with pattern matching logic.

## Architecture Benefits

### ✅ **Modularity**
- Each option is self-contained in its own file
- Easy to add, remove, or modify individual options
- Clear separation of concerns

### ✅ **Maintainability**
- Pattern matching logic is isolated per option
- Easy to debug specific option detection issues
- Simple to add new patterns or synonyms

### ✅ **Scalability**
- New options can be added without touching existing code
- Categories can be extended independently
- Registry automatically includes all new options

### ✅ **Testability**
- Individual options can be tested in isolation
- Pattern matching can be validated per option
- Easy to mock specific options for testing

## File Structure

```
x987/options/
├── __init__.py              # Package initialization
├── base.py                  # Base classes (OptionDefinition, BaseOption)
├── detector.py              # Main OptionsDetector class
├── registry.py              # OptionsRegistry that aggregates all options
├── performance.py           # Performance options (Sport Chrono, PASM, LSD, PSE)
├── seating.py               # Seating options (Sport Seats, Heated, Ventilated)
├── technology.py            # Technology options (PCM, BOSE)
├── exterior.py              # Exterior options (Bi-Xenon, Wheels)
├── convenience.py           # Convenience options (Park Assist)
└── transmission.py          # Transmission options (PDK)
```

## Core Components

### 1. **Base Classes** (`base.py`)
- `OptionDefinition`: Data class for option metadata
- `BaseOption`: Abstract base class for all options

### 2. **Options Registry** (`registry.py`)
- `OptionsRegistry`: Aggregates all options from all modules
- Global instance: `OPTIONS_REGISTRY`
- Provides methods to query options by category, ID, etc.

### 3. **Options Detector** (`detector.py`)
- `OptionsDetector`: Main detection engine
- Uses the registry to check all available options
- Maintains the same public API for backward compatibility

## How It Works

### 1. **Option Definition**
Each option implements the `BaseOption` abstract class:

```python
class SportChronoPackagePlus(BaseOption):
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="639/640",
            display="Sport Chrono Package Plus",
            value_usd=1000,
            patterns=[
                r"\bsport\s+chrono\b",
                r"\bchrono\s+package\b",
                # ... more patterns
            ],
            category="performance"
        )
```

### 2. **Pattern Compilation**
The base class automatically compiles regex patterns:
- Patterns are compiled once during initialization
- Invalid patterns are gracefully skipped
- Case-insensitive matching by default

### 3. **Detection Logic**
Each option implements its own detection logic:
- `is_present(text, trim)`: Checks if option is present
- `get_value(text, trim)`: Returns option value if present
- Standard-on trim logic is handled automatically

### 4. **Registry Aggregation**
The registry automatically discovers and aggregates all options:
- Imports all option modules
- Creates instances of all option classes
- Provides unified access to all options

### 5. **Detection Process**
The detector iterates through all registered options:
- Checks each option for presence in the text
- Respects standard-on trim logic
- Returns sorted results by value and category

## Adding New Options

### Step 1: Create Option File
Create a new file in the appropriate category directory:

```python
# x987/options/performance.py
class NewPerformanceOption(BaseOption):
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="NEW_OPTION",
            display="New Performance Option",
            value_usd=500,
            patterns=[r"\bnew\s+option\b"],
            category="performance"
        )
```

### Step 2: Add to Category Export
Add the new option to the category's export list:

```python
PERFORMANCE_OPTIONS = [
    SportChronoPackagePlus(),
    PASM(),
    LimitedSlipDifferential(),
    SportExhaust(),
    NewPerformanceOption()  # Add here
]
```

### Step 3: Registry Auto-Discovery
The registry automatically includes the new option - no other changes needed!

## Pattern Matching Examples

### Performance Options
- **Sport Chrono**: `sport chrono`, `chrono package`, `chrono plus`
- **PASM**: `pasm`, `adaptive suspension`, `sport suspension`
- **LSD**: `limited slip`, `lsd`, `brake actuated limited slip`
- **PSE**: `sport exhaust`, `pse`, `dual exhaust`

### Seating Options
- **Sport Seats**: `sport seats`, `adaptive sport seats`, `bucket seats`
- **Heated Seats**: `heated seats`, `seat heating`, `heated front seats`
- **Ventilated Seats**: `ventilated seats`, `seat ventilation`

### Technology Options
- **PCM**: `pcm`, `navigation`, `navigation system`
- **BOSE**: `bose`, `premium sound system`, `surround sound`

### Exterior Options
- **Bi-Xenon**: `bi-xenon`, `projector headlights`, `xenon lighting`
- **Wheels**: `19 inch`, `alloy wheels`, `upgraded wheels`

## Backward Compatibility

The new system maintains 100% backward compatibility:
- Same `OptionsDetector` class interface
- Same method signatures and return values
- Same options detection results
- Existing code continues to work unchanged

## Performance Characteristics

- **Pattern Compilation**: Done once during initialization
- **Detection Speed**: O(n) where n = number of options
- **Memory Usage**: Minimal overhead from compiled patterns
- **Scalability**: Linear scaling with number of options

## Testing

### Individual Option Testing
```python
from x987.options.performance import SportChronoPackagePlus

option = SportChronoPackagePlus()
assert option.is_present("Sport Chrono Package", "S")
assert option.get_value("Sport Chrono Package", "S") == 1000
```

### Full System Testing
```python
from x987.options_v2 import OptionsDetector

detector = OptionsDetector()
detected = detector.detect_options("Sport Chrono and PASM", "S")
assert len(detected) == 2
```

## Future Enhancements

### 1. **Configuration-Based Options**
- Load option definitions from YAML/JSON files
- Runtime pattern modification
- Dynamic option value updates

### 2. **Advanced Pattern Matching**
- Fuzzy matching for typos
- Context-aware detection
- Machine learning pattern optimization

### 3. **Category Management**
- Dynamic category creation
- Hierarchical option relationships
- Cross-category dependencies

### 4. **Performance Optimization**
- Pattern caching strategies
- Parallel detection processing
- Lazy loading of option modules

## Conclusion

The new modular architecture provides:
- **Better maintainability** through separation of concerns
- **Easier extensibility** for new options and patterns
- **Improved testability** with isolated components
- **Cleaner code organization** with logical grouping
- **Future-proof design** for advanced features

This architecture makes the options system much more maintainable and scalable while preserving all existing functionality.
