# SSH Key Creation and Download Examples

This directory contains comprehensive examples for creating and downloading SSH keys using the AWS Infrastructure Management Agent.

## Examples Overview

### 1. `ssh_key_example.py` - Complete SSH Key Workflow
**Purpose**: Demonstrates the complete workflow of SSH key creation and download using the agent directly.

**Features**:
- Creates SSH keys via the agent
- Extracts key information from agent responses
- Simulates webapp download process
- Saves keys to files with proper permissions
- Works with or without AWS credentials (simulation mode)

**Usage**:
```bash
# With AWS credentials
python3 ssh_key_example.py

# Without AWS credentials (simulation)
python3 ssh_key_example.py
```

### 2. `webapp_ssh_example.py` - Webapp Integration Example
**Purpose**: Demonstrates how to interact with the webapp for SSH key creation and download.

**Features**:
- Connects to the running webapp
- Sends chat messages via WebSocket
- Receives download information
- Downloads SSH keys via HTTP API
- Saves keys with proper permissions

**Usage**:
```bash
# Start webapp first
python3 main.py

# In another terminal, run the example
python3 webapp_ssh_example.py
```

## Prerequisites

### AWS Credentials Setup
Before running the examples with real AWS resources, set up your credentials:

**Option 1: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"  # Optional
```

**Option 2: AWS CLI Configuration**
```bash
aws configure
```

**Option 3: IAM Role (if running on EC2)**
Ensure your EC2 instance has an IAM role with EC2 permissions.

### Required Permissions
Your AWS credentials need the following permissions:
- `ec2:CreateKeyPair`
- `ec2:DescribeKeyPairs`
- `ec2:DeleteKeyPair`

## Example Workflows

### Workflow 1: Direct Agent Usage
```python
from ssh_key_example import SSHKeyExample

# Create example instance
example = SSHKeyExample()

# Run complete example
success = example.run_complete_example("my-key", "us-east-1")

if success:
    print("SSH key created and saved successfully!")
```

### Workflow 2: Webapp Integration
```python
from webapp_ssh_example import WebappSSHExample

# Create webapp example instance
example = WebappSSHExample("http://0.0.0.0:5001")

# Run complete example
success = example.run_complete_example("webapp-key", "us-east-1")

if success:
    print("SSH key created via webapp and downloaded!")
```

## Expected Output

### Successful SSH Key Creation
```
🚀 SSH Key Creation and Download Example
============================================================
🔑 Creating SSH key 'example-key' in region 'us-east-1'...

📝 Agent Response:
--------------------------------------------------
✅ Key pair created successfully!

Key Pair Details:
- Key Name: example-key
- Key Pair ID: key-123456
- Region: us-east-1

🔑 PRIVATE KEY (Save this securely - it won't be shown again):
```
-----BEGIN RSA PRIVATE KEY-----
[Private key content]
-----END RSA PRIVATE KEY-----
```
--------------------------------------------------

🔍 Detection Results:
✅ Contains 'PRIVATE KEY': True
✅ Contains '-----BEGIN RSA PRIVATE KEY-----': True
✅ Contains 'key pair' and 'created successfully': True
✅ SSH key creation detected successfully!

📋 Extracted Key Information:
Key Name: example-key
Region: us-east-1
Has Private Key: True

📥 Simulating Webapp Download Process:
Key Name: example-key
Region: us-east-1
Private Key Length: 901 characters

🔧 Webapp Process:
1. ✅ Key detected in agent response
2. ✅ Key information extracted
3. ✅ Key stored temporarily with ID: example_key_1234567890
4. ✅ Download button would appear in chat
5. ✅ User clicks download button
6. ✅ Key downloaded as example-key.pem
7. ✅ Key removed from temporary storage

💾 SSH Key Saved:
Filename: example-key.pem
Permissions: 400 (read-only for owner)
Size: 901 characters

🔑 SSH Usage:
ssh -i example-key.pem ec2-user@<instance-public-ip>

🎉 SUCCESS! Complete example completed successfully!
✅ SSH key created via agent
✅ Key information extracted
✅ Download process simulated
✅ Key saved to file with proper permissions
```

## Security Features

### Key Security
- **Temporary Storage**: Keys are stored temporarily with 1-hour expiration
- **Automatic Cleanup**: Keys are removed after download
- **Proper Permissions**: Files are saved with chmod 400 (read-only for owner)
- **No Permanent Storage**: Keys are never stored permanently on the server

### Best Practices
- **Secure Storage**: Save keys to `~/.ssh/` directory
- **Proper Permissions**: Always use `chmod 400` for private keys
- **Never Share**: Private keys should never be shared publicly
- **Regular Rotation**: Rotate keys regularly for security

## Troubleshooting

### Common Issues

**1. AWS Credentials Not Found**
```
❌ Error creating key pair: AWS credentials not found in environment variables.
```
**Solution**: Set up AWS credentials using one of the methods above.

**2. Webapp Not Running**
```
❌ Cannot connect to webapp: [Errno 61] Connection refused
```
**Solution**: Start the webapp with `python3 main.py`.

**3. Permission Denied**
```
❌ Error saving key: [Errno 13] Permission denied
```
**Solution**: Ensure you have write permissions in the current directory.

**4. Key Not Detected**
```
❌ SSH key creation not detected properly
```
**Solution**: Check that the agent is returning the complete tool response.

### Debug Mode
To enable debug output, set the environment variable:
```bash
export DEBUG=1
python3 ssh_key_example.py
```

## Integration with Webapp

### Webapp Features
- **Real-time Chat**: Interactive chat interface for key creation
- **Download Buttons**: One-click download buttons in chat
- **Progress Tracking**: Real-time status updates
- **Error Handling**: Comprehensive error messages

### API Endpoints
- `GET /api/download-key/{key_id}` - Download SSH key
- `GET /api/key-info/{key_id}` - Get key information
- `WebSocket /ws/{user_id}` - Real-time chat communication

## Next Steps

1. **Test the Examples**: Run both examples to understand the workflow
2. **Set Up AWS**: Configure AWS credentials for real key creation
3. **Start Webapp**: Launch the webapp for interactive testing
4. **Create Keys**: Use the chat interface to create SSH keys
5. **Download Keys**: Use the download buttons to get your keys
6. **Use Keys**: Connect to EC2 instances using your SSH keys

## Support

If you encounter issues:
1. Check AWS credentials setup
2. Verify webapp is running
3. Review error messages for specific issues
4. Test with simulation mode first
5. Check file permissions and directory access

The examples are designed to be self-contained and provide comprehensive coverage of the SSH key creation and download functionality.
