import os
import json
import requests
from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
import dataclasses 
from dataclasses import dataclass



from dotenv import load_dotenv
from pathlib import Path
from query_agent import QueryAgent
from rag.config import EMBEDDING_DIMENSIONS, MAX_CONTEXT_LENGTHS
from model import Query, Answer

load_dotenv()

# Initialize application
app = FastAPI()


class RayAssistantAgent:
	def __init__(self, chunk_size, chunk_overlap, num_chunks, embedding_model_name, llm):
		# Query agent
		self.num_chunks = num_chunks
		system_content = "Answer the query using the context provided. Be succint."
		self.oss_agent = QueryAgent(llm=llm, max_context_length=MAX_CONTEXT_LENGTHS[llm], system_content=system_content)
            

	def query(self, query: str) -> str:
		agent = self.oss_agent 
		result = agent(query=query, num_chunks=self.num_chunks, stream=False)
		return json.dumps(result.__dict__)



@serve.deployment(route_prefix="/", num_replicas=1, ray_actor_options={"num_cpus": 1, "num_gpus": 1})
@serve.ingress(app)
class RayAssistantDeployment:
	def __init__(self, chunk_size, chunk_overlap, num_chunks, embedding_model_name, llm):
		self.agent = RayAssistantAgent(chunk_size, chunk_overlap, num_chunks, embedding_model_name, llm)

	@app.post("/query")
	def query(self, query: str) -> str:
		agent = self.agent.oss_agent 
		result = agent(query=query, num_chunks=self.agent.num_chunks, stream=False)
		return json.dumps(result.__dict__)



import ray
#ray.init(address="auto" )


NUM_CHUNKS=os.environ.get("NUM_CHUNKS", 5)
CHUNK_SIZE=os.environ.get("CHUNK_SIZE", 500)
CHUNK_OVERLAP=os.environ.get("CHUNK_OVERLAP", 50)
EMBEDDING_MODEL_NAME=os.environ.get("EMBEDDING_MODEL_NAME", "thenlper/gte-base")
LLM=os.environ.get("LLM_MODEL_NAME", "meta-llama/Llama-2-70b-chat-hf")
# Deploy the Ray Serve application.

deployment = RayAssistantDeployment.bind(
chunk_size=CHUNK_SIZE,
chunk_overlap=CHUNK_OVERLAP,
num_chunks=NUM_CHUNKS,
embedding_model_name=EMBEDDING_MODEL_NAME,
llm=LLM)
#serve.run(deployment)

"""
answer=RayAssistantDeployment(
chunk_size=CHUNK_SIZE,
chunk_overlap=CHUNK_OVERLAP,
num_chunks=NUM_CHUNKS,
embedding_model_name=EMBEDDING_MODEL_NAME,
llm=LLM
).query(query="batch size?")
print(answer)
"""
