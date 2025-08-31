"""
Unified data extraction utilities for all scrapers

PROVIDES: Consistent, robust extraction functions for vehicle data
DEPENDS: Standard library only (re, typing)
CONSUMED BY: All scrapers, profiles, and pipeline modules
CONTRACT: Provides reliable data extraction regardless of source
TECH CHOICE: Regex-based extraction with comprehensive patterns
RISK: Low - extraction logic is centralized and tested
"""

import re
from typing import Optional, Tuple, Dict, Any

# =========================
# MILEAGE EXTRACTION
# =========================

def extract_mileage_unified(text: str) -> Optional[int]:
    """
    Unified mileage extraction - handles all formats and units
    
    Args:
        text: Text containing mileage information
        
    Returns:
        Extracted mileage as integer or None
        
    Examples:
        "142,400 mi." -> 142400
        "142.4k mi" -> 142400
        "mileage: 142,400" -> 142400
        "142,400 ODO" -> 142400
        "142k" -> 142000
    """
    if not text:
        return None
    
    # Comprehensive mileage patterns with units
    patterns = [
        # Standard mileage patterns
        r"(\d[\d,]+)\s*(?:miles?|mi\.?|ODO|odo)\b",  # "142,400 mi." or "142,400 ODO"
        r"mileage\s*:?\s*(\d[\d,]+)",                # "mileage: 142,400"
        # k/K patterns with decimal support
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\s*(?:miles?|mi\.?)\b", # "142.4k mi" or "142.4K mi"
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\b",              # "142.4k" or "142.4K"
        # Odometer patterns
        r"odometer\s*:?\s*(\d[\d,]+)",               # "odometer: 142,400"
        r"(\d[\d,]+)\s*odo",                         # "142,400 odo"
        # Fallback: just numbers (be more careful) - but exclude negative numbers
        r"(?<![-–—])(\d[\d,]+)(?=\s*(?:miles?|mi|k|K|ODO|odo|$))",  # "142,400" followed by units or end (no negative)
    ]
    
    for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                
                # Handle decimal values for k/K patterns
                try:
                    if "k" in text.lower():
                        # Convert decimal k values (e.g., 142.4k -> 142400)
                        value_float = float(value_str.replace(",", ""))
                        value = int(value_float * 1000)
                    else:
                        # Standard integer values
                        value = int(value_str.replace(",", ""))
                    
                    # Sanity check: mileage should be reasonable and positive
                    # Also check if the original text contains negative indicators (but allow dashes in context)
                    if 0 < value <= 999999:
                        # Check for negative numbers, but allow dashes in context like "mi. - highway"
                        text_lower = text.lower()
                        if not (text_lower.startswith("-") or text_lower.startswith("–") or text_lower.startswith("—")):
                            return value
                except ValueError:
                    continue
    
    return None

# =========================
# PRICE EXTRACTION
# =========================

def extract_price_unified(text: str) -> Optional[int]:
    """
    Unified price extraction - handles all price formats
    
    Args:
        text: Text containing price information
        
    Returns:
        Extracted price as integer or None
        
    Examples:
        "$24,000" -> 24000
        "$24.5k" -> 24500
        "Price: $24,000" -> 24000
        "$24,000 - $26,000" -> 24000 (first price)
        "24,000" -> 24000
    """
    if not text:
        return None
    
    # Handle price ranges - take the first price
    if any(separator in text for separator in [" - ", "-", " to ", "–", "—"]):
        # Split on common separators and take first part
        parts = re.split(r"\s*[-–—]\s*|\s+to\s+", text)
        if parts:
            text = parts[0].strip()
    
    # Comprehensive price patterns
    patterns = [
        # Labeled patterns (check these first - most specific)
        r"price\s*:?\s*\$?(\d[\d,]+)",               # "price: $24,000" or "price: 24,000"
        r"asking\s*:?\s*\$?(\d[\d,]+)",              # "asking: $24,000" or "asking: 24,000"
        r"asking\s+(\d[\d,]+)",                       # "asking 24,000"
        # k/K patterns with decimal support
        r"\$(\d+(?:\.\d+)?)\s*(?:k|K)",              # "$24.5k" or "$24K"
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\s*dollars?",     # "24.5k dollars"
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\s*(?:USD|usd)",  # "24.5K USD"
        # Standard price patterns
        r"\$(\d[\d,]+(?:\.\d{2})?)",                 # "$24,000" or "$24,000.50"
        r"(\d[\d,]+)\s*(?:dollars?|USD|usd)",        # "24,000 dollars"
        # Fallback: just numbers (be more careful)
        r"(\d[\d,]+)(?=\s*(?:dollars?|USD|usd|$))", # "24,000" followed by currency or end
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1)
            
            # Handle k/K conversion - only if this pattern actually contains k/K
            if "k" in match.group(0).lower():
                try:
                    price_float = float(price_str) * 1000
                    price_int = int(price_float)
                    # Sanity check: price should be reasonable and positive
                    if 0 < price_int <= 999999:
                        return price_int
                except ValueError:
                    continue
            
            # Standard price conversion
            try:
                # Remove commas and convert to int (ignore cents)
                price_int = int(price_str.replace(",", "").split(".")[0])
                # Sanity check: price should be reasonable and positive
                if 0 < price_int <= 999999:
                    return price_int
            except ValueError:
                continue
    
    return None

# =========================
# COLOR EXTRACTION
# =========================

# Advanced color normalization patterns
_COLOR_CORE = r"(?:Black|White|Gray|Grey|Silver|Red|Blue|Green|Tan|Beige|Brown|Gold|Purple|Burgundy|Yellow|Orange|Ivory|Cream|Pearl|Metallic)"
_COLOR_ADJ = r"(?:[A-Z][a-z]+|Arctic|Meteor|Classic|Carrera|Basalt|Carmine|Aqua|Racing|Guards|Seal|Sand|Sapphire|Slate|Midnight|Jet|Polar|Macadamia|Champagne)"
_COLOR_SPECIAL = r"(?:Macadamia|Carrara|Cognac|Espresso|Mocha|Truffle|Saddle|Chestnut|Havana|Bordeaux|Merlot|Platinum|Titanium)"

_COLOR_PHRASE_RE = re.compile(
    rf"^\s*((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\b"
)

def extract_color_unified(text: str) -> Optional[str]:
    """
    Unified color extraction - handles all color formats
    
    Args:
        text: Text containing color information
        
    Returns:
        Normalized color string or None
        
    Examples:
        "Arctic White" -> "Arctic White"
        "Black Metallic" -> "Black Metallic"
        "Macadamia Interior" -> "Macadamia"
    """
    if not text:
        return None
    
    # Clean the text
    cleaned = str(text).strip()
    if len(cleaned) <= 2:
        return None
    
    # Try advanced pattern matching first
    match = _COLOR_PHRASE_RE.search(cleaned)
    if match:
        return match.group(1)
    
    # Fallback: simple color extraction
    simple_colors = [
        "Black", "White", "Gray", "Grey", "Silver", "Red", "Blue", "Green", 
        "Tan", "Beige", "Brown", "Gold", "Purple", "Burgundy", "Yellow", 
        "Orange", "Ivory", "Cream", "Pearl", "Metallic"
    ]
    
    for color in simple_colors:
        if color.lower() in cleaned.lower():
            return color
    
    return None

def extract_colors_unified(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract both exterior and interior colors from text
    
    Args:
        text: Text containing color information
        
    Returns:
        Tuple of (exterior_color, interior_color)
    """
    if not text:
        return None, None
    
    ext_color = None
    int_color = None
    
    # Strategy 1: Look for labeled color patterns
    ext_match = re.search(r'Exterior\s*Color:\s*([^,\n]+?)(?=\s*Interior|\s*Engine|\s*Drivetrain|$)', text, re.I)
    int_match = re.search(r'Interior\s*Color:\s*([^,\n]+?)(?=\s*Engine|\s*Drivetrain|$)', text, re.I)
    
    if ext_match:
        ext_color = extract_color_unified(ext_match.group(1).strip())
    if int_match:
        int_color = extract_color_unified(int_match.group(1).strip())
    
    # Strategy 2: Look for "Exterior + Interior" patterns
    if not ext_color or not int_color:
        pattern1 = rf"((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+Exterior\s+((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+Interior"
        match = re.search(pattern1, text, re.I)
        if match:
            if not ext_color:
                ext_color = extract_color_unified(match.group(1))
            if not int_color:
                int_color = extract_color_unified(match.group(2))
    
    # Strategy 3: Look for "on/over" patterns
    if not ext_color or not int_color:
        pattern2 = rf"((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+(?:on|over)\s+((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})"
        match = re.search(pattern2, text, re.I)
        if match:
            if not ext_color:
                ext_color = extract_color_unified(match.group(1))
            if not int_color:
                int_color = extract_color_unified(match.group(2))
    
    return ext_color, int_color

# =========================
# TRANSMISSION EXTRACTION
# =========================

def extract_transmission_unified(text: str) -> Optional[str]:
    """
    Unified transmission extraction - handles all transmission formats
    
    Args:
        text: Text containing transmission information
        
    Returns:
        Normalized transmission string or None
        
    Examples:
        "PDK" -> "PDK"
        "Automatic" -> "Automatic"
        "Manual" -> "Manual"
        "Tiptronic" -> "Tiptronic"
    """
    if not text:
        return None
    
    text_lower = text.lower().strip()
    
    # Porsche-specific transmissions
    if "pdk" in text_lower:
        return "PDK"
    elif "tiptronic" in text_lower:
        return "Tiptronic"
    
    # Standard transmissions
    elif any(term in text_lower for term in ["automatic", "auto"]):
        return "Automatic"
    elif "manual" in text_lower:
        return "Manual"
    
    return None

# =========================
# VIN EXTRACTION
# =========================

def extract_vin_unified(text: str) -> Optional[str]:
    """
    Unified VIN extraction - handles all VIN formats
    
    Args:
        text: Text containing VIN information
        
    Returns:
        Extracted VIN string or None
        
    Examples:
        "VIN: WP0AB2A91FS123456" -> "WP0AB2A91FS123456"
        "WP0AB2A91FS123456" -> "WP0AB2A91FS123456"
    """
    if not text:
        return None
    
    # VIN pattern: 17 alphanumeric characters (excluding I, O, Q) - standard VIN length
    vin_pattern = r'[A-HJ-NPR-Z0-9]{17}'
    
    # Look for VIN with label
    labeled_match = re.search(r'VIN\s*:?\s*(' + vin_pattern + ')', text, re.I)
    if labeled_match:
        return labeled_match.group(1).strip()
    
    # Look for standalone VIN
    standalone_match = re.search(r'\b(' + vin_pattern + r')\b', text)
    if standalone_match:
        return standalone_match.group(1).strip()
    
    return None

# =========================
# YEAR/MODEL/TRIM EXTRACTION
# =========================

def extract_vehicle_info_unified(text: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Extract year, model, and trim from vehicle title/text
    
    Args:
        text: Text containing vehicle information
        
    Returns:
        Tuple of (year, model, trim)
    """
    if not text:
        return None, None, None
    
    year = None
    model = None
    trim = None
    
    # Extract year
    year_match = re.search(r'\b(20\d\d)\b', text)
    if year_match:
        year = int(year_match.group(1))
    
    # Extract Porsche model
    model_match = re.search(r'\b(Cayman|Boxster)\b', text, re.I)
    if model_match:
        model = model_match.group(1).title()
    
    # Extract trim (Porsche-specific logic)
    if model:
        # Special trims
        if re.search(r'\bCayman\s+R\b', text, re.I):
            trim = "R"
        elif re.search(r'\bBoxster\s+Spyder\b', text, re.I):
            trim = "Spyder"
        elif re.search(r'\bBlack\s+Edition\b', text, re.I):
            trim = "Black Edition"
        # Explicit S in title
        elif re.search(r'\b(Cayman|Boxster)\s+S\b', text, re.I):
            trim = "S"
        # Explicit Base hints
        elif re.search(r'\bCayman\s+Base\b', text, re.I):
            trim = "Base"
        # Default to Base when title is neutral
        else:
            trim = "Base"
    
    return year, model, trim

# =========================
# UTILITY FUNCTIONS
# =========================

def clean_text_unified(text: str) -> str:
    """
    Unified text cleaning - removes extra whitespace and normalizes
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', str(text))
    
    # Strip leading/trailing whitespace
    return cleaned.strip()

def none_if_na_unified(text: str) -> Optional[str]:
    """
    Convert N/A values to None
    
    Args:
        text: Text to check
        
    Returns:
        Text or None if N/A
    """
    if not text:
        return None
    
    t = re.sub(r"\s+", "", str(text)).lower()
    if t in {"-", "–", "—", "n/a", "na", "notspecified", "unknown", "tbd"}:
        return None
    
    return str(text).strip()
