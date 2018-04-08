import tkinter as tk

root = tk.Tk()
root.title("Counting")

count = tk.IntVar(root, 0)

count_msg = tk.Message(root, textvariable=count)
count_msg.pack()

label = tk.Label(root, fg="dark green")
label.pack()


def increment(var):
    var.set(var.get() + 1)


adder = tk.Button(root, text='Add', width=25, command=lambda: increment(count))
adder.pack()

button = tk.Button(root, text='Stop', width=25, command=root.destroy)
button.pack()
root.mainloop()
