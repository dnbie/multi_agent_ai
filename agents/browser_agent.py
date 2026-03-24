"""
Browser Agent - Web automation and browser control
Opens URLs, searches YouTube, plays videos, and navigates websites
Uses Python's built-in webbrowser module (no extra install required)
"""

import re
import json
import os
import shutil
import webbrowser
import requests
from urllib.parse import quote_plus
from typing import Dict, List, Optional
from .base_agent import BaseAgent, AgentResult


class BrowserAgent(BaseAgent):
    """
    Browser automation agent that opens URLs, plays YouTube videos,
    searches the web, and performs simple browser tasks.
    """

    def __init__(self):
        super().__init__(
            name="Browser Agent",
            description="Open websites, play YouTube videos, search the web"
        )
        self.browser = self._get_chrome_browser()

    def _get_chrome_browser(self):
        """Return a Chrome browser controller when available, else None."""
        # Common Windows install paths
        chrome_candidates = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
        ]

        for path in chrome_candidates:
            if path and os.path.exists(path):
                try:
                    return webbrowser.get(f'"{path}" %s')
                except webbrowser.Error:
                    pass

        # Fallback to command lookup if PATH is configured
        chrome_cmd = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chrome.exe")
        if chrome_cmd:
            try:
                return webbrowser.get(f'"{chrome_cmd}" %s')
            except webbrowser.Error:
                pass

        return None

    def _open(self, url: str) -> None:
        """Open URL in Chrome when available, otherwise use default browser."""
        if self.browser:
            self.browser.open(url)
        else:
            webbrowser.open(url)

    def get_capabilities(self) -> List[str]:
        return [
            "Open any website by URL or name",
            "Search and play YouTube videos / songs",
            "Search Gmail inbox from command",
            "Open Google Maps directions to destination",
            "Search Google for any query",
            "Open common sites (Gmail, Maps, Wikipedia, etc.)",
            "Open local files in browser",
        ]

    # ── site shortcuts ────────────────────────────────────────────────────────
    SITE_SHORTCUTS = {
        "youtube":    "https://www.youtube.com",
        "google":     "https://www.google.com",
        "gmail":      "https://mail.google.com",
        "mail":       "https://mail.google.com",
        "maps":       "https://maps.google.com",
        "google maps": "https://maps.google.com",
        "wikipedia":  "https://www.wikipedia.org",
        "github":     "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "reddit":     "https://www.reddit.com",
        "twitter":    "https://twitter.com",
        "x":          "https://twitter.com",
        "facebook":   "https://www.facebook.com",
        "instagram":  "https://www.instagram.com",
        "linkedin":   "https://www.linkedin.com",
        "amazon":     "https://www.amazon.in",
        "flipkart":   "https://www.flipkart.com",
        "netflix":    "https://www.netflix.com",
        "spotify":    "https://open.spotify.com",
        "whatsapp":   "https://web.whatsapp.com",
        "chatgpt":    "https://chat.openai.com",
        "openai":     "https://www.openai.com",
    }

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)

        try:
            parsed   = self._parse_task(task)
            action   = parsed["action"]
            query    = parsed["query"]
            url      = parsed["url"]

            if action == "youtube_play":
                result = self._youtube_play(query)
            elif action == "youtube_search":
                result = self._youtube_search(query)
            elif action == "gmail_search":
                result = self._gmail_search(query)
            elif action == "maps_route":
                result = self._maps_route(query)
            elif action == "google_search":
                result = self._google_search(query)
            elif action == "open_site":
                result = self._open_site(url or query)
            elif action == "open_url":
                result = self._open_url(url)
            else:
                # Fallback: ask LLM to build the right URL
                result = self._smart_open(task)

        except Exception as e:
            result = self._create_result(False, f"Browser error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── action handlers ───────────────────────────────────────────────────────

    def _youtube_play(self, query: str) -> AgentResult:
        """Try to open the top matching video directly via Google I-am-feeling-lucky."""
        lucky_url = f"https://www.google.com/search?btnI=1&q={quote_plus('site:youtube.com ' + query)}"
        self._open(lucky_url)
        return self._create_result(
            True,
            f"Opened top YouTube result for: {query}",
            data={"action": "youtube_play", "query": query, "url": lucky_url}
        )

    def _youtube_search(self, query: str) -> AgentResult:
        """Open YouTube search results."""
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        self._open(search_url)
        return self._create_result(
            True,
            f"Opened YouTube search: {query}",
            data={"action": "youtube_search", "query": query, "url": search_url}
        )

    def _google_search(self, query: str) -> AgentResult:
        """Open Google search."""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        self._open(search_url)
        return self._create_result(
            True,
            f"Opened Google search: {query}",
            data={"action": "google_search", "query": query, "url": search_url}
        )

    def _gmail_search(self, query: str) -> AgentResult:
        """Open Gmail inbox and apply the requested search query."""
        search_url = f"https://mail.google.com/mail/u/0/#search/{quote_plus(query)}"
        self._open(search_url)
        return self._create_result(
            True,
            f"Opened Gmail search for: {query}",
            data={"action": "gmail_search", "query": query, "url": search_url}
        )

    def _maps_route(self, destination: str) -> AgentResult:
        """Open Google Maps directions to destination (auto-detects current location when origin is missing)."""
        origin = None
        origin_is_current = False

        route_match = re.search(r'^\s*from\s+(.+?)\s+to\s+(.+?)\s*$', destination, re.IGNORECASE)
        if route_match:
            origin = route_match.group(1).strip()
            destination = route_match.group(2).strip()

        # If no origin given, try to fetch current location from IP
        if not origin:
            loc = self._get_current_location()
            if loc:
                origin = loc["city"]
                origin_is_current = True

        route_url = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(destination)}"
        if origin:
            route_url += f"&origin={quote_plus(origin)}"

        route_info = self._estimate_route(origin, destination) if origin else None

        self._open(route_url)

        origin_label = f"your location ({origin})" if origin_is_current else origin
        message = f"Opened Maps directions to: {destination}" + (f" from {origin_label}" if origin_label else "")
        if route_info:
            message += f" | Distance: {route_info['distance_km']} km | ETA: {route_info['duration_text']}"

        return self._create_result(
            True,
            message,
            data={
                "action": "maps_route",
                "origin": origin,
                "origin_is_current_location": origin_is_current,
                "destination": destination,
                "url": route_url,
                "distance_km": route_info.get("distance_km") if route_info else None,
                "duration_seconds": route_info.get("duration_seconds") if route_info else None,
                "duration_text": route_info.get("duration_text") if route_info else None,
                "route_source": route_info.get("source") if route_info else None,
            }
        )

    def _get_current_location(self) -> Optional[Dict]:
        """Detect approximate current location via IP geolocation (ip-api.com, no key needed)."""
        try:
            resp = requests.get("http://ip-api.com/json/?fields=status,city,regionName,country,lat,lon",
                                timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "success":
                return None
            return {
                "city":    data.get("city", ""),
                "region":  data.get("regionName", ""),
                "country": data.get("country", ""),
                "lat":     data.get("lat"),
                "lon":     data.get("lon"),
            }
        except Exception:
            return None

    def _estimate_route(self, origin: str, destination: str) -> Optional[Dict]:
        """Estimate route distance and travel time using free OSM services."""
        try:
            o_lat, o_lon = self._geocode_place(origin)
            d_lat, d_lon = self._geocode_place(destination)
            if o_lat is None or d_lat is None:
                return None

            osrm_url = (
                f"https://router.project-osrm.org/route/v1/driving/"
                f"{o_lon},{o_lat};{d_lon},{d_lat}?overview=false"
            )
            resp = requests.get(osrm_url, timeout=8)
            resp.raise_for_status()
            data = resp.json()

            routes = data.get("routes") or []
            if not routes:
                return None

            first = routes[0]
            distance_m = float(first.get("distance", 0))
            duration_s = int(first.get("duration", 0))
            if distance_m <= 0 or duration_s <= 0:
                return None

            return {
                "distance_km": round(distance_m / 1000, 1),
                "duration_seconds": duration_s,
                "duration_text": self._format_duration(duration_s),
                "source": "OSRM",
            }
        except Exception:
            return None

    def _geocode_place(self, place: str):
        """Geocode a place name to latitude/longitude using Nominatim."""
        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": place, "format": "json", "limit": 1},
                headers={"User-Agent": "agentic-ai-browser-agent/1.0"},
                timeout=8,
            )
            resp.raise_for_status()
            items = resp.json() or []
            if not items:
                return None, None
            return float(items[0]["lat"]), float(items[0]["lon"])
        except Exception:
            return None, None

    def _format_duration(self, seconds: int) -> str:
        """Format duration seconds into a compact human-readable string."""
        mins = max(1, round(seconds / 60))
        hrs, rem = divmod(mins, 60)
        if hrs:
            return f"{hrs}h {rem}m"
        return f"{rem}m"

    def _open_site(self, site: str) -> AgentResult:
        """Open a known site by shortcut name or construct URL."""
        site_lower = site.strip().lower()
        url = self.SITE_SHORTCUTS.get(site_lower)
        if not url:
            # Try adding https:// if looks like a domain
            if re.match(r'^[\w.-]+\.[a-z]{2,}', site_lower):
                url = f"https://{site_lower}"
            else:
                # Fallback to Google search
                return self._google_search(site)
            self._open(url)
        return self._create_result(
            True,
            f"Opened {site}",
            data={"action": "open_site", "site": site, "url": url}
        )

    def _open_url(self, url: str) -> AgentResult:
        """Open a raw URL directly."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self._open(url)
        return self._create_result(
            True,
            f"Opened URL: {url}",
            data={"action": "open_url", "url": url}
        )

    def _smart_open(self, task: str) -> AgentResult:
        """Use LLM to figure out the best URL for the task, then open it."""
        try:
            llm = self.get_llm()
            prompt = f"""You are a browser assistant. Given the user task below, reply with ONLY a single URL
that best fulfills the request. If the user wants to play a song/video, use a YouTube search URL.
Do NOT include explanation — just the URL.

User task: {task}

URL:"""
            url = llm.generate_text(prompt, temperature=0).strip().split()[0]
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            self._open(url)
            return self._create_result(
                True,
                f"Opened: {url}",
                data={"action": "smart_open", "url": url, "task": task}
            )
        except Exception as e:
            return self._create_result(False, f"Could not determine URL: {str(e)}", error=str(e))

    def _ai_parse_task(self, task: str) -> Optional[Dict]:
        """Use LLM to parse complex browser commands into structured actions."""
        try:
            llm = self.get_llm()
            prompt = f"""You are a browser command parser.
Return ONLY valid JSON with keys: action, query, url.

Allowed action values:
- youtube_play
- youtube_search
- gmail_search
- maps_route
- google_search
- open_site
- open_url
- smart

Examples:
Input: open mail and search for vit
Output: {{"action":"gmail_search","query":"vit","url":""}}

Input: open maps and enroute me to coimbatore
Output: {{"action":"maps_route","query":"coimbatore","url":""}}

Input: open youtube and play python tutorial
Output: {{"action":"youtube_play","query":"python tutorial","url":""}}

User input: {task}
JSON:"""
            raw = llm.generate_text(prompt, temperature=0)
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start < 0 or end <= start:
                return None
            parsed = json.loads(raw[start:end])
            action = (parsed.get("action") or "").strip().lower()
            if action not in {
                "youtube_play", "youtube_search", "gmail_search", "maps_route",
                "google_search", "open_site", "open_url", "smart"
            }:
                return None
            return {
                "action": action,
                "query": (parsed.get("query") or "").strip(),
                "url": (parsed.get("url") or "").strip(),
            }
        except Exception:
            return None

    # ── task parser ───────────────────────────────────────────────────────────

    def _parse_task(self, task: str) -> Dict:
        lower = task.lower()
        result = {"action": None, "query": "", "url": ""}

        # ── explicit URL ──────────────────────────────────────────────────────
        url_match = re.search(r'https?://\S+', task)
        if url_match:
            result["action"] = "open_url"
            result["url"] = url_match.group(0)
            return result

        # ── YouTube play/song ─────────────────────────────────────────────────
        yt_play = re.search(
            r'(?:open\s+youtube\s+(?:and\s+)?(?:play|search)|play(?:\s+on\s+youtube)?|youtube\s+play)\s+(.+)',
            lower
        )
        if yt_play:
            result["action"] = "youtube_play"
            result["query"]  = yt_play.group(1).strip()
            return result

        # ── Gmail search command ────────────────────────────────────────────
        gmail_search = re.search(
            r'(?:open\s+(?:gmail|mail).*(?:search\s+for|search)\s+|search\s+(?:gmail|mail)\s+for\s+)(.+)',
            lower
        )
        if gmail_search:
            result["action"] = "gmail_search"
            result["query"] = gmail_search.group(1).strip()
            return result

        # ── Maps route / directions command ────────────────────────────────
        # Pattern: "directions from X to Y on maps" / "get directions from X to Y"
        route_from_to = re.search(
            r'(?:directions?|route|navigate)\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+on\s+maps?)?\s*$',
            lower
        )
        if route_from_to:
            origin = route_from_to.group(1).strip().rstrip("?.!,")
            destination = route_from_to.group(2).strip().rstrip("?.!,")
            if origin and destination:
                result["action"] = "maps_route"
                result["query"] = f"from {origin} to {destination}"
                return result

        # Pattern: "from X to Y on maps" / "from X to Y"
        simple_from_to = re.search(
            r'from\s+(.+?)\s+to\s+(.+?)(?:\s+on\s+maps?)?\s*$',
            lower
        )
        if simple_from_to and ("map" in lower or "direction" in lower or "route" in lower):
            origin = simple_from_to.group(1).strip().rstrip("?.!,")
            destination = simple_from_to.group(2).strip().rstrip("?.!,")
            if origin and destination:
                result["action"] = "maps_route"
                result["query"] = f"from {origin} to {destination}"
                return result

        maps_route = re.search(
            r'(?:maps?.*(?:route|directions?|navigate|enroute|way\s+to)\s+(?:to\s+)?)\s*(.+)',
            lower
        )
        if maps_route and maps_route.group(1).strip():
            destination = maps_route.group(1).strip()
            destination = re.sub(r'^(?:me\s+to\s+|to\s+)', '', destination).strip()
            result["action"] = "maps_route"
            result["query"] = destination
            return result

        # Pattern: "directions to X [on maps]" / "navigate to X on maps"
        # (destination-only — origin will be auto-detected from current location)
        _NON_PLACES = {"maps", "google maps", "map", "google map"}
        dest_only = re.search(
            r'(?:get\s+)?(?:directions?|navigate(?:\s+to)?)\s+(?:to\s+)?(.+?)(?:\s+on\s+(?:google\s+)?maps?)?\s*$',
            lower
        )
        if dest_only:
            raw_dest = dest_only.group(1).strip().rstrip("?.!,")
            if raw_dest and raw_dest not in _NON_PLACES:
                result["action"] = "maps_route"
                result["query"] = raw_dest
                return result

        # Also handle bare "X on maps" / "X on google maps" without direction keyword
        bare_on_maps = re.search(
            r'^(.+?)\s+on\s+(?:google\s+)?maps?\s*$',
            lower
        )
        if bare_on_maps:
            raw_dest = bare_on_maps.group(1).strip().rstrip("?.!,")
            if raw_dest and raw_dest not in _NON_PLACES:
                result["action"] = "maps_route"
                result["query"] = raw_dest
                return result

        # ── YouTube open (without specific play keyword) ──────────────────────
        if "youtube" in lower:
            query_match = re.search(r'youtube[^\w]*(?:for|search|about)?\s+(.+)', lower)
            if query_match:
                result["action"] = "youtube_search"
                result["query"]  = query_match.group(1).strip()
            else:
                result["action"] = "open_site"
                result["url"]    = self.SITE_SHORTCUTS["youtube"]
            return result

        # ── Google search ─────────────────────────────────────────────────────
        google_match = re.search(r'(?:google|search(?:\s+for)?)\s+(.+)', lower)
        if google_match:
            result["action"] = "google_search"
            result["query"]  = google_match.group(1).strip()
            return result

        # ── open <site> ───────────────────────────────────────────────────────
        open_match = re.search(r'(?:open|go\s+to|visit|launch|start)\s+([\w.\-]+(?:\s+[\w.\-]+)?)', lower)
        if open_match:
            site = open_match.group(1).strip()
            result["action"] = "open_site"
            result["query"]  = site
            return result

        # ── app-specific quick commands ─────────────────────────────────────
        if re.search(r'\b(check|open|go\s+to)\s+(gmail|mail)\b', lower):
            result["action"] = "open_site"
            result["query"] = "gmail"
            return result

        if re.search(r'\b(open|go\s+to|navigate\s+to)\s+(google\s+maps|maps?)\b', lower):
            result["action"] = "open_site"
            result["query"] = "maps"
            return result

        if re.search(r'\b(open|launch|watch)\s+netflix\b', lower):
            result["action"] = "open_site"
            result["query"] = "netflix"
            return result

        # ── known site name anywhere in task ─────────────────────────────────
        for site_name in self.SITE_SHORTCUTS:
            if site_name in lower:
                result["action"] = "open_site"
                result["query"]  = site_name
                return result

        # ── domain-like string ────────────────────────────────────────────────
        domain_match = re.search(r'\b([\w-]+\.(com|in|org|net|io|co|edu))\b', lower)
        if domain_match:
            result["action"] = "open_url"
            result["url"]    = domain_match.group(1)
            return result

        # ── AI parser for complex phrasing ─────────────────────────────────
        ai_result = self._ai_parse_task(task)
        if ai_result:
            return ai_result

        # ── fall through to smart LLM ─────────────────────────────────────────
        result["action"] = "smart"
        return result
