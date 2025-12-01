"""
Enhanced observability for The Argonauts trip planner.
Provides detailed logging, metrics tracking, and performance monitoring.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import json
from pathlib import Path

console = Console()


class ObservabilityTracker:
    """
    Tracks agent execution metrics for observability and debugging.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.metrics = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "agents_executed": [],
            "tool_calls": [],
            "errors": [],
            "warnings": [],
            "performance": {}
        }
        self.timers = {}
    
    def start_timer(self, name: str):
        """Start timing an operation"""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End timing and return duration"""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            self.metrics["performance"][name] = f"{duration:.2f}s"
            return duration
        return 0.0
    
    def log_agent_execution(
        self,
        agent_name: str,
        status: str,
        duration: Optional[float] = None,
        details: Optional[str] = None
    ):
        """Log agent execution"""
        entry = {
            "agent": agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if duration:
            entry["duration"] = f"{duration:.2f}s"
        if details:
            entry["details"] = details
        
        self.metrics["agents_executed"].append(entry)
        
        # Display
        status_emoji = {"started": "▶️", "completed": "✅", "failed": "❌"}.get(status, "ℹ️")
        duration_str = f" ({duration:.2f}s)" if duration else ""
        console.print(f"[cyan]{status_emoji} {agent_name}: {status}{duration_str}[/cyan]")
    
    def log_tool_call(self, tool_name: str, status: str, details: Optional[str] = None):
        """Log tool usage"""
        entry = {
            "tool": tool_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            entry["details"] = details
        
        self.metrics["tool_calls"].append(entry)
        
        # Display
        if status == "success":
            console.print(f"  [dim]🔧 {tool_name}: ✅[/dim]")
        elif status == "failed":
            console.print(f"  [yellow]🔧 {tool_name}: ⚠️  {details}[/yellow]")
    
    def log_error(self, error: str, context: Optional[str] = None):
        """Log an error"""
        entry = {
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        if context:
            entry["context"] = context
        
        self.metrics["errors"].append(entry)
        console.print(f"[red]❌ Error: {error}[/red]")
    
    def log_warning(self, warning: str, context: Optional[str] = None):
        """Log a warning"""
        entry = {
            "warning": warning,
            "timestamp": datetime.now().isoformat()
        }
        if context:
            entry["context"] = context
        
        self.metrics["warnings"].append(entry)
        console.print(f"[yellow]⚠️  {warning}[/yellow]")
    
    def display_summary(self):
        """Display execution summary"""
        table = Table(title="🔍 Execution Metrics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        # Add metrics
        table.add_row("Session ID", self.session_id[:16] + "...")
        table.add_row("Agents Executed", str(len(self.metrics["agents_executed"])))
        table.add_row("Tool Calls", str(len(self.metrics["tool_calls"])))
        table.add_row("Errors", str(len(self.metrics["errors"])))
        table.add_row("Warnings", str(len(self.metrics["warnings"])))
        
        # Performance
        if self.metrics["performance"]:
            for key, value in self.metrics["performance"].items():
                table.add_row(f"⏱️  {key}", value)
        
        console.print(table)
    
    def save_metrics(self, output_dir: str = "logs"):
        """Save metrics to file"""
        log_dir = Path(output_dir)
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"metrics_{timestamp}.json"
        
        self.metrics["end_time"] = datetime.now().isoformat()
        
        with open(log_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        console.print(f"[dim]📊 Metrics saved to: {log_file}[/dim]")


class PerformanceMonitor:
    """Monitor performance of agent executions"""
    
    def __init__(self):
        self.metrics = {
            "agent_timings": {},
            "tool_timings": {},
            "total_tokens": 0,
            "api_calls": 0
        }
    
    def record_agent_time(self, agent_name: str, duration: float):
        """Record agent execution time"""
        if agent_name not in self.metrics["agent_timings"]:
            self.metrics["agent_timings"][agent_name] = []
        self.metrics["agent_timings"][agent_name].append(duration)
    
    def record_tool_time(self, tool_name: str, duration: float):
        """Record tool execution time"""
        if tool_name not in self.metrics["tool_timings"]:
            self.metrics["tool_timings"][tool_name] = []
        self.metrics["tool_timings"][tool_name].append(duration)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        summary = {}
        
        # Average agent times
        for agent, times in self.metrics["agent_timings"].items():
            avg = sum(times) / len(times)
            summary[f"{agent}_avg"] = f"{avg:.2f}s"
        
        # Average tool times
        for tool, times in self.metrics["tool_timings"].items():
            avg = sum(times) / len(times)
            summary[f"{tool}_avg"] = f"{avg:.2f}s"
        
        return summary
    
    def display_performance(self):
        """Display performance metrics"""
        console.print("\n[bold]📊 Performance Metrics[/bold]\n")
        
        if self.metrics["agent_timings"]:
            console.print("[cyan]Agent Execution Times:[/cyan]")
            for agent, times in self.metrics["agent_timings"].items():
                avg = sum(times) / len(times)
                console.print(f"  • {agent}: {avg:.2f}s (avg of {len(times)} runs)")
        
        if self.metrics["tool_timings"]:
            console.print("\n[cyan]Tool Execution Times:[/cyan]")
            for tool, times in self.metrics["tool_timings"].items():
                avg = sum(times) / len(times)
                console.print(f"  • {tool}: {avg:.2f}s (avg of {len(times)} calls)")


# Global tracker instance
_current_tracker: Optional[ObservabilityTracker] = None


def get_tracker(session_id: Optional[str] = None) -> ObservabilityTracker:
    """Get or create observability tracker"""
    global _current_tracker
    if _current_tracker is None:
        sid = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        _current_tracker = ObservabilityTracker(sid)
    return _current_tracker


def reset_tracker():
    """Reset the global tracker"""
    global _current_tracker
    _current_tracker = None

