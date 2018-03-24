from tkinter import *

canvas_width = 200
canvas_height = 100

colours = ("#476042", "yellow")
box = []

for ratio in (0.2, 0.35):
    box.append((canvas_width * ratio,
                canvas_height * ratio,
                canvas_width * (1 - ratio),
                canvas_height * (1 - ratio)))

master = Tk()

w = Canvas(master,
           width=canvas_width,
           height=canvas_height)
w.pack()

for dim, color in zip(box, colours):
    w.create_rectangle(dim[0], dim[1], dim[2], dim[3], fill=color)

w.create_line(0, 0,  # origin of canvas
              box[0][0], box[0][1],
              # coordinates of left upper corner of the box[0]
              fill=colours[0],
              width=3)
w.create_line(0, canvas_height,  # lower left corner of canvas
              box[0][0], box[0][3],  # lower left corner of box[0]
              fill=colours[0],
              width=3)
w.create_line(box[0][2], box[0][1],  # right upper corner of box[0]
              canvas_width, 0,  # right upper corner of canvas
              fill=colours[0],
              width=3)
w.create_line(box[0][2], box[0][3],  # lower right corner pf box[0]
              canvas_width, canvas_height,  # lower right corner of canvas
              fill=colours[0], width=3)

w.create_text(canvas_width / 2,
              canvas_height / 2,
              text="Python")
mainloop()
