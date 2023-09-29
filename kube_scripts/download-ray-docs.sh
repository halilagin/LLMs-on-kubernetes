export EFS_DIR=/tmp/raydocs
rm -rf $EFS_DIR && mkdir -p $EFS_DIR 
wget --quiet https://github.com/meddash-cloud/meddash-public-datasets/raw/main/archives/docs.ray.io.tar.gz -P $EFS_DIR
cd $EFS_DIR && tar xzf docs.ray.io.tar.gz && rm docs.ray.io.tar.gz 
