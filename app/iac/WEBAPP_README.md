# IaC Agent WebApp

A modern web application that provides a chatbot interface for AWS EC2 instance management using the Interactive Strands Agent.

## Features

- 🤖 **Real-time Chat Interface**: WebSocket-based communication with the IaC agent
- 💬 **Interactive Conversations**: Natural language interface for AWS EC2 management
- 🎨 **Modern UI**: Beautiful, responsive design with typing indicators and animations
- 📱 **Mobile Friendly**: Works on desktop and mobile devices
- 🔄 **Real-time Updates**: Live connection status and message delivery
- 📋 **Quick Actions**: Pre-built buttons for common operations
- 💾 **Session Management**: Persistent conversation history

## Screenshots

The webapp provides a clean, modern chat interface with:
- Gradient background and card-based design
- Real-time typing indicators
- Message timestamps
- Connection status indicator
- Quick action buttons
- Responsive layout for mobile devices

## Installation

### Prerequisites

1. **Python Dependencies**: Install required packages
```bash
pip install -r requirements.txt
```

2. **AWS Credentials**: Configure your AWS credentials
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-west-2"
```

3. **OpenAI API Key**: Already configured in the agent

### Quick Start

1. **Start the WebApp**:
```bash
python app/iac/start_webapp.py
```

2. **Open your browser** and go to:
```
http://localhost:8000
```

3. **Start chatting** with the IaC agent!

## Usage

### Basic Operations

The webapp provides a chatbot interface where you can:

- **Create EC2 Instances**: "Create a new EC2 instance"
- **List Instances**: "Show me my EC2 instances"
- **Manage Instances**: "Stop my web server", "Start my database instance"
- **Terminate Instances**: "Delete my old instance"
- **Get Information**: "What regions are available?", "Tell me about t3.small"

### Quick Actions

The interface includes quick action buttons for common operations:
- 📋 **List Instances** - Show all EC2 instances
- 🚀 **Create Instance** - Start the instance creation process
- 🌍 **Show Regions** - Display available AWS regions
- ❓ **Help** - Get assistance with AWS EC2

### Example Conversations

#### Creating an Instance
```
👤 You: Create a new EC2 instance
🤖 Agent: I'll help you create an EC2 instance! Let's start with the region. 
Which region would you like to use?

👤 You: us-west-2
🤖 Agent: Great choice! us-west-2 is perfect for web applications. 
Now, what type of instance do you need?

👤 You: t3.small
🤖 Agent: Excellent! t3.small is a great balance of performance and cost. 
What would you like to name your instance?

👤 You: MyWebServer
🤖 Agent: Perfect! Let me create your EC2 instance with these settings:
- Region: us-west-2
- Instance Type: t3.small
- Name: MyWebServer

Should I proceed with creating this instance?

👤 You: Yes
🤖 Agent: ✅ Successfully created EC2 instance!
Instance ID: i-1234567890abcdef0
Region: us-west-2
Instance Type: t3.small
Instance Name: MyWebServer
...
```

#### Managing Instances
```
👤 You: Show me my running instances
🤖 Agent: 📋 EC2 Instances in us-west-2:
- Instance ID: i-1234567890abcdef0
  Name: MyWebServer
  Type: t3.small
  State: running
  Public IP: 54.123.45.67
  Private IP: 10.0.1.123
  Launched: 2024-01-15 10:30:00

👤 You: Stop the MyWebServer instance
🤖 Agent: ✅ Successfully initiated stop of EC2 instance:
Instance ID: i-1234567890abcdef0
Name: MyWebServer
Region: us-west-2
Previous State: running
Current State: stopping

💡 Note: Stopped instances can be restarted later. You'll only be charged for storage.
```

## Architecture

### Components

1. **FastAPI Backend** (`webapp.py`):
   - WebSocket endpoint for real-time communication
   - REST API endpoints for health checks and session management
   - Integration with the Interactive Strands Agent

2. **Frontend** (`templates/chat.html`):
   - Modern HTML5/CSS3/JavaScript interface
   - WebSocket client for real-time communication
   - Responsive design with animations

3. **Interactive Agent** (`interactive_strands_agent.py`):
   - Strands-based conversational AI
   - AWS EC2 management tools
   - Natural language processing

### WebSocket Communication

The webapp uses WebSocket for real-time communication:

```javascript
// Client sends message
{
  "type": "message",
  "content": "Create an EC2 instance",
  "timestamp": "2024-01-15T10:30:00Z"
}

// Server responds
{
  "type": "message",
  "role": "assistant",
  "content": "I'll help you create an EC2 instance!",
  "timestamp": "2024-01-15T10:30:01Z"
}
```

### API Endpoints

- `GET /` - Main chat interface
- `GET /health` - Health check
- `GET /api/sessions` - Active user sessions
- `GET /api/history/{user_id}` - Conversation history
- `WebSocket /ws/{user_id}` - Real-time chat communication

## Configuration

### Environment Variables

```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_SESSION_TOKEN="your_session_token"  # Optional
export AWS_DEFAULT_REGION="us-west-2"

# OpenAI API Key (configured in agent)
# OPENAI_API_KEY="sk-..."  # Already set in code
```

### Customization

You can customize the webapp by modifying:

- **Styling**: Edit `templates/chat.html` CSS
- **Quick Actions**: Modify the quick action buttons
- **Agent Behavior**: Update `interactive_strands_agent.py`
- **Port**: Change the port in `start_webapp.py`

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**:
   - Check if the server is running
   - Verify firewall settings
   - Check browser console for errors

2. **AWS Credentials Error**:
   - Ensure credentials are set in environment
   - Verify credentials are valid
   - Check IAM permissions

3. **Agent Not Responding**:
   - Check OpenAI API key
   - Verify AWS region is correct
   - Check server logs for errors

### Debug Mode

Run with debug logging:
```bash
uvicorn webapp:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### Health Check

Check if the webapp is running:
```bash
curl http://localhost:8000/health
```

## Security Considerations

- **AWS Credentials**: Store securely, never commit to code
- **WebSocket**: Consider adding authentication for production
- **HTTPS**: Use HTTPS in production environments
- **Rate Limiting**: Implement rate limiting for production use

## Production Deployment

For production deployment:

1. **Use HTTPS**: Configure SSL certificates
2. **Environment Variables**: Use secure environment variable management
3. **Reverse Proxy**: Use Nginx or Apache as reverse proxy
4. **Process Manager**: Use PM2 or similar for process management
5. **Monitoring**: Add logging and monitoring
6. **Authentication**: Implement user authentication

Example Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Contributing

To contribute to the webapp:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the agent workspace and follows the same licensing terms.
