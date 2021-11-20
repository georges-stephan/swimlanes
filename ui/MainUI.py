import os
import json

from tkinter import Frame, Tk, Label, RAISED, Button
from tkinter import filedialog as fd

from pathlib import Path

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

# initialize tkinter
root = Tk()
app = Window(root)
label_design_file = Label(root, textvariable="", relief=RAISED)
label_output_dir = Label(root, textvariable="", relief=RAISED)

# set window props
root.wm_title("Swimlanes Diagram")
root.resizable(True, True)
root.geometry('800x150')


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


def generate_svg_file():
    print(f"Design filename is {design_filename}, result will be saved in {dir_name}")

    input_file_dir, input_file_name = os.path.split(design_filename)
    output_file_name = f"{dir_name}{input_file_name}.svg"

    if Path(output_file_name).exists():
        answer = askyesno(title='Confirmation',
                          message=f'The file:\n{output_file_name}\nalready exists, overwrite it?')
        if answer:
            Path(output_file_name).unlink(True)
            diagram = SwimlaneParser.load_file(design_filename)

            generator = SVGRenderer(diagram, 800, 2)

            with open(output_file_name, 'w') as f:
                try:
                    f.write(generator.get_svg_string())
                    showinfo("Feedback", "Completed")
                    update_config_file()
                except SVGSizeError as svg_error:
                    preferred_height = int(svg_error.__str__().split(':')[0])
                    print(f"preferred_height:{preferred_height}")
                    generator = SVGRenderer(diagram, 800, preferred_height)
                    f.close()
                    with open(output_file_name, 'w') as fii:
                        fii.write(generator.get_svg_string())
                        showinfo("Feedback", "Completed")
                        update_config_file()
        else:
            showinfo("Feedback", "Ok, Nothing was generated")


# open file button
open_button = Button(
    root,
    text='Open a Design File',
    command=select_file
)

# output dir button
output_dir_button = Button(
    root,
    text='Open a Target Dir',
    command=select_dir
)

# generate output button
generate_svg_button = Button(
    root,
    text='Generate SVG',
    command=generate_svg_file
)

create_settings_dir_if_needed()

open_button.pack(expand=True)
label_design_file.pack(expand=True)

output_dir_button.pack(expand=True)
label_output_dir.pack(expand=True)

generate_svg_button.pack(expand=True)

# show window
root.mainloop()
