"""
Error handling utilities for The Argonauts trip planner.
Provides graceful error handling and user-friendly messages.
"""

from rich.console import Console
from functools import wraps
import asyncio
from typing import Callable, Any

console = Console()


class TripPlannerError(Exception):
    """Base exception for trip planner errors"""
    pass


class InvalidInputError(TripPlannerError):
    """Raised when user input is invalid"""
    pass


class APIError(TripPlannerError):
    """Raised when external API calls fail"""
    pass


class AgentError(TripPlannerError):
    """Raised when an agent fails to complete its task"""
    pass


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for graceful error handling in agent methods.
    
    Usage:
        @handle_errors
        async def some_agent_method(self, ...):
            ...
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except InvalidInputError as e:
                console.print(f"[bold red]❌ Input Error:[/bold red] {e}")
                console.print("[yellow]Please check your input YAML file.[/yellow]")
                raise
            except APIError as e:
                console.print(f"[bold yellow]⚠️  API Error:[/bold yellow] {e}")
                console.print("[dim]Falling back to alternative methods...[/dim]")
                # Don't re-raise - let fallback handle it
                return None
            except AgentError as e:
                console.print(f"[bold red]❌ Agent Error:[/bold red] {e}")
                console.print("[yellow]The agent encountered an issue. Please try again.[/yellow]")
                raise
            except Exception as e:
                console.print(f"[bold red]❌ Unexpected Error:[/bold red] {e}")
                console.print("[dim]Stack trace for debugging:[/dim]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
                raise
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except InvalidInputError as e:
                console.print(f"[bold red]❌ Input Error:[/bold red] {e}")
                console.print("[yellow]Please check your input YAML file.[/yellow]")
                raise
            except APIError as e:
                console.print(f"[bold yellow]⚠️  API Error:[/bold yellow] {e}")
                console.print("[dim]Falling back to alternative methods...[/dim]")
                return None
            except Exception as e:
                console.print(f"[bold red]❌ Unexpected Error:[/bold red] {e}")
                console.print("[dim]Stack trace:[/dim]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
                raise
        return sync_wrapper


def validate_trip_input(trip_input: Any) -> None:
    """
    Validate trip input has required fields.
    
    Raises:
        InvalidInputError if validation fails
    """
    if not trip_input.destination:
        raise InvalidInputError("Destination is required")
    
    if not trip_input.dates:
        raise InvalidInputError("Dates are required")
    
    # Check if end_date is before start_date
    if trip_input.dates.end_date < trip_input.dates.start_date:
        raise InvalidInputError("End date must be after start date")
    
    if trip_input.dates.duration_days < 1:
        raise InvalidInputError("Trip duration must be at least 1 day")
    
    if trip_input.dates.duration_days > 365:
        raise InvalidInputError("Trip duration cannot exceed 365 days (really? that's not a trip, that's relocating!)")
    
    # Validate budget level
    valid_budgets = ["budget", "mid-range", "luxury"]
    if trip_input.preferences.budget_level not in valid_budgets:
        raise InvalidInputError(f"Budget level must be one of: {', '.join(valid_budgets)}")
    
    # Validate pace
    valid_paces = ["relaxed", "moderate", "fast"]
    if trip_input.preferences.pace_preference not in valid_paces:
        raise InvalidInputError(f"Pace must be one of: {', '.join(valid_paces)}")


def safe_file_parse(file_path: str, parser_func: Callable) -> Any:
    """
    Safely parse a file with error handling.
    
    Args:
        file_path: Path to file
        parser_func: Function to parse the file
        
    Returns:
        Parsed content or None if failed
    """
    try:
        return parser_func(file_path)
    except FileNotFoundError:
        console.print(f"[yellow]⚠️  File not found: {file_path}[/yellow]")
        return None
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not parse {file_path}: {e}[/yellow]")
        return None


def log_agent_event(agent_name: str, event_type: str, details: str = ""):
    """
    Log agent events for observability.
    
    Args:
        agent_name: Name of the agent
        event_type: Type of event (start, complete, error)
        details: Additional details
    """
    if event_type == "start":
        console.print(f"[cyan]▶️  {agent_name} starting... {details}[/cyan]")
    elif event_type == "complete":
        console.print(f"[green]✅ {agent_name} completed {details}[/green]")
    elif event_type == "error":
        console.print(f"[red]❌ {agent_name} error: {details}[/red]")
    else:
        console.print(f"[dim]ℹ️  {agent_name}: {details}[/dim]")

