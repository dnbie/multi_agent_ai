# Agent X - Task Automation System

## BSc Final Year Project

### Project Overview
This project implements an **Agentic AI approach** where AI agents can understand user instructions, decide the required tools, execute tasks, and return results **without human intervention**.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

**Default Login:** `admin` / `admin123`

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STREAMLIT UI                                    │
│                         (User Interface Layer)                               │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT ORCHESTRATOR                                 │
│                    (Routes tasks to appropriate agents)                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
        ┌─────────────┬───────────┼───────────┬─────────────┐
        │             │           │           │             │
        ▼             ▼           ▼           ▼             ▼
┌───────────┐  ┌───────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐
│   Email   │  │  Report   │ │ Flight  │ │   Bus   │ │   Train   │
│   Agent   │  │  Agent    │ │  Agent  │ │  Agent  │ │   Agent   │
└───────────┘  └───────────┘ └─────────┘ └─────────┘ └───────────┘
        │             │           │           │             │
        ▼             ▼           ▼           ▼             ▼
┌───────────┐  ┌───────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐
│  Weather  │  │   News    │ │ Browser │ │Reminder │ │ Emergency │
│   Agent   │  │  Agent    │ │  Agent  │ │  Agent  │ │   Agent   │
└───────────┘  └───────────┘ └─────────┘ └─────────┘ └───────────┘
                       │
                       ▼
              ┌───────────────┐
              │File Organizer │
              │    Agent      │
              └───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TOOLS LAYER                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  SMTP   │ │  File   │ │   PDF   │ │   LLM   │ │   API   │ │  Logger │   │
│  │  Tool   │ │  Tool   │ │  Tool   │ │  Tool   │ │  Tools  │ │  Tool   │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOGGING SYSTEM                                     │
│                    (Records all actions with timestamps)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
agentic_ai_system/
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── agents/                         # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py              # Base agent class
│   ├── orchestrator.py            # Agent orchestrator
│   ├── email_agent.py             # Email automation agent
│   ├── file_processing_agent.py   # File processing agent
│   ├── report_agent.py            # Report generation agent
│   ├── multi_step_agent.py        # Multi-step task agent
│   ├── flight_agent.py            # Flight search agent
│   ├── bus_agent.py               # Bus route agent
│   ├── intelligent_email_agent.py # Smart email agent
│   ├── file_organizer_agent.py    # File organizer agent
│   └── data_analyzer_agent.py     # Data analysis agent
│
├── tools/                          # Tool modules
│   ├── __init__.py
│   ├── email_tool.py              # SMTP email operations
│   ├── file_tool.py               # File operations
│   ├── pdf_tool.py                # PDF generation
│   ├── llm_tool.py                # LLM integration
│   ├── flight_api.py              # Flight API (mock)
│   ├── bus_api.py                 # Bus route API (mock)
│   └── data_tool.py               # Data analysis tools
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── logger.py                  # Action logging system
│   └── helpers.py                 # Helper functions
│
├── data/                           # Data files
│   ├── sample_data.csv            # Sample CSV for analysis
│   ├── sample_email.txt           # Sample email content
│   └── bus_routes.json            # Bus route data
│
├── outputs/                        # Output files
│   ├── reports/                   # Generated reports
│   ├── summaries/                 # File summaries
│   └── organized/                 # Organized files
│
├── logs/                           # Log files
│   └── actions.json               # Action logs
│
└── docs/                           # Documentation
    ├── ARCHITECTURE.md            # Architecture details
    ├── VIVA_PREPARATION.md        # Viva Q&A
    └── FUTURE_SCOPE.md            # Future enhancements
```

---

## 🚀 Features

| Agent | Description |
|-------|-------------|
| **Email Automation Agent** | Generate and send emails using LLM + SMTP |
| **File Processing Agent** | Read, summarize, and save file content |
| **Report Generation Agent** | Create formatted reports (TXT & PDF) |
| **Multi-Step Task Agent** | Execute sequential tasks automatically |
| **Flight Search Agent** | Search flights and plan itineraries |
| **Bus Route Agent** | Find bus routes and schedules |
| **Intelligent Email Agent** | Read, reply, and manage emails smartly |
| **File Manager Agent** | Organize, rename, and move files |
| **Data Analyzer Agent** | Analyze CSV data and generate insights |

---

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **UI Framework**: Streamlit
- **LLM**: Google Gemini API / OpenAI API
- **Email**: SMTP (Gmail/Outlook)
- **PDF Generation**: ReportLab
- **Data Analysis**: Pandas
- **Logging**: JSON-based custom logger

---

## 📦 Installation

### 1. Clone/Download the Project
```bash
cd "agentic ai"
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
copy .env.example .env
# Edit .env with your API keys
```

### 5. Run the Application
```bash
streamlit run app.py
```

---

## ⚙️ Configuration

Edit `.env` file with your credentials:

```env
# LLM API (Choose one)
GOOGLE_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key

# Email SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

---

## 📝 Example Usage

### 1. Email Automation
```
Input: "Send an email to john@example.com about project deadline tomorrow"
Output: Email composed and sent with LLM-generated professional content
```

### 2. File Summarization
```
Input: "Summarize the document research_paper.txt"
Output: AI-generated summary saved to outputs/summaries/
```

### 3. Multi-Step Task
```
Input: "Read report.txt, summarize it, and email to team@company.com"
Output: File read → Summarized → Email sent (all automated)
```

---

## 👨‍🎓 For Viva Preparation

See `docs/VIVA_PREPARATION.md` for:
- Technical questions and answers
- Architecture explanations
- Code walkthrough guide
- Demo scenarios

---

## 🔮 Future Scope

- Voice command integration
- Multi-language support
- Cloud deployment (AWS/GCP)
- Mobile application
- More API integrations

---

## 📄 License

This project is for educational purposes (BSc Final Year Project).

---

## 👤 Author

BSc Computer Science Final Year Project
