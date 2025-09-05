"""
Catalog Step - Exports generation catalog JSON for FE/docs

This step runs late in the pipeline to generate a compact JSON catalog of
models → generations → trims and options (with MSRP) for the FE to consume.

PROVIDES: Generation catalog JSON for UI/documentation
DEPENDS: transformation (ensures config loaded; heavy work already done)
CONSUMED BY: x987-web FE via /api/catalog/generations
CONTRACT: Writes generation_catalog.json to a well-known location
TECH CHOICE: Use existing exporter module (single source of truth)
RISK: Low - generation metadata export is read-only and side-effect is a JSON file
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .base import BasePipelineStep, StepResult


class CatalogStep(BasePipelineStep):
    """Exports the generation catalog JSON after transformation"""

    def get_step_name(self) -> str:
        return "catalog"

    def get_description(self) -> str:
        return "Exports generation catalog JSON for FE consumption"

    def get_dependencies(self) -> List[str]:
        # Run after ranking so the catalog export happens at the end of heavy steps
        return ["ranking"]

    def get_required_config(self) -> List[str]:
        return []

    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        start = datetime.now()
        try:
            from x987.catalog.export import export_generation_catalog_json
            # Resolve repo root robustly via config dir
            from x987.config.manager import get_config_dir
            repo_root = get_config_dir().parent

            # Primary: FE API data path
            fe_api_path = repo_root / 'x987-web' / 'apps' / 'api' / 'data' / 'generation_catalog.json'
            out1 = export_generation_catalog_json(fe_api_path)

            # Secondary: x987-data metadata path (for other consumers)
            data_meta_path = repo_root / 'x987-data' / 'metadata' / 'generation_catalog.json'
            out2 = export_generation_catalog_json(data_meta_path)

            return {
                "ok": True,
                "paths": [str(out1), str(out2)],
                "catalog_type": "generations"
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }


# Export the step instance for registry discovery
CATALOG_STEP = CatalogStep()
