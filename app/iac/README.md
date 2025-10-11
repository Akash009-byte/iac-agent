# Infrastructure-as-Code (IaC) Automation Agent

An intelligent agent built with the Strands SDK that provides natural language interface for AWS infrastructure management.

## Features

- 🤖 **Amazon Bedrock AI**: Uses AWS Bedrock for AI processing
- 🚀 **Natural Language Commands**: Describe what you want in plain English
- ☁️ **AWS EC2 Management**: Create, list, and terminate EC2 instances
- 🔒 **Security Groups**: Create and manage security groups
- 🖼️ **AMI Discovery**: Find the latest Amazon Linux AMIs
- 🏷️ **Tagging Support**: Add custom tags to resources
- 🔧 **Flexible Configuration**: Support for various instance types, regions, and parameters

## Quick Start

### Prerequisites

1. **AWS Bedrock Access**: Ensure your AWS account has Bedrock permissions
2. **AWS Credentials**: Configure your AWS credentials via environment variables
3. **Python Dependencies**: Install required packages

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### Quick Setup

Use the provided setup script to configure AWS credentials:

```bash
# Run the setup script
source app/iac/setup_credentials.sh

# Or manually set environment variables
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_SESSION_TOKEN="your_session_token"  # Optional for temporary credentials
```

### Basic Usage

```python
from app.iac.agent import iac_agent

# Create an EC2 instance
response = iac_agent("Spin up an EC2 instance in us-west-2 using Amazon Linux")
print(response)

# List running instances
response = iac_agent("Show me all running EC2 instances in us-west-2")
print(response)

# Get latest AMI
response = iac_agent("What's the latest Amazon Linux 2 AMI for us-west-2?")
print(response)
```

### Running Examples

```bash
# Run the example script
python app/iac/example_usage.py

# Or run the agent directly
python app/iac/agent.py
```

## Available Tools

### 1. `verify_aws_credentials`
Verifies that AWS credentials are properly configured and accessible.

**Parameters:**
- `region` (optional): AWS region to test credentials against (default: us-west-2)

**Example:**
```python
response = iac_agent("Check if my AWS credentials are properly configured")
```

### 2. `create_ec2_instance`
Creates EC2 instances with customizable parameters.

**Parameters:**
- `region` (required): AWS region
- `instance_type` (optional): EC2 instance type (default: t2.micro)
- `ami` (optional): AMI ID (default: Amazon Linux 2)
- `key_name` (optional): SSH key pair name
- `security_group_ids` (optional): List of security group IDs
- `subnet_id` (optional): Subnet ID
- `user_data` (optional): User data script
- `tags` (optional): Dictionary of tags

**Example:**
```python
response = iac_agent("Create a t3.small instance in us-east-1 with tags Environment=Production")
```

### 3. `list_ec2_instances`
Lists EC2 instances in a region, optionally filtered by state.

**Parameters:**
- `region` (required): AWS region
- `state` (optional): Filter by instance state

**Example:**
```python
response = iac_agent("Show me all stopped instances in us-west-2")
```

### 4. `terminate_ec2_instance`
Terminates an EC2 instance.

**Parameters:**
- `region` (required): AWS region
- `instance_id` (required): Instance ID to terminate

**Example:**
```python
response = iac_agent("Terminate instance i-1234567890abcdef0 in us-west-2")
```

### 5. `create_security_group`
Creates a security group.

**Parameters:**
- `region` (required): AWS region
- `group_name` (required): Security group name
- `description` (required): Description
- `vpc_id` (optional): VPC ID (uses default VPC if not specified)

**Example:**
```python
response = iac_agent("Create a security group named 'web-servers' for HTTP traffic")
```

### 6. `get_amazon_linux_ami`
Gets the latest Amazon Linux 2 AMI ID for a region.

**Parameters:**
- `region` (required): AWS region

**Example:**
```python
response = iac_agent("Get the latest Amazon Linux AMI for us-west-2")
```

## Example Commands

### Basic Infrastructure Requests
```
"Create a web server in us-west-2"
"Spin up a database server using t3.medium in us-east-1"
"Launch an EC2 instance with Amazon Linux in eu-west-1"
```

### Advanced Configuration
```
"Create a t3.large instance in us-west-2 with tags Environment=Production, Project=WebApp"
"Deploy a web server with security group allowing HTTP and HTTPS traffic"
"Create an EC2 instance using the latest Amazon Linux AMI with custom user data"
```

### Management Operations
```
"Show me all running instances in us-west-2"
"List all EC2 instances in us-east-1"
"Terminate instance i-1234567890abcdef0"
"What's the status of my EC2 instances?"
```

### AMI Discovery
```
"What's the latest Amazon Linux 2 AMI for us-west-2?"
"Find the best AMI for a web server in us-east-1"
"Get Amazon Linux AMI details for eu-west-1"
```

## AWS Configuration

The agent uses AWS credentials from environment variables. You can set them in several ways:

### Option 1: Using the Setup Script (Recommended)
```bash
source app/iac/setup_credentials.sh
```

### Option 2: Manual Environment Variables
```bash
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_SESSION_TOKEN="your_session_token"  # Optional for temporary credentials
```

### Option 3: AWS CLI Configuration
```bash
aws configure
```

### Option 4: IAM Roles (for EC2 instances)
If running on an EC2 instance, use IAM roles for automatic credential management.

## Amazon Bedrock Configuration

The agent uses Amazon Bedrock for AI processing. Configure Bedrock access as follows:

### Required Permissions
Your AWS credentials need the following Bedrock permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Enabling Bedrock Models
1. Go to AWS Bedrock console
2. Navigate to "Model access" in the left sidebar
3. Request access to foundation models (e.g., Claude, Llama)
4. Wait for approval (usually instant for most models)

### Troubleshooting Bedrock Access
If you get permission errors:

#### Common Issues and Solutions:

1. **Model Access Error**: "You don't have access to the model with the specified model ID"
   - Go to AWS Bedrock Console → Model access → Request access to foundation models

2. **On-demand Throughput Error**: "Invocation of model ID XXXX with on-demand throughput isn't supported"
   - Use regional prefix: `us.anthropic.claude-sonnet-4-20250514-v1:0` instead of `anthropic.claude-sonnet-4-20250514-v1:0`

3. **Invalid Model Identifier**: "The provided model identifier is invalid"
   - Use a valid model ID without regional prefix: `anthropic.claude-3-5-sonnet-20241022-v2:0`

4. **Permission Denied**: "User is not authorized to perform: bedrock:InvokeModelWithResponseStream"
   - Ensure IAM permissions include `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`
   - Check if Bedrock is available in your region
   - Verify model access is enabled in Bedrock console

## Security Considerations

- 🔐 **IAM Permissions**: Ensure your AWS credentials have appropriate permissions
- 🛡️ **Security Groups**: Always configure security groups properly
- 🔑 **Key Pairs**: Use SSH key pairs for secure instance access
- 🏷️ **Tagging**: Tag resources for better management and cost tracking

### Required IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ec2:DescribeInstances",
                "ec2:TerminateInstances",
                "ec2:CreateSecurityGroup",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeImages",
                "ec2:DescribeVpcs",
                "ec2:CreateTags",
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Error Handling

The agent provides clear error messages for common issues:

- ❌ **Invalid Region**: "Region 'invalid-region' not found"
- ❌ **Insufficient Permissions**: "Access denied for EC2 operations"
- ❌ **Invalid AMI**: "AMI 'ami-invalid' not found in region"
- ❌ **Instance Limits**: "Instance limit exceeded for instance type"

## Contributing

To extend the agent with new capabilities:

1. Add new tool functions using the `@tool` decorator
2. Register tools in the `iac_agent` initialization
3. Update the system prompt with new capabilities
4. Add examples and documentation

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are properly configured
   - Check environment variables or AWS CLI configuration

2. **Permission Denied**
   - Verify IAM permissions for EC2 operations
   - Check if the user/role has necessary permissions

3. **Region Not Found**
   - Use valid AWS region names (e.g., us-west-2, us-east-1)
   - Check if the region supports EC2

4. **AMI Not Found**
   - Use valid AMI IDs for the specified region
   - Try using the `get_amazon_linux_ami` tool first

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export STRANDS_DEBUG=1
```

## License

This project is part of the agent workspace and follows the same licensing terms.
# iac-agent
# iac-agent
