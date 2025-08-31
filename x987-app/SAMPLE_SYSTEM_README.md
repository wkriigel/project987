# x987 Sample System for Quality Improvement

## Overview

The x987 Sample System is a new feature that automatically extracts sample HTML content from different car listing sources and provides tools to test and improve scraping quality. This system helps developers iterate on scraping techniques without repeatedly hitting live websites.

## How It Works

### 1. Automatic Sample Extraction

When scraping vehicle pages, the system automatically:
- Checks if a sample already exists for the source
- If no sample exists, extracts the page title and listing-overview section
- Saves the sample as a formatted HTML file for offline testing
- Never overwrites existing samples (one-time extraction per source)

### 2. Sample-Based Testing

The system provides tools to:
- Test different CSS selectors against saved samples
- Evaluate extraction techniques for various fields (title, mileage, VIN, etc.)
- Generate recommendations for improving scraping quality
- Compare different approaches without network requests

### 3. Quality Improvement Workflow

1. **Extract samples** during normal scraping operations
2. **Test techniques** against samples using the CLI
3. **Review recommendations** for improvement
4. **Iterate on selectors** and extraction logic
5. **Validate improvements** against the same samples

## File Structure

```
x987-app/
├── samples/                    # Sample HTML files
│   └── cars_com/             # Cars.com samples
│       └── sample.html       # Formatted sample with metadata
├── x987/
│   └── pipeline/
│       ├── sample_extractor.py    # Sample extraction logic
│       └── sample_tester.py       # Sample testing and analysis
└── test_sample_system.py     # Test script for the system
```

## Usage

### Command Line Interface

The system adds several new CLI commands:

```bash
# List available samples
python -m x987.cli.main samples

# Test a specific source's sample
python -m x987.cli.main test-sample cars_com

# Run system diagnosis
python -m x987.cli.main doctor

# Run complete pipeline (includes sample extraction)
python -m x987.cli.main pipeline
```

### Sample Testing

Test scraping techniques against saved samples:

```bash
# Test cars.com sample
python -m x987.cli.main test-sample cars_com
```

This will:
- Load the cars.com sample HTML
- Test different title extraction selectors
- Evaluate listing-overview section extraction
- Test field-specific extraction (mileage, VIN, transmission)
- Generate recommendations for improvement
- Save detailed test results to JSON

### Programmatic Usage

```python
from x987.pipeline.sample_extractor import SampleExtractor
from x987.pipeline.sample_tester import SampleTester

# Extract samples during scraping
extractor = SampleExtractor(config)
if extractor.extract_sample_if_needed(page, url):
    print("New sample extracted!")

# Test samples for quality improvement
tester = SampleTester(config)
results = tester.test_source_sample("cars_com")
print(f"Recommendations: {results['recommendations']}")
```

## Sample File Format

Sample files are formatted HTML with:

- **Metadata section**: Source, extraction date, page title
- **Title element**: The extracted page title for analysis
- **Main content**: The listing-overview section or fallback content
- **Styling**: Clean, readable format for easy analysis

Example sample structure:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sample Extract from Cars.com</title>
    <style>/* Clean styling */</style>
</head>
<body>
    <div class="sample-title">
        <h1>Sample Extract from Cars.com</h1>
        <div class="metadata">
            <p><strong>Extracted:</strong> 2025-01-24 13:52:00</p>
            <p><strong>Source:</strong> Cars.com</p>
            <p><strong>Page Title:</strong> 2010 Porsche 987.2 Cayman S</p>
        </div>
    </div>
    
    <div class="sample-content">
        <h2>Page Title Element:</h2>
        <div>2010 Porsche 987.2 Cayman S</div>
        
        <h2>Main Content Section:</h2>
        <div><!-- listing-overview content --></div>
    </div>
</body>
</html>
```

## Testing Different Techniques

### Title Extraction Testing

The system tests multiple title selectors:
- `h1[data-testid='vehicle-title']`
- `h1.vehicle-title`
- `h1.spark-heading-2`
- `.vehicle-title`
- `h1`

And scores them based on:
- Content length
- Presence of vehicle-related keywords
- Numeric content (year, price)

### Field Extraction Testing

For each field (mileage, VIN, transmission), the system:
- Tests profile-defined selectors
- Evaluates text-based extraction
- Checks for pattern matching
- Provides fallback strategies

### Overview Section Testing

Analyzes the listing-overview section for:
- Presence and size
- Key element detection
- Content quality assessment

## Recommendations

The system generates actionable recommendations:

1. **Selector improvements**: "Use 'h1.vehicle-title' for title extraction"
2. **Strategy suggestions**: "Consider text-based search in listing-overview"
3. **Fallback options**: "Implement regex pattern matching for VIN"
4. **Content expansion**: "Include more key elements in overview extraction"

## Benefits

### For Developers

- **Faster iteration**: Test changes without network requests
- **Reproducible testing**: Same content every time
- **Quality metrics**: Quantified improvement tracking
- **Best practices**: Data-driven selector optimization

### For Quality

- **Consistent extraction**: Same techniques across all pages
- **Error reduction**: Validate selectors before deployment
- **Performance improvement**: Optimize extraction logic
- **Maintenance**: Easy to update when sites change

## Integration

### Automatic Integration

The sample extraction is automatically integrated into the existing scraping pipeline:

```python
# In scrape_vehicle_page function
try:
    from .sample_extractor import SampleExtractor
    sample_extractor = SampleExtractor({})
    if sample_extractor.extract_sample_if_needed(page, url):
        logger.info("✓ Sample extracted for quality improvement")
except Exception as e:
    logger.warning(f"⚠️  Sample extraction failed: {e}")
```

### Manual Integration

You can also integrate sample extraction into custom scraping workflows:

```python
def custom_scraping_workflow(page, url):
    # Extract sample first
    extractor = SampleExtractor(config)
    extractor.extract_sample_if_needed(page, url)
    
    # Then proceed with normal scraping
    # ... your scraping logic ...
```

## Troubleshooting

### Common Issues

1. **No samples found**: Run scraping first to generate samples
2. **Import errors**: Ensure beautifulsoup4 is installed
3. **Permission errors**: Check write permissions for samples directory
4. **Empty samples**: Verify page content is loading properly

### Debug Mode

Enable debug logging to see detailed extraction information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Sample Validation

Manually inspect sample files to ensure quality:

```bash
# Open sample in browser
open samples/cars_com/sample.html
```

## Future Enhancements

Planned improvements include:

1. **Multi-page samples**: Multiple examples per source
2. **Automated testing**: CI/CD integration for quality checks
3. **Performance metrics**: Extraction speed and accuracy tracking
4. **Selector optimization**: Machine learning for selector improvement
5. **Cross-source comparison**: Benchmarking across different sites

## Contributing

To improve the sample system:

1. **Add new sources**: Extend the source mapping in sample_tester.py
2. **Improve selectors**: Update site profiles with better selectors
3. **Enhance testing**: Add new extraction technique tests
4. **Optimize extraction**: Improve the sample content extraction logic

## Support

For questions or issues with the sample system:

1. Check the test script: `python test_sample_system.py`
2. Review the CLI help: `python -m x987.cli.main --help`
3. Examine sample files in the `samples/` directory
4. Check the system diagnosis: `python -m x987.cli.main doctor`
