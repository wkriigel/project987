"""
CSV input/output utilities for the x987 application

PROVIDES: CSV reading, writing, and validation for vehicle listings
DEPENDS: schema, utils.io
CONSUMED BY: Pipeline modules and CLI
CONTRACT: Handles CSV format conversion and validation
TECH CHOICE: Standard CSV module with pandas-like functionality
RISK: Low - standard CSV operations
TODO(NEXT): Add Excel export support
"""

import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..schema import NormalizedListing, ListingData
from .io import ensure_directory_exists, create_safe_filename
from .log import get_logger

logger = get_logger("utils.csv_io")

# CSV field mappings for input/output
CSV_FIELDS = {
    "input": [
        "source", "listing_url", "model", "trim", "year", "transmission_norm", 
        "mileage", "price_usd", "exterior_color", "interior_color", 
        "raw_options", "vin", "location"
    ],
    "output": [
        "rank", "source", "listing_url", "model", "trim", "year", 
        "transmission_norm", "mileage", "price_usd", "fair_value_usd", 
        "deal_delta_usd", "exterior_color", "interior_color", 
        "color_ext_bucket", "color_int_bucket", "raw_options", 
        "options_value", "vin", "location", "timestamp_run_id"
    ]
}

def read_csv_input(filepath: str) -> List[Dict[str, Any]]:
    """
    Read CSV input file with vehicle listing data
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        List of dictionaries with vehicle data
    """
    try:
        if not os.path.exists(filepath):
            logger.warning(f"CSV file not found: {filepath}")
            return []
        
        listings = []
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Validate required fields
            required_fields = ["source", "listing_url"]
            if not all(field in reader.fieldnames for field in required_fields):
                logger.error(f"CSV missing required fields: {required_fields}")
                return []
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Clean and validate row data
                    cleaned_row = {}
                    for field in CSV_FIELDS["input"]:
                        value = row.get(field, "")
                        if value and value.strip():
                            cleaned_row[field] = value.strip()
                        else:
                            cleaned_row[field] = None
                    
                    # Clean mode: remove noisy per-row debug prints
                    
                    # Convert numeric fields
                    for field in ["year", "mileage", "price_usd"]:
                        if cleaned_row.get(field):
                            try:
                                cleaned_row[field] = int(str(cleaned_row[field]).replace(",", "").replace("$", ""))
                            except (ValueError, TypeError):
                                cleaned_row[field] = None
                    
                    listings.append(cleaned_row)
                    
                except Exception as e:
                    logger.warning(f"Error processing row {row_num}: {e}")
                    continue
        
        logger.info(f"Read {len(listings)} listings from {filepath}")
        return listings
        
    except Exception as e:
        logger.error(f"Error reading CSV file {filepath}: {e}")
        return []

def write_csv_output(listings: List[NormalizedListing], output_dir: str, filename: Optional[str] = None) -> str:
    """
    Write normalized listings to CSV output file
    
    Args:
        listings: List of normalized listings
        output_dir: Output directory path
        filename: Optional filename (generates timestamped name if None)
        
    Returns:
        Path to written CSV file
    """
    try:
        ensure_directory_exists(output_dir)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"x987_results_{timestamp}.csv"
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_FIELDS["output"])
            writer.writeheader()
            
            for i, listing in enumerate(listings, 1):
                row = {
                    "rank": i,
                    "source": listing.source,
                    "listing_url": listing.listing_url,
                    "model": listing.model,
                    "trim": listing.trim,
                    "year": listing.year,
                    "transmission_norm": listing.transmission_norm,
                    "mileage": listing.mileage,
                    "price_usd": listing.price_usd,
                    "fair_value_usd": listing.fair_value_usd,
                    "deal_delta_usd": listing.deal_delta_usd,
                    "exterior_color": listing.exterior_color,
                    "interior_color": listing.interior_color,
                    "color_ext_bucket": listing.color_ext_bucket,
                    "color_int_bucket": listing.color_int_bucket,
                    "raw_options": listing.raw_options,
                    "options_value": listing.options_value,
                    "vin": listing.vin,
                    "location": listing.location,
                    "timestamp_run_id": listing.timestamp_run_id
                }
                writer.writerow(row)
        
        logger.info(f"Wrote {len(listings)} listings to {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error writing CSV file: {e}")
        return ""

def load_manual_csvs(input_dir: str) -> List[Dict[str, Any]]:
    """
    Load all manual CSV files from input directory
    
    Args:
        input_dir: Directory containing manual CSV files
        
    Returns:
        List of all listings from manual CSV files
    """
    try:
        if not os.path.exists(input_dir):
            logger.warning(f"Manual CSV input directory not found: {input_dir}")
            return []
        
        all_listings = []
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.csv'):
                filepath = os.path.join(input_dir, filename)
                logger.info(f"Loading manual CSV: {filename}")
                
                listings = read_csv_input(filepath)
                all_listings.extend(listings)
        
        logger.info(f"Loaded {len(all_listings)} total listings from manual CSV files")
        return all_listings
        
    except Exception as e:
        logger.error(f"Error loading manual CSV files: {e}")
        return []

def save_results_to_csv(listings: List[NormalizedListing], config) -> str:
    """
    Save pipeline results to CSV file
    
    Args:
        listings: List of ranked listings
        config: Configuration manager
        
    Returns:
        Path to saved CSV file
    """
    try:
        # Get output directory via config manager helper
        from x987.config import get_data_dir
        output_dir = str(get_data_dir())
        csv_dir = os.path.join(output_dir, "results")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"x987_results_{timestamp}.csv"
        
        # Write CSV
        filepath = write_csv_output(listings, csv_dir, filename)
        
        if filepath:
            logger.info(f"Results saved to: {filepath}")
            return filepath
        else:
            logger.error("Failed to save results to CSV")
            return ""
            
    except Exception as e:
        logger.error(f"Error saving results to CSV: {e}")
        return ""
