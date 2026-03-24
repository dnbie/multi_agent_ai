"""
News API Tool - NewsAPI.org integration with mock fallback
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any, List


class NewsAPI:
    """Wraps NewsAPI.org. Falls back to curated mock headlines when key is unavailable."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "")
        self.use_real = bool(self.api_key and self.api_key != "your_newsapi_key_here")

    # ── public ────────────────────────────────────────────────────────────────

    def get_top_headlines(self, topic: str = "technology", country: str = "in",
                          page_size: int = 6) -> Dict[str, Any]:
        if self.use_real:
            return self._real_headlines(topic, country, page_size)
        return self._mock_headlines(topic, page_size)

    def search_news(self, query: str, page_size: int = 6) -> Dict[str, Any]:
        if self.use_real:
            return self._real_search(query, page_size)
        return self._mock_headlines(query, page_size)

    # ── real API ──────────────────────────────────────────────────────────────

    def _real_headlines(self, topic: str, country: str, page_size: int) -> Dict[str, Any]:
        try:
            params = {
                "apiKey": self.api_key,
                "q": topic,
                "country": country,
                "pageSize": page_size,
                "language": "en",
            }
            resp = requests.get(f"{self.BASE_URL}/top-headlines", params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            articles = self._parse_articles(data.get("articles", []))
            return {"success": True, "topic": topic, "count": len(articles), "articles": articles}
        except Exception as e:
            return {"success": False, "error": str(e), "topic": topic, "articles": []}

    def _real_search(self, query: str, page_size: int) -> Dict[str, Any]:
        try:
            params = {
                "apiKey": self.api_key,
                "q": query,
                "pageSize": page_size,
                "language": "en",
                "sortBy": "publishedAt",
            }
            resp = requests.get(f"{self.BASE_URL}/everything", params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            articles = self._parse_articles(data.get("articles", []))
            return {"success": True, "topic": query, "count": len(articles), "articles": articles}
        except Exception as e:
            return {"success": False, "error": str(e), "topic": query, "articles": []}

    @staticmethod
    def _parse_articles(raw: List[dict]) -> List[dict]:
        articles = []
        for a in raw:
            if not a.get("title") or a["title"] == "[Removed]":
                continue
            articles.append({
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
            })
        return articles

    # ── mock data ─────────────────────────────────────────────────────────────

    MOCK_ARTICLES = {
        "ai": [
            {"title": "Google DeepMind releases new reasoning model surpassing GPT-4", "source": "TechCrunch", "description": "A new AI model that shows remarkable reasoning capabilities.", "url": "https://techcrunch.com", "published_at": "2026-03-17"},
            {"title": "OpenAI announces GPT-5 with multimodal reasoning", "source": "The Verge", "description": "GPT-5 integrates vision, audio and code execution natively.", "url": "https://theverge.com", "published_at": "2026-03-17"},
            {"title": "India to invest ₹10,000 crore in AI research infrastructure", "source": "Economic Times", "description": "Government announces major AI initiative for IITs.", "url": "https://economictimes.com", "published_at": "2026-03-16"},
            {"title": "Agentic AI systems reshape enterprise workflows in 2026", "source": "Forbes", "description": "Companies are deploying autonomous agents across operations.", "url": "https://forbes.com", "published_at": "2026-03-16"},
            {"title": "New AI model can write and run Python code autonomously", "source": "Wired", "description": "Research shows LLMs now capable of multi-step coding tasks.", "url": "https://wired.com", "published_at": "2026-03-15"},
        ],
        "technology": [
            {"title": "Apple releases M4 Ultra chip with 3nm architecture", "source": "9to5Mac", "description": "The new chip delivers 40% faster performance than M3 series.", "url": "https://9to5mac.com", "published_at": "2026-03-17"},
            {"title": "SpaceX Starship completes first crewed test flight", "source": "Space.com", "description": "Starship successfully carried 4 astronauts on a suborbital flight.", "url": "https://space.com", "published_at": "2026-03-16"},
            {"title": "5G coverage reaches 95% of Indian urban areas", "source": "Economic Times", "description": "Telecom companies completed nationwide 5G rollout ahead of schedule.", "url": "https://economictimes.com", "published_at": "2026-03-15"},
        ],
        "sports": [
            {"title": "India wins T20 World Cup 2026 by defeating Australia", "source": "Cricbuzz", "description": "Team India clinched the title with a 5-wicket victory.", "url": "https://cricbuzz.com", "published_at": "2026-03-17"},
            {"title": "IPL 2026 auction sets world record with ₹200 crore sale", "source": "ESPN Cricinfo", "description": "The mega auction saw 12 players cross the ₹100 crore mark.", "url": "https://espncricinfo.com", "published_at": "2026-03-16"},
        ],
        "business": [
            {"title": "Reliance Jio launches satellite internet service across India", "source": "Business Standard", "description": "JioSat provides high-speed internet to rural areas.", "url": "https://business-standard.com", "published_at": "2026-03-17"},
            {"title": "Nifty 50 crosses 30,000 milestone for the first time", "source": "NDTV Profit", "description": "Indian stock market hits historic high driven by FII inflows.", "url": "https://ndtv.com", "published_at": "2026-03-16"},
        ],
    }

    def _mock_headlines(self, topic: str, page_size: int) -> Dict[str, Any]:
        # Find closest matching category
        topic_lower = topic.lower()
        articles = []
        for cat, items in self.MOCK_ARTICLES.items():
            if cat in topic_lower or topic_lower in cat:
                articles = items
                break
        if not articles:
            # Default to AI news
            articles = self.MOCK_ARTICLES["ai"]

        articles = articles[:page_size]
        return {
            "success": True,
            "topic": topic,
            "count": len(articles),
            "articles": articles,
            "source": "Mock Data (add NEWS_API_KEY for live news)",
        }
