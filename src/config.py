"""
Configuration settings for the trip planner agent system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration for the trip planner system"""
    
    # ===== API KEYS =====
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Optional - for real-time weather
    ENABLE_GOOGLE_MAPS_LINKS = os.getenv("ENABLE_GOOGLE_MAPS_LINKS", "true").lower() == "true"
    
    # ===== MODEL CONFIGURATION =====
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # ===== MODEL TIER DETECTION =====
    @classmethod
    def get_model_tier(cls) -> str:
        """
        Determine model tier based on model name.
        
        Returns:
            'lite' for gemini-2.5-flash-lite
            'pro' for gemini-2.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp, etc.
        """
        model_lower = cls.MODEL_NAME.lower()
        if "lite" in model_lower:
            return "lite"
        else:
            return "pro"
    
    @classmethod
    def get_max_iterations(cls) -> int:
        """Get max iterations based on model tier"""
        tier = cls.get_model_tier()
        if tier == "lite":
            return 3  # Lite models don't benefit from many iterations
        else:
            return 5  # Pro models can handle more iterations
    
    @classmethod
    def get_approval_threshold(cls) -> float:
        """Get approval threshold based on model tier"""
        tier = cls.get_model_tier()
        if tier == "lite":
            return 7.0  # Lite models ceiling is ~7-7.5
        else:
            return 8.0  # Pro models can reach 8.5+
    
    # Retry configuration for handling rate limits
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "5"))
    RETRY_EXP_BASE = int(os.getenv("RETRY_EXP_BASE", "7"))
    RETRY_INITIAL_DELAY = int(os.getenv("RETRY_INITIAL_DELAY", "1"))
    
    # ===== AGENT SETTINGS =====
    # Now dynamically determined by model tier
    # For backward compatibility, set these as class attributes
    # They will return the default tier values (can be overridden by methods)
    MAX_REVIEW_ITERATIONS = 3  # Default for lite, use get_max_iterations() for dynamic
    APPROVAL_THRESHOLD = 7.0  # Default for lite, use get_approval_threshold() for dynamic
    
    # ===== FEATURE FLAGS =====
    ENABLE_GOOGLE_SEARCH = os.getenv("ENABLE_GOOGLE_SEARCH", "true").lower() == "true"
    ENABLE_CODE_EXECUTION = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    ENABLE_OBSERVABILITY = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"
    ENABLE_EVALUATION = os.getenv("ENABLE_EVALUATION", "true").lower() == "true"
    
    # ===== OBSERVABILITY =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GOOGLE_AI_API_KEY:
            raise ValueError("GOOGLE_AI_API_KEY is required in .env file")
        
        return True
    
    @classmethod
    def print_config_info(cls):
        """Print configuration information"""
        tier = cls.get_model_tier()
        print(f"[CONFIG] Model: {cls.MODEL_NAME}")
        print(f"[CONFIG] Tier: {tier}")
        print(f"[CONFIG] Max Iterations: {cls.get_max_iterations()}")
        print(f"[CONFIG] Approval Threshold: {cls.get_approval_threshold()}")
    
    @classmethod
    def get_agent_type(cls) -> str:
        """
        Get the agent implementation to use based on model tier.
        
        Returns:
            'lite' or 'pro'
        """
        return cls.get_model_tier()

