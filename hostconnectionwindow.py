import customtkinter as ctk
from tkinter import ttk
import pickle
import paramiko

class TableData():
    def __init__(self):
        self.data = []

    def ReadData(self, table):
        return self.data

    def WriteData(self, table):
        iids = table.get_children()
        data = [table.item(iid, "values") for iid in iids]
        self.data = data

class HostConnectionWindow():
    def __init__(self, root, title, geometry, fg_color, main_application):
        self.root = root
        self.top_level = ctk.CTkToplevel(root, fg_color=fg_color)
        self.top_level.title(title)
        self.top_level.geometry(geometry)
        self.top_level.protocol("WM_DELETE_WINDOW", lambda : self.OnWindowExit())
        self.main_application = main_application

        self.selected_item = None
        self.table = None
        self.tabledata = None
        self.LoadTableData()

        self.status_label = None

        self.client = None

        self.config_display = None

        self.connection_return = None

        self.status = 0

        self.DrawGUI()

    def DrawGUI(self):
        self.DrawTitleAndInfo()
        self.DrawLoginConfig()
        self.DrawOptions()
        self.DrawStatus()

    def DrawTitleAndInfo(self):
        frame = ctk.CTkFrame(self.top_level)
        frame.place(anchor = "n", relx = 0.5, rely = 0, relheight = 0.2, relwidth = 1)

        title = ctk.CTkLabel(frame, text = "Host Connection Manager", font = ("system", 40))
        title.place(anchor = "n", relx = 0.5, rely = 0)

        info = ctk.CTkLabel(frame, text = "Select a config to use for SSH. then connect via the button.\nThe Status window will show useful info about the process as well as any errors.", font = ("system", 11))
        info.place(anchor = "s", relx = 0.5, rely = 1)

    def DrawLoginConfig(self):
        frame = ctk.CTkFrame(self.top_level)
        frame.place(anchor = "sw", relx = 0, rely = 1, relheight = 0.7, relwidth = 0.45) 
        
        columns = ("host", "user", "port", "password")
        
        table = ttk.Treeview(frame, columns=columns, show = "headings", selectmode="browse")

        table.heading('host', text = "Host")
        table.heading('user', text = "User")
        table.heading('port', text = "Port")

        table.column('host', minwidth = 0, width = 90)
        table.column('user', minwidth = 0, width = 90)
        table.column('port', minwidth = 0, width = 90)

        table.pack(expand = "yes", fill = "both")

        table.bind('<<TreeviewSelect>>', self.item_selected)

        try:
            for data in self.tabledata.data:
                table.insert("", "end", values = data)
        except:
            pass
        
        if(len(table.get_children()) == 0):
            pass
        elif(len(table.get_children()) == 1):
            table.selection_add(table.get_children())
        else:
            table.selection_add(table.get_children()[0])

        self.table = table

    def DrawOptions(self):
        frame = ctk.CTkFrame(self.top_level)
        frame.place(anchor = "s", relx = 0.55, rely = 0.8, relheight = 0.3, relwidth = 0.15)

        connect_button = ctk.CTkButton(frame, text = "Connect", command = lambda : self.ConnectWithConfig())
        connect_button.place(anchor = "center", relx = 0.5, rely = 0.33, relwidth = 0.8, relheight = 0.3)

        disconnect_button = ctk.CTkButton(frame, text = "Disconnect", command = lambda : self.Disconnect())
        disconnect_button.place(anchor = "center", relx = 0.5, rely = 0.66, relwidth = 0.8, relheight = 0.3)

    def DrawStatus(self):
        frame = ctk.CTkFrame(self.top_level)
        frame.place(anchor = "se", relx = 1, rely = 1, relheight = 0.7, relwidth = 0.3)

        connection_status = ctk.CTkLabel(frame, text = "Disconnected", font = ("system", 30), text_color = "#ff6961")
        connection_status.place(anchor = "n", relx = 0.5, rely = 0, relwidth = 0.8, relheight = 0.15)

        self.status_label = connection_status

        config = ctk.CTkLabel(frame, text = "Config Information", font=("system", 15))
        config.place(anchor = "n", relx = 0.5, rely = 0.2, relwidth = 0.8, relheight = 0.2)

        self.config_display = config

        connection_return = ctk.CTkTextbox(frame)
        connection_return.insert(0.0, "")
        connection_return.place(anchor = "center", relx = 0.5, rely = 0.7, relheight = 0.5, relwidth = 0.9)

        self.connection_return = connection_return

        self.SetStatus(self.status)

    def GetPassword(self):
        input_dialogue = ctk.CTkInputDialog(text = "Enter Password", title = "Password Verification")
        text = input_dialogue.get_input()
        return text

    def item_selected(self, event):
        self.selected_item = self.table.selection()[0]

    def LoadTableData(self):
        try:
            with open("table.pickle", "rb") as f:
                tabledata = pickle.load(f)
                self.tabledata = tabledata
        
        except Exception as ex:
            return TableData()

    def ConnectWithConfig(self):
        if self.selected_item == None:
            return
        
        (host, user, port) = self.table.item(self.selected_item, "values")
        ssh_client = paramiko.client.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        password = self.GetPassword()

        try:
            connected = ssh_client.connect(hostname=host, username=user, port=port, password=password)
        except Exception as exception:
            connected = f"{type(exception).__name__}, -{exception}"



        self.connection_return.delete(0.0, ctk.END)
        self.connection_return.insert(0.0, str(connected))
        
        if connected == None:
            self.SetStatus(1)
            self.client = ssh_client
            self.SetConfig(host, user, port)
            self.main_application.client = self.client

        else:
            self.SetStatus(0)

    def Disconnect(self):
        self.SetStatus(0)
        if self.client != None:
            self.client.close()
            self.client = None
        self.SetConfig(None, None, None)

    def SetStatus(self, status):
        self.status = status
        if status == 0:
            self.status_label.configure(text = "Disconected")
            self.status_label.configure(text_color = "#FF6961")
            self.main_application.connection_label.configure(text = "Disconected")
            self.main_application.connection_label.configure(text_color = "#FF6961")
            return

        if status == 1:
            self.status_label.configure(text = "Connected")
            self.status_label.configure(text_color = "#77DD77")
            self.main_application.connection_label.configure(text = "Connected")
            self.main_application.connection_label.configure(text_color = "#77DD77")
            return
        
    def SetConfig(self, host, user, port):
        self.config_display.configure(text = f"host : {host}\nuser : {user}\nport : {port}")

    def OnWindowExit(self):
        self.top_level.withdraw()