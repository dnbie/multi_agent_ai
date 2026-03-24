"""
Flight Search Agent - Search flights and plan itineraries
Uses mock API for flight information
"""

from typing import Dict, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentResult


class FlightAgent(BaseAgent):
    """
    Flight search and itinerary planning agent.
    Searches for flights and creates travel itineraries.
    """
    
    def __init__(self):
        super().__init__(
            name="Flight Search Agent",
            description="Search flights and plan travel itineraries"
        )
        
        from tools.flight_api import FlightAPI
        self.flight_api = FlightAPI()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Search available flights",
            "Compare flight prices",
            "Create travel itineraries",
            "Multi-city trip planning",
            "View flight details"
        ]
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute flight search task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
                - origin: Origin airport code
                - destination: Destination airport code
                - date: Travel date (YYYY-MM-DD)
                - passengers: Number of passengers
                - travel_class: economy/business/first
                
        Returns:
            AgentResult with flight information
        """
        self._start_execution(task)
        result = self._create_result(False, "")
        
        try:
            # Extract parameters
            origin = kwargs.get("origin") or self._extract_location("from", task)
            destination = kwargs.get("destination") or self._extract_location("to", task)
            date = kwargs.get("date") or self._extract_date(task)
            passengers = kwargs.get("passengers", 1)
            travel_class = kwargs.get("travel_class", "economy")
            
            # Use current date if not specified
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Check if we have required info
            if not origin or not destination:
                # Show available airports
                airports = self.flight_api.get_airports()
                result = self._create_result(
                    False,
                    "Please specify origin and destination airports",
                    data={
                        "available_airports": airports.get("airports", []),
                        "example": "Search flights from DEL to BOM on 2026-03-20"
                    },
                    error="Missing origin or destination"
                )
                self._end_execution(result)
                return result
            
            result.add_step("search_flights", "started", {
                "origin": origin,
                "destination": destination,
                "date": date
            })
            
            # Search flights
            search_result = self.flight_api.search_flights(
                origin=origin,
                destination=destination,
                date=date,
                passengers=passengers,
                travel_class=travel_class
            )
            
            if search_result.get("success"):
                flights = search_result.get("flights", [])
                
                # Format flight information
                flight_summary = []
                for flight in flights[:5]:  # Top 5 flights
                    flight_summary.append({
                        "flight": flight.get("flight_number"),
                        "airline": flight.get("airline"),
                        "departure": flight.get("departure_time"),
                        "arrival": flight.get("arrival_time"),
                        "duration": flight.get("duration"),
                        "price": flight.get('price', 0),
                        "seats": flight.get("seats_available")
                    })
                
                result = self._create_result(
                    True,
                    f"Found {len(flights)} flights from {origin} to {destination}",
                    data={
                        "search_id": search_result.get("search_id"),
                        "origin": search_result.get("origin"),
                        "destination": search_result.get("destination"),
                        "date": date,
                        "flights_found": len(flights),
                        "flights": flight_summary,
                        "all_flights": flights
                    }
                )
                result.add_step("search_flights", "success", {"flights_found": len(flights)})
            else:
                result = self._create_result(
                    False,
                    search_result.get("error", "Flight search failed"),
                    error=search_result.get("error")
                )
                result.add_step("search_flights", "failed")
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Flight search error: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def _extract_airport(self, direction: str, text: str) -> Optional[str]:
        """Extract airport code from text (legacy helper)."""
        import re
        text_upper = text.upper()
        
        # Look for 3-letter codes
        codes = re.findall(r'\b([A-Z]{3})\b', text_upper)
        
        if direction == "from" and codes:
            return codes[0]
        elif direction == "to" and len(codes) > 1:
            return codes[1]
        elif len(codes) == 1:
            return codes[0]
        
        return None

    def _extract_location(self, direction: str, text: str) -> Optional[str]:
        """Extract origin/destination location phrase from text (city name or airport code)."""
        import re

        # First try explicit airport code extraction for backward compatibility.
        code = self._extract_airport(direction, text)
        if code:
            return code

        lower_text = text.lower().strip()

        if direction == "from":
            # Examples: "from delhi to mumbai", "from bengaluru on 2026-04-01"
            patterns = [
                r"\bfrom\s+([a-zA-Z\s\.-]+?)\s+to\b",
                r"\bfrom\s+([a-zA-Z\s\.-]+?)\s+on\b",
                r"\bfrom\s+([a-zA-Z\s\.-]+?)\s+for\b",
                r"\bfrom\s+([a-zA-Z\s\.-]+)$"
            ]
        else:
            # Examples: "to mumbai on 2026-04-01", "to mumabi"
            patterns = [
                r"\bto\s+([a-zA-Z\s\.-]+?)\s+on\b",
                r"\bto\s+([a-zA-Z\s\.-]+?)\s+for\b",
                r"\bto\s+([a-zA-Z\s\.-]+?)\s+in\b",
                r"\bto\s+([a-zA-Z\s\.-]+)$"
            ]

        for pattern in patterns:
            match = re.search(pattern, lower_text)
            if match:
                candidate = match.group(1).strip(" .,-")
                if candidate:
                    return candidate

        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        import re
        
        # Pattern for YYYY-MM-DD
        pattern = r'\d{4}-\d{2}-\d{2}'
        match = re.search(pattern, text)
        
        if match:
            return match.group(0)
        
        # Pattern for DD/MM/YYYY
        pattern2 = r'(\d{2})/(\d{2})/(\d{4})'
        match2 = re.search(pattern2, text)
        
        if match2:
            return f"{match2.group(3)}-{match2.group(2)}-{match2.group(1)}"
        
        return None
    
    def create_itinerary(
        self,
        trips: List[Dict],
        traveler_name: str = "Traveler"
    ) -> AgentResult:
        """
        Create a multi-leg travel itinerary.
        
        Args:
            trips: List of trip specifications
            traveler_name: Name of traveler
            
        Returns:
            AgentResult with itinerary
        """
        self._start_execution(f"Create itinerary for {traveler_name}")
        
        try:
            itinerary = self.flight_api.create_itinerary(trips, traveler_name)
            
            if itinerary.get("success"):
                formatted = self.flight_api.format_itinerary_text(itinerary)
                
                result = self._create_result(
                    True,
                    f"Itinerary created: {itinerary.get('itinerary_id')}",
                    data={
                        "itinerary": itinerary,
                        "formatted_text": formatted,
                        "total_cost": itinerary.get("total_cost")
                    }
                )
            else:
                result = self._create_result(
                    False,
                    "Failed to create itinerary",
                    error=itinerary.get("error")
                )
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Itinerary creation failed: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def get_airports(self) -> Dict:
        """Get list of available airports"""
        return self.flight_api.get_airports()
