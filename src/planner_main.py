#!/usr/bin/env python3
"""
Trip Planner Agent - Capstone Main Entry Point

This is a capstone project for the "5-Day AI Agents Intensive Course with Google"

Features Demonstrated:
✅ Multi-agent system (Research, Planning, Review, Orchestrator)
✅ Sequential agents (orchestrator coordinates workflow)
✅ Loop agent (review with iterative refinement)
✅ Built-in tools (google_search, code_execution)
✅ Sessions & Memory (InMemorySessionService, InMemoryMemoryService)
✅ Observability (logging, tracing, metrics)
✅ Agent evaluation (performance metrics, quality assessment)

Author: Liad
Course: Google AI Agents Intensive (Nov 2025)
"""

import asyncio
import sys
import yaml
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from src.config import Config
from src.models.trip_models import TripInput
from src.agents.orchestrator_capstone import OrchestratorAgentCapstone
from src.tools.itinerary_formatter import ItineraryFormatter
from src.evaluation.evaluator import TripPlannerEvaluator

console = Console()


def display_welcome():
    """Display welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🌍  AI TRIP PLANNER - CAPSTONE PROJECT  🌍        ║
║                                                           ║
║              Google ADK Multi-Agent System                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

[bold cyan]Capstone Features:[/bold cyan]
  ✅ Multi-Agent System (Research → Plan → Review)
  ✅ Sequential Agent Workflow
  ✅ Loop Agent (Iterative Refinement)
  ✅ Built-in ADK Tools (google_search)
  ✅ Sessions & Memory Management
  ✅ Observability (Metrics, Logging, Tracing)
  ✅ Agent Evaluation Framework
"""
    console.print(Panel(banner, border_style="green", expand=False))
    Config.print_config_info()


def load_trip_input(yaml_file: Path) -> TripInput:
    """Load trip input from YAML file"""
    console.print(f"\n[cyan]📂 Loading trip request from: {yaml_file}[/cyan]")
    
    from src.utils.error_handler import validate_trip_input
    
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    trip_input = TripInput(**data)
    
    # Validate the input
    validate_trip_input(trip_input)
    
    return trip_input


async def main_async(yaml_file: Path, output_dir: Path):
    """Main async workflow"""
    
    # Display welcome
    display_welcome()
    
    # Load input
    trip_input = load_trip_input(yaml_file)
    
    # Initialize orchestrator
    console.print("\n[bold green]🚀 Initializing Multi-Agent System...[/bold green]")
    orchestrator = OrchestratorAgentCapstone()
    
    # Plan trip
    console.print("\n[bold cyan]Starting Trip Planning Workflow...[/bold cyan]\n")
    
    try:
        itinerary = await orchestrator.plan_trip(trip_input)
        
        # Save output
        output_file = output_dir / f"itinerary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        markdown = ItineraryFormatter.to_markdown(itinerary)
        
        output_file.write_text(markdown)
        console.print(f"\n[green]✅ Itinerary saved to: {output_file}[/green]")
        
        # Evaluation (if enabled)
        if Config.ENABLE_EVALUATION:
            console.print("\n[bold blue]📊 Running Evaluation...[/bold blue]")
            evaluator = TripPlannerEvaluator()
            eval_results = evaluator.evaluate(
                trip_input=trip_input,
                itinerary=itinerary,
                metrics=orchestrator.get_evaluation_metrics()
            )
            
            # Save evaluation
            eval_file = output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            eval_file.write_text(json.dumps(eval_results, indent=2))
            console.print(f"[blue]📊 Evaluation saved to: {eval_file}[/blue]")
            
            # Display evaluation summary
            _display_evaluation_summary(eval_results)
        
        # Success!
        console.print(Panel.fit(
            "[bold green]🎉 TRIP PLANNING COMPLETE! 🎉[/bold green]\n\n"
            f"Your {itinerary.duration_days}-day itinerary for {itinerary.destination} is ready!\n"
            f"Estimated cost: ${itinerary.total_estimated_cost:.2f}\n\n"
            f"📄 Full itinerary: {output_file}\n"
            + (f"📊 Evaluation: {eval_file}\n" if Config.ENABLE_EVALUATION else ""),
            title="✅ Success",
            border_style="green"
        ))
        
        return 0
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        return 1


def _display_evaluation_summary(eval_results: dict):
    """Display evaluation results"""
    table = Table(title="📊 Evaluation Results", border_style="blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta")
    table.add_column("Rating", style="green")
    
    for category, score in eval_results.get("scores", {}).items():
        rating = "⭐" * int(score / 2)  # Convert 0-10 to 0-5 stars
        table.add_row(category.replace("_", " ").title(), f"{score}/10", rating)
    
    console.print(table)
    
    overall = eval_results.get("overall_score", 0)
    console.print(f"\n[bold]Overall Score: {overall}/10 {'⭐' * int(overall / 2)}[/bold]")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python -m src.planner_main <input.yaml> [output_dir][/yellow]")
        console.print("\n[cyan]Example:[/cyan]")
        console.print("  python -m src.planner_main examples/sample_input.yaml output/")
        console.print("\n[cyan]Tip:[/cyan]")
        console.print("  See examples/sample_input.yaml for input format")
        return 1
    
    # Parse arguments
    yaml_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output")
    
    # Validate input file
    if not yaml_file.exists():
        console.print(f"[red]❌ File not found: {yaml_file}[/red]")
        return 1
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run async main
    return asyncio.run(main_async(yaml_file, output_dir))


if __name__ == "__main__":
    sys.exit(main())

