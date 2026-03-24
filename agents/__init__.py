"""
Agents Package Initialization
All AI agents for task automation
"""

from .base_agent import BaseAgent, AgentResult
from .orchestrator import AgentOrchestrator
from .email_agent import EmailAgent
from .report_agent import ReportAgent
from .flight_agent import FlightAgent
from .bus_agent import BusAgent
from .train_agent import TrainAgent
from .file_organizer_agent import FileOrganizerAgent
from .browser_agent import BrowserAgent
from .weather_agent import WeatherAgent
from .news_agent import NewsAgent
from .reminder_agent import ReminderAgent
from .emergency_agent import EmergencyAgent

__all__ = [
    'BaseAgent',
    'AgentResult',
    'AgentOrchestrator',
    'EmailAgent',
    'ReportAgent',
    'FlightAgent',
    'BusAgent',
    'TrainAgent',
    'FileOrganizerAgent',
    'BrowserAgent',
    'WeatherAgent',
    'NewsAgent',
    'ReminderAgent',
    'EmergencyAgent'
]
