"""
Base Agent - Abstract base class for all AI agents
Provides common functionality and interface for agent implementations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Status of agent execution"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentResult:
    """
    Result object returned by agent operations.
    Standardizes the response format across all agents.
    """
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    steps: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "steps": self.steps
        }
    
    def add_step(self, step_name: str, status: str, details: Dict = None):
        """Add an execution step"""
        self.steps.append({
            "step": step_name,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Implements core functionality and defines the interface.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.execution_history: List[AgentResult] = []
        self._start_time: Optional[datetime] = None
        
        # Initialize logging
        from utils.logger import log_action
        self.log_action = log_action
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> AgentResult:
        """
        Execute the agent's primary task.
        Must be implemented by all subclasses.
        
        Args:
            task: Task description or instruction
            **kwargs: Additional task parameters
            
        Returns:
            AgentResult with execution results
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of agent capabilities.
        Must be implemented by all subclasses.
        
        Returns:
            List of capability descriptions
        """
        pass
    
    def _start_execution(self, task: str):
        """Mark start of execution"""
        self.status = AgentStatus.RUNNING
        self._start_time = datetime.now()
        
        self.log_action(
            agent_name=self.name,
            task=task,
            status="started",
            details={"timestamp": self._start_time.isoformat()}
        )
    
    def _end_execution(self, result: AgentResult):
        """Mark end of execution"""
        if self._start_time:
            result.execution_time = (datetime.now() - self._start_time).total_seconds()
        
        self.status = AgentStatus.SUCCESS if result.success else AgentStatus.FAILED
        self.execution_history.append(result)
        
        self.log_action(
            agent_name=self.name,
            task=result.message,
            status="completed" if result.success else "failed",
            details=result.data,
            error=result.error
        )
    
    def _create_result(
        self,
        success: bool,
        message: str,
        data: Dict = None,
        error: str = None
    ) -> AgentResult:
        """Create a standardized result object"""
        return AgentResult(
            success=success,
            message=message,
            data=data or {},
            error=error
        )
    
    def get_llm(self):
        """Get LLM tool instance"""
        from tools.llm_tool import LLMTool
        return LLMTool()
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "executions": len(self.execution_history),
            "last_execution": self.execution_history[-1].to_dict() if self.execution_history else None
        }
    
    def validate_input(self, required: List[str], provided: Dict) -> Optional[str]:
        """
        Validate required inputs are provided.
        
        Args:
            required: List of required parameter names
            provided: Dictionary of provided parameters
            
        Returns:
            Error message if validation fails, None otherwise
        """
        missing = [r for r in required if r not in provided or not provided[r]]
        
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None
    
    def parse_instruction(self, instruction: str) -> Dict[str, Any]:
        """
        Parse natural language instruction using LLM.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Parsed instruction with identified parameters
        """
        try:
            llm = self.get_llm()
            result = llm.classify_intent(instruction)
            return result
        except Exception as e:
            return {"error": str(e), "original": instruction}
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', status='{self.status.value}')>"
