"""
Configuration for the Trip Planner Agent System.
Handles environment variables and system settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for the trip planner agent system"""
    
    # ===== REQUIRED =====
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # ===== OPTIONAL (System works without these) =====
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Optional - for real-time weather
    ENABLE_GOOGLE_MAPS_LINKS = os.getenv("ENABLE_GOOGLE_MAPS_LINKS", "true").lower() == "true"
    
    # ===== MODEL CONFIGURATION =====
    # Using stable model that SUPPORTS FUNCTION CALLING (tools)
    # Note: gemini-2.5-flash-lite does NOT support function calling!
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Retry configuration for handling rate limits
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "5"))
    RETRY_EXP_BASE = int(os.getenv("RETRY_EXP_BASE", "7"))
    RETRY_INITIAL_DELAY = int(os.getenv("RETRY_INITIAL_DELAY", "1"))
    
    # ===== AGENT SETTINGS =====
    MAX_REVIEW_ITERATIONS = int(os.getenv("MAX_REVIEW_ITERATIONS", "5"))  # Increased for better quality (threshold is 8/10)
    
    # ===== FEATURE FLAGS =====
    ENABLE_GOOGLE_SEARCH = os.getenv("ENABLE_GOOGLE_SEARCH", "true").lower() == "true"
    ENABLE_CODE_EXECUTION = os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"  # Changed to true by default
    ENABLE_OBSERVABILITY = os.getenv("ENABLE_OBSERVABILITY", "true").lower() == "true"
    ENABLE_EVALUATION = os.getenv("ENABLE_EVALUATION", "true").lower() == "true"
    
    # ===== OBSERVABILITY =====
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError(
                "❌ GOOGLE_API_KEY not found!\n\n"
                "Please set it in .env file:\n"
                "1. Copy .env.example to .env\n"
                "2. Add your API key: GOOGLE_API_KEY=your_key_here\n"
                "3. Get a free key at: https://aistudio.google.com/app/apikey\n"
            )
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print(f"""
╔════════════════════════════════════════════╗
║      Trip Planner Configuration            ║
╚════════════════════════════════════════════╝

Model: {cls.MODEL_NAME}
Temperature: {cls.TEMPERATURE}
Max Review Iterations: {cls.MAX_REVIEW_ITERATIONS}

Features:
  • Google Search: {'✅ Enabled' if cls.ENABLE_GOOGLE_SEARCH else '❌ Disabled'}
  • Code Execution: {'✅ Enabled' if cls.ENABLE_CODE_EXECUTION else '❌ Disabled'}
  • Observability: {'✅ Enabled' if cls.ENABLE_OBSERVABILITY else '❌ Disabled'}
  • Evaluation: {'✅ Enabled' if cls.ENABLE_EVALUATION else '❌ Disabled'}

API Keys:
  • Google AI: {'✅ Set' if cls.GOOGLE_API_KEY else '❌ Missing'}
  • OpenWeather: {'✅ Set' if cls.OPENWEATHER_API_KEY else '⚠️  Optional (using fallback)'}
""")


# Validate on import
Config.validate()
