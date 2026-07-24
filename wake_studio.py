import os
import base64
import time
import requests

LIGHTNING_USER_ID = os.environ.get("LIGHTNING_USER_ID", "").strip()
LIGHTNING_API_KEY = os.environ.get("LIGHTNING_API_KEY", "").strip()

if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
    try:
        with open("/tmp/lightning_user_id") as f:
            LIGHTNING_USER_ID = f.read().strip()
    except:
        pass
    try:
        with open("/tmp/lightning_api_key") as f:
            LIGHTNING_API_KEY = f.read().strip()
    except:
        pass

if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
    print("ERROR: No credentials found")
    exit(1)

STUDIO_ID = "01kw59txn0zjg816bff2x4r07k"
TEAMSPACE_ID = "01knbb9vda4z2m3c03apedr3ky"

credentials = f"{LIGHTNING_USER_ID}:{LIGHTNING_API_KEY}"
auth_value = f"Basic {base64.b64encode(credentials.encode()).decode()}"

headers = {
    "Authorization": auth_value,
    "Content-Type": "application/json",
}

start_url = f"https://lightning.ai/v1/projects/{TEAMSPACE_ID}/cloudspaces/{STUDIO_ID}/start"
status_url = f"https://lightning.ai/v1/projects/{TEAMSPACE_ID}/cloudspaces/{STUDIO_ID}"

def get_status():
    try:
        r = requests.get(status_url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("state", data.get("status", "unknown"))
        return f"http_{r.status_code}"
    except Exception as e:
        return f"error: {e}"

def start_studio():
    try:
        r = requests.post(start_url, headers=headers, json={
            "compute_config": {"name": "cpu_x_4", "spot": False}
        }, timeout=30)
        if r.status_code in (200, 201, 202):
            print(f"  Start command sent (HTTP {r.status_code})")
            return True
        elif r.status_code == 500 and "already" in r.text.lower():
            print(f"  Already running (HTTP 500)")
            return True
        else:
            print(f"  Start failed: HTTP {r.status_code} | {r.text[:150]}")
            return False
    except Exception as e:
        print(f"  Start error: {e}")
        return False

MAX_RETRIES = 3
RETRY_DELAY = 30

for attempt in range(1, MAX_RETRIES + 1):
    print(f"
Attempt {attempt}/{MAX_RETRIES}:")
    
    # Check current status first
    state = get_status()
    print(f"  Current state: {state}")
    
    if state in ("running", "started", "ready"):
        print("SUCCESS: Studio is already running")
        exit(0)
    
    # Try to start
    start_studio()
    
    if attempt < MAX_RETRIES:
        print(f"  Waiting {RETRY_DELAY}s before retry...")
        time.sleep(RETRY_DELAY)

# Final status check
state = get_status()
print(f"
Final state: {state}")
if state in ("running", "started", "ready"):
    print("SUCCESS: Studio is now running")
    exit(0)

print(f"DONE: Start command sent {MAX_RETRIES} times. Check studio status.")
exit(0)
