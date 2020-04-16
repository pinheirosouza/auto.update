import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
from threading import Thread
import json
import ctypes
import elevate
import tkinter as tk
from tkinter import ttk

class Updater():
    def __init__ (self, 
        # access_key_id:str,
        # s_access_key_id:str,
        # bucket_name:str,
        # config_s3_path:str,
        # exe_s3_path: str,

        config_local_path: str = "config.json",
        exe_local_path: str = "anotaAIPrinter.exe",

        config_download_path: str = "S3config.json",
        exe_download_path: str = "S3anotaAIPrinter.exe",
        ):

        self.__s3_client = boto3.client('s3')

        self._access_key_id = ""
        self._s_access_key_id = ""
        self._bucket_name = ""
        self._config_s3_path = ""
        self._exe_s3_path = ""

        
        self._config_local_path = os.getenv('LOCALAPPDATA') +'\\tempteste\\config.json'
        self._exe_local_path = exe_local_path

        self._config_download_path = config_download_path
        self._exe_download_path = exe_download_path
        
        self._local_version = ""
        self._s3_version = ""
        
        self.updated = True
    
    def checkUpdates(self):

        if os.path.isfile(self._config_local_path):
            with open(self._config_local_path) as json_file:
                config_local_obj = json.load(json_file)
                self._access_key_id = config_local_obj["ACCESS_ID"]
                self._s_access_key_id = config_local_obj["S_ACCESS_ID"]
                self._bucket_name = config_local_obj["BUCKET_NAME"]
                self._config_s3_path = config_local_obj["CONFIG_S3_PATH"]
                self._exe_s3_path = config_local_obj["EXE_S3_PATH"]
                self._local_version = config_local_obj["APP_VERSION"]
        else:
            # important
            print("Mensagem mandando entrar em contato com o suporte por falta do config.py")

        self._s3_client = boto3.client(
            's3', 
            aws_access_key_id = self._access_key_id, 
            aws_secret_access_key = self._s_access_key_id
        )

        try:
            self._s3_client.download_file(
                self._bucket_name, 
                self._config_s3_path, 
                self._config_download_path
            )
        except ClientError as err:
            logging.error(err)

        with open(self._config_download_path) as json_file:
            config_s3_obj = json.load(json_file)
            self._s3_version = config_s3_obj["APP_VERSION"]

        if self._s3_version != self._local_version:
            self.updated = False

        os.remove(self._config_download_path)

        if self.updated:
            os.startfile(self._exe_local_path)
        else:
            update()
        
        return self.updated

    def update(self):
        try:
            self._s3_client.download_file(
                self._bucket_name, 
                self._exe_s3_path, 
                self._exe_download_path,
            )
        except ClientError as err:
            logging.error(err)
        
        os.system('taskkill /f /im "{}"'.format("anota AI Printer.exe"))
        
        # removendo antigo
        os.remove(self._exe_local_path)

        # renomeando arquivo baixado
        os.rename(self._exe_download_path, self._exe_local_path)

        # inicializando a nova versão da impressora
        os.startfile(self._exe_local_path)

        self.updated = True

elevate.elevate()

updater = Updater()

# fazer a thread
update_status = updater.checkUpdates()

if update_status:
    print("Atualizado com sucesso")
else:
    print("Ocorreu um erro")