import requests

session = requests.Session()

print("--- TESTING AUTHENTICATION API ---")

# Register
print("\n[1] Registering a new AI tester account...")
resp = session.post("http://localhost:8000/api/register/", json={
    "name": "Automated Tester",
    "email": "autotest@example.com",
    "password": "securepassword123"
})
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

# Login
print("\n[2] Logging in to retrieve session cookie...")
resp = session.post("http://localhost:8000/api/login/", json={
    "email": "autotest@example.com",
    "password": "securepassword123"
})
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
print(f"Cookies Received: {session.cookies.get_dict()}")

# Get User
print("\n[3] Accessing protected /api/user/ endpoint...")
resp = session.get("http://localhost:8000/api/user/")
print(f"Status: {resp.status_code}")
print(f"Response (should identify autotest): {resp.text}")

# Logout
print("\n[4] Logging out and destroying session...")
resp = session.post("http://localhost:8000/api/logout/")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

# Get User Again (should fail)
print("\n[5] Accessing protected /api/user/ endpoint after logout...")
resp = session.get("http://localhost:8000/api/user/")
print(f"Status: {resp.status_code} (Expected 403 or 401)")

print("\n--- TEST COMPLETE ---")
