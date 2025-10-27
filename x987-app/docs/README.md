# View-from-CSV v4.5 Documentation Hub

## Overview

This directory contains the architecture and implementation documentation for View-from-CSV v4.5, including audits, callgraphs, and module inventories. It supports rapid onboarding for new developers and provides a clear picture of how to scale the system.

## Documentation Structure

### 📊 Core Documents

- **[`architecture-audit.md`](architecture-audit.md)** - Architecture analysis and mission alignment verification
<!-- loose-ends removed; content consolidated into audits -->
- **[`strong-patterns.md`](strong-patterns.md)** - Standard patterns and improvement recommendations

### 📈 Call Graphs

- **[`callgraphs/main-pipeline-flow.md`](callgraphs/main-pipeline-flow.md)** - Main pipeline execution flow from CLI to final output
- **[`callgraphs/cli-command-structure.md`](callgraphs/cli-command-structure.md)** - CLI command structure and routing
- **[`callgraphs/extraction-options-system.md`](callgraphs/extraction-options-system.md)** - Data extraction and options detection system

### 📋 Data & Inventory

- **[`module-inventory.csv`](module-inventory.csv)** - Complete inventory of all production modules with dependencies and contracts

## Quick Start

### 1. Read the Executive Summary
Start with the **Executive Summary** section in [`architecture-audit.md`](architecture-audit.md) to understand the overall assessment.

### 2. Review Critical Issues
Check [`loose-ends.md`](loose-ends.md) for **CRITICAL** priority items that need immediate attention.

### 3. Understand the Architecture
Review the call graphs in the [`callgraphs/`](callgraphs/) directory to understand data flow and system interactions.

### 4. Plan Improvements
Use [`strong-patterns.md`](strong-patterns.md) to identify patterns to standardize and concrete refactor suggestions.

## Key Summary

### ✅ **Strengths**
- **Modular pipeline architecture** with clear separation of concerns
- **Registry-based module discovery** for zero-configuration extensibility
- **Single-purpose module design** following clean architecture principles
- **Comprehensive data extraction** with confidence scoring
- **Well-defined data contracts** between pipeline steps

### 🚨 **Notable Considerations**
- Maintain selector accuracy as sites evolve
- Monitor selector and site markup drift; adjust profiles promptly

### 📊 **Mission Alignment**
- ✅ **AutoTempest ingestion** - Implemented with Playwright
- ✅ **Per-site scraping** - Implemented with real data collection
- ✅ **Property/option extraction** - Comprehensive modular system
- ✅ **Fair value ranking** - Configurable pricing model
- ✅ **Table view presentation** - Rich library-based display

## Implementation Priority

### **Week 1-2: Critical Fixes**
1. Implement deduplication step
2. Add retry mechanisms for web scraping
3. Implement basic error boundaries

### **Week 3-4: High Priority Features**
1. Implement AutoTempest collector
2. Add data validation schemas
3. Implement environment-specific configuration

### **Month 2: Quality Improvements**
1. Add comprehensive unit tests
2. Implement data quality metrics
3. Add performance monitoring

## Architecture Overview

The 987 v4 system implements a **modular pipeline architecture** with the following components:

```
CLI Layer → Pipeline Orchestration → Data Processing Pipeline → Supporting Systems
    ↓              ↓                        ↓                      ↓
Commands    Step Registry & Runner    Collection→Scraping→     Extractors
Arguments   Dependency Resolution     Transformation→Dedupe→    Options
Routing     Execution Management      Ranking→View            Configuration
                                                            Logging
```

## Data Flow

The pipeline processes data through these stages:

1. **Collection** - AutoTempest search results → listing URLs
2. **Scraping** - Listing URLs → vehicle details with validation
3. **Transformation** - Raw data → extracted properties + options
4. **Deduplication** - Transformed data → unique listings
5. **Ranking** - Deduped data → ranked by total options MSRP
6. **View** - Ranked data → formatted reports and displays

## Technical Stack

- **Language**: Python 3.10+
- **Web Scraping**: Playwright with Chromium (headful mode)
- **Configuration**: TOML with environment variable overrides
- **Data Processing**: Modular pipeline with dependency resolution
- **Display**: Rich library for terminal formatting
- **Storage**: CSV output with timestamped files

## Getting Started (v4.5)

### Prerequisites
- Python 3.10 or higher
- Playwright browser automation
- Required Python packages (see `requirements.txt`)

### Running the Pipeline
```powershell
# Complete pipeline
python -m x987

# Individual steps
python -m x987 collect
python -m x987 scrape
python -m x987 transform
python -m x987 dedupe
python -m x987 rank

# System diagnostics
python -m x987 doctor
```

### Configuration
- Use `x987-config/config.toml` at the repo root (auto-created on setup)
- Modify search URLs and scraping parameters
- Use environment variables for overrides when needed

## Contributing

When adding new functionality:

1. **Follow the single-purpose module pattern**
2. **Use the standardized top-of-file documentation format**
3. **Implement the required interfaces** (BasePipelineStep, BaseExtractor, etc.)
4. **Add comprehensive error handling**
5. **Include confidence scoring for data extraction**
6. **Write unit tests for new modules**

## Support & Questions

For questions about the architecture audit or implementation:

1. Review the relevant documentation sections
2. Check the call graphs for data flow understanding
3. Examine the module inventory for dependencies
4. Refer to the strong patterns document for best practices

## Conclusion

The 987 v4 codebase demonstrates **excellent architectural design** with clear separation of concerns and maintainable structure. While **critical gaps exist** that must be addressed for production readiness, the foundation is **architecturally sound** and ready for enhancement.

With the identified issues resolved, this system will represent a **production-ready vehicle data analysis platform** with **enterprise-grade reliability** and **maintainability**.
