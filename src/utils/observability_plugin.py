"""
Production-grade observability using ADK Plugin architecture.
Based on Day 4 course materials (notebook b52dd9c992_day4a and 676a366b69_day4b).

Implements comprehensive tracking via plugin callbacks:
- before/after_agent_callback: Track agent starts/completions with iterations
- before/after_tool_callback: Track all tool calls with classification
- before/after_model_callback: Track LLM requests
- on_model_error_callback: Track errors

This provides automatic, comprehensive observability without manual logging.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from rich.console import Console

console = Console()


class ObservabilityPlugin(BasePlugin):
    """
    ADK Plugin for comprehensive observability tracking.
    
    Automatically tracks:
    - Agent executions (with iterations)
    - Tool calls (with type classification)
    - LLM requests/responses
    - Errors and warnings
    - Performance timing
    - One-sentence summaries per agent
    """
    
    def __init__(self, session_id: str):
        super().__init__(name="observability_tracker")
        self.session_id = session_id
        self.start_time = datetime.now()
        
        # Core metrics
        self.metrics = {
            "session_id": session_id,
            "start_time": self.start_time.isoformat(),
            "agents_executed": [],
            "tool_calls": [],
            "errors": [],
            "warnings": [],
            "performance": {}
        }
        
        # Tracking state
        self.agent_start_times = {}
        self.agent_iteration_count = {}  # Track iterations per agent
        self.tool_start_times = {}
        
        console.print(f"[dim]🔍 Observability plugin initialized for session: {session_id}[/dim]")
    
    # ==================== AGENT CALLBACKS ====================
    
    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Track when an agent starts execution."""
        agent_name = agent.name
        
        # Track iteration count
        if agent_name not in self.agent_iteration_count:
            self.agent_iteration_count[agent_name] = 0
        self.agent_iteration_count[agent_name] += 1
        
        iteration = self.agent_iteration_count[agent_name]
        
        # Use unique key for each iteration
        timing_key = f"{agent_name}_iter{iteration}"
        self.agent_start_times[timing_key] = time.time()
        
        # Log start
        entry = {
            "agent": agent_name,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
        if iteration > 1:  # Only show iteration if > 1
            entry["iteration"] = iteration
            
        self.metrics["agents_executed"].append(entry)
        console.print(f"[cyan]▶️  {agent_name}: started{' (iteration ' + str(iteration) + ')' if iteration > 1 else ''}[/cyan]")
    
    async def after_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Track when an agent completes execution."""
        agent_name = agent.name
        iteration = self.agent_iteration_count.get(agent_name, 1)
        timing_key = f"{agent_name}_iter{iteration}"
        
        if timing_key in self.agent_start_times:
            duration = time.time() - self.agent_start_times[timing_key]
            
            # Generate summary
            summary = self._generate_agent_summary(agent_name, callback_context, iteration)
            
            # Log completion
            entry = {
                "agent": agent_name,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "duration": f"{duration:.2f}s",
                "summary": summary
            }
            if iteration > 1:
                entry["iteration"] = iteration
                
            self.metrics["agents_executed"].append(entry)
            
            # Update performance metrics
            perf_key = agent_name.lower().replace(" ", "_").replace("-", "_")
            if iteration > 1:
                perf_key += f"_iter{iteration}"
            self.metrics["performance"][perf_key] = f"{duration:.2f}s"
            
            console.print(f"[green]✅ {agent_name}: completed ({duration:.2f}s){' [iteration ' + str(iteration) + ']' if iteration > 1 else ''}[/green]")
            console.print(f"[dim]   → {summary}[/dim]")
    
    # ==================== TOOL CALLBACKS ====================
    
    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args, tool_context: ToolContext
    ) -> None:
        """Track when a tool is called."""
        tool_name = self._get_tool_name(tool)
        
        # Start timing
        timing_key = f"{tool_name}_{datetime.now().timestamp()}"
        self.tool_start_times[timing_key] = time.time()
        
        # Classify tool type
        tool_type = self._classify_tool_type(tool_name, tool_args)
        
        # Extract details
        details = self._extract_tool_details(tool_name, tool_args)
        
        # Log
        entry = {
            "tool": tool_name,
            "type": tool_type,
            "status": "called",
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "_timing_key": timing_key  # Internal use
        }
        
        self.metrics["tool_calls"].append(entry)
        
        # Display
        type_icon = {
            "file": "📁",
            "api": "🌐",
            "built-in": "🔧",
            "custom": "⚙️",
            "mcp": "🔌"
        }.get(tool_type, "🔧")
        
        console.print(f"[dim]  {type_icon} {tool_name}: called ({tool_type})[/dim]")
    
    async def after_tool_callback(
        self, *, tool: BaseTool, tool_args, tool_result, tool_context: ToolContext
    ) -> None:
        """Track tool completion."""
        tool_name = self._get_tool_name(tool)
        
        # Update last tool call with success status
        if self.metrics["tool_calls"]:
            for tool_call in reversed(self.metrics["tool_calls"]):
                if tool_call["tool"] == tool_name and tool_call["status"] == "called":
                    tool_call["status"] = "success"
                    
                    # Add timing if available
                    if "_timing_key" in tool_call:
                        timing_key = tool_call["_timing_key"]
                        if timing_key in self.tool_start_times:
                            duration = time.time() - self.tool_start_times[timing_key]
                            tool_call["duration"] = f"{duration:.2f}s"
                            del tool_call["_timing_key"]  # Clean up internal key
                    
                    break
        
        console.print(f"[dim]  ✅ {tool_name}: completed[/dim]")
    
    # ==================== MODEL CALLBACKS ====================
    
    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Track LLM requests."""
        # Optional: track model calls if needed
        pass
    
    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> None:
        """Track LLM responses."""
        # Optional: track model responses if needed
        pass
    
    async def on_model_error_callback(
        self, *, callback_context: CallbackContext, error: Exception
    ) -> None:
        """Track model errors."""
        self.metrics["errors"].append({
            "error": str(error),
            "context": "LLM call failed",
            "timestamp": datetime.now().isoformat()
        })
        console.print(f"[bold red]❌ Model error: {error}[/bold red]")
    
    # ==================== HELPER METHODS ====================
    
    def _get_tool_name(self, tool: BaseTool) -> str:
        """Get tool name from tool object."""
        if hasattr(tool, '__name__'):
            return tool.__name__
        elif hasattr(tool, 'name'):
            return tool.name
        else:
            return str(tool)
    
    def _classify_tool_type(self, tool_name: str, tool_args: Any) -> str:
        """
        Classify tool into categories.
        
        Categories:
        - file: File parsing tools
        - api: External API calls (weather, etc.)
        - built-in: ADK built-in tools (google_search, code_execution)
        - custom: Custom tools (maps, transport)
        - mcp: Model Context Protocol tools
        """
        tool_name_lower = tool_name.lower()
        
        if any(kw in tool_name_lower for kw in ["file", "parse", "read", "load"]):
            return "file"
        elif any(kw in tool_name_lower for kw in ["weather", "api", "http", "request"]):
            return "api"
        elif any(kw in tool_name_lower for kw in ["google_search", "search", "code_execution", "execute"]):
            return "built-in"
        elif any(kw in tool_name_lower for kw in ["maps", "transport", "export"]):
            return "custom"
        elif "mcp" in tool_name_lower:
            return "mcp"
        else:
            return "custom"
    
    def _extract_tool_details(self, tool_name: str, tool_args: Any) -> str:
        """Extract meaningful details from tool arguments."""
        tool_name_lower = tool_name.lower()
        
        if "parse" in tool_name_lower or "file" in tool_name_lower:
            if isinstance(tool_args, dict):
                if "file_path" in tool_args:
                    return f"Parsing file: {tool_args['file_path']}"
                elif "files" in tool_args:
                    return f"Parsing {len(tool_args['files'])} file(s)"
            return "Parsing reference files"
            
        elif "weather" in tool_name_lower:
            if isinstance(tool_args, dict):
                dest = tool_args.get("destination", "unknown")
                return f"Fetching weather for {dest}"
            return "Fetching weather data"
            
        elif "search" in tool_name_lower:
            if isinstance(tool_args, dict):
                query = tool_args.get("query", "unknown")
                return f"Searching: {query[:50]}"
            return "Web search"
            
        elif "maps" in tool_name_lower:
            return "Generating map links"
            
        elif "transport" in tool_name_lower:
            return "Getting transport info"
            
        elif "export" in tool_name_lower:
            return "Exporting itinerary"
        
        # Default: show first 50 chars of args
        return f"Args: {str(tool_args)[:50]}"
    
    def _generate_agent_summary(
        self, agent_name: str, context: CallbackContext, iteration: int
    ) -> str:
        """Generate a one-sentence summary of what the agent did."""
        agent_lower = agent_name.lower()
        
        if "research" in agent_lower:
            return f"Researched destination, gathered travel information"
        elif "planning" in agent_lower or "plan" in agent_lower:
            if iteration > 1:
                return f"Refined itinerary based on feedback (iteration {iteration})"
            return "Created detailed day-by-day itinerary"
        elif "review" in agent_lower:
            return f"Reviewed itinerary quality and provided feedback (iteration {iteration})"
        elif "exploration" in agent_lower or "explore" in agent_lower:
            return "Explored destination options and trip structures"
        else:
            return f"Executed {agent_name}"
    
    # ==================== WARNING/ERROR LOGGING ====================
    
    def log_warning(self, warning: str, context: str = ""):
        """Manual warning logging."""
        self.metrics["warnings"].append({
            "warning": warning,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        console.print(f"[yellow]⚠️  {warning}[/yellow]")
    
    def log_error(self, error: str, context: str = ""):
        """Manual error logging."""
        self.metrics["errors"].append({
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        console.print(f"[red]❌ Error: {error}[/red]")
    
    # ==================== FINALIZATION ====================
    
    def finalize(self, total_duration: float) -> Path:
        """Finalize metrics and save to file."""
        self.metrics["end_time"] = datetime.now().isoformat()
        self.metrics["performance"]["total_planning_time"] = f"{total_duration:.2f}s"
        
        # Save to logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"metrics_{timestamp}.json"
        
        with open(log_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
            
        console.print(f"\n📊 Metrics saved to: {log_file}")
        return log_file

