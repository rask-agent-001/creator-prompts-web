import os
import base64
import warnings
warnings.filterwarnings('ignore')

from lightning_sdk.lightning_cloud.openapi import ApiClient, Configuration
from lightning_sdk.lightning_cloud.openapi.api.cloud_space_service_api import CloudSpaceServiceApi
from lightning_sdk.lightning_cloud.openapi.models import (
    CloudSpaceServiceStartCloudSpaceInstanceBody,
    V1UserRequestedComputeConfig,
)

LIGHTNING_USER_ID = os.environ.get("LIGHTNING_USER_ID", "")
LIGHTNING_API_KEY = os.environ.get("LIGHTNING_API_KEY", "")

STUDIO_ID = "01kw59txn0zjg816bff2x4r07k"
TEAMSPACE_ID = "01knbb9vda4z2m3c03apedr3ky"

# Build Basic auth header
credentials = f"{LIGHTNING_USER_ID}:{LIGHTNING_API_KEY}"
auth_value = f"Basic {base64.b64encode(credentials.encode()).decode()}"

# Create API client with explicit auth
config = Configuration()
config.host = "https://lightning.ai"
api_client = ApiClient(configuration=config)
api_client.set_default_header("Authorization", auth_value)

# Create the API
cloud_api = CloudSpaceServiceApi(api_client)

# Build the request
body = CloudSpaceServiceStartCloudSpaceInstanceBody(
    compute_config=V1UserRequestedComputeConfig(
        name="cpu_x_4",
        spot=False,
    )
)

# Call the start endpoint
try:
    result = cloud_api.cloud_space_service_start_cloud_space_instance(
        body,
        project_id=TEAMSPACE_ID,
        id=STUDIO_ID,
    )
    print(f"SUCCESS: Studio started")
except Exception as e:
    err_msg = str(e)
    if "already has instances running" in err_msg or "already running" in err_msg.lower():
        print("SUCCESS: Studio is already running")
    elif "401" in err_msg or "Unauthorized" in err_msg:
        print(f"FAILED: Authentication error - check LIGHTNING_USER_ID and LIGHTNING_API_KEY secrets")
        exit(1)
    else:
        print(f"Error: {err_msg[:200]}")
        exit(1)