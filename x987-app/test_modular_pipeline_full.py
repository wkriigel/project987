#!/usr/bin/env python3
"""
Test script for the full modular pipeline

This script runs the complete modular pipeline to verify that our
options architecture is properly integrated and working.
"""

from x987.pipeline import run_pipeline_modular
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    """Run the full modular pipeline"""
    
    console.print(Panel("[bold cyan]Testing Full Modular Pipeline[/bold cyan]", style="cyan"))
    console.print("This will run the complete pipeline using our options architecture")
    console.print()
    
    try:
        # Run the modular pipeline
        console.print("🚀 Starting modular pipeline...")
        
        # Use a minimal config for testing
        config = {
            "search": {
                "urls": [
                    "https://www.autotempest.com/results?make=porsche&model=cayman&year_min=2009&year_max=2012",
                    "https://www.autotempest.com/results?make=porsche&model=boxster&year_min=2009&year_max=2012"
                ]
            },
            "collection": {
                "max_urls": 5,  # Just get a few URLs for testing
                "headful": True
            },
            "scraping": {
                "timeout_per_page": 30,
                "headful": True
            }
        }
        
        results = run_pipeline_modular(config)
        
        console.print("✅ Modular pipeline completed successfully!")
        console.print()
        
        # Display results summary
        if results and 'ranking' in results:
            ranking_result = results['ranking']
            if hasattr(ranking_result, 'data') and ranking_result.data:
                listings = ranking_result.data.get('ranked_listings', [])
                console.print(f"📊 Pipeline produced {len(listings)} ranked listings")
                console.print()
                
                # Show sample listings to verify options are working
                if listings:
                    console.print("🔍 Sample listings with options:")
                    for i, listing in enumerate(listings[:3]):
                        if hasattr(listing, 'options_summary') and listing.options_summary:
                            summary = listing.options_summary
                            if 'by_category' in summary and summary['by_category']:
                                console.print(f"  Listing {i+1}: {len(summary['by_category'])} option categories")
                                for category, data in summary['by_category'].items():
                                    if data['options']:
                                        console.print(f"    {category}: {', '.join(data['options'][:3])}")
                                        console.print(f"      Total value: ${data['value']:,}")
                        elif hasattr(listing, 'options_detected') and listing.options_detected:
                            console.print(f"  Listing {i+1}: {len(listing.options_detected)} legacy options")
                            console.print(f"    Options: {', '.join(listing.options_detected[:5])}")
                        else:
                            console.print(f"  Listing {i+1}: No options detected")
                        
                        console.print()
                else:
                    console.print("⚠️ No listings were produced by the pipeline")
            else:
                console.print("⚠️ Ranking step didn't produce expected data structure")
        else:
            console.print("⚠️ Pipeline didn't complete the ranking step")
        
        console.print("🎯 Test completed!")
        
    except Exception as e:
        console.print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
