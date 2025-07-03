docker save -o ragforge_deps.tar infiniflow/ragforge_deps:latest
docker save -o ragforge.tar infiniflow/ragforge:nightly
docker save -o mysql.tar mysql:8.0.39
docker save  -o  valkey.tar   valkey/valkey:8
docker save  -o  minio.tar quay.io/minio/minio:RELEASE.2023-12-20T01-00-02Z
docker save  -o  elasticsearch.tar  elasticsearch:8.11.3
docker save -o kes.tar minio/kes:v0.22.0
docker pull minio/kes:latest
docker save -o kes_new.tar minio/kes:latest
docker save -o vault.tar hashicorp/vault:1.15.5
docker pull hashicorp/vault:latest
docker save -o vault_new.tar hashicorp/vault:latest

##
#docker load -i ./ragforge_deps.tar 
#docker load -i ./ragforge.tar
#docker load -i ./mysql.tar
#docker load -i ./minio.tar
#docker load -i ./elasticsearch.tar
#docker load -i ./valkey.tar
#
