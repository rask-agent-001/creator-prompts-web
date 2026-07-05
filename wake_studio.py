import os
from lightning_sdk.studio import StudioApi
from lightning_sdk.machine import Machine

# StudioApi uses LIGHTNING_API_KEY env var for auth
# LIGHTNING_USER_ID env var is also read by the Auth class

STUDIO_ID = "01kw59txn0zjg816bff2x4r07k"
TEAMSPACE_ID = "01knbb9vda4z2m3c03apedr3ky"

api = StudioApi()
api.start_studio(
    studio_id=STUDIO_ID,
    teamspace_id=TEAMSPACE_ID,
    machine=Machine.CPU_X_4,
    interruptible=False,
)
print("Studio start command sent.")