import boto3
import logging
from botocore.exceptions import ClientError
import os
import sys
import threading
import json
from elevate import elevate
import tkinter
from tkinter import ttk
from tkinter import messagebox

class Updater():
    def __init__ (self, 
        # access_key_id:str,
        # s_access_key_id:str,
        # bucket_name:str,
        # config_s3_path:str,
        # exe_s3_path: str,

        # config_local_path: str = "config.json",
        exe_local_path: str = "anotaAIPrinter.exe",

        # config_download_path: str = "S3config.json",
        exe_download_path: str = "S3anotaAIPrinter.exe",
        ):

        self.__s3_client = boto3.client('s3')

        self._access_key_id = ""
        self._s_access_key_id = ""
        self._bucket_name = ""
        self._config_s3_path = ""
        self._exe_s3_path = ""

        
        self._config_local_path = os.getenv('LOCALAPPDATA') +'\\anotaAIPrinter\\config.json'
        self._exe_local_path = exe_local_path

        self._config_download_path = os.getenv('LOCALAPPDATA') +'\\anotaAIPrinter\\S3config.json'
        self._exe_download_path = exe_download_path
        
        self._local_version = ""
        self._s3_version = ""
        
        self.updated = True
    
    def checkUpdates(self, root):

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
            messagebox.showerror("Erro", "config.json não existe")
            print("config.json não existe")
            root.quit()
            os._exit(1)

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


        if self.updated:
            if os.path.isfile(self._exe_local_path):
                os.remove(self._config_download_path)
                os.startfile(self._exe_local_path)
                print('Done')
            else:
                without_exe_local = messagebox.showwarning("Arquivo não encontrado", "'anotaAIPrinter.exe não encontrado.' Baixaremos um novo executável para concluir as atualizações")
                self.updated = False

        if not self.updated:
            try:
                self._s3_client.download_file(
                    self._bucket_name, 
                    self._exe_s3_path, 
                    self._exe_download_path,
                )
            except ClientError as err:
                logging.error(err)
            
            os.system('taskkill /f /im "{}"'.format("anota AI Printer.exe"))
            
            # removendo arquivos antigos
            if os.path.isfile(self._exe_local_path):
                os.remove(self._exe_local_path)

            os.remove(self._config_local_path)

            # renomeando arquivos baixados
            os.rename(self._exe_download_path, self._exe_local_path)
            os.rename(self._config_download_path, self._config_local_path)

            # inicializando a nova versão da impressora
            os.startfile(self._exe_local_path)

            self.updated = True
            print('Done')

        root.quit()
        os._exit(1)    

def disable_window_butons():
    pass

def progressBar(root):
    root.geometry('+%d+%d' % (500,500))
    root.wm_minsize(width=300,height=55)
    label = ttk.Label(text = 'Aguarde. Estamos processando algumas atualizações')
    label.pack()
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("blue.Horizontal.TProgressbar", foreground='blue', background='blue')
    ft = ttk.Frame()
    ft.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
    pb_hD = ttk.Progressbar(ft, style="blue.Horizontal.TProgressbar", orient='horizontal', mode='determinate')
    pb_hD.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
    pb_hD.start(50)
    root.mainloop()

def start():
    root = tkinter.Tk()
    root.overrideredirect(True)
    root.protocol("WM_DELETE_WINDOW", disable_window_butons)
    updater = Updater()
    t1=threading.Thread(target=updater.checkUpdates, args=(root,))
    t1.start()
    progressBar(root)
    t1.join()
    

elevate()
start()