# AWS Infrastructure Management Agent

This directory contains the AWS Infrastructure Management Agent built with Strands SDK, providing comprehensive AWS EC2, Security Group, and Key Pair management capabilities.

## Structure

```
iac/
├── interactive_strands_agent.py  # Main agent file
├── tools/                         # Modular tools directory
│   ├── __init__.py               # Tools package initialization
│   ├── validation.py             # Validation functions
│   ├── data_collection.py        # Data collection utilities
│   ├── key_pair_tools.py         # Key pair management tools
│   ├── ec2_tools.py              # EC2 instance management tools
│   └── security_group_tools.py   # Security group management tools
└── README.md                     # This file
```

## Features

### 🔑 Key Pair Management
- **Create Key Pairs**: Generate new SSH key pairs with private key download
- **List Key Pairs**: View all key pairs in a region
- **Delete Key Pairs**: Remove unused key pairs
- **Key Pair Details**: Get detailed information about specific key pairs
- **SSH Integration**: Seamless integration with EC2 instance creation

### 🖥️ EC2 Instance Management
- **Create Instances**: Launch EC2 instances with comprehensive configuration
- **List Instances**: View all instances with detailed information
- **Start/Stop Instances**: Manage instance lifecycle
- **Terminate Instances**: Permanently delete instances
- **Instance Information**: Get detailed instance specifications

### 🔒 Security Group Management
- **Create Security Groups**: Create new security groups with custom rules
- **Add/Remove Rules**: Manage inbound and outbound rules
- **List Security Groups**: View all security groups
- **Security Group Details**: Get comprehensive rule information
- **Web Server Templates**: Pre-configured security groups for common use cases

### 📊 Data Collection & Validation
- **Systematic Data Collection**: Ensures all required information is gathered
- **Parameter Validation**: Validates all inputs before tool execution
- **Progress Tracking**: Tracks data collection status
- **Error Prevention**: Prevents incomplete tool calls

## Key Pair Creation Process

1. **User Request**: User wants to create a key pair or EC2 instance
2. **Data Collection**: Agent collects region and key name
3. **Validation**: Validates all required parameters
4. **Creation**: Creates key pair and returns private key
5. **Download Instructions**: Provides SSH setup and security guidance

### Example Conversation Flow

```
🤖 Agent: I'd like to help you create a key pair for SSH access. 
          First, which AWS region would you like to use?
👤 User: us-east-1

🤖 Agent: Great! What would you like to name this key pair?
👤 User: my-ssh-key

🤖 Agent: Perfect! Let me create your key pair...

✅ Key pair created successfully!
Key Name: my-ssh-key
Region: us-east-1

🔑 PRIVATE KEY (Save this securely):
-----BEGIN RSA PRIVATE KEY-----
[Private key content]
-----END RSA PRIVATE KEY-----

⚠️ IMPORTANT SECURITY NOTES:
1. Save this private key to ~/.ssh/my-ssh-key.pem
2. Set permissions: chmod 400 ~/.ssh/my-ssh-key.pem
3. Never share this private key publicly
4. Use to SSH: ssh -i ~/.ssh/my-ssh-key.pem ec2-user@<instance-ip>
```

## EC2 Instance Creation with Key Pair Integration

The agent seamlessly integrates key pair creation with EC2 instance creation:

1. **Instance Setup**: Collects region, instance type, and name
2. **Key Pair Check**: Asks if user has a key pair
3. **Key Pair Creation**: Creates key pair if needed
4. **Instance Creation**: Uses the key pair for the instance
5. **Complete Setup**: Provides full SSH access instructions

## Security Features

### Key Pair Security
- Private keys are only shown once during creation
- Comprehensive security warnings and best practices
- Proper file permission instructions
- SSH usage examples

### Security Group Best Practices
- Principle of least privilege
- Specific IP ranges instead of 0.0.0.0/0
- Descriptive rule comments
- Regular cleanup recommendations

## Usage

### Direct Import
```python
from iac.interactive_strands_agent import interactive_agent

# Use the agent
response = interactive_agent.run("Create a key pair named my-key in us-east-1")
```

### Individual Tools
```python
from iac.tools import create_key_pair, create_ec2_instance

# Create key pair
result = create_key_pair("us-east-1", "my-key")

# Create EC2 instance
result = create_ec2_instance("us-east-1", "t2.micro", "my-instance", "my-key")
```

### Web Application Integration
The agent is integrated with the web application in `../webapp/webapp.py` and can be accessed through the chatbot interface.

## Configuration

### Required Environment Variables
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_SESSION_TOKEN`: AWS session token (optional)

### OpenAI Configuration
The agent uses OpenAI's GPT-4o model with the following configuration:
- Model: gpt-4o
- Max Tokens: 1000
- Temperature: 0.7

## Error Handling

The agent includes comprehensive error handling:
- Parameter validation before tool execution
- AWS API error handling
- User-friendly error messages
- Graceful degradation for missing dependencies

## Testing

Test scripts are available in the `../example/` directory:
- `test_key_pair_integration.py`: Key pair functionality tests
- `test_data_collection.py`: Data collection validation tests
- `create_ec2_instance.py`: EC2 instance creation examples
- `security_group_management.py`: Security group management examples

## Best Practices

1. **Always collect all required data before calling tools**
2. **Provide clear instructions and warnings to users**
3. **Follow AWS security best practices**
4. **Use descriptive names for resources**
5. **Regularly clean up unused resources**
6. **Keep private keys secure and never share them**

## Troubleshooting

### Common Issues
1. **Missing AWS Credentials**: Ensure environment variables are set
2. **Region Issues**: Verify the region exists and is accessible
3. **Permission Errors**: Check AWS IAM permissions
4. **Key Pair Conflicts**: Ensure key pair names are unique

### Debug Mode
Enable debug logging to see detailed AWS API calls:
```python
import boto3
import logging

logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('', logging.DEBUG)
```

## Contributing

When adding new tools:
1. Create the tool function in the appropriate `tools/` file
2. Add validation functions if needed
3. Update the `__init__.py` imports
4. Add the tool to the agent's tools list
5. Update the system prompt if needed
6. Add tests in the `example/` directory

## License

This project is part of the AWS Infrastructure Management system.
