import streamlit as st
import os
from utils.api_client import ContentCreatorClient
from components.file_upload import render_file_upload
from components.intent_display import render_intent
from components.content_type_selector import render_content_types
from components.content_viewer import render_content

# Configure the page
st.set_page_config(
    page_title="AI Content Creator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the CSS file
    css_file = os.path.join(script_dir, "assets", "styles.css")
    
    # Check if the file exists
    if os.path.isfile(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback for when the file doesn't exist (e.g. in development)
        st.markdown(
            """
            <style>
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )

# Initialize session state for multi-step workflow
def init_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 'upload'
    
    # Initialize API client if not already initialized
    if 'api_client' not in st.session_state:
        # Get the API URL from Streamlit secrets or environment variables
        api_url = os.getenv("API_URL", "http://localhost:8000")
        
        # Create the API client
        st.session_state.api_client = ContentCreatorClient(base_url=api_url)

def main():
    # Load custom CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Application header
    st.title("AI Content Creator")
    
    # Display API connection info
    api_client = st.session_state.api_client
    st.caption(f"Connected to API: {api_client.base_url}")
    
    # Divider
    st.markdown("---")
    
    # Progress indicator for current step
    steps = ["Document Upload", "Customer Intent", "Content Types", "Generated Content"]
    current_step_idx = ["upload", "intent", "content_types", "content"].index(st.session_state.step)
    
    # Calculate the progress for each step
    progress_values = [0.0] * 4
    for i in range(4):
        if i < current_step_idx:  # Past steps are complete
            progress_values[i] = 1.0
        elif i == current_step_idx:  # Current step is active
            progress_values[i] = 0.5
        # Future steps remain at 0.0
    
    # Show the progress bar
    cols = st.columns(4)
    for i, (col, step_name, progress) in enumerate(zip(cols, steps, progress_values)):
        with col:
            st.progress(progress)
            if progress > 0.0:
                if i == current_step_idx:
                    st.markdown(f"**{step_name}**")
                else:
                    st.markdown(step_name)
            else:
                st.markdown(f"<span style='color:#AAAAAA'>{step_name}</span>", unsafe_allow_html=True)
    
    # Divider
    st.markdown("---")
    
    # Render the appropriate component based on the current step
    if st.session_state.step == 'upload':
        render_file_upload()
    
    elif st.session_state.step == 'intent':
        # Check if we have intent data
        if 'intent_data' not in st.session_state:
            st.error("No intent data found. Please upload a document first.")
            st.session_state.step = 'upload'
            st.rerun()
        else:
            render_intent(st.session_state.intent_data)
    
    elif st.session_state.step == 'content_types':
        # Check if we have content types data
        if 'content_types_data' not in st.session_state:
            st.error("No content types data found. Please generate intent first.")
            st.session_state.step = 'intent'
            st.rerun()
        else:
            render_content_types(st.session_state.content_types_data)
    
    elif st.session_state.step == 'content':
        # Check if we have generated content data
        if 'generated_content' not in st.session_state:
            st.error("No generated content found. Please select content types first.")
            st.session_state.step = 'content_types'
            st.rerun()
        else:
            render_content(st.session_state.generated_content)
    
    # Footer
    st.markdown("---")
    st.caption("AI Content Creator © 2023")

if __name__ == "__main__":
    main() 