import subprocess
from time import sleep
import time
from tkinter import DISABLED, E, EW, LEFT,NORMAL, W, BooleanVar, StringVar, filedialog,messagebox,IntVar,Checkbutton
from tkinter.ttk import Progressbar
import uuid
from UserFolder import User
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkCheckBox,CTkProgressBar,CTkOptionMenu,CTkEntry
import os,zipfile,threading,shutil,json,re,winsound,logging,customtkinter,sys

import requests

__version__ = '1.1.0'

customtkinter.set_appearance_mode('System')
LOCAL = os.path.dirname(os.path.realpath(__file__))

user = User('com.legopitstop.minecraft_extracter')

# Theme
if user.exists('theme.json')==False:
    default = {
            "color": {
            "window_bg_color": ["#EBEBEC", "#212325"],
            "button": ["#3B8ED0", "#1F6AA5"],
            "button_hover": ["#36719F", "#144870"],
            "button_border": ["#3E454A", "#949A9F"],
            "checkbox_border": ["#3E454A", "#949A9F"],
            "checkmark": ["white", "gray90"],
            "entry": ["#F9F9FA", "#343638"],
            "entry_border": ["#979DA2", "#565B5E"],
            "entry_placeholder_text": ["gray52", "gray62"],
            "frame_border": ["#979DA2", "#1F2122"],
            "frame_low": ["#D1D5D8", "#2A2D2E"],
            "frame_high": ["#D7D8D9", "#343638"],
            "label": [None, None],
            "text": ["gray10", "#DCE4EE"],
            "text_disabled": ["gray60", "#777B80"],
            "text_button_disabled": ["gray40", "gray74"],
            "progressbar": ["#939BA2", "#4A4D50"],
            "progressbar_progress": ["#3B8ED0", "#1F6AA5"],
            "progressbar_border": ["gray", "gray"],
            "slider": ["#939BA2", "#4A4D50"],
            "slider_progress": ["white", "#AAB0B5"],
            "slider_button": ["#3B8ED0", "#1F6AA5"],
            "slider_button_hover": ["#36719F", "#144870"],
            "switch": ["#939BA2", "#4A4D50"],
            "switch_progress": ["#3B8ED0", "#1F6AA5"],
            "switch_button": ["gray36", "#D5D9DE"],
            "switch_button_hover": ["gray20", "gray100"],
            "optionmenu_button": ["#36719F", "#144870"],
            "optionmenu_button_hover": ["#27577D", "#203A4F"],
            "combobox_border": ["#979DA2", "#565B5E"],
            "combobox_button_hover": ["#6E7174", "#7A848D"],
            "dropdown_color": ["gray90", "gray20"],
            "dropdown_hover": ["gray75", "gray28"],
            "dropdown_text": ["gray10", "#DCE4EE"]
            },
            "text": {
            "macOS": {
                "font": "SF Display",
                "size": -13
            },
            "Windows": {
                "font": "Roboto",
                "size": -13
            },
            "Linux": {
                "font": "Roboto",
                "size": -13
            }
            },
            "shape": {
            "button_corner_radius": 6,
            "button_border_width": 0,
            "checkbox_corner_radius": 6,
            "checkbox_border_width": 3,
            "radiobutton_corner_radius": 1000,
            "radiobutton_border_width_unchecked": 3,
            "radiobutton_border_width_checked": 6,
            "entry_border_width": 2,
            "frame_corner_radius": 6,
            "frame_border_width": 0,
            "label_corner_radius": 8,
            "progressbar_border_width": 0,
            "progressbar_corner_radius": 1000,
            "slider_border_width": 6,
            "slider_corner_radius": 1000,
            "slider_button_length": 0,
            "slider_button_corner_radius": 1000,
            "switch_border_width": 3,
            "switch_corner_radius": 1000,
            "switch_button_corner_radius": 1000,
            "switch_button_length": 0
            }
        }
  
    wrt = user.open('theme.json','w')
    wrt.write(json.dumps(default))
    wrt.close()
customtkinter.ThemeManager.load_theme(os.path.join(user.get(), 'theme.json'))
logging.basicConfig(format='[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%I:%M:%S',handlers=[logging.FileHandler(user.get()+'latest.log',mode='w'),logging.StreamHandler(sys.stdout)], level=logging.INFO)

class App(CTk):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('App')

        # Create default / fallback options
        JarVersionFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','versions')
        ObjectFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','objects')
        ObjectIndexFolder = os.path.join(os.path.expanduser('~'),'AppData','Roaming','.minecraft','assets','indexes')
        OutputFolder = os.path.join(os.path.expanduser('~'),'Downloads', 'output')

        self.default_options = {
            "Version": __version__,
            "ShowOutput": True,
            "OutputFolder": OutputFolder,
            "JarModule": True,
            "JarAssets": True,
            "JarData": True,
            "JarVersion": "1.19",
            "JarVersionFolder": JarVersionFolder,
            "ObjectModule": False,
            "ObjectFolder": ObjectFolder,
            "ObjectIndexFolder": ObjectIndexFolder,
            "ObjectIndex": "1.19",
            "DataModule": False,
            "DataClient": True,
            "DataServer": True,
            "DataReports": True,
            "DataVersion": "unset"
        }
        self.is_running=False

        self.title('Minecraft Extractor %s'%(__version__))
        self.iconbitmap(LOCAL+'/icon.ico')
        self.minsize(600,400)
        self.geometry('600x400')
        self.protocol('WM_DELETE_WINDOW', self.exit)

        # Varables
        self.JAR_MODULE = BooleanVar()
        self.JAR_ASSETS = BooleanVar()
        self.JAR_DATA = BooleanVar()
        self.JAR_VERSION = StringVar()
        self.JAR_VERSION_FOLDER = StringVar()

        self.OBJECT_MODULE = BooleanVar()
        self.OBJECT_INDEX = StringVar()
        self.OBJECT_INDEX_FOLDER = StringVar()
        self.OBJECT_FOLDER = StringVar()

        self.DATA_MODULE = BooleanVar()
        self.DATA_CLIENT = BooleanVar()
        self.DATA_SERVER = BooleanVar()
        self.DATA_REPORTS = BooleanVar()
        self.DATA_VERSION = StringVar()

        self.OUTPUT_FOLDER = StringVar()
        self.SHOW_OUTPUT = BooleanVar()

        # Progressbar
        self.PROGRESS_LBL = StringVar()
        self.PROGRESS_LBL.set('Waiting...')
        self.PROGRESS_MAX = IntVar()
        self.PROGRESS_MAX.set(100)
        self.PROGRESS_PER = StringVar()
        self.PROGRESS_PER.set('0%')

        # Functions
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

        def import_config():
            fp = filedialog.askopenfilename(defaultextension='json', filetypes=[('JSON', '.json')], title='Import Config')
            if fp!='': self.import_file(fp)

        def export_config():
            fp = filedialog.asksaveasfilename(defaultextension='json', filetypes=[('JSON', '.json')],initialfile='config.json',title='Export Config')
            if fp!='': self.export_file(fp)

        def start():
            # Disable module if all options are false
            if self.JAR_MODULE.get() and self.JAR_ASSETS.get() == False and self.JAR_DATA.get()==False:
                self.JAR_MODULE.set(False)

            if self.DATA_MODULE.get() and self.DATA_CLIENT.get()==False and self.DATA_SERVER.get()==False and self.DATA_REPORTS.get()==False:
                self.DATA_MODULE.set(False)

            self._update()

            if self.JAR_MODULE.get()==False and self.OBJECT_MODULE.get()==False and self.DATA_MODULE.get()==False:
                messagebox.showwarning('Minecraft Extractor', 'You must have at least one module activated!')
            else:
                self.is_running=True
                self.export_file(os.path.join(user.get(), 'config2.json'))
                self.close_btn.configure(text='Cancel')
                self.disable_all()
                threading.Thread(target=self.run).start()

        # Widgets
        self.jar_btn = CTkButton(self,text='Jar Extractor', command=lambda: self.toggle_module(self.JAR_MODULE))
        self.jar_btn.grid(row=0,column=0,sticky=EW,padx=3,pady=(10,0))

        self.object_btn = CTkButton(self,text='Object Mapper',command=lambda: self.toggle_module(self.OBJECT_MODULE))
        self.object_btn.grid(row=0,column=1,sticky=EW,padx=3,pady=(10,0))

        self.data_btn = CTkButton(self,text='Data Generator', command=lambda: self.toggle_module(self.DATA_MODULE))
        self.data_btn.grid(row=0,column=2,sticky=EW,padx=3,pady=(10,0))

        # Jar Extractor
        self.jar_wrapper = CTkFrame(self)
        self.jar_assets = CTkCheckBox(self.jar_wrapper, text='Assets', variable=self.JAR_ASSETS, onvalue=True, offvalue=False)
        self.jar_assets.grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.jar_data = CTkCheckBox(self.jar_wrapper, text='Data',variable=self.JAR_DATA, onvalue=True, offvalue=False)
        self.jar_data.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.jar_version = CTkOptionMenu(self.jar_wrapper,variable=self.JAR_VERSION)
        self.jar_version.grid(row=2,column=0, sticky=EW,padx=5,pady=5)
        self.jar_wrapper.grid(row=1,column=0,sticky='nesw',padx=10,pady=(0,10))

        # Object Mapper
        self.object_wrapper = CTkFrame(self)
        self.object_index = CTkOptionMenu(self.object_wrapper,variable=self.OBJECT_INDEX)
        self.object_index.grid(row=0,column=0, sticky=EW,padx=5,pady=5)
        self.object_wrapper.grid(row=1,column=1,sticky='nesw',padx=10,pady=(0,10))

        # Data Generator
        self.data_wrapper = CTkFrame(self)
        self.data_client = CTkCheckBox(self.data_wrapper, text='Assets', variable=self.DATA_CLIENT, onvalue=True, offvalue=False)
        self.data_client.grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.data_server = CTkCheckBox(self.data_wrapper, text='Data',variable=self.DATA_SERVER, onvalue=True, offvalue=False)
        self.data_server.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.data_reports = CTkCheckBox(self.data_wrapper, text='Reports',variable=self.DATA_REPORTS, onvalue=True, offvalue=False)
        self.data_reports.grid(row=2,column=0,sticky=W,padx=5,pady=5)
        self.data_version = CTkOptionMenu(self.data_wrapper, variable=self.DATA_VERSION)
        self.data_version.grid(row=3,column=0, sticky=EW,padx=5,pady=5)
        self.data_wrapper.grid(row=1,column=2,sticky='nesw',padx=10,pady=(0,10))

        # Settings
        self.setting_lbl = CTkLabel(self,text='Settings', fg_color='black')
        self.setting_lbl.grid(row=2,column=0,columnspan=3,sticky=EW,padx=3,pady=(10,0))

        self.setting_wrapper = CTkFrame(self)
        
        self.show_output = CTkCheckBox(self.setting_wrapper, text='Show', variable=self.SHOW_OUTPUT)
        self.show_output.grid(row=0,column=0,columnspan=2,sticky=W,padx=5,pady=5)

        CTkButton(self.setting_wrapper, text='Import Config From JSON File',command=import_config).grid(row=1,column=1,sticky=EW)
        CTkButton(self.setting_wrapper, text='Export Config To JSON File',command=export_config).grid(row=1,column=2,sticky=EW)

        CTkLabel(self.setting_wrapper, text='Output Folder').grid(row=2,column=0,padx=5,pady=5,sticky=W)
        self.output_folder = CTkEntry(self.setting_wrapper, textvariable=self.OUTPUT_FOLDER)
        self.output_folder.grid(row=2,column=1,padx=5,pady=5,sticky=EW)

        self.output_btn = CTkButton(self.setting_wrapper, text='Choose', command=lambda: choose(self.OUTPUT_FOLDER, 'dir'))
        self.output_btn.grid(row=2,column=2,padx=5,pady=5,sticky=E)

        self.setting_wrapper.grid(row=3,column=0,columnspan=3,sticky=EW,padx=10,pady=(0,10))

        # Footer
        footer = CTkFrame(self)
        self.progress_lbl = CTkLabel(footer, textvariable=self.PROGRESS_LBL,wraplength=185, justify=LEFT,width=1)
        self.progress_lbl.grid(row=0,column=0,sticky=W,padx=0,pady=(5, 0))
        
        self.progress_per = CTkLabel(footer, textvariable=self.PROGRESS_PER,width=1)
        self.progress_per.grid(row=0,column=1,sticky=E,padx=0,pady=(5, 0))
    
        self.PROGRESS_BAR = CTkProgressBar(footer,height=10)
        self.PROGRESS_BAR.grid(row=1,column=0,columnspan=2,sticky=EW,padx=5,pady=(0,5))

        self.run_btn = CTkButton(footer, text='Run', command=start)
        self.run_btn.grid(row=0,column=2,rowspan=2,sticky=E,padx=5,pady=5)
        
        self.close_btn = CTkButton(footer, text='Close', command=self.exit)
        self.close_btn.grid(row=0,column=3,rowspan=2)
        
        footer.grid(row=4,column=0,sticky=EW,columnspan=3,padx=10,pady=10)

        # Responsive
        footer.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure([0,1,2], weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.jar_wrapper.grid_columnconfigure(0, weight=1)
        self.object_wrapper.grid_columnconfigure(0, weight=1)
        self.data_wrapper.grid_columnconfigure(0, weight=1)

        self.setting_wrapper.grid_columnconfigure(1, weight=1)

        # Apply defaults
        self.logger.info('Loading default options from user config.')
        self.import_file(os.path.join(user.get(), 'config2.json'))
        self.status(value=100, maximum=100)

    def import_file(self, fp:str):
        """import options from a JSON file"""
        if os.path.exists(fp) and os.path.isfile(fp):
            try:
                opn = open(fp,'r')
                options = json.load(opn)
                opn.close()

                if 'Version' in options:
                    self.import_options(options)
                else:
                    new_options = {}
                    new_options['JarModule'] = options['JarExtractor']['enabled']
                    new_options['JarAssets'] = options['JarExtractor']['assets']
                    new_options['JarData'] = options['JarExtractor']['data']
                    new_options['JarVersionFolder'] = options['JarExtractor']['versions']
                    new_options['JarVersion'] = options['JarExtractor']['version']

                    new_options['ObjectModule'] = options['ObjectExtractor']['enabled']
                    new_options['ObjectFolder'] = options['ObjectExtractor']['objects']
                    new_options['ObjectIndexFolder'] = options['ObjectExtractor']['indexes']
                    new_options['ObjectIndex'] = options['ObjectExtractor']['index']

                    new_options['OutputFolder'] = options['output']
                    new_options['ShowOutput'] = options['show']

                    self.import_options(new_options)
                    print('Update file')

                return True
            except json.decoder.JSONDecodeError:
                return False
        else:
            self.logger.warning('Unknown file "%s". Using default options', fp)
            self.import_options(self.default_options)
            # self.export_file(fp)
            return None

    def import_options(self, obj:dict={}):
        """import options from a dict"""
        if 'JarModule' in obj: self.JAR_MODULE.set(obj['JarModule'])
        else: self.JAR_MODULE.set(self.default_options['JarModule'])
        if 'JarAssets' in obj: self.JAR_ASSETS.set(obj['JarAssets'])
        else: self.JAR_ASSETS.set(self.default_options['JarAssets'])
        if 'JarData' in obj: self.JAR_DATA.set(obj['JarData'])
        else: self.JAR_DATA.set(self.default_options['JarData'])
        if 'JarVersion' in obj: self.JAR_VERSION.set(obj['JarVersion'])
        else: self.JAR_VERSION.set(self.default_options['JarVersion'])
        if 'JarVersionFolder' in obj: self.JAR_VERSION_FOLDER.set(obj['JarVersionFolder'])
        else: self.JAR_VERSION_FOLDER.set(self.default_options['JarVersionFolder'])
        
        if 'ObjectModule' in obj: self.OBJECT_MODULE.set(obj['ObjectModule'])
        else: self.OBJECT_MODULE.set(self.default_options['ObjectModule'])
        if 'ObjectIndex' in obj: self.OBJECT_INDEX.set(obj['ObjectIndex'])
        else: self.OBJECT_INDEX.set(self.default_options['ObjectIndex'])
        if 'ObjectIndexFolder' in obj: self.OBJECT_INDEX_FOLDER.set(obj['ObjectIndexFolder'])
        else: self.OBJECT_INDEX_FOLDER.set(self.default_options['ObjectIndexFolder'])
        if 'ObjectFolder' in obj: self.OBJECT_FOLDER.set(obj['ObjectFolder'])
        else: self.OBJECT_FOLDER.set(self.default_options['ObjectFolder'])

        if 'DataModule' in obj: self.DATA_MODULE.set(obj['DataModule'])
        else: self.DATA_MODULE.set(self.default_options['DataModule'])
        if 'DataClient' in obj: self.DATA_CLIENT.set(obj['DataClient'])
        else: self.DATA_CLIENT.set(self.default_options['DataClient'])
        if 'DataServer' in obj: self.DATA_SERVER.set(obj['DataServer'])
        else: self.DATA_SERVER.set(self.default_options['DataServer'])
        if 'DataReports' in obj: self.DATA_REPORTS.set(obj['DataReports'])
        else: self.DATA_REPORTS.set(self.default_options['DataReports'])
        if 'DataVersion' in obj: self.DATA_VERSION.set(obj['DataVersion'])
        else: self.DATA_VERSION.set(self.default_options['DataVersion'])
        
        if 'OutputFolder' in obj: self.OUTPUT_FOLDER.set(obj['OutputFolder'])
        else: self.OUTPUT_FOLDER.set(self.default_options['OutputFolder'])
        if 'ShowOutput' in obj: self.SHOW_OUTPUT.set(obj['ShowOutput'])
        else: self.SHOW_OUTPUT.set(self.default_options['ShowOutput'])
        self._update()

    def export_file(self, fp:str):
        """Save the current options as a JSON file"""
        try:
            options = self.export_options()
            wrt = open(fp,'w')
            wrt.write(json.dumps(options, indent=4))
            wrt.close()
            return True
        except json.decoder.JSONDecodeError:
            return False

    def export_options(self):
        """Returns all current options as a dict"""
        return {
            'Version': __version__,
            'JarModule': self.JAR_MODULE.get(),
            'JarAssets': self.JAR_ASSETS.get(),
            'JarData': self.JAR_DATA.get(),
            'JarVersion': self.JAR_VERSION.get(),
            'JarVersionFolder': self.JAR_VERSION_FOLDER.get(),
            
            'ObjectModule': self.OBJECT_MODULE.get(),
            'ObjectIndex': self.OBJECT_INDEX.get(),
            'ObjectIndexFolder': self.OBJECT_INDEX_FOLDER.get(),
            'ObjectFolder': self.OBJECT_FOLDER.get(),

            'DataModule': self.DATA_MODULE.get(),
            'DataClient': self.DATA_CLIENT.get(),
            'DataServer': self.DATA_SERVER.get(),
            'DataReports': self.DATA_REPORTS.get(),
            'DataVersion': self.DATA_VERSION.get(),
            
            'OutputFolder': self.OUTPUT_FOLDER.get(),
            'ShowOutput': self.SHOW_OUTPUT.get()
        }

    def disable_all(self):
        """Disables all options"""
        self.jar_btn.configure(state=DISABLED)
        self.jar_assets.configure(state=DISABLED)
        self.jar_data.configure(state=DISABLED)
        self.jar_version.configure(state=DISABLED)
        self.object_btn.configure(state=DISABLED)
        self.object_index.configure(state=DISABLED)
        self.data_btn.configure(state=DISABLED)
        self.data_client.configure(state=DISABLED)
        self.data_server.configure(state=DISABLED)
        self.data_reports.configure(state=DISABLED)
        self.data_version.configure(state=DISABLED)
        self.show_output.configure(state=DISABLED)
        self.output_folder.configure(state=DISABLED)
        self.output_btn.configure(state=DISABLED)
        self.run_btn.configure(state=DISABLED)
    
    def enable_all(self):
        """Enables all options"""
        self.jar_btn.configure(state=NORMAL)
        self.jar_assets.configure(state=NORMAL)
        self.jar_data.configure(state=NORMAL)
        self.jar_version.configure(state=NORMAL)
        self.object_btn.configure(state=NORMAL)
        self.object_index.configure(state=NORMAL)
        self.data_btn.configure(state=NORMAL)
        self.data_client.configure(state=NORMAL)
        self.data_server.configure(state=NORMAL)
        self.data_reports.configure(state=NORMAL)
        self.data_version.configure(state=NORMAL)
        self.show_output.configure(state=NORMAL)
        self.output_folder.configure(state=NORMAL)
        self.output_btn.configure(state=NORMAL)
        self.run_btn.configure(state=NORMAL)
        self._update()

    def toggle_module(self, variable:BooleanVar):
        if variable.get()==False:
            variable.set(True)
            self._update()

        elif variable.get()==True:
            variable.set(False)
            self._update()

    def _update(self):
        # Update Version lists
        def getClientVersions(parent=True):
            """Returns a list of all client versions that are installed on this user"""
            ver = self.JAR_VERSION_FOLDER.get()
            if os.path.exists(ver):
                vers=['unset']
                for v in os.listdir(ver):
                    if os.path.isfile(ver+'/'+v)==False:
                        for i in os.listdir(ver+'/'+v):
                            if i.endswith('.jar'):
                                vers.append(re.sub(r'\.jar$','',i))

                return vers
            else:
                if parent:
                    default = self.default_options['JarVersionFolder']
                    self.logger.warning("Invalid version folder! Using default location '%s'", default)
                    self.JAR_VERSION_FOLDER.set(default)
                    return getClientVersions(False)
                else:
                    self.logger.warning('Invalid version folder!')
                    messagebox.showerror('Missing Folder!','The following version folder is missing! %s'%self.JAR_VERSION_FOLDER.get())
                    return ['unset']

        def getServerVersions():
            """Returns a list of all the server versions that support data gen"""
            return [
                'unset',
                '1.19',
                '1.18.2',
                '1.18.1',
                '1.18',
                '1.17.1',
                '1.17'
            ]

        def getIndexes(parent=True):
            """Returns a list of all index versions that are installed on this user"""
            ver = self.OBJECT_INDEX_FOLDER.get()
            if os.path.exists(ver):
                ind=['unset']
                for i in os.listdir(ver):
                    if os.path.isfile(ver)==False:
                        if i.endswith('.json'):
                            ind.append(re.sub(r'\.json$','',i))
                return ind
            else:
                if parent:
                    default = self.default_options['ObjectIndexFolder']
                    self.logger.warning("Invalid index folder! Using default location '%s'", default)
                    self.OBJECT_INDEX_FOLDER.set(default)
                    return getIndexes(False)
                else:
                    self.logger.warning('Invalid index folder!')
                    messagebox.showerror('Missing Folder!','The following index folder is missing! %s'% self.OBJECT_INDEX_FOLDER.get())
                    return ['unset']

        self.jar_version.configure(values=getClientVersions())
        self.data_version.configure(values=getServerVersions())
        self.object_index.configure(values=getIndexes())

        # Disable run if all modules are off
        if self.JAR_MODULE.get()==False and self.OBJECT_MODULE.get()==False and self.DATA_MODULE.get()==False: self.run_btn.configure(state=DISABLED)
        else: self.run_btn.configure(state=NORMAL)

        if self.JAR_MODULE.get():
            self.jar_wrapper.configure(fg_color='darkgreen')
            self.jar_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.jar_assets.configure(state=NORMAL)
            self.jar_data.configure(state=NORMAL)
            self.jar_version.configure(state=NORMAL)

        else:
            self.jar_wrapper.configure(fg_color='#2A2D2E')
            self.jar_btn.configure(fg_color='black', hover_color='black')
            self.jar_assets.configure(state=DISABLED)
            self.jar_data.configure(state=DISABLED)
            self.jar_version.configure(state=DISABLED)
        
        if self.OBJECT_MODULE.get():
            self.object_wrapper.configure(fg_color='darkgreen')
            self.object_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.object_index.configure(state=NORMAL)

        else:
            self.object_wrapper.configure(fg_color='#2A2D2E')
            self.object_btn.configure(fg_color='black', hover_color='black')
            self.object_index.configure(state=DISABLED)
        
        if self.DATA_MODULE.get():
            self.data_wrapper.configure(fg_color='darkgreen')
            self.data_btn.configure(fg_color='#001b00', hover_color='#001b00')
            self.data_client.configure(state=NORMAL)
            self.data_server.configure(state=NORMAL)
            self.data_reports.configure(state=NORMAL)
            self.data_version.configure(state=NORMAL)
        else:
            self.data_wrapper.configure(fg_color='#2A2D2E')
            self.data_btn.configure(fg_color='black', hover_color='black')
            self.data_client.configure(state=DISABLED)
            self.data_server.configure(state=DISABLED)
            self.data_reports.configure(state=DISABLED)
            self.data_version.configure(state=DISABLED)

    def force_exit(self):
        """Forces the app to close"""
        self.destroy()
        self.logger.warning('Force shutting down!')
        sys.exit()

    def exit(self):
        """Properly close the program"""
        if self.is_running:
            confirm = messagebox.askyesno('Force Shutdown', 'Are you sure you want to quit? Quitting now may result in errors or corruption.', icon='warning',default='no')
            if confirm==True:
                self.force_exit()
            
        else:
            self.logger.info('Stopping!')
            self.destroy()

    def status(self,text:str=None,filename:str=None,value:int=None,maximum:int=None,color:str=None):
        """Update the progress bar and progress label"""
        if text!=None:
            self.PROGRESS_LBL.set(str(text))
            self.logger.info('[Status] %s',str(text))

        if maximum!=None: self.PROGRESS_MAX.set(maximum)

        if value!=None:
            max = self.PROGRESS_MAX.get()
            des = value / max
            per = round(des * 100)
            self.PROGRESS_BAR.set(des)
            self.PROGRESS_PER.set(str(per)+'%')
            self.title('Minecraft Extractor %s - %s'%(__version__,str(per)+'%'))

        if color!=None:
            if color=='complete': self.PROGRESS_BAR.configure(progress_color='green')
            elif color=='reset': self.PROGRESS_BAR.configure(progress_color='#1F6AA5')
            else: self.PROGRESS_BAR.configure(progress_color=color)

    CALCFILES=0
    def calcFiles(self,dir:str,silent:bool=False,reset:bool=True):
        """Calculates the total amount of files, including files inside of folders"""
        if reset==True:
            self.CALCFILES=0
            self.status('Discovering items...', value=0)

        for file in os.listdir(dir):
            filename = os.path.join(dir,file)

            if os.path.isfile(filename):
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
            old = self.PROGRESS_LBL.get()

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
            self.status(value=self.COPYDIR)
            self.COPYDIR+=1

    CLEANUP=0
    def cleanup(self,src,reset:bool=True):
        list = os.listdir(src)
        if reset:
            CLEANUP=0
            self.calcFiles(src)
            self.status('Cleaning Up...',maximum=self.CALCFILES)
        
        for i in list:
            if os.path.isfile(src+'/'+i):
                os.remove(src+'/'+i)
                # self.status(filename='%s of %s items'%(self.CLEANUP, self.CALCFILES),value=self.CLEANUP)
                self.CLEANUP+=1
            else:
                self.cleanup(src+'/'+i,False)
        
        try: os.rmdir(src)
        except: pass

    # Should be moved to main.py
    def run(self):
        err=False
        # Create TEMP
        self.status(color='reset')
        TOTAL_TIME = Stopwatch()

        CACHE = os.path.join(self.OUTPUT_FOLDER.get(), '.cache')
        os.makedirs(CACHE, exist_ok=True)

        if self.JAR_MODULE.get()==True:
            src =  os.path.join(self.JAR_VERSION_FOLDER.get(),self.JAR_VERSION.get(),self.JAR_VERSION.get()+'.jar')
            JAR_CACHE = os.path.join(CACHE, uuid.uuid4().hex)
            if os.path.exists(src) and os.path.isfile(src) and self.JAR_VERSION.get()!='unset':
                # Extract
                TIME = Stopwatch()
                self.status('Extracting Jar...')
                with zipfile.ZipFile(src) as zf:
                    total = len(zf.infolist())
                    self.status(maximum=total)
                    track=0
                    for member in zf.infolist():
                        self.status(value=track)
                        try:
                            # Ignore .class files
                            if member.filename.endswith('.class')==False:
                                zf.extract(member, JAR_CACHE)
                        except zipfile.error as e:
                            pass
                        track+=1
                self.logger.info('[Status] Done! (%s ms)', TIME.end())

                # Copying assets
                if self.JAR_ASSETS.get()==True:
                    self.status('Copying assets...')
                    TIME = Stopwatch()
                    self.copydir(os.path.join(JAR_CACHE, 'assets'),self.OUTPUT_FOLDER.get()+'/assets','filename')
                    self.logger.info('[Status] Done! (%s ms)', TIME.end())

                # Copying data
                if self.JAR_DATA.get()==True:
                    self.status('Copying data...')
                    TIME = Stopwatch()
                    self.copydir(os.path.join(JAR_CACHE, 'data'),self.OUTPUT_FOLDER.get()+'/data','filename')
                    self.logger.info('[Status] Done! (%s ms)', TIME.end())
            else:
                err='The source file is missing or isn\'t a valid file'
        
        if self.OBJECT_MODULE.get()==True:
            indexdir = self.OBJECT_INDEX_FOLDER.get()
            index = os.path.join(indexdir,self.OBJECT_INDEX.get()+'.json')
            if os.path.exists(index) and os.path.isfile(index) and self.OBJECT_INDEX.get()!='unset':
                DST = self.OUTPUT_FOLDER.get()
                opn = open(index,'r')
                indx = json.load(opn)
                opn.close()

                TIME = Stopwatch()
                TOTAL=len(indx['objects'])
                self.status('Mapping objects...',maximum=TOTAL)

                track=0
                for key in indx['objects']:
                    hash = indx['objects'][key]['hash']
                    hashfolder = re.match(r'^.{2}',hash)[0]

                    # Create dir
                    dir = os.path.dirname(key)
                    os.makedirs(DST+'/'+dir, exist_ok=True)
                    source = os.path.join(self.OBJECT_FOLDER.get(),hashfolder,hash)
                    dest=os.path.join(DST,key)
                    try: shutil.copy(source, dest)
                    except FileNotFoundError: self.logger.warning('Missing file "%s"',hash)
                    except: self.logger.exception('Failed: %s',key)
                    # Progressbar
                    self.status(value=track)
                    track+=1
                
                self.logger.info('[Status] Done! (%s ms)', TIME.end())
            else:
                err='The source file is missing or isn\'t a valid file'
        
        if self.DATA_MODULE.get()==True:
            if self.DATA_VERSION.get()!='unset':
                DATA_CACHE = os.path.join(CACHE, uuid.uuid4().hex)
                JAR = os.path.join(DATA_CACHE, 'server.jar')

                # Download server
                self.status('Downloading server JAR...')
                TIME = Stopwatch()
                os.makedirs(DATA_CACHE, exist_ok=True)
                version = self.DATA_VERSION.get()
                file = requests.get(f'https://serverjars.com/api/fetchJar/vanilla/{version}')
                wrt = open(JAR, 'wb')
                wrt.write(file.content)
                wrt.close()
                self.logger.info('[Status] Done! (%s ms)', TIME.end())

                TIME = Stopwatch()
                self.status('Running data generator...')

                generators = ''
                if self.DATA_CLIENT.get()==True: generators+=' --client'
                if self.DATA_SERVER.get()==True: generators+=' --server'
                if self.DATA_REPORTS.get()==True: generators+=' --reports'

                if version=='1.17' or version=='1.17.1':
                    command = "java -cp %s net.minecraft.data.Main --output %s %s"%(JAR,self.OUTPUT_FOLDER.get(),generators)
                    self.logger.info('[Status] Using 1.17 command: %s', command)
                else:
                    command = "java -DbundlerMainClass=net.minecraft.data.Main -jar %s --output %s %s"%(JAR,self.OUTPUT_FOLDER.get(),generators)
                    self.logger.info('[Status] Using 1.18+ command: %s',command)

                cmd = os.system(command)
                if cmd!=0:
                    self.logger.warning('Failed to run data generator! %s', command)
                    messagebox.showwarning('Minecraft Extractor', 'Failed to run data generator!')
                self.logger.info('[Status] Done! (%s ms)', TIME.end())
            else:
                err='The version is missing or isn\'t a valid version'

        TIME = Stopwatch()
        self.cleanup(CACHE)
        self.logger.info('[Status] Done! (%s ms)', TIME.end())
        self.status('Complete! (%s ms)'%(TOTAL_TIME.end()),value=100,maximum=100,color='complete')
        if err==False:
            self.is_running=False
            self.close_btn.configure(text='Close')
            self.enable_all()
            if self.SHOW_OUTPUT.get()==True:
                os.startfile(self.OUTPUT_FOLDER.get())
        else:
            self.is_running=False
            self.close_btn.configure(text='Close')
            self.enable_all()
            self.logger.error(err)
            messagebox.showerror('Error', err)

        self.bell()

class Stopwatch():
    def __init__(self):
        self._start = time.time()

    def end(self):
        self._end = time.time()
        return round(self._end - self._start, 2)

if __name__=='__main__':
    app=App()
    app.mainloop()