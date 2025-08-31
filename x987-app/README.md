# View-from-CSV v4.5

A data processing and visualization application that transforms scraped CSV data of 987.2 Cayman/Boxster listings into a ranked, scannable table with a fair-value pricing model.

## Features

- **Multi-Source Support**: Collect listings from Cars.com, TrueCar, and Carvana via AutoTempest
- **Universal Scraper**: Single engine with site-specific profiles for reliable data extraction
- **Fair Value Model**: Configurable pricing algorithm with options detection
- **Smart Ranking**: Sort by deal delta (fair value minus asking price) with transmission grouping
- **Options Detection**: Advanced pattern matching for car options with configurable values
- **Lean Architecture**: Fast iteration cycles with isolated testing capabilities

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Windows 10 (PowerShell)
- Internet connection for web scraping

### Installation

1. **Clone or download** the project to your local machine
2. **Open PowerShell** in the `x987-app` directory
3. **Run the setup script**:
   ```powershell
   .\scripts\setup.ps1
   ```

The setup script will:
- Create a Python virtual environment
- Install required dependencies
- Set up Playwright browsers
- Create configuration and data directories
- Run system diagnostics

### First Run

1. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the application**:
   ```powershell
   python -m x987
   ```

This will execute the complete pipeline: collect → scrape → transform → dedupe → fair value → rank → report.

## Configuration

The application uses TOML configuration files located in `x987-config/config.toml`. Key settings include:

### Search Configuration
```toml
[search]
urls = [
    "https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214"
]
```

### Fair Value Model
```toml
[fair_value]
base_value_usd = 30500
year_step_usd = 500
s_premium_usd = 7000
exterior_color_usd = 300
interior_color_usd = 300
```

### Scraping Settings
```toml
[scraping]
concurrency = 2
polite_delay_ms = 1000
cap_listings = 150
debug = true
```

## Usage

### Command Line Interface

The application provides several commands for different operations:

```powershell
# Run complete pipeline (default)
python -m x987

# Run individual steps
python -m x987 collect      # Collect URLs
python -m x987 scrape       # Scrape vehicles
python -m x987 transform    # Normalize data
python -m x987 dedupe       # Remove duplicates
python -m x987 fairvalue    # Calculate fair values
python -m x987 rank         # Rank by deal delta

# Display final ranked view from latest results
python -m x987 view-step

# System diagnostics
python -m x987 doctor

# Help
python -m x987 --help
```

### Output

The application generates several output files in the `x987-data` directory:

- **Raw data**: Timestamped CSV files from scraping
- **Normalized data**: Processed and cleaned listings
- **Final results**: Ranked listings with fair values and deal deltas
- **Terminal report**: Formatted table for quick scanning

## Architecture

### Core Components

- **Collector**: AutoTempest-based URL collection
- **Universal Scraper**: Single VDP processing engine with site profiles
- **Data Normalizer**: Consistent formatting and validation
- **Options Detector**: Pattern-based option detection and valuation
- **Fair Value Engine**: Configurable pricing model
- **Display Renderer**: Terminal-friendly table output

### Data Flow

1. **Collection**: AutoTempest URLs → Collector
2. **Scraping**: URLs → Universal VDP Scraper → Raw Data
3. **Processing**: Raw Data → Normalizer → Options Detector → Valuation Engine
4. **Output**: Valuation Engine → Display Renderer → Formatted Table

### File Structure

```
x987-app/
├── x987/                    # Package code
│   ├── utils/              # Utility modules
│   ├── collectors/         # URL collection
│   ├── scrapers/           # Web scraping
│   ├── pipeline/           # Data processing
│   └── view/               # Output formatting
├── scripts/                 # Setup scripts
├── tests/                   # Test files
└── docs/                    # Documentation

x987-config/                 # Configuration files
├── config.toml             # Main configuration
├── rules/                   # Custom rules
└── input/manual-csv/        # Manual CSV files

x987-data/                   # Output data
├── raw/                     # Raw scraped data
├── normalized/              # Processed data
└── meta/                    # Metadata and logs
```

## Fair Value Model

The application calculates fair value using a configurable formula:

```
Fair Value = Base + Trim Premium + Year Step + Mileage Bonus + Color Bonus + Options Total
Deal Δ = Fair Value - Asking Price
```

### Base Values
- **Base Car**: $30,500 (2009 Base, Automatic, 60-79k miles, mono/mono, no options)
- **Year Step**: +$500 per year from 2009
- **Trim Premiums**: S ($7,000), R ($30,000), Black Edition ($1,500), Boxster Spyder ($30,000)

### Mileage Bands
- <40k: +$3,000
- 40-59k: +$1,500
- 60-79k: +$0 (neutral)
- 80-99k: -$4,000
- 100k-119k: -$9,000
- ≥120k: -$15,000

### Options Detection

The system detects options using pattern matching and assigns configurable values:

- **LSD**: $1,200
- **Sport Chrono**: $1,000
- **Sport Exhaust**: $800
- **PASM**: $800
- **19" Wheels**: $400
- **BOSE**: $300
- **PCM/Nav**: $300
- **Bi-Xenon**: $250
- **Heated/Cooled Seats**: $150
- **Sport Seats**: $500

## Development

### Setup Development Environment

1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Install Playwright**: `playwright install chromium`
4. **Run tests**: `python -m pytest tests/`

### Code Structure

- **Small modules**: Most modules are ≤150 lines of code
- **Clear contracts**: Each module has documented interfaces
- **Isolated testing**: Each pipeline step can run independently
- **Fixtures-first**: Offline testing with saved HTML snapshots

### Adding New Features

1. **Update requirements** in `PROJECT_REQUIREMENTS.md`
2. **Implement core functionality** in appropriate modules
3. **Add tests** for new features
4. **Update documentation** and examples

## Troubleshooting

### Common Issues

**Playwright browser not found**
```powershell
playwright install chromium
```

**Configuration errors**
- Check `x987-config/config.toml` syntax
- Verify all required fields are present
- Run `python -m x987 doctor` for diagnostics

**Scraping failures**
- Check network connectivity
- Verify target sites are accessible
- Review scraping configuration (delays, concurrency)

**Memory issues**
- Reduce `cap_listings` in configuration
- Process data in smaller batches
- Monitor system resources

### Debug Mode

Enable debug mode for detailed logging:

```powershell
python -m x987 --debug
```

Or set in configuration:
```toml
[scraping]
debug = true
```

## Performance

- **Processing Speed**: 1000+ listings in under 5 seconds
- **Scraping Speed**: Conservative pacing (~5 minutes for 150 listings)
- **Memory Usage**: Efficient processing with configurable batch sizes
- **Scalability**: Support for multiple sources and growing datasets

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make changes** following the established patterns
4. **Add tests** for new functionality
5. **Submit a pull request**

## License

This project is provided as-is for educational and personal use.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run system diagnostics: `python -m x987 doctor`
3. Review configuration and logs
4. Check the project requirements document

---

**View-from-CSV v4.5** - Streamlined architecture with universal scraper, multi-source support, and optimized iteration efficiency.
