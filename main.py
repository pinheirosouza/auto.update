import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading
import json

class ProgressPercentage(object):

    def __init__(self, bucketName, fileS3Path):
        self._bucketName = bucketName
        self._fileS3Path = fileS3Path
        self._size = s3_client.head_object(Bucket=self._bucketName, Key=self._fileS3Path)['ContentLength']
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._fileS3Path, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()




# VARIÁVEIS
bucketName = "auto.updater"
fileS3Path = 'update/config.json'
fileDownloadPath = 's3Config.json'
configPath = 'config.json'
selfUpdate = False

newDirectoryS3Path = 'update'
# /VARIÁVEIS


s3_client = boto3.client('s3')

progress = ProgressPercentage(bucketName, fileS3Path)

try:
    s3_client.download_file(bucketName, fileS3Path, fileDownloadPath,
    Callback=progress
)

except ClientError as err:
    logging.error(err)


# Testar se config.py está na pasta e se as versões coincidem
if os.path.isfile(configPath):
    with open(configPath) as json_file:
        localConfigObj = json.load(json_file)
    
    with open(fileDownloadPath) as json_file:
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

os.remove(fileDownloadPath)

if autoUpdate:
    print("\nFazer download, executar atualização, executar impressora")
else:
    print("\nExecutar Impressora")