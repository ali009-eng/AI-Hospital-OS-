#!/usr/bin/env python3
"""
Setup script for AI Triage Assistant
Initializes the system, downloads models, and sets up the database
"""
import os
import sys
import argparse
from pathlib import Path
import subprocess
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from data_processing.mimic_processor import MIMICProcessor
from surveillance.syndromic_surveillance import SyndromicSurveillanceSystem


def create_directories():
    """create directories"""
    print("Creating project directories...")
    
    directories = [
        Config.MODEL_CACHE_DIR,
        Config.VECTOR_DB_PATH,
        Config.MIMIC_DATA_PATH,
        "data/processed",
        "logs",
        "dashboard/static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_environment():
    """setup environment"""
    print("Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from template")
        print("Please update .env file with your actual configuration values")
    elif not env_file.exists():
        print("No .env file found. Please create one based on env.example")

def download_model():
    """download model"""
    print("Downloading fine-tuned model...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = Config.MODEL_NAME
        cache_dir = Config.MODEL_CACHE_DIR
        
        print(f"Downloading model: {model_name}")
        
        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        
        # Download model
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype="auto",
            trust_remote_code=True
        )
        
        print("Model downloaded successfully")
        
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Model download failed. Please ensure you have access to the model and sufficient disk space.")

def setup_database():
    """setup database"""
    print("Setting up surveillance database...")
    
    try:
        surveillance = SyndromicSurveillanceSystem()
        surveillance.initialize()
        print("Surveillance database initialized successfully")
    except Exception as e:
        print(f"Error setting up database: {e}")

def process_mimic_data():
    """process mimic data"""
    print("Checking for MIMIC-IV-ED dataset...")
    
    mimic_path = Path(Config.MIMIC_DATA_PATH)
    
    if not mimic_path.exists():
        print(f"MIMIC-IV-ED dataset not found at {mimic_path}")
        print("Please download the MIMIC-IV-ED dataset and place it in the data/mimic_iv_ed directory")
        print("The dataset should contain the following tables:")
        for table in Config.MIMIC_TABLES:
            print(f"  - {table}.csv")
        return
    
    # Check if required tables exist
    required_tables = [f"{table}.csv" for table in Config.MIMIC_TABLES]
    missing_tables = []
    
    for table in required_tables:
        if not (mimic_path / table).exists():
            missing_tables.append(table)
    
    if missing_tables:
        print(f"Missing MIMIC-IV-ED tables: {missing_tables}")
        print("Please ensure all required tables are present before processing")
        return
    
    try:
        print("Processing MIMIC-IV-ED dataset...")
        processor = MIMICProcessor()
        processor.process_dataset()
        print("MIMIC-IV-ED dataset processed successfully")
    except Exception as e:
        print(f"Error processing MIMIC-IV-ED dataset: {e}")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def run_tests():
    """Run basic tests to verify setup"""
    print("Running basic tests...")
    
    try:
        # Test imports
        from rag.rag_system import RAGSystem
        from surveillance.syndromic_surveillance import SyndromicSurveillanceSystem
        from langchain_integration.triage_agent import TriageAgent
        
        print("All imports successful")
        
        # Test basic functionality
        surveillance = SyndromicSurveillanceSystem()
        print("Surveillance system test passed")
        
        print("Basic tests completed successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup AI Triage Assistant")
    parser.add_argument("--skip-model", action="store_true", help="Skip model download")
    parser.add_argument("--skip-mimic", action="store_true", help="Skip MIMIC data processing")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--test-only", action="store_true", help="Run tests only")
    
    args = parser.parse_args()
    
    print("Starting AI Triage Assistant setup...")
    
    try:
        # Create directories
        create_directories()
        
        # Setup environment
        setup_environment()
        
        if not args.test_only:
            # Install dependencies
            if not args.skip_deps:
                install_dependencies()
            
            # Download model
            if not args.skip_model:
                download_model()
            
            # Setup database
            setup_database()
            
            # Process MIMIC data
            if not args.skip_mimic:
                process_mimic_data()
        
        # Run tests
        run_tests()
        
        print("Setup completed successfully!")
        print("You can now start the application with: python -m uvicorn api.server:app --reload")
        
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


