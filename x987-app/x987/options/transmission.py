"""
Transmission options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class PDK(BaseOption):
    """PDK transmission option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="PDK",
            display="PDK",
            value_usd=0,  # Standard on automatic 987.2
            patterns=[
                r"\bpdk\b",
                r"\bdoppelkupplung\b",
                r"\b7[-\s]?speed\b",
                r"\bautomatic\b",
                r"\bauto\b",
                r"\btiptronic\b"
            ],
            category="transmission"
        )


# Export all transmission options
TRANSMISSION_OPTIONS = [
    PDK()
]
