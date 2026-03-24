# Architecture Documentation
## Agentic AI Based Task Automation System

---

## System Overview

The Agentic AI Task Automation System is designed as a modular, extensible platform that enables autonomous task execution through intelligent agent orchestration.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│                      (Streamlit Web Interface)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │  Task Input  │  │   Result    │  │    Logs     │                │
│  │   Widget     │  │   Display   │  │    View     │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATION LAYER                           │
│                     (AgentOrchestrator Class)                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Intent       →  Agent        →  Task        →  Result       │  │
│  │  Classification   Selection      Execution      Aggregation  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐          │
│  │  Email    │ │   File    │ │  Report   │ │ Multi-Step│          │
│  │  Agent    │ │Processing │ │  Agent    │ │   Agent   │          │
│  │           │ │  Agent    │ │           │ │           │          │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘          │
│        │             │             │             │                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐          │
│  │  Flight   │ │    Bus    │ │ Intelligent│ │   File    │          │
│  │  Agent    │ │   Agent   │ │   Email   │ │  Manager  │          │
│  │           │ │           │ │   Agent   │ │   Agent   │          │
│  └─────┬─────┘ └─────┴─────┘ └─────┬─────┘ └─────┬─────┘          │
│        │                           │             │                  │
│        │           ┌───────────────┴─────────────┘                  │
│        │           │                                                │
│  ┌─────┴───────────┴─────┐                                         │
│  │    Data Analyzer      │                                         │
│  │        Agent          │                                         │
│  └───────────────────────┘                                         │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          TOOLS LAYER                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │  LLM    │ │  Email  │ │  File   │ │   PDF   │ │  Data   │      │
│  │  Tool   │ │  Tool   │ │  Tool   │ │  Tool   │ │  Tool   │      │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │
│       │          │          │          │          │               │
│  ┌─────────┐ ┌─────────┐                                          │
│  │ Flight  │ │   Bus   │                                          │
│  │   API   │ │   API   │                                          │
│  └────┬────┘ └────┬────┘                                          │
│       │          │                                                 │
└───────┴──────────┴─────────────────┬──────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                              │
│  │ Gemini  │ │  SMTP   │ │  File   │                              │
│  │   API   │ │ Server  │ │ System  │                              │
│  └─────────┘ └─────────┘ └─────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         LOGGING LAYER                               │
│                    (ActionLogger - JSON-based)                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Timestamp | Agent | Task | Status | Details | Error         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer (app.py)

**Purpose**: Provides user interface for interaction

**Components**:
- **Task Input Widget**: Text area for natural language commands
- **Result Display**: Shows execution results with formatting
- **Agent Selector**: Direct agent selection mode
- **Logs View**: Historical execution viewing

**Technologies**: Streamlit, Custom CSS

---

### 2. Orchestration Layer (orchestrator.py)

**Purpose**: Central controller for request routing

**Responsibilities**:
- Parse user input
- Classify intent using keywords + LLM
- Extract entities (emails, dates, file paths)
- Select appropriate agent
- Manage execution context
- Aggregate results

**Key Methods**:
```python
process_request(user_input) → AgentResult
_classify_intent(text) → Dict
_select_agent(intent) → str
_extract_entities(text, intent) → Dict
```

---

### 3. Agent Layer

**Base Class**: `BaseAgent` (Abstract)
```python
class BaseAgent(ABC):
    name: str
    description: str
    status: AgentStatus
    
    @abstractmethod
    def execute(task, **kwargs) → AgentResult
    
    @abstractmethod
    def get_capabilities() → List[str]
```

**Agents**:

| Agent | Tools Used | Primary Function |
|-------|-----------|------------------|
| EmailAgent | LLMTool, EmailTool | Email composition and sending |
| FileProcessingAgent | FileTool, LLMTool | File reading and summarization |
| ReportAgent | LLMTool, FileTool, PDFTool | Report generation |
| MultiStepAgent | All agents via orchestrator | Sequential task execution |
| FlightAgent | FlightAPI | Flight search |
| BusAgent | BusAPI | Bus route search |
| IntelligentEmailAgent | LLMTool, FileTool, EmailTool | Smart email handling |
| FileOrganizerAgent | FileTool | File organization |
| DataAnalyzerAgent | DataTool, LLMTool | Data analysis |

---

### 4. Tools Layer

**LLMTool** (llm_tool.py)
- Unified interface for Gemini and OpenAI
- Text generation, summarization, email composition
- Intent classification

**EmailTool** (email_tool.py)
- SMTP connection management
- Email composition with MIME
- Attachment handling
- Draft creation

**FileTool** (file_tool.py)
- Read/write operations
- File organization by type
- Batch rename
- Search functionality

**PDFTool** (pdf_tool.py)
- ReportLab-based PDF creation
- Paragraph and table support
- Multi-section reports

**DataTool** (data_tool.py)
- Pandas-based CSV analysis
- Statistical summaries
- Correlation analysis
- Data filtering

**FlightAPI / BusAPI** (flight_api.py, bus_api.py)
- Mock APIs for demonstration
- Realistic data generation
- Search and itinerary creation

---

### 5. Logging Layer (logger.py)

**Features**:
- Singleton pattern for single log file
- Thread-safe operations
- JSON format storage
- Query by agent, status, time
- Export to TXT

**Log Entry Structure**:
```json
{
    "id": "20260315120000123456",
    "timestamp": "2026-03-15T12:00:00.000000",
    "agent": "Email Agent",
    "task": "Send email to user@example.com",
    "status": "completed",
    "details": {...},
    "error": null
}
```

---

## Data Flow

### Request Processing Flow

```
User Input
    │
    ▼
┌───────────────────┐
│  Streamlit UI     │
│  (app.py)         │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   Orchestrator    │──┐
│  process_request  │  │
└─────────┬─────────┘  │
          │            │
          ▼            │
┌───────────────────┐  │  Logs each
│ Intent Classifier │  │  action
│ (keyword + LLM)   │  │
└─────────┬─────────┘  │
          │            │
          ▼            │
┌───────────────────┐  │
│  Agent Selector   │  │
└─────────┬─────────┘  │
          │            │
          ▼            ▼
┌───────────────────┬───────────┐
│   Selected Agent  │  Logger   │
│   .execute()      │           │
└─────────┬─────────┴───────────┘
          │
          ▼
┌───────────────────┐
│   Tool(s)         │
│   execution       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   AgentResult     │
│   object          │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│   UI Display      │
└───────────────────┘
```

---

## Key Design Patterns

### 1. Strategy Pattern
- Different agents encapsulate different algorithms
- Orchestrator selects strategy at runtime

### 2. Factory Pattern
- LLMTool creates appropriate LLM provider
- Tool instantiation based on configuration

### 3. Singleton Pattern
- ActionLogger ensures single log file
- Thread-safe logging

### 4. Template Method Pattern
- BaseAgent defines execution template
- Subclasses implement specific steps

### 5. Command Pattern
- Tasks encapsulated as objects (AgentResult)
- Can be logged, undone, stored

---

## Security Considerations

1. **Credential Management**
   - Environment variables for API keys
   - Never logged or displayed
   - .env file excluded from version control

2. **Input Validation**
   - Email format validation
   - File path sanitization
   - Parameter type checking

3. **Encryption**
   - TLS for SMTP connections
   - HTTPS for API calls

4. **Access Control**
   - Local deployment only
   - No remote execution capabilities

---

## Scalability Considerations

### Current Limitations
- Single-user design
- File-based logging
- Synchronous execution

### Future Improvements
- Database for logs (PostgreSQL/MongoDB)
- Queue-based processing (Celery/RabbitMQ)
- Async agent execution
- Microservices architecture
- Container deployment (Docker/Kubernetes)

---

## Error Handling Strategy

```
Layer          Error Type              Handling
─────────────────────────────────────────────────
UI             User input errors       Validation messages
Orchestrator   Routing failures        Fallback to default
Agent          Execution errors        Result with error flag
Tool           External failures       Retry + graceful failure
Logging        IO errors               Silent failure, console log
```

---

## Configuration Management

**config.py** centralizes:
- API endpoints and keys
- Directory paths
- Default settings
- Agent configurations

**Environment Variables** (.env):
- GOOGLE_API_KEY
- OPENAI_API_KEY
- SMTP_SERVER, PORT
- EMAIL credentials

---

## Testing Strategy

### Unit Tests
- Test each tool independently
- Mock external services

### Integration Tests
- Test agent-tool interactions
- Test orchestrator routing

### End-to-End Tests
- Full workflow testing
- UI interaction testing

---

This architecture provides a solid foundation for an extensible, maintainable AI task automation system.
