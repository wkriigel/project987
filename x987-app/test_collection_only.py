#!/usr/bin/env python3
"""
Test script for the collection step only

This script tests just the collection step to avoid opening too many browsers
and causing crashes.
"""

from x987.pipeline.steps.runner import PipelineRunner
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Test just the collection step"""
    
    console.print(Panel("[bold cyan]Testing Collection Step Only[/bold cyan]", style="cyan"))
    console.print("This will test just the collection step to avoid browser crashes")
    console.print()
    
    try:
        # Get the pipeline runner
        runner = PipelineRunner()
        
        # Use a minimal config for testing
        config = {
            "search": {
                "urls": [
                    "https://www.autotempest.com/results?make=porsche&model=cayman&year_min=2009&year_max=2012",
                ]
            },
            "collection": {
                "max_urls": 3,  # Just get a few URLs for testing
                "headful": True
            },
            "pipeline": {
                "output_directory": "x987-data/results"
            }
        }
        
        # Run just the collection step
        console.print("🚀 Starting collection step...")
        result = runner.run_single_step("collection", config, headful=True)
        
        if result and result.is_success:
            console.print("✅ Collection step completed successfully!")
            if hasattr(result, 'data') and result.data:
                if 'collection_data' in result.data:
                    listings = result.data['collection_data']
                    console.print(f"📊 Collected {len(listings)} listings")
                    
                    # Show sample listings
                    for i, listing in enumerate(listings[:3]):
                        console.print(f"  {i+1}. {listing.get('title', 'Unknown')}")
                        console.print(f"     Price: {listing.get('price', 'Unknown')}")
                        console.print(f"     Year: {listing.get('year', 'Unknown')}")
                        console.print(f"     Model: {listing.get('model', 'Unknown')}")
                        console.print()
                else:
                    console.print("⚠️ No collection data found in result")
            else:
                console.print("⚠️ No data in result")
        else:
            console.print(f"❌ Collection step failed: {result.error if result else 'Unknown error'}")
        
        console.print("🎯 Test completed!")
        
    except Exception as e:
        console.print(f"❌ Collection test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
