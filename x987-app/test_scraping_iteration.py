#!/usr/bin/env python3
"""
Test script for iterating on cars.com scraping quality

PROVIDES: Testing of scraping iteration and quality improvement
DEPENDS: Sample tester and extractor modules
CONSUMED BY: Development and testing
CONTRACT: Tests scraping pipeline iteration for quality improvement
TECH CHOICE: Sample-based testing for scraping validation
RISK: Low - test files don't affect production code

This script simulates the actual scraping pipeline to show:
1. What data we're currently extracting
2. The CSV row format we're generating
3. Areas for improvement
"""

import sys
import os
from pathlib import Path

# Add the x987 package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_current_scraping():
    """Test the current scraping implementation against our sample"""
    print("=== Testing Current Scraping Implementation ===")
    
    try:
        from x987.pipeline.sample_tester import SampleTester
        from x987.pipeline.sample_extractor import SampleExtractor
        
        # Create testers
        sample_tester = SampleTester({})
        sample_extractor = SampleExtractor({})
        
        # Test against our cars.com sample
        print("Testing against cars.com sample...")
        results = sample_tester.test_source_sample("cars_com")
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return False
        
        # Extract the data we would get from scraping
        extracted_data = extract_data_from_sample_results(results)
        
        # Display the extracted data
        print("\n--- Extracted Data ---")
        for key, value in extracted_data.items():
            print(f"  {key}: {value}")
        
        # Generate CSV row
        csv_row = generate_csv_row(extracted_data)
        print(f"\n--- CSV Row Output ---")
        print(f"  {csv_row}")
        
        # Analyze data quality
        analyze_data_quality(extracted_data)
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def extract_data_from_sample_results(results):
    """Extract the data we would get from actual scraping"""
    data = {
        "source": "cars.com",
        "listing_url": "https://example.com/test",
        "title": "",
        "year": None,
        "model": "",
        "trim": "",
        "transmission": "",
        "mileage": None,
        "price": None,
        "exterior_color": "",
        "interior_color": "",
        "vin": "",
        "location": ""
    }
    
    # Extract title
    title_tests = results.get("extraction_tests", {}).get("title", {})
    print(f"DEBUG: Title tests: {title_tests}")
    
    if title_tests.get("best_result"):
        best_selector = title_tests["best_result"]
        title_text = title_tests["techniques"][best_selector]["text"]
        data["title"] = title_text
        
        print(f"DEBUG: Title text: '{title_text}'")
        
        # Parse year, model, trim from title
        year, model, trim = parse_title_components(title_text)
        print(f"DEBUG: Parsed title - Year: {year}, Model: {model}, Trim: {trim}")
        
        data["year"] = year
        data["model"] = model
        data["trim"] = trim
    else:
        print(f"DEBUG: No best_result found in title_tests")
    
    # Extract mileage
    mileage_tests = results.get("extraction_tests", {}).get("fields", {}).get("mileage", {})
    if mileage_tests.get("found"):
        data["mileage"] = mileage_tests["value"]
    
    # Extract VIN
    vin_tests = results.get("extraction_tests", {}).get("fields", {}).get("vin", {})
    if vin_tests.get("found"):
        data["vin"] = vin_tests["value"]
    
    # Extract transmission
    transmission_tests = results.get("extraction_tests", {}).get("fields", {}).get("transmission", {})
    print(f"DEBUG: Transmission tests: {transmission_tests}")
    
    if transmission_tests.get("found"):
        # Get the best transmission value
        for selector, technique in transmission_tests.get("techniques", {}).items():
            if technique.get("value"):
                data["transmission"] = technique["value"]
                print(f"DEBUG: Found transmission: {technique['value']}")
                break
    else:
        print(f"DEBUG: No transmission found")
    
    # Extract price
    price_tests = results.get("extraction_tests", {}).get("fields", {}).get("price", {})
    if price_tests.get("found"):
        data["price"] = price_tests.get("value")
    
    # Extract colors
    color_tests = results.get("extraction_tests", {}).get("fields", {}).get("colors", {})
    if color_tests.get("found"):
        data["exterior_color"] = color_tests.get("exterior")
        data["interior_color"] = color_tests.get("interior")
    
    # Extract colors and other fields from overview content (fallback)
    overview_content = results.get("extraction_tests", {}).get("overview", {}).get("content", "")
    extract_colors_from_overview(data, overview_content)
    
    return data

def parse_title_components(title):
    """Parse year, model, trim from vehicle title using unified extractor"""
    try:
        from x987.utils.extractors import extract_vehicle_info_unified
        print(f"DEBUG: About to call extract_vehicle_info_unified with: '{title}'")
        result = extract_vehicle_info_unified(title)
        print(f"DEBUG: extract_vehicle_info_unified returned: {result}")
        year, model, trim = result
        print(f"DEBUG: Unpacked - Year: {year}, Model: {model}, Trim: {trim}")
        return year, model, trim
    except Exception as e:
        print(f"DEBUG: Exception in parse_title_components: {e}")
        # Fallback to basic parsing if unified extractor fails
        import re
        
        year = None
        model = ""
        trim = ""
        
        # Extract year
        year_match = re.search(r'\b(20[0-9]{2})\b', title)
        if year_match:
            year = int(year_match.group(1))
        
        # Extract model (Porsche + model number)
        model_match = re.search(r'\b(Porsche\s+[0-9]+(?:\.[0-9]+)?)\b', title, re.I)
        if model_match:
            model = model_match.group(1)
        
        return year, model, trim

def extract_colors_from_overview(data, overview_content):
    """Extract color information from overview content using unified extractors"""
    try:
        from x987.utils.extractors import extract_color_unified, extract_price_unified
        
        # Look for exterior color - more specific pattern
        ext_color_match = re.search(r'Exterior Color:\s*([^,\n]+?)(?=\s*Interior|\s*Engine|\s*Drivetrain|$)', overview_content, re.I)
        if ext_color_match:
            exterior_text = ext_color_match.group(1).strip()
            data["exterior_color"] = extract_color_unified(exterior_text)
        
        # Look for interior color - more specific pattern  
        int_color_match = re.search(r'Interior Color:\s*([^,\n]+?)(?=\s*Engine|\s*Drivetrain|$)', overview_content, re.I)
        if int_color_match:
            interior_text = int_color_match.group(1).strip()
            data["interior_color"] = extract_color_unified(interior_text)
        
        # Look for price - more specific pattern
        price_match = re.search(r'Price:\s*\$([\d,]+)', overview_content)
        if price_match:
            price_text = f"${price_match.group(1)}"
            data["price"] = extract_price_unified(price_text)
    except:
        # Fallback to basic extraction if unified extractors fail
        import re
        
        # Look for exterior color - more specific pattern
        ext_color_match = re.search(r'Exterior Color:\s*([^,\n]+?)(?=\s*Interior|\s*Engine|\s*Drivetrain|$)', overview_content, re.I)
        if ext_color_match:
            data["exterior_color"] = ext_color_match.group(1).strip()
        
        # Look for interior color - more specific pattern  
        int_color_match = re.search(r'Interior Color:\s*([^,\n]+?)(?=\s*Engine|\s*Drivetrain|$)', overview_content, re.I)
        if int_color_match:
            data["interior_color"] = int_color_match.group(1).strip()
        
        # Look for price - more specific pattern
        price_match = re.search(r'Price:\s*\$([\d,]+)', overview_content)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            data["price"] = int(price_str)

def generate_csv_row(data):
    """Generate CSV row from extracted data"""
    csv_fields = [
        data["source"],
        str(data["year"]) if data["year"] else "",
        data["model"] or "",
        data["trim"] or "",
        str(data["price"]) if data["price"] else "",
        str(data["mileage"]) if data["mileage"] else "",
        data["transmission"] or "",
        data["vin"] or "",
        data["exterior_color"] or "",
        data["interior_color"] or ""
    ]
    
    return ",".join(csv_fields)

def analyze_data_quality(data):
    """Analyze the quality of extracted data"""
    print(f"\n--- Data Quality Analysis ---")
    
    # Check completeness
    required_fields = ["year", "model", "trim", "mileage", "transmission", "vin"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        print(f"  ⚠️  Missing required fields: {', '.join(missing_fields)}")
    else:
        print(f"  ✅ All required fields present")
    
    # Check data quality
    quality_issues = []
    
    if data["year"] and (data["year"] < 1990 or data["year"] > 2030):
        quality_issues.append("Year seems unrealistic")
    
    if data["mileage"] and data["mileage"] > 500000:
        quality_issues.append("Mileage seems unrealistic")
    
    if data["price"] and data["price"] > 1000000:
        quality_issues.append("Price seems unrealistic")
    
    if data["transmission"] and len(data["transmission"]) < 3:
        quality_issues.append("Transmission value seems too short")
    
    if quality_issues:
        print(f"  ⚠️  Quality issues: {', '.join(quality_issues)}")
    else:
        print(f"  ✅ Data quality looks good")
    
    # Calculate completeness score
    total_fields = len(required_fields)
    present_fields = len([f for f in required_fields if data.get(f)])
    completeness = (present_fields / total_fields) * 100
    
    print(f"  📊 Data completeness: {completeness:.1f}% ({present_fields}/{total_fields})")

def suggest_improvements(data):
    """Suggest improvements based on current data"""
    print(f"\n--- Improvement Suggestions ---")
    
    suggestions = []
    
    if not data["year"]:
        suggestions.append("Improve year extraction from title")
    
    if not data["model"]:
        suggestions.append("Improve model extraction from title")
    
    if not data["trim"]:
        suggestions.append("Improve trim extraction from title")
    
    if not data["transmission"]:
        suggestions.append("Improve transmission extraction - current selectors only find label")
    
    if not data["exterior_color"]:
        suggestions.append("Improve color extraction from overview section")
    
    if not data["price"]:
        suggestions.append("Improve price extraction from overview section")
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("  ✅ No immediate improvements needed")

def main():
    """Run the scraping iteration test"""
    print("Testing x987 Cars.com Scraping Iteration")
    print("=" * 50)
    
    try:
        success = test_current_scraping()
        
        if success:
            print(f"\n=== Test Complete ===")
            print("Use this output to iterate on scraping quality.")
            print("Next steps:")
            print("1. Address any missing fields")
            print("2. Improve data quality issues")
            print("3. Test against real cars.com pages")
            print("4. Integrate improvements into main pipeline")
        else:
            print(f"\n=== Test Failed ===")
            print("Check the error messages above.")
        
        return success
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
