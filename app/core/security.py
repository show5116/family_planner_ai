from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings
from loguru import logger

# define the API Key header scheme. We look for the "X-API-Key" header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency function to verify the API key provided in the request headers.
    """
    if not api_key:
        logger.warning("API Key missing in request headers.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing in request headers.",
        )
        
    if api_key != settings.APP_API_KEY:
        logger.warning("Invalid API Key provided.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate API Key",
        )
        
    return api_key
