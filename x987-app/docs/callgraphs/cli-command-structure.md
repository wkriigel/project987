# CLI Command Structure Call Graph

## Overview
This call graph shows the CLI command structure and routing from argument parsing to individual command execution.

## Call Graph

```mermaid
graph TD
    A[python -m x987 <command>] --> B[x987.__main__:main]
    B --> C[x987.cli.main:main]
    
    C --> D[argparse.ArgumentParser]
    D --> E[Command Routing Dictionary]
    
    E --> F[cmd_pipeline]
    E --> G[cmd_collect]
    E --> H[cmd_scrape]
    E --> I[cmd_transform]
    E --> J[cmd_dedupe]
    E --> K[cmd_fair_value]
    E --> L[cmd_rank]
    E --> M[cmd_view_step]
    E --> N[cmd_info]
    E --> O[cmd_config]
    E --> P[cmd_doctor]
    
    F --> Q[x987.pipeline:get_pipeline_runner]
    Q --> R[runner.run_pipeline]
    
    G --> S[x987.pipeline:get_pipeline_runner]
    S --> T[runner.run_single_step:collection]
    
    H --> U[x987.pipeline:get_pipeline_runner]
    U --> V[runner.run_single_step:scraping]
    
    I --> W[x987.pipeline:get_pipeline_runner]
    W --> X[runner.run_single_step:transformation]
    
    J --> Y[x987.pipeline:get_pipeline_runner]
    Y --> Z[runner.run_single_step:deduplication]
    
    K --> AA[x987.pipeline:get_pipeline_runner]
    AA --> BB[runner.run_single_step:fair_value]
    
    L --> CC[x987.pipeline:get_pipeline_runner]
    CC --> DD[runner.run_single_step:ranking]
    
    M --> EE[x987.pipeline.steps.view:VIEW_STEP]
    
    N --> GG[x987.pipeline:get_pipeline_runner]
    GG --> HH[runner.get_pipeline_info]
    
    O --> II[x987.config:get_config]
    II --> JJ[config.get_config_summary]
    
    P --> KK[x987.doctor:run_doctor]
    KK --> LL[System diagnostics execution]
    
    C --> MM[setup_logging]
    C --> NN[Error handling & exit codes]
```

## Command Details

### Pipeline Commands
- **`pipeline`**: Runs complete pipeline end-to-end
- **`collect`**: Runs only collection step
- **`scrape`**: Runs only scraping step  
- **`transform`**: Runs only transformation step
- **`dedupe`**: Runs only deduplication step
- **`fair_value`**: Runs only fair value calculation
- **`rank`**: Runs only ranking step

### Utility Commands
- **`view-step`**: Displays the final ranked view (Enhanced View) from the latest results
- **`info`**: Shows pipeline information and step details
- **`config`**: Shows configuration information
- **`doctor`**: Runs system diagnostics

## Common Dependencies

All commands depend on:
- `x987.config:get_config` - Configuration management
- `x987.utils.log:setup_logging` - Logging setup
- `x987.pipeline:get_pipeline_runner` - Pipeline orchestration

## Error Handling

- **KeyboardInterrupt**: Graceful cancellation with exit code 130
- **Command failures**: Return appropriate exit codes (0=success, 1=failure)
- **Unexpected errors**: Log error details and exit with code 1
- **Verbose mode**: Show full traceback for debugging

## Command Arguments

### Global Arguments
- `--headful`: Use headful mode for browser automation (default: True)
- `--verbose, -v`: Enable verbose logging

### Command-Specific Arguments
- `command`: Required command to execute (choices from command list)

## Exit Codes

- **0**: Success
- **1**: Command failure or unexpected error
- **130**: Keyboard interrupt (Ctrl+C)

## Logging

- **Default**: Info level logging
- **Verbose**: Debug level logging with full tracebacks
- **File logging**: Configured through `x987.utils.log:setup_logging`

## Configuration

- **Config file**: Loaded from TOML configuration
- **Environment variables**: Override config file values
- **Validation**: Configuration validated before use
- **Defaults**: Sensible defaults for all required values
