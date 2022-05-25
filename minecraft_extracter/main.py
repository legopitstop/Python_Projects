from tkinter import DISABLED, E, EW, LEFT,NORMAL, RIGHT, W, BooleanVar, Button, Checkbutton, Entry, Frame, Label, OptionMenu, StringVar,LabelFrame, filedialog,messagebox,IntVar
from tkinter.ttk import Progressbar
from UserFolder import User
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry,CTkCheckBox,CTkProgressBar
import os,zipfile,threading,shutil,json,re,winsound,logging,customtkinter

customtkinter.set_appearance_mode('System')
customtkinter.set_default_color_theme('blue')

LOCAL = os.path.dirname(os.path.realpath(__file__))

user = User('com.legopitstop.minecraft_extracter')
logging.basicConfig(format='[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%I:%M:%S', filename=os.path.join(user.get(),'latest.log'), filemode='w', encoding='utf-8', level=logging.DEBUG)

class App(CTk):
    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger('App')
        if user.exists('config.json'):
            self.logger.info('Loading config...')
            opn = user.open('config.json','r')
            self._config = json.load(opn)
            opn.close()
        else:
            self.logger.info('Creating config...')
            versions = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','versions')
            objects = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','objects')
            indexes = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','indexes')
            output = os.path.join(os.path.expanduser('~'),'Downloads')

            self._config={"JarExtractor": {"enabled": True,"assets": True,"data": True,"versions": versions,"version": "unset" },"ObjectExtractor": {"enabled": False,"objects": objects,"indexes":indexes,"index":"unset"},"output": output,"show": True}
            self.save_config(user,self._config)

        self.title('Minecraft Extractor')
        self.iconbitmap(LOCAL+'/icon.ico')
        # self.resizable(False,False)
        self.protocol('WM_DELETE_WINDOW', self.exit)

        # Varables
        self.ENABLEJE=BooleanVar()
        self.ENABLEJE.set(self._config['JarExtractor']['enabled'])
        self.ASSETS=BooleanVar()
        self.ASSETS.set(self._config['JarExtractor']['assets'])
        self.DATA=BooleanVar()
        self.DATA.set(self._config['JarExtractor']['data'])
        self.SRC=StringVar()
        self.SRC.set(self._config['JarExtractor']['version'])
        self.INDEX=StringVar()
        self.INDEX.set(self._config['ObjectExtractor']['index'])
        self.ENABLEOE=BooleanVar()
        self.ENABLEOE.set(self._config['ObjectExtractor']['enabled'])
        self.OBJ=StringVar()
        self.OBJ.set(self._config['ObjectExtractor']['objects'])
        self.DST=StringVar()
        self.DST.set(self._config['output'])
        self.SHOW=BooleanVar()
        self.SHOW.set(self._config['show'])
        self.PROGRESS=IntVar()
        self.PROGRESS.set(0)

        # Functions
        def get_versions():
            ver = self._config['JarExtractor']['versions']
            if os.path.exists(ver):
                vers=['unset']
                for v in os.listdir(ver):
                    if os.path.isfile(ver+'/'+v)==False:
                        for i in os.listdir(ver+'/'+v):
                            if i.endswith('.jar'):
                                # print(i)
                                vers.append(re.sub(r'\.jar$','',i))

                return vers
            else:
                opn = messagebox.askyesno('ERROR','Invalid version folder! Do you want to open the configureation file?')
                if opn == True:
                    user.show('config.json')
                return ["unset"]

        def get_indexes():
            ver = self._config['ObjectExtractor']['indexes']
            if os.path.exists(ver):
                ind=['unset']
                for i in os.listdir(ver):
                    if os.path.isfile(ver)==False:
                        if i.endswith('.json'):
                            ind.append(re.sub(r'\.json$','',i))
                return ind
            else:
                opn = messagebox.askyesno('ERROR','Invalid index folder! Do you want to open the configureation file?')
                if opn == True:
                    user.show('config.json')
                return ["unset"]

        def choose(varable,type):
            if type=='dir':
                path = filedialog.askdirectory(initialdir=varable.get(),mustexist=True)
                if path!='':
                    varable.set(path)

            elif type=='jar':
                types=[
                    ('Jar','.jar')
                ]
                path = filedialog.askopenfilename(defaultextension='.jar',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            elif type=='json':
                types=[
                    ('JSON','.json')
                ]
                path = filedialog.askopenfilename(defaultextension='.json',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            else:
                self.logger.warning('Unknown choose type "%s"',type)

        def start():  
            threading.Thread(target=self.extract).start()

        WRAPPER = CTkFrame(self)
        CTkLabel(WRAPPER,text='This tool is for extracting Minecraft\'s assets and data').grid(row=0,column=0,columnspan=2,pady=5,padx=5,sticky=EW)

        JE = CTkFrame(WRAPPER)
        check = CTkFrame(JE)
        CTkCheckBox(check,text='Enable',border_width=1,variable=self.ENABLEJE,command=self._update).grid(row=0,column=0)
        assets = CTkCheckBox(check,text='Assets',border_width=1,variable=self.ASSETS,command=self._update)
        assets.grid(row=0,column=1)
        data = CTkCheckBox(check,text='Data',border_width=1,variable=self.DATA,command=self._update)
        data.grid(row=0,column=2)
        check.grid(row=0,column=0,sticky=W)
        CTkLabel(JE,text='The version to extract:').grid(row=1,column=0,sticky=W)
        self.src = OptionMenu(JE,self.SRC,*get_versions())
        self.src.grid(row=2,column=0,sticky=W)
        JE.grid(row=1,column=0,pady=2,padx=2,sticky='nesw')

        OE = CTkFrame(WRAPPER)
        CTkCheckBox(OE,text='Enable',variable=self.ENABLEOE,border_width=1,command=self._update).grid(row=0,column=0,sticky=W)
        CTkLabel(OE,text='The folder that contains all the objects:').grid(row=1,column=0,sticky=W)
        objEntry = CTkEntry(OE,textvariable=self.OBJ,width=65)
        objEntry.grid(row=2,column=0,sticky=W)
        objBtn = CTkButton(OE,text='Browse...',command=lambda: choose(self.OBJ,'dir'))
        objBtn.grid(row=2,column=1,padx=5,sticky=W)
        CTkLabel(OE,text='The index version:').grid(row=3,column=0,sticky=W)
        index = OptionMenu(OE,self.INDEX,*get_indexes())
        index.grid(row=4,column=0,sticky=W)
        OE.grid(row=1,column=1,pady=2,padx=2,sticky='nesw')

        WRAPPER.grid(row=0,column=0,pady=5,padx=5,sticky=EW)

        GLOBE = CTkFrame(self)
        CTkLabel(GLOBE,text='Files will be extracted to this folder:').grid(row=0,column=0,sticky=W)
        CTkEntry(GLOBE,textvariable=self.DST,width=65).grid(row=1,column=0,sticky=W)
        CTkButton(GLOBE,text='Browse...',command=lambda: choose(self.DST,'dir')).grid(row=1,column=1,padx=5,sticky=W)
        CTkCheckBox(GLOBE,text='Show extracted files when complete',variable=self.SHOW,onvalue=True,offvalue=False).grid(row=2,columnspan=2,column=0,sticky=W)
        GLOBE.grid(row=1,column=0,pady=5,padx=5,sticky=EW)
        
        # Foot
        foot = CTkFrame(self)
        label = CTkFrame(foot)
        self.PROGRESS_LABEL = CTkLabel(label,text='Waiting...')
        self.PROGRESS_LABEL.grid(row=0,column=0,sticky=W)

        self.PROGRESS_FILE = CTkLabel(label)
        self.PROGRESS_FILE.grid(row=0,column=1,sticky=W)

        label.grid(row=0,column=0,sticky=EW)

        self.PROGRESSBAR = CTkProgressBar(foot,variable=self.PROGRESS)
        self.PROGRESSBAR.grid(row=1,column=0,padx=2,sticky=EW)
        self.EXTRACTBTN = CTkButton(foot,text='Extract',command=start)
        self.EXTRACTBTN.grid(row=0,column=1,rowspan=2,padx=2,pady=2,sticky=E)
        CTkButton(foot,text='Cancel',command=self.exit).grid(row=0,column=2,rowspan=2,padx=2,pady=2,sticky=E)
        foot.grid(row=2,column=0,pady=5,padx=5,sticky=EW)

        # Responsive
        self.grid_columnconfigure(0,weight=1)
        WRAPPER.grid_columnconfigure(0,weight=1)
        WRAPPER.grid_columnconfigure(1,weight=1)
        foot.grid_columnconfigure(0,weight=1)

        # Update
        self._update()

    def _update(self):
        # if self.ENABLEJE.get():
        #     self.src.configure(state=NORMAL)
        #     self.assets.configure(state=NORMAL)
        #     self.data.configure(state=NORMAL)
        # else:
        #     self.src.configure(state=DISABLED)
        #     self.assets.configure(state=DISABLED)
        #     self.data.configure(state=DISABLED)

        # if self.ENABLEOE.get():
        #     self.src.configure(state=NORMAL)
        #     self.assets.configure(state=NORMAL)
        #     self.data.configure(state=NORMAL)
        # else:
        #     self.src.configure(state=DISABLED)
        #     self.assets.configure(state=DISABLED)
        #     self.data.configure(state=DISABLED)
        print('Update widgets')

    def exit(self):
        """Properly close the program"""
        self.destroy()

    def status(self,text:str=None,filename:str=None,maximum:int=None,mode:str='determinate'):
        if text!=None: self.PROGRESS_LABEL['text']=text
        if maximum: self.PROGRESSBAR['maximum']=maximum
        if mode: self.PROGRESSBAR['mode']=mode

        if filename!=None:
            lbl = len(self.PROGRESS_LABEL['text'])
            file = len(str(filename))
            total = 80
            allowed = total-lbl
            if file>allowed:
                remove = file-allowed
                new = re.sub(re.compile('^(.){%s}'%(remove)),'',filename)
                self.PROGRESS_FILE['text']=new
            else:
                self.PROGRESS_FILE['text']=filename

    def save_config(self,user,config):
        # Update values
        self.logger.info('Saving config...')
        try:
            config['JarExtractor']['enabled'] = self.ENABLEJE.get()
            config['JarExtractor']['assets'] = self.ASSETS.get()
            config['JarExtractor']['data'] = self.DATA.get()
            config['ObjectExtractor']['enabled'] = self.ENABLEOE.get()
            config['ObjectExtractor']['objects'] = self.OBJ.get()
            config['ObjectExtractor']['index'] = self.INDEX.get()
            config['output'] = self.DST.get()
            config['show'] = self.SHOW.get()
            config['JarExtractor']['version'] = self.SRC.get()
        except: pass

        opn=user.open('config.json','w')
        opn.write(json.dumps(config,indent=4))
        opn.close()

    CALCFILES=0
    def calcFiles(self,dir:str,silent:bool=False,reset:bool=True):
        """Calculates the total amount of files, including files inside of folders"""
        if reset==True:
            self.CALCFILES=0
            self.PROGRESS.set(0)
            self.status('','')

        for file in os.listdir(dir):
            filename = os.path.join(dir,file)

            if os.path.isfile(filename):
                if silent!=True:
                    self.status('Discovered %s items...'%(self.CALCFILES),'')
                self.CALCFILES+=1
            elif os.path.isdir(filename):
                self.calcFiles(filename,silent,False)

    COPYDIR=0
    def copydir(self,src:str,dst:str,display:str,reset:bool=True):
        """Copies dir from src to dst."""
        files = os.listdir(src)
        if os.path.exists(dst)==False:
            os.makedirs(dst)
        
        if reset==True:
            self.COPYDIR=0
            # Save status
            old = self.PROGRESS_LABEL['text']

            # Go through and calculate the max amount of files
            self.calcFiles(src)
            self.status(text=old,maximum=self.CALCFILES)

        for filename in files:
            source = src+'\\' + filename
            destination = dst+'\\' + filename
            if os.path.exists(source) and os.path.isfile(source):
                if display=='filename': self.status(filename=source)
                elif display=='items': self.status(filename='%s of %s items'%(self.COPYDIR, self.CALCFILES))
                shutil.copy(source, destination)
            else:
                self.copydir(source+'\\',destination+'\\',display,False)
            self.PROGRESS.set(self.COPYDIR)
            self.COPYDIR+=1

    CLEANUP=0
    def cleanup(self,src,reset:bool=True):
        list = os.listdir(src)
        if reset:
            CLEANUP=0
            self.calcFiles(src)
            self.status('Cleaning Up','',self.CALCFILES)
        
        for i in list:
            if os.path.isfile(src+'/'+i):
                os.remove(src+'/'+i)
                self.status(filename='%s of %s items'%(self.CLEANUP, self.CALCFILES))
                self.PROGRESS.set(self.CLEANUP)
                self.CLEANUP+=1
            else:
                self.cleanup(src+'/'+i,False)
        
        try: os.rmdir(src)
        except: pass

    # Make seperate lib
    def extract(self):
        self.save_config(user,self._config)
        err=False
        # Create TEMP
        self.EXTRACTBTN['state'] = DISABLED
        if os.path.exists(LOCAL+'/_temp/')==False:
            os.makedirs(LOCAL+'/_temp/')
        if self.ENABLEJE.get()==True:
            src =  os.path.join(self._config['JarExtractor']['versions'],self.SRC.get(),self.SRC.get()+'.jar')
            if os.path.exists(src) and os.path.isfile(src) and self.SRC.get()!='unset':
                # Extract
                self.logger.info('Extracting jar...')
                with zipfile.ZipFile(src) as zf:
                    total = len(zf.infolist())
                    self.status('Extracting Jar',maximum=total)
                    track=0
                    for member in zf.infolist():
                        self.PROGRESS.set(track)
                        try:
                            self.status(filename=member.filename)
                            zf.extract(member, LOCAL+'/_temp/output')
                        except zipfile.error as e:
                            pass
                        track+=1

                # Copying assets
                if self.ASSETS.get()==True:
                    self.logger.info('Copying assets')
                    self.status('Copying assets')
                    self.copydir(LOCAL+'/_temp/output/assets',self.DST.get()+'/assets','filename')
                # Copying data
                if self.DATA.get()==True:
                    self.logger.info('Copying data')
                    self.status('Copying data')
                    self.copydir(LOCAL+'/_temp/output/data',self.DST.get()+'/data','filename')
            else:
                err='The source file is missing or isn\'t a valid file'
        
        if self.ENABLEOE.get()==True:
            indexdir = self._config['ObjectExtractor']['indexes']
            index = os.path.join(indexdir,self.INDEX.get()+'.json')
            if os.path.exists(index) and os.path.isfile(index) and self.INDEX.get()!='unset':
                DST = self.DST.get()
                opn = open(index,'r')
                indx = json.load(opn)
                opn.close()
                # Copy objects
                self.logger.info('Copying objects...')
                self.status('Copying objects')
                src = self.OBJ.get()
                dst = LOCAL+'\\_temp\\objects'
                
                self.copydir(src,dst,'items')

                TOTAL=len(indx['objects'])
                self.status('Mapping objects',maximum=TOTAL)

                track=0
                for key in indx['objects']:
                    self.status(filename='%s of %s items'%(track,TOTAL))
                    hash = indx['objects'][key]['hash']
                    hashfolder = re.match(r'^.{2}',hash)[0]
                    objects = os.path.join(LOCAL, '_temp','objects',hashfolder)
                    # Create dir
                    dir = os.path.dirname(key)
                    if os.path.exists(DST+'/'+dir)==False:
                        os.makedirs(DST+'/'+dir)
                    source = os.path.join(objects,hash)
                    dest=os.path.join(DST,key)
                    try: os.rename(source,dest)
                    except FileNotFoundError: self.logger.warning('Missing file "%s"',hash)
                    except FileExistsError: self.logger.warning('File already exists "%s"',key)
                    except: self.logger.exception('Failed: %s',key)
                    # Progressbar
                    self.PROGRESS.set(track)
                    track+=1
            else:
                err='The source file is missing or isn\'t a valid file'
        
        self.logger.info('Cleaning up...')
        self.cleanup(LOCAL+'/_temp')
        self.status('Complete!',filename='',maximum=100)
        self.PROGRESS.set(100)
        self.logger.info('Complete!')
        if err==False:
            self.EXTRACTBTN['state'] = NORMAL
            if self.SHOW.get()==True:
                os.startfile(self.DST.get())
        else:
            self.logger.error(err)
            messagebox.showerror('Error', err)
        winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

if __name__=='__main__':
    app=App()
    app.mainloop()