import os
import json
import tempfile

from tkinter import Frame, Tk, Label, RAISED, Button, ttk, Scrollbar, Text, HORIZONTAL, BOTTOM, RIGHT, NONE, X, Y, END
from tkinter import filedialog as fd

from pathlib import Path
from tkinter.ttk import Notebook

from parsing import SwimlaneParser
from svg.Errors import SVGSizeError
from svg.SVGGenerator import SVGRenderer
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master


dir_name = ""
design_filename = ""
home_dir = ""
config = {}
config_file = ""
output_file_name = ""

# initialize tkinter
root = Tk()
app = Window(root)

# set window props
root.wm_title("Swimlanes Diagram")
root.resizable(True, True)
root.geometry('800x600')

# Tabs
my_notebook = ttk.Notebook(root)
my_notebook.pack(fill="both")

my_frame1 = Frame(my_notebook)
my_frame2 = Frame(my_notebook)

my_frame1.pack(fill="both", expand=1)
my_frame2.pack(fill="both", expand=1)

my_notebook.add(my_frame1, text="Interactive")
my_notebook.add(my_frame2, text="Batch")

# Labels
label_design_file = Label(my_frame2, textvariable="", relief=RAISED)
label_output_dir = Label(my_frame2, textvariable="", relief=RAISED)

# Textarea
# Horizontal (x) Scroll bar
xscrollbar = Scrollbar(my_frame1, orient=HORIZONTAL)
xscrollbar.pack(side=BOTTOM, fill=X)

# Vertical (y) Scroll Bar
yscrollbar = Scrollbar(my_frame1)
yscrollbar.pack(side=RIGHT, fill=Y)

# Text Widget
text = Text(my_frame1, wrap=NONE, undo=True, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
text.pack()

# Configure the scrollbars
xscrollbar.config(command=text.xview)
yscrollbar.config(command=text.yview)


# Button to generate the SVG
def generate_and_view():
    global design_filename
    global dir_name

    svg_text = text.get(1.0, END)
    tmp_design_filename = tempfile.TemporaryFile(mode='w+b', suffix='.txt', delete=False)
    dir_name, xxx = os.path.split(tmp_design_filename.name)
    dir_name = f"{dir_name}\\"

    with open(tmp_design_filename.name, 'w') as f:
        f.write(svg_text)

    design_filename = tmp_design_filename.name

    generate_svg_file(update_conf_file_after_gen=False)

    os.startfile(output_file_name)


button_frame = Frame(my_frame1)
button_frame.pack()

generate_svg_button = Button(button_frame, text="View SVG", command=generate_and_view)
generate_svg_button.grid(row=0, column=0)


def create_settings_dir_if_needed():
    global home_dir
    global config
    global config_file
    global design_filename
    global dir_name

    home_dir = Path(f"{str(Path.home())}/.py-swimlanes/")
    config_file = f"{home_dir}/py-swimlanes-config.json"

    if home_dir.exists() and home_dir.is_dir() and Path(config_file).exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            design_filename = config['design_file']
            dir_name = config['out_dir']
            label_design_file.config(text=design_filename)
            label_output_dir.config(text=dir_name)
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
    label_design_file.config(text=design_filename)


def view_generated_svg():
    pass


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


# open file button
open_button = Button(
    my_frame2,
    text='Open a Design File',
    command=select_file
)

# output dir button
output_dir_button = Button(
    my_frame2,
    text='Open a Target Dir',
    command=select_dir
)

# open_button = Button(
#     my_frame1,
#     text='View Diagram',
#     command=view_generated_svg
# )

create_settings_dir_if_needed()

open_button.pack(expand=True)
label_design_file.pack(expand=True)

output_dir_button.pack(expand=True)
label_output_dir.pack(expand=True)

generate_svg_button.pack(expand=True)

# show window
root.mainloop()
