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
        
        # Method 1: Check if result has messages (primary method)
        if hasattr(result, 'messages') and result.messages:
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
                        # Collect tool outputs separately
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
            
            # Prioritize assistant responses, then add tool outputs
            if all_responses:
                response_text = '\n\n'.join(all_responses)
                print(f"🔍 Agent wrapper: Found {len(all_responses)} assistant responses")
                print(f"🔍 Agent wrapper: Assistant response preview: {response_text[:200]}...")
                
                # Add tool outputs if they exist and are different from assistant response
                if tool_outputs:
                    tool_text = '\n\n'.join(tool_outputs)
                    print(f"🔍 Agent wrapper: Found {len(tool_outputs)} tool outputs")
                    print(f"🔍 Agent wrapper: Tool output preview: {tool_text[:200]}...")
                    
                    # Only add tool output if it's different from the assistant response
                    if tool_text not in response_text:
                        response_text += '\n\n' + tool_text
                        print("🔍 Agent wrapper: Added tool output to response")
                    else:
                        print("🔍 Agent wrapper: Tool output already included in assistant response")
            elif tool_outputs:
                # Fallback to tool outputs if no assistant response
                response_text = '\n\n'.join(tool_outputs)
                print(f"🔍 Agent wrapper: No assistant response, using {len(tool_outputs)} tool outputs")
                
        
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
            print("🔍 Agent wrapper: No response text found, using fallback message")
        
        print(f"🔍 Agent wrapper: Final response length: {len(response_text)}")
        print(f"🔍 Agent wrapper: Final response preview: {response_text[:200]}...")
        
        return response_text
        
    except Exception as e:
        return f"I'm sorry, I encountered an error: {str(e)}. Please try again."


# Export the wrapper as the main function
__all__ = ['interactive_agent']
