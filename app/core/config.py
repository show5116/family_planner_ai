from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Family Planner AI"
    API_V1_STR: str = "/api/v1"
    # OPENAI_API_KEY will be read from environment automatically
    
    class Config:
        env_file = ".env"

settings = Settings()
