# idrac-tsr-report

Usage
```
$ python setup.py install
$ tsr -h             
usage: run.py [-h] [-i IP] [-u USER] [-p PASSWD] [-n NFSHOST] [-a NFSPATH]
              [-k KBID]

get logs, wait, then upload it

optional arguments:
  -h, --help  show this help message and exit
  -i IP       IDRAC_HOST IP address
  -u USER     IDRAC_USER username
  -p PASSWD   IDRAC_PASSWORD password
  -n NFSHOST  NFS_HOST IP address
  -a NFSPATH  NFS_PATH /path/to/store
  -k KBID     KB_ID Kanboard id
```

Environment variables

```
export IDRAC_HOST=
export IDRAC_USER=
export IDRAC_PASSWORD=
export NFS_HOST=
export NFS_PATH=
export KB_ID=
export NOTIFY_API=
```

Create docker image

```
docker build --no-cache -f docker/Dockerfile -t tsr:1.0.0 .

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
