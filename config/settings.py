import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # 방화벽 관련 설정
    FIREWALL_TIMEOUT = 30
    ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
    
    # 로깅 설정
    LOG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    
    # 임시 파일 저장 기간 (일)
    TEMP_FILE_DAYS = 7 