# EC2 Instance Creation Examples

This directory contains examples demonstrating how to create and manage EC2 instances using boto3.

## Files

- `create_ec2_instance.py` - Comprehensive example showing EC2 instance creation with various configurations

## Prerequisites

1. **AWS Credentials**: Ensure your AWS credentials are configured. You can:
   - Use AWS CLI: `aws configure`
   - Set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - Use IAM roles (if running on EC2)

2. **Required Permissions**: Your AWS user/role needs the following permissions:
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
                   "ec2:CreateTags",
                   "ec2:DescribeImages",
                   "ec2:DescribeSecurityGroups",
                   "ec2:DescribeSubnets",
                   "ec2:DescribeVpcs"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

## Usage

### Basic Example

```python
from example.create_ec2_instance import EC2InstanceManager

# Initialize manager
ec2_manager = EC2InstanceManager(region_name='us-east-1')

# Create a basic instance
result = ec2_manager.create_instance(
    image_id='ami-0c02fb55956c7d316',  # Amazon Linux 2
    instance_type='t2.micro',
    tags={
        'Name': 'My-Instance',
        'Environment': 'Development'
    }
)

if result['success']:
    print(f"Instance created: {result['instance_id']}")
    print(f"Public IP: {result['instance_details']['public_ip']}")
else:
    print(f"Error: {result['error']}")
```

### Advanced Example with User Data

```python
# User data script to install Apache
user_data = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from EC2!</h1>" > /var/www/html/index.html
"""

result = ec2_manager.create_instance(
    image_id='ami-0c02fb55956c7d316',
    instance_type='t2.micro',
    user_data=user_data,
    tags={'Name': 'Web-Server', 'Purpose': 'Web-Server'}
)
```

### VPC Example

```python
# Create instance in specific subnet
result = ec2_manager.create_instance(
    image_id='ami-0c02fb55956c7d316',
    instance_type='t2.micro',
    subnet_id='subnet-12345678',  # Your subnet ID
    security_group_ids=['sg-12345678'],  # Your security group ID
    tags={'Name': 'VPC-Instance', 'Network': 'Private'}
)
```

## Running the Examples

1. **Direct execution**:
   ```bash
   cd app/example
   python3 create_ec2_instance.py
   ```

2. **Import and use**:
   ```python
   from example.create_ec2_instance import EC2InstanceManager, main
   
   # Run the example
   main()
   
   # Or use the class directly
   ec2_manager = EC2InstanceManager()
   # ... your code here
   ```

## Features Demonstrated

- ✅ Basic EC2 instance creation
- ✅ Instance configuration (type, AMI, etc.)
- ✅ Tagging instances
- ✅ User data scripts
- ✅ VPC and subnet configuration
- ✅ Security group assignment
- ✅ Error handling
- ✅ Instance details retrieval
- ✅ Instance listing
- ✅ Instance termination

## Important Notes

1. **Cost**: EC2 instances incur charges. Always terminate instances when done testing.

2. **AMI IDs**: AMI IDs are region-specific. The example uses `ami-0c02fb55956c7d316` (Amazon Linux 2) for `us-east-1`. Update for your region.

3. **Security Groups**: Ensure your security groups allow necessary traffic (SSH, HTTP, etc.).

4. **Key Pairs**: For SSH access, you'll need a key pair. Create one in the AWS Console or via CLI.

5. **Free Tier**: `t2.micro` instances are eligible for AWS Free Tier (750 hours/month for 12 months).

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check your AWS credentials and IAM permissions
2. **AMI Not Found**: Verify the AMI ID exists in your region
3. **Subnet Not Found**: Ensure the subnet ID is correct and in the same region
4. **Security Group Not Found**: Verify the security group ID and region

### Debug Mode

Enable debug logging to see detailed boto3 requests:

```python
import boto3
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('', logging.DEBUG)
```

## Integration with IaC Agent

This example can be integrated with the IaC agent in `app/iac/interactive_strands_agent.py` to provide programmatic EC2 management capabilities through the chatbot interface.
