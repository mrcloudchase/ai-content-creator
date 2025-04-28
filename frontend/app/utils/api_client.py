import requests
import streamlit as st
from typing import Dict, Any, List
import io

class ContentCreatorClient:
    """Client for the AI Content Creator API"""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API (e.g., 'http://api:80')
        """
        self.base_url = base_url
        # Remove trailing slash if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    def generate_intent(self, file) -> Dict[str, Any]:
        """
        Generate customer intent from a document file
        
        Args:
            file: Streamlit UploadedFile object
        
        Returns:
            API response containing the generated intent
        
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/api/v1/customer-intent"
        
        try:
            # Prepare the file for multipart/form-data upload
            files = {
                'file': (file.name, file.getvalue(), file.type)
            }
            
            # Make the POST request
            response = requests.post(endpoint, files=files)
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            raise Exception(f"Failed to generate intent: {str(e)}")
    
    def get_content_types(self, intent: str, text_used: str) -> Dict[str, Any]:
        """
        Get recommended content types based on intent and text
        
        Args:
            intent: Customer intent statement
            text_used: Text extracted from document
        
        Returns:
            API response containing recommended content types
        
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/api/v1/content-types"
        
        try:
            # Prepare JSON payload
            data = {
                "intent": intent,
                "text_used": text_used
            }
            
            # Make the POST request
            response = requests.post(endpoint, json=data)
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            raise Exception(f"Failed to get content types: {str(e)}")
    
    def generate_content(self, intent: str, text_used: str, content_types: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate content based on intent, text, and selected content types
        
        Args:
            intent: Customer intent statement
            text_used: Text extracted from document
            content_types: List of selected content types and titles
        
        Returns:
            API response containing generated content
        
        Raises:
            Exception: If the API request fails
        """
        endpoint = f"{self.base_url}/api/v1/content-generate"
        
        try:
            # Prepare JSON payload
            data = {
                "intent": intent,
                "text_used": text_used,
                "content_types": content_types
            }
            
            # Make the POST request
            response = requests.post(endpoint, json=data)
            
            # Raise exception for HTTP errors
            response.raise_for_status()
            
            # Return the JSON response
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}") 