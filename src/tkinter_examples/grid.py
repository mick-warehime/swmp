from tkinter import *

root = Tk()
colours = ['red', 'green', 'orange', 'white', 'yellow', 'blue']

entries = []
for row, color in enumerate(colours):
    Label(root, text=color, relief=RIDGE, width=15).grid(row=row, column=0)
    entry = Entry(root, bg=color, relief=SUNKEN, width=10)
    entries.append(entry)
    entry.grid(row=row, column=1)


def print_all_entries():
    last = "{}".format(entries[-1].get())
    print("".join("{},\n".format(ent.get()) for ent in entries[:-1]) + last)


button = Button(root, text='Print all', width=25, command=print_all_entries)
button.grid(row=len(colours), column=0)

mainloop()
