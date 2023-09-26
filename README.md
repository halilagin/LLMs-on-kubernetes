# Introduction

This repo presensts how you can fine tune an LLM on a scraped web site, in this example, ray.io, and serve it as a REST API. This codebase is highly influenced by the [Ray](http://ray.io) example  [here](https://www.anyscale.com/blog/a-comprehensive-guide-for-building-rag-based-llm-applications-part-1), so credits go to the Ray team!

The following explains each step of LLM fine tuning and serving it, i.e. from scraping a web page to serving the fine tuned LLM with Vector Database backed (PG Vector) as Rest API.



## Scrap the web page

You can scrap  the target web page with the script below

```bash
export EFS_DIR=/tmp/raydocs
wget --quiet -e robots=off --recursive --no-clobber --page-requisites \
  --html-extension --convert-links --restrict-file-names=windows \
  --domains docs.ray.io --no-parent --accept=html \
  -P $EFS_DIR https://docs.ray.io/en/master/
```

or just run the command below, which places the already scrapped content under `$EFS_DIR`

```bash
bash download-ray-docs.sh
```

## Setup PgSQL Database

You need to ahve a PGSQL Database supporting vector documents. This DB will be your Vector database for each chunk of word sequence in your training dataset. We need this to provide a global context to LLM. Vector DB basically provide you to search on vectors by doing cosine similarty between your query vector and the residing vecots in your db (i.e. each row is a vector, or a document.)

The YAML files in `yamls` directory provide you a ready Vector database on kubernetes. I would suggest you to install Microk8s and run the command below to have a VEctor DB ready.

```bash
microk8s.kubectl create -f yamls
```

The following listing presents a successful Postgresql cwserver installation on kubernetes

```bash
> k get pods -A
NAMESPACE     NAME                                      READY   STATUS    RESTARTS      AGE
kube-system   hostpath-provisioner-766849dd9d-tr55v     1/1     Running   1 (17h ago)   42h
kube-system   calico-kube-controllers-d8b9b6478-sjhfz   1/1     Running   1 (17h ago)   42h
kube-system   calico-node-xfw2z                         1/1     Running   1 (17h ago)   42h
kube-system   coredns-d489fb88-v9kr4                    1/1     Running   1 (17h ago)   42h
default       postgresdb-7d4c8f6974-qlh4n               1/1     Running   1 (17h ago)   42h
~/root/github/rag-ray-langchain-example
> k get svc
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
kubernetes   ClusterIP   10.152.183.1    <none>        443/TCP    42h
postgresdb   ClusterIP   10.152.183.81   <none>        5432/TCP   42h
```

Now, here is the last step, you need to be able to access the postgresql server. This can be achieved by port forwarding, so that you can you can access the DB from your local. Please run the command below in a separate terminal

```bash
bash postgres-port-forward.sh
```

Now, enable vector database support on Postgresql with the command below.

```bash
bash setup-pgvector.sh
```

now  your are ready to create your vector table. run the command below.

```bash
bash create-embedding-vector-table.sh
```

finally check if everythin alright. Run the command below

```bash
bash psql_cmd.sh '\d'
```

and see the result below

```bash

               List of relations
 Schema |      Name       |   Type   |  Owner
--------+-----------------+----------+----------
 public | document        | table    | testUser
 public | document_id_seq | sequence | testUser
(2 rows)
```


# Configure your LLM API 
As LLM agent we will use Scaleway and OpenAPI API gateways. Therefore, we need to setup the api keys and endpoints. the following lists the content of `llm_agent/.env`, which is our configuration file. Please set the API keys accordingly.

```bash

OPENAI_API_KEY=
ANYSCALE_API_KEY=
OPENAI_API_BASE="https://api.endpoints.anyscale.com/v1"
ANYSCALE_API_BASE="https://api.endpoints.anyscale.com/v1"
DB_CONNECTION_STRING="postgresql://testUser:testPassword@localhost:15432/testDB"
EMBEDDING_INDEX_DIR=/tmp/embedding_index_sql
VECTOR_TABLE_NAME=document
VECTOR_TABLE_DUMP_OUTPUT_PATH=/tmp/vector.document.dump.sql
RAYDOCS_ROOT=/tmp/raydocs
NUM_CPUS=14
NUM_GPUS=1
NUM_CHUNKS=5
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EMBEDDING_MODEL_NAME="thenlper/gte-base"
LLM_MODEL_NAME=meta-llama/Llama-2-70b-chat-hf
```

My machine has 16 CPUs and 1 GPU, so I set up `NUM_CPUS` and `NUM_GPUs` accordingly. These numbers may differ according to your machine. The principle here is that you can not set up a number larger than existing resources (CPU and GPU).

Pleae note that we are using `thenlper/gte-base` as an embedding model, this is a relatively small model, you might like to change it. `LLM_MODEL_NAME`is good for this setup, but again you might like to change it.


When we do fine tuning the code stores the each vector as a separate sql file under the directory `EMBEDDING_INDEX_DIR`. I would suggest you to backup this directory to avoid a second indexing of embedding (Just use the already produced one in your previous step).


# Fine tuning and populating your vector database

Here the core step: fine tuning and populating the vector db. First, Run the command below to install all python libraries.

```bash
pipenv install
```

then enter pipenv shell

```bash
pipenv shell
```
Now our python environment is ready. It means that we have Ray and LLM libraries installed.

Run the command below to start Ray cluster

```bash
bash start-ray-cluster.sh
```

The above command will rad `llm_agent/.env` and according to the CPU And GPU numbers, it will start an Ray Actor cluster.

Check if your cluster is running with the command below.

```bash
ray status
```

## Start fine tunning your LLM

If everything is alright, start fine tuning your LLM with the command below.

```bash
python main.py
```
At the end you will see something like below

```bash
The default batch size for map_batches is rollout_fragment_length * num_envs.
```
which indicates that LLM fine tuning is done, vector db is populated, and a query is sent to LLM with the context identified by your vector DB. Congrats!


## Serve LLM model

Now it is time to serve your LLM model as a REST API.

Run the command below and see the server is running on the port 8000
```bash
bash start-ray-serve.sh
```

The command below tests the LLM Rest API by sending a query (a question asking something about he batch size).

```bash
python test-query-llm.py
```
As a result you should see the answer of  your LLM agent. It should be something like below.

```bash
b'"{\\"question\\": \\"What is the default batch size for map_batches?\\", \\"sources\\": [\\"https://docs.ray.io/en/master/rllib/rllib-training.html#specifying-rollout-workers\\", \\"https://docs.ray.io/en/master/rllib/rllib-training.html#specifying-rollout-workers\\", \\"https://docs.ray.io/en/master/rllib/package_ref/doc/ray.rllib.policy.policy.Policy.compute_log_likelihoods.html#ray-rllib-policy-policy-policy-compute-log-likelihoods\\", \\"https://docs.ray.io/en/master/rllib/package_ref/doc/ray.rllib.policy.policy.Policy.compute_log_likelihoods.html#ray-rllib-policy-policy-policy-compute-log-likelihoods\\", \\"https://docs.ray.io/en/master/rllib/rllib-algorithms.html#importance-weighted-actor-learner-architecture-impala\\"], \\"answer\\": \\" The default batch size for map_batches is rollout_fragment_length * num_envs.\\", \\"llm\\": \\"meta-llama/Llama-2-70b-chat-hf\\"}"'

```


Congrats! You hvae fine-tuned and LLM on a scraped web site content, populated a vector db, served your fine tuned LLM as a REST API, and tested it successfully!



# Final note

don't forget to make `USE_THIS_PORTION_OF_DATA=1` when everything is working as expected. You did this experiement on 5% of your training data set, when you set `USE_THIS_PORTION_OF_DATA=1` in `llm_agent/.env` and rerun the process described above, you will have a fiend tuned model on 100% of your trainign dataset.
