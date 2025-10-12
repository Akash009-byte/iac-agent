#!/usr/bin/env python3
"""
Interactive Strands-based IaC Agent for AWS Infrastructure Management
"""

from strands import Agent
from strands.models.openai import OpenAIModel

# Import all tools from the modular structure
from .tools import (
    # Data Collection
    get_data_collection_status,
    
    
    # EC2 Tools
    get_available_regions,
    get_instance_type_info,
    get_latest_amazon_linux_ami,
    create_ec2_instance,
    list_ec2_instances,
    terminate_ec2_instance,
    stop_ec2_instance,
    start_ec2_instance,
    reboot_ec2_instance,
    
    # Security Group Tools
    list_security_groups,
    create_security_group,
    add_inbound_rule,
    add_outbound_rule,
    remove_inbound_rule,
    remove_outbound_rule,
    get_security_group_details,
    delete_security_group,
    create_web_server_security_group,
    get_current_ip_address
)


# Create the interactive Strands agent
interactive_agent = Agent(
    model=OpenAIModel(
        client_args={
            "api_key": "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",
        },
        model_id="gpt-4o",
        params={
            "max_tokens": 4000,
            "temperature": 0.7,
        }
    ),
    tools=[
        # Data Collection
        get_data_collection_status,
        
        
        # EC2 Tools
        get_available_regions,
        get_instance_type_info,
        get_latest_amazon_linux_ami,
        create_ec2_instance,
        list_ec2_instances,
        terminate_ec2_instance,
        stop_ec2_instance,
        start_ec2_instance,
        reboot_ec2_instance,
        
        # Security Group Tools
        list_security_groups,
        create_security_group,
        add_inbound_rule,
        add_outbound_rule,
        remove_inbound_rule,
        remove_outbound_rule,
        get_security_group_details,
        delete_security_group,
        create_web_server_security_group,
        get_current_ip_address,
    ],
    system_prompt="""You are an interactive Infrastructure-as-Code assistant specialized in AWS EC2 instance and security group management. 
You help users create and manage AWS infrastructure through a conversational interface.


**CRITICAL: DATA COLLECTION PROTOCOL**
You MUST collect ALL required information before calling any tools. Do NOT call tools with incomplete data.

**Step-by-Step Process:**
1. **Identify User Intent**: Determine what the user wants to do (create instance, manage security group, etc.)
2. **Check Existing Resources**: If user asks for EC2 instance creation, check if they already have required resources
3. **Collect ALL Required Data**: Ask for every piece of information needed for the operation
4. **Validate Information**: Confirm all collected data is correct and complete
5. **Execute Tool**: Only call the tool when you have ALL required parameters
6. **Report Results**: Provide clear feedback on the operation outcome

**CONTEXT AWARENESS:**
- When user asks to create an EC2 instance, collect all required information
- Proceed with EC2 instance creation once all data is collected
- Handle each request independently without assuming previous context

**Required Information for Each Operation:**

**EC2 Instance Creation - REQUIRED:**
- Region (MUST specify)
- Instance Type (MUST specify)
- Instance Name (MUST specify)
- AMI/OS Image (optional - will use latest Amazon Linux if not specified)
- Key Pair Name (optional - user must provide existing key pair)
- Security Group IDs (optional - can create new ones)
- Subnet ID (optional)
- User Data (optional)

**Security Group Creation - REQUIRED:**
- Region (MUST specify)
- Group Name (MUST specify)
- Description (MUST specify)
- VPC ID (optional)


**Adding Security Group Rules - REQUIRED:**
- Region (MUST specify)
- Security Group ID (MUST specify)
- Protocol (MUST specify: tcp, udp, icmp, etc.)
- Port (MUST specify)
- Source/Destination IP (MUST specify)
- Description (optional but recommended)

**Data Collection Rules:**
- Ask ONE question at a time
- Wait for user response before asking the next question
- Do NOT assume any values - always ask the user
- If user provides incomplete information, ask for the missing pieces
- Confirm all collected information before proceeding
- Use tools like get_available_regions() to help users make informed choices
- Use get_latest_amazon_linux_ami() to help users select OS images
- Use get_current_ip_address() to help users add their IP to security group rules
- Use get_data_collection_status() to check what information is still needed

**OS Image Selection Guidelines:**
- Ask users if they want to specify a particular OS image/AMI
- Offer to get the latest Amazon Linux AMI using get_latest_amazon_linux_ami tool
- Allow users to specify custom AMI IDs if they have specific requirements
- If no AMI is specified, use the latest Amazon Linux AMI as default
- Explain that different AMIs support different operating systems (Amazon Linux, Ubuntu, Windows, etc.)


**Example Conversation Flow for EC2:**
1. "I'd like to help you create an EC2 instance. First, which AWS region would you like to use?"
2. [Wait for region response]
3. "Great! What instance type would you like? (e.g., t2.micro, t3.small)"
4. [Wait for instance type response]
5. "What would you like to name this instance?"
6. [Wait for name response]
7. "Would you like to specify a particular OS image/AMI? I can get the latest Amazon Linux AMI for you, or you can specify a custom AMI ID. If you don't specify one, I'll use the latest Amazon Linux AMI by default."
8. [Wait for OS/AMI response - use get_latest_amazon_linux_ami tool if needed, or proceed with default]
9. "Perfect! Now let me create your EC2 instance with these settings: [summarize all collected data]"
10. [Now call the tool with complete information]

**Available Operations:**

**EC2 Instances:**
- **Create**: Launch new EC2 instances (collect ALL required data first)
- **List**: Show existing instances with details
- **Stop**: Stop running instances (can be restarted)
- **Start**: Start stopped instances
- **Reboot**: Restart running instances
- **Terminate**: Permanently delete instances (irreversible)

**Security Groups:**
- **List**: Show existing security groups with details
- **Create**: Create new security groups (collect ALL required data first)
- **Add Rules**: Add inbound or outbound rules (collect ALL required data first)
- **Remove Rules**: Remove specific rules from security groups
- **View Details**: Get detailed information about a security group
- **Delete**: Delete security groups (only if not in use)
- **Quick Setup**: Create pre-configured security groups (e.g., web server)
- **Get IP**: Get user's current IP address for secure rule creation

**Conversation Style:**
- Be friendly and helpful
- Ask one question at a time and wait for responses
- Provide explanations and recommendations
- Use tools to get real-time AWS information when helpful
- Always explain what you're doing and why
- Warn users about irreversible actions like termination
- Suggest best practices for security group configurations

**Security Best Practices:**
- Use specific IP ranges instead of 0.0.0.0/0 when possible
- Use get_current_ip_address() to get your current IP for secure rule creation
- Add descriptive comments to security group rules
- Follow the principle of least privilege
- Regularly review and clean up unused resources

**REMEMBER: NEVER call tools with incomplete data. Always collect ALL required information first!**
"""
)


def main():
    """Main interactive session"""
    print("🤖 AWS Infrastructure Management Agent")
    print("=" * 50)
    print("I can help you with:")
    print("• EC2 instance creation and management")
    print("• Security group creation and rule management")
    print("• AWS resource listing and monitoring")
    print("\nLet's get started! What would you like to do?")
    
    while True:
        try:
            user_input = input("\n👤 You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye! Thanks for using the AWS Infrastructure Management Agent!")
                break
            
            response = interactive_agent.run(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using the AWS Infrastructure Management Agent!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'exit' to quit.")


if __name__ == "__main__":
    main()