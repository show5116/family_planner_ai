import sys
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

def run_test():
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": settings.APP_API_KEY
    }
    
    # Test triggering 'macro' briefing
    payload = {
        "category": "macro"
    }
    
    print("------- API ROUTER TEST START -------")
    try:
        # with TestClient(app) as client triggers the lifespan events properly
        with TestClient(app) as client:
            print("Sending test POST request to /api/v1/market/trigger...")
            response = client.post("/api/v1/market/trigger", json=payload, headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response JSON: {response.json()}")
            
            if response.status_code == 200:
                print("API Endpoint Routing successfully configured. The payload was accepted.")
                sys.exit(0)
            else:
                print("Test FAILED: The payload was rejected or routing broke.")
                sys.exit(1)
                
    except Exception as e:
        print(f"Test FAILED with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
