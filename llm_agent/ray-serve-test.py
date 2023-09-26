import requests
from starlette.requests import Request
from typing import Dict
import ray
from ray import serve


# 1: Define a Ray Serve application.
@serve.deployment(route_prefix="/")
class MyModelDeployment:
    def __init__(self, msg: str):
        # Initialize model state: could be very large neural net weights.
        self._msg = msg

    def __call__(self, request: Request) -> Dict:
        return {"result": self._msg}

ray.init(address="auto")

app = MyModelDeployment.bind(msg="Hello world!")

serve.run(app)

print(requests.get("http://localhost:8000/").json())
