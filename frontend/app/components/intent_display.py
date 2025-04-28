import streamlit as st
from typing import Dict, Any
from utils.content_display import format_token_usage, display_model_info, display_token_info, truncate_text

def render_intent(intent_data: Dict[str, Any]):
    """
    Render the intent display component for the second step of the workflow
    
    This component displays the generated customer intent statement and allows
    users to proceed to content type selection.
    
    Args:
        intent_data: The response data from the customer intent API
    """
    st.subheader("Customer Intent")
    
    # Display the intent statement prominently
    st.info(intent_data["intent"])
    
    # Create columns for details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Model Information")
        display_model_info(
            model=intent_data["model"],
            model_family=intent_data["model_family"],
            capabilities=intent_data["capabilities"]
        )
    
    with col2:
        st.markdown("### Token Usage")
        display_token_info(
            token_limit=intent_data["token_limit"],
            token_count=intent_data["token_count"],
            remaining_tokens=intent_data["remaining_tokens"]
        )
        st.markdown(format_token_usage(intent_data["usage"]))
    
    # Show a sample of the text used to generate the intent
    with st.expander("Text Used for Intent Generation"):
        st.markdown(truncate_text(intent_data["text_used"], 1000))
        st.caption("Showing up to first 1000 characters of the text")
    
    # Add buttons for navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Upload", use_container_width=True):
            # Clear intent data
            if "intent_data" in st.session_state:
                del st.session_state.intent_data
            
            # Go back to upload step
            st.session_state.step = 'upload'
            st.rerun()
    
    with col2:
        if st.button("Suggest Content Types ➡️", type="primary", use_container_width=True):
            try:
                # Get API client from session state
                api_client = st.session_state.api_client
                
                # Call the API with a spinner to show progress
                with st.spinner("Analyzing intent and suggesting content types..."):
                    response = api_client.get_content_types(
                        intent=intent_data["intent"],
                        text_used=intent_data["text_used"]
                    )
                
                # Store the response in session state
                st.session_state.content_types_data = response
                
                # Move to the next step
                st.session_state.step = 'content_types'
                
                # Force page refresh to update UI
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to suggest content types: {str(e)}")
                st.markdown(
                    """
                    Please check that:
                    - The API service is running and accessible
                    - The intent statement is valid
                    """
                ) 