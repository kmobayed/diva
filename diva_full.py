#!/usr/bin/env python2.7
import Tkinter as tk    
from ttk import *
import ScrolledText
from git import *
import ConfigParser
import threading, time
import sys

class Application(tk.Frame):              
    
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        self.read_conf()
        self.init_git()
        self.run_thread()
        self.grid()
        self.createWidgets()
        self.master.protocol("WM_DELETE_WINDOW", self.quitAction)
    
    def read_conf(self):
	config = ConfigParser.RawConfigParser()
	config.read('diva.cfg')
	self.my_repo=config.get("git","my_repo")
	self.my_branch=config.get("git","my_branch")
	
	self.friends_repo=config.get("git","friends_repo")
	self.friends_repo=self.friends_repo.split(" ")
	
	self.friends_branch=config.get("git","friends_branch")
	self.friends_branch=self.friends_branch.split(" ")
	
	self.refresh_rate=int(config.get("diva","refresh_rate"))
	self.sync_limit=int(config.get("diva","sync_limit"))
      
    def init_git(self):
	repo = Repo(self.my_repo, odbt=GitDB)
	assert repo.bare ==False
	self.git = repo.git
	
    def run_thread(self):
	self.update_stop=threading.Event()
	self.thread=threading.Thread(target=self.threadUpdateRepo)
	self.thread.start()
	
    def threadUpdateRepo(self):
	while(not self.update_stop.is_set()):
	  self.git.remote("update")
	  #self.calculateDelta()
	  self.calculateGDtot()
	  self.update_stop.wait(self.refresh_rate)
	pass
    
    def createWidgets(self):
        self.frame1 = tk.LabelFrame(self,text="Detailed information:")
        self.frame1.grid(column=0,row=0,columnspan=1,rowspan=3,sticky='WEN', padx=5, pady=5, ipadx=5, ipady=5)

        self.logwnd = ScrolledText.ScrolledText(self.frame1,  state=tk.DISABLED)
        self.logwnd.grid(column=0,row=0,columnspan=1,sticky="WE",padx=5,pady=5)
        
        self.controlVarGDtot=tk.IntVar()
        self.controlVarDelta=tk.IntVar()
        self.controlVarState=tk.StringVar()

	self.frame2 = tk.LabelFrame(self)
        self.frame2.grid(row=0,column=7,columnspan=2,rowspan=4, sticky='WEN', padx=5, pady=5, ipadx=5, ipady=5)
    
	self.Label1 = tk.Label(self.frame2, text="GDtot=")
        self.Label1.grid(column=0,row=0,sticky='WE',padx=2,pady=2)
	self.GDtotLabel = tk.Label(self.frame2, textvariable=self.controlVarGDtot)
        self.GDtotLabel.grid(column=1,row=0,sticky='W',padx=2,pady=2)

        self.progress_barGDtot = Progressbar(self.frame2,orient=tk.HORIZONTAL,mode='determinate',variable=self.controlVarGDtot)
        self.progress_barGDtot.grid(column=0,row=1,columnspan=2,sticky='WE',padx=5,pady=2)
        
        self.Label2 = tk.Label(self.frame2, text="Distance=")
        self.Label2.grid(column=0,row=2,sticky='WE',padx=2,pady=2)
        self.DeltaLabel = tk.Label(self.frame2, textvariable=self.controlVarDelta)
        self.DeltaLabel.grid(column=1,row=2,sticky='W',padx=2,pady=2)

        #self.progress_barDelta = Progressbar(self.frame2,orient=tk.HORIZONTAL,mode='determinate',variable=self.controlVarDelta)
	#self.progress_barDelta.grid(column=0,row=3,columnspan=2,sticky='WE',padx=5,pady=2)
 
	#self.Label3 = tk.Label(self.frame2, text="State: ")
        #self.Label3.grid(column=0,row=3,sticky='WE',padx=2,pady=2)
        
        self.StateLabel = tk.Label(self.frame2, textvariable=self.controlVarState)
        self.StateLabel.grid(column=0,row=3,columnspan=2,sticky='WE',padx=2,pady=2)
        
        self.frame3= tk.LabelFrame(self,text="Commands:")
        self.frame3.grid(row=2,column=7,columnspan=2,sticky='WEN', padx=5, pady=5, ipadx=5, ipady=5)
        
        self.commitButton = tk.Button(self.frame3, text='Commit', command=self.commitAction)            
        self.commitButton.grid(sticky='WE',padx=5,pady=5)
        
        self.pullButton = tk.Button(self.frame3, text='Pull', command=self.pullAction)            
        self.pullButton.grid(sticky='WE',padx=5,pady=5)
        
        self.quitButton = tk.Button(self.frame3, text='Quit', command=self.quitAction)            
        self.quitButton.grid(sticky='WE',padx=5,pady=5)
              
        
    def quitAction(self):
      self.update_stop.set()
      if self.thread.isAlive():
	self.thread.join()
      self.master.quit()
      
    def commitAction(self):
      g = Git(self.my_repo)
      g.init()
      try:
	g.commit("--all", "--message=auto")
      except:
	instance = sys.exc_info()[1]
      pass
      
    def pullAction(self):
      g = Git(self.my_repo)
      g.init()
      g.pull()
      for repo in self.friends_repo:
	g.pull(repo)
      pass
       
    def calculateDelta(self):
	LM1=self.git.log("friend1/master..master",format="oneline")
	if (LM1 != ""):
	    LM1=LM1.split('\n')
	textLM1= str(len(LM1))
	
	LM2=self.git.log("friend2/master..master",format="oneline")
	if (LM2 != ""):
	    LM2=LM2.split('\n')
	textLM2= str(len(LM2))
	
	RM1=self.git.log("master..friend1/master",format="oneline")
	if (RM1 != ""):
	    RM1=RM1.split('\n')
	textRM1= str(len(RM1))
	
	RM2=self.git.log("master..friend2/master",format="oneline")
	if (RM2 != ""):
	    RM2=RM2.split('\n')
	textRM2= str(len(RM2))
	
	RM3=self.git.log("friend1/master..friend2/master",format="oneline")
	if (RM3 != ""):
	    RM3=RM3.split('\n')
	textRM3= str(len(RM3))
	
	RM4=self.git.log("friend2/master..friend1/master",format="oneline")
	if (RM4 != ""):
	    RM4=RM4.split('\n')
	textRM4= str(len(RM4))
	
	self.onLogMessage("1/2= "+textLM1 + "\t1/3= "+textLM2 + "\t2/1= "+ textRM1 + "\t2/3= " + textRM4+ "\t3/1= " + 
textRM2 + "\t3/2= " + textRM3)

    def calculateGDtot(self):
	H1=self.git.log(self.my_branch,format="oneline")
	if (H1 != ""):
	    H1=set(H1.split('\n'))
	textH1= str(len(H1))
	
	sumHi=len(H1)
	Hmax=H1
	textHi='\t'
	for branch in self.friends_branch:
	  log=self.git.log(branch,format="oneline")
	  if (log != ""):
	      Hi=set(log.split('\n'))
	  sumHi=sumHi+len(Hi)
	  Hmax=Hmax|Hi
	  textHi=textHi+branch+"= "+str(len(Hi))+"\t"
	
	textHmax=str(len(Hmax))	
	self.onLogMessage("H1= "+textH1 + textHi+ "\tHmax= " + textHmax)
	self.controlVarGDtot.set((len(self.friends_branch)+1)*len(Hmax)-sumHi)
	self.controlVarDelta.set(len(Hmax)-len(H1))
	
	if ((len(Hmax)-len(H1)) < self.sync_limit):
	  self.StateLabel.config(foreground='green')
	  self.controlVarState.set("OK")
	else:
	  self.StateLabel.config(foreground='red')
	  self.controlVarState.set("ATTENTION")
	  
    def onLogMessage(self, text):
	w = self.logwnd
	w.configure(state=tk.NORMAL)
	w.insert(tk.END, text)
	w.insert(tk.END, "\n")
	w.see(tk.END)
	w.configure(state=tk.DISABLED)
	pass
      
      
app = Application()                       
app.master.title('Divergence Awareness Widget')
app.master.geometry('800x390+100+50')
app.mainloop()
