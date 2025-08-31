"""
Model+Trim Extractor - Extracts vehicle model and trim as a combined field

This file contains everything needed to extract the vehicle model and trim.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any, Tuple
from .base import BaseExtractor, ExtractionResult


class ModelTrimExtractor(BaseExtractor):
    """Model and trim extraction from vehicle text"""
    
    def get_field_name(self) -> str:
        return "model_trim"
    
    def get_patterns(self) -> List[str]:
        return [
            r'(Cayman|Boxster|911|Cayenne|Macan|Panamera|Taycan|918|959|944|928|968|924|356|550)\s*(S|R|Turbo|GT3|GT4|GT2|GT2RS|GT3RS|GT4RS|Spyder|Targa|Carrera|GTS|4S|4|2S|2|Black\s+Edition)?',
            r'(Porsche)\s*(Cayman|Boxster|911|Cayenne|Macan|Panamera|Taycan|918|959|944|928|968|924|356|550)\s*(S|R|Turbo|GT3|GT4|GT2|GT2RS|GT3RS|GT4RS|Spyder|Targa|Carrera|GTS|4S|4|2S|2|Black\s+Edition)?',
            r'(\d{4})\s*(Cayman|Boxster|911|Cayenne|Macan|Panamera|Taycan|918|959|944|928|968|924|356|550)\s*(S|R|Turbo|GT3|GT4|GT2|GT2RS|GT3RS|GT4RS|Spyder|Targa|Carrera|GTS|4S|4|2S|2|Black\s+Edition)?',
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process model+trim match to return combined string"""
        try:
            # Extract model and trim from groups
            groups = match.groups()
            
            # Patterns may include year in group 1 for some variants; normalize capture indices
            # Known patterns:
            # 1) (Model) (Trim?)
            # 2) (Porsche) (Model) (Trim?)
            # 3) (Year) (Model) (Trim?)
            if len(groups) == 3 and groups[0] and groups[0].isdigit():
                # Year, Model, Trim
                model = groups[1] or "Unknown"
                trim = groups[2] or "Base"
            elif len(groups) >= 2:
                # Model, Trim
                model = groups[0] or "Unknown"
                trim = groups[1] or "Base"
            elif len(groups) == 1:
                model = groups[0] if groups[0] else "Unknown"
                trim = "Base"
            else:
                return None
            
            # Clean up the model and trim
            model = model.strip()
            trim = trim.strip()
            
            # Ignore spurious '2' trim (e.g., from '2d' = 2 door). Treat as Base
            if trim == "2":
                trim = "Base"

            # Handle special cases
            if trim == "Base" and model in ["Cayman", "Boxster", "911"]:
                # For base models, just return the model name
                return model
            elif trim and trim != "Base":
                # Return "Model Trim" format
                return f"{model} {trim}"
            else:
                # Just return the model
                return model
                
        except (ValueError, AttributeError):
            pass
        return None
    
    def extract_separate(self, text: str) -> Tuple[str, str]:
        """Extract model and trim as separate values"""
        result = self.extract(text)
        if not result or not result.value:
            return "Unknown", "Base"
        
        value = result.value
        
        # Split combined value back into model and trim
        if " " in value:
            parts = value.split(" ", 1)
            model = parts[0]
            trim = parts[1]
        else:
            model = value
            trim = "Base"
        
        return model, trim


# Export the extractor instance
MODEL_TRIM_EXTRACTOR = ModelTrimExtractor()
