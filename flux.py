# Install requests: pip install requests

import os
import requests

request = requests.post(
    'https://api.bfl.ai/v1/flux-2-pro-preview',
    headers={
        'accept': 'application/json',
        'x-key': os.getenv("BFL_API_KEY"),
        'Content-Type': 'application/json',
    },
    json={
        'prompt': 'A cat on its back legs running like a human is holding a big silver fish with its arms. The cat is running away from the shop owner and has a panicked look on his face. The scene is situated in a crowded market.',
        'width': 1440,
        'height': 2048
    },
).json()

print(request)
