from tkinter import DISABLED,NORMAL, W, BooleanVar, Button, Checkbutton, Entry, Frame, Label, OptionMenu, StringVar, Tk,LabelFrame, filedialog,messagebox,IntVar
from tkinter.ttk import Progressbar
from tkstylesheet import TkThemeLoader
from UserFolder import User
import os,zipfile,threading,shutil,json,re,winsound

LOCAL = os.path.dirname(os.path.realpath(__file__))

class App():
    def __init__(self):
        self.USER = User('com.legopitstop.minecraft_extracter')
        if self.USER.exists('config.json'):
            print('Loading config')
            opn = self.USER.open('config.json','r')
            self.config = json.loads(opn.read())
            opn.close()
        else:
            print('Create config')
            versions = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','versions')
            objects = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','objects')
            indexes = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','indexes')
            output = os.path.join(os.path.expanduser('~'),'Downloads')

            self.config={"JarExtractor": {"enabled": True,"assets": True,"data": True,"versions": versions,"version": "unset" },"ObjectExtractor": {"enabled": False,"objects": objects,"indexes":indexes,"index":"unset"},"output": output,"show": True}
            self.save_config(self.USER,self.config)

        
        root=Tk()
        root.title('Minecraft Extractor')
        root.iconbitmap(LOCAL+'/icon.ico')
        root.resizable(False,False)

        # Varables
        self.ENABLEJE=BooleanVar()
        self.ENABLEJE.set(self.config['JarExtractor']['enabled'])
        self.ASSETS=BooleanVar()
        self.ASSETS.set(self.config['JarExtractor']['assets'])
        self.DATA=BooleanVar()
        self.DATA.set(self.config['JarExtractor']['data'])
        self.SRC=StringVar()
        self.SRC.set(self.config['JarExtractor']['version'])
        self.INDEX=StringVar()
        self.INDEX.set(self.config['ObjectExtractor']['index'])
        self.ENABLEOE=BooleanVar()
        self.ENABLEOE.set(self.config['ObjectExtractor']['enabled'])
        self.OBJ=StringVar()
        self.OBJ.set(self.config['ObjectExtractor']['objects'])
        self.DST=StringVar()
        self.DST.set(self.config['output'])
        self.SHOW=BooleanVar()
        self.SHOW.set(self.config['show'])
        self.PROGRESS=IntVar()
        self.PROGRESS.set(0)

        # Functions
        def get_versions():
            ver = self.config['JarExtractor']['versions']
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
                    self.USER.show('config.json')
                return ["unset"]

        def get_indexes():
            ver = self.config['ObjectExtractor']['indexes']
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
                    self.USER.show('config.json')
                return ["unset"]

        def update():
            if self.ENABLEJE.get():
                JE['fg'] = 'green'
                src['state'] = NORMAL
                assets['state'] = NORMAL
                data['state'] = NORMAL
            else:
                JE['fg'] = 'black'
                src['state'] = DISABLED
                assets['state'] = DISABLED
                data['state'] = DISABLED
            if self.ENABLEOE.get():
                OE['fg'] = 'green'
                objEntry['state'] = NORMAL
                objBtn['state'] = NORMAL
                index['state'] = NORMAL
            else:
                OE['fg'] = 'black'
                objEntry['state'] = DISABLED
                objBtn['state'] = DISABLED
                index['state'] = DISABLED

        def choose(varable,type):
            if type=='dir':
                print('DIR')
                path = filedialog.askdirectory(initialdir=varable.get(),mustexist=True)
                if path!='':
                    varable.set(path)

            elif type=='jar':
                print('JAR')
                types=[
                    ('Jar','.jar')
                ]
                path = filedialog.askopenfilename(defaultextension='.jar',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            elif type=='json':
                print('JSON')
                types=[
                    ('JSON','.json')
                ]
                path = filedialog.askopenfilename(defaultextension='.json',filetypes=types,initialdir=varable.get())
                if path!='':
                    varable.set(path)
            else:
                print('ERROR')

        def start():  
            threading.Thread(target=self.extract).start()

        WRAPPER = Frame(root)
        Label(WRAPPER,text='This tool will extract the Minecraft Jar or Unobficate Minecraft\'s objects using the index').grid(row=0,column=0,columnspan=2,sticky=W)

        JE = LabelFrame(WRAPPER,text='Jar Extractor',pady=5,padx=5)
        check = Frame(JE)
        Checkbutton(check,text='Enable',variable=self.ENABLEJE,command=update).grid(row=0,column=0)
        assets = Checkbutton(check,text='Assets',variable=self.ASSETS,command=update)
        assets.grid(row=0,column=1)
        data = Checkbutton(check,text='Data',variable=self.DATA,command=update)
        data.grid(row=0,column=2)
        check.grid(row=0,column=0,sticky=W)
        Label(JE,text='The version to extract:').grid(row=1,column=0,sticky=W)
        src = OptionMenu(JE,self.SRC,*get_versions())
        src.grid(row=2,column=0,sticky=W)
        JE.grid(row=1,column=0,pady=5,padx=5,sticky='nesw')

        OE = LabelFrame(WRAPPER,text='Object Extractor',pady=5,padx=5)
        Checkbutton(OE,text='Enable',variable=self.ENABLEOE,command=update).grid(row=0,column=0,sticky=W)
        Label(OE,text='The folder that contains all the objects:').grid(row=1,column=0,sticky=W)
        objEntry = Entry(OE,textvariable=self.OBJ,width=65)
        objEntry.grid(row=2,column=0,sticky=W)
        objBtn = Button(OE,text='Browse...',command=lambda: choose(self.OBJ,'dir'))
        objBtn.grid(row=2,column=1,padx=5,sticky=W)
        Label(OE,text='The index version:').grid(row=3,column=0,sticky=W)
        index = OptionMenu(OE,self.INDEX,*get_indexes())
        index.grid(row=4,column=0,sticky=W)
        OE.grid(row=1,column=1,pady=5,padx=5,sticky='nesw')
        WRAPPER.grid(row=0,column=0)


        GLOBE = Frame(root,pady=5,padx=5)
        Label(GLOBE,text='Files will be extracted to this folder:').grid(row=0,column=0,sticky=W)
        Entry(GLOBE,textvariable=self.DST,width=65).grid(row=1,column=0,sticky=W)
        Button(GLOBE,text='Browse...',command=lambda: choose(self.DST,'dir')).grid(row=1,column=1,padx=5,sticky=W)
        Checkbutton(GLOBE,text='Show extracted files when complete',variable=self.SHOW,onvalue=True,offvalue=False).grid(row=2,columnspan=2,column=0,sticky=W)
        GLOBE.grid(row=1,column=0,sticky=W)
        
        # Foot
        foot = Frame(root,pady=5,padx=5)
        self.PROGRESS_LABEL = Label(foot,text='Waiting')
        self.PROGRESS_LABEL.object_id='foot'
        self.PROGRESS_LABEL.grid(row=0,column=0,sticky=W)
        self.PROGRESSBAR = Progressbar(foot,length=530,mode='determinate',maximum=100,variable=self.PROGRESS)
        self.PROGRESSBAR.grid(row=1,column=0)
        self.EXTRACTBTN = Button(foot,text='Extract',command=start)
        self.EXTRACTBTN.grid(row=0,column=1,rowspan=2,padx=20,pady=10)
        Button(foot,text='Cancel',command=root.destroy).grid(row=0,column=2,rowspan=2,padx=20,pady=10)
        foot.object_id='foot'
        foot.grid(row=2,column=0,sticky=W)
        
        # Update
        update()

        # Load theme
        theme = TkThemeLoader(root)
        theme.loadStyleSheet(LOCAL+'/theme.tkss')
        root.mainloop()

    def status(self,text=None,maximum=None,mode='determinate'):
        if text: self.PROGRESS_LABEL['text']=text
        if maximum: self.PROGRESSBAR['maximum']=maximum
        if mode: self.PROGRESSBAR['mode']=mode

    def save_config(self,user,config):
        # Update values
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

    def copydir(self,src,dst):
        """Copies dir from src to dst."""
        if os.path.exists(dst)==False:
            os.makedirs(dst)
        track=0
        self.status(maximum=len(os.listdir(src)),mode='indeterminate')
        for filename in os.listdir(src):
            source = src+'\\' + filename
            destination = dst+'\\' + filename
            if os.path.exists(source) and os.path.isfile(source):
                shutil.copy(source, destination)
            else:
                print('Copying folder: ',destination)
                self.copydir(source+'\\',destination+'\\')
            self.PROGRESS.set(track)
            track+=1

    def cleanup(self,src):
        list = os.listdir(src)
        self.status('Cleaning Up',len(list),'indeterminate')
        track=0
        for i in list:
            if os.path.isfile(src+'/'+i):
                os.remove(src+'/'+i)
                self.PROGRESS.set(track)
                track+=1
            else:
                self.cleanup(src+'/'+i)
                # os.rmdir(src+'/'+i)
        
        try: os.rmdir(src)
        except: pass

    # Make seperate lib
    def extract(self):
        self.save_config(self.USER,self.config)
        err=False
        # Create TEMP
        self.EXTRACTBTN['state'] = DISABLED
        if os.path.exists(LOCAL+'/_temp/')==False:
            os.makedirs(LOCAL+'/_temp/')
        if self.ENABLEJE.get()==True:
            src =  os.path.join(self.config['JarExtractor']['versions'],self.SRC.get(),self.SRC.get()+'.jar')
            if os.path.exists(src) and os.path.isfile(src) and self.SRC.get()!='unset':
                # Extract
                with zipfile.ZipFile(src) as zf:
                    total = len(zf.infolist())
                    self.status('Extracting Jar',total)
                    track=0
                    for member in zf.infolist():
                        self.PROGRESS.set(track)
                        try:
                            zf.extract(member, LOCAL+'/_temp/output')
                        except zipfile.error as e:
                            pass
                        track+=1

                # Copying assets
                if self.ASSETS.get()==True:
                    self.status('Copying Assets')
                    self.copydir(LOCAL+'/_temp/output/assets',self.DST.get()+'/assets')
                # Copying data
                if self.DATA.get()==True:
                    self.status('Copying Data')
                    self.copydir(LOCAL+'/_temp/output/data',self.DST.get()+'/data')
            else:
                err='The source file is missing or isn\'t a valid file'
        
        if self.ENABLEOE.get()==True:
            indexdir = self.config['ObjectExtractor']['indexes']
            index = os.path.join(indexdir,self.INDEX.get()+'.json')
            if os.path.exists(index) and os.path.isfile(index) and self.INDEX.get()!='unset':
                DST = self.DST.get()
                opn = open(index,'r')
                indx = json.load(opn)
                opn.close()
                # Copy objects
                self.status('Backing up objects')
                src = self.OBJ.get()
                dst = LOCAL+'\\_temp\\objects'
                self.copydir(src,dst)
                track=0
                self.status('Mapping objects',len(indx['objects']))
                for key in indx['objects']:
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
                    except: print('FAILED: ',key)
                    # Progressbar
                    self.PROGRESS.set(track)
                    track+=1
            else:
                err='The source file is missing or isn\'t a valid file'
        
        self.cleanup(LOCAL+'/_temp')
        self.status('Complete!',100)
        self.PROGRESS.set(100)
        if err==False:
            self.EXTRACTBTN['state'] = NORMAL
            if self.SHOW.get()==True:
                os.startfile(self.DST.get())
        else:
            messagebox.showerror('Error', err)
        winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

app=App()