import streamlit as st
import time
from config import Config

# Try to import Gemini
try:
    from src.gemini_agent import GeminiHRAssistant
    gemini_available = True
except ImportError as e:
    gemini_available = False
    print(f"Import error: {e}")

# Set page configuration
st.set_page_config(
    page_title="HR Assistant Agent 🤖",
    page_icon="🤖",
    layout="wide"
)

# Local HR knowledge base as fallback
HR_KNOWLEDGE = {
    "sick_leave": "**Sick Leave Policy**\n\n• 12 days per year\n• Medical certificate required for leaves beyond 3 days\n• Can be used for personal illness or medical appointments",
    "dress_code": "**Dress Code Policy**\n\n• Business casual (Monday-Thursday)\n• Casual wear (Friday)\n• Formal attire for client meetings",
    "health_insurance": "**Health Insurance**\n\n• Covers employee + family\n• ₹5 lakhs coverage per year\n• Includes hospitalization and OPD",
    "working_hours": "**Working Hours**\n\n• 9:00 AM to 6:00 PM\n• Monday to Friday\n• 1 hour lunch break",
    "maternity_leave": "**Maternity Leave**\n\n• 26 weeks fully paid\n• Apply 8 weeks before due date\n• Medical documentation required",
    "paternity_leave": "**Paternity Leave**\n\n• 15 days fully paid\n• Use within 6 months of childbirth",
    "annual_leave": "**Annual Leave**\n\n• 15 days per year (<5 years service)\n• 20 days (5+ years service)\n• Can carry forward 30 days",
    "probation": "**Probation Period**\n\n• 6 months for new hires\n• Performance reviews at 3 and 6 months",
    "resignation": "**Resignation Process**\n\n• 30 days notice period\n• Submit resignation to manager\n• Exit interview required"
}

def get_local_response(question):
    """Fallback to local responses if Gemini fails"""
    question_lower = question.lower()
    
    if "sick" in question_lower:
        return HR_KNOWLEDGE["sick_leave"]
    elif "dress" in question_lower:
        return HR_KNOWLEDGE["dress_code"]
    elif "health" in question_lower or "insurance" in question_lower:
        return HR_KNOWLEDGE["health_insurance"]
    elif "work" in question_lower and "hour" in question_lower:
        return HR_KNOWLEDGE["working_hours"]
    elif "maternity" in question_lower:
        return HR_KNOWLEDGE["maternity_leave"]
    elif "paternity" in question_lower:
        return HR_KNOWLEDGE["paternity_leave"]
    elif "annual" in question_lower or "vacation" in question_lower:
        return HR_KNOWLEDGE["annual_leave"]
    elif "probation" in question_lower:
        return HR_KNOWLEDGE["probation"]
    elif "resign" in question_lower:
        return HR_KNOWLEDGE["resignation"]
    else:
        return "I can help with HR policies including leaves, benefits, and company procedures. Please ask a specific question!"

def initialize_session_state():
    """Initialize session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "hr_assistant" not in st.session_state:
        try:
            if Config.validate_config() and gemini_available:
                st.session_state.hr_assistant = GeminiHRAssistant()
                st.session_state.ai_enabled = True
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "✅ **Google Gemini Connected!** Hello! I'm your AI HR Assistant. How can I help you today?"
                })
            else:
                st.session_state.ai_enabled = False
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "ℹ️ **Local Mode** Hello! I'm your HR Assistant. Ask me about HR policies (using local knowledge base)."
                })
        except Exception as e:
            st.session_state.ai_enabled = False
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ **Local Mode** Hello! Gemini connection failed. Using local knowledge. Error: {str(e)}"
            })
    
    # ADDED: Track last question to prevent duplicates
    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

def get_ai_response(question):
    """Get response from Gemini or fallback to local"""
    if st.session_state.ai_enabled:
        try:
            return st.session_state.hr_assistant.get_response(question, st.session_state.messages)
        except Exception as e:
            return f"Gemini Error: {str(e)}\n\n{get_local_response(question)}"
    else:
        return get_local_response(question)

def main():
    # Initialize session state
    initialize_session_state()
    
    # Title
    st.title("🤖 HR Assistant Agent")
    
    # Status
    if st.session_state.get('ai_enabled', False):
        st.success("✅ **Google Gemini AI Active**")
    else:
        st.warning("ℹ️ **Local Mode Active**")
        st.info("💡 Add Google API key to .env for AI features")
    
    # Quick Questions
    st.subheader("🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏥 Sick Leave", key="sick_btn"):
            process_question("How many sick leaves do I get?")
        if st.button("👔 Dress Code", key="dress_btn"):
            process_question("What is the dress code policy?")
    
    with col2:
        if st.button("💊 Health Insurance", key="insurance_btn"):
            process_question("Tell me about health insurance benefits")
        if st.button("🕒 Working Hours", key="hours_btn"):
            process_question("What are the working hours?")
    
    with col3:
        if st.button("🤰 Maternity Leave", key="maternity_btn"):
            process_question("What is the maternity leave policy?")
        if st.button("📝 Resignation", key="resign_btn"):
            process_question("How do I resign from the company?")
    
    st.markdown("---")
    
    # Display Chat
    st.subheader("💬 Conversation")
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**HR Assistant:** {message['content']}")
        st.markdown("---")
    
    # Chat Input - FIXED: Only this part changed
    user_input = st.chat_input("Ask your HR question...")
    
    if user_input and user_input != st.session_state.last_question:
        st.session_state.last_question = user_input
        process_question(user_input)
        st.rerun()
    
    # Clear Chat
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_question = ""  # ADDED: Reset last question
        initialize_session_state()
        st.rerun()

def process_question(question):
    """Process a question and add to chat"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Get response
    with st.spinner("🤔 Thinking..."):
        response = get_ai_response(question)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()