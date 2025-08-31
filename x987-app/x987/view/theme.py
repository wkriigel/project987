"""
Theme and styling configuration for View-from-CSV

PROVIDES: Color schemes, styling rules, and display configuration
DEPENDS: Standard library only
CONSUMED BY: Report generation modules
CONTRACT: Provides consistent theming across all views
TECH CHOICE: Centralized theme configuration
RISK: Low - styling changes don't affect functionality
"""

import os
from typing import Dict, Any, Optional, Tuple

# =========================
# THEME SYSTEM
# =========================
THEME = {
    "bg":            "#0B0F14",
    "surface":       "#121820",
    "surface_alt":   "#0E141B",

    "text":          "#C9D1D9",
    "text_muted":    "#8A97A6",
    "text_dim":      "#55616E",

    "gray_900": "#1A222C",
    "gray_800": "#252F3A",
    "gray_700": "#3A4654",
    "gray_600": "#4D5967",
    "gray_500": "#6B7785",
    "gray_400": "#8794A2",
    "gray_300": "#A5AFBA",
    "gray_200": "#C2CBD6",
    "gray_100": "#DEE4EC",

    # Teal ramp (cheap = bright, low miles = bright)
    "teal_1": "#5FFBF1",
    "teal_2": "#37E9DF",
    "teal_3": "#19E1D6",
    "teal_4": "#3FB8B0",
    "teal_5": "#5E8F91",
    "teal_6": "#6F7F82",

    # Oranges for Porsche models
    "orange_cayman_s":  "#FF6A1A",
    "orange_cayman":    "#FFC04D",
    "orange_boxster_s": "#FFD137",
    "orange_boxster":   "#FFE394",
    "orange_special_1": "#FF3B1A",
    "orange_special_2": "#E62500",

    # Warm dim ramp (manual de-emphasis)
    "warm_dim_1": "#6E5A4E",
    "warm_dim_2": "#665247",
    "warm_dim_3": "#5D4B41",
    "warm_dim_4": "#54443B",
    "warm_dim_5": "#4B3C35",
    "warm_dim_6": "#43362F",

    # Row stripe (subtle)
    "stripe_1": "#11151B",

    # Dark green for MSRP totals
    "msrp_green": "#0F7B47",
    # Dim greenish background for MSRP highlight (greener than teal, subdued)
    "msrp_bg": "#2B4A40",
}

# ANSI color mapping for fallback
NEAREST_ANSI = [
    ("black","#000000"),("dark_gray","#808080"),("bright_black","#555555"),
    ("white","#C0C0C0"),("bright_white","#E6EDF3"),("red","#CC0000"),
    ("bright_red","#FF6A00"),("green","#00A86B"),("bright_green","#24D67A"),
    ("yellow","#FFC300"),("bright_yellow","#FFD966"),("blue","#3A8EDB"),
    ("bright_blue","#66A8EA"),("purple","#A888FF"),("bright_purple","#C9A8FF"),
    ("cyan","#00CFC7"),("bright_cyan","#19E1D6"),
]

# =========================
# CONFIGURATION
# =========================
BG_PRICE = os.environ.get("X987_BG_PRICE", "1") in ("1", "true", "TRUE", "yes", "YES")
BG_MILES = os.environ.get("X987_BG_MILES", "1") in ("1", "true", "TRUE", "yes", "YES")

# Column widths
K_COL_WIDTH = 5   # fits $999k / 999k
PRICE_W = K_COL_WIDTH
MILES_W = K_COL_WIDTH

# =========================
# COLOR UTILITIES
# =========================
def theme_style(fg: Optional[str] = None, bg: Optional[str] = None, **kwargs) -> str:
    """Create a theme style string"""
    style_parts = []
    
    if fg:
        style_parts.append(f"color({fg})")
    if bg:
        style_parts.append(f"on({bg})")
    
    for key, value in kwargs.items():
        style_parts.append(f"{key}({value})")
    
    return " ".join(style_parts)

def get_nearest_ansi(hex_color: str) -> str:
    """Get nearest ANSI color for hex color"""
    if not hex_color or not hex_color.startswith("#"):
        return "white"
    
    # Simple distance calculation
    def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    
    def color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5
    
    target_rgb = hex_to_rgb(hex_color)
    nearest_color = "white"
    min_distance = float('inf')
    
    for ansi_name, ansi_hex in NEAREST_ANSI:
        ansi_rgb = hex_to_rgb(ansi_hex)
        distance = color_distance(target_rgb, ansi_rgb)
        if distance < min_distance:
            min_distance = distance
            nearest_color = ansi_name
    
    return nearest_color

# =========================
# PRICE STYLING
# =========================
def price_style_key(price_int: Optional[int]) -> str:
    """Get style key for price value"""
    if price_int is None:
        return "text_muted"
    if price_int < 20_000:
        return "teal_1"
    if price_int < 25_000:
        return "teal_2"
    if price_int < 30_000:
        return "teal_3"
    if price_int < 35_000:
        return "teal_4"
    if price_int < 40_000:
        return "teal_5"
    return "teal_6"

def miles_style_key(miles_val: Optional[int]) -> str:
    """Get style key for mileage value"""
    if miles_val is None:
        return "text_muted"
    if miles_val < 30_000:
        return "teal_1"
    if miles_val < 45_000:
        return "teal_2"
    if miles_val < 60_000:
        return "teal_3"
    if miles_val < 80_000:
        return "teal_4"
    if miles_val < 100_000:
        return "teal_5"
    return "teal_6"

# =========================
# MODEL STYLING
# =========================
def model_style_key(model: str, trim: str) -> str:
    """Get style key for model/trim combination"""
    model_lower = model.lower()
    trim_lower = trim.lower()
    
    if "cayman" in model_lower:
        if "s" in trim_lower:
            return "orange_cayman_s"
        elif "r" in trim_lower:
            return "orange_special_1"
        else:
            return "orange_cayman"
    elif "boxster" in model_lower:
        if "s" in trim_lower:
            return "orange_boxster_s"
        elif "spyder" in trim_lower:
            return "orange_special_2"
        else:
            return "orange_boxster"
    else:
        return "text"

# =========================
# TRANSMISSION STYLING
# =========================
def transmission_style_key(transmission: str) -> str:
    """Get style key for transmission"""
    if transmission and transmission.lower() == "manual":
        return "warm_dim_3"  # De-emphasize manual
    return "text"  # Emphasize automatic
