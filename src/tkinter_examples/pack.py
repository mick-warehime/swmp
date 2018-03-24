from tkinter import *

root = Tk()

Label(root, text="Red Sun", bg="red", fg="white").pack(fill=X,pady=4)
Label(root, text="Green Grass", bg="green", fg="black").pack(side=RIGHT)
Label(root, text="Blue Sky", bg="blue", fg="white").pack(side=LEFT,ipady=5)

mainloop()