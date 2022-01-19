from tkinter import messagebox

def required(**kwrgs):
    """A list of required tkinter varables"""
    missing=[]
    for i in kwrgs:
        # print(i)
        if kwrgs[i].get()=='':
            missing.append(str(i))
    try:
        if missing[0]:
            messagebox.showwarning('Required','Missing required entries %s'%(missing))
            return False
    except:
        return True