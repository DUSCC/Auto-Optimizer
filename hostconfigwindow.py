import customtkinter as ctk
from tkinter import ttk

import pickle

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("light")

class TableData():
    def __init__(self):
        self.data = []

    def ReadData(self, table):
        return self.data

    def WriteData(self, table):
        iids = table.get_children()
        data = [table.item(iid, "values") for iid in iids]
        self.data = data

class HostConfigWindow():
    def __init__(self, root, title, geometry, fg_color):
        self.root = root
        self.top_level = ctk.CTkToplevel(root, fg_color=fg_color)
        self.top_level.title(title)
        self.top_level.geometry(geometry)
        self.top_level.protocol("WM_DELETE_WINDOW", lambda : self.OnWindowExit())
        
        self.selected_items = None
        self.tabledata = self.LoadTableData()
        self.table = None

        self.login_info_and_options()
        self.known_hosts_information()

    def AddHostConfig(self, host, user, port):      
        config = (host, user, port)
        self.table.insert("", "end", values = config)

    def UpdateHostConfig(self, host, user, port):
        if self.selected_items == None:
            return
        
        config = (host, user, port, password)
        
        for item in self.selected_items:
            index = self.table.index(item)
            self.table.delete(item)
            new_item = self.table.insert("", index, values = config)
            self.table.selection_add(new_item)      

    def DeleteHostConfig(self):
        if self.selected_items == None:
            return
        
        for item in self.selected_items:
            self.table.delete(item)
        
        self.selected_items = None

    def item_selected(self, event):
        self.selected_items = self.table.selection()

    def login_info_and_options(self):
        info_frame = ctk.CTkFrame(self.top_level)
        info_frame.place(relx = 0, rely = 0, relwidth = 1, relheight = 0.1, anchor = "nw")
        login_frame = ctk.CTkFrame(self.top_level)
        login_frame.place(relx = 0, rely = 1, relwidth = 0.2, relheight = 0.6, anchor = "sw")
        options_frame = ctk.CTkFrame(self.top_level)
        options_frame.place(relx = 0.25, rely = 1, relwidth = 0.15, relheight = 0.4, anchor = "sw")

        info_title = ctk.CTkLabel(info_frame, text = "Host Config Manager", font = ("system", 30))
        info_title.place(anchor = "n", relx = 0.5, rely = 0)

        info_description = ctk.CTkLabel(info_frame, text = "Using the input panel you can enter login information, then, using the options panel you can save the info,\n allowing connection to the host with the saved parameters. known hosts are saved to the table to the right", font = ("system", 11))
        info_description.place(anchor = "s", relx = 0.5, rely = 1)

        login_title = ctk.CTkLabel(login_frame, text = "Input", font = ("system", 30))
        login_title.place(anchor = "n", relx = 0.5, rely = 0)

        login_host_entry = ctk.CTkEntry(login_frame, placeholder_text="Host", font = ("system", 20))
        login_host_entry.place(anchor = "center", relx = 0.5, rely = 0.2, relwidth = 0.8, relheight = 0.15)
        login_user_entry = ctk.CTkEntry(login_frame, placeholder_text="User")
        login_user_entry.place(anchor = "center", relx = 0.5, rely = 0.4, relwidth = 0.8, relheight = 0.15)
        login_port_entry = ctk.CTkEntry(login_frame, placeholder_text="Port")
        login_port_entry.place(anchor = "center", relx = 0.5, rely = 0.6, relwidth = 0.8, relheight = 0.15)

        options_title = ctk.CTkLabel(options_frame, text = "Options", font = ("system", 30))
        options_title.place(anchor = "n", relx = 0.5, rely = 0)

        options_add_button = ctk.CTkButton(options_frame, text = "Add", command = lambda : self.AddHostConfig(login_host_entry.get(), login_user_entry.get(), login_port_entry.get()), font = ("system", 20))
        options_add_button.place(anchor = "center", relwidth = 0.8, relheight = 0.2, relx = 0.5, rely = 0.25)

        options_edit_button = ctk.CTkButton(options_frame, text = "Update", command = lambda : self.UpdateHostConfig(login_host_entry.get(), login_user_entry.get(), login_port_entry.get(), login_password_entry.get()), font = ("system", 20))
        options_edit_button.place(anchor = "center", relwidth = 0.8, relheight = 0.2, relx = 0.5, rely = 0.50)

        options_delete_button = ctk.CTkButton(options_frame, text = "Delete", command = lambda : self.DeleteHostConfig(), font = ("system", 20))
        options_delete_button.place(anchor = "center", relwidth = 0.8, relheight = 0.2, relx = 0.5, rely = 0.75)

    def known_hosts_information(self):
        info_frame = ctk.CTkFrame(self.top_level)
        info_frame.place(relx = 1, rely = 1, relwidth = 0.45, relheight = 0.75, anchor = "se")

        columns = ("host", "user", "port")
        
        table = ttk.Treeview(info_frame, columns=columns, show = "headings", selectmode="extended")

        table.heading('host', text = "Host")
        table.heading('user', text = "User")
        table.heading('port', text = "Port")

        table.column('host', minwidth = 0, width = 90)
        table.column('user', minwidth = 0, width = 90)
        table.column('port', minwidth = 0, width = 90)

        table.pack(expand = "yes", fill = "both")

        table.bind('<<TreeviewSelect>>', self.item_selected)

        for data in self.tabledata.data:
            table.insert("", "end", values = data)

        self.table = table
        
    def OnWindowExit(self):
        self.SaveTableData()
        self.top_level.withdraw()

    def SaveTableData(self):
        self.tabledata.WriteData(self.table)
        
        try:
            with open("table.pickle", "wb") as f:
                pickle.dump(self.tabledata, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        except Exception as ex:
            print(f"1 {ex}")

    def LoadTableData(self):
        try:
            with open("table.pickle", "rb") as f:
                tabledata = pickle.load(f)
                return tabledata
        
        except Exception as ex:
            print(f"2 {ex}")
            return TableData()
        pass