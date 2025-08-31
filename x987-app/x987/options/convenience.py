"""
Convenience options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class ParkAssist(BaseOption):
    """Park Assist option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Park Assist",
            display="Park Assist",
            value_usd=200,
            patterns=[
                r"\bpark\s+assist\b",
                r"\bparking\s+assist\b",
                r"\bparking\s+aid\b",
                r"\bparking\s+sensors\b",
                r"\brear\s+parking\s+sensors\b",
                r"\bfront\s+parking\s+sensors\b"
            ],
            category="convenience"
        )


# Export all convenience options
CONVENIENCE_OPTIONS = [
    ParkAssist()
]
