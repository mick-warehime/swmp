import tkinter as tk
import random

root = tk.Tk()
# width x height + x_offset + y_offset:
root.geometry("170x200+200+330")

languages = ['Python', 'Perl', 'C++', 'Java', 'Tcl/Tk']
labels = range(5)
for i, language in enumerate(languages):
    ct = [random.randrange(256) for x in range(3)]
    brightness = int(round(0.299 * ct[0] + 0.587 * ct[1] + 0.114 * ct[2]))
    bg_colour = "#%02x%02x%02x" % tuple(ct)
    l = tk.Label(root,
                 text=language,
                 fg='White' if brightness < 120 else 'Black',
                 bg=bg_colour)
    l.place(x=20, y=30 + i * 30, width=120, height=25)

root.mainloop()