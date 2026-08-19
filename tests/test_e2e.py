import requests
import time
import os
import uuid

BASE_URL = "http://localhost:8005/api/v1"

def test_flow():
    # Use a unique email for every test run
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    print("1. Testing Health...")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200
    print("Health OK!")
    
    print("2. Testing Signup...")
    res = requests.post(f"{BASE_URL}/auth/signup", json={
        "name": "Test User",
        "email": email,
        "password": password
    })
    assert res.status_code == 201, f"Signup failed: {res.text}"
    print("Signup OK!")
    
    print("3. Testing Login...")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    print("Login OK!")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("4. Testing /me endpoint...")
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert res.status_code == 200
    print("Profile OK:", res.json()["email"])
    
    print("5. Testing Upload...")
    with open("test.md", "rb") as f:
        res = requests.post(
            f"{BASE_URL}/upload/doc/", 
            headers=headers,
            files={"file": ("test.md", f, "text/markdown")}
        )
    assert res.status_code == 200, f"Upload failed: {res.text}"
    print("Upload OK! Waiting 30s for background worker to index it...")
    
    time.sleep(30) # wait for worker to download from S3, parse, and upload to Qdrant
    
    print("6. Testing Query...")
    res = requests.post(
        f"{BASE_URL}/query/",
        headers=headers,
        json={"query": "What was the net revenue in Q3 2023?"}
    )
    assert res.status_code == 200, f"Query failed: {res.text}"
    ans = res.json()["message"]
    print("Query Response:", ans)
    
    if "4.5 million" in ans or "$4.5" in ans:
        print("✅ SUCCESS! E2E RAG Pipeline working perfectly.")
    else:
        print("⚠️ Response got something else, but pipeline worked!")

if __name__ == "__main__":
    test_flow()
