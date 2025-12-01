"""
Cross-session memory management for The Argonauts.
Enables persistence across multiple planning sessions.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from rich.console import Console

console = Console()


class PersistentSessionManager:
    """
    Manages sessions with persistence to disk.
    Allows resuming conversations and accessing past planning sessions.
    """
    
    def __init__(self, storage_dir: str = ".sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.in_memory_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        
        console.print(f"[dim]📁 Session storage: {self.storage_dir}[/dim]")
    
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """Save session data to disk"""
        session_file = self.storage_dir / f"{session_id}.json"
        
        # Add metadata
        data["saved_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        console.print(f"[dim]💾 Session saved: {session_id[:16]}...[/dim]")
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from disk"""
        session_file = self.storage_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        console.print(f"[dim]📂 Session loaded: {session_id[:16]}...[/dim]")
        return data
    
    def list_sessions(self) -> List[str]:
        """List all saved sessions"""
        sessions = []
        for session_file in self.storage_dir.glob("*.json"):
            sessions.append(session_file.stem)
        return sorted(sessions, reverse=True)
    
    def get_recent_sessions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent sessions with metadata"""
        sessions = []
        
        for session_file in sorted(
            self.storage_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            with open(session_file, 'r') as f:
                data = json.load(f)
                sessions.append({
                    "session_id": session_file.stem,
                    "destination": data.get("destination", "Unknown"),
                    "dates": data.get("dates", "Unknown"),
                    "saved_at": data.get("saved_at", "Unknown")
                })
        
        return sessions
    
    def save_trip_session(
        self,
        session_id: str,
        trip_input: Any,
        itinerary: Optional[Any] = None,
        metadata: Optional[Dict] = None
    ):
        """Save a complete trip planning session"""
        data = {
            "session_id": session_id,
            "destination": trip_input.destination,
            "dates": {
                "start": str(trip_input.dates.start_date),
                "end": str(trip_input.dates.end_date),
                "duration": trip_input.dates.duration_days
            },
            "preferences": {
                "interests": trip_input.preferences.interests,
                "budget": trip_input.preferences.budget_level,
                "pace": trip_input.preferences.pace_preference,
                "dietary": trip_input.preferences.dietary_restrictions
            }
        }
        
        if itinerary:
            data["itinerary_generated"] = True
            data["total_cost"] = itinerary.total_estimated_cost
        
        if metadata:
            data["metadata"] = metadata
        
        self.save_session(session_id, data)
    
    def display_session_history(self):
        """Display recent sessions"""
        recent = self.get_recent_sessions(limit=5)
        
        if not recent:
            console.print("[yellow]No previous sessions found[/yellow]")
            return
        
        from rich.table import Table
        
        table = Table(title="📚 Recent Planning Sessions")
        table.add_column("Destination", style="cyan")
        table.add_column("Dates", style="green")
        table.add_column("Session ID", style="dim")
        
        for session in recent:
            table.add_row(
                session["destination"],
                session["dates"],
                session["session_id"][:20] + "..."
            )
        
        console.print(table)


# Global session manager
_session_manager: Optional[PersistentSessionManager] = None


def get_session_manager() -> PersistentSessionManager:
    """Get or create the global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = PersistentSessionManager()
    return _session_manager

