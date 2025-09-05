"""
Auto-dimming mirrors & rain sensor option
"""

import re
from typing import List


class AutoDimRainSensorOption:
    def __init__(self):
        self.id = "DIM_RAIN"
        self.display = "Auto-dim Mirrors & Rain Sensor"
        self.value_usd = 0  # overridden per generation
        self.category = "comfort"
        self.patterns = [
            r"\b(auto[-\s]?dimm?ing|self[-\s]?dimm?ing)\b",
            r"\brain\s+sensor\b",
            r"\b635\b",
        ]
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        out = []
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


AUTO_DIM_RAIN_SENSOR_OPTION = AutoDimRainSensorOption()
