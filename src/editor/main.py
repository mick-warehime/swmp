"""Editor for creating new quests."""
import tkinter
from tkinter import filedialog

from data.input_output import load_quest_data
from editor.util import close_window_after_call, assert_yaml_filename


def _start_window() -> tkinter.Tk:
    root = tkinter.Tk()
    root.resizable(width=False, height=False)
    root.title('Quest editor')
    return root


def _quest_editor_window(filename: str) -> tkinter.Tk:
    assert_yaml_filename(filename)

    root = tkinter.Tk()
    root.geometry('{}x{}'.format(800, 600))
    root.title(filename)

    quest_data = load_quest_data(filename,full_path=True)
    print(quest_data)


    return root


def _new_quest() -> None:
    filename = filedialog.asksaveasfilename()
    if filename[-4:] != '.yml':
        filename += '.yml'
    _quest_editor_window(filename)


def _open_quest() -> None:
    filename = filedialog.askopenfilename()

    _quest_editor_window(filename)


def main() -> None:
    root = _start_window()

    new_fun = close_window_after_call(_new_quest, root)
    new_button = tkinter.Button(root, text="New Quest", command=new_fun)
    new_button.pack(pady=10)

    open_fun = close_window_after_call(_open_quest, root)
    open_button = tkinter.Button(root, text="Open Quest", command=open_fun)
    open_button.pack(pady=10)

    quit_button = tkinter.Button(root, text="Quit", command=root.quit)
    quit_button.pack(pady=10)

    tkinter.mainloop()


if __name__ == '__main__':
    main()
