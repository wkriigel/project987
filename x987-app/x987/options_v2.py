"""
Backward-compatibility shim for the legacy `x987.options_v2` import path.

Exports a compatible `OptionsDetector` that delegates to the new modular
options system under `x987.options` and provides minor API aliases expected by
older tests/docs (e.g., `total_options` in the summary dict).
"""

from __future__ import annotations

from typing import Any, Dict

# Delegate to the current implementation
from .options.detector import OptionsDetector as _NewOptionsDetector


class OptionsDetector(_NewOptionsDetector):
    """Compatibility wrapper over the new OptionsDetector.

    Adds legacy summary keys expected by older tests:
    - `total_options` (alias of `total_count`)
    """

    def get_detailed_options_summary(self, *args, **kwargs) -> Dict[str, Any]:  # type: ignore[override]
        summary = super().get_detailed_options_summary(*args, **kwargs)
        # Provide legacy alias expected by older tests/docs
        if 'total_options' not in summary and 'total_count' in summary:
            try:
                summary['total_options'] = int(summary.get('total_count') or 0)
            except Exception:
                summary['total_options'] = summary.get('total_count')
        return summary


# Legacy constant expected by some old test files; not used by core code.
DEFAULT_OPTIONS: list = []

__all__ = [
    'OptionsDetector',
    'DEFAULT_OPTIONS',
]

