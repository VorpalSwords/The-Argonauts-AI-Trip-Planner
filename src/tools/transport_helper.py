"""
Transportation helper for providing transit pass information and booking suggestions.
Helps travelers navigate local transportation systems efficiently.
"""

from typing import Dict, List, Optional
from datetime import date


class TransportHelper:
    """
    Provides transportation recommendations and pass information.
    No real-time booking, but gives practical guidance.
    """
    
    # Transit pass information for major destinations
    TRANSIT_PASSES = {
        "tokyo": {
            "passes": [
                {
                    "name": "Suica Card",
                    "type": "Rechargeable IC card",
                    "cost": "¥2,000 (¥500 deposit + ¥1,500 balance)",
                    "coverage": "Tokyo Metro, JR lines, buses, convenience stores",
                    "how_to_get": "Purchase at any major station (Narita Airport, Tokyo Station, Shinjuku)",
                    "notes": "Essential for Tokyo travel. Tap and go on all transit."
                },
                {
                    "name": "Tokyo Metro 24/48/72-hour Pass",
                    "type": "Unlimited subway pass",
                    "cost": "¥600 (24h), ¥1,200 (48h), ¥1,500 (72h)",
                    "coverage": "Tokyo Metro lines only (not JR)",
                    "how_to_get": "Metro stations, some convenience stores",
                    "notes": "Good if staying in Tokyo Metro zones. Calculate if worth it vs Suica."
                },
                {
                    "name": "JR Tokyo Wide Pass",
                    "type": "3-day unlimited pass",
                    "cost": "¥10,180",
                    "coverage": "JR lines in Greater Tokyo, Nikko, Hakone, Mount Fuji area",
                    "how_to_get": "JR stations",
                    "notes": "Only worth it for day trips outside Tokyo."
                }
            ],
            "recommendations": [
                "For most travelers: Suica card is simplest and most flexible",
                "If doing 4+ subway rides per day: Consider 72-hour Metro pass",
                "Download: Google Maps works perfectly for Tokyo transit"
            ]
        },
        "kyoto": {
            "passes": [
                {
                    "name": "ICOCA Card",
                    "type": "Rechargeable IC card (Kansai region version of Suica)",
                    "cost": "¥2,000 (¥500 deposit + ¥1,500 balance)",
                    "coverage": "Buses, trains, subways in Kyoto, Osaka, Nara",
                    "how_to_get": "Kyoto Station, Osaka stations",
                    "notes": "Suica cards also work in Kyoto. ICOCA is local equivalent."
                },
                {
                    "name": "Kyoto City Bus 1-Day Pass",
                    "type": "Unlimited bus pass",
                    "cost": "¥700",
                    "coverage": "Kyoto City buses (most tourist attractions)",
                    "how_to_get": "Bus station, some hotels",
                    "notes": "Great value if visiting 3+ temples/areas by bus per day."
                }
            ],
            "recommendations": [
                "Buses are main transit in Kyoto (fewer train lines than Tokyo)",
                "Bus pass is excellent value for temple-hopping",
                "Many areas are walkable - beautiful neighborhoods to explore on foot"
            ]
        },
        "osaka": {
            "passes": [
                {
                    "name": "ICOCA Card",
                    "type": "Rechargeable IC card",
                    "cost": "¥2,000 (¥500 deposit + ¥1,500 balance)",
                    "coverage": "Osaka Metro, JR, buses",
                    "how_to_get": "Osaka Station, Namba Station",
                    "notes": "Works across Kansai region."
                },
                {
                    "name": "Osaka Amazing Pass",
                    "type": "1 or 2-day pass with free attractions",
                    "cost": "¥2,800 (1-day), ¥3,600 (2-day)",
                    "coverage": "Unlimited subway/bus + 40+ free attractions",
                    "how_to_get": "Tourist centers, major stations",
                    "notes": "Great value if visiting multiple attractions."
                }
            ],
            "recommendations": [
                "Osaka is compact - lots of areas are walkable",
                "Amazing Pass is excellent value for sightseeing days",
                "ICOCA card works for day trips to Nara, Kobe"
            ]
        },
        "japan": {
            "inter_city": [
                {
                    "name": "JR Pass (Japan Rail Pass)",
                    "type": "7, 14, or 21-day unlimited JR trains",
                    "cost": "¥50,000 (7-day), ¥80,000 (14-day), ¥100,000 (21-day)",
                    "coverage": "All JR trains including most Shinkansen",
                    "how_to_get": "Must purchase BEFORE arriving in Japan (exchange order)",
                    "notes": "Worth it if doing Tokyo-Kyoto-Osaka + more. Calculate based on your routes.",
                    "booking": "Buy online 3 months to 1 week before travel. Exchange at airport/major station."
                }
            ],
            "recommendations": [
                "JR Pass calculation: Tokyo-Kyoto round trip = ~¥26,000. If doing this + more, pass pays off",
                "Book Shinkansen seats in advance during peak seasons (cherry blossom, fall)",
                "Consider purchasing individual tickets if only 1-2 long journeys"
            ]
        }
    }
    
    @staticmethod
    def get_transit_recommendations(
        city: str,
        num_days: int,
        budget_level: str = "mid-range"
    ) -> Dict:
        """
        Get transit pass recommendations for a city.
        
        Args:
            city: City name
            num_days: Number of days in the city
            budget_level: Budget constraints
            
        Returns:
            Dictionary with pass options and recommendations
        """
        city_lower = city.lower()
        
        # Find matching city data
        city_data = None
        for key in TransportHelper.TRANSIT_PASSES:
            if key in city_lower or city_lower in key:
                city_data = TransportHelper.TRANSIT_PASSES[key]
                break
        
        if not city_data:
            return {
                "city": city,
                "note": "No specific transit pass data available. Check local tourism websites.",
                "general_advice": [
                    "Look for rechargeable IC cards (like Suica in Tokyo)",
                    "Many cities offer day passes for unlimited transit",
                    "Google Maps usually shows best public transit routes"
                ]
            }
        
        return {
            "city": city,
            "passes": city_data.get("passes", []),
            "recommendations": city_data.get("recommendations", []),
            "inter_city": city_data.get("inter_city", [])
        }
    
    @staticmethod
    def format_transit_guide(city: str, num_days: int) -> str:
        """
        Format transit recommendations as readable text.
        
        Args:
            city: City name
            num_days: Stay duration
            
        Returns:
            Formatted transit guide
        """
        info = TransportHelper.get_transit_recommendations(city, num_days)
        
        output = f"\n**🚇 Transportation Guide for {city.title()}**\n\n"
        
        if "passes" in info and info["passes"]:
            output += "**Transit Pass Options:**\n\n"
            for pass_info in info["passes"]:
                output += f"**{pass_info['name']}**\n"
                output += f"- Type: {pass_info['type']}\n"
                output += f"- Cost: {pass_info['cost']}\n"
                output += f"- Coverage: {pass_info['coverage']}\n"
                output += f"- Where to buy: {pass_info['how_to_get']}\n"
                output += f"- Notes: {pass_info['notes']}\n\n"
        
        if "inter_city" in info and info["inter_city"]:
            output += "**Inter-City Travel:**\n\n"
            for option in info["inter_city"]:
                output += f"**{option['name']}**\n"
                output += f"- Type: {option['type']}\n"
                output += f"- Cost: {option['cost']}\n"
                output += f"- Coverage: {option['coverage']}\n"
                if "booking" in option:
                    output += f"- Booking: {option['booking']}\n"
                output += f"- Notes: {option['notes']}\n\n"
        
        if "recommendations" in info and info["recommendations"]:
            output += "**Recommendations:**\n"
            for rec in info["recommendations"]:
                output += f"- {rec}\n"
            output += "\n"
        
        return output
    
    @staticmethod
    def get_japan_transit_overview(cities: List[str]) -> str:
        """
        Get comprehensive transit guide for multi-city Japan trip.
        
        Args:
            cities: List of cities being visited
            
        Returns:
            Complete transit strategy
        """
        output = "\n**🚅 Japan Transportation Strategy**\n\n"
        
        # JR Pass consideration
        if len(cities) > 1:
            output += "**Inter-City Travel (Shinkansen):**\n\n"
            output += "**JR Pass**: ¥50,000 (7-day) or ¥80,000 (14-day)\n"
            output += "- Unlimited JR trains including most Shinkansen\n"
            output += "- **Worth it if**: Tokyo-Kyoto-Osaka + additional trips\n"
            output += "- **Not worth it if**: Only doing Tokyo-Kyoto round trip (¥26,000 total)\n"
            output += "- **IMPORTANT**: Must buy BEFORE arriving in Japan\n"
            output += "- Booking: Purchase online 3 months to 1 week before departure\n\n"
            
            output += "**Individual Ticket Costs** (for comparison):\n"
            output += "- Tokyo → Kyoto: ¥13,320 (2h 15m)\n"
            output += "- Kyoto → Osaka: ¥560 (30 min)\n"
            output += "- Osaka → Tokyo: ¥13,870 (2h 30m)\n\n"
        
        # City-specific passes
        for city in cities:
            city_info = TransportHelper.get_transit_recommendations(city, 0)
            if city_info.get("passes"):
                output += f"**In {city.title()}:**\n"
                # Just mention the essential pass
                main_pass = city_info["passes"][0]
                output += f"- Get a **{main_pass['name']}** ({main_pass['cost']}) for local transit\n"
        
        output += "\n**General Tips:**\n"
        output += "- IC cards (Suica/ICOCA) work nationwide in Japan\n"
        output += "- Google Maps is accurate for Japanese transit\n"
        output += "- Trains are punctual - arrive 5 minutes early\n"
        output += "- Reserve Shinkansen seats during peak season\n\n"
        
        return output


# Convenience function
def get_transport_guide(city: str, num_days: int) -> str:
    """Quick access to transport guide"""
    return TransportHelper.format_transit_guide(city, num_days)

