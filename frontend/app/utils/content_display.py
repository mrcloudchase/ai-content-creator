import streamlit as st
from typing import Dict, Any

def format_token_usage(usage: Dict[str, int]) -> str:
    """
    Format token usage data into a human-readable string
    
    Args:
        usage: Token usage dictionary with prompt_tokens, completion_tokens, total_tokens
        
    Returns:
        Formatted string representation of token usage
    """
    return (
        f"**Prompt tokens:** {usage.get('prompt_tokens', 0):,}\n"
        f"**Completion tokens:** {usage.get('completion_tokens', 0):,}\n"
        f"**Total tokens:** {usage.get('total_tokens', 0):,}"
    )

def display_model_info(model: str, model_family: str, capabilities: Dict[str, bool]) -> None:
    """
    Display model information in a formatted way
    
    Args:
        model: Model name
        model_family: Model family name
        capabilities: Model capabilities dictionary
    """
    st.markdown(f"**Model:** {model}")
    st.markdown(f"**Model family:** {model_family}")
    
    # Display capabilities
    st.markdown("**Capabilities:**")
    for capability, enabled in capabilities.items():
        icon = "✅" if enabled else "❌"
        st.markdown(f"- {icon} {capability.replace('_', ' ').title()}")

def display_token_info(token_limit: int, token_count: int, remaining_tokens: int) -> None:
    """
    Display token information with a progress bar
    
    Args:
        token_limit: Maximum tokens allowed
        token_count: Current token count
        remaining_tokens: Remaining tokens
    """
    # Calculate percentage used
    percentage_used = (token_count / token_limit) * 100 if token_limit > 0 else 0
    
    # Display token counts
    st.markdown(f"**Token limit:** {token_limit:,}")
    st.markdown(f"**Token count:** {token_count:,}")
    st.markdown(f"**Remaining tokens:** {remaining_tokens:,}")
    
    # Show progress bar
    st.progress(min(percentage_used / 100, 1.0))
    
    # Add warning if tokens are running out
    if percentage_used > 75:
        st.warning(f"Using {percentage_used:.1f}% of available tokens")
    
def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text and add ellipsis if too long
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..." 