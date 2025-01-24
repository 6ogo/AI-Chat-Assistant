import os
import streamlit as st
from groq import Groq
from datetime import datetime
import PyPDF2
from docx import Document
import requests
from bs4 import BeautifulSoup

# Initialize Groq client
client = Groq(api_key=st.secrets.GROQ_API_KEY)

# Model configurations
MODELS = {
    "mixtral-8x7b-32768": {
        "name": "Mixtral-8x7b",
        "description": "High quality model with 32k context window",
        "context_window": 32768,
        "supports_files": True
    },
    "llama2-70b-4096": {
        "name": "LLaMA2-70b",
        "description": "Meta's powerful 70B parameter model",
        "context_window": 4096,
        "supports_files": False
    },
    "gemma-7b-it": {
        "name": "Gemma-7B",
        "description": "Google's lightweight model for basic tasks",
        "context_window": 8192,
        "supports_files": True
    }
}

ROLES = {
    "coding": {
        "name": "Coding Genius AI",
        "prompt": "You are an expert software engineer. Provide clean, efficient code with explanations.",
        "parameters": ["programming_language"]
    },
    "data_science": {
        "name": "Data Scientist AI",
        "prompt": "You are a senior data scientist. Provide statistical insights and ML solutions.",
        "parameters": []
    },
    "marketing": {
        "name": "Marketing Professional AI",
        "prompt": "You are a digital marketing expert. Provide creative campaigns and strategies.",
        "parameters": []
    }
}

STYLES = {
    "professional": "Use formal business language",
    "casual": "Use friendly, conversational tone",
    "technical": "Include detailed technical terms",
    "concise": "Be brief and to the point"
}

def extract_text_from_file(file):
    """Extract text from uploaded files"""
    text = ""
    if file.type == "text/plain":
        text = file.read().decode()
    elif file.type == "application/pdf":
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def get_web_content(url):
    """Fetch and extract main content from a webpage"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return ' '.join([p.get_text() for p in soup.find_all('p')])
    except Exception as e:
        st.error(f"Error fetching URL: {e}")
        return ""

def initialize_chat():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        st.session_state.model = "mixtral-8x7b-32768"
    if "context" not in st.session_state:
        st.session_state.context = ""

def render_sidebar():
    """Render the sidebar controls"""
    with st.sidebar:
        st.header("Configuration")
        
        # Model selection
        model_key = st.selectbox(
            "Select Model",
            options=list(MODELS.keys()),
            format_func=lambda x: MODELS[x]["name"],
            help="Choose the AI model to use for generation"
        )
        st.caption(MODELS[model_key]["description"])
        
        # Role selection
        role_key = st.selectbox(
            "Select AI Role",
            options=list(ROLES.keys()),
            format_func=lambda x: ROLES[x]["name"],
            help="Choose the specialized role for the AI"
        )
        
        # Role parameters
        role_params = {}
        for param in ROLES[role_key]["parameters"]:
            if param == "programming_language":
                role_params[param] = st.text_input("Programming Language", "Python")
        
        # Style selection
        style = st.selectbox(
            "Response Style",
            options=list(STYLES.keys()),
            format_func=lambda x: STYLES[x],
            index=0
        )
        
        # File upload
        if MODELS[model_key]["supports_files"]:
            uploaded_files = st.file_uploader(
                "Upload context files (TXT, PDF, DOCX)",
                type=["txt", "pdf", "docx"],
                accept_multiple_files=True
            )
            
            urls = st.text_input("Enter URLs (comma-separated)", help="Provide websites for context")
            
            if st.button("Process Context"):
                context_text = ""
                
                # Process files
                for file in uploaded_files:
                    context_text += extract_text_from_file(file) + "\n\n"
                
                # Process URLs
                if urls:
                    for url in urls.split(','):
                        context_text += get_web_content(url.strip()) + "\n\n"
                
                st.session_state.context = context_text[:MODELS[model_key]["context_window"]]
                st.success(f"Processed {len(context_text)} characters of context")
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.context = ""
            st.rerun()

        return {
            "model": model_key,
            "role": ROLES[role_key],
            "style": style,
            "role_params": role_params
        }

def main():
    st.set_page_config(page_title="Groq AI Chat", layout="wide")
    initialize_chat()
    config = render_sidebar()

    # Main chat interface
    st.title("Groq AI Chat Assistant")
    st.subheader(f"{config['role']['name']} ({MODELS[config['model']]['name']})")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "timestamp" in message:
                st.caption(f"{message['timestamp']}")

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        # Construct system prompt
        system_prompt = f"{config['role']['prompt']} {STYLES[config['style']]}"
        if config['role_params']:
            system_prompt += "\n" + "\n".join([f"{k}: {v}" for k, v in config['role_params'].items()])
        if st.session_state.context:
            system_prompt += f"\n\nContext:\n{st.session_state.context}"

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                for response in client.chat.completions.create(
                    model=config["model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]} 
                          for m in st.session_state.messages]
                    ],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.content or ""
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
            except Exception as e:
                st.error(f"API Error: {str(e)}")

if __name__ == "__main__":
    main()