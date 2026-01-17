import requests
import json

def test_login_flow():
    base_url = "http://localhost:8000"
    client = requests.Session()

    # 1. Login
    print("--- 1. Attempting Login ---")
    login_url = f"{base_url}/api/login/"
    login_data = {"username": "admin", "password": "yourpassword"}
    
    try:
        response = client.post(login_url, json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        print(f"Cookies: {client.cookies.get_dict()}")
        
        if response.status_code != 200:
            print("Login failed, aborting.")
            return
    except Exception as e:
        print(f"Login Error: {e}")
        return

    # 2. Check Auth Status (Who Am I)
    print("\n--- 2. Checking Auth Status (Who Am I) ---")
    whoami_url = f"{base_url}/api/whoami/"
    try:
        response = client.get(whoami_url)
        print(f"WhoAmI Status: {response.status_code}")
        print(f"WhoAmI Response: {response.text}")
    except Exception as e:
        print(f"WhoAmI Error: {e}")

    # 3. Test Create Session Access
    print("\n--- 3. Testing Create Session Access ---")
    create_url = f"{base_url}/api/sessoes/criar/"
    try:
        # GET request to check access (should be allowed now)
        response = client.get(create_url)
        print(f"Create Session (GET) Status: {response.status_code}")
        print(f"Create Session (GET) Response: {response.text}")
    except Exception as e:
        print(f"Create Session Error: {e}")

    # 4. Test Create Sale Auth
    print("\n--- 4. Testing Create Sale Auth ---")
    create_sale_url = f"{base_url}/api/vendas/criar/"
    try:
        # We send empty data, expecting 400 Bad Request if Auth passes, or 403 if Auth fails
        response = client.post(create_sale_url, json={})
        print(f"Create Sale Status: {response.status_code}")
        print(f"Create Sale Response: {response.text}")
    except Exception as e:
        print(f"Create Sale Error: {e}")

if __name__ == "__main__":
    test_login_flow()
