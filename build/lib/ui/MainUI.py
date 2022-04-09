import os
import json
import sys
import tempfile
from json import JSONDecodeError

from tkinter import Frame, Tk, Label, Button, Scrollbar, Text, HORIZONTAL, BOTTOM, RIGHT, NONE, X, Y, \
    messagebox, Menu, BOTH, LEFT, END, PanedWindow, VERTICAL, DISABLED
from tkinter import filedialog as fd

from pathlib import Path

from parsing import SwimlaneParser
from svg.Errors import SVGSizeError
from svg.SVGGenerator import SVGRenderer
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo

from ui.SwimlaneEditorModel import SwimlaneEditorModel

# Global Variables
dir_name = None
design_filename = None
home_dir = None
config = {}
config_file = None
output_file_name = None
text = None
label_design_file = None
root = None
swimlaneEditorModel = None  # TODO init to blank when starting the UI

filetypes = (
    ('text files', '*.txt'),
    ('All files', '*.*')
)


def donothing():
    pass


def on_closing():
    global root
    global swimlaneEditorModel
    global text

    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        if swimlaneEditorModel is not None:
            # Text area contains text from a file. Check if contents needs saving
            if swimlaneEditorModel.is_needs_saving(text.get('1.0', END)):
                # Content loaded from file and actual content in the text area widget are changed.
                if messagebox.askyesno("Save", "Content changed, do you want to save it?"):
                    # save to file
                    save_file_as()
                    sys.exit()
                else:
                    # Content changed, but the user does not want to keep it
                    sys.exit()
            else:
                # loaded and text area content are the same
                sys.exit()
        elif len(SwimlaneEditorModel.remove_control_characters(text.get('1.0', END))) > 0:
            # Nothing was loaded from file, however, the text area is not empty
            if messagebox.askyesno("Save", "Content not saved, do you want to save it?"):
                save_file_as()
                sys.exit()
            else:
                # user does not care about the content
                sys.exit()
        else:
            # Text area is empty
            sys.exit()
    else:
        # The user refrained from quitting
        pass


# Button to generate the SVG
def generate_and_view():
    global design_filename
    global dir_name

    svg_text = text.get(1.0, END)
    tmp_design_filename = tempfile.TemporaryFile(mode='w+b', suffix='.txt', delete=False)
    dir_name, ignore_attribute = os.path.split(tmp_design_filename.name)
    dir_name = f"{dir_name}\\"

    with open(tmp_design_filename.name, 'w') as f:
        f.write(svg_text)

    design_filename = tmp_design_filename.name
    generate_svg_file(update_conf_file_after_gen=False)
    os.startfile(output_file_name)


def save_file_as():
    global design_filename
    global dir_name

    if dir_name is not None and Path(dir_name).exists():
        design_file = fd.asksaveasfile(title='Save a Design File as', filetypes=filetypes,
                                       defaultextension=filetypes,
                                       initialdir=dir_name)
    else:
        design_file = fd.asksaveasfile(title='Save a Design File as', filetypes=filetypes,
                                       defaultextension=filetypes)
    if design_file is not None:
        # design_filename = design_file.name
        dir_name, design_filename = os.path.split(design_file.name)
        print(f"Dir name:{dir_name}, design file name:{design_filename}, text is {text.get('1.0', END)}")
        try:
            design_file.write(text.get('1.0', END))
            update_config_file()
        finally:
            design_file.close()


def create_settings_dir_if_needed():
    global home_dir
    global config
    global config_file
    global design_filename
    global dir_name
    global label_design_file

    home_dir = Path(f"{str(Path.home())}/.py-swimlanes/")
    config_file = f"{home_dir}/py-swimlanes-config.json"

    if home_dir.exists() and home_dir.is_dir() and Path(config_file).exists():
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
                design_filename = config['design_file']
                dir_name = config['out_dir']
            except JSONDecodeError as e:
                print(f"Config file damaged:{e.msg}")
                config = {"design_file": str(Path.home()), "out_dir": str(Path.home())}

                with open(config_file, 'w') as ff:
                    json.dump(config, ff)
    else:
        if home_dir.exists() and home_dir.is_dir():
            pass
        else:
            os.mkdir(home_dir)
        config = {"design_file": str(Path.home()), "out_dir": str(Path.home())}

        with open(config_file, 'w') as f:
            json.dump(config, f)

    if home_dir is None:
        home_dir = str(Path.home())


def update_config_file():
    global config
    config = {"design_file": design_filename, "out_dir": dir_name}

    with open(config_file, 'w') as f:
        json.dump(config, f)


def select_dir():
    global dir_name
    dir_name = fd.askdirectory()


def select_and_load_file():
    global design_filename
    global label_design_file
    global swimlaneEditorModel
    global text

    design_filename = fd.askopenfilename(
        title='Open a Design File',
        initialdir=str(design_filename),
        filetypes=filetypes)

    if design_filename is None or design_filename == "":
        return

    label_design_file.config(text=design_filename)
    with open(design_filename, 'r') as f:
        text.insert(1.0, f.read())
    swimlaneEditorModel = SwimlaneEditorModel(text.get('1.0', END))


def generate_svg_file(update_conf_file_after_gen=True):
    global output_file_name
    global design_filename

    print(f"Design filename is {design_filename}, result will be saved in {dir_name}")

    input_file_dir, input_file_name = os.path.split(design_filename)
    output_file_name = f"{dir_name}{input_file_name}.svg"

    override = True
    if Path(output_file_name).exists():
        override = askyesno(title='Confirmation',
                            message=f'The file:\n{output_file_name}\nalready exists, overwrite it?')

    generate_design = True
    if override:
        if Path(output_file_name).exists():
            Path(output_file_name).unlink(True)
    else:
        showinfo("Feedback", "Ok, Nothing was generated")
        generate_design = False

    if generate_design:
        diagram = SwimlaneParser.load_file(design_filename)
        generator = SVGRenderer(diagram, 800, 2)
        with open(output_file_name, 'w') as f:
            try:
                f.write(generator.get_svg_string())
                showinfo("Feedback", "Completed")
                if update_conf_file_after_gen:
                    update_config_file()
            except SVGSizeError as svg_error:
                preferred_height = int(svg_error.__str__().split(':')[0])
                print(f"preferred_height:{preferred_height}")
                # TODO find a way to calculate the preferred width instead of hard-coding 800. Ex. add a 'width' keyword
                generator = SVGRenderer(diagram, 800, preferred_height)
                f.close()
                with open(output_file_name, 'w') as fii:
                    fii.write(generator.get_svg_string())
                    showinfo("Feedback", "Completed")
                    if update_conf_file_after_gen:
                        update_config_file()


def draw_window():
    global root
    global text
    global label_design_file
    # initialize tkinter
    root = Tk()

    # set window props
    root.wm_title("Swimlanes Diagram")
    root.resizable(True, True)
    root.geometry('800x600')

    panedWindow = PanedWindow(root, orient=HORIZONTAL, showhandle=True)
    panedWindow.pack(fill=BOTH, expand=1)

    # Textarea
    editor_frame = Frame()
    editor_frame.pack(fill=BOTH, expand=True)
    panedWindow.add(editor_frame)

    editor_help_frame = Frame(panedWindow)
    editor_help_frame.pack(fill=BOTH, expand=True)
    panedWindow.add(editor_help_frame)

    # Horizontal (x) Scroll bar
    x_scrollbar = Scrollbar(editor_frame, orient=HORIZONTAL)
    x_scrollbar.pack(side=BOTTOM, fill=X)

    x_scrollbar_help = Scrollbar(editor_help_frame, orient=HORIZONTAL)
    x_scrollbar_help.pack(side=BOTTOM, fill=X)

    # Vertical (y) Scroll Bar
    y_scrollbar = Scrollbar(editor_frame)
    y_scrollbar.pack(side=RIGHT, fill=Y)

    y_scrollbar_help = Scrollbar(editor_help_frame)
    y_scrollbar_help.pack(side=RIGHT, fill=Y)

    # Text Widget
    text = Text(editor_frame, wrap=NONE, undo=True, xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set,
                borderwidth=3)
    text.pack(expand=True, fill='both')

    # Help Widget
    text_help = Text(editor_help_frame, wrap=NONE, undo=True, xscrollcommand=x_scrollbar.set,
                     yscrollcommand=y_scrollbar.set,
                     borderwidth=3)
    text_help.insert(1.0, """
    title: Welcome to Python Swimlanes

    One -> Two: Message

    note:
    **Python Swimlanes** is a simple online tool for creating _sequence diagrams_.

    Two -> Two: To self

    Two -->> Three: _Notification_

    Two -> One: `ok`

    note: See **Built for Fun** for more details
    """)
    text_help.pack(expand=True, fill='both')
    text_help.config(state=DISABLED)

    # Configure the scrollbars
    x_scrollbar.config(command=text.xview)
    y_scrollbar.config(command=text.yview)

    x_scrollbar_help.config(command=text_help.xview)
    y_scrollbar_help.config(command=text_help.yview)

    button_frame = Frame(root)
    button_frame.pack(fill=X)

    generate_svg_button = Button(button_frame, text="Generate and View SVG", command=generate_and_view)
    generate_svg_button.pack(side=RIGHT, padx=5, pady=5)

    label_design_file = Label(button_frame)
    label_design_file.pack(side=LEFT, padx=5, pady=5)

    # Menu
    menu_bar = Menu(root)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New", command=lambda: text.delete(1.0, END))
    file_menu.add_command(label="Open", command=select_and_load_file)
    file_menu.add_command(label="Save", command=donothing)
    file_menu.add_command(label="Save as...", command=save_file_as)
    file_menu.add_command(label="Close", command=on_closing)

    menu_bar.add_cascade(label="File", menu=file_menu)

    create_settings_dir_if_needed()

    # show window
    root.config(menu=menu_bar)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    draw_window()
