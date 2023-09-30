
create_builder:
	docker buildx create --name mybuilder
use_builder:
	docker buildx use mybuilder

inspect_builder:
	docker buildx inspect --bootstrap


buildx64:
	#export DOCKER_DEFAULT_PLATFORM=linux/amd64
	export DOCKER_DEFAULT_PLATFORM=linux/aarch64
	#docker build -t halilagin/jupyter-rag-langchain:0.0.1  . --platform linux/arm64
	docker-compose build

buildx86:
	docker build -t halilagin/cuda-llm-runner:0.0.1  . 

build:
	echo =====================
	echo building for arm64. try 'make buildx86' for intel arch.
	echo =====================
	#docker buildx build  --platform linux/amd64,linux/arm64 .
	#docker buildx create --name=cuda-llm-runner  --platform linux/amd64,linux/arm64 
	docker buildx build  --platform linux/amd64,linux/arm64 -t halilagin/cuda-llm-runner:0.0.1 --push .

push:
	docker push halilagin/cuda-llm-runner:0.0.1
run:
	docker-compose up  -d
term:
	docker exec -it jupyter_notebook bash
dup: 
	export DOCKER_DEFAULT_PLATFORM=linux/amd64
	docker-compose up -d
down:
	docker-compose down
push_to_local:
	docker tag halilagin/cuda-llm-runner:0.0.1 localhost:32000/halilagin/cuda-llm-runner:0.0.1
	docker push localhost:32000/halilagin/cuda-llm-runner:0.0.1
:
