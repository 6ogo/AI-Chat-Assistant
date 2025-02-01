# AI Chat Assistant
A Streamlit-based ChatGPT-like interface powered by Groq's lightning-fast inference API, featuring model selection, role-based personas, and context-aware conversations.

## Features
- **Multiple AI Models**:
  - Mixtral-8x7b (32k context)
  - LLaMA2-70b (4k context)
  - Gemma-7B (8k context)
  
- **Role-Based Personas**:
  - Coding Genius AI (with language selection)
  - Data Scientist AI
  - Marketing Professional AI

- **Customization**:
  - Response styles (Professional, Casual, Technical, Concise)
  - System prompt engineering
  - Context management

- **File & Web Context**:
  - Upload TXT, PDF, DOCX files
  - Extract content from URLs
  - Context-aware conversations

- **Advanced Features**:
  - Real-time streaming responses
  - Chat history with timestamps
  - Model capability-based restrictions
  - Session state management

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/6ogo/AI-Chat-Assistant.git
   cd groq-ai-chat
   ```
   
2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
    ```
3. **Configure API Key:**
Create .streamlit/secrets.toml
Add your Groq API key:
    ```toml
    GROQ_API_KEY = "your-api-key-here"
    ```

## Usage
1. Start the application:

   ```bash
    streamlit run app.py
    ```
2. Configure Settings (Sidebar):
- Select AI Model with context window information
- Choose AI Role (Coding/Data/Marketing)
- Pick Response Style
- Upload files (for supported models)
- Enter URLs for web context

3. Process Context:
- Click "Process Context" after uploading files/URLs
- Context will be automatically truncated to model limits

4. Chat Interface:
- Type your message in the chat input
- Responses stream in real-time
- Use "Clear Chat" to reset conversation

## Configuration
Modify these sections in app.py to customize:

1. Models:

    ```python
    MODELS = {
        "model-id": {
            "name": "Display Name",
            "description": "Model description",
            "context_window": 32768,
            "supports_files": True
        }
    }
    ```
2. Roles:

    ```python
    ROLES = {
        "role-key": {
            "name": "Role Name",
            "prompt": "System prompt",
            "parameters": ["custom_params"]
        }
    }
    ```
3. Styles:

    ```python
    STYLES = {
        "style-key": "Style description"
    }
    ```
    
## Prerequisites
Python 3.7+
Groq API key (from Groq Cloud)
Supported browsers: Chrome, Firefox, Edge

## License
MIT License - see LICENSE file for details

Note: This project is not affiliated with Groq Technologies. Use of Groq's API is subject to their terms of service. Always monitor your API usage and costs.

