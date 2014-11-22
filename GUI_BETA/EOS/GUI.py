from tkinter import *
from tkinter.ttk import Treeview
from tkinter.constants import DISABLED
from EOS.connect import Connection
import json,os,glob,threading,queue,datetime

class eos:
    
    def __init__(self, parent):
        
        """ Constants """
        self.buttonPadx = 40
        self.buttonPadxAbout = 112
        self.buttonPady = 5
        
        self.paddingPopup = 10
        self.paddinTitlePopup = 50
        self.paddingTitleExp = 30
        self.paddingGeneralExp = 10
        
        self.titlefont = ("Consolas", 24, "bold")
        self.titlePopupfont = ("Consolas", 18, "bold")
        self.generalExpfont = ("Consolas", 14)
        self.generalfont = ("Consolas", 12)
        
        self.background = "#A7DBD8"
        self.foreground = "#594F4F"
        
        self.oldRadio = 1
        
        self.connected = None
        
        self.ExpFrame = None
        
        self.queue = queue.Queue()
        
        """ Init Windows """
        
        # Parent
        self.myParent = parent
        self.myParent.minsize(800, 600)
        self.myParent.config(bg="green")
        
        ## Frame for the listbox located at the left of the window
        self.left_frame = Frame(self.myParent)
        self.left_frame.pack(side = "left",fill="y")
        
        # Right Frame
        self.right_frame = Frame(self.myParent,borderwidth=2, relief=RIDGE)
        self.right_frame.pack(side = "left",fill="both",expand = 1)
        
        self.initHistoryList()
        self.initHomeView()
    
    """ Initializing history listbox"""
    def initHistoryList(self):
        # Label
        self.historyL = Label(self.left_frame,text="History",fg="black")
        self.historyL.pack(side="top",fill="x");
        
        # Scrollbar
        self.scrollbar = Scrollbar(self.left_frame)
        self.scrollbar.pack(side = "right",fill="y")
        
        # Listbox
        self.listBox = Listbox(self.left_frame, selectmode='Browse', yscrollcommand=self.scrollbar.set)
        # Iterate through the files with a .info extension
        for i,file in enumerate(glob.glob( os.path.join(os.getcwd()+"\Experiments", '*.info'))):
            # Load file
            json_data=open(file)
            # Get json data
            expElement = json.load(json_data)
            # Insert it in the list
            self.listBox.insert(i, expElement["name"])
            # If a .txt is found, a experiment is running
#             if len(glob.glob(os.path.join(os.getcwd()+"\Experiments\\" + expElement["name"]+".txt"))) == 1:
#                 self.listBox.itemconfig(i, bg = "green")
            
        self.listBox.pack(side = "left",fill="y")
         
        # Attach scollbar to listbox
        self.scrollbar.config(command=self.listBox.yview)
        
        self.listBox.bind("<<ListboxSelect>>", self.viewExperiment)
        
    """ Initializing right Frame"""
    def initHomeView(self):
        global currentExp
        
        # Main Frame
        self.homeFrame = Frame(self.right_frame, relief=RIDGE, bg = self.background)
        self.homeFrame.pack(fill="both",expand = 1)
        
        # Title
        self.photo = PhotoImage(file="../eos.gif")
        self.titleL = Label(self.homeFrame,image=self.photo,fg=self.foreground,bg =self.background, font = self.titlefont)
        self.titleL.place(relx=0.5, rely=0.03, anchor=N)
        
        # Group label for status info
        self.statusGroup = LabelFrame(self.homeFrame, padx=5, pady=5, bg = self.background)
        self.statusGroup.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Status Label
        self.statusL = Label(self.statusGroup,fg=self.foreground, bg = self.background, font = self.generalfont)
        # Button for connecting and disconnecting
        self.connectB = Button(self.statusGroup, text = "Connect",fg = "black",bg="#F3A262", padx = self.buttonPadxAbout, pady = self.buttonPady, font = self.generalfont, command = self.initConnect)
        
        # Port Frame for COM ports
        self.portFrame = Frame(self.statusGroup, bg = self.background, pady = self.paddingGeneralExp)
        # Label and entry for port connection
        self.connectL = Label(self.portFrame,text = "Connect to Port: ",fg=self.foreground, bg = self.background, font = self.generalfont)
        self.connectE = Entry(self.portFrame, font = self.generalfont)
        
        # Create Button
        self.createExperimentB = Button(self.homeFrame, text = "Create New Experiment",fg = "black",bg="#F3A262", padx = self.buttonPadx, pady = self.buttonPady, font = self.generalfont,command=self.initCreateExpPopup)
        
        if self.connected == None:
            # Not connected
            self.initNotconnectedStatus()
        else:
            # Connected
            self.initConnectedStatus()
        
        # Place create button
        self.createExperimentB.place(relx = 0.5,rely=0.85, anchor = CENTER)
        
        if currentExp is not None or self.connected is None:
            self.createExperimentB["state"] = DISABLED
        else:
            self.createExperimentB["state"] = NORMAL
        
        self.aboutB = Button(self.homeFrame, text = "About",fg = "black",bg="#F3A262", padx = self.buttonPadxAbout, pady = self.buttonPady, font = self.generalfont)
        self.aboutB.place(relx = 0.5,rely=0.93, anchor = CENTER)
    
    """ Init home frame COM status when disconnected """
    def initNotconnectedStatus(self):
        
        # Destroy status label and connect button to keep widgets in the same order for .pack()
        self.statusL.destroy()
        self.connectB.destroy()
        
        # Status Label
        self.statusL = Label(self.statusGroup,fg=self.foreground, bg = self.background, font = self.generalfont)
        # Button for connecting and disconnecting
        self.connectB = Button(self.statusGroup, text = "Connect",fg = "black",bg="#F3A262", padx = self.buttonPadxAbout, pady = self.buttonPady, font = self.generalfont, command = self.initConnect)
        
        # Port Frame for COM ports
        self.portFrame = Frame(self.statusGroup, bg = self.background, pady = self.paddingGeneralExp)
        # Label and entry for port connection
        self.connectL = Label(self.portFrame,text = "Connect to Port: ",fg=self.foreground, bg = self.background, font = self.generalfont)
        self.connectE = Entry(self.portFrame, font = self.generalfont)
        
        # Modify Label and button state
        self.statusL["text"] = "System not connected"
        self.connectB["text"] = "Connect"
        self.connectB["state"] = NORMAL
        self.createExperimentB["state"] = DISABLED
        
        # Pack connect options
        self.connectL.pack(side=LEFT)
        self.connectE.pack(side=RIGHT)
        
        # Pack label, port frame and button
        self.statusL.pack()
        self.portFrame.pack()
        self.connectB.pack()
        
    """ Init home frame COM status when connected """
    def initConnectedStatus(self):
        # Modify labels
        self.statusL["text"] = "System Connected through port: " + self.connected.getPort()
        self.connectB["text"] = "Disconnect"
        self.createExperimentB["state"] = NORMAL
        # Pack label and disconnect button
        self.statusL.pack()
        self.connectB.pack()
        # Destroy port frame
        self.portFrame.destroy()
        
    """ Function used for connecting or disconnecting the COM port"""
    def initConnect(self):
        # Callbacks
        def callbackConnect():
            # Open port
            port = self.connectE.get()
            print (port)
            try:
                self.connected = Connection(port)
                self.queue.put(self.connected)
            except:
                e = sys.exc_info()[0]
                print(e)
                
        def callbackClose():
            # Close port
            try:
                self.connected.closePort()
                self.connected = None
                self.queue.put(1)
            except:
                e = sys.exc_info()[0]
                self.queue.put(e)
                
        # Check connection status
        if self.connected is None:
            # Not connected
            t = threading.Thread(target=callbackConnect)
            t.start()
            self.myParent.after(100,self.checkConnectQueue)
        else:
            # Connected
            t = threading.Thread(target=callbackClose)
            t.start()
            self.myParent.after(100,self.checkDisconnectQueue)

    def checkDisconnectQueue(self):
        if not self.queue.empty():
            self.queue.get()
            self.initNotconnectedStatus()
        else:
            self.myParent.after(100,self.checkDisconnectQueue)

    def checkConnectQueue(self):
        if not self.queue.empty():
            self.connected = self.queue.get()
            try:
                self.connected.getPort()
            except:
                print("Error! " + str(self.connected))
            self.initConnectedStatus()
        else:
            self.myParent.after(100,self.checkConnectQueue)
            
    """ Create new Experiment Popup"""
    def initCreateExpPopup(self):
        # Creating a top level window
        self.createPopup = Toplevel(bg = self.background)
        self.createPopup.grab_set()
        
        self.createPopup.resizable(width=FALSE, height=FALSE)
        
        # Initializing header and name form
        self.createPopupL = Label(self.createPopup, text = "Create a new Experiment",fg=self.foreground, font = self.titlePopupfont, bg = self.background)
        self.createPopupL.grid(row=0, column=0, padx=self.paddinTitlePopup, pady=self.paddingPopup, columnspan = 2)
        
        self.nameL = Label(self.createPopup, text = "Name", bg = self.background, font = self.generalfont)
        self.nameL.grid(row=1, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)

        self.nameE = Entry(self.createPopup, font = self.generalfont)
        self.nameE.grid(row=1, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        # Initialize form depending on the type of experiment selected
        if(self.oldRadio == 1):
            self.initStep()
        else:
            self.initCustomInterval()
        
        # Init radio variable and set the radio to the selected option
        self.experimentType = IntVar()
        self.experimentType.set(self.oldRadio)
        
        # Radio Buttons
        self.stepR = Radiobutton(self.createPopup, text="Step", variable=self.experimentType, value=1, bg = self.background, font = self.generalfont, pady= self.paddingPopup, command = self.radioSel)
        self.stepR.grid(row=6, column=0, sticky = E)
        
        self.customIntervalR = Radiobutton(self.createPopup, text="Custom Intervals", variable=self.experimentType, value=2, bg = self.background, font = self.generalfont, command = self.radioSel)
        self.customIntervalR.grid(row=6, column=1, sticky = W)
        
        # Buttons for canceling or creating
        self.cancelB = Button(self.createPopup, text = "Cancel",fg = "black",bg="#F3A262", font = self.generalfont, command = self.closePopup)
        self.cancelB.grid(row=7, column=0, sticky = E+W)
        self.createB = Button(self.createPopup, text = "Create",fg = "black",bg="#F3A262", font = self.generalfont, command = self.startExperiment)
        self.createB.grid(row=7, column=1, sticky = W+E)
        
        self.createPopup.columnconfigure(0, weight = 1)
        self.createPopup.columnconfigure(1, weight = 1)
    
    """ Init step form """
    def initStep(self):
        # Label and entry boxes
        self.maxTemL = Label(self.createPopup, text = "Max Temperature", bg = self.background, font = self.generalfont)
        self.maxTemL.grid(row=2, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.maxTemE = Spinbox(self.createPopup, font = self.generalfont, from_=28, to=120, width = 18)
        self.maxTemE.grid(row=2, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        self.minTemL = Label(self.createPopup, text = "Min Temperature", bg = self.background, font = self.generalfont)
        self.minTemL.grid(row=3, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.minTemE = Spinbox(self.createPopup, font = self.generalfont, from_=27, to=120, width = 18)
        self.minTemE.grid(row=3, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        self.intervalL = Label(self.createPopup, text = "Interval", bg = self.background, font = self.generalfont)
        self.intervalL.grid(row=4, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.intervalE = Spinbox(self.createPopup, font = self.generalfont, from_=1, to=256, width = 18)
        self.intervalE.grid(row=4, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        self.timeL = Label(self.createPopup, text = "Time (min)", bg = self.background, font = self.generalfont)
        self.timeL.grid(row=5, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.timeE = Spinbox(self.createPopup, font = self.generalfont, from_=1, to=10, width = 18)
        self.timeE.grid(row=5, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)

    """ Init custom interval form"""        
    def initCustomInterval(self):
        
        self.setPointsL = Label(self.createPopup, text = "Setpoints", bg = self.background, font = self.generalfont)
        self.setPointsL.grid(row=2, column=0, columnspan = 2)
        
        # Frame for the list and other widgets
        self.listPopupFrame = Frame(self.createPopup, bg = self.background)
        self.listPopupFrame.grid(row=3, column=0, columnspan = 2)
        
        # Frame for the listbox
        self.listPack = Frame(self.listPopupFrame)
        self.listPack.grid(row=0,column=0, columnspan = 2, pady = self.paddingPopup)
        
        self.intervalList = Listbox(self.listPack, height=6)
        self.intervalList.pack(side=LEFT)
        
        self.yscrollInterval = Scrollbar(self.listPack,command=self.intervalList.yview, orient=VERTICAL)
        self.yscrollInterval.pack(side=RIGHT, fill = Y)
        
        self.intervalList.configure(yscrollcommand=self.yscrollInterval.set)
        
        # Button and entry for new temp
        self.addT = Label(self.listPopupFrame, text = "Add Temperature", bg = self.background, font = self.generalfont)
        self.addT.grid(row=1, column=0,padx = self.paddingPopup)
        self.addE = Spinbox(self.listPopupFrame, font = self.generalfont, from_=27, to=120, width = 8)
        self.addE.grid(row=1,column=1)
        self.addE.bind('<Return>', self.addTemp)
        
        # Frame for buttons
        self.buttonListFrame = Frame(self.listPopupFrame, bg = self.background)
        self.buttonListFrame.grid(row=2,column=0, columnspan =2)
        
        # Buttons
        self.addTempButton = Button(self.buttonListFrame, text = "Add",fg = "black",bg="#F3A262", font = self.generalfont)
        self.addTempButton.grid(row = 0, column = 0, pady = self.paddingPopup)
        # Bind the same function as enter in addE
        self.addTempButton.bind("<Button-1>", self.addTemp)
        
        self.deleteTempButton = Button(self.buttonListFrame, text = "Delete",fg = "black",bg="#F3A262", font = self.generalfont, command = self.deleteTemp)
        self.deleteTempButton.grid(row = 0, column = 1, pady = self.paddingPopup)

        self.fileTempButton = Button(self.buttonListFrame, text = "File",fg = "black",bg="#F3A262", font = self.generalfont)
        self.fileTempButton.grid(row = 0, column = 2, pady = self.paddingPopup)
        
    """ Add a temp to the list of custom interval"""        
    def addTemp(self,event):
        self.intervalList.insert(END,self.addE.get())
    
    """ Deleting a temp to the list of custom interval"""
    def deleteTemp(self):
        try:
            # get selected line index
            index = self.intervalList.curselection()[0]
            self.intervalList.delete(index)
        except IndexError:
            pass

    """ Depending of the radio button selected, show the step or custom interval form"""
    def radioSel(self):
        # This gets fired everything its click, check for changes
        if self.oldRadio != self.experimentType.get():
            self.oldRadio = self.experimentType.get()
            if self.oldRadio == 1:
                # If its a step
                self.intervalList.destroy()
                self.yscrollInterval.destroy()
                self.setPointsL.destroy()
                self.addT.destroy()
                self.addE.destroy()
                self.addTempButton.destroy()
                self.deleteTempButton.destroy()
                self.listPopupFrame.destroy()
                # Init Step
                self.initStep()
            else:
                # If its a custom interval
                self.minTemL.destroy()
                self.minTemE.destroy()
                self.maxTemE.destroy()
                self.maxTemL.destroy()
                self.intervalE.destroy()
                self.intervalL.destroy()
                # Init Custom Interval
                self.initCustomInterval()
    
    """ Close popup function for cancel button """
    def closePopup(self):
        self.createPopup.destroy()
    
    """ Called when a experiment is created in the popup form"""
    def startExperiment(self):
        global currentExp
        if self.oldRadio == 1:
            # Its a step experiment
            currentExp = { "name": self.nameE.get(),
                    "type": self.oldRadio,
                    "maxTemp": self.maxTemE.get(),
                    "minTemp": self.minTemE.get(),
                    "intervals": self.intervalE.get(),
                    "time": self.timeE.get()}
            # Creating file 'expName'.info to write the description of the experiment
            with open('./Experiments/'+self.nameE.get()+'.info', 'w') as outfile:
                json.dump(currentExp, outfile)
        else:
            # its a custom interval experiment
            # Get the list of temps from the interval List
            temps = self.intervalList.get(0, self.intervalList.size())
            currentExp = { "name": self.nameE.get(),
                    "type": self.oldRadio,
                    "setPoints": temps,
                    "time": self.timeE.get()}
            # Creating file 'expName'.info to write the description of the experiment
            with open('./Experiments/'+self.nameE.get()+'.info', 'w') as outfile:
                json.dump(currentExp, outfile)
                
        self.createPopup.destroy()
        
        # Add the experiment to the history list
        self.listBox.insert(END, currentExp["name"])
        
        # Sort history list and get the index of added item
        index = self.sort_list(currentExp["name"])
        
        # Highlight running exp in green
        self.listBox.itemconfig(index, bg = "green")
        
        # Init running experiment view
        self.time = 0
        self.initRunningExpView()
        self.tick()
        
    def tick(self):
        self.time += 1
        if self.runningExpFrame.winfo_exists():
            self.runningTimeL['text'] = 'Elapsed Time: ' + str(datetime.timedelta(seconds=self.time))  
        self.myParent.after(1000, self.tick)
    
    """ Initialize running Exp View"""
    def initRunningExpView(self):
        global currentExp
        
        # Destroy current View
        if self.homeFrame.winfo_exists():
            # If the home frame is running
            self.homeFrame.destroy()
        elif self.ExpFrame.winfo_exists():
            self.ExpFrame.destroy()
        else:
            # If person click the running exp again, return
            return
        
        # Create running Exp Frame
        self.runningExpFrame = Frame(self.right_frame, relief=RIDGE, bg = self.background)
        self.runningExpFrame.pack(fill = BOTH, expand = YES)
        
        # Title
        self.runningTitleL = Label(self.runningExpFrame,text="Running Experiment:\n"+currentExp["name"],fg=self.foreground,bg =self.background, font = self.titlefont)
        self.runningTitleL.grid(row=0,column=0,pady = self.paddingTitleExp)
        
        # Group frame to group every other remainding elements
        group = LabelFrame(self.runningExpFrame, padx=5, pady=5, bg = self.background)
        group.grid(row=1,column=0,pady = self.paddingTitleExp, ipadx = self.paddingGeneralExp*4)
        
        # Labels
        self.runningTimeL = Label(group,fg=self.foreground,bg =self.background, font = self.generalExpfont)
        self.runningTimeL['text'] = 'Elapsed Time: ' + str(datetime.timedelta(seconds=self.time))  
        self.runningTimeL.grid(row=0,column=0, pady = self.paddingGeneralExp, columnspan = 2)
        
        self.currentTempL = Label(group,text="Temperature: 41C",fg=self.foreground,bg =self.background, font = self.generalExpfont)
        self.currentTempL.grid(row=1,column=0, pady = self.paddingGeneralExp, columnspan = 2)
        
        self.percentageL = Label(group,text="Percentage: 75%",fg=self.foreground,bg =self.background, font = self.generalExpfont)
        self.percentageL.grid(row=2,column=0, pady = self.paddingGeneralExp, columnspan = 2)
        
        self.runningTableFrame = Frame(group, relief=RIDGE, bg = self.background)
        self.runningTableFrame.grid(row = 3,column =0, columnspan = 2)
        
        # List and scrollbar
        self.runningTreeScroll = Scrollbar(self.runningTableFrame)
        self.runningTreeScroll.pack(side=RIGHT,fill=Y)
        
        self.runningTable = Treeview(self.runningTableFrame,height="8", columns=("Time","Temperature","Resistance"), selectmode="none")
        self.runningTable.heading('#1', text='Time', anchor=CENTER)
        self.runningTable.heading('#2', text='Temperature', anchor=CENTER)
        self.runningTable.heading('#3', text='Resistance', anchor=CENTER)
        self.runningTable.column('#1', width = 120, anchor=CENTER)
        self.runningTable.column('#2', width = 120, anchor=CENTER)
        self.runningTable.column('#3', width = 120, anchor=CENTER)
        self.runningTable.column('#0', stretch=NO, minwidth=0, width=0)
        self.runningTable.pack(side=LEFT)
        
        self.runningTable.configure(yscrollcommand=self.runningTreeScroll.set)
        self.runningTreeScroll.config(command=self.runningTable)
        
        self.runningTable.insert("", "end", "", values=(("1:20","33C", "75K")), tag = 1)
        self.runningTable.insert("", "end", "", values=(("1:34","44C", "67K")), tag = 0)
        self.runningTable.insert("", "end", "", values=(("2:04","47C", "55K")), tag = 1)
        self.runningTable.insert("", "end", "", values=(("2:32","52C", "45K")), tag = 0)
        self.runningTable.insert("", "end", "", values=(("2:57","66C", "48K")), tag = 1)
        self.runningTable.insert("", "end", "", values=(("3:33","52C", "50K")), tag = 0)
        self.runningTable.insert("", "end", "", values=(("3:43","47C", "53K")), tag = 1)
        self.runningTable.insert("", "end", "", values=(("3:56","44C", "57K")), tag = 0)
        self.runningTable.tag_configure(1, background = "#EFEFEF",font = self.generalfont)
        self.runningTable.tag_configure(0,font = self.generalfont)
        
        # Abort Button
        self.abortB = Button(group, text = "Abort",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont)
        self.abortB.grid(row=4,column=0, pady = self.paddingGeneralExp*2, sticky = E+W)
        
        self.backBRunning = Button(group, text = "Back",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = self.backHomeRunning)
        self.backBRunning.grid(row=4,column=1, pady = self.paddingGeneralExp*2, sticky = E+W)
        
        # Column weights
        group.columnconfigure(0, weight = 1)
        group.columnconfigure(1, weight = 1)
        
        self.runningExpFrame.columnconfigure(0, weight = 1)
    
    """ Init Experiment Frame View"""
    def initExperimentFrameView(self,value):
        
        # Destroy current View
        if self.homeFrame.winfo_exists():
            # Destroy homeframe
            self.homeFrame.destroy()
        elif self.ExpFrame is not None:
            print("Exp not none")
            if self.ExpFrame.winfo_exists():
                # Destroy exp frame
                self.ExpFrame.destroy()
            else:
                self.runningExpFrame.destroy()
        else:
            print("Deleting running exp")
            self.runningExpFrame.destroy()
        
        # Get info file of the experiment
        # os.path.join returns a list of .info files, history and files are organize in the same manner
        # curselection returns a list of selected item
        # Only one item is selected [0] which correspond to the index in the os.path.list
        # TODO: DONT RELY ON THIS METHOD
        
        #index = int(self.listBox.curselection()[0])
        
        #file = glob.glob(os.path.join(os.getcwd()+"\Experiments", '*.info'))[int(self.listBox.curselection()[0])]
        #file = open(os.path.join(os.getcwd()+"\Experiments",'*.info') )
        
#         for filename in glob.glob(os.path.join(os.getcwd()+"\Experiments", '*.info')):
#             print (filename)
        
        json_data= open( os.path.join(os.getcwd()+"\Experiments", value + ".info"), "r" )
        self.info = json.load(json_data)
        
        # Get the result file of the experiment
        file = glob.glob(os.path.join(os.getcwd()+"\Experiments", '*.dat'))[int(self.listBox.curselection()[0])]
        json_data=open(file)
        results = json.load(json_data)
        
        # Create experiment Frame
        self.ExpFrame = Frame(self.right_frame, relief=RIDGE, bg = self.background)
        self.ExpFrame.pack(fill = BOTH, expand = YES)
        
        # Populate labels with the info
        self.expTitleL = Label(self.ExpFrame,text="Finished Experiment:\n"+self.info["name"],fg=self.foreground,bg =self.background, font = self.titlefont)
        self.expTitleL.grid(row=0,column=0,pady = self.paddingTitleExp, columnspan = 2)
        
        # Group frame to group every other remaining elements
        group = LabelFrame(self.ExpFrame, padx=5, pady=5, bg = self.background)
        group.grid(row=1,column=0,pady = self.paddingTitleExp, ipadx = self.paddingGeneralExp*4, columnspan = 2)
        
        self.expTimeL = Label(group,text="Time Elapsed: "+results["results"][len(results["results"]) - 1]["time"],fg=self.foreground,bg =self.background, font = self.generalExpfont)
        self.expTimeL.grid(row=1,column=0, pady = self.paddingGeneralExp, columnspan = 2)
        
        self.expTableFrame = Frame(group, relief=RIDGE, bg = self.background)
        self.expTableFrame.grid(row = 2,column =0, columnspan = 2)
        
        # List and scroll bar
        self.expTreeScroll = Scrollbar(self.expTableFrame)
        self.expTreeScroll.pack(side=RIGHT,fill=Y)
        
        self.expTable = Treeview(self.expTableFrame,height="8", columns=("Time","Temperature","Resistance"), selectmode="none")
        self.expTable.heading('#1', text='Time', anchor=CENTER)
        self.expTable.heading('#2', text='Temperature', anchor=CENTER)
        self.expTable.heading('#3', text='Resistance', anchor=CENTER)
        self.expTable.column('#1', width = 120, anchor=CENTER)
        self.expTable.column('#2', width = 120, anchor=CENTER)
        self.expTable.column('#3', width = 120, anchor=CENTER)
        self.expTable.column('#0', stretch=NO, minwidth=0, width=0)
        self.expTable.pack(side=LEFT)
        
        self.expTable.configure(yscrollcommand=self.expTreeScroll.set)
        
        # Populate table with results
        for i,value in enumerate(results["results"]):
            if i % 2 == 0:
                self.expTable.insert("", "end", "", values=((value["time"],value["temp"], value["resistance"])), tag = 1)
            else:
                self.expTable.insert("", "end", "", values=((value["time"],value["temp"], value["resistance"])), tag = 0)
        
        # Config table 
        self.expTable.tag_configure(1, background = "#EFEFEF",font = self.generalfont)
        self.expTable.tag_configure(0,font = self.generalfont)
        
        # Export and back buttons
        self.exportB = Button(group, text = "Export",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont)
        self.exportB.grid(row=3,column=0, pady = self.paddingGeneralExp, sticky = E+W)
        
        self.backB = Button(group, text = "Back",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = self.backHomeFinished)
        self.backB.grid(row=3,column=1, pady = self.paddingGeneralExp, sticky = E+W)
        
        # Column weight
        self.ExpFrame.columnconfigure(0, weight = 1)
        
        group.columnconfigure(0, weight = 1)
        group.columnconfigure(1, weight = 1)

    """ Function for back button in experiment frame """        
    def backHomeFinished(self):
        self.ExpFrame.destroy()
        self.initHomeView()
        
    """ Function for back button in running frame """        
    def backHomeRunning(self):
        self.runningExpFrame.destroy()
        self.initHomeView()
    
    """ History listbox callback function"""
    def viewExperiment(self, event):
        global currentExp
        # Get selected experiment
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print ('You selected item %d: "%s"' % (index, value))
        # Find if the experiment was running
        if currentExp == None:
            # No running experiment, start experiment frame
            print("init Experiment Frame")
            self.initExperimentFrameView(value)
        else:
            # Find if selected is a running experiment
            if currentExp["name"] == value:
                # is a running experiment
                print("init Running Experiment Frame 2")
                self.initRunningExpView()
            else:
                # Not a running experiment
                print("init Experiment Frame 2")
                self.initExperimentFrameView(value)
    
    def sort_list(self,name):
        temp_list = list(self.listBox.get(0, END))
        temp_list.sort(key=str.lower)
        # delete contents of present listbox
        self.listBox.delete(0, END)
        index = 0
        # load listbox with sorted data
        for i,item in enumerate(temp_list):
            self.listBox.insert(END, item)
            if(self.listBox.get(i) == name):
                index = i
        return index
        
if __name__ == "__main__":
    currentExp = None
    root = Tk();
    root.title("EOS Measuring System")
    app = eos(root)
    root.mainloop()