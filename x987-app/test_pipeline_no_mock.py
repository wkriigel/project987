#!/usr/bin/env python3
"""
Test script for the pipeline without mock data

PROVIDES: Testing of pipeline without mock data fallback
DEPENDS: Pipeline modules and Rich library
CONSUMED BY: Development and testing
CONTRACT: Tests pipeline with real scraped data processing
TECH CHOICE: Rich library for pipeline testing output
RISK: Low - test files don't affect production code

This script tests that the pipeline properly processes real scraped data
without falling back to mock data.
"""

from x987.pipeline import run_pipeline_modular
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Test the pipeline without mock data"""
    
    console.print(Panel("[bold cyan]Testing Pipeline Without Mock Data[/bold cyan]", style="cyan"))
    console.print("This will test that the pipeline properly processes real scraped data")
    console.print()
    
    try:
        # Run the modular pipeline
        console.print("🚀 Starting modular pipeline...")
        
        # Use a minimal config for testing
        config = {
            "search": {
                "urls": [
                    "https://www.autotempest.com/results?make=porsche&model=cayman&year_min=2009&year_max=2012",
                ]
            },
            "collection": {
                "max_urls": 5,  # Just get a few URLs for testing
                "headful": True
            },
            "scraping": {
                "timeout_per_page": 30,
                "headful": True
            },
            "fair_value": {
                "base_value_usd": 30500,
                "year_step_usd": 500,
                "s_premium_usd": 7000
            },
            "pipeline": {
                "output_directory": "x987-data/results"
            }
        }
        
        results = run_pipeline_modular(config)
        
        console.print("✅ Pipeline completed successfully!")
        console.print()
        
        # Display results summary
        if results and 'pipeline_results' in results:
            pipeline_results = results['pipeline_results']
            
            # Check each step
            for step_name, result in pipeline_results.items():
                if result.is_success:
                    console.print(f"✅ {step_name}: Success")
                    if hasattr(result, 'data') and result.data:
                        if 'collection_data' in result.data:
                            console.print(f"   📊 Collected {len(result.data['collection_data'])} listings")
                        elif 'scraping_data' in result.data:
                            console.print(f"   📊 Scraped {len(result.data['scraping_data'])} listings")
                        elif 'transformed_data' in result.data:
                            console.print(f"   📊 Transformed {len(result.data['transformed_data'])} listings")
                        elif 'deduped_data' in result.data:
                            console.print(f"   📊 Deduplicated {len(result.data['deduped_data'])} listings")
                else:
                    console.print(f"❌ {step_name}: Failed - {result.error}")
        else:
            console.print("⚠️ No pipeline results available")
        
        console.print("🎯 Test completed!")
        
    except Exception as e:
        console.print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
