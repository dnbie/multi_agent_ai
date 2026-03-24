"""
Flight API - Flight Search with Aviation Stack API
Supports both real Aviation Stack API and mock data for demonstration
"""

import random
import os
import re
import difflib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class FlightAPI:
    """
    Flight API supporting Aviation Stack API and mock data fallback.
    Uses real Aviation Stack API when credentials are available, otherwise mock data.
    """
    
    # Aviation Stack API base URL
    AVIATIONSTACK_BASE_URL = "http://api.aviationstack.com/v1"
    
    # Mock airline data
    AIRLINES = [
        {"code": "AI", "name": "Air India"},
        {"code": "6E", "name": "IndiGo"},
        {"code": "SG", "name": "SpiceJet"},
        {"code": "UK", "name": "Vistara"},
        {"code": "G8", "name": "Go First"},
        {"code": "AA", "name": "American Airlines"},
        {"code": "BA", "name": "British Airways"},
        {"code": "EK", "name": "Emirates"},
        {"code": "SQ", "name": "Singapore Airlines"},
        {"code": "LH", "name": "Lufthansa"}
    ]
    
    # Airline code to name mapping for real API
    AIRLINE_NAMES = {
        "AI": "Air India", "6E": "IndiGo", "SG": "SpiceJet", "UK": "Vistara",
        "G8": "Go First", "AA": "American Airlines", "BA": "British Airways",
        "EK": "Emirates", "SQ": "Singapore Airlines", "LH": "Lufthansa",
        "QF": "Qantas", "AF": "Air France", "KL": "KLM", "TK": "Turkish Airlines",
        "QR": "Qatar Airways", "EY": "Etihad", "NH": "ANA", "JL": "Japan Airlines"
    }
    
    # Mock airports
    AIRPORTS = {
        "DEL": {"city": "New Delhi", "country": "India", "name": "Indira Gandhi International"},
        "BOM": {"city": "Mumbai", "country": "India", "name": "Chhatrapati Shivaji International"},
        "BLR": {"city": "Bangalore", "country": "India", "name": "Kempegowda International"},
        "MAA": {"city": "Chennai", "country": "India", "name": "Chennai International"},
        "CCU": {"city": "Kolkata", "country": "India", "name": "Netaji Subhas Chandra Bose"},
        "HYD": {"city": "Hyderabad", "country": "India", "name": "Rajiv Gandhi International"},
        "LHR": {"city": "London", "country": "UK", "name": "Heathrow"},
        "JFK": {"city": "New York", "country": "USA", "name": "John F. Kennedy"},
        "DXB": {"city": "Dubai", "country": "UAE", "name": "Dubai International"},
        "SIN": {"city": "Singapore", "country": "Singapore", "name": "Changi Airport"}
    }

    # City aliases and major Indian cities mapped to nearest supported airport code.
    CITY_TO_AIRPORT = {
        "delhi": "DEL", "new delhi": "DEL", "ncr": "DEL", "gurgaon": "DEL", "gurugram": "DEL", "noida": "DEL",
        "mumbai": "BOM", "bombay": "BOM", "navi mumbai": "BOM", "thane": "BOM",
        "bangalore": "BLR", "bengaluru": "BLR", "mysuru": "BLR", "mysore": "BLR", "mangalore": "BLR", "mangaluru": "BLR",
        "chennai": "MAA", "madras": "MAA", "vellore": "MAA", "pondicherry": "MAA", "puducherry": "MAA",
        "kolkata": "CCU", "calcutta": "CCU", "howrah": "CCU", "durgapur": "CCU", "asansol": "CCU",
        "hyderabad": "HYD", "secunderabad": "HYD", "warangal": "HYD", "nizamabad": "HYD",

        "ahmedabad": "BOM", "surat": "BOM", "vadodara": "BOM", "rajkot": "BOM", "bhavnagar": "BOM",
        "pune": "BOM", "nagpur": "BOM", "nashik": "BOM", "aurangabad": "BOM", "kolhapur": "BOM",
        "jaipur": "DEL", "jodhpur": "DEL", "udaipur": "DEL", "kota": "DEL", "ajmer": "DEL", "bikaner": "DEL",
        "lucknow": "DEL", "kanpur": "DEL", "agra": "DEL", "varanasi": "DEL", "prayagraj": "DEL", "allahabad": "DEL", "meerut": "DEL", "ghaziabad": "DEL",
        "patna": "CCU", "gaya": "CCU", "muzaffarpur": "CCU", "bhagalpur": "CCU",
        "ranchi": "CCU", "jamshedpur": "CCU", "dhanbad": "CCU", "bokaro": "CCU",
        "bhubaneswar": "CCU", "cuttack": "CCU", "rourkela": "CCU", "puri": "CCU",
        "guwahati": "CCU", "silchar": "CCU", "dibrugarh": "CCU", "tezpur": "CCU", "jorhat": "CCU",
        "imphal": "CCU", "agartala": "CCU", "aizawl": "CCU", "kohima": "CCU", "itanagar": "CCU", "shillong": "CCU",

        "coimbatore": "MAA", "madurai": "MAA", "trichy": "MAA", "tiruchirappalli": "MAA", "salem": "MAA", "erode": "MAA",
        "kochi": "MAA", "cochin": "MAA", "kozhikode": "MAA", "calicut": "MAA", "trivandrum": "MAA", "thiruvananthapuram": "MAA", "thrissur": "MAA",
        "visakhapatnam": "HYD", "vizag": "HYD", "vijayawada": "HYD", "guntur": "HYD", "tirupati": "HYD", "kurnool": "HYD",
        "bhopal": "DEL", "indore": "DEL", "jabalpur": "DEL", "gwalior": "DEL", "ujjain": "DEL",
        "chandigarh": "DEL", "ludhiana": "DEL", "amritsar": "DEL", "jalandhar": "DEL", "patiala": "DEL",
        "dehradun": "DEL", "haridwar": "DEL", "roorkee": "DEL", "haldwani": "DEL", "nainital": "DEL",
        "shimla": "DEL", "dharamshala": "DEL", "manali": "DEL", "solan": "DEL",
        "srinagar": "DEL", "jammu": "DEL", "leh": "DEL",
        "raipur": "DEL", "bilaspur": "DEL", "durg": "DEL", "korba": "DEL",

        "goa": "BOM", "panaji": "BOM", "margao": "BOM", "vasco da gama": "BOM",
        "port blair": "CCU", "silvassa": "BOM", "daman": "BOM", "diu": "BOM"
    }
    
    def __init__(self, use_real_api: bool = True):
        """
        Initialize Flight API.
        
        Args:
            use_real_api: Whether to use real Aviation Stack API (if credentials available)
        """
        self.search_count = 0
        self.use_real_api = use_real_api
        self.aviationstack_key = None
        
        # Try to initialize Aviation Stack API
        if use_real_api:
            self._init_aviationstack()
    
    def _init_aviationstack(self):
        """Initialize Aviation Stack API"""
        try:
            api_key = os.getenv("AVIATIONSTACK_API_KEY")
            
            if api_key:
                self.aviationstack_key = api_key
                print("[OK] Aviation Stack API initialized successfully")
            else:
                print("[INFO] Aviation Stack API key not found, using mock data")
        except Exception as e:
            print(f"[WARN] Aviation Stack initialization failed: {e}, using mock data")
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        passengers: int = 1,
        travel_class: str = "economy"
    ) -> Dict[str, any]:
        """
        Search for available flights using Amadeus API or mock data.
        
        
        Args:
            origin: Origin airport code (e.g., 'DEL')
            destination: Destination airport code (e.g., 'BOM')
            date: Travel date (YYYY-MM-DD)
            passengers: Number of passengers
            travel_class: Travel class (economy, business, first)
            
        Returns:
            Search results with flight options
        """
        self.search_count += 1

        origin_resolution = self.resolve_location(origin)
        destination_resolution = self.resolve_location(destination)

        if not origin_resolution["success"]:
            return {
                "success": False,
                "error": f"Unknown origin: {origin}",
                "did_you_mean": origin_resolution.get("suggestions", []),
                "available_airports": list(self.AIRPORTS.keys())
            }

        if not destination_resolution["success"]:
            return {
                "success": False,
                "error": f"Unknown destination: {destination}",
                "did_you_mean": destination_resolution.get("suggestions", []),
                "available_airports": list(self.AIRPORTS.keys())
            }

        origin = origin_resolution["code"]
        destination = destination_resolution["code"]
        
        if origin == destination:
            return {
                "success": False,
                "error": "Origin and destination cannot be the same"
            }
        
        # Parse date
        try:
            travel_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }

        # Prevent searching/bookings for past travel dates
        if travel_date.date() < datetime.now().date():
            return {
                "success": False,
                "error": "Travel date cannot be in the past. Please select today or a future date."
            }
        
        # Try real API first, fallback to mock
        if self.aviationstack_key:
            try:
                return self._search_aviationstack(origin, destination, date, passengers, travel_class)
            except Exception as e:
                print(f"Aviation Stack API error: {e}, falling back to mock data")
        
        # Generate mock flights
        flights = self._generate_flights(
            origin, destination, travel_date, travel_class
        )
        
        # Calculate prices based on class
        class_multiplier = {"economy": 1, "business": 2.5, "first": 4}
        multiplier = class_multiplier.get(travel_class.lower(), 1)
        
        for flight in flights:
            flight["price"] = int(flight["base_price"] * multiplier * passengers)
            flight["passengers"] = passengers
            flight["travel_class"] = travel_class
        
        return {
            "success": True,
            "search_id": f"SEARCH{self.search_count:04d}",
            "origin": {
                "code": origin,
                **self.AIRPORTS[origin]
            },
            "destination": {
                "code": destination,
                **self.AIRPORTS[destination]
            },
            "date": date,
            "passengers": passengers,
            "travel_class": travel_class,
            "flights_found": len(flights),
            "flights": flights,
            "data_source": "mock",
            "normalized_input": {
                "origin": origin_resolution,
                "destination": destination_resolution
            }
        }

    def resolve_location(self, user_input: str) -> Dict[str, any]:
        """Resolve airport code/city input to a supported airport code with typo correction."""
        if not user_input:
            return {"success": False, "error": "Empty location", "suggestions": []}

        raw = str(user_input).strip()
        cleaned = re.sub(r"\s+", " ", raw.lower()).strip()
        cleaned = re.sub(r"[^a-z\s]", "", cleaned)

        # Direct 3-letter airport code
        code_candidate = raw.strip().upper()
        if len(code_candidate) == 3 and code_candidate in self.AIRPORTS:
            return {
                "success": True,
                "code": code_candidate,
                "input": raw,
                "matched": code_candidate,
                "corrected": False,
                "match_type": "airport_code"
            }

        # Direct city alias map
        if cleaned in self.CITY_TO_AIRPORT:
            code = self.CITY_TO_AIRPORT[cleaned]
            return {
                "success": True,
                "code": code,
                "input": raw,
                "matched": cleaned,
                "corrected": cleaned != raw.lower(),
                "match_type": "city"
            }

        # Exact airport city in AIRPORTS dict
        for code, details in self.AIRPORTS.items():
            city = details.get("city", "").lower()
            if cleaned == city:
                return {
                    "success": True,
                    "code": code,
                    "input": raw,
                    "matched": details.get("city"),
                    "corrected": cleaned != raw.lower(),
                    "match_type": "airport_city"
                }

        # Fuzzy matching for typo correction
        candidates = list(self.CITY_TO_AIRPORT.keys()) + [
            details.get("city", "").lower() for details in self.AIRPORTS.values()
        ]
        close = difflib.get_close_matches(cleaned, candidates, n=3, cutoff=0.72)

        if close:
            best = close[0]
            mapped_code = self.CITY_TO_AIRPORT.get(best)
            if not mapped_code:
                for code, details in self.AIRPORTS.items():
                    if details.get("city", "").lower() == best:
                        mapped_code = code
                        break

            if mapped_code:
                return {
                    "success": True,
                    "code": mapped_code,
                    "input": raw,
                    "matched": best,
                    "corrected": True,
                    "match_type": "fuzzy_city",
                    "suggestions": close
                }

        return {
            "success": False,
            "error": f"Could not resolve location: {raw}",
            "suggestions": close if 'close' in locals() else []
        }
    
    def _search_aviationstack(
        self,
        origin: str,
        destination: str,
        date: str,
        passengers: int,
        travel_class: str
    ) -> Dict[str, any]:
        """
        Search flights using Aviation Stack API.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            date: Travel date (YYYY-MM-DD)
            passengers: Number of passengers
            travel_class: Travel class
            
        Returns:
            Flight search results from Aviation Stack
        """
        try:
            # Call Aviation Stack Flights API
            params = {
                "access_key": self.aviationstack_key,
                "dep_iata": origin,
                "arr_iata": destination,
                "limit": 10
            }
            
            response = requests.get(
                f"{self.AVIATIONSTACK_BASE_URL}/flights",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                raise Exception(f"API Error: {data['error'].get('message', 'Unknown error')}")
            
            # Parse response
            flights = []
            for flight_data in data.get("data", []):
                airline_info = flight_data.get("airline", {})
                flight_info = flight_data.get("flight", {})
                departure = flight_data.get("departure", {})
                arrival = flight_data.get("arrival", {})
                
                airline_code = airline_info.get("iata", "XX")
                airline_name = self.AIRLINE_NAMES.get(airline_code, airline_info.get("name", airline_code))
                
                # Calculate duration if times are available
                dep_time = departure.get("scheduled", "")
                arr_time = arrival.get("scheduled", "")
                duration_str, duration_mins = self._calculate_duration(dep_time, arr_time)
                
                # Estimate price based on route and class
                base_price = self._estimate_price(origin, destination, travel_class)
                
                flight = {
                    "flight_number": flight_info.get("iata", f"{airline_code}000"),
                    "airline": airline_name,
                    "airline_code": airline_code,
                    "departure_time": dep_time[11:16] if len(dep_time) > 16 else "N/A",
                    "arrival_time": arr_time[11:16] if len(arr_time) > 16 else "N/A",
                    "duration": duration_str,
                    "duration_minutes": duration_mins,
                    "stops": 0,  # Aviation Stack returns direct flights
                    "price": base_price * passengers,
                    "currency": "INR",
                    "seats_available": "Available",
                    "aircraft": flight_data.get("aircraft", {}).get("iata", "N/A"),
                    "flight_status": flight_data.get("flight_status", "scheduled"),
                    "departure_terminal": departure.get("terminal", "N/A"),
                    "arrival_terminal": arrival.get("terminal", "N/A")
                }
                flights.append(flight)
            
            return {
                "success": True,
                "search_id": f"AVSTACK{self.search_count:04d}",
                "origin": {
                    "code": origin,
                    **self.AIRPORTS.get(origin, {"city": origin, "country": "Unknown", "name": origin})
                },
                "destination": {
                    "code": destination,
                    **self.AIRPORTS.get(destination, {"city": destination, "country": "Unknown", "name": destination})
                },
                "date": date,
                "passengers": passengers,
                "travel_class": travel_class,
                "flights_found": len(flights),
                "flights": flights,
                "data_source": "aviationstack_api"
            }
            
        except requests.RequestException as e:
            raise Exception(f"Aviation Stack API request error: {str(e)}")
        except Exception as e:
            raise Exception(f"Aviation Stack API error: {str(e)}")
    
    def _calculate_duration(self, dep_time: str, arr_time: str) -> tuple:
        """Calculate flight duration from departure and arrival times"""
        try:
            if dep_time and arr_time:
                dep = datetime.fromisoformat(dep_time.replace("Z", "+00:00").replace("+00:00", ""))
                arr = datetime.fromisoformat(arr_time.replace("Z", "+00:00").replace("+00:00", ""))
                diff = arr - dep
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60
                return f"{hours}h {minutes}m", hours * 60 + minutes
        except:
            pass
        return "N/A", 0
    
    def _estimate_price(self, origin: str, destination: str, travel_class: str) -> int:
        """Estimate flight price based on route and class"""
        # Base prices for domestic vs international
        domestic_airports = {"DEL", "BOM", "BLR", "MAA", "CCU", "HYD"}
        is_domestic = origin in domestic_airports and destination in domestic_airports
        
        base_price = 5000 if is_domestic else 25000
        
        # Class multipliers
        multipliers = {"economy": 1, "business": 2.5, "first": 4}
        multiplier = multipliers.get(travel_class.lower(), 1)
        
        # Add some variation
        import random
        variation = random.uniform(0.8, 1.2)
        
        return int(base_price * multiplier * variation)
    
    def _generate_flights(
        self,
        origin: str,
        destination: str,
        date: datetime,
        travel_class: str
    ) -> List[Dict]:
        """Generate mock flight data"""
        flights = []
        
        # Generate 3-6 flights
        num_flights = random.randint(3, 6)
        
        # Base times
        base_times = ["06:00", "08:30", "11:00", "14:30", "17:00", "20:30"]
        
        # Estimate flight duration based on route
        domestic_routes = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
        is_domestic = origin in domestic_routes and destination in domestic_routes
        
        if is_domestic:
            duration_hours = random.uniform(1.5, 3)
            base_price = random.randint(3000, 8000)
        else:
            duration_hours = random.uniform(6, 14)
            base_price = random.randint(25000, 80000)
        
        for i in range(num_flights):
            airline = random.choice(self.AIRLINES)
            departure_time = base_times[i % len(base_times)]
            
            # Calculate arrival
            dep_hour, dep_min = map(int, departure_time.split(':'))
            total_minutes = dep_hour * 60 + dep_min + int(duration_hours * 60)
            arr_hour = (total_minutes // 60) % 24
            arr_min = total_minutes % 60
            arrival_time = f"{arr_hour:02d}:{arr_min:02d}"
            
            # Flight number
            flight_num = f"{airline['code']}{random.randint(100, 999)}"
            
            # Price variation
            price_variation = random.uniform(0.85, 1.15)
            
            flights.append({
                "flight_number": flight_num,
                "airline": airline["name"],
                "airline_code": airline["code"],
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": f"{int(duration_hours)}h {int((duration_hours % 1) * 60)}m",
                "duration_minutes": int(duration_hours * 60),
                "stops": 0 if random.random() > 0.3 else 1,
                "base_price": int(base_price * price_variation),
                "seats_available": random.randint(5, 50),
                "aircraft": random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380"])
            })
        
        # Sort by departure time
        flights.sort(key=lambda x: x["departure_time"])
        
        return flights
    
    def get_flight_details(self, flight_number: str, date: str) -> Dict[str, any]:
        """
        Get details for a specific flight.
        
        Args:
            flight_number: Flight number (e.g., 'AI302')
            date: Flight date
            
        Returns:
            Flight details
        """
        airline_code = flight_number[:2].upper()
        airline = next(
            (a for a in self.AIRLINES if a["code"] == airline_code),
            {"code": airline_code, "name": "Unknown Airline"}
        )
        
        return {
            "success": True,
            "flight_number": flight_number,
            "airline": airline["name"],
            "date": date,
            "status": random.choice(["On Time", "On Time", "Slight Delay"]),
            "departure_terminal": random.choice(["T1", "T2", "T3"]),
            "arrival_terminal": random.choice(["T1", "T2"]),
            "check_in_counter": f"{random.randint(1, 30)}-{random.randint(31, 50)}",
            "gate": f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 20)}",
            "amenities": ["Meal Included", "Entertainment System", "WiFi Available"]
        }
    
    def create_itinerary(
        self,
        trips: List[Dict],
        traveler_name: str = "Traveler"
    ) -> Dict[str, any]:
        """
        Create a travel itinerary.
        
        Args:
            trips: List of trip dictionaries with origin, destination, date
            traveler_name: Name of the traveler
            
        Returns:
            Complete itinerary
        """
        itinerary = {
            "success": True,
            "itinerary_id": f"ITIN{random.randint(10000, 99999)}",
            "created_at": datetime.now().isoformat(),
            "traveler": traveler_name,
            "trips": [],
            "total_cost": 0
        }
        
        for trip in trips:
            search_result = self.search_flights(
                origin=trip.get("origin", "DEL"),
                destination=trip.get("destination", "BOM"),
                date=trip.get("date", datetime.now().strftime("%Y-%m-%d")),
                passengers=trip.get("passengers", 1),
                travel_class=trip.get("travel_class", "economy")
            )
            
            if search_result["success"] and search_result["flights"]:
                # Select cheapest flight
                best_flight = min(search_result["flights"], key=lambda x: x["price"])
                
                itinerary["trips"].append({
                    "leg": len(itinerary["trips"]) + 1,
                    "route": f"{trip['origin']} → {trip['destination']}",
                    "date": trip.get("date"),
                    "flight": best_flight,
                    "origin_details": search_result["origin"],
                    "destination_details": search_result["destination"]
                })
                
                itinerary["total_cost"] += best_flight["price"]
        
        return itinerary
    
    def get_airports(self) -> Dict[str, any]:
        """Get list of available airports"""
        return {
            "success": True,
            "airports": [
                {"code": code, **details}
                for code, details in self.AIRPORTS.items()
            ],
            "supported_indian_cities": sorted(list(self.CITY_TO_AIRPORT.keys()))
        }
    
    def format_itinerary_text(self, itinerary: Dict) -> str:
        """
        Format itinerary as readable text.
        
        Args:
            itinerary: Itinerary dictionary
            
        Returns:
            Formatted text
        """
        lines = [
            "=" * 50,
            f"TRAVEL ITINERARY",
            f"Itinerary ID: {itinerary.get('itinerary_id', 'N/A')}",
            f"Traveler: {itinerary.get('traveler', 'N/A')}",
            "=" * 50,
            ""
        ]
        
        for trip in itinerary.get("trips", []):
            flight = trip.get("flight", {})
            lines.extend([
                f"LEG {trip.get('leg', '')}",
                f"Route: {trip.get('route', '')}",
                f"Date: {trip.get('date', '')}",
                f"Flight: {flight.get('flight_number', '')} - {flight.get('airline', '')}",
                f"Departure: {flight.get('departure_time', '')}",
                f"Arrival: {flight.get('arrival_time', '')}",
                f"Duration: {flight.get('duration', '')}",
                f"Class: {flight.get('travel_class', 'Economy').title()}",
                f"Price: ₹{flight.get('price', 0):,}",
                "-" * 40,
                ""
            ])
        
        lines.extend([
            f"TOTAL COST: ₹{itinerary.get('total_cost', 0):,}",
            "=" * 50
        ])
        
        return "\n".join(lines)
