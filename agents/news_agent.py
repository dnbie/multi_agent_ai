"""
News Agent - Fetch news headlines and summarize using LLM
Reuses: NewsAPI (tools/news_api.py), LLMTool (tools/llm_tool.py)
"""

import re
from typing import List
from .base_agent import BaseAgent, AgentResult


class NewsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="News Agent",
            description="Fetch latest news and generate AI summaries"
        )
        from tools.news_api import NewsAPI
        self.news_api = NewsAPI()

    def get_capabilities(self) -> List[str]:
        return [
            "Fetch top headlines by topic",
            "Search news across all sources",
            "AI-generated summary of news",
            "Topics: AI, Technology, Sports, Business, India, World",
        ]

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)
        try:
            topic = kwargs.get("topic") or self._extract_topic(task)
            result = self._build_result(topic, task)
        except Exception as e:
            result = self._create_result(False, f"News agent error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── helpers ───────────────────────────────────────────────────────────────

    def _build_result(self, topic: str, task: str) -> AgentResult:
        news = self.news_api.get_top_headlines(topic)

        if not news.get("success") or not news.get("articles"):
            news = self.news_api.search_news(topic)

        if not news.get("articles"):
            return self._create_result(False, f"No news found for topic: {topic}",
                                       error="No articles returned")

        articles = news["articles"]
        summary = self._summarize(articles, topic)

        headlines = "\n".join(
            f"{i+1}. {a['title']} ({a['source']})" for i, a in enumerate(articles)
        )
        message = f"Top {len(articles)} news on '{topic}':\n{headlines}"

        return self._create_result(True, message, data={
            "topic": topic,
            "articles": articles,
            "count": len(articles),
            "summary": summary,
            "source": news.get("source", "NewsAPI"),
        })

    def _summarize(self, articles: list, topic: str) -> str:
        try:
            llm = self.get_llm()
            headlines_text = "\n".join(
                f"- {a['title']}: {a.get('description', '')}" for a in articles
            )
            prompt = (
                f"Here are the latest news headlines about '{topic}':\n{headlines_text}\n\n"
                "Write a concise 2-3 sentence summary of what is happening in this topic today. "
                "Be factual and informative."
            )
            return llm.generate_text(prompt, temperature=0.4)
        except Exception:
            return f"Found {len(articles)} articles on '{topic}'. Check headlines above."

    def _extract_topic(self, text: str) -> str:
        lower = text.lower()

        topic_map = {
            "ai": ["ai", "artificial intelligence", "machine learning", "llm", "chatgpt", "gemini"],
            "technology": ["tech", "technology", "software", "hardware", "gadget", "startup"],
            "sports": ["sports", "cricket", "football", "ipl", "fifa", "olympics", "match"],
            "business": ["business", "market", "stock", "economy", "finance", "startup", "nifty"],
            "india": ["india", "indian", "modi", "government", "delhi", "parliament"],
            "world": ["world", "global", "international", "usa", "china", "russia"],
        }
        for topic, keywords in topic_map.items():
            if any(k in lower for k in keywords):
                return topic

        # Fallback: extract words after "news about" / "news on" / "latest"
        for pat in [r'news\s+(?:about|on|for)\s+([a-z\s]+)', r'latest\s+([a-z\s]+)\s+news',
                    r'show\s+([a-z\s]+)\s+news', r'get\s+([a-z\s]+)\s+news']:
            m = re.search(pat, lower)
            if m:
                extracted = m.group(1).strip().rstrip("?.,")
                if len(extracted) > 1:
                    return extracted

        return "technology"
