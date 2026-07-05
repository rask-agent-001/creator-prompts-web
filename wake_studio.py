import os
import base64
import requests

LIGHTNING_USER_ID = os.environ.get("LIGHTNING_USER_ID", "").strip()
LIGHTNING_API_KEY = os.environ.get("LIGHTNING_API_KEY", "").strip()

if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
    # Try reading from credential files
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
    print("ERROR: No credentials found - LIGHTNING_USER_ID and LIGHTNING_API_KEY are both empty")
    print(f"USER_ID length: {len(LIGHTNING_USER_ID)}")
    print(f"API_KEY length: {len(LIGHTNING_API_KEY)}")
    exit(1)

STUDIO_ID = "01kw59txn0zjg816bff2x4r07k"
TEAMSPACE_ID = "01knbb9vda4z2m3c03apedr3ky"

# Build Basic auth header
credentials = f"{LIGHTNING_USER_ID}:{LIGHTNING_API_KEY}"
auth_value = f"Basic {base64.b64encode(credentials.encode()).decode()}"

headers = {
    "Authorization": auth_value,
    "Content-Type": "application/json",
}

url = f"https://lightning.ai/v1/projects/{TEAMSPACE_ID}/cloudspaces/{STUDIO_ID}/start"

response = requests.post(url, headers=headers, json={
    "compute_config": {
        "name": "cpu_x_4",
        "spot": False
    }
})

if response.status_code in (200, 201, 202):
    print(f"SUCCESS: Studio start command sent (HTTP {response.status_code})")
elif response.status_code == 500 and "already has instances running" in response.text:
    print("SUCCESS: Studio is already running (HTTP 500: already running)")
elif response.status_code == 401:
    print(f"FAILED: Authentication error (401)")
    print(f"USER_ID: {LIGHTNING_USER_ID[:10]}...")
    print(f"Response: {response.text[:200]}")
    exit(1)
else:
    print(f"FAILED: HTTP {response.status_code} | {response.text[:200]}")
    exit(1)