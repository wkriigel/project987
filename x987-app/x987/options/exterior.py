"""
Exterior options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class BiXenonHeadlights(BaseOption):
    """Bi-Xenon Headlights with Dynamic Cornering option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Bi-Xenon",
            display="Bi-Xenon Headlights with Dynamic Cornering",
            value_usd=250,
            patterns=[
                r"\bbi[-\s]?xenon\b",
                r"\bxenon\s+headlights\b",
                r"\bxenon\s+lighting\b",
                r"\bprojector\s+beam\s+headlights\b",
                r"\bprojector\s+headlights\b",
                r"\bdynamic\s+cornering\s+lights\b",
                r"\bcornering\s+lights\b",
                r"\badaptive\s+headlights\b",
                r"\badaptive\s+lighting\b"
            ],
            category="exterior"
        )


class UpgradedWheels(BaseOption):
    """18–19" Upgraded Wheels option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="Wheels",
            display="18–19\" Upgraded Wheels",
            value_usd=400,
            patterns=[
                r"\b19\s*inch\b",
                r"\b19\s*\"\b",
                r"\b19\s*x\s*\d+\s*inch\b",
                r"\b19\s*x\s*\d+\s*\"\b",
                r"\b18\s*inch\b",
                r"\b18\s*\"\b",
                r"\b18\s*x\s*\d+\s*inch\b",
                r"\b18\s*x\s*\d+\s*\"\b",
                r"\balloy\s+wheels\b",
                r"\bupgraded\s+wheels\b",
                r"\bpremium\s+wheels\b",
                r"\bsport\s+wheels\b",
                r"\b19\s*inch\s+alloy\s+wheels\b",
                r"\b18\s*inch\s+alloy\s+wheels\b"
            ],
            category="exterior"
        )


# Export all exterior options
EXTERIOR_OPTIONS = [
    BiXenonHeadlights(),
    UpgradedWheels()
]
