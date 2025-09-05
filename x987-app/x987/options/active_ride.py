"""
Porsche Active Ride (Adaptive Suspension) Option

Detects Taycan's generation-specific Porsche Active Ride system.
"""

import re
from typing import List


class ActiveRideOption:
    def __init__(self):
        self.id = "ACTIVE_RIDE"
        self.display = "Porsche Active Ride (Adaptive Suspension)"
        self.value_usd = 0  # Spec value accounted for via MSRP overrides/fallback catalog
        self.category = "performance"
        self.patterns = [
            r"\bporsche\s+active\s+ride\b",
            r"\bactive\s+ride\b",
            r"\bactive\s+ride\s+adaptive\s+suspension\b",
            r"\badaptive\s+suspension\b"  # keep broad for coverage; PASM has own file
        ]
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        out: List[re.Pattern] = []
        for p in self.patterns:
            try:
                out.append(re.compile(p, re.IGNORECASE))
            except re.error:
                pass
        return out

    def is_present(self, text: str, trim: str = None) -> bool:
        if not text:
            return False
        for pat in self.compiled_patterns:
            if pat.search(text):
                return True
        return False

    def get_value(self, text: str, trim: str = None) -> int:
        return self.value_usd if self.is_present(text, trim) else 0

    def get_display(self) -> str:
        return self.display

    def get_category(self) -> str:
        return self.category

    def get_id(self) -> str:
        return self.id


ACTIVE_RIDE_OPTION = ActiveRideOption()

