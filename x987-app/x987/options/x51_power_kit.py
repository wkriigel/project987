"""
X51 Power Kit option
"""

import re
from typing import List


class X51PowerKitOption:
    def __init__(self):
        self.id = "X51"
        self.display = "X51 Power Kit"
        self.value_usd = 0  # Value overridden per generation via config
        self.category = "performance"
        self.patterns = [
            r"\bx51\b",
            r"\bx\s*51\b",
            r"\bpower\s*kit\b",
            r"\bengine\s*power\s*kit\b",
        ]
        self.compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> List[re.Pattern]:
        compiled = []
        for p in self.patterns:
            try:
                compiled.append(re.compile(p, re.IGNORECASE))
            except re.error:
                pass
        return compiled

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


X51_POWER_KIT_OPTION = X51PowerKitOption()
