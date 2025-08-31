# Modular Pipeline Steps System

This directory contains the new modular pipeline system that follows the same "one file per responsibility" approach as the options and extractors systems. Each pipeline step has its own dedicated file with execution logic.

## Architecture

### Individual Step Files

Each pipeline step has its own dedicated file:

- **`collection.py`** - Collects vehicle listing URLs from search sources
- **`scraping.py`** - Scrapes vehicle data from collected URLs  
- **`transformation.py`** - Transforms raw scraped data into normalized format
- **`deduplication.py`** - Removes duplicate vehicle listings
- **`fair_value.py`** - Calculates fair values and deal deltas
- **`ranking.py`** - Ranks vehicle listings by deal delta and other criteria

### Base Classes

- **`base.py`** - Abstract base classes for pipeline steps
  - `BasePipelineStep` - Abstract base class for all steps
  - `StepResult` - Result data class for step execution
  - `StepStatus` - Enum for step execution status

### Registry and Runner

- **`registry.py`** - Automatically discovers all step files and manages dependencies
- **`runner.py`** - Orchestrates the execution of all pipeline steps

## Key Features

### 1. **Automatic Discovery**
The registry automatically finds all step files and creates a unified interface:
```python
from x987.pipeline.steps import get_registry

registry = get_registry()
steps = registry.get_all_steps()
execution_order = registry.get_execution_order()
```

### 2. **Dependency Management**
Each step declares its dependencies, and the system automatically calculates execution order:
```python
def get_dependencies(self) -> List[str]:
    return ["collection"]  # This step depends on collection step
```

### 3. **Configuration Validation**
Steps can declare required configuration and validate it before execution:
```python
def get_required_config(self) -> List[str]:
    return ["search", "scraping"]  # These config keys are required
```

### 4. **Unified Execution Interface**
All steps use the same execution interface:
```python
result = step.execute(config, previous_results, **kwargs)
```

### 5. **Comprehensive Result Tracking**
Each step execution returns detailed results:
```python
@dataclass
class StepResult:
    step_name: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime]
    data: Optional[Any]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

## Usage Examples

### Running the Complete Pipeline
```python
from x987.pipeline.steps import get_pipeline_runner

runner = get_pipeline_runner()
results = runner.run_pipeline(config)
```

### Running a Single Step
```python
runner = get_pipeline_runner()
result = runner.run_single_step("collection", config)
```

### Getting Pipeline Information
```python
runner = get_pipeline_runner()
info = runner.get_pipeline_info()
print(f"Steps: {info['steps']}")
print(f"Execution Order: {info['execution_order']}")
```

### Listing All Steps
```python
runner = get_pipeline_runner()
runner.list_steps()
```

## Adding New Pipeline Steps

To add a new pipeline step:

1. **Create a new file** in this directory (e.g., `new_step.py`)
2. **Inherit from BasePipelineStep**:
```python
from .base import BasePipelineStep, StepResult

class NewStep(BasePipelineStep):
    def get_step_name(self) -> str:
        return "new_step"
    
    def get_description(self) -> str:
        return "Description of what this step does"
    
    def get_dependencies(self) -> List[str]:
        return ["step_name"]  # Dependencies
    
    def get_required_config(self) -> List[str]:
        return ["config_key"]  # Required config
    
    def run_step(self, config, previous_results, **kwargs):
        # Your step logic here
        return result_data
```

3. **Export the step instance**:
```python
NEW_STEP = NewStep()
```

4. **The registry will automatically discover it** on next import!

## Benefits of This Architecture

### 1. **Single Responsibility**
Each file handles exactly one pipeline step, making code easier to understand and maintain.

### 2. **Independent Modification**
You can modify any step without affecting others - just edit the individual file.

### 3. **Automatic Discovery**
No need to manually register steps - just create the file and it's automatically available.

### 4. **Dependency Management**
The system automatically handles step dependencies and execution order.

### 5. **Easy Testing**
Each step can be tested independently by running it in isolation.

### 6. **Clear Interfaces**
All steps use the same interface, making the system predictable and easy to use.

### 7. **Extensibility**
Adding new steps is as simple as creating a new file - no changes to existing code needed.

## Testing

Run the test suite to see the system in action:
```bash
python test_modular_pipeline.py
```

This will demonstrate:
- Automatic step discovery
- Pipeline validation
- Dependency resolution
- Step information display
- Single step execution

## Migration from Old System

The new system is designed to be a drop-in replacement for the old pipeline. The existing functions in `transform.py`, `dedupe.py`, etc. are still used by the individual step files, so no existing functionality is lost.

To migrate:
1. Use the new step system for new development
2. Gradually refactor existing code to use individual steps
3. The old pipeline functions remain available for backward compatibility
