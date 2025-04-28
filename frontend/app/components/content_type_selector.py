import streamlit as st
from typing import Dict, Any, List
from utils.content_display import format_token_usage, display_model_info, display_token_info

def render_content_types(content_types_data: Dict[str, Any]):
    """
    Render the content type selector component for the third step of the workflow
    
    This component displays recommended content types with confidence scores,
    allows the user to select which content types to generate, and proceeds
    to content generation.
    
    Args:
        content_types_data: The response data from the content types API
    """
    st.subheader("Recommended Content Types")
    
    # Add explanatory text
    st.markdown(
        """
        The system has analyzed your document and recommended the following content types
        based on the Diátaxis framework. Select the content types you want to generate.
        """
    )
    
    # Initialize list for selected content types
    selected_types = []
    
    # Container for content type selection
    with st.container():
        # Add some styling
        st.markdown(
            """
            <style>
            .content-type-card {
                border: 1px solid #EEEEEE;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 10px;
                background-color: #FAFAFA;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        # Display each content type as a card with selection checkbox
        for content_type in content_types_data["selected_types"]:
            # Determine if this content type should be selected by default
            # based on confidence score (select if confidence > 0.7)
            default_selected = content_type["confidence"] > 0.7
            
            # Create a card-like container for this content type
            st.markdown(
                f"""
                <div class="content-type-card">
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Content type details
            col1, col2 = st.columns([1, 6])
            
            with col1:
                # Checkbox for selection
                selected = st.checkbox(
                    label="",
                    value=default_selected,
                    key=f"checkbox_{content_type['type']}"
                )
            
            with col2:
                # Type name and confidence score
                st.markdown(f"### {content_type['type'].title()}")
                st.markdown(f"**Confidence score:** {content_type['confidence']:.2f}")
                
                # Reasoning
                st.markdown("**Reasoning:**")
                st.markdown(content_type['reasoning'])
            
            # Get intent from session state instead of content_types_data
            intent_text = st.session_state.intent_data["intent"]
            
            # Add to selected types if checked
            if selected:
                selected_types.append({
                    "type": content_type["type"],
                    "title": f"{content_type['type'].title()} for {intent_text.split(',')[0]}"
                })
    
    # Show model information and token usage in an expander
    with st.expander("Model Information and Token Usage"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Model Information")
            display_model_info(
                model=content_types_data["model"],
                model_family=content_types_data["model_family"],
                capabilities=content_types_data["capabilities"]
            )
        
        with col2:
            st.markdown("### Token Usage")
            display_token_info(
                token_limit=content_types_data["token_limit"],
                token_count=content_types_data["token_count"],
                remaining_tokens=content_types_data["remaining_tokens"]
            )
            st.markdown(format_token_usage(content_types_data["usage"]))
    
    # Add warning if no content types are selected
    if not selected_types and st.button("Generate Content", type="primary", use_container_width=True):
        st.warning("Please select at least one content type to generate.")
        return
    
    # Add buttons for navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Intent", use_container_width=True):
            # Go back to intent step
            st.session_state.step = 'intent'
            st.rerun()
    
    with col2:
        if selected_types and st.button("Generate Content ➡️", type="primary", use_container_width=True):
            try:
                # Get the intent from the previous step
                intent = st.session_state.intent_data["intent"]
                text_used = st.session_state.intent_data["text_used"]
                
                # Get API client from session state
                api_client = st.session_state.api_client
                
                # Call the API with a spinner to show progress
                with st.spinner("Generating content for selected types..."):
                    response = api_client.generate_content(
                        intent=intent,
                        text_used=text_used,
                        content_types=selected_types
                    )
                
                # Store the response in session state
                st.session_state.generated_content = response
                
                # Move to the next step
                st.session_state.step = 'content'
                
                # Force page refresh to update UI
                st.rerun()
                
            except Exception as e:
                st.error(f"Failed to generate content: {str(e)}")
                st.markdown(
                    """
                    Please check that:
                    - The API service is running and accessible
                    - The selected content types are valid
                    """
                ) 