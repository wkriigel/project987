"""
Performance options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class SportChronoPackagePlus(BaseOption):
    """Sport Chrono Package Plus option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="639/640",
            display="Sport Chrono Package Plus",
            value_usd=1000,
            patterns=[
                r"\bsport\s+chrono\b",
                r"\bchrono\s+package\b", 
                r"\bchrono\s+plus\b",
                r"\bsport\s+chrono\s+plus\b",
                r"\bchrono\s+package\s+plus\b",
                r"\bsport\s+chrono\s+package\b",
                r"\bchrono\b",
                r"\bsport\s+chrono\s+package\s+plus\b"
            ],
            category="performance"
        )


class PASM(BaseOption):
    """PASM (Porsche Active Suspension Management) option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="PASM",
            display="PASM",
            value_usd=800,
            patterns=[
                r"\bpasm\b",
                r"\badaptive\s+suspension\b",
                r"\bactive\s+suspension\b",
                r"\badaptive\s+damping\b",
                r"\bporsche\s+active\s+suspension\s+management\b",
                r"\badaptive\s+sport\s+suspension\b",
                r"\bsport\s+suspension\b"
            ],
            category="performance"
        )


class LimitedSlipDifferential(BaseOption):
    """Limited Slip Differential (LSD) option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="LSD",
            display="Limited Slip Differential (LSD)",
            value_usd=1200,
            patterns=[
                r"\blimited\s+slip\b",
                r"\blsd\b",
                r"\blimited\s+slip\s+differential\b",
                r"\bbrake\s+actuated\s+limited\s+slip\b",
                r"\bmechanical\s+limited\s+slip\b"
            ],
            category="performance"
        )


class SportExhaust(BaseOption):
    """Sport Exhaust (PSE) option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="PSE",
            display="Sport Exhaust (PSE)",
            value_usd=800,
            patterns=[
                r"\bsport\s+exhaust\b",
                r"\bpse\b",
                r"\bsport\s+exhaust\s+system\b",
                r"\bdual\s+exhaust\b",
                r"\bstainless\s+steel\s+dual\s+exhaust\b",
                r"\bexhaust\s+system\b",
                r"\bsport\s+exhaust\s+with\s+dual\s+tailpipes\b"
            ],
            category="performance"
        )


# Export all performance options
PERFORMANCE_OPTIONS = [
    SportChronoPackagePlus(),
    PASM(),
    LimitedSlipDifferential(),
    SportExhaust()
]
