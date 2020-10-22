## Dockerize

Build
```
docker build --no-cache -t tsr:1.0.0 .
```

Execute
```
docker run \
-e IDRAC_HOST='10.75.139.154' \
-e IDRAC_PORT=22 \
-e IDRAC_USER='root' \
-e IDRAC_PASSWORD='' \
-e NFS_HOST=10.75.169.153 \
-e NFS_PATH=/home/ubuntu/nfs/shared \
-e KB_ID=100 \
tsr:1.0.0
```
