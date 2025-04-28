import streamlit as st
from utils.api_client import ContentCreatorClient

def render_file_upload():
    """
    Render the file upload component for the first step of the workflow
    
    This component allows users to upload a document file and generate customer intent.
    """
    st.subheader("Upload a Document")
    
    # Add some explanatory text
    st.markdown(
        """
        Upload a document file to generate a customer intent statement. The system will analyze 
        the document content and identify the key user needs and goals.
        
        **Supported file types:** .docx, .md, .txt
        """
    )
    
    # Create the file uploader
    uploaded_file = st.file_uploader(
        label="Choose a file",
        type=["docx", "md", "txt"],
        help="Upload a document in .docx, .md, or .txt format"
    )
    
    # Show a placeholder when no file is uploaded
    if not uploaded_file:
        # Display a placeholder container with dotted border
        with st.container():
            st.markdown(
                """
                <div style="border:2px dashed #CCCCCC; border-radius:5px; padding:20px; text-align:center;">
                <p>No file uploaded yet. Please upload a document to continue.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        return
    
    # Show file information when a file is uploaded
    st.success(f"File uploaded: **{uploaded_file.name}**")
    
    # File size in KB
    file_size = uploaded_file.size / 1024
    st.markdown(f"**File size:** {file_size:.1f} KB")
    
    # Add a button to generate intent
    if st.button("Generate Intent", type="primary", use_container_width=True):
        try:
            # Get API client from session state
            api_client = st.session_state.api_client
            
            # Call the API with a spinner to show progress
            with st.spinner("Analyzing document and generating customer intent..."):
                response = api_client.generate_intent(uploaded_file)
            
            # Store the response in session state
            st.session_state.intent_data = response
            
            # Move to the next step
            st.session_state.step = 'intent'
            
            # Force page refresh to update UI
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to generate intent: {str(e)}")
            st.markdown(
                """
                Please check that:
                - The API service is running and accessible
                - The document is properly formatted
                - The document is not too large (under 4MB)
                """
            ) 