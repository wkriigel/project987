"""
Seating options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class SportSeats(BaseOption):
    """Sport Seats / Adaptive Sport Seats option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Sport Seats",
            display="Sport Seats / Adaptive Sport Seats",
            value_usd=500,
            patterns=[
                r"\bsport\s+seats\b",
                r"\badaptive\s+sport\s+seats\b",
                r"\bsport\s+bucket\s+seats\b",
                r"\badaptive\s+sport\s+bucket\s+seats\b",
                r"\bbucket\s+seats\b",
                r"\bsport\s+seating\b",
                r"\badaptive\s+sport\s+seating\b"
            ],
            category="seating"
        )


class HeatedSeats(BaseOption):
    """Heated Seats option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Heated Seats",
            display="Heated Seats",
            value_usd=150,
            patterns=[
                r"\bheated\s+seats\b",
                r"\bseat\s+heating\b",
                r"\bheated\s+front\s+seats\b",
                r"\bheated\s+driver\s+seat\b",
                r"\bheated\s+passenger\s+seat\b"
            ],
            category="seating"
        )


class VentilatedSeats(BaseOption):
    """Ventilated Seat option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Ventilated Seats",
            display="Ventilated Seat",
            value_usd=150,
            patterns=[
                r"\bventilated\s+seats\b",
                r"\bventilated\s+seating\b",
                r"\bseat\s+ventilation\b",
                r"\bperforated\s+leather\s+seats\b",
                r"\bventilated\s+leather\b"
            ],
            category="seating"
        )


# Export all seating options
SEATING_OPTIONS = [
    SportSeats(),
    HeatedSeats(),
    VentilatedSeats()
]
