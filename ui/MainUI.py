import os
import json
import tempfile

from tkinter import Frame, Tk, Label, RAISED, Button, ttk, Scrollbar, Text, HORIZONTAL, BOTTOM, RIGHT, NONE, X, Y, \
    messagebox, Menu, BOTH, LEFT, END
from tkinter import filedialog as fd

from pathlib import Path

from parsing import SwimlaneParser
from svg.Errors import SVGSizeError
from svg.SVGGenerator import SVGRenderer
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo

# Global Variables
dir_name = ""
design_filename = ""
home_dir = ""
config = {}
config_file = ""
output_file_name = ""
text = None
label_design_file = None
root = None


def donothing():
    pass


def on_closing():
    global root

    if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
        root.destroy()


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
            config = json.load(f)
            design_filename = config['design_file']
            dir_name = config['out_dir']
            label_design_file.config(text=design_filename)
            # label_output_dir.config(text=dir_name)
    else:
        if home_dir.exists() and home_dir.is_dir():
            pass
        else:
            os.mkdir(home_dir)
        config = {"design_file": str(Path.home()), "out_dir": str(Path.home())}

        with open(config_file, 'w') as f:
            json.dump(config, f)


def update_config_file():
    global config
    config = {"design_file": design_filename, "out_dir": dir_name}

    with open(config_file, 'w') as f:
        json.dump(config, f)


def select_dir():
    global dir_name
    global label_output_dir
    dir_name = fd.askdirectory()

    label_output_dir.config(text=dir_name)


def select_file():
    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )

    global design_filename
    global label_design_file
    design_filename = fd.askopenfilename(
        title='Open a Design File',
        initialdir=str(design_filename),
        filetypes=filetypes)
    # label_design_file.config(text=design_filename)
    with open(design_filename, 'r') as f:
        text.insert(1.0, f.read())


def generate_svg_file(update_conf_file_after_gen=True):
    global output_file_name
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

    # Textarea
    editor_frame = Frame(root)
    editor_frame.pack(fill=BOTH, expand=True)

    # Horizontal (x) Scroll bar
    x_scrollbar = Scrollbar(editor_frame, orient=HORIZONTAL)
    x_scrollbar.pack(side=BOTTOM, fill=X)

    # Vertical (y) Scroll Bar
    y_scrollbar = Scrollbar(editor_frame)
    y_scrollbar.pack(side=RIGHT, fill=Y)

    # Text Widget
    text = Text(editor_frame, wrap=NONE, undo=True, xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set,
                borderwidth=3)
    text.pack(expand=True, fill='both')

    # Configure the scrollbars
    x_scrollbar.config(command=text.xview)
    y_scrollbar.config(command=text.yview)

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
    file_menu.add_command(label="Open", command=select_file)
    file_menu.add_command(label="Save", command=donothing)
    file_menu.add_command(label="Save as...", command=select_dir)
    file_menu.add_command(label="Close", command=on_closing)

    menu_bar.add_cascade(label="File", menu=file_menu)

    create_settings_dir_if_needed()

    # show window
    root.config(menu=menu_bar)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    draw_window()
