"""
Technology options for Porsche 987.2 vehicles
"""

from .base import BaseOption, OptionDefinition


class PCMNavigation(BaseOption):
    """PCM w/ Navigation option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="PCM",
            display="PCM w/ Navigation",
            value_usd=300,
            patterns=[
                r"\bpcm\b",
                r"\bnavigation\b",
                r"\bnavigation\s+system\b",
                r"\bpremium\s+communication\s+module\b",
                r"\bcommunication\s+module\b",
                r"\bpremium\s+communication\b",
                r"\bpremium\s+communication\s+system\b"
            ],
            category="technology"
        )


class BOSESurroundSound(BaseOption):
    """BOSE Surround Sound option"""
    
    def get_definition(self) -> OptionDefinition:
        return OptionDefinition(
            id="BOSE",
            display="BOSE Surround Sound",
            value_usd=300,
            patterns=[
                r"\bbose\b",
                r"\bbose\s+surround\s+sound\b",
                r"\bsurround\s+sound\b",
                r"\bpremium\s+sound\s+system\b",
                r"\bpremium\s+audio\b",
                r"\bpremium\s+sound\b",
                r"\bpremium\s+audio\s+system\b",
                r"\bupgraded\s+sound\s+system\b"
            ],
            category="technology"
        )


# Export all technology options
TECHNOLOGY_OPTIONS = [
    PCMNavigation(),
    BOSESurroundSound()
]
