"""
Google Maps URL generator for trip planning.
Generates searchable and direction links without needing an API key.
"""

from typing import List, Optional
import urllib.parse


class MapsHelper:
    """Helper for generating Google Maps URLs"""
    
    @staticmethod
    def search_url(query: str, location: Optional[str] = None) -> str:
        """
        Generate a Google Maps search URL.
        
        Args:
            query: What to search for (e.g., "Ichiran Ramen Shinjuku")
            location: Optional location context (e.g., "Tokyo, Japan")
            
        Returns:
            Google Maps search URL
        """
        if location:
            full_query = f"{query}, {location}"
        else:
            full_query = query
            
        encoded_query = urllib.parse.quote(full_query)
        return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"
    
    @staticmethod
    def directions_url(
        origin: str,
        destination: str,
        mode: str = "transit"
    ) -> str:
        """
        Generate a Google Maps directions URL.
        
        Args:
            origin: Starting location
            destination: Ending location
            mode: Transit mode (transit, driving, walking, bicycling)
            
        Returns:
            Google Maps directions URL
        """
        encoded_origin = urllib.parse.quote(origin)
        encoded_dest = urllib.parse.quote(destination)
        
        return (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={encoded_origin}"
            f"&destination={encoded_dest}"
            f"&travelmode={mode}"
        )
    
    @staticmethod
    def place_url(place_name: str, location: str) -> str:
        """
        Generate a URL that searches for a specific place.
        
        Args:
            place_name: Name of the place
            location: General location/city
            
        Returns:
            Google Maps search URL
        """
        return MapsHelper.search_url(place_name, location)
    
    @staticmethod
    def area_url(area_name: str, city: str) -> str:
        """
        Generate a URL for exploring an area/neighborhood.
        
        Args:
            area_name: Name of the area (e.g., "Shinjuku")
            city: City name (e.g., "Tokyo")
            
        Returns:
            Google Maps search URL
        """
        query = f"{area_name}, {city}"
        encoded = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/?api=1&query={encoded}"
    
    @staticmethod
    def create_maps_context(
        destination: str,
        attractions: List[str],
        restaurants: List[str]
    ) -> dict:
        """
        Create a context with Google Maps links for all locations.
        
        Args:
            destination: Main destination
            attractions: List of attractions
            restaurants: List of restaurants
            
        Returns:
            Dictionary with maps links
        """
        context = {
            "destination_overview": MapsHelper.area_url(destination, destination),
            "attractions": {},
            "restaurants": {}
        }
        
        for attraction in attractions:
            context["attractions"][attraction] = MapsHelper.search_url(
                attraction, destination
            )
        
        for restaurant in restaurants:
            context["restaurants"][restaurant] = MapsHelper.search_url(
                restaurant, destination
            )
        
        return context

