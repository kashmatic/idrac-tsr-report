import os
import time
import logging
import argparse
from subprocess import Popen, PIPE
import paramiko
import requests
import json

logging.getLogger().setLevel('DEBUG')
logging.getLogger("paramiko").setLevel('INFO')
logging.basicConfig(format="%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")

TICKETS_URL = os.environ.get('NOTIFY_API')
ATTEMPTS = 10
WAITTIME = 60

def run_paramiko(hostname, username, password, cmd):
    logging.debug(cmd)
    with paramiko.SSHClient() as c:
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname=hostname, username=username, password=password)
        stdin, stdout, stderr = c.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
    if err:
        raise Exception(err)
    logging.debug(output)
    return output

def command_collect():
    return f'racadm techsupreport collect -t SysInfo,TTYLog'

def command_tsr(nfs_host, nfs_path):
    return f'racadm techsupreport export -l {nfs_host}:{nfs_path}'

def command_job_view(jobid):
    return f'racadm jobqueue view -i {jobid}'

def get_dict(astr):
    adict = {}
    for line in astr.split("\n"):
        if '=' not in line:
            continue
        key, value = line.split('=')
        adict[key.strip()] = value.strip()
    return adict

def job_loop(hostname, username, password, jobid):
    sleeptime = 10
    attempts = ATTEMPTS
    time.sleep(sleeptime)
    while True:
        output = run_paramiko(hostname, username, password, command_job_view(jobid))
        jobstatus = get_dict(output)
        logging.debug(f"++++ sleeptime: {sleeptime}, attempts: {attempts}, jobstatus: {jobstatus}")
        if jobstatus['Percent Complete'] == '[100]' \
        and (jobstatus['Status'] == 'Completed with Errors' \
        or jobstatus['Status'] == 'Completed'):
            break
        if jobstatus['Status'] == 'Failed':
            raise Exception(output)
            break
        else:
            time.sleep(WAITTIME)
        attempts -= 1
        if attempts == 0:
            raise Exception(f'Maximum number of attempts made. Last report {output}')
            break
    return jobstatus

def track_collect(args):
    logging.info(">>>>> Collect")
    output = run_paramiko(args.ip, args.user, args.passwd, command_collect())
    jobid = get_dict(output)
    jobstatus = job_loop(args.ip, args.user, args.passwd, jobid['Job ID'])
    logging.info("Collect <<<<<")
    return True

def track_export(args):
    logging.info(">>>>> Export")
    output = run_paramiko(args.ip, args.user, args.passwd, command_tsr(args.nfshost, args.nfspath))
    jobid = get_dict(output)
    jobstatus = job_loop(args.ip, args.user, args.passwd, jobid['Job ID'])
    logging.info("Export <<<<<")
    return True

def api_status(kbid, status):
    data = {
    "status": status,
    "id": kbid
    }
    headers = {'content-type': 'application/json'}
    if TICKETS_URL:
        r = requests.post(TICKETS_URL, data=json.dumps(data), headers=headers)
        logging.debug(r.status_code)
        logging.debug(r.text)
    else:
        logging.info("UPDATED")

def cli_args():
    """
    command line args definition
    """
    parser = argparse.ArgumentParser(description="get logs, wait, then upload it")
    parser.add_argument("-i", dest="ip", required=False, help="IDRAC_HOST IP address", default=os.environ.get('IDRAC_HOST', None))
    parser.add_argument("-u", dest="user", required=False, help="IDRAC_USER username", default=os.environ.get('IDRAC_USER', 'root'))
    parser.add_argument("-p", dest="passwd", required=False, help="IDRAC_PASSWORD password", default=os.environ.get('IDRAC_PASSWORD', None))
    parser.add_argument("-n", dest="nfshost", required=False, help="NFS_HOST IP address", default=os.environ.get('NFS_HOST', '10.75.169.153'))
    parser.add_argument("-a", dest="nfspath", required=False, help="NFS_PATH /path/to/store", default=os.environ.get('NFS_PATH', None))
    parser.add_argument("-k", dest="kbid", required=False, help="KB_ID Kanboard id", default=os.environ.get('KB_ID', None))
    args = parser.parse_args()
    return args

def app():
    ## collect command line args
    args = cli_args()
    logging.debug(args)
    try:
        track_collect(args)
        track_export(args)
        if args.kbid:
            api_status(args.kbid, 1)
    except Exception as e:
        if args.kbid:
            api_status(args.kbid, 0)
        raise(e)

if __name__ == '__main__':
    app()
