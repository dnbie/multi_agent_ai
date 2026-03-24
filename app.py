"""
Agent X - Task Automation System - Main Application
Streamlit-based user interface for the multi-agent system
"""

import streamlit as st
from datetime import datetime
import json
import os

# Import authentication module
from auth import require_auth, show_user_info_sidebar, is_logged_in, logout

# Import profile settings page
from views.profile_settings import render_profile_settings

# Import payment module
from utils.payment import render_payment_form, show_payment_success, render_book_now_button

# ── Per-agent example commands ──────────────────────────────────────────────
AGENT_EXAMPLES = {
    "email": {
        "placeholder": "Send email to john@example.com about the project deadline",
        "examples": [
            "Send email to boss@company.com about quarterly review",
            "Draft email to team@office.com about the Friday meeting",
            "Send follow-up email to client@biz.com regarding proposal",
        ],
    },
    "report": {
        "placeholder": "Generate a report about quarterly sales performance",
        "examples": [
            "Generate a report on monthly expenses",
            "Create a project status report for the team",
            "Write a detailed report on customer feedback",
        ],
    },
    "flight": {
        "placeholder": "Search flights from Delhi to Mumbai on 2026-04-15",
        "examples": [
            "Search flights from DEL to BOM on 2026-04-15",
            "Find cheapest flights from Bangalore to Hyderabad next week",
            "Book flight from Chennai to Kolkata on 2026-05-01",
        ],
    },
    "bus": {
        "placeholder": "Find buses from Delhi to Jaipur tomorrow morning",
        "examples": [
            "Find buses from Mumbai to Pune tomorrow morning",
            "Search bus routes from Bangalore to Mysore",
            "Show bus schedules from Chennai to Coimbatore",
        ],
    },
    "train": {
        "placeholder": "Book train from Coimbatore to Chennai tomorrow",
        "examples": [
            "Book train from Coimbatore to Chennai tomorrow",
            "Find trains from Delhi to Mumbai on 2026-04-10",
            "Search Rajdhani express from Delhi to Bangalore",
        ],
    },
    "file_organizer": {
        "placeholder": "Organize all files in the selected folder by file type",
        "examples": [
            "Organize all files in the selected folder by file type",
            "Find all PDF files in my Documents folder",
            "Rename all images in the folder with today's date prefix",
        ],
    },
    "browser": {
        "placeholder": "Play Shape of You by Ed Sheeran on YouTube",
        "examples": [
            "Play Shape of You by Ed Sheeran on YouTube",
            "Search for Python tutorials on Google",
            "Open Gmail and search for emails about invoice",
            "Get directions from Coimbatore to Chennai on Maps",
        ],
    },
    "weather": {
        "placeholder": "What is the weather in Chennai today? Should I carry an umbrella?",
        "examples": [
            "What is the weather in Chennai today?",
            "Show 3-day forecast for Mumbai",
            "Is it going to rain in Coimbatore tomorrow?",
            "Weather in Delhi — should I carry a jacket?",
        ],
    },
    "news": {
        "placeholder": "Show me today's top AI and technology news",
        "examples": [
            "Show today's top AI news headlines",
            "What are the latest technology news?",
            "Show sports news for today",
            "Latest business and finance news",
        ],
    },
    "reminder": {
        "placeholder": "Remind me to take medicine at 8 PM today",
        "examples": [
            "Remind me to take medicine at 8 PM",
            "Set a reminder to call mom in 30 minutes",
            "Remind me to submit the assignment tomorrow at 9 AM",
            "Show all my pending reminders",
        ],
    },
    "emergency": {
        "placeholder": "I met with an accident near Chennai, need help",
        "examples": [
            "I met with an accident near Chennai, need help",
            "Show emergency contacts and nearest hospitals in Mumbai",
            "Fire emergency in Bangalore, what should I do?",
            "Chest pain — need immediate assistance in Delhi",
        ],
    },
}

_AUTO_PLACEHOLDER = (
    "Example: Search flights from Delhi to Mumbai tomorrow, "
    "then email the results to me@example.com"
)

# Page configuration
st.set_page_config(
    page_title="Agent X",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    .info-box {
        padding: 1rem;
        background-color: #cce5ff;
        border-radius: 5px;
        border: 1px solid #b8daff;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'orchestrator' not in st.session_state:
        from agents.orchestrator import AgentOrchestrator
        st.session_state.orchestrator = AgentOrchestrator()
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None

    if 'output_chat_history' not in st.session_state:
        st.session_state.output_chat_history = []

    if 'output_chat_signature' not in st.session_state:
        st.session_state.output_chat_signature = ""

    if '_prefill_task' not in st.session_state:
        st.session_state['_prefill_task'] = ""

    if '_clear_task_input' not in st.session_state:
        st.session_state['_clear_task_input'] = False

    if 'selected_provider' not in st.session_state:
        st.session_state.selected_provider = "gemini"
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "gemini-1.5-flash"

    if 'report_preview' not in st.session_state:
        st.session_state.report_preview = None


def choose_local_folder() -> str:
    """Open native folder picker and return selected path, or empty string if cancelled/unsupported."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select folder")
        root.destroy()

        return folder or ""
    except Exception:
        return ""


def render_sidebar():
    """Render the sidebar with agent selection and settings"""
    st.sidebar.markdown("## 🤖 Agent X")
    st.sidebar.markdown("---")
    
    # Mode selection
    mode = st.sidebar.radio(
        "Select Mode",
        ["🧠 Auto (Intelligent)", "🎯 Direct Agent", "📊 Logs & History", "⚙️ Profile Settings"],
        help="Auto mode intelligently selects the agent. Direct mode lets you choose."
    )
    
    selected_agent = None
    
    if mode == "🎯 Direct Agent":
        st.sidebar.markdown("### Select Agent")
        
        agents = {
            "📧 Email Agent":       "email",
            "📋 Report Generator":  "report",
            "✈️ Flight Search":     "flight",
            "🚌 Bus Routes":        "bus",
            "🚆 Train Tickets":     "train",
            "📁 File Organizer":    "file_organizer",
            "🌐 Browser / Web":     "browser",
            "🌤️ Weather":           "weather",
            "📰 News":              "news",
            "⏰ Reminders":         "reminder",
            "🚨 Emergency":         "emergency",
        }
        
        selected_display = st.sidebar.selectbox(
            "Choose Agent",
            list(agents.keys())
        )
        selected_agent = agents[selected_display]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    
    # Settings
    show_steps = st.sidebar.checkbox("Show execution steps", value=True)
    show_raw = st.sidebar.checkbox("Show raw output", value=False)

    # ── Model selector ──────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Model")

    _PROVIDER_MODELS = {
        "gemini": [
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-pro",
        ],
        "openai": [
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-4o",
            "gpt-4-turbo",
        ],
    }

    _new_provider = st.sidebar.selectbox(
        "Provider",
        options=list(_PROVIDER_MODELS.keys()),
        index=list(_PROVIDER_MODELS.keys()).index(st.session_state.selected_provider),
        format_func=lambda p: "Google Gemini" if p == "gemini" else "OpenAI",
        key="provider_select",
    )

    _available_models = _PROVIDER_MODELS[_new_provider]
    _cur_model = (
        st.session_state.selected_model
        if st.session_state.selected_model in _available_models
        else _available_models[0]
    )

    _new_model = st.sidebar.selectbox(
        "Model",
        options=_available_models,
        index=_available_models.index(_cur_model),
        key="model_select",
    )

    st.sidebar.caption(f"Active: `{_new_model}`")

    if _new_provider != st.session_state.selected_provider or _new_model != st.session_state.selected_model:
        st.session_state.selected_provider = _new_provider
        st.session_state.selected_model = _new_model
        if "orchestrator" in st.session_state:
            del st.session_state["orchestrator"]
        from tools.llm_tool import set_model_override
        set_model_override(_new_provider, _new_model)
        st.rerun()

    # Ensure override is always active (survives page interactions / hot-reload)
    from tools.llm_tool import set_model_override
    set_model_override(st.session_state.selected_provider, st.session_state.selected_model)

    # ── System Prompt editor ────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧠 System Prompt (LLM Instructions)")

    with st.sidebar.expander("Edit System Prompt", expanded=False):
        from tools.llm_tool import load_system_prompt, save_system_prompt

        current_prompt = load_system_prompt()
        edited_prompt = st.text_area(
            "Instructions sent to the LLM before every request:",
            value=current_prompt,
            height=240,
            key="sidebar_system_prompt_editor",
            help="These instructions are prepended to every LLM call as background context."
        )

        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 Save", key="save_system_prompt_btn", use_container_width=True):
                save_system_prompt(edited_prompt)
                st.success("Saved!")
        with col_reset:
            if st.button("↩ Reset", key="reset_system_prompt_btn", use_container_width=True):
                default = (
                    "You are a helpful, professional AI assistant that is part of an "
                    "Agent X Task Automation System.\n\n"
                    "Your responsibilities:\n"
                    "- Understand the user's intent clearly and respond accurately and concisely.\n"
                    "- When generating emails, keep them professional, polite, and to-the-point.\n"
                    "- When summarizing files or data, be accurate and highlight key insights.\n"
                    "- When generating reports, use structured headings and bullet points.\n"
                    "- Always be factual. Do not make up information.\n"
                    "- If uncertain, say so and ask the user for clarification.\n\n"
                    "Language style: Clear, professional, helpful."
                )
                save_system_prompt(default)
                st.success("Reset to default!")
                st.rerun()

        st.caption(f"Stored at: prompts/system_prompt.txt")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 Quick Help")

    # Initialize example shuffle state
    if "example_shuffle_key" not in st.session_state:
        st.session_state.example_shuffle_key = 0
    
    # Dynamic examples — show agent-specific examples in Direct mode
    if mode == "🎯 Direct Agent" and selected_agent and selected_agent in AGENT_EXAMPLES:
        _agent_label = selected_display.split(" ", 1)[-1]   # strip emoji part
        with st.sidebar.expander(f"📋 Examples for {_agent_label}", expanded=True):
            # Refresh button
            if st.button("🔄 Refresh Examples", key="refresh_direct_examples", use_container_width=True):
                st.session_state.example_shuffle_key += 1
                st.rerun()
            
            import random
            examples = AGENT_EXAMPLES[selected_agent]["examples"].copy()
            random.seed(st.session_state.example_shuffle_key)
            random.shuffle(examples)
            
            for cmd in examples:
                st.markdown(f"- *{cmd}*")
    else:
        with st.sidebar.expander("Example Commands", expanded=False):
            # Refresh button
            if st.button("🔄 Refresh Examples", key="refresh_all_examples", use_container_width=True):
                st.session_state.example_shuffle_key += 1
                st.rerun()
            
            import random
            random.seed(st.session_state.example_shuffle_key)
            
            for _key, _val in AGENT_EXAMPLES.items():
                agent_name = next(
                    (k.split(" ", 1)[-1] for k, v in {
                        "📧 Email Agent":       "email",
                        "📋 Report Generator":  "report",
                        "✈️ Flight Search":     "flight",
                        "🚌 Bus Routes":        "bus",
                        "🚆 Train Tickets":     "train",
                        "📁 File Organizer":    "file_organizer",
                        "🌐 Browser / Web":     "browser",
                        "🌤️ Weather":           "weather",
                        "📰 News":              "news",
                        "⏰ Reminders":         "reminder",
                        "🚨 Emergency":         "emergency",
                    }.items() if v == _key),
                    _key.replace("_", " ").title()
                )
                st.markdown(f"**{agent_name}**")
                # Pick a random example for each agent
                example = random.choice(_val['examples'])
                st.markdown(f"- *{example}*")
                st.markdown("")
    
    return mode, selected_agent, show_steps, show_raw


def _save_previewed_report(content: str, output_format: str):
    """Save the previewed (and possibly user-edited) report content."""
    preview = st.session_state.report_preview
    with st.spinner("Saving report..."):
        agent = st.session_state.orchestrator.get_agent("report")
        result = agent.save_report(
            content=content,
            topic=preview["topic"],
            author=preview["author"],
            output_format=output_format,
        )
    st.session_state.current_result = result
    st.session_state.report_preview = None
    st.session_state.history.append({
        "timestamp": datetime.now().isoformat(),
        "input": f"[Save report: {preview['topic']}]",
        "result": result.to_dict(),
    })
    st.rerun()


def render_report_preview():
    """Show the LLM-generated report to the user for editing/approval before saving."""
    preview = st.session_state.report_preview
    if not preview:
        return

    st.markdown("---")
    st.markdown("### 📋 Report Preview")
    st.caption(
        f"Topic: **{preview['topic']}** &nbsp;·&nbsp; Author: {preview['author']} &nbsp;·&nbsp; "
        f"Review and edit below, then choose how to save."
    )

    edited_content = st.text_area(
        "Edit report content:",
        height=480,
        key="report_content_edit",
        help="The AI-generated content is shown here. You can edit it freely before saving.",
    )

    st.markdown("")
    col_regen, col_txt, col_pdf, col_both, col_discard = st.columns([2, 2, 2, 2, 1])

    with col_regen:
        if st.button("♻️ Regenerate", use_container_width=True,
                     help="Ask the AI to rewrite the report from scratch"):
            with st.spinner("Regenerating report..."):
                agent = st.session_state.orchestrator.get_agent("report")
                new_data = agent.generate_content_only(
                    preview["task"], **preview.get("kwargs", {})
                )
            st.session_state.report_preview = new_data
            st.session_state["report_content_edit"] = new_data["content"]
            st.rerun()

    with col_txt:
        if st.button("💾 Save as TXT", use_container_width=True):
            _save_previewed_report(edited_content, "txt")

    with col_pdf:
        if st.button("📄 Save as PDF", use_container_width=True):
            _save_previewed_report(edited_content, "pdf")

    with col_both:
        if st.button("📦 Save Both", use_container_width=True, type="primary"):
            _save_previewed_report(edited_content, "both")

    with col_discard:
        if st.button("✕", use_container_width=True, help="Discard and start over"):
            st.session_state.report_preview = None
            st.rerun()


def render_main_interface(mode, selected_agent, show_steps, show_raw):
    """Render the main interface"""
    st.markdown('<p class="main-header">🤖 Agent X - Task Automation System</p>', unsafe_allow_html=True)
    
    # Description
    st.markdown("""
    <div class="info-box">
    <strong>Intelligent Task Automation:</strong> Enter your task in natural language. 
    The AI agent will understand, select the right tool, execute, and return results automatically.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Check if Email Agent is selected in Direct Agent mode
    if mode == "🎯 Direct Agent" and selected_agent == "email":
        render_email_agent_ui(show_steps, show_raw)
        return
    
    # Default input area for other agents
    # Compute dynamic placeholder and examples based on selected agent
    if mode == "🎯 Direct Agent" and selected_agent and selected_agent in AGENT_EXAMPLES:
        _active_placeholder = AGENT_EXAMPLES[selected_agent]["placeholder"]
        _active_examples    = AGENT_EXAMPLES[selected_agent]["examples"]
    else:
        _active_placeholder = _AUTO_PLACEHOLDER
        _active_examples    = [
            "Search flights from Delhi to Mumbai on 2026-04-15",
            "Send email to team@office.com about the Friday standup",
            "Weather in Chennai today — should I carry an umbrella?",
            "Remind me to submit assignment at 7 PM",
            "Show today's top AI news headlines",
        ]

    # Streamlit keyed widgets ignore `value=` updates after first render.
    # Push pending example text into the widget's session key before drawing it.
    if st.session_state.get("_clear_task_input", False):
        st.session_state["task_input_typed"] = ""
        st.session_state["_clear_task_input"] = False

    _prefill = st.session_state.get("_prefill_task", "")
    if _prefill:
        st.session_state["task_input_typed"] = _prefill
        st.session_state["_prefill_task"] = ""

    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_area(
            "Enter your task:",
            height=100,
            placeholder=_active_placeholder,
            key="task_input_typed"
        )

    with col2:
        st.markdown("")
        st.markdown("")
        execute_btn = st.button("🚀 Execute", type="primary", use_container_width=True)
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    # ── Quick-fill example buttons ────────────────────────────────────────
    # Initialize example shuffle state for main area
    if "main_example_shuffle_key" not in st.session_state:
        st.session_state.main_example_shuffle_key = 0
    
    with st.expander("💡 Example Commands — click to fill", expanded=False):
        # Shuffle examples based on key
        import random
        shuffled_examples = _active_examples.copy()
        random.seed(st.session_state.main_example_shuffle_key)
        random.shuffle(shuffled_examples)
        # Take first 5 (or fewer if less available)
        display_examples = shuffled_examples[:5]
        
        # Refresh button and example buttons in columns
        refresh_col, *ex_cols = st.columns([1] + [2] * len(display_examples))
        
        with refresh_col:
            if st.button("🔄", key="refresh_main_examples", help="Refresh examples", use_container_width=True):
                st.session_state.main_example_shuffle_key += 1
                st.rerun()
        
        for idx, ex_cmd in enumerate(display_examples):
            with ex_cols[idx]:
                if st.button(ex_cmd, key=f"example_btn_{idx}", use_container_width=True):
                    st.session_state["_prefill_task"] = ex_cmd
                    st.rerun()

    # File upload (optional)
    ACCEPTED_EXTENSIONS = [
        "txt", "pdf", "csv", "xlsx", "xls",
        "docx", "doc", "json", "md", "log", "py"
    ]

    # Which agents can actually use an uploaded file
    FILE_AWARE_AGENTS = {
        "report", "file_organizer"
    }

    show_uploader = (
        mode == "🧠 Auto (Intelligent)"
        or (mode == "🎯 Direct Agent" and selected_agent in FILE_AWARE_AGENTS)
    )

    is_file_organizer = (mode == "🎯 Direct Agent" and selected_agent == "file_organizer")

    uploaded_files = None
    file_content = None
    file_name = None
    folder_path_input = None

    if show_uploader:
        # --- Folder path input with native picker ---
        # We use a separate non-widget state key "_picked_folder_path" so we never
        # touch the widget's own key after instantiation (Streamlit restriction).
        _prefill = st.session_state.get("_picked_folder_path", "")

        path_col, browse_col = st.columns([5, 1])

        with path_col:
            folder_path_input = st.text_input(
                "📁 Folder / Directory Path" + (" *" if is_file_organizer else " (optional)"),
                value=_prefill,
                placeholder=r"e.g. C:\Users\You\Documents\MyFolder",
                key="folder_path_input_typed",
                help="Type a path or click 📂 Browse to pick a local folder."
            )

        with browse_col:
            st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
            if st.button("📂 Browse", key="browse_folder_btn", use_container_width=True):
                selected_folder = choose_local_folder()
                if selected_folder:
                    st.session_state["_picked_folder_path"] = selected_folder
                    st.rerun()
                else:
                    st.info("No folder selected.")

        # Prefer whatever the user typed over the picker value
        folder_path_input = (
            st.session_state.get("folder_path_input_typed") or
            st.session_state.get("_picked_folder_path", "")
        ).strip()

        if folder_path_input:
            if not os.path.isdir(folder_path_input):
                st.warning("⚠️ That path doesn't exist or is not a folder on this machine.")
            else:
                try:
                    items = os.listdir(folder_path_input)
                    st.success(f"📂 **{folder_path_input}** — {len(items)} item(s) found")
                except PermissionError:
                    st.error("❌ Permission denied reading that folder.")

        # --- File upload (single or multiple) ---
        uploaded_files = st.file_uploader(
            "📎 Attach file(s) (optional) — useful for analysis, summarisation, reports",
            type=ACCEPTED_EXTENSIONS,
            accept_multiple_files=True,
            key="task_file_upload",
            help="Supported: txt, pdf, csv, xlsx, docx, json, md, log, py"
        )

        if uploaded_files:
            all_parts = []
            for uf in uploaded_files:
                uf_name = uf.name
                ext = uf_name.rsplit(".", 1)[-1].lower()
                try:
                    if ext in ("txt", "md", "log", "py", "json"):
                        text = uf.read().decode("utf-8", errors="replace")
                    elif ext == "csv":
                        import pandas as pd
                        text = pd.read_csv(uf).to_csv(index=False)
                    elif ext in ("xlsx", "xls"):
                        import pandas as pd
                        text = pd.read_excel(uf).to_csv(index=False)
                    elif ext == "pdf":
                        try:
                            import PyPDF2, io
                            reader = PyPDF2.PdfReader(io.BytesIO(uf.read()))
                            text = "\n".join(p.extract_text() or "" for p in reader.pages)
                        except Exception:
                            text = f"[PDF: {uf_name} — install PyPDF2 for text extraction]"
                    elif ext in ("docx", "doc"):
                        try:
                            import docx as _docx, io
                            doc = _docx.Document(io.BytesIO(uf.read()))
                            text = "\n".join(p.text for p in doc.paragraphs)
                        except Exception:
                            text = f"[Word doc: {uf_name} — install python-docx for extraction]"
                    else:
                        text = uf.read().decode("utf-8", errors="replace")

                    all_parts.append(f"=== File: {uf_name} ===\n{text}")

                except Exception as e:
                    st.error(f"❌ Could not read {uf_name}: {e}")

            if all_parts:
                file_content = "\n\n".join(all_parts)
                file_name = ", ".join(uf.name for uf in uploaded_files)
                total_chars = len(file_content)
                label = f"{'3' if len(uploaded_files) > 1 else '1'} file(s): {file_name}"
                st.success(f"📄 **{label}** — {total_chars:,} characters")

    if clear_btn:
        st.session_state.current_result = None
        st.session_state.report_preview = None
        st.session_state["_prefill_task"] = ""
        st.session_state["_clear_task_input"] = True
        st.rerun()

    # Execute task
    if execute_btn and user_input:
        # Clear any stale report preview when the user re-executes
        st.session_state.report_preview = None

        with st.spinner("🔄 Processing your request..."):
            try:
                extra_kwargs = {}

                # Pass folder path if provided and valid
                if folder_path_input and os.path.isdir(folder_path_input):
                    extra_kwargs["directory"] = folder_path_input
                    extra_kwargs["folder_path"] = folder_path_input

                # Pass file content if any files uploaded
                if file_content:
                    extra_kwargs["file_content"] = file_content
                    extra_kwargs["file_name"] = file_name

                # Build enriched task string for LLM routing
                task_parts = [user_input]
                if folder_path_input and os.path.isdir(folder_path_input):
                    task_parts.append(f"[Folder: {folder_path_input}]")
                if file_content:
                    task_parts.append(f"[Attached file(s): {file_name}]\n{file_content[:3000]}")
                task_with_file = "\n\n".join(task_parts)

                _history_input = (
                    user_input
                    + (f" [+folder: {folder_path_input}]" if folder_path_input else "")
                    + (f" [+file: {file_name}]" if file_name else "")
                )

                # ── Report agent: generate content for preview first ──────────
                if mode == "🎯 Direct Agent" and selected_agent == "report":
                    agent = st.session_state.orchestrator.get_agent("report")
                    preview_data = agent.generate_content_only(task_with_file, **extra_kwargs)
                    st.session_state.report_preview = preview_data
                    st.session_state["report_content_edit"] = preview_data["content"]
                    st.session_state.current_result = None
                    st.session_state["_prefill_task"] = ""
                    st.session_state["_clear_task_input"] = True
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": _history_input,
                        "result": {"status": "preview", "topic": preview_data["topic"]},
                    })
                    st.rerun()

                # ── All other agents: normal execution ────────────────────────
                elif mode == "🎯 Direct Agent" and selected_agent:
                    result = st.session_state.orchestrator.execute_agent(
                        selected_agent, task_with_file, **extra_kwargs
                    )
                else:
                    result = st.session_state.orchestrator.process_request(task_with_file)

                st.session_state.current_result = result
                st.session_state["_prefill_task"] = ""
                st.session_state["_clear_task_input"] = True
                st.session_state.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "input": _history_input,
                    "result": result.to_dict()
                })
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Display report preview (before saving) or normal result
    if st.session_state.get("report_preview"):
        render_report_preview()
    elif st.session_state.current_result:
        render_result(st.session_state.current_result, show_steps, show_raw)


def render_email_agent_ui(show_steps, show_raw):
    """Render specialized Email Agent UI"""
    import os
    import re
    from dotenv import load_dotenv
    load_dotenv()
    
    st.markdown("### 📧 Email Composer")
    
    # Get default sender name from env email with validation
    def extract_name_from_email():
        """
        Extract a valid name from email address.
        Returns (name, is_valid) tuple.
        """
        email = os.getenv("EMAIL_ADDRESS", "")
        if not email or "@" not in email:
            return "", False
        
        # Extract part before @
        name_part = email.split("@")[0]
        
        # Clean up: replace common separators with space
        cleaned = re.sub(r'[._-]', ' ', name_part)
        
        # Remove trailing/leading numbers
        cleaned = re.sub(r'^\d+|\d+$', '', cleaned)
        
        # Remove any remaining numbers
        cleaned = re.sub(r'\d+', '', cleaned)
        
        # Strip and normalize spaces
        cleaned = ' '.join(cleaned.split()).strip()
        
        if not cleaned:
            return "", False
        
        # Validation checks
        # 1. Must be at least 2 characters
        if len(cleaned) < 2:
            return "", False
        
        # 2. Must contain only letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', cleaned):
            return "", False
        
        # 3. Each word should be at least 2 chars (to filter out initials only)
        words = cleaned.split()
        valid_words = [w for w in words if len(w) >= 2]
        if not valid_words:
            return "", False
        
        # Format as title case
        formatted_name = ' '.join(w.title() for w in valid_words)
        
        # 4. Final sanity check - name shouldn't be too long (likely garbage)
        if len(formatted_name) > 50:
            return "", False
        
        return formatted_name, True
    
    # Initialize session state for email form
    if "email_generated_body" not in st.session_state:
        st.session_state.email_generated_body = ""
    if "email_body_input" not in st.session_state:
        st.session_state.email_body_input = ""
    if "default_sender_name" not in st.session_state:
        extracted_name, is_valid = extract_name_from_email()
        st.session_state.default_sender_name = extracted_name if is_valid else ""
        st.session_state.name_extracted_valid = is_valid
    
    # Show warning if name couldn't be extracted
    if "name_extracted_valid" in st.session_state and not st.session_state.name_extracted_valid:
        if not st.session_state.get("name_warning_dismissed", False):
            st.info("ℹ️ Could not extract a valid name from your email address. Please enter your name below for the signature.")
    
    # Email form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        to_email = st.text_input(
            "📬 To Email *",
            placeholder="recipient@example.com",
            key="email_to"
        )
    
    with col2:
        cc_email = st.text_input(
            "📋 CC (optional)",
            placeholder="cc@example.com",
            key="email_cc"
        )
    
    subject = st.text_input(
        "📌 Subject *",
        placeholder="Enter email subject...",
        key="email_subject"
    )
    
    # Sender name - required if not auto-extracted
    name_required = not st.session_state.get("name_extracted_valid", False)
    sender_name = st.text_input(
        "👤 Your Name (for signature)" + (" *" if name_required else ""),
        placeholder="Enter your name for signature",
        key="sender_name",
        value=st.session_state.default_sender_name,
        help="Used in 'Best Regards, [Name]' signature" + (" - Required since name couldn't be extracted from email" if name_required else "")
    )
    
    # Generate body button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        generate_btn = st.button("✨ Generate Body", use_container_width=True)
    
    with col2:
        tone = st.selectbox(
            "Tone",
            ["Professional", "Friendly", "Formal", "Casual"],
            key="email_tone"
        )
    
    # Get effective sender name (user input or default from env)
    effective_sender = sender_name.strip() if sender_name else st.session_state.default_sender_name
    
    # Warn if no name available
    if not effective_sender and name_required:
        st.warning("⚠️ Please enter your name for the email signature")
    
    # Auto-generate body when subject is provided and button clicked
    if generate_btn:
        if not subject:
            st.warning("⚠️ Please enter a subject first to generate email body")
        elif not effective_sender:
            st.warning("⚠️ Please enter your name first for the signature")
        else:
            with st.spinner("✨ AI is generating email body..."):
                try:
                    llm = st.session_state.orchestrator.get_llm()
                    
                    prompt = f"""Generate a {tone.lower()} email body for the following subject. 
Do NOT include the subject line, greeting, or signature - only the main content.
Keep it concise, clear, and approximately 3-5 sentences.

Subject: {subject}

Email body content:"""
                    
                    generated_content = llm.generate_text(prompt, temperature=0.7)
                    
                    # Add greeting and signature with sender name
                    greeting = "Dear Sir/Madam,\n\n" if tone in ["Formal", "Professional"] else "Hi,\n\n"
                    signature = f"\n\nBest Regards,\n{effective_sender}"

                    final_body = greeting + generated_content.strip() + signature
                    st.session_state.email_generated_body = final_body
                    st.session_state.email_body_input = final_body
                    st.success("✅ Body generated")
                    
                except Exception as e:
                    st.error(f"❌ Failed to generate: {str(e)}")
    
    # Email body text area
    body = st.text_area(
        "📝 Email Body *",
        height=250,
        placeholder="Click 'Generate Body' to auto-generate based on subject, or type your message here...",
        key="email_body_input"
    )
    
    # Update generated body if user edits
    if body != st.session_state.email_generated_body:
        st.session_state.email_generated_body = body
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        send_btn = st.button("📤 Send Email", type="primary", use_container_width=True)
    
    with col2:
        clear_btn = st.button("🗑️ Clear Form", use_container_width=True)
    
    if clear_btn:
        st.session_state.email_generated_body = ""
        st.session_state.email_body_input = ""
        st.session_state.current_result = None
        st.rerun()
    
    # Send email
    if send_btn:
        # Validation
        if not to_email:
            st.error("❌ Please enter recipient email address")
        elif not subject:
            st.error("❌ Please enter email subject")
        elif not body:
            st.error("❌ Please enter or generate email body")
        else:
            with st.spinner("📤 Sending email..."):
                try:
                    # Build task description
                    task = f"Send email to {to_email} with subject: {subject}"
                    
                    # Execute with body already provided
                    result = st.session_state.orchestrator.execute_agent(
                        "email",
                        task,
                        to_email=to_email,
                        subject=subject,
                        body=body,
                        cc=[cc_email] if cc_email else []
                    )
                    
                    st.session_state.current_result = result
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": f"Email to {to_email}: {subject}",
                        "result": result.to_dict()
                    })
                    
                    if result.success:
                        st.success("✅ Email sent successfully!")
                        st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display result
    if st.session_state.current_result:
        render_result(st.session_state.current_result, show_steps, show_raw)


def render_result(result, show_steps, show_raw):
    """Render the execution result"""
    st.markdown("---")
    st.markdown("### 📊 Result")
    
    # Status indicator
    if result.success:
        st.markdown(f"""
        <div class="success-box">
        ✅ <strong>Success:</strong> {result.message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="error-box">
        ❌ <strong>Failed:</strong> {result.message}
        {f'<br><strong>Error:</strong> {result.error}' if result.error else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Execution info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Execution Time", f"{result.execution_time:.2f}s")
    with col2:
        agent_used = result.data.get("agent_used", "Auto")
        st.metric("Agent Used", agent_used.replace("_", " ").title())
    with col3:
        st.metric("Steps", len(result.steps))
    
    # Main data
    if result.data:
        st.markdown("#### Output Data")
        data = result.data.copy()
        agent_used = data.get("agent_used", "")

        # ── Weather rich display ──────────────────────────────────────────
        if agent_used == "weather" and "current" in data:
            w = data["current"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", f"{w.get('temperature')}°C", f"Feels {w.get('feels_like')}°C")
            c2.metric("Humidity", f"{w.get('humidity')}%")
            c3.metric("Wind Speed", f"{w.get('wind_speed')} m/s")
            st.info(f"**Condition:** {w.get('description')}  |  **Source:** {w.get('source','')}")
            if data.get("forecast"):
                with st.expander("3-Day Forecast", expanded=True):
                    import pandas as pd
                    st.dataframe(pd.DataFrame(data["forecast"]))
            if data.get("advice"):
                with st.expander("AI Advice", expanded=True):
                    st.write(data["advice"])

        # ── News rich display ─────────────────────────────────────────────
        elif agent_used == "news" and "articles" in data:
            if data.get("summary"):
                st.info(data["summary"])
            for i, a in enumerate(data["articles"]):
                with st.expander(f"{i+1}. {a['title']}", expanded=(i == 0)):
                    st.caption(f"{a['source']}  |  {a.get('published_at','')}")
                    if a.get("description"):
                        st.write(a["description"])
                    if a.get("url"):
                        st.markdown(f"[Read more]({a['url']})")

        # ── Train rich display ────────────────────────────────────────────
        elif agent_used == "train" and "trains" in data:
            # Extract origin/destination names (can be dict or string)
            train_origin_raw = data.get('origin', 'Origin')
            train_dest_raw = data.get('destination', 'Destination')
            train_origin_name = train_origin_raw.get('name', train_origin_raw.get('code', str(train_origin_raw))) if isinstance(train_origin_raw, dict) else str(train_origin_raw)
            train_dest_name = train_dest_raw.get('name', train_dest_raw.get('code', str(train_dest_raw))) if isinstance(train_dest_raw, dict) else str(train_dest_raw)
            
            st.info(f"Route: **{train_origin_name} → {train_dest_name}**  |  Date: {data.get('date')}")
            
            # Check if payment flow is active
            if st.session_state.get("show_payment_train") or st.session_state.get("payment_done_train"):
                selected = st.session_state.get("selected_booking_train", {})
                amount = selected.get("fare", 1500)
                render_book_now_button("train", selected, amount)
            else:
                # Train selection
                train_options = []
                for t in data["trains"]:
                    # Get minimum fare
                    min_fare = min(t["fare"].values()) if t["fare"] else 0
                    train_options.append({
                        "label": f"{t['train_no']} – {t['name']} ({t['dep']} → {t['arr']}) - ₹{min_fare}",
                        "train_no": t['train_no'],
                        "name": t['name'],
                        "departure": t['dep'],
                        "arrival": t['arr'],
                        "duration": t['duration'],
                        "classes": t['classes'],
                        "fare": t["fare"]
                    })
                
                for i, t in enumerate(data["trains"]):
                    with st.expander(f"{t['train_no']} – {t['name']}  ({t['dep']} → {t['arr']})", expanded=(i==0)):
                        col_a, col_b, col_c = st.columns([2, 2, 1])
                        col_a.write(f"**Duration:** {t['duration']}")
                        col_a.write(f"**Classes:** {', '.join(t['classes'])}")
                        
                        # Class and fare selection
                        selected_class = col_b.selectbox(
                            "Select Class",
                            options=list(t["fare"].keys()),
                            key=f"train_class_{i}"
                        )
                        fare = t["fare"].get(selected_class, 0)
                        col_b.metric("Fare", f"₹{fare}")
                        
                        # Book button for this train
                        with col_c:
                            st.write("")  # Spacing
                            st.write("")
                            if st.button(f"🎫 Book", key=f"book_train_{i}", use_container_width=True):
                                st.session_state["show_payment_train"] = True
                                st.session_state["selected_booking_train"] = {
                                    "Train": f"{t['train_no']} - {t['name']}",
                                    "From": train_origin_name.upper(),
                                    "To": train_dest_name.upper(),
                                    "Date": data.get('date', ''),
                                    "Departure": t['dep'],
                                    "Arrival": t['arr'],
                                    "Duration": t['duration'],
                                    "Class": selected_class,
                                    "fare": fare
                                }
                                st.rerun()
                
                if data.get("itinerary"):
                    with st.expander("Full Itinerary"):
                        st.code(data["itinerary"])

        # ── Reminder rich display ─────────────────────────────────────────
        elif agent_used == "reminder":
            if data.get("reminder"):
                r = data["reminder"]
                st.success(f"Reminder set: **{r['message']}**")
                st.caption(f"Scheduled for: {r['remind_at'][:16]}")
            elif data.get("reminders"):
                for r in data["reminders"]:
                    st.info(f"[ID {r['id']}] {r['message']} — {r['remind_at'][:16]}")

        # ── Emergency rich display ────────────────────────────────────────
        elif agent_used == "emergency":
            st.error("EMERGENCY DETECTED — Take action immediately!")
            ec_col, hos_col = st.columns(2)
            with ec_col:
                st.markdown("**Emergency Contacts**")
                for c in data.get("contacts", [])[:6]:
                    st.write(f"- **{c['name']}**: `{c['number']}`")
            with hos_col:
                st.markdown("**Nearby Hospitals**")
                for h in data.get("hospitals", []) or ["Search on Google Maps"]:
                    st.write(f"- {h}")
            if data.get("maps_url"):
                st.markdown(f"[Open Maps — Nearest Hospitals]({data['maps_url']})")
            if data.get("guidance"):
                with st.expander("AI First-Response Guidance", expanded=True):
                    st.write(data["guidance"])

        else:
            # ── Flight rich display with booking ──────────────────────────
            if "flights" in data and data["flights"]:
                # Extract origin/destination names (can be dict or string)
                flight_origin_raw = data.get('origin', 'Origin')
                flight_dest_raw = data.get('destination', 'Destination')
                flight_origin_name = flight_origin_raw.get('name', flight_origin_raw.get('code', str(flight_origin_raw))) if isinstance(flight_origin_raw, dict) else str(flight_origin_raw)
                flight_dest_name = flight_dest_raw.get('name', flight_dest_raw.get('code', str(flight_dest_raw))) if isinstance(flight_dest_raw, dict) else str(flight_dest_raw)
                
                st.info(f"Route: **{flight_origin_name} → {flight_dest_name}**  |  Date: {data.get('date', 'N/A')}")
                
                # Check if payment flow is active
                if st.session_state.get("show_payment_flight") or st.session_state.get("payment_done_flight"):
                    selected = st.session_state.get("selected_booking_flight", {})
                    amount = selected.get("fare", 5000)
                    render_book_now_button("flight", selected, amount)
                else:
                    flights = data["flights"]
                    for i, f in enumerate(flights[:8]):
                        flight_name = f.get('airline', f.get('flight', 'Flight'))
                        flight_no = f.get('flight_number', f.get('flight', ''))
                        dep_time = f.get('departure', f.get('departure_time', ''))
                        arr_time = f.get('arrival', f.get('arrival_time', ''))
                        price_raw = f.get('price', f.get('fare', 0))
                        # Clean price - remove existing ₹ if present
                        price = str(price_raw).replace('₹', '').replace(',', '').strip()
                        try:
                            price = int(float(price))
                        except:
                            price = 0
                        
                        with st.expander(f"✈️ {flight_name} {flight_no} ({dep_time} → {arr_time}) - ₹{price:,}", expanded=(i==0)):
                            col_a, col_b, col_c = st.columns([2, 2, 1])
                            col_a.write(f"**Airline:** {flight_name}")
                            col_a.write(f"**Flight:** {flight_no}")
                            col_a.write(f"**Duration:** {f.get('duration', 'N/A')}")
                            
                            col_b.write(f"**Departure:** {dep_time}")
                            col_b.write(f"**Arrival:** {arr_time}")
                            col_b.metric("Price", f"₹{price:,}")
                            
                            with col_c:
                                st.write("")
                                st.write("")
                                if st.button(f"🎫 Book", key=f"book_flight_{i}", use_container_width=True):
                                    st.session_state["show_payment_flight"] = True
                                    st.session_state["selected_booking_flight"] = {
                                        "Flight": f"{flight_name} {flight_no}",
                                        "From": flight_origin_name.upper(),
                                        "To": flight_dest_name.upper(),
                                        "Date": data.get('date', ''),
                                        "Departure": dep_time,
                                        "Arrival": arr_time,
                                        "Duration": f.get('duration', 'N/A'),
                                        "Class": f.get('class', 'Economy'),
                                        "fare": price
                                    }
                                    st.rerun()
                data.pop("flights", None)
            
            # ── Bus rich display with booking ─────────────────────────────
            if "buses" in data and data["buses"]:
                # Extract origin/destination names (can be dict or string)
                origin_raw = data.get('origin', 'Origin')
                dest_raw = data.get('destination', 'Destination')
                origin_name = origin_raw.get('name', origin_raw.get('code', str(origin_raw))) if isinstance(origin_raw, dict) else str(origin_raw)
                dest_name = dest_raw.get('name', dest_raw.get('code', str(dest_raw))) if isinstance(dest_raw, dict) else str(dest_raw)
                
                st.info(f"Route: **{origin_name} → {dest_name}**  |  Date: {data.get('date', 'N/A')}")
                
                # Check if payment flow is active
                if st.session_state.get("show_payment_bus") or st.session_state.get("payment_done_bus"):
                    selected = st.session_state.get("selected_booking_bus", {})
                    amount = selected.get("fare", 500)
                    render_book_now_button("bus", selected, amount)
                else:
                    buses = data["buses"]
                    for i, b in enumerate(buses[:8]):
                        operator = b.get('operator', 'Bus Operator')
                        bus_type = b.get('bus_type', b.get('type', 'AC'))
                        dep_time = b.get('departure_time', b.get('departure', ''))
                        arr_time = b.get('arrival_time', b.get('arrival', ''))
                        price_raw = b.get('price', b.get('fare', 0))
                        # Clean price - remove existing ₹ if present
                        price = str(price_raw).replace('₹', '').replace(',', '').strip()
                        try:
                            price = int(float(price))
                        except:
                            price = 0
                        
                        with st.expander(f"🚌 {operator} - {bus_type} ({dep_time} → {arr_time}) - ₹{price:,}", expanded=(i==0)):
                            col_a, col_b, col_c = st.columns([2, 2, 1])
                            col_a.write(f"**Operator:** {operator}")
                            col_a.write(f"**Bus Type:** {bus_type}")
                            col_a.write(f"**Duration:** {b.get('duration', 'N/A')}")
                            
                            col_b.write(f"**Departure:** {dep_time}")
                            col_b.write(f"**Arrival:** {arr_time}")
                            col_b.metric("Price", f"₹{price:,}")
                            
                            with col_c:
                                st.write("")
                                st.write("")
                                if st.button(f"🎫 Book", key=f"book_bus_{i}", use_container_width=True):
                                    st.session_state["show_payment_bus"] = True
                                    st.session_state["selected_booking_bus"] = {
                                        "Operator": operator,
                                        "Bus Type": bus_type,
                                        "From": origin_name.upper(),
                                        "To": dest_name.upper(),
                                        "Date": data.get('date', ''),
                                        "Departure": dep_time,
                                        "Arrival": arr_time,
                                        "Duration": b.get('duration', 'N/A'),
                                        "Amenities": b.get('amenities', 'N/A'),
                                        "fare": price
                                    }
                                    st.rerun()
                data.pop("buses", None)
            
            # Generic display for all other agents
            display_fields = ["to", "subject", "body", "summary", "generated_reply",
                              "files", "insights", "ai_insights"]
            for field in display_fields:
                if field in data and data[field]:
                    with st.expander(f"{field.replace('_', ' ').title()}", expanded=True):
                        value = data[field]
                        if isinstance(value, list):
                            for item in value[:10]:
                                st.write(f"• {item}")
                        elif isinstance(value, dict):
                            st.json(value)
                        else:
                            st.text_area(field, str(value), height=200, disabled=True)
                    data.pop(field, None)

        remaining = {k: v for k, v in data.items() if v and k not in ["agent_used", "intent_detected"]}
        if remaining and show_raw:
            with st.expander("Additional Data"):
                st.json(remaining)

    render_output_chatbot(result)
    
    # Execution steps
    if show_steps and result.steps:
        st.markdown("#### 🔄 Execution Steps")
        for i, step in enumerate(result.steps):
            status_icon = "✅" if step.get("status") == "success" else "⏳" if step.get("status") == "started" else "❌"
            with st.expander(f"{status_icon} Step {i+1}: {step.get('step', 'Unknown')}"):
                st.write(f"**Status:** {step.get('status', 'Unknown')}")
                if step.get("details"):
                    st.json(step.get("details"))
                st.caption(f"Timestamp: {step.get('timestamp', 'N/A')}")


def render_output_chatbot(result):
    """Chatbot to answer follow-up questions about the current output."""
    st.markdown("#### 💬 Ask About This Output")
    st.caption("Ask questions like: What is the cheapest option? Summarize this result. What should I do next?")

    # Reset chat when the result changes.
    try:
        result_signature = json.dumps(result.to_dict(), sort_keys=True, default=str)
    except Exception:
        result_signature = str(result.message)

    if st.session_state.output_chat_signature != result_signature:
        st.session_state.output_chat_signature = result_signature
        st.session_state.output_chat_history = []

    # Show chat history.
    for msg in st.session_state.output_chat_history:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        with st.chat_message("user" if role == "user" else "assistant"):
            st.write(content)

    user_question = st.chat_input("Ask a question about the output...")

    if user_question:
        st.session_state.output_chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    llm = st.session_state.orchestrator.get_llm()

                    # Keep prompt compact to avoid token bloat.
                    context_payload = {
                        "success": result.success,
                        "message": result.message,
                        "error": result.error,
                        "data": result.data,
                        "steps": result.steps[:8]
                    }

                    prompt = f"""You are an assistant answering ONLY from task output context.
If the answer is not in context, clearly say that and suggest the best next action.
Be concise and practical.

Task Output Context (JSON):
{json.dumps(context_payload, indent=2, default=str)}

User Question:
{user_question}

Answer:"""

                    reply = llm.generate_text(prompt, temperature=0.3)
                    st.write(reply)

                    st.session_state.output_chat_history.append({
                        "role": "assistant",
                        "content": reply
                    })
                except Exception as e:
                    error_text = f"I could not answer from AI right now: {str(e)}"
                    st.error(error_text)
                    st.session_state.output_chat_history.append({
                        "role": "assistant",
                        "content": error_text
                    })


def render_logs_page():
    """Render logs and history page"""
    st.markdown("### 📊 Execution Logs & History")
    
    # History
    st.markdown("#### Recent Executions")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            with st.expander(f"🕐 {item['timestamp'][:19]} - {item['input'][:50]}..."):
                st.write(f"**Input:** {item['input']}")
                st.write(f"**Success:** {'✅ Yes' if item['result']['success'] else '❌ No'}")
                st.write(f"**Message:** {item['result']['message']}")
                if item['result'].get('error'):
                    st.write(f"**Error:** {item['result']['error']}")
    else:
        st.info("No execution history yet. Run some tasks to see history.")
    
    st.markdown("---")
    
    # System logs
    st.markdown("#### System Logs")
    
    try:
        from utils.logger import get_logs
        logs = get_logs(limit=20)
        
        if logs:
            for log in logs:
                status_color = "green" if log.get("status") == "completed" else "red" if log.get("status") == "failed" else "orange"
                st.markdown(f"""
                <div style="padding: 0.5rem; margin: 0.25rem 0; background-color: #f0f0f0; border-radius: 5px; border-left: 4px solid {status_color};">
                <small><strong>{log.get('timestamp', '')[:19]}</strong> | {log.get('agent', '')} | {log.get('status', '')}</small><br>
                {log.get('task', '')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No system logs available.")
    except Exception as e:
        st.warning(f"Could not load system logs: {str(e)}")
    
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.success("History cleared!")
        st.rerun()


def render_agent_info():
    """Render information about available agents"""
    st.markdown("### Available Agents (11 total)")

    agents_info = [
        ("📧 Email Automation", "Generate and send professional emails using AI",
         ["Send via SMTP", "AI-powered content", "Draft creation"]),
        ("📋 Report Generator", "Create formatted reports in TXT and PDF",
         ["Generate reports", "PDF creation", "Professional formatting"]),
        ("✈️ Flight Search", "Search flights and plan itineraries",
         ["Flight search", "Price comparison", "Itinerary creation"]),
        ("🚌 Bus Routes", "Search bus routes and schedules",
         ["Route search", "Schedule info", "Bus types"]),
        ("🚆 Train Tickets", "Search trains, fares and create journey itinerary",
         ["Train search", "Fare comparison", "IRCTC-style itinerary"]),
        ("📁 File Organizer", "Organize and manage files in a directory",
         ["Organize by type", "Batch rename", "File search"]),
        ("🌐 Browser / Web", "Open websites, play YouTube, search web",
         ["YouTube play/search", "Gmail search", "Maps directions"]),
        ("🌤️ Weather", "Current weather with AI advice",
         ["Current conditions", "3-day forecast", "AI tips (umbrella etc.)"]),
        ("📰 News", "Fetch headlines and AI summaries",
         ["Top headlines by topic", "AI news summary", "Search any topic"]),
        ("⏰ Reminders", "Set reminders with desktop notifications",
         ["Set time-based reminders", "List/delete reminders", "Auto notification"]),
        ("🚨 Emergency", "Smart emergency assistant",
         ["Emergency contacts", "Nearest hospitals", "AI first-aid guidance"]),
    ]

    cols = st.columns(3)
    for i, (name, desc, capabilities) in enumerate(agents_info):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="agent-card">
            <strong>{name}</strong><br>
            <small>{desc}</small><br>
            <small style="color: #666;">• {'<br>• '.join(capabilities)}</small>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Check authentication - show login page if not logged in
    if not require_auth():
        return
    
    initialize_session_state()
    
    # Show user info and logout button in sidebar
    show_user_info_sidebar()
    
    mode, selected_agent, show_steps, show_raw = render_sidebar()
    
    if mode == "📊 Logs & History":
        render_logs_page()
    elif mode == "⚙️ Profile Settings":
        render_profile_settings()
    else:
        render_main_interface(mode, selected_agent, show_steps, show_raw)
        
        st.markdown("---")
        
        with st.expander("ℹ️ About Available Agents", expanded=False):
            render_agent_info()


if __name__ == "__main__":
    main()
