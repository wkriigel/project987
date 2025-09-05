# View-from-CSV Architecture v4.5

## Overview

This document describes the cleaned and reorganized architecture of View-from-CSV v4.5, which focuses on maintainability, code organization, and developer efficiency.

## Key Improvements

### 1. Modular Architecture
- **Separated Concerns**: Each module has a single, clear responsibility
- **Clean Interfaces**: Well-defined contracts between modules
- **Reduced Coupling**: Modules depend on interfaces, not implementations

### 2. Scraper Architecture
- **Base Scraper**: Abstract base class with common functionality
- **Site Profiles**: Data-driven configuration for different sites
- **Universal Scraper**: Single engine that works across all sources

### 3. Pipeline Organization
- **Step-by-Step**: Clear pipeline execution order
- **Error Handling**: Consistent error handling across all steps
- **Testing**: Each step can be tested independently

### 4. View Layer
- **Theme Separation**: Styling configuration separated from logic
- **Formatting Functions**: Pure functions for data formatting
- **Report Generation**: Clean, focused report creation

## Directory Structure

```
x987-app/
├── x987/                          # Main package
│   ├── __init__.py               # Public API
│   ├── __main__.py               # Entry point
│   ├── cli/                      # CLI package
│   │   ├── __init__.py          # CLI public API
│   │   ├── main.py              # Main CLI logic
│   │   ├── commands.py          # Command implementations
│   │   └── utils.py             # CLI utilities
│   ├── config/                   # Configuration package
│   │   ├── __init__.py          # Config public API
│   │   ├── manager.py           # Configuration management
│   │   ├── validation.py        # Configuration validation
│   │   └── defaults.py          # Default configurations
│   ├── scrapers/                 # Web scraping package
│   │   ├── __init__.py          # Scrapers public API
│   │   ├── base.py              # Base scraper interface
│   │   ├── profiles.py          # Site-specific profiles
│   │   └── universal.py         # Universal VDP scraper
│   ├── pipeline/                 # Data processing pipeline
│   │   ├── __init__.py          # Pipeline public API
│   │   ├── collect_streamlined.py # URL collection
│   │   ├── scrape_clean.py      # Clean scraping (NEW)
│   │   ├── transform.py         # Data transformation
│   │   ├── dedupe.py            # Data deduplication
│   │   ├── fairvalue.py         # Fair value calculation
│   │   └── rank.py              # Data ranking
│   ├── view/                     # Data visualization
│   │   ├── __init__.py          # View public API
│   │   ├── theme.py             # Styling and theming (NEW)
│   │   ├── report_clean.py      # Clean report generation (NEW)
│   │   └── report_fixed.py      # Legacy report (deprecated)
│   ├── utils/                    # Common utilities
│   │   ├── __init__.py          # Utils public API
│   │   ├── csv_io.py            # CSV I/O operations
│   │   ├── io.py                # General I/O operations
│   │   ├── log.py               # Logging utilities
│   │   └── text.py              # Text processing utilities
│   ├── schema.py                 # Data models and schemas
│   ├── settings.py               # Legacy settings (deprecated)
│   ├── fair_value.py            # Legacy fair value step (no-op in MSRP-only)
│   ├── options_v2.py            # Options detection system
│   └── doctor.py                 # System diagnostics
```

## Module Dependencies

### Core Dependencies
```
cli/ → pipeline/ → scrapers/ → config/
  ↓         ↓         ↓         ↓
view/ → utils/ → schema/ → settings/
```

### Dependency Flow
1. **CLI** orchestrates the pipeline
2. **Pipeline** processes data through steps
3. **Scrapers** extract data from web sources
4. **Config** provides configuration data
5. **View** displays results
6. **Utils** provides common functionality
7. **Schema** defines data structures

## Key Design Patterns

### 1. Strategy Pattern (Scrapers)
- Different sites use different scraping strategies
- All strategies implement the same interface
- Easy to add new sites without changing core code

### 2. Factory Pattern (Site Profiles)
- Site profiles are created based on URL patterns
- Profiles contain all site-specific configuration
- Centralized management of site configurations

### 3. Pipeline Pattern (Data Processing)
- Data flows through a series of processing steps
- Each step can be tested independently
- Easy to add/remove/reorder steps

### 4. Template Method (Base Scraper)
- Common scraping logic in base class
- Site-specific logic in derived classes
- Consistent behavior across all scrapers

## Configuration Management

### TOML Configuration
```toml
[search]
urls = ["https://autotempest.com/..."]

[fair_value]
base_value_usd = 30500
year_step_usd = 500

[scraping]
concurrency = 2
polite_delay_ms = 1000
```

### Environment Variables
- `X987_BG_PRICE`: Enable price background colors
- `X987_BG_MILES`: Enable mileage background colors

## Error Handling

### Consistent Error Handling
- All modules use the same error handling patterns
- Errors are logged with context
- Partial failures don't crash the system

### Error Recovery
- Failed scrapes are logged but don't stop processing
- Configuration errors provide helpful messages
- Timeout protection for long-running operations

## Testing Strategy

### Unit Testing
- Each module can be tested independently
- Mock data and fixtures for offline testing
- Clear interfaces make mocking easier

### Integration Testing
- Pipeline steps can be tested in sequence
- End-to-end testing with sample data
- Configuration validation testing

### Performance Testing
- Timeout protection for long operations
- Progress indicators for user feedback
- Memory usage monitoring

## Migration Guide

### From v4.0 to v4.1

#### 1. Import Changes
```python
# Old
from x987.settings import get_config
from x987.pipeline.scrape_streamlined import run_scraping

# New
from x987.config import get_config
from x987.pipeline import run_scraping
```

#### 2. CLI Usage
```bash
# Old
python -m x987 scrape

# New (same, but cleaner internals)
python -m x987 scrape
```

#### 3. Configuration
- Configuration format remains the same
- New validation ensures configuration correctness
- Better error messages for configuration issues

## Future Enhancements

### 1. Plugin System
- Site profiles as plugins
- Custom scraping strategies
- Extensible pipeline steps

### 2. Web Interface
- REST API for programmatic access
- Web UI for easier configuration
- Real-time progress monitoring

### 3. Advanced Analytics
- Historical price tracking
- Market trend analysis
- Predictive pricing models

## Best Practices

### 1. Adding New Sites
1. Create a new site profile in `scrapers/profiles.py`
2. Add selectors and patterns for the site
3. Test with sample URLs
4. Update documentation

### 2. Adding New Pipeline Steps
1. Create the step module in `pipeline/`
2. Implement the step function
3. Add to `PIPELINE_STEPS` in `pipeline/__init__.py`
4. Update CLI commands if needed

### 3. Modifying Display
1. Update theme configuration in `view/theme.py`
2. Modify formatting functions in `view/report_clean.py`
3. Test with different data scenarios

### 4. Configuration Changes
1. Update `config/defaults.py` with new defaults
2. Add validation rules in `config/validation.py`
3. Update documentation and examples

## Performance Considerations

### 1. Scraping Performance
- Network blocking for faster page loads
- Concurrent scraping with controlled limits
- Polite delays to avoid rate limiting

### 2. Memory Usage
- Streaming processing for large datasets
- Efficient data structures
- Memory monitoring and cleanup

### 3. Processing Speed
- Optimized algorithms for data transformation
- Efficient sorting and filtering
- Minimal data copying

## Security Considerations

### 1. Input Validation
- URL validation before scraping
- Configuration file validation
- Data sanitization

### 2. Rate Limiting
- Polite delays between requests
- Configurable concurrency limits
- Respect for robots.txt

### 3. Error Handling
- No sensitive data in error messages
- Secure logging practices
- Graceful failure modes

---

This architecture provides a solid foundation for future development while maintaining the same user experience and functionality.
