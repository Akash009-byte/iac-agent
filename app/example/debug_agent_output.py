#!/usr/bin/env python3
"""
Debug script to see raw agent output
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from iac.interactive_strands_agent import interactive_agent as _interactive_agent


def debug_agent_output():
    """Debug the raw agent output"""

    # Generate unique name
    unique_name = f'debug-{int(time.time())}'
    print(f"🔍 Debugging agent output for: {unique_name}")
    print("=" * 60)

    try:
        # Test message
        test_message = f"Create SSH key named {unique_name} in us-east-1"
        print(f"📝 Test Message: {test_message}")

        # Call agent directly
        result = _interactive_agent(test_message)

        print(f"📝 Raw Agent Result:")
        print(f"Type: {type(result)}")
        print(f"Dir: {dir(result)}")

        # Check if result has messages
        if hasattr(result, 'messages') and result.messages:
            print(f"\n📝 Messages ({len(result.messages)}):")
            for i, message_obj in enumerate(result.messages):
                print(f"\nMessage {i+1}:")
                print(f"  Type: {type(message_obj)}")
                print(f"  Dir: {dir(message_obj)}")

                if hasattr(message_obj, 'role'):
                    print(f"  Role: {message_obj.role}")

                if hasattr(message_obj, 'content'):
                    print(f"  Content: {message_obj.content}")
                    if isinstance(message_obj.content, list):
                        for j, content_block in enumerate(message_obj.content):
                            print(f"    Content Block {j+1}:")
                            print(f"      Type: {type(content_block)}")
                            print(f"      Dir: {dir(content_block)}")
                            if hasattr(content_block, 'text'):
                                print(f"      Text: {content_block.text[:200]}...")

                if hasattr(message_obj, 'text'):
                    print(f"  Text: {message_obj.text[:200]}...")

        # Check other attributes
        for attr in ['content', 'text', 'response', 'output']:
            if hasattr(result, attr):
                value = getattr(result, attr)
                print(f"\n📝 {attr}: {value}")

        # String representation
        print(f"\n📝 String representation:")
        print(f"{str(result)[:500]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_agent_output()
