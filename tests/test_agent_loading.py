"""
Tests for dynamic agent loading system.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config


class TestAgentImports:
    """Test that agent modules can be imported"""
    
    def test_lite_agents_import(self):
        """Test that lite agents can be imported"""
        from src.agents.lite_model import ResearchAgentLite, PlanningAgentLite, ReviewAgentLite
        
        assert ResearchAgentLite is not None
        assert PlanningAgentLite is not None
        assert ReviewAgentLite is not None
    
    def test_pro_agents_import(self):
        """Test that pro agents can be imported"""
        from src.agents.pro_model import ResearchAgentPro, PlanningAgentPro, ReviewAgentPro
        
        assert ResearchAgentPro is not None
        assert PlanningAgentPro is not None
        assert ReviewAgentPro is not None
    
    def test_orchestrator_import(self):
        """Test that orchestrator can be imported"""
        from src.agents.orchestrator_capstone import OrchestratorAgentCapstone
        
        assert OrchestratorAgentCapstone is not None
    
    def test_exploration_agent_import(self):
        """Test that exploration agent can be imported"""
        from src.agents.exploration_agent import ExplorationAgent
        
        assert ExplorationAgent is not None


class TestAgentClasses:
    """Test agent class structure"""
    
    def test_lite_agents_have_required_attributes(self):
        """Test that lite agents have required structure"""
        from src.agents.lite_model import ResearchAgentLite, PlanningAgentLite, ReviewAgentLite
        
        # Check class names are correct
        assert ResearchAgentLite.__name__ == "ResearchAgentLite"
        assert PlanningAgentLite.__name__ == "PlanningAgentLite"
        assert ReviewAgentLite.__name__ == "ReviewAgentLite"
    
    def test_pro_agents_have_required_attributes(self):
        """Test that pro agents have required structure"""
        from src.agents.pro_model import ResearchAgentPro, PlanningAgentPro, ReviewAgentPro
        
        # Check class names are correct
        assert ResearchAgentPro.__name__ == "ResearchAgentPro"
        assert PlanningAgentPro.__name__ == "PlanningAgentPro"
        assert ReviewAgentPro.__name__ == "ReviewAgentPro"
    
    def test_lite_and_pro_are_different_classes(self):
        """Test that lite and pro agents are actually different"""
        from src.agents.lite_model import ResearchAgentLite
        from src.agents.pro_model import ResearchAgentPro
        
        assert ResearchAgentLite != ResearchAgentPro
        assert ResearchAgentLite.__name__ != ResearchAgentPro.__name__


class TestDynamicLoading:
    """Test the dynamic agent loading mechanism"""
    
    def test_load_agents_for_model_function_exists(self):
        """Test that the loading function exists"""
        from src.agents.orchestrator_capstone import load_agents_for_model
        
        assert load_agents_for_model is not None
        assert callable(load_agents_for_model)
    
    def test_lite_model_loads_lite_agents(self):
        """Test that lite model loads lite agents"""
        from src.agents.orchestrator_capstone import load_agents_for_model
        
        original_model = Config.MODEL_NAME
        
        try:
            Config.MODEL_NAME = "gemini-2.5-flash-lite"
            ResearchAgent, PlanningAgent, ReviewAgent = load_agents_for_model()
            
            # Check that we got Lite versions
            assert "Lite" in ResearchAgent.__name__
            assert "Lite" in PlanningAgent.__name__
            assert "Lite" in ReviewAgent.__name__
        finally:
            Config.MODEL_NAME = original_model
    
    def test_pro_model_loads_pro_agents(self):
        """Test that pro model loads pro agents"""
        # Import Config from the SAME place orchestrator imports it
        import src.config
        from src.agents.orchestrator_capstone import load_agents_for_model
        
        original_model = src.config.Config.MODEL_NAME
        
        try:
            # Change Config in the module that orchestrator actually uses
            src.config.Config.MODEL_NAME = "gemini-2.5-flash"
            
            ResearchAgent, PlanningAgent, ReviewAgent = load_agents_for_model()
            
            # Check that we got Pro versions
            assert "Pro" in ResearchAgent.__name__
            assert "Pro" in PlanningAgent.__name__
            assert "Pro" in ReviewAgent.__name__
        finally:
            src.config.Config.MODEL_NAME = original_model
    
    def test_loading_returns_three_classes(self):
        """Test that loading returns exactly three agent classes"""
        from src.agents.orchestrator_capstone import load_agents_for_model
        
        result = load_agents_for_model()
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        
        # All should be classes
        for agent_class in result:
            assert isinstance(agent_class, type)

