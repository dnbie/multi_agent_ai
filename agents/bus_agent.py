"""
Bus Route Agent - Search bus routes and schedules
Uses mock API for bus information
"""

from typing import Dict, List, Optional
from datetime import datetime
from .base_agent import BaseAgent, AgentResult


class BusAgent(BaseAgent):
    """
    Bus route search agent.
    Searches for bus routes and provides schedule information.
    """
    
    def __init__(self):
        super().__init__(
            name="Bus Route Agent",
            description="Search bus routes and schedules"
        )
        
        from tools.bus_api import BusAPI
        self.bus_api = BusAPI()
    
    def get_capabilities(self) -> List[str]:
        return [
            "Search bus routes",
            "Compare bus operators",
            "View schedules",
            "Check bus types and amenities",
            "Route planning"
        ]
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute bus search task.
        
        Args:
            task: Task description
            **kwargs: Additional parameters
                - origin: Origin city code
                - destination: Destination city code
                - date: Travel date
                - bus_type: Preferred bus type
                
        Returns:
            AgentResult with bus information
        """
        self._start_execution(task)
        result = self._create_result(False, "")
        
        try:
            # Extract parameters
            origin = kwargs.get("origin") or self._extract_city("from", task)
            destination = kwargs.get("destination") or self._extract_city("to", task)
            date = kwargs.get("date") or self._extract_date(task)
            bus_type = kwargs.get("bus_type")
            
            # Check if we have required info
            if not origin or not destination:
                cities = self.bus_api.get_cities()
                result = self._create_result(
                    False,
                    "Please specify origin and destination cities",
                    data={
                        "available_cities": cities.get("cities", []),
                        "example": "Search buses from DEL to JAI"
                    },
                    error="Missing origin or destination"
                )
                self._end_execution(result)
                return result
            
            result.add_step("search_buses", "started", {
                "origin": origin,
                "destination": destination,
                "date": date
            })
            
            # Search buses
            search_result = self.bus_api.search_routes(
                origin=origin,
                destination=destination,
                date=date,
                bus_type=bus_type
            )
            
            if search_result.get("success"):
                buses = search_result.get("buses", [])
                
                # Format bus information
                bus_summary = []
                for bus in buses[:8]:  # Top 8 options
                    bus_summary.append({
                        "operator": bus.get("operator"),
                        "type": bus.get("bus_type"),
                        "departure": bus.get("departure_time"),
                        "arrival": bus.get("arrival_time"),
                        "duration": bus.get("duration"),
                        "fare": bus.get('fare', 0),
                        "seats": bus.get("seats_available"),
                        "amenities": bus.get("amenities", [])
                    })
                
                # Format as text
                formatted_text = self.bus_api.format_route_text(search_result)
                
                result = self._create_result(
                    True,
                    f"Found {len(buses)} buses from {search_result['origin']['name']} to {search_result['destination']['name']}",
                    data={
                        "origin": search_result.get("origin"),
                        "destination": search_result.get("destination"),
                        "distance_km": search_result.get("distance_km"),
                        "date": search_result.get("date"),
                        "buses_found": len(buses),
                        "buses": bus_summary,
                        "formatted_text": formatted_text
                    }
                )
                result.add_step("search_buses", "success", {"buses_found": len(buses)})
            else:
                result = self._create_result(
                    False,
                    search_result.get("error", "Bus search failed"),
                    error=search_result.get("error")
                )
                result.add_step("search_buses", "failed")
            
        except Exception as e:
            result = self._create_result(
                False,
                f"Bus search error: {str(e)}",
                error=str(e)
            )
        
        self._end_execution(result)
        return result
    
    def _extract_city(self, direction: str, text: str) -> Optional[str]:
        """Extract city code from text"""
        import re
        text_upper = text.upper()

        # Check for full city names first (more reliable than raw 3-letter codes)
        city_names = {
            "DELHI": "DEL", "NEW DELHI": "DEL",
            "JAIPUR": "JAI",
            "AGRA": "AGR",
            "MUMBAI": "BOM", "BOMBAY": "BOM",
            "PUNE": "PUN",
            "BANGALORE": "BLR", "BENGALURU": "BLR",
            "MYSORE": "MYS", "MYSURU": "MYS",
            "HYDERABAD": "HYD",
            "CHENNAI": "CHE", "MADRAS": "CHE",
            "AHMEDABAD": "AHM",
            "LUCKNOW": "LKO",
            "KOLKATA": "KOL", "CALCUTTA": "KOL"
        }

        # Collect all city name matches sorted by position in text
        found_cities = []
        for name, code in city_names.items():
            if name in text_upper:
                pos = text_upper.index(name)
                found_cities.append((pos, code))
        found_cities.sort(key=lambda x: x[0])

        if found_cities:
            if direction == "from":
                return found_cities[0][1]
            elif direction == "to":
                return found_cities[1][1] if len(found_cities) > 1 else found_cities[0][1]

        # Fall back to 3-letter codes, filtering out common English words
        common_words = {"BUS", "FOR", "THE", "AND", "FROM", "VIA", "NEW", "CITY", "SHOW", "FIND"}
        codes = [c for c in re.findall(r'\b([A-Z]{3})\b', text_upper) if c not in common_words]

        if direction == "from" and codes:
            return codes[0]
        elif direction == "to" and len(codes) > 1:
            return codes[1]
        elif len(codes) == 1 and direction == "to":
            return codes[0]

        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        import re
        
        # Pattern for YYYY-MM-DD
        pattern = r'\d{4}-\d{2}-\d{2}'
        match = re.search(pattern, text)
        
        if match:
            return match.group(0)
        
        return None
    
    def get_route_details(self, origin: str, destination: str) -> AgentResult:
        """Get detailed route information"""
        self._start_execution(f"Get route: {origin} to {destination}")
        
        try:
            details = self.bus_api.get_route_details(origin, destination)
            
            if details.get("success"):
                result = self._create_result(
                    True,
                    f"Route details: {origin} to {destination}",
                    data=details
                )
            else:
                result = self._create_result(
                    False,
                    "Failed to get route details",
                    error=details.get("error")
                )
            
        except Exception as e:
            result = self._create_result(False, str(e), error=str(e))
        
        self._end_execution(result)
        return result
    
    def get_cities(self) -> Dict:
        """Get available cities"""
        return self.bus_api.get_cities()
    
    def get_bus_types(self) -> Dict:
        """Get available bus types"""
        return self.bus_api.get_bus_types()
