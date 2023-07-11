from hostconfigwindow import HostConfigWindow
from hostconnectionwindow import HostConnectionWindow

import customtkinter as ctk
import tkinter as tk

import matplotlib.figure as figure
import matplotlib.backends.backend_tkagg as backend_tkagg

import math

import platform
import os
import time

ctk.set_default_color_theme("green")
ctk.set_appearance_mode("light")

def ConfigureBaseFile(base_file, *inputs):
    file = base_file
    for input in inputs:
        file = file.replace("{}", str(input), 1)

    return file

def LoadSetup():
    from_file = open("templates/setup.sh", 'r')
    to_file = open("filestosend/setup.sh", 'w')

    to_file.write(from_file.read())

    from_file.close()
    to_file.close()

    return "filestosend/setup.sh"

def GenerateRunHPL(cores_per_node):
    base_file = open("templates/runhpl.sh", 'r')
    base_data = base_file.read()
    base_file.close()

    data = ConfigureBaseFile(base_data, cores_per_node, cores_per_node)

    file = open("filestosend/runhpl.sh", 'w')
    file.write(data)
    file.close()

    return "filestosend/runhpl.sh"

def GenerateDotDatFiles(standard_values, nb_groups, pq_groups):
    hpl_dot_dat_file_paths = []
    for nb_group in nb_groups:
        hpl_dot_dat_file_paths.append(GenerateNBDat(standard_values, nb_group))
    for pq_group in pq_groups:
        p_group = [pair[0] for pair in pq_groups]
        q_group = [pair[1] for pair in pq_groups]
        hpl_dot_dat_file_paths.append(GeneratePQDat(standard_values, p_group, q_group))
    
    return hpl_dot_dat_file_paths
    
def GenerateNBDat(standard_values, nb_group):
    Ns = standard_values[0]
    NB_n = len(nb_group)
    NBs = ""
    for NB in nb_group:
        NBs += NB
    PQ_n = 1
    Ps = standard_values[2]
    Qs = standard_values[3]
    data = ConfigureBaseFile("templates/HPL.dat", Ns, NB_n, NBs, PQ_n, Ps, Qs)

    file_path = f"filestosend/hplfiles/NB ({nb_group[0]} - {nb_group[-1]}) HPL.dat"

    file = open(file_path, 'w')
    file.write(data)
    file.close()

    return file_path

def GeneratePQDat(standard_values, p_group, q_group):
    Ns = standard_values[0]
    NB_n = 1
    NBs = standard_values[1]
    PQ_n = len(pq_group)
    Ps = ""
    for p in p_group:
        Ps += p
    Qs = ""
    for q in q_group:
        Qs += q
    
    data = ConfigureBaseFile("templates/HPL.dat", Ns, NB_n, NBs, PQ_n, Ps, Qs)

    file_path = f"filestosend/hplfiles/PQ ({pq_group[0]} - {pq_group[-1]}) HPL.dat"

    file = open(file_path, 'w')
    file.write(data)
    file.close()

    return file_path

def GenerateFiles(standard_values, nb_groups, pq_groups, cores_per_node):

    setup_sh_path = LoadSetup()
    runhpl_dot_sh_path = GenerateRunHPL(cores_per_node)
    hpl_dot_dat_files_paths = GenerateDotDatFiles(standard_values, nb_groups, pq_groups)

    return setup_sh_path, runhpl_dot_sh_path, hpl_dot_dat_files_paths

def RemoveOldFiles():
    
    dir = 'filestosend/hplfiles'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def WaitingForCurrentProcessToFinish(client):
    stdin, stdout, stderr = client.exec_command("squeue -u pzhm13")
    if(len(stdout.readlines()) > 1):
        return False
    else:
        True

class MainApplication(ctk.CTk):
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Main Application")
        self.root.geometry("1600x900+80+45")
        self.menu = self.GenerateMenu()

        self.host_config_window = None
        self.host_connection_window = None

        self.client = None

        self.connection_label = None

        self.optimization_parameters = None

        self.standard_n = 0
        self.standard_nb = 0
        self.standard_p = 0
        self.standard_q = 0

        self.optimal_n = None
        self.optimal_nb = None
        self.optimal_p = None
        self.optimal_q = None

        self.MAX_PARTITION_SIZE = 20

        self.cores_per_node = None

        self.n_data_set = []
        self.nb_data_set = []
        self.pq_data_set = []

        self.remote_dir = None

        self.optimization_data = None

        self.DrawGUI()

    def GenerateMenu(self):
        menubar = tk.Menu(self.root)

        sshbar = tk.Menu(menubar, tearoff = 0)
        
        sshbar.add_command(label = "Host Config", command = lambda : self.OpenHostConfigWindow())
        sshbar.add_command(label = "Connect to Host", command = lambda : self.OpenHostConnectionWindow())

        menubar.add_cascade(label = "SSH", menu = sshbar)
        self.root.config(menu = menubar)
    
    def DrawGUI(self):
        self.DrawOptimizationSetupFrame()
        self.DrawPerformanceFrame()
        self.DrawConnectionFrame()
        self.DrawPredictionsFrame()

    def DrawOptimizationSetupFrame(self):
        optimization_settings_frame = ctk.CTkFrame(self.root)
        optimization_settings_frame.place(anchor = "center", relx = 0.2, rely = 0.5, relwidth = 0.35, relheight = 0.9)

        calculate_start_settings = ctk.CTkButton(optimization_settings_frame, text="Calculate Start Settings", command = lambda : self.CalculateStartSettings())
        calculate_start_settings.place(anchor = "center", relx = 0.25, rely = 0.05, relwidth = 0.45, relheight = 0.08)
        run_optimization = ctk.CTkButton(optimization_settings_frame, text="Run Optimization", command = lambda : self.RunOptimization())
        run_optimization.place(anchor = "center", relx = 0.75, rely = 0.05, relwidth = 0.45, relheight = 0.08)
        
        memory = ctk.CTkFrame(optimization_settings_frame, fg_color="grey80", border_color="grey80")
        memory.place(anchor = "n", relx = 0.25, rely = 0.1, relheight = 0.2, relwidth = 0.45)


        mem_per_node_input = ctk.CTkEntry(memory, font=("System", 20), placeholder_text="GB per Node:")
        mem_per_node_input.place(anchor = "nw", relx = 0.02, rely = 0.0, relwidth = 0.6, relheight = 0.4)

        self.mem_size = mem_per_node_input

        percentage_input = ctk.CTkEntry(memory, font=("System", 20), placeholder_text="%mem")
        percentage_input.place(anchor = "ne", relx = 0.98, rely = 0.0, relwidth = 0.3, relheight = 0.4)

        self.mem_percent = percentage_input

        cores_input = ctk.CTkEntry(memory, font=("System", 20), placeholder_text="Cores per node:")
        cores_input.place(anchor = "s", relx = 0.5, rely = 1, relwidth = 0.8, relheight = 0.4)

        self.cores_per_node = cores_input

        start_settings = ctk.CTkFrame(optimization_settings_frame, fg_color="grey80", border_color="grey80")
        start_settings.place(anchor = "s", relx = 0.25, rely = 0.95, relheight = 0.6, relwidth = 0.45)
        start_settings_label = ctk.CTkLabel(start_settings, text="Start Settings", font=("System", 20))
        start_settings_label.place(relx = 0.5, rely = 0, anchor = "n", relwidth = 0.9, relheight = 0.1)
        
        self.ss_N = ctk.CTkLabel(start_settings, fg_color="grey75", text = "N:")
        self.ss_N.place(relx = 0.5, rely = 0.1, relwidth = 0.9, relheight = 0.1, anchor = "n")
        self.ss_NB = ctk.CTkLabel(start_settings, fg_color="grey75", text = "NB:")
        self.ss_NB.place(relx = 0.5, rely = 0.22, relwidth = 0.9, relheight = 0.1, anchor = "n")
        self.ss_PQ = ctk.CTkLabel(start_settings, fg_color="grey75", text = "(P,Q):")
        self.ss_PQ.place(relx = 0.5, rely = 0.34, relwidth = 0.9, relheight = 0.1, anchor = "n")

        search_settings = ctk.CTkFrame(optimization_settings_frame, fg_color="grey80", border_color="grey80")
        search_settings.place(anchor = "s", relx = 0.75, rely = 0.95, relheight = 0.85, relwidth = 0.45)

        search_settings_label = ctk.CTkLabel(search_settings, text="Search Settings", font=("system", 20))
        search_settings_label.place(anchor = "n", relx = 0.5, rely = 0, relheight = 0.1, relwidth = 0.8)

        mms_NB_frame = ctk.CTkFrame(search_settings, fg_color="grey75", bg_color="grey75")
        mms_NB_frame.place(anchor = "n", relx = 0.5, rely = 0.22, relheight = 0.1, relwidth=1)
        
        self.mms_NB_min = ctk.CTkEntry(mms_NB_frame, fg_color="grey70", border_color="grey70", placeholder_text = "NB min", text_color="#000000")
        self.mms_NB_min.place(anchor = "center", relx = 0.20, rely = 0.5, relheight = 0.8, relwidth = 0.25)

        self.mms_NB_max = ctk.CTkEntry(mms_NB_frame, fg_color="grey70", border_color="grey70", placeholder_text = "NB max", text_color="#000000")
        self.mms_NB_max.place(anchor = "center", relx = 0.5, rely = 0.5, relheight = 0.8, relwidth = 0.25)

        self.mms_NB_n = ctk.CTkEntry(mms_NB_frame, fg_color="grey70", border_color="grey70", placeholder_text = "NB n", text_color="#000000")
        self.mms_NB_n.place(anchor = "center", relx = 0.80, rely = 0.5, relheight = 0.8, relwidth = 0.25)



        mms_PQ_frame = ctk.CTkFrame(search_settings, fg_color="grey75", bg_color="grey75")
        mms_PQ_frame.place(anchor = "n", relx = 0.5, rely = 0.34, relheight = 0.1, relwidth=1)
        
        self.mms_PQ_min = ctk.CTkEntry(mms_PQ_frame, fg_color="grey70", border_color="grey70", placeholder_text = "PQ min", text_color="#000000")
        self.mms_PQ_min.place(anchor = "center", relx = 0.20, rely = 0.5, relheight = 0.8, relwidth = 0.25)

        self.mms_PQ_max = ctk.CTkEntry(mms_PQ_frame, fg_color="grey70", border_color="grey70", placeholder_text = "PQ max", text_color="#000000")
        self.mms_PQ_max.place(anchor = "center", relx = 0.5, rely = 0.5, relheight = 0.8, relwidth = 0.25)

        self.mms_PQ_n = ctk.CTkEntry(mms_PQ_frame, fg_color="grey70", border_color="grey70", placeholder_text = "PQ n", text_color="#000000")
        self.mms_PQ_n.place(anchor = "center", relx = 0.80, rely = 0.5, relheight = 0.8, relwidth = 0.25)

        remote_dir_frame = ctk.CTkFrame(search_settings, fg_color="grey75", bg_color="grey75")
        remote_dir_frame.place(anchor = "n", relx = 0.5, rely = 0.46, relheight = 0.1, relwidth=1)

        self.remote_dir = ctk.CTkEntry(remote_dir_frame, fg_color="grey70", bg_color="grey70", font = ("system", 1), placeholder_text="/home/username/hpl-location/")
        self.remote_dir.place(anchor = "center", relx = 0.5, rely = 0.5, relheight = 0.8, relwidth = 0.8)

    def DrawPerformanceFrame(self):
        performance_data_frame = ctk.CTkFrame(self.root)
        performance_data_frame.place(anchor = "center", relx = 0.65, rely = 0.5, relwidth = 0.45, relheight = 0.9)

        n_frame = ctk.CTkFrame(performance_data_frame, fg_color="grey80", border_color="grey80")
        n_frame.place(anchor = "center", relheight = 0.48, relwidth = 0.98, relx = 0.5, rely = 0.25)

        n_fig = figure.Figure(figsize=(5, 5), dpi = 100)
        n_plot = n_fig.add_subplot(111)
        n_plot.set_title = "NB"
        n_plot.set_xlabel("NB value")
        n_plot.set_ylabel("Gflops/s")
        n_plot.plot(self.nb_data_set)
        n_canvas = backend_tkagg.FigureCanvasTkAgg(n_fig, master = n_frame)
        n_canvas.draw()
        n_canvas.get_tk_widget().place(anchor = "center", relx = 0.5, rely = 0.5, relwidth = 0.95, relheight= 0.95) 

        self.nb_figure = n_fig
        self.nb_canvas = n_canvas

        s_frame = ctk.CTkFrame(performance_data_frame, fg_color="grey80", border_color="grey80")
        s_frame.place(anchor = "center", relheight = 0.48, relwidth = 0.98, relx = 0.5, rely = 0.75)

        s_fig = figure.Figure(figsize=(5, 5), dpi = 100)
        s_plot = s_fig.add_subplot(111)
        s_plot.set_title = "(P,Q)"
        s_plot.set_xlabel("P from the (P,Q) value pair")
        s_plot.set_ylabel("Gflops/s")
        s_plot.plot(self.pq_data_set)
        s_canvas = backend_tkagg.FigureCanvasTkAgg(s_fig, master = s_frame)
        s_canvas.draw()
        s_canvas.get_tk_widget().place(anchor = "center", relx = 0.5, rely = 0.5, relwidth = 0.95, relheight= 0.95) 
  
        self.pq_figure = s_fig
        self.pq_canvas = s_canvas

    def DrawConnectionFrame(self):
        connection_frame = ctk.CTkFrame(self.root)
        connection_frame.place(anchor = "center", relx = 0.95, rely = 0.1, relwidth = 0.08, relheight = 0.1)

        self.connection_label = ctk.CTkLabel(connection_frame, text = "Disconnected", text_color = "#FF6961", font=("system", 20))
        self.connection_label.place(anchor = "center", relx = 0.5, rely = 0.5)

        predicted_N = ctk.CTkLabel(connection_frame)
        predicted_NB = ctk.CTkLabel(connection_frame)
        predicted_P = ctk.CTkLabel(connection_frame)
        predicted_Q = ctk.CTkLabel(connection_frame)

    def DrawPredictionsFrame(self):
        predictions_frame = ctk.CTkFrame(self.root)
        predictions_frame.place(anchor = "center", relx = 0.95, rely = 0.575, relwidth = 0.08, relheight = 0.75)

        optimal_n = ctk.CTkLabel(predictions_frame, text="N:", fg_color = "grey80", bg_color= "grey80")
        optimal_n.place(anchor = "center", relx = 0.5, rely = 0.2, relwidth = 0.9, relheight = 0.15)
        self.optimal_n = optimal_n

        optimal_nb = ctk.CTkLabel(predictions_frame, text="NB:", fg_color = "grey80", bg_color= "grey80")
        optimal_nb.place(anchor = "center", relx = 0.5, rely = 0.4, relwidth = 0.9, relheight = 0.15)
        self.optimal_nb = optimal_nb

        optimal_p = ctk.CTkLabel(predictions_frame, text="P:", fg_color = "grey80", bg_color= "grey80")
        optimal_p.place(anchor = "center", relx = 0.5, rely = 0.6, relwidth = 0.9, relheight = 0.15)
        self.optimal_p = optimal_p

        optimal_q = ctk.CTkLabel(predictions_frame, text="Q:", fg_color = "grey80", bg_color= "grey80")
        optimal_q.place(anchor = "center", relx = 0.5, rely = 0.8, relwidth = 0.9, relheight = 0.15)
        self.optimal_q = optimal_q

    def RunOptimization(self):
        standard_n = 10000#self.standard_n
        standard_nb = 240#self.standard_nb
        standard_p = 4#self.standard_p
        standard_q = 32#self.standard_q

        standard_values = (standard_n, standard_nb, standard_p, standard_q)

        nb_min = 120#int(self.mms_NB_min.get())
        nb_max = 240#int(self.mms_NB_max.get())
        nb_n = 70#int(self.mms_NB_n.get())

        p_min = 1#int(self.mms_PQ_min.get())
        p_max = 4#int(self.mms_PQ_max.get())
        p_n = 2#int(self.mms_PQ_n.get())

        PATH = "test/path"#self.remote_dir.get()

        cores_per_node = 128#int(self.cores_per_node.get())
        
        nb_range = self.GenerateSamplePoints(nb_min, nb_max, nb_n)
        p_range = self.GenerateSamplePoints(p_min, p_max, p_n)
        q_range = [cores_per_node // p for p in p_range]

        nb_groups = self.PartitionRange(nb_range)
        pq_groups = [[(p, cores_per_node // p) for p in p_group] for p_group in self.PartitionRange(p_range)]

        RemoveOldFiles()

        setup_sh_path, runhpl_dot_sh_path, hpl_dot_dat_file_paths = GenerateFiles(standard_values, nb_groups, pq_groups, cores_per_node)

        # sftpClient = self.client.open_sftp()

        # sftpClient.put(setup_sh_path, f"{PATH}/setup.sh")#send setup.sh
        # sftpClient.put(runhpl_dot_sh_path, f"{PATH}/runhpl.sh")#send runhpl.sh

        # def sftp_exists(sftp, path):
        #     try:
        #         sftp.stat(path)
        #         return True
        #     except FileNotFoundError:
        #         return False

        # data = []
        # for hpl_dot_dat_file_path in hpl_dot_dat_file_paths:
            
        #     sftpClient.put(hpl_dot_dat_file_path, f"{PATH}/HPL.dat")#move
        #     if sftp_exists(sftpClient, f"{PATH}/auto-opt/build/bin/xhpl") == True:
        #         (stdin, stdout, stderr) = self.client.exec_command(f"cd {PATH}/; dos2unix runhpl.sh; sbatch runhpl.sh")
        #         while(WaitingForCurrentProcessToFinish(self.client) == False):
        #             time.sleep(0.2)
            
        #     else:
        #         (stdin, stdout, stderr) = self.client.exec_command(f"cd {PATH}/; dos2unix setup.sh; sbatch setup.sh")
        #         while(sftp_exists(sftpClient, f"{PATH}/auto-opt/build/bin/xhpl") == False):
        #             time.sleep(0.2)
                
        #         (stdin, stdout, stderr) = self.client.exec_command(f"cd{PATH}/; dos2unix runhpl.sh; sbatch runhpl.sh")
        #         while(WaitingForCurrentProcessToFinish(self.client) == False):
        #             time.sleep(0.2)

        #     hpl_out_file = sftpClient.open(f"{PATH}/auto-opt/out/HPL.out")
        #     out_data = hpl_out_file.readlines()
            
        #     useful_line_indexs = [18, 19, 21, 22, 38]
        #     useful_data = [line for index, line in enumerate(out_data) if index in useful_line_indexs]
            
        #     lines =[]
        #     for line in useful_data:
        #         line = line.strip(' \n')
        #         lastspaceindex = line.rfind(' ')
        #         line = float(line[lastspaceindex:])
        #         lines.append(line)
            
        #     variables = lines[0:-1]
        #     performance = lines[-1:][0]
            
        #     index, value = self.FindChangedValueAndIndex(variables[1:])
        #     data.append((index, value, performance))
            
        #     sftpClient.remove(f"{PATH}/HPL.dat")#delete
        #     while sftp_exists(sftpClient, f"{PATH}/HPL.dat") == True:
        #         time.sleep(0.2)

        # data.sort(key = lambda x:x[0])

        # number_of_varibles = data[-1][0]

        # variable_fields = [[] for i in range(number_of_varibles)]

        # for piece in data:
        #     index, value = piece[0] - 1, piece[1:]
        #     variable_fields[index].append(value)

        # self.optimization_data = variable_fields

        # self.UpdatePredictions()
        # self.UpdatePerformanceGraphs()

    def GenerateSamplePoints(self, MIN, MAX, SAMPLENUMBER):
        delta = MAX - MIN
        
        if SAMPLENUMBER > delta + 1:
            raise SAMPLE_NUM_TOO_LARGE_EXCEPTION
        if SAMPLENUMBER < 2:
            raise SAMPLE_NUM_TOO_SMALL_EXCEPTION
    
        if delta < 0:
            raise MIN_TOO_LARGE_EXCEPTION
        if delta == 0:
            raise MIN_EQUAL_TO_MAX_EXCEPTION
    
        if MIN <= 0:
            raise MIN_TOO_SMALL_EXCEPTION
        
        sample_points = [int(MIN + delta * (i / (SAMPLENUMBER - 1))) for i in range(SAMPLENUMBER)]
        return sample_points  
    
    def PartitionRange(self, rangedata):

        number_of_samples = len(rangedata)
        number_of_partitions = (number_of_samples // self.MAX_PARTITION_SIZE) + 1
        
        partitions = []
        
        for partition_number in range(number_of_partitions):
            index = self.MAX_PARTITION_SIZE * partition_number
            if partition_number == number_of_partitions - 1:
                partitions.append(rangedata[index :])
            else:
                partitions.append(rangedata[index : index + self.MAX_PARTITION_SIZE])
        
        return partitions 

    def UpdatePredictions(self):
        optimal_settings = [max(variable_field, key = lambda x:x[1])[0] for variable_field in self.optimization_data]

        mem_fraction = 0.95
        mem_size = int(self.mem_size.get())
        mem_size_bytes = mem_size * 1024 * 1024 * 1024

        self.optimal_n.configure(text = f"N: {math.floor(math.sqrt(mem_size_bytes * (mem_fraction / 8.0)))}")
        self.optimal_nb.configure(text = f"NB: {math.floor(optimal_settings[0])}")
        self.optimal_p.configure(text = f"P: {math.floor(optimal_settings[1])}")
        self.optimal_q.configure(text = f"Q: {math.floor(float(self.cores_per_node.get()) / optimal_settings[1])}")

    def UpdatePerformanceGraphs(self):
        
        nb_data = self.optimization_data[0]
        nb_x = [data[0] for data in nb_data]
        nb_y = [data[1] for data in nb_data]
        self.nb_figure.clear()
        nb_plot = self.nb_figure.add_subplot(111)
        nb_plot.plot(nb_x, nb_y,  '-gD')
        nb_plot.set_title = "NB"
        nb_plot.set_xlabel("NB value")
        nb_plot.set_ylabel("Gflops/s")
        self.nb_canvas.draw_idle()

        pq_data = self.optimization_data[1]
        pq_x = [data[0] for data in pq_data]
        pq_y = [data[1] for data in pq_data]
        self.pq_figure.clear()
        pq_plot = self.pq_figure.add_subplot(111)
        pq_plot.plot(pq_x, pq_y, '-gD')
        pq_plot.set_title = "(P, Q)"
        pq_plot.set_xlabel("P from the (P,Q) value pair")
        pq_plot.set_ylabel("Gflops/s")
        self.pq_canvas.draw_idle()

    def FindChangedValueAndIndex(self, variables):

        standard_nb = self.standard_nb
        standard_p = self.standard_p
        standard_q = self.standard_q

        standard_values = (standard_nb, standard_p, standard_q)
        for index, value in enumerate(standard_values):
            if float(value) != float(variables[index]):
                return (index + 1, float(variables[index]))
        
    def CalculateStartSettings(self):
        mem_size = int(self.mem_size.get())
        mem_percent = int(self.mem_percent.get())
        cores_per_node = int(self.cores_per_node.get())

        self.cores_per_node_num = cores_per_node

        mem_size_bytes = mem_size * 1024 * 1024 * 1024
        mem_fraction = int(mem_percent) / 100

        N = math.floor(math.sqrt(mem_size_bytes * (mem_fraction / 8.0)))
        
        NB = 240

        square_PQ = math.floor(math.sqrt(cores_per_node))
        
        P = square_PQ
        Q = square_PQ

        self.ss_N.configure(text = f"N : {N}")
        self.ss_NB.configure(text = f"NB : {NB}") 
        self.ss_PQ.configure(text = f"(P, Q) : ({P}, {Q})")

        self.standard_n = N
        self.standard_nb = NB
        self.standard_p = P
        self.standard_q = Q

    def OpenHostConnectionWindow(self):
        if self.host_connection_window == None:
            self.host_connection_window = HostConnectionWindow(self.root, "Host Connection Manager", "800x600", "grey95", self)
        else:
            self.host_connection_window.top_level.deiconify()
            self.host_connection_window.LoadTableData()
        self.host_connection_window.top_level.lift()
        self.host_connection_window.top_level.attributes('-topmost',True)
        self.host_connection_window.top_level.after_idle(self.host_connection_window.top_level.attributes,'-topmost',False)

    def OpenHostConfigWindow(self):
        self.host_config_window = HostConfigWindow(self.root, "Host Config Manager", "800x600", "grey95")
        self.host_config_window.top_level.deiconify()
        self.host_config_window.top_level.lift()
        self.host_config_window.top_level.attributes('-topmost',True)
        self.host_config_window.top_level.after_idle(self.host_config_window.top_level.attributes,'-topmost',False)

    def StartMainLoop(self):
        self.root.mainloop()