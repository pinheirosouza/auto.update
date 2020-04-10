import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading
import json
import time

start = time.time()
class ProgressPercentage(object):

    def __init__(self, bucketName, configS3Path):
        self._bucketName = bucketName
        self._configS3Path = configS3Path
        self._size = s3_client.head_object(Bucket=self._bucketName, Key=self._configS3Path)['ContentLength']
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._configS3Path, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()




# VARIÁVEIS
bucketName = "auto.updater"
configS3Path = 'update/config.json'
configDownloadPath = 's3Config.json'
configPath = 'config.json'
selfUpdate = False

updaterS3Path = 'update/DS4Updater.exe'
updaterDownloadPath = 'DS4Updater.exe'
exe = "DS4Windows.exe"

ACCESS_ID = ''
S_ACCESS_ID = ''
# /VARIÁVEIS

with open(configPath) as json_file:
    credentials = json.load(json_file)
    ACCESS_ID = credentials["ACCESS_ID"]
    S_ACCESS_ID = credentials["S_ACCESS_ID"]

s3_client = boto3.client('s3', aws_access_key_id = ACCESS_ID, aws_secret_access_key = S_ACCESS_ID)

configDownloadProgress = ProgressPercentage(bucketName, configS3Path)

try:
    s3_client.download_file(bucketName, configS3Path, configDownloadPath,
    Callback=configDownloadProgress
)

except ClientError as err:
    logging.error(err)


# Testar se config.py está na pasta e se as versões coincidem
if os.path.isfile(configPath):
    with open(configPath) as json_file:
        localConfigObj = json.load(json_file)
    
    with open(configDownloadPath) as json_file:
        s3ConfigObj = json.load(json_file)
    
    if localConfigObj["APP_NAME"] == s3ConfigObj["APP_NAME"]:
        if localConfigObj["APP_VERSION"] == s3ConfigObj["APP_VERSION"]:
            autoUpdate = False
        else:
            autoUpdate = True
    else:
        autoUpdate = True

else:
    autoUpdate = True

os.remove(configDownloadPath)

if autoUpdate:
    updaterDownloadProgress = ProgressPercentage(bucketName, updaterS3Path)
    try:
        s3_client.download_file(bucketName, updaterS3Path, updaterDownloadPath,
        Callback=updaterDownloadProgress
    )
    except ClientError as err:
        logging.error(err)

    os.startfile(updaterDownloadPath)

else:
    os.startfile(exe)

end = time.time()

print("\nTempo de execução:", (end-start))