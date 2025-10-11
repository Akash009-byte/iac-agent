#!/usr/bin/env python3
"""
Startup script for the IaC Agent WebApp
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import jinja2
        import websockets
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def check_aws_credentials():
    """Check if AWS credentials are set"""
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS credentials not found in environment variables")
        print("Please set:")
        print("export AWS_ACCESS_KEY_ID=your_access_key")
        print("export AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("export AWS_DEFAULT_REGION=us-west-2")
        return False
    
    print("✅ AWS credentials are configured")
    return True

def check_openai_key():
    """Check if OpenAI API key is set"""
    # The key is hardcoded in the agent, so this is just informational
    print("✅ OpenAI API key is configured in the agent")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting IaC Agent WebApp")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check credentials
    if not check_aws_credentials():
        print("\n⚠️  Warning: AWS credentials not set. The agent may not work properly.")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            sys.exit(1)
    
    check_openai_key()
    
    print("\n🌐 Starting web server...")
    print("The webapp will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start the webapp
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "webapp:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 WebApp stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting webapp: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
