import tkinter as tk
from tkinter import ttk



def disable_event():
        pass

class UpdateProgressbar(tk.Tk):
    def __init__(self,*args, **kwargs):

        tk.Tk.__init__(self,*args, **kwargs)
        tk.Tk.geometry(self,'+%d+%d' % (500, 500))
        tk.Tk.wm_minsize(self, width=300,height=55)
        tk.Tk.overrideredirect(self, True)
        tk.Tk.protocol(self,"WM_DELETE_WINDOW", disable_event)

        self.label = ttk.Label(text = 'Aguarde. Estamos processando algumas atualizações')
        self.label.pack()

        self.var_aux = tk.IntVar()

        self.progress = ttk.Progressbar(
            self, orient = "horizontal",
            length = 200, mode = "determinate",
            variable = self.var_aux
            )

        self.progress.place(x = 50, y = 25)

        self.bytes = 0
        self.maxbytes = 0

    def start(self):

        self.maxbytes = 50000
        self.progress['maximum'] = self.maxbytes
        self.read_bytes()


    def read_bytes(self):

        self.bytes += 500
        self.var_aux.set(self.bytes)

        if self.bytes < self.maxbytes:
            self.after(100, self.read_bytes)

app = UpdateProgressbar()
app.mainloop()