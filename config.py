"""
Configuration management for AI Triage Assistant
Centralized configuration with environment variable support
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration with environment variable support"""
    
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "ali009eng/llama-8b-mimic-ed-triage")
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./models")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "400"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
    MODEL_DEVICE = os.getenv("MODEL_DEVICE", "auto")  # auto, cuda, cpu
    
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triage_surveillance.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Data Paths
    MIMIC_DATA_PATH = os.getenv("MIMIC_DATA_PATH", "./data/mimic_iv_ed")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
    
    # MIMIC Dataset Tables
    MIMIC_TABLES = ["triage", "edstays", "vitalsign", "diagnosis", "medrecon", "pyxis"]
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_TITLE = os.getenv("API_TITLE", "AI Triage Assistant API")
    API_VERSION = os.getenv("API_VERSION", "1.0.0")
    API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # ESI Triage Levels
    ESI_LEVELS = {
        1: "Immediate - Life-threatening",
        2: "High Risk - Urgent", 
        3: "Medium - Stable but needs evaluation",
        4: "Lower Medium - Stable with minor issues",
        5: "Minor - Non-urgent"
    }
    
    # Surveillance Configuration
    SURVEILLANCE_WINDOW_HOURS = int(os.getenv("SURVEILLANCE_WINDOW_HOURS", "24"))
    OUTBREAK_THRESHOLD = float(os.getenv("OUTBREAK_THRESHOLD", "0.8"))
    CLUSTER_MIN_SIZE = int(os.getenv("CLUSTER_MIN_SIZE", "5"))
    TFIDF_MAX_FEATURES = int(os.getenv("TFIDF_MAX_FEATURES", "10000"))
    
    # Dashboard Configuration
    DASHBOARD_REFRESH_INTERVAL = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", "30"))
    MAX_PATIENTS_DISPLAY = int(os.getenv("MAX_PATIENTS_DISPLAY", "50"))
    
    # RAG Configuration
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))  # Number of similar cases to retrieve
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # LangChain Configuration
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "triage-assistant")
    LANGCHAIN_TRACING = os.getenv("LANGCHAIN_TRACING", "false").lower() == "true"
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-very-secret-key-here")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    ENABLE_AUTH = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Performance Configuration
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        directories = [
            cls.MODEL_CACHE_DIR,
            cls.VECTOR_DB_PATH,
            cls.MIMIC_DATA_PATH,
            cls.PROCESSED_DATA_PATH,
            "logs",
            "dashboard/static"
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)