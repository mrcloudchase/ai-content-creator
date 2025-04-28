import streamlit as st
from typing import Dict, Any
from utils.content_display import format_token_usage, display_model_info, display_token_info
import json
import uuid
import html
import re
import os

def render_content(content_data: Dict[str, Any]):
    """
    Render the content viewer component for the final step of the workflow
    
    This component displays the generated content for each selected content type
    in tabs and provides download options.
    
    Args:
        content_data: The response data from the content generate API
    """
    st.subheader("Generated Content")
    
    # Add explanatory text
    st.markdown(
        """
        The system has generated content for your selected content types.
        Use the tabs below to view each content type and download the markdown files.
        """
    )
    
    # Safely check for generated_content key
    if "generated_content" not in content_data:
        st.error("No 'generated_content' found in the API response. Please check the API logs.")
        return
    
    # Create a list of tab names based on content types
    tab_names = [
        f"{content['type'].title()}"
        for content in content_data["generated_content"]
    ]
    
    # Add CSS for the copy button and content container
    st.markdown("""
    <style>
    .copy-button {
        float: right;
        padding: 5px 10px;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        font-size: 12px;
        color: #1e3a8a;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 10px;
    }
    .copy-button:hover {
        background-color: #e0e2e6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .copy-button:active {
        background-color: #d0d2d6;
    }
    .copy-success {
        background-color: #dcfce7 !important;
        border-color: #86efac !important;
        color: #166534 !important;
    }
    .markdown-container {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 15px;
        margin-top: 10px;
        background-color: #f9fafb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stMarkdown {
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for each content type
    if tab_names:
        tabs = st.tabs(tab_names)
        
        # Populate each tab with its content
        for i, tab in enumerate(tabs):
            with tab:
                try:
                    content = content_data["generated_content"][i]
                    
                    # Display content title
                    if "title" in content:
                        st.markdown(f"# {content['title']}")
                    else:
                        st.markdown(f"# {content['type'].title()} Content")
                    
                    # Add a download button
                    if "content" in content:
                        # Clean the markdown content: Remove leading markdown code block indicators
                        raw_markdown = content["content"]
                        # Clean any ```markdown or ``` at the beginning of the content
                        cleaned_markdown = re.sub(r'^```markdown\s*\n|^```\s*\n', '', raw_markdown)
                        # Also clean any trailing ``` if present
                        cleaned_markdown = re.sub(r'\n```\s*$', '', cleaned_markdown)
                        
                        st.download_button(
                            label="📥 Download as Markdown",
                            data=cleaned_markdown,
                            file_name=f"{content['type']}_{content.get('title', content['type']).replace(' ', '_')}.md",
                            mime="text/markdown",
                        )
                        
                        # Show content preview with copy functionality
                        st.markdown("## Content Preview")
                        
                        # Add a standard Streamlit copy button
                        copy_button = st.button("Copy to clipboard", key=f"copy_{content['type']}")
                        if copy_button:
                            st.toast("Content copied to clipboard!", icon="✅")
                            # Use st.components.v1.html to add JavaScript for clipboard copy
                            st.components.v1.html(
                                f"""
                                <script>
                                    navigator.clipboard.writeText({json.dumps(cleaned_markdown)});
                                </script>
                                """,
                                height=0
                            )
                        
                        # Display the content in a clean container using code formatting to preserve whitespace
                        st.code(cleaned_markdown, language="markdown")
                        
                    else:
                        st.error("Content field missing in the response")
                        st.json(content)
                except Exception as e:
                    st.error(f"Error rendering content tab: {str(e)}")
    else:
        st.warning("No content was generated. Please go back and select content types.")
    
    # Add buttons for navigation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Content Types", use_container_width=True):
            # Go back to content types step
            st.session_state.step = 'content_types'
            st.rerun()
    
    with col2:
        if st.button("🔄 Start New Content Creation", type="primary", use_container_width=True):
            # Clear all data from previous steps
            for key in ['intent_data', 'content_types_data', 'generated_content']:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Go back to the first step
            st.session_state.step = 'upload'
            st.rerun()