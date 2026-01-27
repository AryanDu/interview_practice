"""
Calculate costs for LLM API calls
"""
from typing import Dict, Optional
from config import Config


class CostCalculator:
    """Calculate API costs based on token usage"""
    
    # Pricing per 1M tokens (as of common pricing, update as needed)
    PRICING = {
        "openai": {
            "gpt-4o": {"input": 2.50, "output": 10.00},  # per 1M tokens
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4.1": {"input": 3.00, "output": 12.00},  # Estimated
            "gpt-4.1-mini": {"input": 0.20, "output": 0.80},  # Estimated
            "gpt-4.1-nano": {"input": 0.10, "output": 0.40},  # Estimated
            "text-embedding-3-small": {"input": 0.02, "output": 0.0},
        },
        "gemini": {
            "gemini-pro": {"input": 0.50, "output": 1.50},  # Legacy model
            "gemini-1.5-pro": {"input": 1.50, "output": 6.00},  # Current pricing
        },
        "claude": {
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        }
    }
    
    @classmethod
    def calculate_cost(
        cls,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> Dict[str, float]:
        """Calculate cost for API call"""
        provider_lower = provider.lower()
        model_lower = model.lower()
        
        # Get pricing
        pricing = cls.PRICING.get(provider_lower, {}).get(model_lower)
        if not pricing:
            # Default fallback pricing
            pricing = {"input": 0.50, "output": 1.50}
        
        # Calculate costs
        input_cost = (prompt_tokens / 1_000_000) * pricing.get("input", 0)
        output_cost = (completion_tokens / 1_000_000) * pricing.get("output", 0)
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
            "model": model,
            "provider": provider
        }
    
    @classmethod
    def calculate_from_response(
        cls,
        provider: str,
        model: str,
        usage: Dict[str, int]
    ) -> Dict[str, float]:
        """Calculate cost from API response usage dictionary"""
        # Defensive handling: `usage` may be None or contain None values.
        if not usage:
            usage = {}

        # Coerce token counts to integers and fallback to 0 for None/invalid values
        def _safe_int(value):
            try:
                if value is None:
                    return 0
                return int(value)
            except (ValueError, TypeError):
                return 0

        prompt_tokens = _safe_int(usage.get("prompt_tokens"))
        completion_tokens = _safe_int(usage.get("completion_tokens"))

        return cls.calculate_cost(
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
    
    @classmethod
    def estimate_cost(
        cls,
        provider: str,
        model: str,
        estimated_prompt_tokens: int,
        estimated_completion_tokens: int
    ) -> Dict[str, float]:
        """Estimate cost before making API call"""
        return cls.calculate_cost(
            provider=provider,
            model=model,
            prompt_tokens=estimated_prompt_tokens,
            completion_tokens=estimated_completion_tokens
        )
    
    @classmethod
    def format_cost_display(cls, cost_info: Dict[str, float]) -> str:
        """Format cost information for display"""
        return f"""
**Cost Breakdown:**
- Input Tokens: {cost_info['input_tokens']:,}
- Output Tokens: {cost_info['output_tokens']:,}
- Total Tokens: {cost_info['total_tokens']:,}
- Input Cost: ${cost_info['input_cost_usd']:.6f}
- Output Cost: ${cost_info['output_cost_usd']:.6f}
- **Total Cost: ${cost_info['total_cost_usd']:.6f}**
- Model: {cost_info['model']}
- Provider: {cost_info['provider']}
        """
