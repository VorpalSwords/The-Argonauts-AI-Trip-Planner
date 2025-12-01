"""
Tests for configuration and model-aware settings.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config


class TestConfigModelTier:
    """Test model tier detection"""
    
    def test_lite_model_detection(self):
        """Test that lite models are detected correctly"""
        # Save original
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash-lite"
            assert Config.get_model_tier() == "lite"
            
            # Test case-insensitive matching with real model names
            Config.MODEL_NAME = "GEMINI-2.5-FLASH-LITE"
            assert Config.get_model_tier() == "lite"
        finally:
            Config.MODEL_NAME = original_model
    
    def test_pro_model_detection(self):
        """Test that pro models are detected correctly"""
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash"
            assert Config.get_model_tier() == "pro"
            
            Config.MODEL_NAME = "gemini-1.5-pro"
            assert Config.get_model_tier() == "pro"
            
            Config.MODEL_NAME = "gemini-2.0-flash-exp"
            assert Config.get_model_tier() == "pro"
        finally:
            Config.MODEL_NAME = original_model
    
    def test_max_iterations_lite(self):
        """Test that lite models get fewer iterations"""
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash-lite"
            max_iters = Config.get_max_iterations()
            assert max_iters == 3  # Lite default
        finally:
            Config.MODEL_NAME = original_model
    
    def test_max_iterations_pro(self):
        """Test that pro models get more iterations"""
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash"
            max_iters = Config.get_max_iterations()
            assert max_iters == 5  # Pro default
        finally:
            Config.MODEL_NAME = original_model
    
    def test_approval_threshold_lite(self):
        """Test that lite models have lower approval threshold"""
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash-lite"
            threshold = Config.get_approval_threshold()
            assert threshold == 7.0  # Lite threshold
        finally:
            Config.MODEL_NAME = original_model
    
    def test_approval_threshold_pro(self):
        """Test that pro models have higher approval threshold"""
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash"
            threshold = Config.get_approval_threshold()
            assert threshold == 8.0  # Pro threshold
        finally:
            Config.MODEL_NAME = original_model


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_config_has_required_fields(self):
        """Test that Config has all required fields"""
        assert hasattr(Config, 'MODEL_NAME')
        assert hasattr(Config, 'MAX_REVIEW_ITERATIONS')
        assert hasattr(Config, 'ENABLE_CODE_EXECUTION')
        assert hasattr(Config, 'get_model_tier')
        assert hasattr(Config, 'get_max_iterations')
        assert hasattr(Config, 'get_approval_threshold')
    
    def test_config_types(self):
        """Test that config values have correct types"""
        assert isinstance(Config.MODEL_NAME, str)
        # MAX_REVIEW_ITERATIONS is now dynamic - use the method
        assert isinstance(Config.get_max_iterations(), int)
        assert isinstance(Config.ENABLE_CODE_EXECUTION, bool)
        assert isinstance(Config.get_model_tier(), str)
        assert isinstance(Config.get_max_iterations(), int)
        assert isinstance(Config.get_approval_threshold(), float)

