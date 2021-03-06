from tkinter import *
from tkinter.ttk import Treeview
from tkinter.constants import DISABLED
import connect
import json,os,glob,threading,queue,datetime, tkinter.messagebox, serial.tools.list_ports, re,time,csv
from math import floor
from tkinter.filedialog import FileDialog

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
        
        self.tickID = None
        self.bufferID = None
        
        
        """ Init Windows """
        
        # Parent
        self.myParent = parent
        self.myParent.minsize(800, 600)
        self.myParent.protocol('WM_DELETE_WINDOW', self.closingWindow)
        
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
        # Label for port connection
        self.connectL = Label(self.portFrame,text = "Connect to Port: ",fg=self.foreground, bg = self.background, font = self.generalfont)
        
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
        
        # Label and dropdown for port connection
        self.connectL = Label(self.portFrame,text = "Connect to Port: ",fg=self.foreground, bg = self.background, font = self.generalfont)
        # Get port list
        ports = list(serial.tools.list_ports.comports())
        portNames = list()
        for port in ports:
            portNames.append(port[0])
        self.portDropS = StringVar()
        self.portDropS.set(portNames[0])
        self.portDrop = OptionMenu(self.portFrame, self.portDropS, *portNames)
        
        #self.connectE = Entry(self.portFrame, font = self.generalfont)
        
        # Modify Label and button state
        self.statusL["text"] = "System not connected"
        self.connectB["text"] = "Connect"
        self.connectB["state"] = NORMAL
        self.createExperimentB["state"] = DISABLED
        
        # Pack connect options
        self.connectL.pack(side=LEFT)
        self.portDrop.pack(side=RIGHT)
        
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
            port = self.portDropS.get()
            print (port)
            try:
                self.connected = connect.Connection(port, self.queue)
                self.queue.put(self.connected)
            except:
                tkinter.messagebox.showwarning("Opening Port","Unavailable to connect to the port")
                e = sys.exc_info()[0]
                print(e)
                
        def callbackClose():
            # Close port
            try:
                self.connected.closePort()
                self.connected = None
                self.queue.put(1)
            except:
                tkinter.messagebox.showwarning("Closing Port","Unavailable to close to the port")
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
                # Init Connection
                self.connected.initUI()
                self.initConnectedStatus()
            except:
                tkinter.messagebox.showwarning("Opening Port","Unavailable to connect to the port")
                print("Error! " + str(self.connected))
                self.connected = None
        else:
            self.myParent.after(100,self.checkConnectQueue)
            
    def checkBufferQueue(self):
        def callback():
            global currentExp
            try:
                if self.runningExpFrame.winfo_exists():
                    if not self.queue.empty():
                        header = ''
                        try:
                            header = self.queue.get()
                        except:
                            pass
                        if header == b'0':
                            # temp update
                            temp = ''
                            nextChar = self.queue.get()
                            while(nextChar != b'\n'):
                                temp += nextChar.decode()
                                nextChar = self.queue.get()
                            print (temp)
                            self.currentTempL['text'] = 'Temperature: ' + temp
                        elif header == b'1':
                            # resistance update
                            resistance = ''
                            nextChar = self.queue.get()
                            while(nextChar != b'\n'):
                                resistance += nextChar.decode()
                                nextChar = self.queue.get()
                            print (resistance)
                            t = threading.Thread(target=self.saveTable,args=[self.runningTimeL["text"].split(" ")[2],self.currentTempL["text"].split(" ")[1],resistance])
                            t.start()
            except:
                print ("Exp frame not running")
            
            self.bufferID = self.myParent.after(1000,callback)
        t = threading.Thread(target=callback)
        t.start()
            
    def saveTable(self,time,temp,resistance):
        global currentExp
        newSetpoint = {"temp": temp,
                       "time": time,
                       "resistance": resistance
                       }
        if currentExp["current"] % 2 == 0:
            self.runningTable.insert("", "end", "", values=((time,temp,resistance)), tag = 1)
        else:
            self.runningTable.insert("", "end", "", values=((time,temp,resistance)), tag = 0)
            
        currentExp["current"] = currentExp["current"] + 1
        current = int(currentExp["current"])
        
        if currentExp["type"] == 1:
            #its a step experiment
            maxTemp = int(currentExp["maxTemp"])
            minTemp = int(currentExp["minTemp"])
            intervals = int(currentExp["intervals"])
            
            testingStep = (maxTemp-minTemp)/intervals
            if testingStep == round(testingStep):
                percentage = current/(testingStep * 2 + 1) * 100
            else:
                percentage = current/(floor(testingStep) * 2 -1) *100
            
            self.percentageL["text"] = "Percentage: " + "{0:.2f}".format(percentage) + "%"
        else:
            size = len(currentExp["setPoints"])
            percentage = current/(size*2-1) * 100
            self.percentageL["text"] = "Percentage: " + "{0:.2f}".format(percentage) + "%"
        
        if os.path.exists(".\Experiments\\"+ currentExp["name"] +".dat"):
            file =open(".\Experiments\\"+ currentExp["name"] +".dat",'r')
            expElements = json.load(file)
            file.close()
            file=open(".\Experiments\\"+ currentExp["name"] +".dat",'w+')
        else:
            file=open(".\Experiments\\"+ currentExp["name"] +".dat",'w+')
            expElements  = { "results": []}
        expElements["results"].append(newSetpoint)
        json.dump(expElements,file)
        file.close()
        if int(percentage) == 100:
            print("Finished!")
            # init time
            self.time = 0
            # Cancel tick callback
            root.after_cancel(self.tickID)
            # cancle queue
            root.after_cancel(self.bufferID)
            temp = currentExp["name"]
            for i,item in enumerate(self.listBox.get(0, END)):
                if currentExp["name"] == item:
                    self.listBox.itemconfig(i, bg = "white")
                    break
            currentExp = None
            self.myParent.after(100,self.backHomeRunning())
            
    
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
        
        self.timeL = Label(self.createPopup, text = "Time (min)", bg = self.background, font = self.generalfont)
        self.timeL.grid(row=5, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.timeE = Spinbox(self.createPopup, font = self.generalfont, from_=1, to=10, width = 18)
        self.timeE.grid(row=5, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
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
        self.minTemL = Label(self.createPopup, text = "Min Temperature", bg = self.background, font = self.generalfont)
        self.minTemL.grid(row=2, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.minTemE = Spinbox(self.createPopup, font = self.generalfont, from_=20, to=120, width = 18)
        self.minTemE.grid(row=2, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        # Label and entry boxes
        self.maxTemL = Label(self.createPopup, text = "Max Temperature", bg = self.background, font = self.generalfont)
        self.maxTemL.grid(row=3, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.maxTemE = Spinbox(self.createPopup, font = self.generalfont, from_=21, to=120, width = 18)
        self.maxTemE.grid(row=3, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)
        
        self.intervalL = Label(self.createPopup, text = "Interval", bg = self.background, font = self.generalfont)
        self.intervalL.grid(row=4, column=0, padx=self.paddingPopup, pady=self.paddingPopup, sticky = E)
        self.intervalE = Spinbox(self.createPopup, font = self.generalfont, from_=1, to=255, width = 18)
        self.intervalE.grid(row=4, column=1, padx=self.paddingPopup, pady=self.paddingPopup, sticky = W)

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
        self.addE = Spinbox(self.listPopupFrame, font = self.generalfont, from_=20, to=120, width = 8)
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

#         self.fileTempButton = Button(self.buttonListFrame, text = "File",fg = "black",bg="#F3A262", font = self.generalfont)
#         self.fileTempButton.grid(row = 0, column = 2, pady = self.paddingPopup)
        
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
            self.stepChecker()
            currentExp = { "name": self.nameE.get(),
                    "type": self.oldRadio,
                    "maxTemp": self.maxTemE.get(),
                    "minTemp": self.minTemE.get(),
                    "intervals": self.intervalE.get(),
                    "time": self.timeE.get(),
                    "current": 0}
            # Creating file 'expName'.info to write the description of the experiment
            with open('./Experiments/'+self.nameE.get()+'.info', 'w') as outfile:
                json.dump(currentExp, outfile)
            # Send Exp commands
            self.connected.initStepExperiment(currentExp)
            # Init updater
            self.connected.updater()
            self.checkBufferQueue()
        else:
            # its a custom interval experiment
            # Get the list of temps from the interval List
            temp_list = list(self.intervalList.get(0, END))
            temp_list.sort(key=str.lower)
            currentExp = { "name": self.nameE.get(),
                    "type": self.oldRadio,
                    "setPoints": temp_list,
                    "time": self.timeE.get(),
                    "current": 0}
            # Creating file 'expName'.info to write the description of the experiment
            with open('./Experiments/'+self.nameE.get()+'.info', 'w') as outfile:
                json.dump(currentExp, outfile)
            # Send Exp commands
            self.connected.initPreSetExperiment(currentExp)
            # Init updater
            self.connected.updater()
            self.checkBufferQueue()
                
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
       
    """ Tick tack """ 
    def tick(self):
        self.time += 1
        if self.runningExpFrame.winfo_exists():
            self.runningTimeL['text'] = 'Elapsed Time: ' + str(datetime.timedelta(seconds=self.time))  
        self.tickID = self.myParent.after(1000, self.tick)
    
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
        
        self.currentTempL = Label(group, text="Temperature: X",fg=self.foreground,bg =self.background, font = self.generalExpfont)
        self.currentTempL.grid(row=1,column=0, pady = self.paddingGeneralExp, columnspan = 2)
        
        self.percentageL = Label(group, text="Percentage: 0.00%", fg=self.foreground,bg =self.background, font = self.generalExpfont)
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
        
        if currentExp["current"] >= 1:
            # Load file
            json_data=open('./Experiments/'+currentExp["name"]+'.dat', 'w')
            # Get json data
            expElement = json.load(json_data)
            for i,item in enumerate(expElement["results"]):
                if i % 2 == 0:
                    self.runningTable.insert("", "end", "", values=((item["time"],item["temp"],item["resistance"])), tag = 1)
                else:
                    self.runningTable.insert("", "end", "", values=((item["time"],item["temp"],item["resistance"])), tag = 0)
        
        self.runningTable.tag_configure(1, background = "#EFEFEF",font = self.generalfont)
        self.runningTable.tag_configure(0,font = self.generalfont)
        
        # Abort Button
        self.abortB = Button(group, text = "Abort",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = self.abort)
        self.abortB.grid(row=4,column=0, pady = self.paddingGeneralExp*2, sticky = E+W)
        
        self.backBRunning = Button(group, text = "Back",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = self.backHomeRunning)
        self.backBRunning.grid(row=4,column=1, pady = self.paddingGeneralExp*2, sticky = E+W)
        
        # Column weights
        group.columnconfigure(0, weight = 1)
        group.columnconfigure(1, weight = 1)
        
        self.runningExpFrame.columnconfigure(0, weight = 1)
    
    """ Init Experiment Frame View"""
    def initExperimentFrameView(self,value):
        
        filename = os.path.join(os.getcwd()+"\Experiments", value + ".info")
        
        # Opening info and data files
        try:
            json_data = open( filename, "r" )
        except:
            tkinter.messagebox.showwarning("Opening info file","Cannot open this file\n(%s)" % filename)
            return
            
        self.info = json.load(json_data)
        json_data.close()
        
        filename =  os.path.join(os.getcwd()+"\Experiments", value + ".dat")
        
        try:
            json_data = open(filename , "r")
            # Get the result file of the experiment
            results = json.load(json_data)
        except:
            tkinter.messagebox.showwarning("Open dat file","Cannot open this file\n(%s)" % filename)
            self.listBox.delete(self.listBox.curselection()[0])
            os.remove(os.path.join(os.getcwd()+"\Experiments", value + ".info"))
            return
        
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
        for i,item in enumerate(results["results"]):
            if i % 2 == 0:
                self.expTable.insert("", "end", "", values=((item["time"],item["temp"], item["resistance"])), tag = 1)
            else:
                self.expTable.insert("", "end", "", values=((item["time"],item["temp"], item["resistance"])), tag = 0)
        
        # Config table 
        self.expTable.tag_configure(1, background = "#EFEFEF",font = self.generalfont)
        self.expTable.tag_configure(0,font = self.generalfont)
        
        # Export and back buttons
        self.exportB = Button(group, text = "Export",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = lambda: self.export(results["results"]))
        self.exportB.grid(row=3,column=0, pady = self.paddingGeneralExp, sticky = E+W)
        
        self.backB = Button(group, text = "Back",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = self.backHomeFinished)
        self.backB.grid(row=3,column=1, pady = self.paddingGeneralExp, sticky = E+W)
        
        self.deleteB = Button(group, text = "Delete",fg = "black",bg="#F3A262", pady = self.buttonPady, font = self.generalExpfont, command = lambda: self.deleteExperiment(value))
        self.deleteB.grid(row=4,column=0, pady = self.paddingGeneralExp, sticky = E+W,columnspan = 2)
        
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
    
    """ Sorts the history list """
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
    
    """ Abort callback for a running experiment"""
    def abort(self):
        global currentExp
        if tkinter.messagebox.askyesno("Abort", "Abort this experiment?\nData will be save"):
            # init time
            self.time = 0
            # Cancel tick callback
            root.after_cancel(self.tickID)
            # cancle queue
            root.after_cancel(self.bufferID)
            # delete 
            try:
                # Check if theres a dat file
                open(os.path.join(os.getcwd()+"\Experiments", currentExp["name"] + ".dat"))
                # theres a dat keep the experiment, just remove green thingy
                for i,item in enumerate(self.listBox.get(0, END)):
                    if currentExp["name"] == item:
                        self.listBox.itemconfig(i, bg = "white")
                        break
            except:
                # if not delete the experiment for good
                os.remove(os.path.join(os.getcwd()+"\Experiments", currentExp["name"] + ".info"))
                # Remove experiment from listbox 
                for i,item in enumerate(self.listBox.get(0, END)):
                    if currentExp["name"] == item:
                        self.listBox.delete(i)
                        break
            # Delete current experiment reference
            currentExp = None
            self.backHomeRunning()
            self.connected.sendByte(self.connected.ABORT)
            
    def export(self, results):
        filename = ''
        try:
            options = {}
            options['defaultextension'] = '.csv'
            filename = tkinter.filedialog.asksaveasfilename(**options)
            if filename == '':
                return
            file = open(filename,"w+")
            writer = csv.writer(file)
        except:
            tkinter.messagebox.showwarning("Export","Could not save file " + filename)
        writer.writerow( ('Time', 'Temperature', 'Resistance') )
        for item in results:
            writer.writerow( (item["time"], item["temp"],item["resistance"]) )
        file.close()
    
    def stepChecker(self):
        if re.match(r'^[\w\d_()]*',self.nameE.get()):
            print ('yes')
        else: 
            print ('false')
    
    def closingWindow(self):
        global currentExp
        if currentExp is not None:
            if tkinter.messagebox.askyesno("Closing", "A current experiment is running\n Do you wish to cancel it?"):
                self.connected.sendByte(self.connected.ABORT)
                self.deleteExperiment(currentExp["name"],False)
                self.connected.closePort()
                self.myParent.destroy()
        elif self.connected is not None:
            try:
                self.connected.closePort()
            except:
                pass
            self.myParent.destroy()
        else:
            self.myParent.destroy()

    def deleteExperiment(self,value,ask = True):
        # Warn the user if needed
        if ask:
            # Clicking delete button
            if tkinter.messagebox.askyesno("Delete", "Delete experiment?"): 
                self.listBox.delete(self.listBox.curselection()[0])
                os.remove(os.path.join(os.getcwd()+"\Experiments", value + ".info"))
                try:
                    os.remove(os.path.join(os.getcwd()+"\Experiments", value + ".dat"))
                except:
                    print("no .dat file")
                self.backHomeFinished()
        else:
            # Closing Window
            os.remove(os.path.join(os.getcwd()+"\Experiments", value + ".info"))
            try:
                os.remove(os.path.join(os.getcwd()+"\Experiments", value + ".dat"))
            except:
                print("no .dat file")
    
if __name__ == "__main__":
    currentExp = None
    root = Tk()
    root.title("EOS Measuring System")
    eos(root)
    root.mainloop()