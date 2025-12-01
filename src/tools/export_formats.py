"""
Export utilities for trip itineraries.
Converts markdown itineraries to different formats.
"""

from src.models.trip_models import TripItinerary
from src.tools.itinerary_formatter import ItineraryFormatter
from datetime import datetime
from pathlib import Path
from rich.console import Console
from typing import Optional
import json

console = Console()


class ItineraryExporter:
    """
    Export itineraries to various formats.
    Currently supports: Markdown, JSON, Text
    Future: PDF, Google Calendar, Mobile JSON
    """
    
    @staticmethod
    def to_markdown(itinerary: TripItinerary, output_path: Optional[str] = None) -> str:
        """
        Export to Markdown (default format).
        
        Args:
            itinerary: The trip itinerary
            output_path: Optional path to save file
            
        Returns:
            Markdown string
        """
        md_content = ItineraryFormatter.to_markdown(itinerary)
        
        if output_path:
            Path(output_path).write_text(md_content, encoding='utf-8')
            console.print(f"[green]✅ Markdown saved to: {output_path}[/green]")
        
        return md_content
    
    @staticmethod
    def to_json(itinerary: TripItinerary, output_path: Optional[str] = None) -> str:
        """
        Export to JSON format (machine-readable).
        Useful for mobile apps or further processing.
        
        Args:
            itinerary: The trip itinerary
            output_path: Optional path to save file
            
        Returns:
            JSON string
        """
        # Convert Pydantic model to dict, handling dates
        def date_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        json_data = itinerary.model_dump(mode='json')
        json_str = json.dumps(json_data, indent=2, default=date_serializer)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
            console.print(f"[green]✅ JSON saved to: {output_path}[/green]")
        
        return json_str
    
    @staticmethod
    def to_plain_text(itinerary: TripItinerary, output_path: Optional[str] = None) -> str:
        """
        Export to plain text (no markdown formatting).
        Good for copying to simple text editors or emails.
        
        Args:
            itinerary: The trip itinerary
            output_path: Optional path to save file
            
        Returns:
            Plain text string
        """
        md_content = ItineraryFormatter.to_markdown(itinerary)
        
        # Strip markdown formatting
        text_content = md_content
        # Remove markdown headers
        text_content = text_content.replace('###', '')
        text_content = text_content.replace('##', '')
        text_content = text_content.replace('#', '')
        # Remove bold
        text_content = text_content.replace('**', '')
        # Remove italic
        text_content = text_content.replace('_', '')
        # Remove code blocks
        text_content = text_content.replace('`', '')
        # Clean up extra newlines
        while '\n\n\n' in text_content:
            text_content = text_content.replace('\n\n\n', '\n\n')
        
        if output_path:
            Path(output_path).write_text(text_content, encoding='utf-8')
            console.print(f"[green]✅ Plain text saved to: {output_path}[/green]")
        
        return text_content
    
    @staticmethod
    def export_all(itinerary: TripItinerary, output_dir: str = "output"):
        """
        Export to all available formats.
        
        Args:
            itinerary: The trip itinerary
            output_dir: Directory to save files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"itinerary_{timestamp}"
        
        # Export to each format
        ItineraryExporter.to_markdown(
            itinerary,
            str(output_path / f"{base_name}.md")
        )
        
        ItineraryExporter.to_json(
            itinerary,
            str(output_path / f"{base_name}.json")
        )
        
        ItineraryExporter.to_plain_text(
            itinerary,
            str(output_path / f"{base_name}.txt")
        )
        
        console.print(f"\n[bold green]✅ All formats exported to: {output_dir}/[/bold green]")
        console.print(f"  📄 {base_name}.md (Markdown)")
        console.print(f"  📊 {base_name}.json (JSON)")
        console.print(f"  📝 {base_name}.txt (Plain Text)")


# Convenience functions
def export_to_markdown(itinerary: TripItinerary, path: str):
    """Quick export to markdown"""
    return ItineraryExporter.to_markdown(itinerary, path)


def export_to_json(itinerary: TripItinerary, path: str):
    """Quick export to JSON"""
    return ItineraryExporter.to_json(itinerary, path)

