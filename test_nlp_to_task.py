import sys
import json
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

def run_test():
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": settings.APP_API_KEY
    }
    
    # Test payload referencing real user query
    payload = {
        "message": "이번 주 금요일까지 하민이 기저귀 쿠팡에서 주문하는 거 등록해 줘. 담당자는 아내로 지정해 주고, 수요일부터 알림 울리게 해.",
        "target_agent": "planner"
    }
    
    print("------- NLP TO TASK E2E TEST START -------")
    try:
        with TestClient(app) as client:
            print(f"User Input: {payload['message']}")
            print("Sending POST request to /api/v1/agent/chat...")
            
            response = client.post("/api/v1/agent/chat", json=payload, headers=headers)
            
            print(f"\nStatus Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n[AI Chat Response]")
                print(data.get("response", ""))
                print(f"\n[Extracted Plan JSON Payload]")
                
                plan_str = data.get("plan")
                if plan_str:
                    try:
                        parsed_plan = json.loads(plan_str)
                        print(json.dumps(parsed_plan, ensure_ascii=False, indent=2))
                    except:
                        print(plan_str)
                    print("\nTest PASSED: The JSON plan payload was correctly intercepted.")
                    sys.exit(0)
                else:
                    print("\nTest FAILED: The agent did not populate the 'plan' state payload.")
                    sys.exit(1)
            else:
                print(f"Test FAILED: Unhandled status code. Body: {response.text}")
                sys.exit(1)
                
    except Exception as e:
        print(f"Test FAILED with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
