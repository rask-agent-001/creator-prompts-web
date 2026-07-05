import os
import lightning_sdk

os.environ['LIGHTNING_USER_ID'] = os.environ.get('LIGHTNING_USER_ID', '')
os.environ['LIGHTNING_API_KEY'] = os.environ.get('LIGHTNING_API_KEY', '')

studio = lightning_sdk.Studio(name='hermes-1')
studio.start()
print('Studio wake command sent.')