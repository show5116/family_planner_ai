import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get request ID from header or generate a new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Bind the request ID to the loguru context for this scope
        with logger.contextualize(request_id=request_id):
            logger.info(f"Incoming request: {request.method} {request.url.path}")
            
            response = await call_next(request)
            
            # Optionally attach the request ID to the response header
            response.headers["X-Request-ID"] = request_id
            
            logger.info(f"Completed request: {request.method} {request.url.path} - Status: {response.status_code}")
            return response
