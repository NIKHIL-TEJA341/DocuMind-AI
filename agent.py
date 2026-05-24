import os
import streamlit as st
from agno.agent import Agent
from agno.models.groq import Groq

def generate_documentation(code_dict: dict) -> str:
    """Generate documentation from a dictionary of file paths and contents."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
            
    if not api_key:
        return "## Error Generating Documentation\n\nGroq API Key is missing. Please add it to your Streamlit App Secrets as instructed."
    
    # Format the codebase context
    code_context = []
    for filepath, content in code_dict.items():
        if filepath == 'error.txt':
            continue
        # Truncate extremely large single files if needed (for safety)
        if len(content) > 50000:
            content = content[:50000] + "\n...[TRUNCATED]"
            
        code_context.append(f"--- FILE: {filepath} ---\n```\n{content}\n```\n")
    
    context_str = "\n".join(code_context)
    
    if not context_str.strip():
        return "No valid source code found to document. Please check your upload or repository."
    
    system_prompt = (
        "You are DocuMind AI, an expert technical documentation generator. "
        "Analyze the codebase context provided and generate professional, clean documentation in Markdown format. "
        "Your output must include:\n"
        "1. Project Overview\n"
        "2. Installation/Setup Guide (infer from the files if possible)\n"
        "3. Usage Instructions\n"
        "4. Feature List\n"
        "5. Detailed Function/Class/API Documentation for core modules\n\n"
        "Do NOT include conversational filler. Just output the Markdown documentation directly."
    )
    
    try:
        # Initialize Groq model using Agno
        os.environ["GROQ_API_KEY"] = api_key
        groq_model = Groq(id="llama-3.3-70b-versatile", api_key=api_key)
        
        agent = Agent(
            model=groq_model,
            description=system_prompt,
            markdown=True,
        )
        
        # Enforce strict character limits for Groq free tiers (~12000 TPM limit)
        # 25,000 characters is roughly 6,000 tokens, safely below the 12k TPM limit
        if len(context_str) > 25000:
            context_str = context_str[:25000] + "\n\n...[CODEBASE TRUNCATED DUE TO GROQ FREE TIER LIMITS]"
            
        # We pass the codebase context as the user message
        prompt = "Please generate the comprehensive documentation for the following codebase:\n\n" + context_str
        
        response = agent.run(prompt)
        return response.content
        
    except Exception as e:
        return f"## Error Generating Documentation\n\nAn error occurred while connecting to the AI: {str(e)}"
