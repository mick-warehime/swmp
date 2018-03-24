from tkinter import *
from tkinter.messagebox import *
from tkinter import filedialog
from tkinter import colorchooser


root = Tk()

def answer():
    showerror("Answer", "Sorry, no answer available")


def callback():
    if askyesno('Verify', 'Really quit?'):
        showwarning('Yes', 'Not yet implemented')
    else:
        showinfo('No', 'Quit has been cancelled')


Button(text='Quit', command=callback).pack(fill=X)
Button(text='Answer', command=answer).pack(fill=X)


def file_callback():
    name = filedialog.askopenfilename()
    print(name)


errmsg = 'Error!'
Button(text='File Open', command=file_callback).pack(fill=X)


def color_callback():
    result = colorchooser.askcolor(color="#6A9662",
                                   title="Dvir's Color Chooser")
    print(result)


Button(root,
       text='Choose Color',
       fg="darkgreen",
       command=color_callback).pack(side=LEFT, padx=10)
Button(text='Really Quit',
       command=root.quit,
       fg="red").pack(side=LEFT, padx=10)

mainloop()
