#!/usr/bin/env python3
"""
Startup script for AI Triage Assistant
Handles different deployment modes and configurations
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config

def start_api_server(host: str = None, port: int = None, reload: bool = True):
    """start api server"""
    host = host or Config.API_HOST
    port = port or Config.API_PORT
    
    print(f"Starting API server on {host}:{port}")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "api.server:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

def start_langserve_server(host: str = None, port: int = None, reload: bool = True):
    """start langserve server"""
    host = host or Config.API_HOST
    port = port or Config.API_PORT
    
    print(f"Starting LangServe server on {host}:{port}")
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "deployment.langserve_deploy:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error starting LangServe server: {e}")
        sys.exit(1)

def start_docker_deployment():
    """start docker"""
    print("Starting Docker deployment...")
    
    docker_compose_file = project_root / "deployment" / "docker-compose.yml"
    
    if not docker_compose_file.exists():
        print("Docker compose file not found")
        sys.exit(1)
    
    try:
        subprocess.run([
            "docker-compose", "-f", str(docker_compose_file), "up", "-d"
        ], check=True)
        
        print("Docker deployment started successfully")
        print("Services available at:")
        print("  - API: http://localhost:8000")
        print("  - Dashboard: http://localhost:8000/dashboard")
        print("  - Grafana: http://localhost:3000")
        print("  - Prometheus: http://localhost:9090")
        
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker deployment: {e}")
        sys.exit(1)

def stop_docker_deployment():
    """stop docker"""
    print("Stopping Docker deployment...")
    
    docker_compose_file = project_root / "deployment" / "docker-compose.yml"
    
    try:
        subprocess.run([
            "docker-compose", "-f", str(docker_compose_file), "down"
        ], check=True)
        
        print("Docker deployment stopped successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error stopping Docker deployment: {e}")
        sys.exit(1)

def check_dependencies():
    """check dependencies"""
    print("Checking dependencies...")
    
    # Check Python packages
    required_packages = [
        "fastapi", "uvicorn", "langchain", "transformers", 
        "torch", "pandas", "numpy", "chromadb"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {missing_packages}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    # Check if model is available
    model_path = Path(Config.MODEL_CACHE_DIR)
    if not model_path.exists():
        print("Model cache directory not found. Run setup script first.")
        return False
    
    # Check if data directories exist
    data_path = Path(Config.MIMIC_DATA_PATH)
    if not data_path.exists():
        print("MIMIC data directory not found. RAG system may not work properly.")
    
    print("Dependencies check completed")
    return True

def show_status():
    """Show system status"""
    print("AI Triage Assistant Status")
    print("=" * 40)
    
    # Check configuration
    print(f"Model: {Config.MODEL_NAME}")
    print(f"API Host: {Config.API_HOST}")
    print(f"API Port: {Config.API_PORT}")
    print(f"Database: {Config.DATABASE_URL}")
    
    # Check directories
    directories = [
        Config.MODEL_CACHE_DIR,
        Config.VECTOR_DB_PATH,
        Config.MIMIC_DATA_PATH
    ]
    
    for directory in directories:
        path = Path(directory)
        status = "✓" if path.exists() else "✗"
        print(f"{status} {directory}")
    
    # Check environment variables
    env_vars = [
        "LANGCHAIN_API_KEY",
        "DATABASE_URL",
        "REDIS_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        print(f"{status} {var}: {'Set' if value else 'Not set'}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Triage Assistant Startup Script")
    parser.add_argument("mode", choices=["api", "langserve", "docker", "stop", "status"], 
                       help="Deployment mode")
    parser.add_argument("--host", default=Config.API_HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=Config.API_PORT, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    
    args = parser.parse_args()
    
    # Check dependencies unless skipped
    if not args.skip_deps and not check_dependencies():
        sys.exit(1)
    
    # Show status
    if args.mode == "status":
        show_status()
        return
    
    # Stop Docker deployment
    if args.mode == "stop":
        stop_docker_deployment()
        return
    
    # Start appropriate service
    if args.mode == "api":
        start_api_server(args.host, args.port, not args.no_reload)
    elif args.mode == "langserve":
        start_langserve_server(args.host, args.port, not args.no_reload)
    elif args.mode == "docker":
        start_docker_deployment()

if __name__ == "__main__":
    main()


