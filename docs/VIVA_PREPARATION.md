# Viva Preparation Guide
## Agentic AI Based Task Automation System

---

## 1. Project Overview Questions

### Q: What is an Agentic AI system?
**A:** An Agentic AI system is an artificial intelligence approach where the AI agent:
- **Understands** user instructions in natural language
- **Decides** which tools or actions are needed
- **Executes** tasks autonomously without human intervention
- **Returns** results to the user

Unlike traditional chatbots that just respond to queries, agentic AI systems can take actions and complete tasks independently.

### Q: What problem does your project solve?
**A:** This project automates repetitive tasks that typically require manual effort:
- Composing and sending emails
- Reading and summarizing documents
- Creating reports
- Organizing files
- Analyzing data

The AI agent understands what the user wants and automatically selects the right tool to complete the task.

### Q: What is the architecture of your system?
**A:** The system follows a layered architecture:

1. **UI Layer (Streamlit)**: User interface for interaction
2. **Orchestrator Layer**: Routes tasks to appropriate agents
3. **Agent Layer**: Specialized agents for different task types
4. **Tools Layer**: Implements actual functionality (SMTP, file I/O, etc.)
5. **Logging Layer**: Records all actions for audit and debugging

---

## 2. Technical Questions

### Q: Why did you choose Python for this project?
**A:** Python was chosen because:
- Rich ecosystem for AI/ML (LangChain, Google GenAI, OpenAI)
- Easy integration with Streamlit for web UI
- Extensive libraries for file handling, email, PDF generation
- Clean syntax suitable for rapid development
- Strong community support

### Q: Explain the Agent design pattern you used.
**A:** We use an **Abstract Base Class pattern**:
```python
class BaseAgent(ABC):
    @abstractmethod
    def execute(self, task, **kwargs) -> AgentResult
    
    @abstractmethod
    def get_capabilities(self) -> List[str]
```
Each specialized agent inherits from BaseAgent and implements these methods. This ensures:
- Consistent interface across all agents
- Easy addition of new agents
- Standardized result format

### Q: How does the Orchestrator work?
**A:** The Orchestrator:
1. **Receives** user input
2. **Classifies** intent using keyword matching + LLM
3. **Extracts** entities (emails, file paths, dates)
4. **Selects** the appropriate agent
5. **Executes** the task with extracted parameters
6. **Logs** the execution
7. **Returns** the result

### Q: How do you handle LLM integration?
**A:** We support both Google Gemini and OpenAI:
```python
class LLMTool:
    def __init__(self, provider="gemini"):
        if provider == "gemini":
            self.llm = GeminiLLM(api_key)
        else:
            self.llm = OpenAILLM(api_key)
```
The LLMTool provides a unified interface for:
- Text generation
- Email composition
- Summarization
- Report generation
- Intent classification

### Q: How does multi-step task execution work?
**A:** The MultiStepAgent:
1. Parses the task to identify individual steps
2. Maintains a context dictionary shared between steps
3. Executes steps sequentially
4. Passes output from one step as input to the next
5. Stops on failure and reports status

Example: "Read file.txt, summarize, email to user@example.com"
- Step 1: Read file → context["content"] = file_content
- Step 2: Summarize → context["summary"] = summarized_text
- Step 3: Email → sends context["summary"] to user

---

## 3. Implementation Questions

### Q: How do you send emails?
**A:** Using Python's SMTP library:
```python
with smtplib.SMTP(server, port) as smtp:
    smtp.starttls()  # Enable TLS encryption
    smtp.login(email, password)
    smtp.sendmail(from_addr, to_addr, message)
```
For Gmail, users need to generate an App Password (not regular password).

### Q: How do you generate PDFs?
**A:** Using ReportLab library:
```python
from reportlab.platypus import SimpleDocTemplate, Paragraph
doc = SimpleDocTemplate(filename)
doc.build([Paragraph(text, style)])
```
We support titles, headings, paragraphs, and tables.

### Q: How does the logging system work?
**A:** We use a JSON-based logging system:
```python
{
    "id": "20260315120000123456",
    "timestamp": "2026-03-15T12:00:00",
    "agent": "Email Agent",
    "task": "Send email",
    "status": "completed",
    "details": {...}
}
```
Logs are stored in `logs/actions.json` and can be:
- Filtered by agent or status
- Exported to TXT format
- Viewed in the UI

### Q: How do you handle errors?
**A:** Multiple levels of error handling:
1. **Input validation**: Check required parameters
2. **Try-except blocks**: Catch exceptions in tool operations
3. **Result objects**: Standardized success/failure responses
4. **Logging**: Record all errors for debugging

---

## 4. Feature-Specific Questions

### Q: Explain the Flight Search functionality.
**A:** The FlightAgent uses a mock API that:
- Maintains airport and airline databases
- Generates realistic flight options with prices
- Creates multi-leg itineraries
- Returns formatted search results

In production, this would integrate with real APIs like Amadeus or Skyscanner.

### Q: How does file organization work?
**A:** The FileOrganizerAgent:
1. Scans the source directory
2. Categorizes files by extension (images, documents, code, etc.)
3. Creates category folders in destination
4. Moves/copies files to appropriate folders
5. Returns a summary of operations

### Q: How does data analysis work?
**A:** Using Pandas for analysis:
1. Read CSV into DataFrame
2. Calculate statistics (mean, std, min, max)
3. Identify missing values and duplicates
4. Find correlations between numeric columns
5. Use LLM to generate natural language insights
6. Save results to file

---

## 5. Security & Best Practices

### Q: How do you handle sensitive data like API keys?
**A:** Using environment variables:
- Keys stored in `.env` file (not committed to git)
- Loaded using `python-dotenv`
- Never displayed in UI or logs
- Example shows masked output

### Q: What security measures are implemented?
**A:**
- TLS encryption for email
- Input validation to prevent injection
- File path sanitization
- No execution of arbitrary code
- Logging without sensitive data

---

## 6. Future Scope & Improvements

### Q: What improvements could be made?
**A:**
1. **Voice Interface**: Add speech recognition for hands-free operation
2. **Cloud Deployment**: Deploy on AWS/GCP for accessibility
3. **Real APIs**: Integrate actual flight/bus booking APIs
4. **Mobile App**: React Native or Flutter companion app
5. **Multi-language**: Support for regional languages
6. **Calendar Integration**: Connect with Google Calendar
7. **Advanced Analytics**: More sophisticated data visualizations

### Q: How would you scale this system?
**A:**
- Microservices architecture for agents
- Queue-based task processing
- Database instead of JSON logs
- Caching for API responses
- Load balancing for multiple users

---

## 7. Demo Scenarios

### Scenario 1: Email Automation
```
Input: "Send an email to john@company.com about the project meeting tomorrow at 3 PM"
Expected: AI generates professional email, sends via SMTP
```

### Scenario 2: Document Summary
```
Input: "Summarize the file research_report.txt"
Expected: Reads file, generates AI summary, saves to outputs/summaries/
```

### Scenario 3: Multi-Step Task
```
Input: "Read notes.txt, summarize it, and email the summary to team@company.com"
Expected: Reads → Summarizes → Sends email (all automatic)
```

### Scenario 4: Flight Search
```
Input: "Search flights from DEL to BOM on 2026-03-25"
Expected: Returns list of flights with prices, times, airlines
```

### Scenario 5: Data Analysis
```
Input: "Analyze the sales data in sales.csv"
Expected: Statistical summary + AI insights + saved report
```

---

## 8. Code Walkthrough Points

1. **config.py**: Central configuration management
2. **agents/base_agent.py**: Abstract base class with common functionality
3. **agents/orchestrator.py**: Intent classification and routing
4. **tools/llm_tool.py**: LLM integration abstraction
5. **tools/email_tool.py**: SMTP implementation
6. **app.py**: Streamlit UI components

---

## 9. Key Terminology

| Term | Definition |
|------|------------|
| **Agent** | Autonomous component that executes specific tasks |
| **Orchestrator** | Central controller that routes user requests |
| **Tool** | Low-level module that implements functionality |
| **Intent** | The detected purpose/action from user input |
| **Entity** | Extracted parameters (email, date, file path) |
| **LLM** | Large Language Model for text generation |

---

## 10. Common Viva Tips

1. **Know your code**: Be ready to explain any function
2. **Understand flow**: Trace a request from UI to result
3. **Be honest**: If you don't know, say you'll look into it
4. **Show enthusiasm**: Discuss future improvements
5. **Prepare demo**: Have working examples ready
6. **Anticipate errors**: Know common failure points

Good luck with your viva! 🎓
