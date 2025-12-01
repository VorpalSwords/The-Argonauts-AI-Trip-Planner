"""
Model Helper - Creates properly configured Gemini models with retry logic.
"""

from google.adk.models.google_llm import Gemini
from google.genai import types
from src.config import Config


def create_gemini_model(
    model_name: str = None,
    temperature: float = None,
    retry_attempts: int = None,
    retry_exp_base: int = None,
    retry_initial_delay: int = None
) -> Gemini:
    """
    Create a Gemini model with proper retry configuration.
    
    This handles rate limits (429) and server errors (500, 503, 504) automatically.
    
    Args:
        model_name: Model to use (default: from Config)
        temperature: Temperature for generation (default: from Config)
        retry_attempts: Max retry attempts (default: from Config)
        retry_exp_base: Exponential backoff base (default: from Config)
        retry_initial_delay: Initial delay in seconds (default: from Config)
        
    Returns:
        Configured Gemini model with retry logic
    """
    # Use config defaults if not specified
    model_name = model_name or Config.MODEL_NAME
    temperature = temperature if temperature is not None else Config.TEMPERATURE
    retry_attempts = retry_attempts or Config.RETRY_ATTEMPTS
    retry_exp_base = retry_exp_base or Config.RETRY_EXP_BASE
    retry_initial_delay = retry_initial_delay or Config.RETRY_INITIAL_DELAY
    
    # Create retry configuration
    retry_config = types.HttpRetryOptions(
        attempts=retry_attempts,
        exp_base=retry_exp_base,
        initial_delay=retry_initial_delay,
        http_status_codes=[429, 500, 503, 504]  # Retry on rate limits and server errors
    )
    
    # Create and return Gemini model
    return Gemini(
        model=model_name,
        retry_options=retry_config,
        temperature=temperature
    )


# Pre-configured model for easy import
default_model = create_gemini_model()

