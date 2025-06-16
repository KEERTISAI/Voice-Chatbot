# 🤖 Voice ChatBot with User defined Persona

A Streamlit-based voice chatbot that simulates conversations with predefined persona. Perfect for interview practice and learning conversational AI.


## 🎯 Features

- **Voice Input/Output**: Speak to the bot and hear responses
- **AI Persona**: Chat with a predefined persona
- **Interview Practice**: Pre-loaded with common interview questions
- **Real-time Chat**: Powered by OpenAI GPT-3.5-turbo
- **Clean UI**: Professional Streamlit interface


## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI**: OpenAI GPT-3.5-turbo API
- **Voice**: SpeechRecognition + pyttsx3
- **Language**: Python 3.8+



## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (You will have to enter the Openai api key in the streamlit UI)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/KEERTISAI/Voice-Chatbot


2.Create and activate a virtual environment
  On Windows:
           python -m venv voice_env
           voice_env\Scripts\activate
  
  On macOS/Linux:
           python3 -m venv voice_env
           source voice_env/bin/activate    

# Install dependencies
pip install -r requirements.txt



# Run the application
streamlit run app.py
