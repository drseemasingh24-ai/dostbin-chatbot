#!/usr/bin/env python3
"""
Dostbin Groq Llama 3.1 8B Chatbot - Streamlit Cloud Version
Ultra-cheap AI chatbot using Groq's free tier
Cost: $0.05 input / $0.08 output per 1M tokens
"""

import streamlit as st
import json
from groq import Groq
from datetime import datetime
from collections import defaultdict

# --- Configuration ---
MODEL = "llama-3.1-8b-instant"

# --- Secrets Retrieval (Streamlit Cloud) ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("⚠️ GROQ_API_KEY not found in Streamlit Secrets. Please configure it in app settings.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Page configuration
st.set_page_config(
    page_title="Dostbin AI Assistant",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chat styling
st.markdown("""
<style>
    .stApp { background-color: #f5f7f9; }
    .chat-message {
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #28a745;
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: white;
        color: #333;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
    /* Hide Streamlit branding for embed */
    iframe[title="streamlit_chat_message"] { display: none; }
</style>
""", unsafe_allow_html=True)

# Load knowledge base from file (bundled with app)
@st.cache_data
def load_knowledge_base():
    try:
        with open('knowledge_base.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

kb = load_knowledge_base()

# Build YouTube videos section
def get_youtube_section():
    if not kb or 'collections' not in kb or 'youtube_videos' not in kb['collections']:
        return ""
    
    videos = kb['collections']['youtube_videos']
    youtube_section = "\n\nAVAILABLE YOUTUBE VIDEOS:\n"
    
    videos_by_category = defaultdict(list)
    for video in videos:
        videos_by_category[video['category']].append(video)
    
    for category, vids in videos_by_category.items():
        youtube_section += f"\n{category}:\n"
        for vid in vids:
            summary = vid.get('content_summary', '')[:150]
            youtube_section += f"- {vid['title']}\n  URL: {vid['video_url']}\n  Summary: {summary}...\n"
    
    return youtube_section

# Create system prompt with knowledge base
def get_system_prompt():
    if not kb:
        return "You are a helpful assistant for Dostbin Solutions."

    # Extract official product info from knowledge base
    official_info = ""
    products = kb.get('collections', {}).get('products', [])
    for doc in products:
        if doc.get('id') == 'AUTHORITATIVE-PRODUCT-INFO-001':
            official_info = doc.get('description', '')
            break

    return f"""You are a helpful customer support assistant for Dostbin Solutions, India's first patented automatic compost bin company.

CRITICAL INSTRUCTIONS:
- Keep responses SHORT and CONCISE (2-3 sentences max for simple questions)
- Be friendly and professional
- Only answer questions about Dostbin products and services
- If asked about unrelated topics, politely redirect to Dostbin
- When relevant, suggest YouTube videos to help users learn more (don't force links on every response)
- Include YouTube links when users ask about: products, variants, composting process, setup, demos, or how things work

⚠️ IMPORTANT: For pricing, delivery time, and product specifications, ONLY use the information below. Ignore any conflicting information from other sources.

OFFICIAL DOSTBIN INFORMATION (USE THIS ONLY):

{official_info}

Contact:
- Email: info@dostbin.com
- Phone: +918105868094, +919740374780
- Website: dostbin.com
- YouTube: https://www.youtube.com/@dostbin

How it works:
1. Add kitchen waste daily with cocopeat powder
2. Bin automatically/manually mixes and aerates (depending on model)
3. Get compost in 20-30 days (two phases of 7-10 days each)
4. Leachate can be diluted 1:15 for liquid fertilizer

Features:
- Odor-free operation with odor absorber
- Shred and digest buttons for easy operation (Premium model)
- Two-phase composting system
- Leachate collection for liquid fertilizer
- Made in India, Patented technology
- All variants: Up to 5 Kg/day waste capacity

COMPOSTING GUIDE VIDEOS:
- Composting basics: https://www.youtube.com/watch?v=b7jsXoghslQ
- Quick composting guide: https://www.youtube.com/shorts/yJSMnd9g2yo
{get_youtube_section()}

When users ask about tutorials, demos, setup, or how things work, ALWAYS provide specific YouTube video links.
Answer questions naturally and conversationally."""

SYSTEM_PROMPT = get_system_prompt()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = {'input': 0, 'output': 0}

# Header
st.title("🌱 Dostbin AI Assistant")
st.caption("Powered by Groq Llama 3.1 8B - Ultra-fast AI Support")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about Dostbin..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend([{"role": m["role"], "content": m["content"]}
                     for m in st.session_state.messages])

    # Get response from Groq
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            assistant_message = response.choices[0].message.content
            st.markdown(assistant_message)
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About Dostbin")
    st.markdown("""
    **India's First Patented Automatic Compost Bin**

    🌿 Convert kitchen waste to compost at home
    📱 IoT & Mobile App control (Premium)
    🚚 Free delivery PAN India

    **Contact:**
    - 📧 info@dostbin.com
    - 📞 +918105868094
    - 🌐 [dostbin.com](https://dostbin.com)
    """)

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

