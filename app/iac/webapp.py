#!/usr/bin/env python3
"""
Web Application for Interactive IaC Agent
A chatbot interface for AWS EC2 instance management
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
import os
from datetime import datetime
from typing import Dict, List
import uuid

# Import our interactive agent wrapper
from agent_wrapper import interactive_agent


app = FastAPI(title="IaC Agent WebApp", description="Interactive AWS EC2 Management Chatbot")

# Templates directory
templates = Jinja2Templates(directory="templates")

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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

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


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the main chat page"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


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
        "content": "🤖 Hello! I'm your AWS EC2 management assistant. I can help you create, manage, and monitor EC2 instances. What would you like to do today?",
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
                    # Get response from the interactive agent wrapper
                    # Run the agent in a thread to avoid blocking
                    loop = asyncio.get_event_loop()
                    agent_response = await loop.run_in_executor(
                        None, 
                        lambda: interactive_agent(user_message)
                    )
                    
                    # Send agent response
                    response_message = {
                        "type": "message",
                        "role": "assistant",
                        "content": agent_response,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await manager.send_personal_message(json.dumps(response_message), websocket)
                    manager.add_to_history(user_id, "assistant", agent_response)
                    
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
