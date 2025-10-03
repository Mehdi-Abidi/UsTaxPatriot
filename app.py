import os
import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from pinecone import Pinecone
from datetime import datetime
import speech_recognition as sr
import tempfile
import hashlib
import html
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="USTax - AI Tax Consultation Assistant",
    page_icon="🏛️",
    layout="wide"
)

INDEX_NAME = "ustax"  # Updated Pinecone index name
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Deep Navy Blue Color Palette - Sophisticated & Professional
PRIMARY_COLOR = "#00072D"      # Deep navy blue
SECONDARY_COLOR = "#001952"    # Lighter navy
ACCENT_COLOR = "#003d82"       # Medium blue
LIGHT_BG = "#f0f4f8"          # Very light blue-grey
CARD_BG = "#ffffff"           # White
TEXT_COLOR = "#00072D"        # Deep navy text
BORDER_COLOR = "#d4e1f0"      # Light blue border
HIGHLIGHT_COLOR = "#b8d4ee"   # Subtle blue highlight

def get_theme_styles():
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, #f0f4f8 0%, #e3ecf5 25%, #d4e1f0 50%, #e3ecf5 75%, #f0f4f8 100%);
        font-family: 'Inter', sans-serif;
        color: {TEXT_COLOR};
    }}
    
    /* US Government Deep Navy Header */
    .government-header {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 244, 248, 0.9) 100%);
        border: 3px solid {PRIMARY_COLOR}30;
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        margin-top: 1rem;
        box-shadow: 
            0 20px 40px {PRIMARY_COLOR}15,
            inset 0 1px 0 rgba(255, 255, 255, 0.9),
            0 0 40px {PRIMARY_COLOR}10;
        backdrop-filter: blur(15px);
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: subtleGlow 3s infinite ease-in-out;
    }}
    
    @keyframes subtleGlow {{
        0%, 100% {{ box-shadow: 0 20px 40px {PRIMARY_COLOR}15, 0 0 40px {PRIMARY_COLOR}10; }}
        50% {{ box-shadow: 0 20px 40px {PRIMARY_COLOR}20, 0 0 60px {PRIMARY_COLOR}15; }}
    }}
    
    .government-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, {PRIMARY_COLOR}08, {ACCENT_COLOR}08, transparent);
        animation: shimmer 8s infinite linear;
    }}
    
    @keyframes shimmer {{
        0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
        100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
    }}
    
    .government-title {{
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 50%, {ACCENT_COLOR} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 2;
        filter: drop-shadow(0 2px 4px {PRIMARY_COLOR}20);
    }}
    
    .government-subtitle {{
        font-size: 1.3rem;
        color: {PRIMARY_COLOR};
        font-weight: 600;
        margin-bottom: 1rem;
        position: relative;
        z-index: 2;
    }}
    
    .government-description {{
        color: {SECONDARY_COLOR};
        font-size: 1rem;
        margin-top: 1rem;
        position: relative;
        z-index: 2;
        line-height: 1.6;
    }}
    
    /* Status cards with charcoal grey theme */
    .status-card {{
        background: linear-gradient(145deg, {CARD_BG} 0%, {LIGHT_BG} 100%);
        border: 2px solid {BORDER_COLOR};
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .status-card:hover {{
        transform: translateY(-8px);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.1),
            0 0 20px rgba(0, 0, 0, 0.05);
        border-color: {PRIMARY_COLOR}60;
    }}
    
    /* Voice Input Styling */
    .voice-input-container {{
        background: linear-gradient(145deg, {CARD_BG} 0%, {LIGHT_BG} 100%);
        border: 2px solid {BORDER_COLOR};
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }}
    
    /* Chat interface - Charcoal Grey */
    .chat-container {{
        background: linear-gradient(145deg, {CARD_BG} 0%, {LIGHT_BG} 100%);
        border: 2px solid {BORDER_COLOR};
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        min-height: 500px;
        max-height: 700px;
        overflow-y: auto;
        position: relative;
    }}
    
    /* Message bubbles */
    .user-message {{
        background: linear-gradient(135deg, #e3ecf5 0%, #d4e1f0 50%, #e3ecf5 100%);
        color: {TEXT_COLOR};
        padding: 1.2rem 1.8rem;
        border-radius: 20px 20px 8px 20px;
        margin: 1rem 0 1rem 15%;
        box-shadow: 
            0 6px 20px {PRIMARY_COLOR}08,
            0 2px 4px {PRIMARY_COLOR}05;
        border: 2px solid {BORDER_COLOR};
        position: relative;
        word-wrap: break-word;
        animation: slideInRight 0.3s ease-out;
        line-height: 1.6;
    }}
    
    .assistant-message {{
        background: linear-gradient(145deg, {CARD_BG} 0%, #f0f4f8 100%);
        color: {TEXT_COLOR};
        padding: 1.2rem 1.8rem;
        border-radius: 20px 20px 20px 8px;
        margin: 1rem 15% 1rem 0;
        border-left: 5px solid {PRIMARY_COLOR};
        box-shadow: 
            0 6px 20px {PRIMARY_COLOR}10,
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border: 2px solid {BORDER_COLOR};
        position: relative;
        word-wrap: break-word;
        animation: slideInLeft 0.3s ease-out;
        line-height: 1.6;
    }}
    
    /* Input section */
    .input-section {{
        background: linear-gradient(145deg, {CARD_BG} 0%, {LIGHT_BG} 100%);
        border: 3px solid {BORDER_COLOR};
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 2rem;
        box-shadow: 
            0 12px 32px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        position: relative;
    }}
    
    /* Centered button container */
    .centered-button-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 1rem;
    }}
    
    /* Textarea styling */
    .stTextArea textarea {{
        background: {CARD_BG} !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        color: {TEXT_COLOR} !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        min-height: 120px !important;
        resize: vertical !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
        line-height: 1.5 !important;
    }}
    
    .stTextArea textarea:focus {{
        border-color: {PRIMARY_COLOR} !important;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.08) !important;
        outline: none !important;
        min-height: 150px !important;
    }}
    
    .stTextArea textarea::placeholder {{
        color: {ACCENT_COLOR} !important;
        font-style: italic !important;
    }}
    
    /* Button styling - Charcoal Grey */
    .stButton > button {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%) !important;
        color: #ffffff !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, {SECONDARY_COLOR} 0%, {PRIMARY_COLOR} 100%) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 
            0 6px 20px rgba(0, 0, 0, 0.2),
            0 0 15px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Audio input styling */
    .stAudioInput > div > div {{
        background: {CARD_BG} !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        color: {TEXT_COLOR} !important;
    }}
    
    .stAudioInput label {{
        color: {PRIMARY_COLOR} !important;
        font-weight: 600 !important;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: {CARD_BG} !important;
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {PRIMARY_COLOR} !important;
        font-weight: 600 !important;
    }}
    
    .streamlit-expanderContent {{
        background: {CARD_BG} !important;
        border: 2px solid {BORDER_COLOR} !important;
        color: {TEXT_COLOR} !important;
        padding: 1rem !important;
    }}
    
    .streamlit-expanderContent pre {{
        color: {TEXT_COLOR} !important;
        background: {LIGHT_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }}
    
    /* Voice icon styling */
    .voice-indicator {{
        color: {PRIMARY_COLOR} !important;
    }}
    
    /* Hide Streamlit elements */
    .stDeployButton {{ display: none; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    
    /* Common animations */
    @keyframes slideInRight {{
        from {{ transform: translateX(50px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    @keyframes slideInLeft {{
        from {{ transform: translateX(-50px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {LIGHT_BG};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {ACCENT_COLOR}, {PRIMARY_COLOR});
        border-radius: 5px;
        border: 1px solid {BORDER_COLOR};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {PRIMARY_COLOR}, {SECONDARY_COLOR});
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .government-title {{ font-size: 2rem; }}
        .user-message, .assistant-message {{ 
            margin-left: 5%; 
            margin-right: 5%; 
        }}
    }}
        /* Voice recorder styling - clean white with navy icons */
    .stAudioInput {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 1.2rem auto !important;
        padding: 1rem !important;
        background: #ffffff !important;  /* pure white */
        border: 2px solid {BORDER_COLOR} !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08) !important;
    }}

    .stAudioInput label {{
        font-weight: 600 !important;
        color: {PRIMARY_COLOR} !important;  /* deep navy */
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }}

    /* Inner recorder controls */
    .stAudioInput > div > div {{
        background: #ffffff !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        color: {PRIMARY_COLOR} !important;
    }}

    /* Mic and playback icons */
    .stAudioInput svg {{
        fill: {PRIMARY_COLOR} !important;
        stroke: {PRIMARY_COLOR} !important;
    }}


</style>
"""

# Apply theme styles
st.markdown(get_theme_styles(), unsafe_allow_html=True)

# ------------------ TEXT FORMATTING FUNCTION ------------------
def format_text_content(text):
    """
    Format text content to handle HTML characters and improve readability
    """
    if not text:
        return ""
    
    # Escape HTML characters to prevent formatting issues
    formatted_text = html.escape(text)
    
    # Add proper line breaks for better readability
    formatted_text = formatted_text.replace('\n', '<br>')
    
    # Handle common formatting patterns
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_text)
    formatted_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_text)
    
    return formatted_text

# ------------------ SOURCE EXTRACTION FUNCTION ------------------
def extract_clean_sources(source_documents):
    """
    Extract clean source information showing only page numbers and document names
    """
    if not source_documents:
        return ""
    
    sources = []
    for doc in source_documents:
        try:
            # Extract metadata
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            # Get document name/source
            doc_name = metadata.get('source', metadata.get('title', 'Unknown Document'))
            
            # Extract page number if available
            page = metadata.get('page', metadata.get('page_number', None))
            
            # Clean document name (remove file extensions and paths)
            if isinstance(doc_name, str):
                doc_name = os.path.basename(doc_name)
                doc_name = os.path.splitext(doc_name)[0]
            
            # Format source entry
            if page is not None:
                source_entry = f"{doc_name} (Page {page})"
            else:
                source_entry = doc_name
                
            if source_entry not in sources:
                sources.append(source_entry)
                
        except Exception as e:
            continue
    
    return "\n".join(f"• {source}" for source in sources[:5])  # Limit to 5 sources

# ------------------ PINECONE DB LOADER ------------------
@st.cache_resource
def load_vector_store():
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Ensure index exists
        indexes = [idx["name"] for idx in pc.list_indexes()]
        if INDEX_NAME not in indexes:
            st.error(f"❌ Pinecone index '{INDEX_NAME}' not found. Please create it with 3072 dimensions.")
            return None

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=OPENAI_API_KEY
        )

        db = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
        return db
    except Exception as e:
        st.error(f"Failed to connect to Pinecone: {str(e)}")
        return None

# ------------------ VOICE TRANSCRIPTION ------------------
def transcribe_audio(uploaded_file):
    try:
        recognizer = sr.Recognizer()
        audio_bytes = uploaded_file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio_data)
            except sr.RequestError:
                try:
                    return recognizer.recognize_sphinx(audio_data)
                except sr.RequestError:
                    return "Speech recognition unavailable."
            except sr.UnknownValueError:
                return "Could not understand audio."

    except Exception as e:
        return f"Error processing audio: {str(e)}"
    finally:
        try:
            os.unlink(temp_audio_path)
        except:
            pass

# ------------------ PROMPT TEMPLATE ------------------
PROMPT_TEMPLATE = """
You are USTax, an expert AI tax assistant powered by OpenAI's GPT-4, specializing in United States tax regulations. Use the context below to provide accurate, professional tax advice.

Context:
{context}

Question:
{question}

Please provide:
- Direct answer based on US tax code
- Tax implications and compliance requirements
- Practical recommendations for taxpayers
- Required disclaimers for legal compliance

Response:
"""

def get_prompt(template):
    return PromptTemplate(template=template, input_variables=["context", "question"])

# ------------------ OPENAI MODEL ------------------
@st.cache_resource
def get_openai_model():
    try:
        return ChatOpenAI(
            model_name="gpt-4",
            temperature=0.3,
            max_tokens=1024,
            openai_api_key=OPENAI_API_KEY
        )
    except Exception as e:
        st.error(f"Failed to init GPT-4: {str(e)}")
        return None

# ------------------ DISPLAY CHAT ------------------
def display_chat_message(role, content):
    if role == "user":
        voice_indicator = '<span class="voice-indicator">🎤</span>' if content.startswith("[Voice Input]") else "👤"
        display_content = content.replace("[Voice Input] ", "") if content.startswith("[Voice Input]") else content
        
        # Format the content properly
        formatted_content = format_text_content(display_content)
        
        st.markdown(f"""
        <div class="user-message">
            <strong>{voice_indicator} Taxpayer:</strong><br>
            {formatted_content}
        </div>
        """, unsafe_allow_html=True)
    else:
        # Split content and sources
        parts = content.split("\n\nSource Docs:\n")
        main_answer = parts[0]
        raw_sources = parts[1] if len(parts) > 1 else ""
        
        # Format the main answer properly
        formatted_answer = format_text_content(main_answer)
        
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🏛️ USTax AI (GPT-4):</strong><br>
            {formatted_answer}
        </div>
        """, unsafe_allow_html=True)
        
        # Show clean sources if available
        if raw_sources:
            try:
                # Parse the source documents from string representation
                import ast
                source_docs = ast.literal_eval(raw_sources) if raw_sources.startswith('[') else []
                clean_sources = extract_clean_sources(source_docs)
                
                if clean_sources:
                    with st.expander("📋 View IRS Documentation Sources", expanded=False):
                        st.markdown(f"""
                        <div style="color: {TEXT_COLOR};">
                            {clean_sources.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
            except:
                # Fallback for malformed source data
                with st.expander("📋 View IRS Documentation Sources", expanded=False):
                    st.markdown(f"""
                    <div style="color: {TEXT_COLOR};">
                        Sources available - see original query for details.
                    </div>
                    """, unsafe_allow_html=True)

# ------------------ QUERY PROCESSING ------------------
def process_query(query, is_voice=False):
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: {LIGHT_BG}; border-radius: 12px; border: 2px solid {BORDER_COLOR}; box-shadow: 0 4px 12px {PRIMARY_COLOR}08;">
        <span style="color: {PRIMARY_COLOR}; font-weight: 600;">🏛️ Analyzing IRS regulations...</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        db = load_vector_store()
        if db is None:
            st.error("❌ Pinecone DB unavailable.")
            return

        retriever = db.as_retriever(search_kwargs={"k": 6})
        llm = get_openai_model()
        if llm is None:
            st.error("❌ GPT-4 unavailable.")
            return

        prompt = get_prompt(PROMPT_TEMPLATE)

        retrieval_qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        response = retrieval_qa.invoke({"query": query})
        result = response["result"].strip()
        source_documents = response["source_documents"]

        if result.startswith("Response:"):
            result = result[9:].strip()
        if is_voice:
            result = f"🎤 *Processed from voice input* \n\n{result}"

        full_response = result + "\n\nSource Docs:\n" + str(source_documents)
        st.session_state.messages.append({'role': 'assistant', 'content': full_response})
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ------------------ MAIN APP ------------------
def main():
    st.markdown(f"""
    <div class="government-header">
        <div class="government-title">🏛️ US TaxPatriot</div>
        <div class="government-subtitle">US Government Tax Consultation Assistant</div>
        <div class="government-description">
            🇺🇸 IRS Compliance • Tax Code Analysis
            <br>Voice-enabled for accessible tax consultation
            <br>Professional guidance for individuals and businesses
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🏛️ USTax AI (GPT-4):</strong><br>
            Welcome to USTax! I'm your AI tax assistant specializing in United States tax regulations. 
            I can help you with IRS compliance, tax planning strategies, deductions, credits, and general tax questions. 
            How can I assist you with your US tax matters today?
        </div>
        """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.messages:
        display_chat_message(message['role'], message['content'])

    st.markdown("###    Ask Your Questions Related To Tax")

    # Voice input section
    voice_col1, voice_col2, voice_col3 = st.columns([1, 2, 1])
    with voice_col2:
        if "last_audio_hash" not in st.session_state:
            st.session_state.last_audio_hash = None

        audio_bytes = st.audio_input("", key="voice_input")
        if audio_bytes:
            audio_data = audio_bytes.read()
            audio_bytes.seek(0)
            current_audio_hash = hashlib.md5(audio_data).hexdigest()

            if current_audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = current_audio_hash
                with st.spinner("🎤 Processing your voice input..."):
                    text = transcribe_audio(audio_bytes)
                    if text and not text.startswith(("Error", "Could not", "Speech recognition")):
                        st.success(f"🎤 Transcribed: {text}")
                        st.session_state.messages.append({'role': 'user', 'content': f"[Voice Input] {text}"})
                        process_query(text, is_voice=True)
                    else:
                        st.error(f"❌ {text}")
        else:
            st.session_state.last_audio_hash = None

    # Text input section
    user_query = st.text_area(
        label="Tax query input",
        placeholder="Type your US tax question here... (e.g., What are the standard deductions for 2024? How do I report cryptocurrency? What business expenses can I deduct?)",
        key="tax_query",
        label_visibility="hidden"
    )
    
    # Center the submit button
    st.markdown('<div class="centered-button-container">', unsafe_allow_html=True)
    
    # Create columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        submit = st.button("🏛️ Get Expert Tax Advice ", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

    if submit and user_query.strip():
        st.session_state.messages.append({'role': 'user', 'content': user_query})
        process_query(user_query)

st.markdown(f"""
<style>
.st-emotion-cache-1maeoc0 {{
    background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}}

.st-emotion-cache-1maeoc0 svg {{
    color: #ffffff !important;
}}

.st-emotion-cache-1maeoc0:hover {{
    background: linear-gradient(135deg, {SECONDARY_COLOR} 0%, {PRIMARY_COLOR} 100%) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
}}
</style>
""", unsafe_allow_html=True)