#!/usr/bin/env python3
"""
Wrapper for Strands Agent to handle response extraction
"""

import sys
from pathlib import Path

# Add parent directory to path to import from iac
sys.path.append(str(Path(__file__).parent.parent))
from iac.interactive_strands_agent import interactive_agent as _interactive_agent


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
        
        # Method 1: Check traces for tool outputs (for key pair creation)
        if hasattr(result, 'metrics') and hasattr(result.metrics, 'traces'):
            tool_outputs = []
            for trace in result.metrics.traces:
                if hasattr(trace, 'children'):
                    for child in trace.children:
                        if hasattr(child, 'name') and 'Tool:' in child.name:
                            if hasattr(child, 'message') and child.message:
                                message = child.message
                                if isinstance(message, dict) and 'content' in message:
                                    content = message['content']
                                    if isinstance(content, list):
                                        for content_block in content:
                                            if isinstance(content_block, dict) and 'toolResult' in content_block:
                                                tool_result = content_block['toolResult']
                                                if 'content' in tool_result:
                                                    tool_content = tool_result['content']
                                                    if isinstance(tool_content, list):
                                                        for tool_block in tool_content:
                                                            if isinstance(tool_block, dict) and 'text' in tool_block:
                                                                tool_outputs.append(tool_block['text'])
            
            if tool_outputs:
                # Use tool outputs as the primary response
                response_text = '\n\n'.join(tool_outputs)
                
        
        # Method 2: Check if result has messages (fallback)
        if not response_text and hasattr(result, 'messages') and result.messages:
            # Collect all assistant messages and tool outputs
            all_responses = []
            tool_outputs = []
            
            for message_obj in result.messages:
                if hasattr(message_obj, 'role'):
                    if message_obj.role == 'assistant':
                        if hasattr(message_obj, 'content'):
                            if isinstance(message_obj.content, list):
                                # Content is a list of content blocks
                                for content_block in message_obj.content:
                                    if hasattr(content_block, 'text'):
                                        all_responses.append(content_block.text)
                                        break
                            else:
                                all_responses.append(str(message_obj.content))
                        elif hasattr(message_obj, 'text'):
                            all_responses.append(message_obj.text)
                    elif message_obj.role == 'tool':
                        # Collect tool outputs separately (like key pair creation results)
                        if hasattr(message_obj, 'content'):
                            if isinstance(message_obj.content, list):
                                for content_block in message_obj.content:
                                    if hasattr(content_block, 'text'):
                                        tool_outputs.append(content_block.text)
                                        break
                            else:
                                tool_outputs.append(str(message_obj.content))
                        elif hasattr(message_obj, 'text'):
                            tool_outputs.append(message_obj.text)
            
            # Prioritize tool outputs for key pair creation
            if tool_outputs:
                # If we have tool outputs, use them as the primary response
                response_text = '\n\n'.join(tool_outputs)
            elif all_responses:
                # Otherwise, use assistant responses
                response_text = '\n\n'.join(all_responses)
        
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
