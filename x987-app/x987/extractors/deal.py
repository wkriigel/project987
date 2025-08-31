"""
Deal Extractor - Calculates deal delta (fair value minus asking price)

This file contains everything needed to calculate the deal delta.
It's completely self-contained and can be modified independently.
"""

from typing import Optional, Dict, Any, List
from .base import BaseExtractor, ExtractionResult


class DealExtractor(BaseExtractor):
    """Deal delta calculation"""
    
    def get_field_name(self) -> str:
        return "deal_delta"
    
    def get_patterns(self) -> List[str]:
        # This extractor doesn't use regex patterns - it calculates values
        return []
    
    def calculate_deal_delta(self, fair_value: int, asking_price: int) -> Optional[int]:
        """
        Calculate deal delta: Fair Value - Asking Price
        
        Args:
            fair_value: Calculated fair value in USD
            asking_price: Actual asking price in USD
            
        Returns:
            Deal delta (positive = good deal, negative = overpriced)
        """
        if fair_value is None or asking_price is None:
            return None
        
        try:
            deal_delta = fair_value - asking_price
            return deal_delta
        except (TypeError, ValueError):
            return None
    
    def get_deal_rating(self, deal_delta: int) -> str:
        """
        Get a human-readable rating for the deal
        
        Args:
            deal_delta: Deal delta value
            
        Returns:
            Deal rating string
        """
        if deal_delta is None:
            return "Unknown"
        
        if deal_delta >= 5000:
            return "Excellent"
        elif deal_delta >= 2000:
            return "Good"
        elif deal_delta >= 0:
            return "Fair"
        elif deal_delta >= -2000:
            return "Overpriced"
        else:
            return "Very Overpriced"
    
    def get_deal_percentage(self, deal_delta: int, asking_price: int) -> Optional[float]:
        """
        Calculate deal delta as a percentage of asking price
        
        Args:
            deal_delta: Deal delta value
            asking_price: Asking price
            
        Returns:
            Deal delta as percentage (positive = good deal, negative = overpriced)
        """
        if deal_delta is None or asking_price is None or asking_price == 0:
            return None
        
        try:
            percentage = (deal_delta / asking_price) * 100
            return round(percentage, 1)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    
    def format_deal_delta(self, deal_delta: Optional[int]) -> str:
        """
        Format deal delta for display
        
        Args:
            deal_delta: Deal delta value
            
        Returns:
            Formatted string
        """
        if deal_delta is None:
            return "N/A"
        
        if deal_delta > 0:
            return f"+${deal_delta:,}"
        elif deal_delta < 0:
            return f"-${abs(deal_delta):,}"
        else:
            return "$0"
    
    def extract(self, text: str, **kwargs) -> Optional[ExtractionResult]:
        """
        This extractor doesn't extract from text - it calculates deal delta
        from fair value and asking price
        """
        fair_value = kwargs.get('fair_value')
        asking_price = kwargs.get('asking_price')
        
        if fair_value is not None and asking_price is not None:
            deal_delta = self.calculate_deal_delta(fair_value, asking_price)
            if deal_delta is not None:
                return ExtractionResult(
                    value=deal_delta,
                    confidence=1.0,
                    source_pattern="calculated",
                    raw_match=f"fair_value={fair_value}, asking_price={asking_price}"
                )
        
        return None


# Export the extractor instance
DEAL_EXTRACTOR = DealExtractor()
