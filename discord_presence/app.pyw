from tkinter.font import NORMAL
from customtkinter import CTk, CTkButton, CTkOptionMenu,CTkToplevel,CTkLabel,CTkEntry,CTkFrame
from tkinter import DISABLED, E, EW, StringVar, messagebox,PhotoImage
from UserFolder import User, Config
import pypresence
import os
import customtkinter
import json
import jsonschema
import logging
import sys
import uuid
import requests

def setup(u:User):
    os.makedirs(user.join('profiles'))
    # Save default profile

customtkinter.set_default_color_theme('blue')
LOCAL = os.path.dirname(os.path.realpath(__file__))
user = User('com.legopitstop.discord_presence')
logging.basicConfig(format='[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%I:%M:%S',handlers=[logging.FileHandler(user.join()+'latest.log',mode='w'),logging.StreamHandler(sys.stdout)], level=logging.INFO)

class Button():
    def __init__(self, label:str, url:str):
        self.label = label
        self.url = url

    def json(self):
        return {
            'label': self.label,
            'url': self.url
        }

class Presence():
    def __init__(self, app, state:str, details:str, buttons:list, large_image:str, large_text:str, small_image:str, small_text:str):
        self.app = app
        self.state = state
        self.details = details
        self.large_image = large_image
        self.large_text = large_text
        self.small_image = small_image
        self.small_text = small_text

        if buttons!=None:
            self.buttons = []
            for button in buttons: self.buttons.append(Button(**button))
        else: self.buttons = None

    def json(self):
        data = {
            'state': self.state,
            'details': self.details,
            'buttons': None,
            'large_image': self.large_image,
            'large_text': self.large_text,
            'small_image': self.small_image,
            'small_text': self.small_text
        }
        if self.buttons!=None:
            data['buttons'] = []
            for button in self.buttons: data['buttons'].append(button.json())
        return data

    def update(self, rpc:pypresence.Presence):
        """Update the precense"""
        data = self.json()
        rpc.update(**data)

class Profile():
    def __init__(self, app, filename:str, id:int, name:str, presence:dict):
        self.app = app
        self.filename = filename
        self.id = int(id)
        self.name = name
        self.is_running = False
        if type(presence) == dict: self.presence = Presence(self.app, **presence)
        else: self.presence = presence

        try:
            self.RPC = pypresence.Presence(self.id)
        except pypresence.exceptions.DiscordError as err:
            self.app.logger.warning('Failed to start presence: %s', err.message)
            messagebox.showwarning('Discord Presence', 'Failed to start presence: %s'%(err.message))
            self.RPC = None

    def json(self):
        return {
            'name': self.name,
            'id': int(self.id),
            'presence': self.presence.json()
        }

    def connect(self):
        """Connect to discord"""
        self.RPC.connect()
        self.is_running = True

    def start(self):
        """Start the profile"""
        if type(self.presence) == Presence: # Can also be a list (soon!)
            self.connect()
            self.presence.update(self.RPC)

    def stop(self):
        """Stops the profile"""
        if self.RPC !=None and self.is_running==True:
            self.is_running = False
            self.RPC.close()

    def save(self):
        """Saves the class to the file"""
        with user.open(os.path.join('profiles', str(self.filename)), 'w') as w: w.write(json.dumps(self.json()))
        self.app.profile.configure(values=self.app.list_profiles())

    def remove(self):
        """Delete this profile"""
        os.remove(user.join('profiles', str(self.filename)))
        self.app.reload()

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title('Discord Presence')
        self.iconbitmap(LOCAL+'/icon.ico')
        self.resizable(False, False)
        self.geometry('300x100')
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.logger = logging.getLogger('App')

        # Load icons
        self.PLAY = PhotoImage(file=os.path.join(LOCAL, 'assets', 'play.png'))
        self.STOP = PhotoImage(file=os.path.join(LOCAL, 'assets', 'stop.png'))
        self.EDIT = PhotoImage(file=os.path.join(LOCAL, 'assets', 'edit.png'))
        self.DELETE = PhotoImage(file=os.path.join(LOCAL, 'assets', 'delete.png'))
        self.ADD = PhotoImage(file=os.path.join(LOCAL, 'assets', 'add.png'))
        
        # Load config
        default = Config(user)
        default.setItem('profile', 'unset')
        default.setItem('theme', 'System')
        self.c = default.section('CONFIG')

        # Variable
        self.profiles = self.load()
        self.PROFILE = StringVar()
        self.PROFILE.set(self.c.getItem('profile'))

        # Widgets
        self.start_btn = CTkButton(self, image=self.PLAY, text='', command=self.start, width=50, state=DISABLED)
        self.start_btn.grid(row=0,column=0,padx=10,pady=5)

        self.btn = CTkButton(self, image=self.EDIT, text='', width=50)
        self.btn.grid(row=0,column=1,padx=10,pady=5)

        self.profile = CTkOptionMenu(self, values=self.list_profiles(), variable=self.PROFILE, command=self.update_optionmenu)
        self.profile.grid(row=0,column=2,padx=10,pady=5)

        # Default
        self.after(500, self.start_default)

        # Load config
        customtkinter.set_appearance_mode(self.c.getItem('theme'))
    
    def get_assets(self, appid:str):
        """Get a list of assets"""
        data = requests.get('https://discordapp.com/api/oauth2/applications/%s/assets'%(appid))
        if data.status_code==200: return data.json()
        else: return None

    def _value(self, variable, max:int=None):
        if variable.get()=='' or variable.get().lower()=='none' or variable.get().lower()=='null': return None
        else:
            value = variable.get()
            if max!=None and len(value)>=max: return value[0:max]
            else: return value

    def start_default(self):
        self.update_optionmenu(self.c.getItem('profile'))
        self.start(self.c.getItem('profile'))
        if self.c.getItem('profile')!='unset': self.iconify()

    def load(self):
        """Returns a list of all profiles"""
        profiles = []
        for profile in os.listdir(user.join('profiles')):
            with user.open(os.path.join('profiles', str(profile))) as f:
                try:
                    data = json.load(f)
                    with open(os.path.join(LOCAL, 'assets', 'schema.json'), 'r') as s:
                        schema = json.load(s)
                        jsonschema.validate(data, schema)
                        profiles.append(Profile(app=self, filename=profile, **data))
                except json.decoder.JSONDecodeError as err: self.logger.warning('Failed to load profile "%s": %s', profile, err)
                except jsonschema.ValidationError as err: self.logger.warning('Failed to load profile "%s": %s', profile, err.message)
        return profiles

    def reload(self):
        """Reload all profiles"""
        self.logger.info('Reloading all profiles')
        self.profiles = self.load()
        self.profile.configure(values=self.list_profiles())

    def list_profiles(self):
        """Returns a list of all the profile names"""
        profiles = ['unset']
        for profile in self.profiles: profiles.append(profile.name)
        return profiles

    def get_profile(self, id:str=None, name:str=None):
        """Get the current selected profile"""
        for profile in self.profiles:
            if id!=None and profile.id == id: return profile
            elif name!=None and profile.name == name: return profile
        return None

    def update_optionmenu(self, name:str):
        self.c.setItem('profile', name)
        self.stop()
        if name=='unset':
            self.start_btn.configure(state=DISABLED)
            self.btn.configure(command=self.new)
        else:
            self.start_btn.configure(state=NORMAL)
            self.btn.configure(command=self.edit)

    def start(self, name:str=None):
        """Start the profile"""
        if name!='unset':
            if name==None: profile:Profile = self.get_profile(name=self.PROFILE.get())
            else: profile:Profile = self.get_profile(name=name)
            if profile!=None:
                profile.start()
                self.start_btn.configure(image=self.STOP, command=self.stop)
                self.btn.configure(state=DISABLED)
            else: self.logger.warning('Failed to find profile "%s"', name)

    def stop(self):
        """Stop all or any profile"""
        for profile in self.profiles: profile.stop()
        self.btn.configure(state=NORMAL)
        self.start_btn.configure(image=self.PLAY, command=self.start)

    def close(self):
        """Close the app"""
        self.stop()
        self.destroy()
        exit(0)

    def profile_screen(self, confirmcommand, profile:Profile=None):
        """Opens the profile screen"""
        root = CTkToplevel(self)
        root.attributes('-topmost', True)
        root.title('Profile')
        root.iconbitmap(LOCAL+'/icon.ico')
        root.minsize(300,300)

        # variables
        PROFILE_ID = StringVar()
        NAME = StringVar()
        ID = StringVar()
        STATE = StringVar()
        DETAILS = StringVar()
        LARGE_IMAGE = StringVar()
        LARGE_TEXT = StringVar()
        SMALL_IMAGE = StringVar()
        SMALL_TEXT = StringVar()
        BUTTONS = []

        def confirm():
            if ID.get()!='':
                if NAME.get()!='' and NAME.get()!='unset':
                    if PROFILE_ID.get()=='': filename = uuid.uuid4().hex
                    else: filename = PROFILE_ID.get()
                    
                    if len(BUTTONS) >= 1:
                        buttons = []
                        for button in BUTTONS: buttons.append({'label': self._value(button['label'], 32), 'url': self._value(button['url'])})
                    else: buttons = None

                    presence = Presence(self, state=self._value(STATE, 128), details=self._value(DETAILS, 128), large_image=self._value(LARGE_IMAGE, 256), large_text=self._value(LARGE_TEXT, 128), small_image=self._value(SMALL_IMAGE, 256), small_text=self._value(SMALL_TEXT,128), buttons=buttons)
                    confirmcommand(Profile(self, filename=filename, id=ID.get(), name=NAME.get(), presence=presence))
                    root.destroy()
                else: messagebox.showinfo('Discord Presence', '"Name" is a required property.', parent=root)
            else: messagebox.showinfo('Discord Presence', '"ID" is a required property.', parent=root)
        
        def delete():
            """Remove the profile"""
            self.PROFILE.set('unset')
            self.c.setItem('profile', 'unset')
            profile.remove()
            root.destroy()

        def remove_btn(widget:CTkFrame, index:int):
            """remmove the button"""
            i = 0
            for btn in BUTTONS:
                if btn['index'] == index:
                    del BUTTONS[i]
                i+=1
            widget.destroy()

        def add_btn(label=None, url=None):
            """Add a button"""
            index = len(BUTTONS)
            if index<=1:
                BUTTONS.append({'index': index ,'label': StringVar(), 'url': StringVar()})

                btn = CTkFrame(btns)
                CTkButton(btn, image=self.DELETE, text='', width=20, command=lambda w=btn, i=index: remove_btn(w, i)).grid(row=0,column=2,padx=5,pady=5)
                CTkLabel(btn, text='Label', anchor=E).grid(row=0,column=0,padx=5,pady=5)
                CTkEntry(btn, textvariable=BUTTONS[index]['label'], placeholder_text='MyButton').grid(row=0,column=1,padx=5,pady=5,sticky=EW)

                CTkLabel(btn, text='Url', anchor=E).grid(row=1,column=0,padx=5,pady=5)
                CTkEntry(btn, textvariable=BUTTONS[index]['url'], placeholder_text='https://example.com').grid(row=1,column=1,padx=5,pady=5,sticky=EW)
                btn.grid(row=index, column=0,padx=10,pady=10, sticky='nesw')
                btn.grid_columnconfigure(1, weight=1)

                # Defaults
                if label!=None: BUTTONS[index]['label'].set(label)
                if url!=None: BUTTONS[index]['url'].set(url)
            else:
                messagebox.showinfo('Discord Presence', 'You can only add up to 2 buttons', parent=root)

        def update_assets():
            assets = self.get_assets(ID.get())
            if assets==None: messagebox.showerror('Client ID Error', 'Invalid client ID!', parent=root)            
            else:
                images = ['None']
                for image in assets: images.append(image['name'])
                large_image.configure(values=images)
                small_image.configure(values=images)

        # Widgets
        # self.preview = Canvas(root, bd=0, highlightthickness=0)
        # self.preview.grid(row=0,column=0, columnspan=3,padx=10,pady=5)

        CTkLabel(root, text='Name', anchor=E).grid(row=1,column=0,padx=5,pady=5)
        CTkEntry(root, textvariable=NAME, placeholder_text='My Presence').grid(row=1,column=1,columnspan=2,padx=5,pady=5,sticky=EW)

        CTkLabel(root, text='Client ID', anchor=E).grid(row=2,column=0,padx=5,pady=5)
        id = CTkEntry(root, textvariable=ID, show='*', placeholder_text='client id')
        id.bind('<FocusOut>', lambda e: update_assets())
        id.grid(row=2,column=1,columnspan=2,padx=5,pady=5,sticky=EW)

        CTkLabel(root, text='State', anchor=E).grid(row=3,column=0,padx=5,pady=5)
        CTkEntry(root, textvariable=STATE, placeholder_text='Playing Solo').grid(row=3,column=1,columnspan=2,padx=5,pady=5,sticky=EW)

        CTkLabel(root, text='Details', anchor=E).grid(row=4,column=0,padx=5,pady=5)
        CTkEntry(root, textvariable=DETAILS, placeholder_text='Competitive - Captain\'s Mode').grid(row=4,column=1,columnspan=2,padx=5,pady=5,sticky=EW)
        
        CTkLabel(root, text='Large Image', anchor=E).grid(row=5,column=0,padx=5,pady=5)
        large_image = CTkOptionMenu(root, variable=LARGE_IMAGE, values=['default'])
        large_image.grid(row=5,column=1,columnspan=2,padx=5,pady=5,sticky=EW)
        
        CTkLabel(root, text='Large Text', anchor=E).grid(row=6,column=0,padx=5,pady=5)
        CTkEntry(root, textvariable=LARGE_TEXT, placeholder_text='Blade\'s Edge Arena').grid(row=6,column=1,columnspan=2,padx=5,pady=5,sticky=EW)
        
        CTkLabel(root, text='Small Image', anchor=E).grid(row=7,column=0,padx=5,pady=5)
        small_image = CTkOptionMenu(root, variable=SMALL_IMAGE, values=['default'])
        small_image.grid(row=7,column=1,columnspan=2,padx=5,pady=5,sticky=EW)

        CTkLabel(root, text='Small Text', anchor=E).grid(row=8,column=0,padx=5,pady=5)
        CTkEntry(root, textvariable=SMALL_TEXT, placeholder_text='Rogue - Level 100').grid(row=8,column=1,columnspan=2,padx=5,pady=5,sticky=EW)
        
        CTkLabel(root, text='Buttons', anchor=E).grid(row=9,column=0,padx=5,pady=5)
        CTkButton(root, image=self.ADD, text='', command=add_btn).grid(row=9,column=1,padx=5,pady=5)
        btns = CTkFrame(root, width=358, height=97)
        btns.grid(row=10,column=1,columnspan=2,padx=5,pady=5,sticky='nesw')
        btns.grid_columnconfigure(0, weight=1)

        delete_btn = CTkButton(root, text='Delete', command=delete)
        delete_btn.grid(row=11,column=0,padx=5,pady=5,sticky=EW)
        cancel_btn = CTkButton(root, text='Cancel', command=root.destroy)
        cancel_btn.grid(row=11,column=1,padx=5,pady=5,sticky=EW)
        confirm_btn = CTkButton(root, text='Confirm', command=confirm)
        confirm_btn.grid(row=11,column=2,padx=5,pady=5,sticky=EW)

        # Responsive
        root.grid_columnconfigure([1, 2], weight=1)

        # Default values
        if profile!=None:
            PROFILE_ID.set(profile.filename)
            NAME.set(profile.name)
            ID.set(profile.id)
            if type(profile.presence) == Presence:
                STATE.set(profile.presence.state)
                DETAILS.set(profile.presence.details)
                LARGE_IMAGE.set(profile.presence.large_image)
                LARGE_TEXT.set(profile.presence.large_text)
                SMALL_IMAGE.set(profile.presence.small_image)
                SMALL_TEXT.set(profile.presence.small_text)
                if profile.presence.buttons!=None:
                    for button in profile.presence.buttons:
                        add_btn(button.label, button.url)
            update_assets()
        else:
            delete_btn.configure(state=DISABLED)

    def new(self):
        """Create new profile"""
        def confirm(profile:Profile):
            profile.save()
            self.reload()
        self.profile_screen(confirm)

    def edit(self):
        """Edit the current profile"""
        def confirm(profile:Profile):
            profile.save()
            self.reload()
        
        profile = self.get_profile(name=self.PROFILE.get())
        self.profile_screen(confirm, profile)

if __name__ == '__main__':
    app=App()
    app.mainloop()