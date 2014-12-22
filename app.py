from tkinter import *
from random import randint

class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.floater = FloatingWindow(self)

def stitch(args):
    res = str.join(" ", [numFormat(arg) for arg in args])
    if len(args) == 2:
        res += ", diff=" + numFormat(abs(args[1] - args[0]))
    return res

def writeEnds(*args):
    return "ends " + stitch(args)

def writeStarts(*args):
    return "starts " + stitch(args)

frm = "{:.2f}"
def numFormat(num):
    return frm.format(num).rstrip("0").rstrip(".")

# Serato does not have a zero-th measure
def noZero(num):
    return numFormat(num if num > 0 else num - 1)

# 3 number pairs 10 measures at a time
def lineUp(a, b, inca=10, incb=10):
    res = ""
    for x in range(1, 4):
        if x > 1:
            res = " - " + res
        res = noZero(a - inca * x) + " " + noZero(b - incb * x) + res
    return res

# 3 number pairs 10 measures at a time
def lineUp1to2(a, b, inc=10):
    return lineUp(a, b, inc/2, inc)

# 3 number pairs 10 measures at a time
def lineUp2to1(a, b, inc=10):
    return lineUp(a, b, inc, inc/2)

evalFns = {
    "/-11": lineUp,
    "/-12": lineUp1to2,
    "/-21": lineUp2to1,
    "/+1": writeEnds,
    "/+0": writeStarts,
}

colors = "fcb6"
colors_len = len(colors)-1
def getColor():
    res = ""
    while len(res) < 6:
        colornum = randint(0, colors_len)
        res += colors[colornum] + colors[colors_len - colornum]
    return "#" + res

# ---------------------------------------------
class Ans(object):
    def __init__(self, ansVar, ansLabel):
        self.ansVar = ansVar
        self.ansLabel = ansLabel

class CalculatorInterface(Frame):
    def __init__(self, master, rows=3, columns=3):
        Frame.__init__(self, master)
        self["bg"] = "#111"
        c2 = "#1a1a1a"
        self.input1 = Entry(self, insertofftime=0, highlightbackground=c2, font="Arial 13", bd=0, bg=c2, highlightthickness=2, justify=CENTER, width=24)
        self.input1.grid(row=0, sticky=W)
        self.anss = list()

        crow = 0
        ccol = 0
        maxcol = columns - 1 # starting at index 0
        maxrow = rows - 1 # starting at index 0
        for _ in range((maxcol + 1) * (maxrow + 1) - 1):
            if (ccol + 1 > maxcol):
                crow += 1
                ccol = 0
            else:
                ccol += 1
            ansVar = StringVar()
            ansLabel = Label(self, textvariable=ansVar, font="Arial 13", bg=c2, width=24, justify=CENTER)
            ansLabel.grid(row=crow, column=ccol, padx=(5 if (ccol > 0 and ccol < maxcol) else 0),\
                          pady=(5 if (crow > 0 and crow < maxrow) else 0))
            ans = Ans(ansVar, ansLabel)
            self.anss.append(ans)

        self.input1.bind("<Return>", self.submit1)
        self.newColor()

    def focus(self):
        self.input1.focus_set()

    def newColor(self):
        newColor = getColor()
        self.input1["fg"] = newColor
        self.input1["insertbackground"] = newColor
        self.input1["highlightcolor"] = newColor


    def submit1(self, event):
        text = self.input1.get()
        # /-11 56 4 -> lineUp(56, 4)
        try:
            sp = text.split("++")
            if sp[0] in evalFns:
                text = evalFns[sp[0]](*[float(a) for a in sp[1::]])
        except:
            return "break"

        try:
            evald = str(eval(text, {"__builtins__": {}}))
            if evald != text:
                text = text + " = " + evald
        except:
            pass
        prev = (self.input1["fg"], text)
        for ans in self.anss:
            use = prev
            prev = (ans.ansLabel["fg"], ans.ansVar.get())
            ans.ansLabel.config(fg=use[0])
            ans.ansVar.set(use[1])

        self.input1.delete(0, END)
        self.newColor()

# ---------------------------------------------

class FloatingWindow(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.protocol("WM_DELETE_WINDOW", lambda: master.destroy() )
        master.withdraw()
        self.overrideredirect(True)
        self.attributes( '-topmost', 1 )
        self["bg"] = "#111"

        self.calcInter = CalculatorInterface(self)
        self.calcInter.grid(row=0, column=0, padx=5, pady=5)

        self.bind("<ButtonPress-1>", self.StartMove)
        self.bind("<ButtonRelease-1>", self.StopMove)
        self.bind("<B1-Motion>", self.OnMotion)

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.calcInter.focus()
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))



app=App()
app.mainloop()