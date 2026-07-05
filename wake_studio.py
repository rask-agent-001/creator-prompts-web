import os
import lightning_sdk

user_id = os.environ.get("LIGHTNING_USER_ID", "")
api_key = os.environ.get("LIGHTNING_API_KEY", "")

os.environ["LIGHTNING_USER_ID"] = user_id
os.environ["LIGHTNING_API_KEY"] = api_key

# teamspace is the Lightning AI project/teamspace name
studio = lightning_sdk.Studio(name="hermes-1", teamspace="financial-llm-training-project")
print(f"Studio found: {studio.name} | Status: {studio.status}")
studio.start()
print("Studio wake command sent.")