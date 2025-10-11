#!/usr/bin/env python3
"""
Simple WebApp without external dependencies
A basic chatbot interface for demonstration
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
import os
from datetime import datetime
from typing import Dict, List

app = FastAPI(title="Simple IaC Agent WebApp", description="Basic AWS EC2 Management Chatbot")

# Templates directory - pointing to local templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[user_id] = {
            "websocket": websocket,
            "conversation_history": [],
            "created_at": datetime.now()
        }

    def disconnect(self, websocket: WebSocket, user_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def add_to_history(self, user_id: str, role: str, message: str):
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["conversation_history"].append({
                "role": role,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

    def get_history(self, user_id: str) -> List[Dict]:
        if user_id in self.user_sessions:
            return self.user_sessions[user_id]["conversation_history"]
        return []


manager = ConnectionManager()


def simple_agent_response(message: str) -> str:
    """Simple mock agent response"""
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "🤖 Hello! I'm your AWS EC2 management assistant. I can help you with basic EC2 operations. What would you like to do?"
    
    elif "ec2" in message_lower or "instance" in message_lower:
        return "🤖 I can help you with EC2 instances! Here are some things I can do:\n• List EC2 instances\n• Create new instances\n• Manage existing instances\n\nNote: This is a demo version. For full functionality, install the required dependencies (openai, strands)."
    
    elif "list" in message_lower:
        return "📋 Here's a demo list of EC2 instances:\n\n• Instance ID: i-1234567890abcdef0\n  Type: t2.micro\n  State: running\n  Public IP: 54.123.45.67\n\n• Instance ID: i-0987654321fedcba0\n  Type: t3.small\n  State: stopped\n  Public IP: N/A\n\nNote: This is demo data. Install dependencies for real AWS integration."
    
    elif "create" in message_lower:
        return "🚀 I can help you create EC2 instances! Here's what I need:\n\n1. Region (e.g., us-west-2)\n2. Instance type (e.g., t2.micro)\n3. Instance name\n\nNote: This is a demo. Install dependencies for real instance creation."
    
    elif "help" in message_lower:
        return "❓ I'm here to help! You can ask me about:\n\n• EC2 instances\n• AWS regions\n• Instance types\n• Creating instances\n• Managing instances\n\nNote: This is a demo version. For full functionality, install the required dependencies."
    
    else:
        return f"🤖 I received your message: '{message}'\n\nI'm a demo AWS EC2 assistant. To get full functionality, please install the required dependencies:\n\n```bash\npip install openai strands-agents\n```\n\nThen restart the server to access the full webapp!"


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the main chat page"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "mode": "demo"}


@app.get("/api/sessions")
async def get_active_sessions():
    """Get active user sessions"""
    sessions = {}
    for user_id, session_data in manager.user_sessions.items():
        sessions[user_id] = {
            "created_at": session_data["created_at"].isoformat(),
            "message_count": len(session_data["conversation_history"])
        }
    return {"active_sessions": len(sessions), "sessions": sessions}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for chat communication"""
    await manager.connect(websocket, user_id)
    
    # Send welcome message
    welcome_message = {
        "type": "message",
        "role": "assistant",
        "content": "🤖 Hello! I'm your AWS EC2 management assistant (Demo Mode). I can help you learn about EC2 operations. What would you like to know?",
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.send_personal_message(json.dumps(welcome_message), websocket)
    manager.add_to_history(user_id, "assistant", welcome_message["content"])
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":
                user_message = message_data["content"]
                
                # Add user message to history
                manager.add_to_history(user_id, "user", user_message)
                
                # Send typing indicator
                typing_message = {
                    "type": "typing",
                    "role": "assistant"
                }
                await manager.send_personal_message(json.dumps(typing_message), websocket)
                
                try:
                    # Get response from simple agent
                    agent_response_text = simple_agent_response(user_message)
                    
                    # Send agent response
                    response_message = {
                        "type": "message",
                        "role": "assistant",
                        "content": agent_response_text,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await manager.send_personal_message(json.dumps(response_message), websocket)
                    manager.add_to_history(user_id, "assistant", agent_response_text)
                    
                except Exception as e:
                    error_message = {
                        "type": "message",
                        "role": "assistant",
                        "content": f"❌ Sorry, I encountered an error: {str(e)}. Please try again.",
                        "timestamp": datetime.now().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(error_message), websocket)
                    manager.add_to_history(user_id, "assistant", error_message["content"])
            
            elif message_data["type"] == "ping":
                # Respond to ping with pong
                pong_message = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(pong_message), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


@app.get("/api/history/{user_id}")
async def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    history = manager.get_history(user_id)
    return {"user_id": user_id, "history": history}
