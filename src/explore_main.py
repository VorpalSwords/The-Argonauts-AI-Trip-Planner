#!/usr/bin/env python3
"""
The Argonauts - Exploration Mode

Use this script when you don't know much about a destination and want
high-level recommendations before detailed planning.

Usage:
    python3 -m src.explore_main "Japan" 10 --interests culture food temples --budget mid-range
"""

import asyncio
import sys
from pathlib import Path

from src.agents.exploration_agent import ExplorationAgent
from rich.console import Console
from rich.panel import Panel
import argparse

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Explore a destination before detailed planning"
    )
    parser.add_argument("destination", help="Country or region to explore")
    parser.add_argument("days", type=int, help="Number of days for the trip")
    parser.add_argument(
        "--interests",
        nargs="+",
        default=[],
        help="Your interests (e.g., culture food temples nature)"
    )
    parser.add_argument(
        "--budget",
        choices=["budget", "mid-range", "luxury"],
        default="mid-range",
        help="Budget level"
    )
    
    args = parser.parse_args()
    
    # Run exploration
    agent = ExplorationAgent()
    result = asyncio.run(agent.explore(
        destination=args.destination,
        num_days=args.days,
        interests=args.interests,
        budget_level=args.budget
    ))
    
    # Display results
    console.print(Panel(
        result,
        title=f"🗺️  Exploration Report: {args.destination}",
        border_style="green",
        padding=(1, 2)
    ))
    
    console.print("\n[bold green]✅ Exploration complete![/bold green]")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print("1. Review the suggested trip structures above")
    console.print("2. Choose which cities/regions to include")
    console.print("3. Create a trip plan YAML with your chosen destinations")
    console.print("4. Run full planning: [bold]python3 -m src.planner_main your_trip.yaml[/bold]")


if __name__ == "__main__":
    main()

