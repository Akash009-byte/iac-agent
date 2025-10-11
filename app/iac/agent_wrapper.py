#!/usr/bin/env python3
"""
Wrapper for Strands Agent to handle response extraction
"""

from interactive_strands_agent import interactive_agent as _interactive_agent


def interactive_agent(message: str) -> str:
    """
    Wrapper function that extracts text content from Strands AgentResult
    
    Args:
        message: User message to send to the agent
    
    Returns:
        String response from the agent
    """
    try:
        # Get the agent result
        result = _interactive_agent(message)
        
        # Extract text content from AgentResult
        response_text = None
        
        # Method 1: Check if result has messages
        if hasattr(result, 'messages') and result.messages:
            # Get the last assistant message
            for message_obj in reversed(result.messages):
                if hasattr(message_obj, 'role') and message_obj.role == 'assistant':
                    if hasattr(message_obj, 'content'):
                        if isinstance(message_obj.content, list):
                            # Content is a list of content blocks
                            for content_block in message_obj.content:
                                if hasattr(content_block, 'text'):
                                    response_text = content_block.text
                                    break
                        else:
                            response_text = str(message_obj.content)
                    elif hasattr(message_obj, 'text'):
                        response_text = message_obj.text
                    break
        
        # Method 2: Direct attributes
        if not response_text:
            if hasattr(result, 'content'):
                response_text = str(result.content)
            elif hasattr(result, 'text'):
                response_text = str(result.text)
            elif hasattr(result, 'response'):
                response_text = str(result.response)
            elif hasattr(result, 'output'):
                response_text = str(result.output)
        
        # Method 3: String conversion fallback
        if not response_text:
            response_text = str(result)
        
        # Ensure we have a valid response
        if not response_text or response_text.strip() == "":
            response_text = "I'm sorry, I couldn't process your request. Please try again."
        
        return response_text
        
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."


# Export the wrapper as the main function
__all__ = ['interactive_agent']
