"""
Agent Orchestrator - Routes tasks to appropriate agents
Central controller for the multi-agent system
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentResult


class AgentOrchestrator:
    """
    Central orchestrator that manages all agents and routes tasks.
    Implements the agentic AI approach - understanding instructions,
    selecting tools, and executing without human intervention.
    """
    
    def __init__(self):
        """Initialize the orchestrator with all available agents"""
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_log: List[Dict] = []
        
        # Register all agents
        self._register_agents()
    
    def _register_agents(self):
        """Register all available agents"""
        from .email_agent import EmailAgent
        from .report_agent import ReportAgent
        from .flight_agent import FlightAgent
        from .bus_agent import BusAgent
        from .file_organizer_agent import FileOrganizerAgent
        from .browser_agent import BrowserAgent
        from .weather_agent import WeatherAgent
        from .news_agent import NewsAgent
        from .reminder_agent import ReminderAgent
        from .emergency_agent import EmergencyAgent
        from .train_agent import TrainAgent

        # Feature Manager: register all agents (reuse-first)
        from core.feature_manager import FeatureManager
        fm = FeatureManager()

        def _reg(key, cls, caps, desc):
            inst = fm.get_instance(key)
            if inst is None:
                inst = cls()
                fm.register(key, f"agents/{key}_agent.py", caps, desc, inst)
            return inst

        # Create and register agents
        self.agents = {
            "email":            _reg("email",            EmailAgent,           ["Send emails"], "Email automation"),
            "report":           _reg("report",           ReportAgent,          ["Generate reports"], "Report generator"),
            "flight":           _reg("flight",           FlightAgent,          ["Search flights"], "Flight search"),
            "bus":              _reg("bus",               BusAgent,             ["Search buses"], "Bus routes"),
            "file_organizer":   _reg("file_organizer",   FileOrganizerAgent,   ["Organize files"], "File organizer"),
            "browser":          _reg("browser",          BrowserAgent,         ["Open websites", "YouTube"], "Browser agent"),
            "weather":          _reg("weather",          WeatherAgent,         ["Current weather", "Forecast", "AI advice"], "Weather agent"),
            "news":             _reg("news",             NewsAgent,            ["Fetch news", "Summarize headlines"], "News agent"),
            "reminder":         _reg("reminder",         ReminderAgent,        ["Set reminders", "Notifications"], "Reminder agent"),
            "emergency":        _reg("emergency",        EmergencyAgent,       ["Emergency contacts", "Hospitals", "Guidance"], "Emergency agent"),
            "train":            _reg("train",            TrainAgent,           ["Search trains", "Fares", "Itinerary"], "Train ticket agent"),
        }
    
    def process_request(self, user_input: str) -> AgentResult:
        """
        Process a user request by routing to the appropriate agent.
        This is the main entry point for the agentic AI system.
        
        Args:
            user_input: Natural language instruction from user
            
        Returns:
            AgentResult from the selected agent
        """
        start_time = datetime.now()
        
        # Step 1: Understand the intent
        intent = self._classify_intent(user_input)
        
        # Step 2: Select appropriate agent
        agent_name = self._select_agent(intent)
        
        if not agent_name or agent_name not in self.agents:
            return AgentResult(
                success=False,
                message="Could not determine appropriate agent for this task",
                error=f"Unknown intent: {intent.get('intent', 'unknown')}",
                data={"user_input": user_input, "detected_intent": intent}
            )
        
        # Step 3: Execute with selected agent
        agent = self.agents[agent_name]
        
        try:
            result = agent.execute(user_input, **intent.get("entities", {}))
        except Exception as e:
            result = AgentResult(
                success=False,
                message=f"Agent execution failed: {str(e)}",
                error=str(e)
            )
        
        # Log the execution
        execution_time = (datetime.now() - start_time).total_seconds()
        
        self._log_execution(
            user_input=user_input,
            intent=intent,
            agent_name=agent_name,
            result=result,
            execution_time=execution_time
        )
        
        result.execution_time = execution_time
        result.data["agent_used"] = agent_name
        result.data["intent_detected"] = intent.get("intent", "unknown")
        
        return result
    
    def _classify_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Classify user intent using keyword matching and LLM.
        
        Args:
            user_input: User's instruction
            
        Returns:
            Intent classification
        """
        input_lower = user_input.lower()
        
        # Keyword-based classification (faster, no API call)
        intent_keywords = {
            "email_send": ["send email", "email to", "mail to", "compose email"],
            "report": ["generate report", "create report", "make report", "report on"],
            "flight": ["flight", "fly", "airplane", "air ticket", "flight search"],
            "bus": ["bus", "bus route", "bus ticket", "travel by bus"],
            "organize": ["organize", "organise", "sort files", "arrange files", "clean folder"],
            "rename": ["rename", "batch rename"],
            "move": ["move files", "transfer files"],
            "weather": [
                "weather", "temperature", "humidity", "forecast", "rain today",
                "umbrella", "hot outside", "cold outside", "climate",
            ],
            "news": [
                "news", "headlines", "latest news", "show news", "today news",
                "ai news", "tech news", "sports news", "business news",
            ],
            "reminder": [
                "remind me", "set reminder", "reminder at", "remind at",
                "don't forget", "notify me", "alert me", "schedule reminder",
            ],
            "emergency": [
                "emergency", "accident", "help me", "i met with", "urgent help",
                "hospital near", "nearest hospital", "call ambulance", "fire emergency",
                "i was attacked", "robbery", "chest pain", "unconscious", "bleeding",
            ],
            "train": [
                "train", "train ticket", "book train", "railway", "irctc",
                "train from", "train to", "express train", "rajdhani", "shatabdi",
            ],
            "browser": [
                "open youtube", "play on youtube", "youtube play", "play song", "play video",
                "open website", "open browser", "go to website", "visit website",
                "search on google", "google search", "open google", "open instagram",
                "open facebook", "open twitter", "open github", "open reddit",
                "open netflix", "open spotify", "open whatsapp", "open gmail",
                "open maps", "open wikipedia", "browse to", "navigate to",
                "go to gmail", "check gmail", "open mail", "go to mail",
                "open google maps", "go to maps", "navigate to maps",
                "launch netflix", "watch netflix", "go to netflix",
                "get directions", "map directions", "route to", "route from",
                "directions from", "on maps"
            ]
        }
        
        # Check for keyword matches
        detected_intent = None
        for intent, keywords in intent_keywords.items():
            if any(kw in input_lower for kw in keywords):
                detected_intent = intent
                break
        
        # Extract entities based on intent
        entities = self._extract_entities(user_input, detected_intent)
        
        # If no keyword match, try LLM classification
        if detected_intent is None:
            try:
                from tools.llm_tool import LLMTool
                llm = LLMTool()
                llm_result = llm.classify_intent(user_input)
                
                if llm_result.get("intent") != "unknown":
                    detected_intent = llm_result.get("intent")
                    entities.update(llm_result.get("entities", {}))
            except:
                pass
        
        return {
            "intent": detected_intent or "unknown",
            "entities": entities,
            "original_input": user_input
        }
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract relevant entities from text"""
        import re
        entities = {}
        
        # Extract email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        if emails:
            entities["emails"] = emails
            entities["to_email"] = emails[0]
        
        # Extract file paths
        file_pattern = r'["\']?([a-zA-Z]:\\[^"\'<>|*?\n]+|[./]?[\w\-./]+\.\w+)["\']?'
        files = re.findall(file_pattern, text)
        if files:
            entities["files"] = files
            entities["file_path"] = files[0]
        
        # Extract dates
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}'
        dates = re.findall(date_pattern, text)
        if dates:
            entities["dates"] = dates
            entities["date"] = dates[0]
        
        # Extract city codes (for travel)
        if intent in ["flight", "bus"]:
            city_pattern = r'\b([A-Z]{3})\b'
            cities = re.findall(city_pattern, text.upper())
            if len(cities) >= 2:
                entities["origin"] = cities[0]
                entities["destination"] = cities[1]

        # Extract email subject/body hints
        if intent in ["email_send", "email"]:
            subject_patterns = [
                r'subject\s*(?:is|:)?\s*["\']?([^"\'\n]+)',
                r'(?:about|regarding|on)\s+["\']?([^"\'\n]+)'
            ]
            for pattern in subject_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    subject = match.group(1).strip(" .,:;\t\n\"'")
                    if subject:
                        entities["subject"] = subject
                        break

            body_match = re.search(r'(?:body|message)\s*(?:is|:)?\s*["\']?(.+)', text, re.IGNORECASE)
            if body_match:
                body = body_match.group(1).strip(" .,:;\t\n\"'")
                if body:
                    entities["body"] = body

        # Extract browser-specific entities
        if intent == "browser":
            gmail_search = re.search(r'(?:search\s+for|find)\s+(.+)', text, re.IGNORECASE)
            if gmail_search and ("mail" in text.lower() or "gmail" in text.lower()):
                entities["query"] = gmail_search.group(1).strip()

            route_match = re.search(r'(?:to|towards)\s+([a-zA-Z ]+)$', text.strip(), re.IGNORECASE)
            if route_match and "map" in text.lower():
                destination = route_match.group(1).strip(" .,:;\t\n")
                if destination:
                    entities["destination"] = destination
        
        return entities
    
    def _select_agent(self, intent: Dict) -> Optional[str]:
        """
        Select the appropriate agent based on intent.
        
        Args:
            intent: Classified intent
            
        Returns:
            Agent name to use
        """
        intent_type = intent.get("intent", "unknown")
        
        # Map intents to agents
        intent_agent_map = {
            "email_send": "email",
            "email": "email",
            "report": "report",
            "flight": "flight",
            "flight_search": "flight",
            "bus": "bus",
            "bus_search": "bus",
            "organize": "file_organizer",
            "organize_files": "file_organizer",
            "rename": "file_organizer",
            "move": "file_organizer",
            "browser": "browser",
            "weather": "weather",
            "news": "news",
            "reminder": "reminder",
            "emergency": "emergency",
            "train": "train",
        }
        
        return intent_agent_map.get(intent_type)
    
    def _log_execution(
        self,
        user_input: str,
        intent: Dict,
        agent_name: str,
        result: AgentResult,
        execution_time: float
    ):
        """Log execution details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "intent": intent,
            "agent": agent_name,
            "success": result.success,
            "execution_time": execution_time
        }
        
        self.execution_log.append(log_entry)
        
        # Also log to file
        from utils.logger import log_action
        log_action(
            agent_name="Orchestrator",
            task=f"Routed to {agent_name}",
            status="completed" if result.success else "failed",
            details=log_entry
        )
    
    def execute_agent(self, agent_name: str, task: str, **kwargs) -> AgentResult:
        """
        Execute a specific agent directly.
        
        Args:
            agent_name: Name of the agent to use
            task: Task description
            **kwargs: Additional parameters
            
        Returns:
            AgentResult
        """
        if agent_name not in self.agents:
            return AgentResult(
                success=False,
                message=f"Unknown agent: {agent_name}",
                error=f"Available agents: {list(self.agents.keys())}"
            )
        
        return self.agents[agent_name].execute(task, **kwargs)
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a specific agent by name"""
        return self.agents.get(agent_name)
    
    def get_all_agents(self) -> Dict[str, Dict]:
        """Get information about all registered agents"""
        return {
            name: {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.get_capabilities(),
                "status": agent.status.value
            }
            for name, agent in self.agents.items()
        }
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities grouped by agent"""
        return {
            name: agent.get_capabilities()
            for name, agent in self.agents.items()
        }
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history"""
        return self.execution_log[-limit:]
    
    def get_llm(self):
        """Get LLM tool instance for direct use"""
        from tools.llm_tool import LLMTool
        return LLMTool()
