from tkinter import E, W, BooleanVar, Button, Checkbutton, Entry, Label, Spinbox, Tk,LabelFrame,StringVar, Toplevel, filedialog, messagebox,IntVar
from tktooltip import ToolTip
import os
# Local
from required import required

LOCAL = os.path.dirname(os.path.realpath(__file__))

class main():
    def __init__(self):
        R=Tk()
        R.title('Score to bossbar')
        R.iconbitmap(LOCAL+'/icon.ico')
        R.resizable(False,False)
        R.config(pady=5,padx=5)
        # Varables
        NAME = StringVar()
        NAME.set('#Health')
        OBJECTIVE = StringVar()
        OBJECTIVE.set('bossbar')
        ID = StringVar()
        ID.set('minecraft:bossbar')
        VALUE=IntVar()
        VALUE.set(100)
        ERRORS=BooleanVar()
        ERRORS.set(True)

        # Functions
        def advanced_bossbar():
            A = Toplevel()
            A.title('Advanced')
            A.iconbitmap(LOCAL+'/icon.ico')
            A.geometry('250x100')
            A.resizable(False,False)
            A.config(pady=5,padx=5)

            Label(A,text='More features coming soon!',fg='red').grid(row=0,column=0)
            Button(A,text='Close',command=A.destroy).grid(row=1,column=0,sticky=E)

        def confirm():
            if required(name=NAME,objective=OBJECTIVE,namespace=ID):
                types = [('Minecraft Language','.mcfunction'),('Any','*')]
                path = filedialog.asksaveasfilename(confirmoverwrite=True,defaultextension='.mcfunction',initialfile='bossbar.mcfunction',filetypes=types)
                if path!='':
                    try:
                        file = '# Desc: (Generated) Converts scoreboard value to bossbar value\n#\n# Called By: #minecraft:tick\n\n'
                        score = NAME.get()+' '+OBJECTIVE.get()

                        if ERRORS.get() == True:
                            file+='execute if score '+score+' matches ..-1 run tellraw @a {"text":"WARN: Value must be more than 0","color":"yellow"}\nexecute if score '+score+' matches ..-1 run scoreboard players set '+score+' 0\nexecute if score '+score+' matches '+str(VALUE.get()+1) +'.. run tellraw @a {"text":"WARN: value must be less than '+str(VALUE.get()) +'","color":"yellow"}\nexecute if score '+score+' matches '+str(VALUE.get()+1) +'.. run scoreboard players set '+score+' '+str(VALUE.get()) +'\n\n'

                        for i in range(int(VALUE.get())+1):
                            file+='execute if score %s matches %s run bossbar set %s value %s\n'%(score,i,ID.get(),i)

                        # file.append('asd')
                        write = open(path,'w')
                        write.write(file)
                        write.close()

                        messagebox.showinfo('Success','Generated scoreboard to bossbar file.')
                        R.destroy()
                    except:
                        messagebox.showerror('Failed','Failed to generate file.')

        # Create Widgets
        SCORE = LabelFrame(R,text='Scoreboard',pady=5,padx=5)
        score_name = Label(SCORE,text='Name: ').grid(row=0,column=0,sticky=E)
        Entry(SCORE,textvariable=NAME).grid(row=0,column=1,sticky=W)
        score_obj = Label(SCORE,text='Objective:').grid(row=1,column=0,sticky=E)
        Entry(SCORE,textvariable=OBJECTIVE).grid(row=1,column=1,sticky=W)
        SCORE.grid(row=0,column=0,columnspan=2,pady=5,padx=5)

        BAR = LabelFrame(R,text='Bossbar',pady=5,padx=5)
        bar_id = Label(BAR,text='ID:').grid(row=0,column=0,sticky=E)
        Entry(BAR,textvariable=ID).grid(row=0,column=1,sticky=W)
        Button(BAR,text='Advanced',command=advanced_bossbar).grid(row=1,column=0,columnspan=2,sticky=W)
        BAR.grid(row=1,column=0,columnspan=2,pady=5,padx=5)

        OTHER = LabelFrame(R,text='Other',pady=5,padx=5)
        value = Label(OTHER,text='Value:').grid(row=0,column=0,sticky=E)
        Spinbox(OTHER,textvariable=VALUE,from_=0,to=2147483647).grid(row=0,column=1,sticky=W)
        fixer = Checkbutton(OTHER,text='Fixer',variable=ERRORS,onvalue=True,offvalue=False)
        OTHER.grid(row=2,column=0,columnspan=2,pady=5,padx=5)

        Button(R,text='Confirm',command=confirm,padx=10).grid(row=3,column=0)
        Button(R,text='Cancel',command=R.destroy,padx=10).grid(row=3,column=1)

        # Display Widgets
        fixer.grid(row=1,column=0,columnspan=2,sticky=W)


        # Tooltips
        ToolTip(fixer,msg='When score is outside the range it will show a warning message and fix the value.',width=200)


        R.mainloop()


app=main()