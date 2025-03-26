import docx
from typing import Dict, List, Any, Optional
import io
import os
import re
import sys

class DocxParserError(Exception):
    """Custom exception for document parsing errors"""
    pass

class DocxParser:
    """Service for parsing .docx documents"""
    
    @staticmethod
    def parse_document(file_content: bytes) -> Dict[str, Any]:
        """
        Parse a .docx document and maintain its structure
        
        Args:
            file_content: Binary content of the .docx file
            
        Returns:
            Dictionary containing the parsed document structure
            
        Raises:
            DocxParserError: If there's an error parsing the document
        """
        # Input validation
        assert file_content is not None, "File content cannot be None"
        assert isinstance(file_content, bytes), "File content must be bytes"
        assert len(file_content) > 0, "File content cannot be empty"
        
        try:
            # Load the document from bytes
            doc = docx.Document(io.BytesIO(file_content))
            
            # Parse document content
            result = {
                "title": DocxParser._get_title(doc),
                "paragraphs": DocxParser._get_paragraphs(doc),
                "tables": DocxParser._get_tables(doc),
                "headings": DocxParser._get_headings(doc),
                "metadata": DocxParser._get_metadata(doc),
            }
            
            # Output validation
            assert isinstance(result, dict), "Result must be a dictionary"
            assert "title" in result, "Result must have a title"
            assert "paragraphs" in result, "Result must have paragraphs"
            assert "tables" in result, "Result must have tables"
            assert "headings" in result, "Result must have headings"
            assert "metadata" in result, "Result must have metadata"
            
            return result
        except AssertionError as e:
            # Re-raise assertion errors for debugging
            raise
        except Exception as e:
            raise DocxParserError(f"Error parsing document: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes) -> str:
        """
        Extract text content from a .docx document, simulating what would be 
        captured by a Select All + Copy operation in Word
        
        Args:
            file_content: Binary content of the .docx file
            
        Returns:
            String containing all text from the document
            
        Raises:
            DocxParserError: If there's an error parsing the document
        """
        # Input validation
        assert file_content is not None, "File content cannot be None"
        assert isinstance(file_content, bytes), "File content must be bytes"
        assert len(file_content) > 0, "File content cannot be empty"
        
        try:
            # Load the document from bytes
            doc = docx.Document(io.BytesIO(file_content))
            
            # Extract text from paragraphs, preserving the document flow
            text_parts = []
            
            # Process document elements in sequential order
            for element in doc.element.body.iter():
                # Skip the overall body element
                if element.tag.endswith('body'):
                    continue
                
                # Process paragraphs (includes headings, normal paragraphs, and list items)
                if element.tag.endswith('p'):
                    paragraph = None
                    
                    # Find the corresponding paragraph object
                    for p in doc.paragraphs:
                        if p._element is element:
                            paragraph = p
                            break
                    
                    if paragraph and paragraph.text.strip():
                        # Check if it's a list item (has a numPr or bullet/number character)
                        is_list_item = False
                        list_format = ""
                        
                        # Look for numbering properties
                        num_pr = element.xpath('.//w:numPr')
                        if num_pr:
                            is_list_item = True
                            # Approximation of indentation level based on list item
                            ilvl = element.xpath('.//w:ilvl/@w:val')
                            indent = int(ilvl[0]) if ilvl else 0
                            list_format = "  " * indent + "• "
                        
                        # Add the paragraph with appropriate formatting
                        if is_list_item:
                            text_parts.append(f"{list_format}{paragraph.text}")
                        else:
                            text_parts.append(paragraph.text)
                
                # Process tables
                elif element.tag.endswith('tbl'):
                    table = None
                    
                    # Find the corresponding table object
                    for t in doc.tables:
                        if t._element is element:
                            table = t
                            break
                    
                    if table:
                        table_text_parts = []
                        for row in table.rows:
                            row_texts = []
                            for cell in row.cells:
                                row_texts.append(cell.text.strip())
                            table_text_parts.append(" | ".join(row_texts))
                        
                        # Add the table rows as separate lines
                        text_parts.extend(table_text_parts)
            
            # Join all text parts with appropriate spacing
            # Simulate the way Word adds spacing between different elements
            text = "\n\n".join(text_parts)
            
            # Clean up excessive whitespace
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Output validation - empty documents just return empty string
            assert isinstance(text, str), "Result must be a string"
            
            # Return the text - even if empty
            return text
        except AssertionError as e:
            # Re-raise assertion errors for debugging
            raise
        except Exception as e:
            raise DocxParserError(f"Error extracting text from document: {str(e)}")
    
    @staticmethod
    def _get_title(doc: docx.Document) -> str:
        """Extract the document title"""
        if doc.paragraphs and doc.paragraphs[0].text:
            return doc.paragraphs[0].text
        return "Untitled Document"
    
    @staticmethod
    def _get_paragraphs(doc: docx.Document) -> List[Dict[str, Any]]:
        """Extract all paragraphs from the document"""
        paragraphs = []
        
        for para in doc.paragraphs:
            if not para.text.strip():
                continue
                
            # Skip if this is a heading (we'll handle these separately)
            if re.match(r'Heading \d+', para.style.name):
                continue
                
            paragraph_data = {
                "text": para.text,
                "style": para.style.name,
                "runs": [
                    {
                        "text": run.text,
                        "bold": run.bold,
                        "italic": run.italic,
                        "underline": run.underline,
                    }
                    for run in para.runs
                ]
            }
            paragraphs.append(paragraph_data)
            
        return paragraphs
    
    @staticmethod
    def _get_tables(doc: docx.Document) -> List[Dict[str, Any]]:
        """Extract all tables from the document"""
        tables = []
        
        for table in doc.tables:
            table_data = []
            
            for row in table.rows:
                row_data = []
                
                for cell in row.cells:
                    row_data.append(cell.text)
                    
                table_data.append(row_data)
                
            tables.append({"data": table_data})
            
        return tables
    
    @staticmethod
    def _get_headings(doc: docx.Document) -> List[Dict[str, Any]]:
        """Extract all headings from the document"""
        headings = []
        
        for para in doc.paragraphs:
            if re.match(r'Heading \d+', para.style.name):
                level = int(para.style.name.split()[-1])
                headings.append({
                    "text": para.text,
                    "level": level
                })
                
        return headings
    
    @staticmethod
    def _get_metadata(doc: docx.Document) -> Dict[str, str]:
        """Extract document metadata"""
        metadata = {}
        
        try:
            core_properties = doc.core_properties
            
            if core_properties.author:
                metadata["author"] = core_properties.author
            if core_properties.title:
                metadata["title"] = core_properties.title
            if core_properties.created:
                metadata["created"] = str(core_properties.created)
            if core_properties.modified:
                metadata["modified"] = str(core_properties.modified)
                
        except Exception:
            # If we can't get metadata, just return an empty dict
            pass
            
        return metadata 