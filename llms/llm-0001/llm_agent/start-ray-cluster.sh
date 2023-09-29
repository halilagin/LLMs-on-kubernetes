set -a
source .env.kube
#ray start --head --num-cpus=1 --num-gpus=1
ray start --head --num-cpus=$NUM_CPUS --num-gpus=$NUM_GPUS
