#!/usr/bin/env python3
"""
Test script to understand the Strands agent response structure
"""

from interactive_strands_agent import interactive_agent

def test_agent_response():
    """Test the agent response structure"""
    print("🧪 Testing Strands Agent Response Structure")
    print("=" * 50)
    
    # Test with a simple message
    test_message = "Hello, can you help me with AWS EC2?"
    
    try:
        print(f"📤 Sending message: {test_message}")
        result = interactive_agent(test_message)
        
        print(f"\n📥 Response type: {type(result)}")
        print(f"📥 Response attributes: {dir(result)}")
        
        # Try different ways to extract content
        print(f"\n🔍 Content extraction attempts:")
        
        if hasattr(result, 'content'):
            print(f"✅ Has 'content' attribute: {result.content}")
        
        if hasattr(result, 'text'):
            print(f"✅ Has 'text' attribute: {result.text}")
        
        if hasattr(result, 'messages'):
            print(f"✅ Has 'messages' attribute: {result.messages}")
            if result.messages:
                print(f"   Last message: {result.messages[-1]}")
                print(f"   Last message type: {type(result.messages[-1])}")
                print(f"   Last message attributes: {dir(result.messages[-1])}")
        
        if hasattr(result, 'response'):
            print(f"✅ Has 'response' attribute: {result.response}")
        
        if hasattr(result, 'output'):
            print(f"✅ Has 'output' attribute: {result.output}")
        
        # Try string conversion
        print(f"\n🔤 String conversion: {str(result)}")
        
        # Try to access common attributes
        for attr in ['content', 'text', 'response', 'output', 'result', 'data']:
            if hasattr(result, attr):
                value = getattr(result, attr)
                print(f"✅ {attr}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_response()
