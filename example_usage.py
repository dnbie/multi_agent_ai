"""
Example Usage Script
Demonstrates the capabilities of the Agent X Task Automation System
Run this script to test the system before using the UI
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import AgentOrchestrator
from config import DATA_DIR

def print_result(result):
    """Pretty print an AgentResult"""
    print("\n" + "=" * 60)
    print(f"Success: {'✅' if result.success else '❌'} {result.success}")
    print(f"Message: {result.message}")
    if result.error:
        print(f"Error: {result.error}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print("-" * 60)
    
    if result.data:
        print("Data:")
        for key, value in result.data.items():
            if key not in ['all_flights', 'formatted_text', 'content']:
                print(f"  {key}: {str(value)[:200]}...")
    print("=" * 60 + "\n")

def main():
    """Run example demonstrations"""
    print("\n" + "=" * 60)
    print("AGENT X - TASK AUTOMATION SYSTEM - DEMO")
    print("=" * 60 + "\n")
    
    # Initialize orchestrator
    print("Initializing system...")
    orchestrator = AgentOrchestrator()
    print("System initialized with agents:", list(orchestrator.agents.keys()))
    print()
    
    # Example 1: File Processing
    print("\n[DEMO 1] File Processing - Summarization")
    print("-" * 40)
    sample_file = str(DATA_DIR / "sample_email.txt")
    result = orchestrator.process_request(f"Summarize the file {sample_file}")
    print_result(result)
    input("Press Enter to continue...")
    
    # Example 2: Data Analysis
    print("\n[DEMO 2] Data Analysis")
    print("-" * 40)
    csv_file = str(DATA_DIR / "sample_data.csv")
    result = orchestrator.process_request(f"Analyze the data in {csv_file}")
    print_result(result)
    input("Press Enter to continue...")
    
    # Example 3: Flight Search
    print("\n[DEMO 3] Flight Search")
    print("-" * 40)
    result = orchestrator.process_request("Search flights from DEL to BOM on 2026-03-25")
    print_result(result)
    input("Press Enter to continue...")
    
    # Example 4: Bus Route Search
    print("\n[DEMO 4] Bus Route Search")
    print("-" * 40)
    result = orchestrator.process_request("Find buses from Delhi to Jaipur")
    print_result(result)
    input("Press Enter to continue...")
    
    # Example 5: Report Generation
    print("\n[DEMO 5] Report Generation")
    print("-" * 40)
    result = orchestrator.process_request("Generate a report about the benefits of AI in education")
    print_result(result)
    input("Press Enter to continue...")
    
    # Example 6: Email (Demo mode - won't actually send)
    print("\n[DEMO 6] Email Automation (Demo Mode)")
    print("-" * 40)
    result = orchestrator.process_request("Send an email to test@example.com about the project meeting tomorrow")
    print_result(result)
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nTo use the full system with UI, run:")
    print("  streamlit run app.py")
    print("\nTo configure email and LLM APIs, edit .env file")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed requirements: pip install -r requirements.txt")
        print("2. Configured .env file with API keys")
        print("3. Run from the project directory")
