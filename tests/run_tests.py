import subprocess
import time
import requests
import os
import uuid
import sys

BASE_URL = "http://localhost:8006/api/v1"

def wait_for_server():
    for _ in range(30):
        try:
            r = requests.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                print("Server is up!")
                return True
        except:
            time.sleep(1)
    print("Server failed to start")
    return False

def test_flow():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    
    print("\n--- Testing Signup ---")
    res = requests.post(f"{BASE_URL}/auth/signup", json={
        "name": "Test User",
        "email": email,
        "password": password
    })
    print(res.text)
    assert res.status_code == 201
    
    print("\n--- Testing Login ---")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    print(res.text)
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Testing /me endpoint ---")
    res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(res.text)
    assert res.status_code == 200
    
    # Get the directory of this script to build absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "../app")
    test_file_path = os.path.join(script_dir, "test.md")

    print("\n--- Testing Upload ---")
    with open(test_file_path, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/upload/doc/", 
            headers=headers,
            files={"file": ("test.md", f, "text/markdown")}
        )
    print(res.text)
    assert res.status_code == 200
    
    print("\nWaiting 20 seconds for worker to process...")
    time.sleep(20)
    
    print("\n--- Testing Query ---")
    res = requests.post(
        f"{BASE_URL}/query/",
        headers=headers,
        json={"query": "What was the net revenue in Q3 2023?"}
    )
    print(res.text)
    assert res.status_code == 200
    
    print("\n✅ E2E TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "../app")
    
    env = os.environ.copy()
    env["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
    
    server_process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"],
        stdout=sys.stdout, stderr=sys.stderr, env=env, cwd=app_dir
    )
    
    worker_process = subprocess.Popen(
        ["rq", "worker", "documents", "-w", "rq.SimpleWorker"],
        stdout=sys.stdout, stderr=sys.stderr, env=env, cwd=app_dir
    )
    
    try:
        if wait_for_server():
            test_flow()
    finally:
        server_process.terminate()
        worker_process.terminate()
