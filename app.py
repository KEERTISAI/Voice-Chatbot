import streamlit as st
from openai import OpenAI
import speech_recognition as sr
import pyttsx3
import threading
import time
from io import BytesIO
import base64

# Set page config
st.set_page_config(
    page_title="Voice Chat Bot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'listening' not in st.session_state:
    st.session_state.listening = False


# Initialize text-to-speech engine
@st.cache_resource
def init_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level
    return engine


# Initialize speech recognition
@st.cache_resource
def init_speech_recognition():
    return sr.Recognizer()


def speak_text(text):
    """Convert text to speech"""
    try:
        engine = init_tts()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        st.error(f"Speech synthesis error: {e}")


def listen_for_speech():
    """Listen for speech input"""
    recognizer = init_speech_recognition()
    microphone = sr.Microphone()
    
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        
        with microphone as source:
            st.info("🎤 Listening... Speak now!")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        text = recognizer.recognize_google(audio)
        return text
    except sr.WaitTimeoutError:
        return "Timeout - no speech detected"
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Speech recognition error: {e}"


def get_chatgpt_response(prompt, api_key):
    """Get response from ChatGPT API"""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Ram's persona - hardcoded system prompt
        system_message = """You are Keerti Sai Naidu, an engineer deeply passionate about Generative AI with hands-on experience in building intelligent, real-world solutions using LLMs and vision-language models. Currently working as an Associate Software Engineer (GenAI) at Iota Analytics, you have developed a range of impactful AI applications including a dual-version Law Firm RAG chatbot using Streamlit (OpenAI and Phi 3.5), with features like PDF uploads, page-referenced answers, streaming output, and local inference via Ollama for offline use. You also built a multi-agent chatbot platform that lets users interact with role-based assistants (e.g., Math Tutor, Science Helper) across models like OpenAI, Phi, and Qwen. Other key contributions include an Excel clustering and header suggestion system using DBSCAN and FastAPI, and image classification pipelines using both traditional ML and vision-language models (Pix2Struct, Pixtral), including platform porting to Windows. You hold a B.E. in Artificial Intelligence and Machine Learning (CGPA 8.38) from New Horizon College of Engineering, and have interned with Nokia as a Technical Writer—honing your documentation skills—and with NeoAstra on real-time object detection and dataset annotation. Your core skills include Python, SQL, PyTorch, TensorFlow, Scikit-learn, OpenCV, FastAPI, Hugging Face, Ollama, and Streamlit. You are multilingual (English, Hindi, Telugu, Kannada) and certified via NPTEL in both Machine Learning and Deep Learning. You are known for your curiosity, rapid learning, and ability to build GenAI solutions that are human-centric, resource-efficient, and production-ready. You thrive under tight deadlines through lean development strategies, and enjoy solving ambiguous technical problems. In the next five years, you aim to become a technical leader in the GenAI space, mentoring others and contributing to open-source AI tooling. You are most excited about the future of small-footprint LLMs, multi-agent systems, and vision-language models that can drive intuitive user experiences and responsible AI applications."""
        
        # Prepare conversation history
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        for msg in st.session_state.messages[-5:]:  # Last 5 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"


# Main app
def main():
    st.title("🤖 Voice Chat Bot")
    st.markdown("*Hi, I am Keerti Sai, Your questions, my context — zero fluff.!*")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        st.markdown("---")
        
        # Voice settings
        st.subheader("🔊 Voice Settings")
        use_voice_input = st.checkbox("Enable Voice Input", value=True)
        use_voice_output = st.checkbox("Enable Voice Output", value=False)
        
        st.markdown("---")
        
        # Sample questions for practice
        st.subheader("💡 Ice Breaker ")
        sample_questions = [
            "Tell me about yourself",
            "What are your strengths?",
            "Where do you see yourself in 5 years?",
            "Why should we hire you?",
            "What's your biggest weakness?",
            "Describe a challenging project you worked on",
            "How do you handle tight deadlines?",
            "What technologies are you most excited about?"
        ]
        
        selected_question = st.selectbox("Quick Start Questions:", [""] + sample_questions)
        
        if st.button("Use Selected Question") and selected_question:
            st.session_state.current_input = selected_question
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Show Ram's persona info
        st.info("🎭 Can’t wait to chat with you — let’s dive in!")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
    
    # Input section
    st.markdown("---")
    
    # Text input
    text_input = st.text_input(
        "Type your message:", 
        key="text_input",
        value=st.session_state.get("current_input", "")
    )
    
    # Input buttons
    col_send, col_voice = st.columns([1, 1])
    
    with col_send:
        send_button = st.button("📤 Send", use_container_width=True)
    
    with col_voice:
        if use_voice_input:
            voice_button = st.button("🎤 Voice Input", use_container_width=True)
        else:
            voice_button = False
    
    # Handle text input
    if send_button and text_input and api_key:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": text_input})
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = get_chatgpt_response(text_input, api_key)
        
        # Add AI response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Text-to-speech if enabled
        if use_voice_output:
            with st.spinner("Speaking..."):
                speak_text(response)
        
        # Clear input
        st.session_state.current_input = ""
        st.rerun()
    
    # Handle voice input
    if voice_button and api_key:
        with st.spinner("Listening for your voice..."):
            voice_text = listen_for_speech()
        
        if voice_text and not voice_text.startswith(("Timeout", "Could not", "Speech recognition error")):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": voice_text})
            
            # Get AI response
            with st.spinner("Processing..."):
                response = get_chatgpt_response(voice_text, api_key)
            
            # Add AI response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Text-to-speech if enabled
            if use_voice_output:
                with st.spinner("Speaking response..."):
                    speak_text(response)
            
            st.rerun()
        else:
            st.error(f"Voice input failed: {voice_text}")
    
    # Instructions
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start chatting!")
    
    with st.expander("📋 How to Use"):
        st.markdown("""
        1. **Get API Key**: Sign up at OpenAI and get your API key
        2. **Enter API Key**: Paste it in the sidebar
        3. **Start Chatting**: Type or use voice input
        4. **Practice**: Use sample questions for interview practice
        
        **Voice Features:**
        - Enable voice input to speak your questions
        - Enable voice output to hear responses
        - Great for practicing speaking skills!
        
        **Tips:**
        - Practice common interview questions
        - Work on your storytelling skills
        - Build confidence in verbal communication
        """)


if __name__ == "__main__":
    main()