#!/usr/bin/env python2.7
import Tkinter as tk   
import ttk
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
	self.always_ontop=int(config.get("diva","always_ontop"))
      
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
	  self.calculateGDtot()
	  self.update_stop.wait(self.refresh_rate)
	pass
    
    def createWidgets(self):    
        self.controlVarGDtot=tk.IntVar()
        self.controlVarDelta=tk.IntVar()
        self.controlVarState=tk.StringVar()

	self.Label1 = tk.Label(self, text="GDtot=")
        self.Label1.grid(column=0,row=0,sticky='WE',padx=2,pady=2)
	self.GDtotLabel = tk.Label(self, textvariable=self.controlVarGDtot)
        self.GDtotLabel.grid(column=1,row=0,sticky='W',padx=2,pady=2)

        self.progress_barGDtot = ttk.Progressbar(self,orient=tk.HORIZONTAL,mode='determinate',variable=self.controlVarGDtot)
        self.progress_barGDtot.grid(column=0,row=1,columnspan=2,sticky='WE',padx=5,pady=2)
        
        self.Label2 = tk.Label(self, text="Distance=")
        self.Label2.grid(column=0,row=2,sticky='WE',padx=2,pady=2)
        self.DeltaLabel = tk.Label(self, textvariable=self.controlVarDelta)
        self.DeltaLabel.grid(column=1,row=2,sticky='W',padx=2,pady=2)

        self.StateLabel = tk.Label(self, textvariable=self.controlVarState)
        self.StateLabel.grid(column=0,row=3,columnspan=2,sticky='WE',padx=2,pady=2)
        
        self.quitButton = tk.Button(self, text='Quit', command=self.quitAction)            
        self.quitButton.grid(sticky='WE',columnspan=2,padx=5,pady=5)
                   
    def quitAction(self):
      self.update_stop.set()
      if self.thread.isAlive():
	self.thread.join()
      self.master.quit()

    def calculateGDtot(self):
	H1=self.git.log(self.my_branch,format="oneline")
	if (H1 != ""):
	    H1=set(H1.split('\n'))
	
	sumHi=len(H1)
	Hmax=H1
	for branch in self.friends_branch:
	  log=self.git.log(branch,format="oneline")
	  if (log != ""):
	      Hi=set(log.split('\n'))
	  sumHi=sumHi+len(Hi)
	  Hmax=Hmax|Hi
	
	self.controlVarGDtot.set((len(self.friends_branch)+1)*len(Hmax)-sumHi)
	self.controlVarDelta.set(len(Hmax)-len(H1))
	
	if ((len(Hmax)-len(H1)) < self.sync_limit):
	  self.StateLabel.config(foreground='green')
	  self.controlVarState.set("OK")
	else:
	  self.StateLabel.config(foreground='red')
	  self.controlVarState.set("ATTENTION")
	    
app = Application() 
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight() 
Xpos=str(screen_width-120)
app.master.title('diva')
app.master.geometry('115x130+'+Xpos+'+50')
app.master.overrideredirect(app.always_ontop)
app.master.wm_iconbitmap(bitmap = "@diva.xbm")
app.mainloop()
