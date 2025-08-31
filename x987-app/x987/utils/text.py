"""
Text utilities for View-from-CSV

PROVIDES: Text processing, cleaning, and normalization functions
DEPENDS: Standard library only
CONSUMED BY: Scraping and normalization modules
CONTRACT: Provides consistent text processing across the application
TECH CHOICE: Standard library with regex for pattern matching
RISK: Low - text processing is generally safe
TODO(NEXT): Add more text normalization patterns
"""

import re
from typing import Optional, List, Dict, Any
from unicodedata import normalize

# =========================
# TEXT CLEANING
# =========================

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and normalizing unicode
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = normalize('NFKC', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def extract_number(text: str) -> Optional[int]:
    """
    Extract numeric value from text
    
    Args:
        text: Text containing a number
        
    Returns:
        Extracted integer or None if no number found
    """
    if not text:
        return None
    
    # Find first number in text
    match = re.search(r'(\d{1,3}(?:,\d{3})*)', text.replace(',', ''))
    if match:
        return int(match.group(1))
    
    return None

def extract_price(text: str) -> Optional[int]:
    """
    Extract price from text, handling currency symbols and formatting
    
    Args:
        text: Text containing a price
        
    Returns:
        Extracted price in cents or None if no price found
    """
    if not text:
        return None
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[\$£€¥,]', '', text)
    
    # Find price pattern (numbers with optional decimal)
    match = re.search(r'(\d+(?:\.\d{2})?)', cleaned)
    if match:
        price_str = match.group(1)
        try:
            # Convert to integer (cents)
            price_float = float(price_str)
            return int(price_float * 100)
        except ValueError:
            pass
    
    return None

def extract_mileage(text: str) -> Optional[int]:
    """
    Extract mileage from text, handling various formats including commas
    
    Args:
        text: Text containing mileage information
        
    Returns:
        Extracted mileage or None if no mileage found
    """
    if not text:
        return None
    
    # Remove common mileage indicators
    cleaned = re.sub(r'\b(miles?|mi|k|km)\b', '', text, flags=re.IGNORECASE)
    
    # Find number pattern - improved to handle any comma placement
    match = re.search(r'(\d[\d,]+)', cleaned)
    if match:
        # Remove commas and convert to integer
        mileage_str = match.group(1).replace(',', '')
        try:
            return int(mileage_str)
        except ValueError:
            pass
    
    return None

# =========================
# TEXT NORMALIZATION
# =========================

def normalize_transmission(text: str) -> str:
    """
    Normalize transmission text to standard format
    
    Args:
        text: Raw transmission text
        
    Returns:
        Normalized transmission string
    """
    if not text:
        return "Unknown"
    
    text_lower = text.lower()
    
    # Automatic transmissions
    if any(term in text_lower for term in ["pdk", "automatic", "tiptronic", "auto"]):
        return "Automatic"
    
    # Manual transmissions
    elif "manual" in text_lower:
        return "Manual"
    
    else:
        return "Unknown"

# Advanced color normalization patterns from idea.txt
_COLOR_CORE = r"(?:Black|White|Gray|Grey|Silver|Red|Blue|Green|Tan|Beige|Brown|Gold|Purple|Burgundy|Yellow|Orange|Ivory|Cream|Pearl|Metallic)"
_COLOR_ADJ = r"(?:[A-Z][a-z]+|Arctic|Meteor|Classic|Carrera|Basalt|Carmine|Aqua|Racing|Guards|Seal|Sand|Sapphire|Slate|Midnight|Jet|Polar|Macadamia|Champagne)"
# Special interior colors that don't follow the standard pattern
_COLOR_SPECIAL = r"(?:Macadamia|Carrara|Cognac|Espresso|Mocha|Truffle|Saddle|Chestnut|Havana|Cognac|Bordeaux|Merlot|Champagne|Platinum|Titanium)"
_COLOR_PHRASE_RE = re.compile(
    rf"^\s*((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\b"
)

def clean_color(val: str | None) -> str | None:
    """
    Clean and validate color values
    
    Args:
        val: Raw color value
        
    Returns:
        Cleaned color string or None if invalid
    """
    if not val:
        return None
    s = str(val).strip()
    if len(s) <= 2:
        return None
    return s

def none_if_na(s: str | None) -> str | None:
    """
    Check if string represents N/A or similar and return None if so
    
    Args:
        s: String to check
        
    Returns:
        Original string or None if N/A equivalent
    """
    if not s:
        return None
    t = re.sub(r"\s+", "", s).lower()
    if t in {"-", "–", "—", "n/a", "na", "notspecified"}:
        return None
    return s.strip()

def normalize_color_phrase(s: str | None) -> str | None:
    """
    Normalize color phrases using advanced patterns
    
    Args:
        s: Raw color text
        
    Returns:
        Normalized color phrase or None if invalid
    """
    if not s:
        return None
    m = _COLOR_PHRASE_RE.search(s)
    return m.group(1) if m else None

def normalize_color(text: str) -> str:
    """
    Normalize color text and categorize as monochrome or color
    
    Args:
        text: Raw color text
        
    Returns:
        Color category: "Monochrome", "Color", or "Unknown"
    """
    if not text:
        return "Unknown"
    
    # First try to normalize the color phrase
    normalized = normalize_color_phrase(text)
    if normalized:
        text = normalized
    
    text_lower = text.lower()
    
    # Monochrome colors
    monochrome_terms = ["white", "black", "gray", "grey", "silver"]
    if any(term in text_lower for term in monochrome_terms):
        return "Monochrome"
    
    # Color colors
    else:
        return "Color"

def extract_colors_from_text(body_text: str) -> tuple[str | None, str | None]:
    """
    Extract exterior and interior colors from text using multiple fallback strategies
    
    Args:
        body_text: Full page text content
        
    Returns:
        Tuple of (exterior_color, interior_color)
    """
    ext_color = None
    int_color = None
    
    # Strategy 1: Look for labeled color patterns (flexible - handles both "Exterior:" and "Exterior color:")
    ext_match = re.search(r"Exterior\s*(?:color\s*)?:\s*([A-Za-z \-]+)", body_text, re.I)
    int_match = re.search(r"Interior\s*(?:color\s*)?:\s*([A-Za-z \-]+)", body_text, re.I)
    
    if ext_match:
        ext_color = normalize_color_phrase(clean_color(ext_match.group(1)))
    if int_match:
        int_color = normalize_color_phrase(clean_color(int_match.group(1)))
    
    # Strategy 2: Look for "Exterior + Interior" patterns
    if not ext_color or not int_color:
        pattern1 = rf"((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+Exterior\s+((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+Interior"
        match = re.search(pattern1, body_text, re.I)
        if match:
            if not ext_color:
                ext_color = normalize_color_phrase(match.group(1))
            if not int_color:
                int_color = normalize_color_phrase(match.group(2))
    
    # Strategy 3: Look for "on/over" patterns
    if not ext_color or not int_color:
        pattern2 = rf"((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})\s+(?:on|over)\s+((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?|{_COLOR_SPECIAL})"
        match = re.search(pattern2, body_text, re.I)
        if match:
            if not ext_color:
                ext_color = normalize_color_phrase(match.group(1))
            if not int_color:
                int_color = normalize_color_phrase(match.group(2))
    
    return ext_color, int_color

def normalize_model_trim(year: Optional[int], model: str, trim: str) -> str:
    """
    Normalize and format model/trim combination
    
    Args:
        year: Vehicle year
        model: Vehicle model (Cayman/Boxster)
        trim: Vehicle trim
        
    Returns:
        Formatted model string
    """
    if not year or not model:
        return "Unknown"
    
    # Validate year range
    if year < 2009 or year > 2012:
        return f"Invalid Year {year}"
    
    # Validate model
    if model.lower() not in ["cayman", "boxster"]:
        return f"Invalid Model {model}"
    
    # Format trim (omit "Base" or blank)
    if not trim or trim.lower() in ["base", ""]:
        return f"{year} {model}"
    else:
        return f"{year} {model} {trim}"

def infer_trim_intelligent(title: str, body: str = "") -> str:
    """
    Intelligently infer trim using multiple data sources and engine displacement logic
    
    Args:
        title: Vehicle title text
        body: Additional body text for context
        
    Returns:
        Inferred trim string
    """
    if not title:
        return "Base"
    
    title_lower = title.lower()
    body_lower = body.lower()
    
    # Special trims (title only) - use word boundaries to prevent false positives
    if re.search(r"\bCayman\s+R\b", title, re.I):
        return "R"
    if re.search(r"\bBoxster\s+Spyder\b", title, re.I):
        return "Spyder"
    if re.search(r"\bBlack\s+Edition\b", title, re.I):
        return "Black Edition"
    
    # Explicit S in title - use word boundaries
    if re.search(r"\b(Cayman|Boxster)\s+S\b", title, re.I):
        return "S"
    
    # Explicit Base hints
    if re.search(r"\bCayman\s+Base\b", title, re.I):
        return "Base"
    if re.search(r"\bBoxster\s+Base\b", title, re.I):
        return "Base"
    if re.search(r"\bBASE\s+(Cayman|Boxster)\b", body, re.I):
        return "Base"
    
    # Default to Base when title is neutral
    trim = "Base"
    
    # Engine displacement override (only if unambiguous)
    has29 = re.search(r"\b2[\.,]9\s*l\b|\b2\.9l\b", body, re.I)
    has34 = re.search(r"\b3[\.,]4\s*l\b|\b3\.4l\b", body, re.I)
    
    if has34 and not has29:
        trim = "S"
    elif has29 and not has34:
        trim = "Base"
    
    return trim

# =========================
# PATTERN MATCHING
# =========================

def find_patterns(text: str, patterns: List[str], case_sensitive: bool = False) -> List[str]:
    """
    Find all patterns in text
    
    Args:
        text: Text to search
        patterns: List of patterns to find
        case_sensitive: Whether to use case-sensitive matching
        
    Returns:
        List of found patterns
    """
    if not text or not patterns:
        return []
    
    found = []
    search_text = text if case_sensitive else text.lower()
    
    for pattern in patterns:
        search_pattern = pattern if case_sensitive else pattern.lower()
        if search_pattern in search_text:
            found.append(pattern)
    
    return found

def extract_with_regex(text: str, pattern: str, group: int = 1) -> Optional[str]:
    """
    Extract text using regex pattern
    
    Args:
        text: Text to search
        pattern: Regex pattern
        group: Capture group to return
        
    Returns:
        Extracted text or None if no match
    """
    if not text:
        return None
    
    try:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and len(match.groups()) >= group:
            return match.group(group)
    except re.error:
        pass
    
    return None

# =========================
# TEXT VALIDATION
# =========================

def is_valid_vin(vin: str) -> bool:
    """
    Validate VIN format (basic validation)
    
    Args:
        vin: VIN string to validate
        
    Returns:
        True if VIN appears valid
    """
    if not vin:
        return False
    
    # VIN should be 17 characters
    if len(vin) != 17:
        return False
    
    # VIN should contain only alphanumeric characters (no I, O, Q)
    invalid_chars = set('IOQ')
    if any(char in invalid_chars for char in vin.upper()):
        return False
    
    return True

def is_valid_year(year: int) -> bool:
    """
    Validate vehicle year
    
    Args:
        year: Year to validate
        
    Returns:
        True if year is valid for 987.2
    """
    return 2009 <= year <= 2012

def is_valid_price(price: int) -> bool:
    """
    Validate price range
    
    Args:
        price: Price in dollars
        
    Returns:
        True if price is reasonable
    """
    return 0 <= price <= 1000000  # $0 to $1M

def is_valid_mileage(mileage: int) -> bool:
    """
    Validate mileage range
    
    Args:
        mileage: Mileage in miles
        
    Returns:
        True if mileage is reasonable
    """
    return 0 <= mileage <= 200000  # 0 to 200k miles

# =========================
# TEXT FORMATTING
# =========================

def format_price_display(price: Optional[int]) -> str:
    """
    Format price for display
    
    Args:
        price: Price in dollars
        
    Returns:
        Formatted price string
    """
    if price is None:
        return ""
    
    if price < 1000:
        return f"${price}"
    elif price < 10000:
        return f"${price:,}"
    else:
        return f"${price//1000}k"

def format_mileage_display(mileage: Optional[int]) -> str:
    """
    Format mileage for display
    
    Args:
        mileage: Mileage in miles
        
    Returns:
        Formatted mileage string
    """
    if mileage is None:
        return ""
    
    if mileage < 1000:
        return f"{mileage} miles"
    else:
        return f"{mileage//1000}k"

def format_deal_delta(delta: Optional[int]) -> str:
    """
    Format deal delta for display
    
    Args:
        delta: Deal delta in dollars
        
    Returns:
        Formatted delta string
    """
    if delta is None:
        return ""
    
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:,}"

# =========================
# UTILITY FUNCTIONS
# =========================

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        text: Text containing HTML
        
    Returns:
        Clean text without HTML tags
    """
    if not text:
        return ""
    
    # Simple HTML tag removal
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()

def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Text with potentially irregular whitespace
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    normalized = re.sub(r'\s+', ' ', text)
    return normalized.strip()
