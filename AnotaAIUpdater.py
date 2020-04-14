import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading
import json
import ctypes
import elevate

class Updater():
    # bucketName = Nome do bucket no S3;    
    def __init__(self, bucketName, access_key, s_access_key):
        self._bucketName = bucketName
        self._s3_client = boto3.client(
            's3', 
            aws_access_key_id = access_key, 
            aws_secret_access_key = s_access_key
        )

    # configS3Path = Caminho do config no S3; configDownloadPath = Onde o config será salvo; 
    # configLocalPath = Onde o config local está armazenado;
    def checkNewUpdates(self, configS3Path, configDownloadPath, configLocalPath):
        try:
            self._s3_client.download_file(self._bucketName, configS3Path, configDownloadPath,
        )

        except ClientError as err:
            logging.error(err)


        # Testar se config.py está na pasta e se as versões coincidem
        if os.path.isfile(configLocalPath):
            with open(configLocalPath) as json_file:
                localConfigObj = json.load(json_file)
            
            with open(configDownloadPath) as json_file:
                s3ConfigObj = json.load(json_file)
            
            if localConfigObj["APP_NAME"] == s3ConfigObj["APP_NAME"]:
                if localConfigObj["APP_VERSION"] == s3ConfigObj["APP_VERSION"]:
                    doUpdate = False
                else:
                    doUpdate = True
            else:
                doUpdate = True

        else:
            doUpdate = True
        os.remove(configDownloadPath)

        return doUpdate

    
    def update(self, exeS3Path, exeDownloadPath, exeLocalPath, processToKill):
        try:
            self._s3_client.download_file(self._bucketName, exeS3Path, exeDownloadPath,
        )

        except ClientError as err:
            logging.error(err)
        
        for n in processToKill:
            os.system("taskkill /f /im " + n)
        
        # removendo antigo
        os.remove(exeLocalPath)

        # renomeando arquivo baixado
        os.rename(exeDownloadPath, exeLocalPath)

        # inicializando a nova versão da impressora
        os.startfile(exeLocalPath)



# VARIÁVEIS
bucketName = 'auto.updater'
configS3Path = 'update/config.json'
configDownloadPath = 's3Config.json'
configLocalPath = os.getenv('LOCALAPPDATA')+'\\tempteste\\config.json'
update = False

exeS3Path = 'update/DS4Updater.exe'
exeDownloadPath = 'S3DS4Windows.exe'
exeLocalPath = 'DS4Windows.exe'
processToKill = ["DS4Windows.exe"]

ACCESS_ID = ''
S_ACCESS_ID = ''
# /VARIÁVEIS

def main():
    with open(configLocalPath) as json_file:
        credentials = json.load(json_file)
        ACCESS_ID = credentials["ACCESS_ID"]
        S_ACCESS_ID = credentials["S_ACCESS_ID"]

    updater = Updater("auto.updater", ACCESS_ID, S_ACCESS_ID)

    doUpdate = updater.checkNewUpdates(configS3Path, configDownloadPath, configLocalPath)

    if (doUpdate == False):
        os.startfile(exeLocalPath)

    else:
        updater.update(exeS3Path, exeDownloadPath, exeLocalPath, processToKill)

# todos os privilégios:
# elevate.elevate()
main()