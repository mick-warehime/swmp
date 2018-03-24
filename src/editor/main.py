"""Editor for creating new quests."""
import tkinter
from tkinter import filedialog

from data.input_output import load_quest_data
from editor.util import assert_yaml_filename, draw_circle, close_window_after_call
from quests.scenes.builder import SceneType


def _start_window() -> tkinter.Tk:
    root = tkinter.Tk()
    root.resizable(width=False, height=False)
    root.title('Quest editor')
    return root


def _quest_editor_window(filename: str, full_path=True) -> tkinter.Tk:
    assert_yaml_filename(filename)

    root = tkinter.Tk()
    root.title(filename)


    layer_spacing = 50

    canvas = tkinter.Canvas(root, width=800, height=600)
    canvas.pack()

    quest_data = load_quest_data(filename, full_path)
    print(quest_data)
    root_data = quest_data['root']
    scene_type = SceneType(root_data['type'])

    data_keys = scene_type.arg_labels
    print(data_keys)

    draw_circle(30, 30, 20, canvas)

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
    # root = _start_window()
    #
    # new_fun = close_window_after_call(_new_quest, root)
    # new_button = tkinter.Button(root, text="New Quest", command=new_fun)
    # new_button.pack(pady=10)
    #
    # open_fun = close_window_after_call(_open_quest, root)
    # open_button = tkinter.Button(root, text="Open Quest", command=open_fun)
    # open_button.pack(pady=10)
    #
    # quit_button = tkinter.Button(root, text="Quit", command=root.quit)
    # quit_button.pack(pady=10)

    _quest_editor_window('zombie_quest.yml', full_path=False)

    tkinter.mainloop()


if __name__ == '__main__':
    main()
