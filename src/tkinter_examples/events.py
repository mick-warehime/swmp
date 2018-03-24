from tkinter import *

root = Tk()


def hello(event):
    print("Single Click, Button-l")


def quit(event):
    print("Double Click, so let's stop")
    root.quit()
    # import sys;
    # sys.exit()


def motion(event):
    print("Mouse position: (%s %s)" % (event.x, event.y))
    return


master = Tk()
whatever_you_do = "Whatever you do will be insignificant, but it is very " \
                  "important that you do; it.\n(Mahatma Gandhi)"
msg = Message(master, text=whatever_you_do)
msg.config(bg='lightgreen', font=('times', 24, 'italic'))
msg.bind('<Motion>', motion)
msg.pack()

widget = Button(root, text='Mouse Clicks')
widget.pack()
widget.bind('<Button-1>', hello)
widget.bind('<Double-1>', quit)
widget.mainloop()
