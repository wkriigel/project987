# Data Extraction and Options System Call Graph

## Overview
This call graph shows the modular data extraction and options detection system used in the transformation step.

## Call Graph

```mermaid
graph TD
    A[x987.pipeline.steps.transformation:TransformationStep] --> B[_extract_basic_properties]
    A --> C[_detect_options]
    
    B --> D[x987.extractors:get_unified_extractor]
    D --> E[x987.extractors.unified:UNIFIED_EXTRACTOR]
    
    E --> F[extract_year]
    E --> G[extract_price]
    E --> H[extract_mileage]
    E --> I[extract_model_trim]
    E --> J[extract_colors]
    E --> K[extract_source]
    
    F --> L[x987.extractors.year:YearExtractor]
    G --> M[x987.extractors.price:PriceExtractor]
    H --> N[x987.extractors.mileage:MileageExtractor]
    I --> O[x987.extractors.model_trim:ModelTrimExtractor]
    J --> P[x987.extractors.colors:ColorsExtractor]
    K --> Q[x987.extractors.source:SourceExtractor]
    
    C --> R[x987.options:get_registry]
    R --> S[x987.options.registry:OPTIONS_REGISTRY]
    
    S --> T[get_all_options]
    T --> U[OptionsDetector]
    
    U --> V[transmission.py]
    U --> W[convenience.py]
    U --> X[exterior.py]
    U --> Y[seating.py]
    U --> Z[technology.py]
    U --> AA[performance.py]
    U --> BB[heated_seats.py]
    U --> CC[park_assist.py]
    U --> DD[bi_xenon_headlights.py]
    U --> EE[bose_surround_sound.py]
    U --> FF[pcm_navigation.py]
    U --> GG[sport_seats.py]
    U --> HH[upgraded_wheels.py]
    U --> II[limited_slip_differential.py]
    U --> JJ[pasm.py]
    U --> KK[sport_chrono.py]
    U --> LL[sport_exhaust.py]
    
    V --> MM[is_present]
    V --> NN[get_id]
    V --> OO[get_display]
    V --> PP[get_category]
    V --> QQ[get_value]
    V --> RR[get_confidence]
    
    A --> SS[_create_unified_transformed_csv]
    SS --> TT[Merge properties and options data]
    TT --> UU[Write to CSV file]
```

## Data Flow

### Property Extraction Flow
1. **Input**: Raw text from scraped listings
2. **Processing**: Each extractor processes text independently
3. **Output**: Extracted values with confidence scores
4. **Integration**: Unified extractor combines all results

### Options Detection Flow
1. **Input**: Raw text from scraped listings
2. **Processing**: Each option detector checks for presence
3. **Output**: Detected options with metadata and values
4. **Integration**: Options registry aggregates all results

## Extractor Contracts

### BaseExtractor Interface
```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> ExtractionResult:
        pass
```

### ExtractionResult Structure
```python
@dataclass
class ExtractionResult:
    value: Any
    confidence: float
    metadata: Dict[str, Any]
```

## Options Contracts

### BaseOption Interface
```python
class BaseOption(ABC):
    def is_present(self, text: str) -> bool: ...
    def get_id(self) -> str: ...
    def get_display(self) -> str: ...
    def get_category(self) -> str: ...
    def get_value(self, text: str) -> float: ...
    def get_confidence(self) -> float: ...
```

### Option Categories
- **Transmission**: Manual, Automatic, PDK
- **Convenience**: Comfort access, keyless entry
- **Exterior**: Bi-xenon headlights, sport exhaust
- **Seating**: Sport seats, heated seats
- **Technology**: PCM navigation, Bose audio
- **Performance**: PASM, sport chrono, limited slip differential

## Confidence Scoring

### Property Extraction Confidence
- **High (1.0)**: Clear pattern match with validation
- **Medium (0.7)**: Pattern match with some uncertainty
- **Low (0.3)**: Weak pattern match
- **Zero (0.0)**: No pattern found

### Options Detection Confidence
- **High (1.0)**: Multiple strong indicators present
- **Medium (0.7)**: Single strong indicator
- **Low (0.3)**: Weak or ambiguous indicators

## Error Handling

- **Missing extractors**: Graceful fallback with default values
- **Pattern failures**: Log warnings and continue processing
- **Invalid data**: Mark with low confidence scores
- **Registry errors**: Fall back to basic extraction

## Performance Considerations

- **Parallel processing**: Extractors can run independently
- **Caching**: Option patterns compiled once at startup
- **Memory usage**: Text content processed in streaming fashion
- **Scalability**: Linear scaling with number of listings

## Configuration

- **Extractor patterns**: Configurable regex patterns
- **Option definitions**: Configurable option metadata
- **Confidence thresholds**: Configurable quality filters
- **Fallback values**: Configurable default values

## Integration Points

- **Transformation step**: Main consumer of extraction results
- **Pipeline runner**: Orchestrates extraction execution
- **Configuration system**: Provides extraction parameters
- **Logging system**: Tracks extraction performance and errors
