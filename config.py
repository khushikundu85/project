import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Storage Configuration
    # If connection string is missing, files will be saved locally to LOCAL_UPLOADS_DIR
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME", "threat-scanner-uploads")
    
    # Path inside Docker container (mapped to VM volume)
    LOCAL_UPLOADS_DIR = os.getenv("LOCAL_UPLOADS_DIR", "data/uploads")

    # Local Database Configuration (SQLite)
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/scanner_audit.db")
    DATABASE_URL = f"sqlite:///./{DATABASE_PATH}"

    # Application Security
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-security-fallback-key-2024")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.zip', '.exe', '.jpg', '.png', '.py', '.js', '.sh'}

    @staticmethod
    def is_allowed_file(filename):
        return '.' in filename and \
               os.path.splitext(filename)[1].lower() in Config.ALLOWED_EXTENSIONS
