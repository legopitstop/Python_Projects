from tkinter import LEFT, W,E, Button, Frame, Label, Spinbox, StringVar, Tk,Entry,LabelFrame, Toplevel, filedialog,messagebox,IntVar
import re,os
from tkinter.ttk import Progressbar

from validators import length

LOCAL = os.path.dirname(os.path.realpath(__file__))

class App():
    def __init__(self):
        root=Tk()
        root.title('Time Creator')
        root.resizable(False,False)
        root.config(pady=5,padx=5)
        root.iconbitmap(LOCAL+'/icon.ico')
        # Varables
        NAME = StringVar()
        NAME.set('#timer')
        OBJECTIVE=StringVar()
        OBJECTIVE.set('main.timer')
        TIME=StringVar()
        TIME.set('05:00')
        PROGRESS=IntVar()
        PROGRESS.set(0)

        # Functions
        def save():
            if NAME.get()!='' and OBJECTIVE.get()!='' and TIME.get()!='':
                types=[('MC LANG','.mcfunction')]
                path = filedialog.asksaveasfilename(confirmoverwrite=True,defaultextension='.mcfunction',filetypes=types,initialfile='time.mcfunction')
                if path!='':
                    if re.match(r'^[0-9]{2}:[0-9]{2}$',TIME.get()):
                        # Start progressbar
                        default = '# Desc: (Generated) Converts scoreboard time to actionbar time.\n#\n# Called By: #minecraft:tick\n'
                        def get_sec():
                            l = TIME.get().split(':')
                            return l[1]
                        def get_min():
                            l = TIME.get().split(':')
                            return int(l[0])
                        def get_time():
                            l = TIME.get().split(':')
                            sec = 0
                            count=0
                            for i in l:
                                if count==0:
                                    sec+=get_min()*60
                                else:
                                    sec+=int(get_sec())
                                count+=1
                            return sec
                        tick=0
                        min=0
                        sec=0
                        for i in range(get_time()+1):
                            default+='\nexecute if score '+NAME.get()+' '+OBJECTIVE.get()+' matches '+str(tick) +'..' +str(tick+19)+' run title @a actionbar {"text":"%s:%s"}'%(str(min).zfill(2),str(sec).zfill(2))
                            # print(min,':',sec, ' - ',tick,'..',str(tick+19))
                            sec+=1
                            tick+=20
                            if sec>=60:
                                min+=1
                                sec=0
                        opn = open(path,'w')
                        opn.write(default)
                        opn.close()
                        q = messagebox.askyesno('Open','Do you want to open the file?')
                        if q==True:
                            try: os.startfile(path)
                            except: messagebox.showerror('error','Failed to open file.')
                        root.destroy()
                    else:
                        messagebox.showerror('error','Invalid time format. MM:SS')
            else:
                messagebox.showerror('error','Missing required field(s)')
            
        def validate():
            if re.match(r'^[0-9]{2}:[0-9]{2}$',TIME.get()):
                time['bg'] = 'white'
            else:
                time['bg'] = 'red'

        # Widgets
        Label(root,text='Display a formatted scoreboard via the actionbar without having to convert score times.',wraplength=400,justify=LEFT).grid(row=0,column=0,columnspan=2,sticky=W)

        score = LabelFrame(root,text='Scoreboard',pady=5,padx=5)
        Label(score,text='Name:').grid(row=0,column=0,sticky=E)
        Entry(score,textvariable=NAME).grid(row=0,column=1)
        Label(score,text='Objective:').grid(row=1,column=0,sticky=E)
        Entry(score,textvariable=OBJECTIVE).grid(row=1,column=1)
        score.grid(row=1,column=0,pady=5,padx=5)

        option = LabelFrame(root,text='Options',pady=5,padx=5)
        Label(option,text='Time:').grid(row=0,column=0)
        time = Entry(option,textvariable=TIME)
        time.bind('<KeyRelease>',lambda e: validate())
        time.grid(row=0,column=1)
        option.grid(row=1,column=1,pady=5,padx=5)

        foot=Frame(root)
        Button(foot,text='Save',padx=20,command=save).grid(row=0,column=1,padx=5)
        Button(foot,text='Cancel',padx=20,command=root.destroy).grid(row=0,column=2,padx=5)
        foot.grid(row=2,column=0,columnspan=2,sticky=E)


        root.mainloop()

app=App()