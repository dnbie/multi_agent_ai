"""
Bus API - Bus Route Search Module
Provides bus route information and schedule search
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path


class BusAPI:
    """
    Bus route search API using mock data.
    Simulates real bus route information system.
    """
    
    # Mock bus operators
    BUS_OPERATORS = [
        {"id": "RSRTC", "name": "Rajasthan State Road Transport"},
        {"id": "KSRTC", "name": "Karnataka State Road Transport"},
        {"id": "MSRTC", "name": "Maharashtra State Road Transport"},
        {"id": "APSRTC", "name": "Andhra Pradesh State Road Transport"},
        {"id": "TSRTC", "name": "Telangana State Road Transport"},
        {"id": "VRL", "name": "VRL Travels"},
        {"id": "SRS", "name": "SRS Travels"},
        {"id": "ORANGE", "name": "Orange Travels"},
        {"id": "NEETA", "name": "Neeta Travels"},
        {"id": "HANS", "name": "Hans Travels"}
    ]
    
    # Mock cities and routes
    CITIES = {
        "DEL": {"name": "Delhi", "state": "Delhi"},
        "JAI": {"name": "Jaipur", "state": "Rajasthan"},
        "AGR": {"name": "Agra", "state": "Uttar Pradesh"},
        "BOM": {"name": "Mumbai", "state": "Maharashtra"},
        "PUN": {"name": "Pune", "state": "Maharashtra"},
        "BLR": {"name": "Bangalore", "state": "Karnataka"},
        "MYS": {"name": "Mysore", "state": "Karnataka"},
        "HYD": {"name": "Hyderabad", "state": "Telangana"},
        "CHE": {"name": "Chennai", "state": "Tamil Nadu"},
        "CBE": {"name": "Coimbatore", "state": "Tamil Nadu"},
        "MDU": {"name": "Madurai", "state": "Tamil Nadu"},
        "TVC": {"name": "Thiruvananthapuram", "state": "Kerala"},
        "GOA": {"name": "Goa", "state": "Goa"},
        "MNG": {"name": "Mangalore", "state": "Karnataka"},
        "AHM": {"name": "Ahmedabad", "state": "Gujarat"},
        "LKO": {"name": "Lucknow", "state": "Uttar Pradesh"},
        "KOL": {"name": "Kolkata", "state": "West Bengal"}
    }
    
    # Distance matrix (approximate km)
    DISTANCES = {
        ("DEL", "JAI"): 280,
        ("DEL", "AGR"): 230,
        ("DEL", "LKO"): 550,
        ("BOM", "PUN"): 150,
        ("BOM", "AHM"): 530,
        ("BLR", "MYS"): 145,
        ("BLR", "CHE"): 350,
        ("HYD", "BLR"): 570,
        ("HYD", "CHE"): 630,
        ("JAI", "AHM"): 660,
        ("CHE", "CBE"): 505,
        ("CHE", "MDU"): 460,
        ("CBE", "MDU"): 210,
        ("CBE", "BLR"): 365,
        ("BLR", "GOA"): 560,
        ("BLR", "MNG"): 350,
        ("CHE", "HYD"): 630,
        ("CBE", "TVC"): 430,
        ("MDU", "TVC"): 310,
        ("BOM", "GOA"): 590
    }
    
    # Bus types
    BUS_TYPES = [
        {"type": "ORDINARY", "name": "Ordinary", "multiplier": 1.0},
        {"type": "EXPRESS", "name": "Express", "multiplier": 1.3},
        {"type": "DELUXE", "name": "Deluxe", "multiplier": 1.5},
        {"type": "AC_SEATER", "name": "AC Seater", "multiplier": 2.0},
        {"type": "AC_SLEEPER", "name": "AC Sleeper", "multiplier": 2.5},
        {"type": "VOLVO", "name": "Volvo Multi-Axle", "multiplier": 3.0}
    ]
    
    def __init__(self, data_file: str = None):
        """
        Initialize Bus API.
        
        Args:
            data_file: Optional JSON file with bus route data
        """
        self.data_file = data_file
        self.custom_routes = []
        
        if data_file:
            self._load_custom_routes()
    
    def _load_custom_routes(self):
        """Load custom routes from JSON file"""
        try:
            path = Path(self.data_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self.custom_routes = json.load(f)
        except Exception:
            self.custom_routes = []
    
    def _get_distance(self, origin: str, destination: str) -> int:
        """Get distance between two cities"""
        key = (origin, destination)
        reverse_key = (destination, origin)
        
        if key in self.DISTANCES:
            return self.DISTANCES[key]
        elif reverse_key in self.DISTANCES:
            return self.DISTANCES[reverse_key]
        else:
            # Estimate distance
            return random.randint(200, 800)
    
    def search_routes(
        self,
        origin: str,
        destination: str,
        date: str = None,
        bus_type: str = None
    ) -> Dict[str, any]:
        """
        Search for bus routes.
        
        Args:
            origin: Origin city code
            destination: Destination city code
            date: Travel date (YYYY-MM-DD)
            bus_type: Type of bus (ORDINARY, EXPRESS, DELUXE, AC_SEATER, AC_SLEEPER, VOLVO)
            
        Returns:
            Search results with available buses
        """
        origin = origin.upper()
        destination = destination.upper()
        
        # Validate cities
        if origin not in self.CITIES:
            return {
                "success": False,
                "error": f"Unknown origin city: {origin}",
                "available_cities": list(self.CITIES.keys())
            }
        
        if destination not in self.CITIES:
            return {
                "success": False,
                "error": f"Unknown destination city: {destination}",
                "available_cities": list(self.CITIES.keys())
            }
        
        if origin == destination:
            return {
                "success": False,
                "error": "Origin and destination cannot be the same"
            }
        
        # Parse date
        if date:
            try:
                travel_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return {
                    "success": False,
                    "error": "Invalid date format. Use YYYY-MM-DD"
                }
        else:
            travel_date = datetime.now()
        
        # Generate buses
        buses = self._generate_buses(origin, destination, travel_date, bus_type)
        
        return {
            "success": True,
            "origin": {
                "code": origin,
                **self.CITIES[origin]
            },
            "destination": {
                "code": destination,
                **self.CITIES[destination]
            },
            "date": travel_date.strftime("%Y-%m-%d"),
            "distance_km": self._get_distance(origin, destination),
            "buses_found": len(buses),
            "buses": buses
        }
    
    def _generate_buses(
        self,
        origin: str,
        destination: str,
        date: datetime,
        bus_type: str = None
    ) -> List[Dict]:
        """Generate mock bus data"""
        buses = []
        distance = self._get_distance(origin, destination)
        
        # Base fare per km
        base_fare_per_km = 1.5
        
        # Generate multiple departure times
        departure_times = [
            "06:00", "07:30", "09:00", "11:00", "13:30",
            "15:00", "17:00", "19:00", "21:00", "22:30"
        ]
        
        # Filter bus types if specified
        bus_types = self.BUS_TYPES
        if bus_type:
            bus_types = [bt for bt in self.BUS_TYPES if bt["type"] == bus_type.upper()]
            if not bus_types:
                bus_types = self.BUS_TYPES
        
        # Generate buses
        num_buses = random.randint(5, 10)
        
        for i in range(num_buses):
            operator = random.choice(self.BUS_OPERATORS)
            bt = random.choice(bus_types)
            dep_time = departure_times[i % len(departure_times)]
            
            # Calculate duration (assuming average speed varies by bus type)
            avg_speeds = {
                "ORDINARY": 40, "EXPRESS": 50, "DELUXE": 55,
                "AC_SEATER": 60, "AC_SLEEPER": 55, "VOLVO": 65
            }
            avg_speed = avg_speeds.get(bt["type"], 50)
            duration_hours = distance / avg_speed
            
            # Calculate arrival
            dep_hour, dep_min = map(int, dep_time.split(':'))
            total_minutes = dep_hour * 60 + dep_min + int(duration_hours * 60)
            arr_hour = (total_minutes // 60) % 24
            arr_min = total_minutes % 60
            arrival_time = f"{arr_hour:02d}:{arr_min:02d}"
            
            # Next day arrival?
            next_day = total_minutes >= 24 * 60
            
            # Calculate fare
            fare = int(distance * base_fare_per_km * bt["multiplier"])
            
            buses.append({
                "bus_id": f"BUS{random.randint(1000, 9999)}",
                "operator": operator["name"],
                "operator_code": operator["id"],
                "bus_type": bt["name"],
                "bus_type_code": bt["type"],
                "departure_time": dep_time,
                "arrival_time": arrival_time + (" (+1 day)" if next_day else ""),
                "duration": f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m",
                "fare": fare,
                "seats_available": random.randint(5, 40),
                "amenities": self._get_amenities(bt["type"]),
                "boarding_point": f"{self.CITIES[origin]['name']} Bus Station",
                "dropping_point": f"{self.CITIES[destination]['name']} Bus Station"
            })
        
        # Sort by departure time
        buses.sort(key=lambda x: x["departure_time"])
        
        return buses
    
    def _get_amenities(self, bus_type: str) -> List[str]:
        """Get amenities based on bus type"""
        base_amenities = ["Seat Belt"]
        
        if bus_type in ["DELUXE", "AC_SEATER", "AC_SLEEPER", "VOLVO"]:
            base_amenities.extend(["Air Conditioning", "Charging Point"])
        
        if bus_type in ["AC_SLEEPER", "VOLVO"]:
            base_amenities.extend(["Blanket", "Water Bottle"])
        
        if bus_type == "VOLVO":
            base_amenities.extend(["WiFi", "Entertainment Screen", "Reading Light"])
        
        return base_amenities
    
    def get_route_details(self, origin: str, destination: str) -> Dict[str, any]:
        """
        Get detailed route information.
        
        Args:
            origin: Origin city code
            destination: Destination city code
            
        Returns:
            Route details including intermediate stops
        """
        origin = origin.upper()
        destination = destination.upper()
        
        if origin not in self.CITIES or destination not in self.CITIES:
            return {"success": False, "error": "Invalid city codes"}
        
        distance = self._get_distance(origin, destination)
        
        # Generate intermediate stops
        all_cities = list(self.CITIES.keys())
        all_cities.remove(origin)
        all_cities.remove(destination)
        
        num_stops = min(random.randint(1, 3), len(all_cities))
        intermediate_stops = random.sample(all_cities, num_stops)
        
        return {
            "success": True,
            "route": {
                "origin": {
                    "code": origin,
                    **self.CITIES[origin]
                },
                "destination": {
                    "code": destination,
                    **self.CITIES[destination]
                },
                "distance_km": distance,
                "intermediate_stops": [
                    {"code": stop, **self.CITIES[stop]}
                    for stop in intermediate_stops
                ],
                "estimated_duration": f"{distance // 50}h {(distance % 50) * 60 // 50}m",
                "highway": random.choice(["NH-8", "NH-44", "NH-48", "NH-66"])
            }
        }
    
    def get_schedule(self, operator: str, route: str = None) -> Dict[str, any]:
        """
        Get bus schedule for an operator.
        
        Args:
            operator: Operator code
            route: Optional route specification
            
        Returns:
            Schedule information
        """
        operator_info = next(
            (op for op in self.BUS_OPERATORS if op["id"] == operator.upper()),
            None
        )
        
        if not operator_info:
            return {
                "success": False,
                "error": f"Unknown operator: {operator}",
                "available_operators": [op["id"] for op in self.BUS_OPERATORS]
            }
        
        # Generate schedule
        schedule = []
        cities = list(self.CITIES.keys())
        
        for i in range(5):
            origin = random.choice(cities)
            destination = random.choice([c for c in cities if c != origin])
            
            schedule.append({
                "route": f"{origin} - {destination}",
                "departures": ["06:00", "10:00", "14:00", "18:00", "22:00"][:random.randint(2, 5)],
                "bus_types": random.sample(
                    [bt["name"] for bt in self.BUS_TYPES],
                    random.randint(2, 4)
                )
            })
        
        return {
            "success": True,
            "operator": operator_info,
            "schedule": schedule
        }
    
    def get_cities(self) -> Dict[str, any]:
        """Get list of available cities"""
        return {
            "success": True,
            "cities": [
                {"code": code, **details}
                for code, details in self.CITIES.items()
            ]
        }
    
    def get_bus_types(self) -> Dict[str, any]:
        """Get available bus types"""
        return {
            "success": True,
            "bus_types": [
                {"code": bt["type"], "name": bt["name"]}
                for bt in self.BUS_TYPES
            ]
        }
    
    def format_route_text(self, search_result: Dict) -> str:
        """
        Format search results as readable text.
        
        Args:
            search_result: Search result dictionary
            
        Returns:
            Formatted text
        """
        if not search_result.get("success"):
            return f"Error: {search_result.get('error', 'Unknown error')}"
        
        lines = [
            "=" * 60,
            "BUS ROUTE SEARCH RESULTS",
            "=" * 60,
            f"Route: {search_result['origin']['name']} → {search_result['destination']['name']}",
            f"Date: {search_result.get('date', 'N/A')}",
            f"Distance: {search_result.get('distance_km', 'N/A')} km",
            f"Buses Found: {search_result.get('buses_found', 0)}",
            "-" * 60,
            ""
        ]
        
        for bus in search_result.get("buses", []):
            lines.extend([
                f"🚌 {bus['operator']} ({bus['bus_type']})",
                f"   Departure: {bus['departure_time']} | Arrival: {bus['arrival_time']}",
                f"   Duration: {bus['duration']}",
                f"   Fare: ₹{bus['fare']}",
                f"   Seats Available: {bus['seats_available']}",
                f"   Amenities: {', '.join(bus['amenities'])}",
                ""
            ])
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
