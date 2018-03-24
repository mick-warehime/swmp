from tkinter import *

canvas_width = 500
canvas_height = 150

max_ovals = 10

ovals = []


def paint(event):
    python_green = "#476042"
    x1, y1 = (event.x - 2), (event.y - 2)
    x2, y2 = (event.x + 2), (event.y + 2)

    ovals.append(w.create_oval(x1, y1, x2, y2, fill=python_green))
    if len(ovals) > max_ovals:
        w.delete(ovals[0])
        del ovals[0]


master = Tk()
master.title("Painting using Ovals")
w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
w.pack(expand=YES, fill=BOTH)
w.bind("<B1-Motion>", paint)

message = Label(master, text="Press and Drag the mouse to draw")
message.pack(side=BOTTOM)

mainloop()
