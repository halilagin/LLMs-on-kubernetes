import os
import ray

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

LLM=os.environ.get("LLM_MODEL_NAME", "meta-llama/Llama-2-70b-chat-hf")
OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ANYSCALE_API_KEY= os.environ["ANYSCALE_API_KEY"]
DB_CONNECTION_STRING=os.environ.get("DB_CONNECTION_STRING", "postgresql://testUser:testPassword@localhost:15432/testDB")
raydocs_root=os.environ.get("RAYDOCS_ROOT", "/tmp/raydocs")
num_cpus=int(os.environ.get("NUM_CPUS", 1))
num_gpus=int(os.environ.get("NUM_GPUS", 0))
num_chunks=int(os.environ.get("NUM_CHUNKS", 5))
USE_THIS_PORTION_OF_DATA=float(os.environ.get("USE_THIS_PORTION_OF_DATA", 0.01))
embedding_model_name = os.environ.get("EMBEDDING_MODEL_NAME", "thenlper/gte-base")


# Directories
EFS_DIR = Path(raydocs_root)
ROOT_DIR = Path(__file__).parent.parent.absolute()





import sys; 
import warnings; warnings.filterwarnings("ignore")
from dotenv import load_dotenv; load_dotenv()
import rag
from  query_agent import QueryAgent 

#ray.shutdown()
#ray_context = ray.init(ignore_reinit_error=True,num_cpus=num_cpus, num_gpus=num_gpus,runtime_env={
#        "env_vars": {
#                    "OPENAI_API_BASE": "",
#                            "OPENAI_API_KEY": OPENAI_API_KEY, 
#                                    # "ANYSCALE_API_BASE": os.environ["ANYSCALE_API_BASE"],
#                                            # "ANYSCALE_API_KEY": os.environ["ANYSCALE_API_KEY"],
#                                                    "DB_CONNECTION_STRING": DB_CONNECTION_STRING,
#                                                        },
#            "working_dir": str(ROOT_DIR),
#            })


from rag.config import EMBEDDING_DIMENSIONS, MAX_CONTEXT_LENGTHS

from pathlib import Path
from rag.config import EFS_DIR

EFS_DIR="/tmp/raydocs"

import os
import ray
# Ray dataset
DOCS_DIR = Path(EFS_DIR, "docs.ray.io/en/master/")
ds = ray.data.from_items([{"path": path} for path in DOCS_DIR.rglob("*.html") if not path.is_dir()])

print ("USE_THIS_PORTION_OF_DATA", USE_THIS_PORTION_OF_DATA)
print ("ds count", ds.count(), ds.count() * USE_THIS_PORTION_OF_DATA)
ds = ds.limit( int(ds.count() * USE_THIS_PORTION_OF_DATA) )
print(f"{ds.count()} documents")

import matplotlib.pyplot as plt
from rag.data import extract_sections



sample_html_fp = Path(EFS_DIR, "docs.ray.io/en/master/rllib/rllib-env.html")
extract_sections({"path": sample_html_fp})[0]



sections_ds = ds.flat_map(extract_sections)
sections_ds.count()



section_lengths = []
for section in sections_ds.take_all():
    section_lengths.append(len(section["text"]))







from functools import partial
from langchain.text_splitter import RecursiveCharacterTextSplitter



# Text splitter
chunk_size = 300
chunk_overlap = 50
text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
                chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                        length_function=len)







# Chunk a sample section
sample_section = sections_ds.take(1)[0]
chunks = text_splitter.create_documents(
            texts=[sample_section["text"]], 
                metadatas=[{"source": sample_section["source"]}])
print("=============================")
print("chunk[0] content:")
print (chunks[0])
print("=============================")









def chunk_section(section, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len)
    chunks = text_splitter.create_documents(
        texts=[section["text"]], 
        metadatas=[{"source": section["source"]}])
    return [{"text": chunk.page_content, "source": chunk.metadata["source"]} for chunk in chunks]



# Scale chunking
chunks_ds = sections_ds.flat_map(partial(
        chunk_section, 
            chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap))
print(f"{chunks_ds.count()} chunks")
chunks_ds.show(1)




from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import numpy as np
from ray.data import ActorPoolStrategy





class EmbedChunks:
    def __init__(self, model_name):
        if model_name == "text-embedding-ada-002":
            self.embedding_model = OpenAIEmbeddings(
                model=model_name,
                openai_api_base=OPENAI_API_BASE,
                openai_api_key=OPENAI_API_KEY)
        else:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"device": "cpu", "batch_size": 100})
    
    def __call__(self, batch):
        embeddings = self.embedding_model.embed_documents(batch["text"])
        return {"text": batch["text"], "source": batch["source"], "embeddings": embeddings}


# Embed chunks
embedded_chunks = chunks_ds.map_batches(
            EmbedChunks,
                fn_constructor_kwargs={"model_name": embedding_model_name},
                    batch_size=20, 
                        num_gpus=0.25,
                            compute=ActorPoolStrategy(size=2))




# Sample
sample = embedded_chunks.take(1)
print("======================")
print ("embedding size:", len(sample[0]["embeddings"]))
print (sample[0]["text"])
print("======================")


print("==========:::============")
print("finished")
print("==========:::============")



import psycopg2
from pgvector.psycopg2 import register_vector


import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str



class StoreResults:
    def __call__(self, batch):
        with psycopg2.connect(os.environ["DB_CONNECTION_STRING"]) as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                for text, source, embedding in zip(batch["text"], batch["source"], batch["embeddings"]):
                    sql_cmd="INSERT INTO document (text, source, embedding) VALUES ('%s', '%s', %s);" % (text, source, embedding)
                    file_path="%s/%s.sql" % (os.environ["EMBEDDING_INDEX_DIR"], get_random_string(64))
                    with open(file_path, "w") as f:
                        f.write(str(sql_cmd))
                        f.close()
                    cur.execute("INSERT INTO document (text, source, embedding) VALUES (%s, %s, %s)", (text, source, embedding,),)
        return {}


print("embedded_chunks.map_batches...")
os.makedirs(os.environ["EMBEDDING_INDEX_DIR"], exist_ok=True)
# Index data
embedded_chunks.map_batches(
StoreResults,
batch_size=20,
num_gpus=0.25,
compute=ActorPoolStrategy(size=2),
).count()








import json
import numpy as np
from rag.embed import get_embedding_model


print("get embedding model")
# Embed query
embedding_model = get_embedding_model(
    embedding_model_name=embedding_model_name, 
    model_kwargs={"device": "cuda"}, 
    encode_kwargs={"device": "cuda", "batch_size": 100})
query = "What is the default batch size for map_batches?"
embedding = np.array(embedding_model.embed_query(query))
print("=================")
print("embedding:")
len(embedding)
print("=================")




from query_agent import get_sources_and_context




num_chunks = os.environ.get("num_chunks", 5)
sources, context = get_sources_and_context(query, embedding_model, num_chunks)
for i, item in enumerate(context):
    print (sources[i])
    print (item["text"])
    print ("\n")




import openai
import time
from rag.generate import prepare_response
from rag.utils import get_credentials
from query_agent import  generate_response



query = "What is the default batch size for map_batches?"
response = generate_response(
            llm=os.environ["LLM_MODEL_NAME"],
                temperature=0.0,
                    stream=True,
                        system_content="Answer the query using the context provided. Be succinct.",
                            user_content=f"query: {query}, context: {context}")
# Stream response
for content in response:
    print(content, end='', flush=True)



query = "What is the default batch size for map_batches?"
system_content = "Answer the query using the context provided. Be succinct."
agent = QueryAgent(
            embedding_model_name=embedding_model_name,
                llm=LLM,
                    max_context_length=MAX_CONTEXT_LENGTHS[LLM],
                        system_content=system_content)
result = agent(query=query, stream=False)
print("\n\n", json.dumps(result, indent=2))


