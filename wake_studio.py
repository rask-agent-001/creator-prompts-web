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

credentials = LIGHTNING_USER_ID + ":" + LIGHTNING_API_KEY
auth_value = "Basic " + base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": auth_value,
    "Content-Type": "application/json",
}

start_url = "https://lightning.ai/v1/projects/" + TEAMSPACE_ID + "/cloudspaces/" + STUDIO_ID + "/start"
status_url = "https://lightning.ai/v1/projects/" + TEAMSPACE_ID + "/cloudspaces/" + STUDIO_ID


def get_status():
    try:
        r = requests.get(status_url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("state", data.get("status", "unknown"))
        return "http_" + str(r.status_code)
    except Exception as e:
        return "error: " + str(e)


def start_studio():
    try:
        r = requests.post(start_url, headers=headers, json={
            "compute_config": {"name": "cpu_x_4", "spot": False}
        }, timeout=30)
        print("  HTTP " + str(r.status_code) + " | " + r.text[:150])
    except Exception as e:
        print("  Error: " + str(e))


# 3 unconditional starts, 60s apart
for attempt in range(1, 4):
    print("")
    print("Attempt " + str(attempt) + "/3 (unconditional start):")
    start_studio()
    if attempt < 3:
        print("  Waiting 60s...")
        time.sleep(60)

# 2 check + start, 90s apart
for attempt in range(1, 3):
    print("")
    print("Attempt " + str(attempt + 3) + "/5 (check + start):")

    state = get_status()
    print("  Status: " + str(state))

    if state in ("running", "started", "ready"):
        print("SUCCESS: Studio is running")
        exit(0)

    print("  Not running — sending start...")
    start_studio()

    if attempt < 2:
        print("  Waiting 90s...")
        time.sleep(90)

# Final check
state = get_status()
print("")
print("Final status: " + str(state))
if state in ("running", "started", "ready"):
    print("SUCCESS: Studio is running")
else:
    print("DONE: 5 start commands sent. Studio may still be waking up.")
