from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Family Planner AI"
    API_V1_STR: str = "/api/v1"
    APP_API_KEY: str = "change_me_to_a_secure_random_string_in_production"
    # OPENAI_API_KEY/GEMINI_API_KEY 등은 환경 변수에서 자동으로 읽어옵니다.
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
