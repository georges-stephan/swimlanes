import os
import json
import sys
import tempfile
import logging.config
from tkinter.ttk import Entry

import yaml

from json import JSONDecodeError

from tkinter import Frame, Tk, Label, Button, Scrollbar, Text, HORIZONTAL, BOTTOM, RIGHT, NONE, X, Y, \
    Menu, BOTH, LEFT, END, PanedWindow, DISABLED, messagebox
from tkinter import filedialog as fd

from pathlib import Path

from diagram.parsing.SwimlaneParser import SwimlaneParser
from diagram.svg.SVGGenerator import SVGRenderer
from tkinter.messagebox import askyesno
from tkinter.messagebox import showinfo

from diagram.templates.FileTemplate import FileTemplate
from diagram.templates.Template import Template
from diagram.ui.SwimlaneEditorModel import SwimlaneEditorModel

# Logging configuration
with open(f'{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}..{os.path.sep}'
          f'logging-properties.yml', 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


class MainUI:

    def __init__(self):
        self.dir_name = None
        self.design_filename = None
        self.home_dir = None
        self.config = {}
        self.config_file = None
        self.output_file_name = None
        self.text = None
        self.label_design_file = None
        self.root = None
        self.swimlaneEditorModel = None  # TODO init to blank when starting the UI
        self.debug = False  # This flag changes the behavior of the application to make testing easier
        self.output_image_width_entry = None

        self.filetypes = (
            ('text files', '*.flow'),
            ('All files', '*.*')
        )

    def on_closing(self) -> None:
        """
        Should be invoked when a window closing event is triggered
        :return:
        """
        if self.debug:
            logger.info("Exiting immediately when running in Debug mode")
            sys.exit(0)

        if self.swimlaneEditorModel is None \
                and len(SwimlaneEditorModel.remove_control_characters(self.text.get('1.0', END))) < 1:
            logger.debug("Exiting immediately when textarea is empty")
            sys.exit(0)

        # Editor model is None (no data loaded from a previous file) and there is content in the text area
        self.save_file(save_as=True, exit_after_save=True)

    def generate_and_view(self) -> None:
        """
        Button to generate the SVG diagram
        :return:
        """
        svg_text = self.text.get(1.0, END)
        tmp_design_filename = tempfile.TemporaryFile(mode='w+b', suffix='.flow', delete=False)
        self.dir_name, ignore_attribute = os.path.split(tmp_design_filename.name)
        self.dir_name = f"{self.dir_name}{os.path.sep}"

        with open(tmp_design_filename.name, 'w') as f:
            f.write(svg_text)

        self.design_filename = tmp_design_filename.name
        self.generate_svg_file(update_conf_file_after_gen=False)
        os.startfile(self.output_file_name)

    def save_file_as(self) -> None:
        self.save_file(save_as=True)

    def save_file(self, save_as=False, exit_after_save=False) -> None:
        """
        Should be invoked to save the content in the editor
        :param exit_after_save: should we exit the program save is completed?
        :param save_as: should we prompt the user for a name?
        :return:
        """
        if save_as:
            logger.debug("Saving file as...")
        else:
            logger.debug("Saving file")

        if self.design_filename is None or save_as:
            # Got a save request, but we don't know the name of the file to save
            if self.dir_name is not None and Path(self.dir_name).exists():
                design_file_text_io = fd.asksaveasfile(title='Save a Design file as', filetypes=self.filetypes,
                                                       defaultextension=self.filetypes,
                                                       initialdir=self.dir_name)
            else:
                design_file_text_io = fd.asksaveasfile(title='Save a Design File as', filetypes=self.filetypes,
                                                       defaultextension=self.filetypes)
            try:
                design_file_text_io.write(self.text.get('1.0', END))
                self.update_config_file()
            finally:
                if design_file_text_io is not None:
                    design_file_text_io.close()
                    logger.info("Saved content.")
                if exit_after_save:
                    sys.exit(0)
        else:
            # A design file name is defined at the class level
            with open(self.design_filename, 'w') as f:
                f.write(self.text.get('1.0', END))
                logger.info(f"Saved content to {self.design_filename}.")
                if exit_after_save:
                    sys.exit(0)

    def create_settings_dir_if_needed(self) -> None:
        """
        Create the default config file if no config file is available
        :return:
        """
        self.home_dir = Path(f"{str(Path.home())}{os.path.sep}.py-swimlanes{os.path.sep}")
        self.config_file = f"{self.home_dir}{os.path.sep}py-swimlanes-config.json"

        if self.home_dir.exists() and self.home_dir.is_dir() and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                try:
                    self.config = json.load(f)
                    self.design_filename = self.config['design_file']
                    self.dir_name = self.config['out_dir']
                except JSONDecodeError as e:
                    logger.info(f"Config file damaged:{e.msg}")
                    self.config = {"design_file": str(Path.home()), "out_dir": str(Path.home())}

                    with open(self.config_file, 'w') as ff:
                        json.dump(self.config, ff)
        else:
            if self.home_dir.exists() and self.home_dir.is_dir():
                pass
            else:
                os.mkdir(self.home_dir)
            self.config = {"design_file": str(Path.home()), "out_dir": str(Path.home())}

            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)

        if self.home_dir is None:
            self.home_dir = str(Path.home())

    def update_config_file(self) -> None:
        """
        Update the content of the config file
        :return:
        """
        self.config = {"design_file": self.design_filename, "out_dir": self.dir_name}

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def select_and_load_file(self) -> None:
        """
        Allow the user to load a file
        :return:
        """
        self.design_filename = fd.askopenfilename(
            title='Open a Design File',
            initialdir=str(self.design_filename),
            filetypes=self.filetypes)

        if self.design_filename is None or self.design_filename == "":
            return

        self.label_design_file.config(text=self.design_filename)
        with open(self.design_filename, 'r') as f:
            self.text.insert(1.0, f.read())
        self.swimlaneEditorModel = SwimlaneEditorModel(self.text.get('1.0', END))

    def generate_svg_file(self, update_conf_file_after_gen=True) -> None:
        """
        Use the content of the editor to convert the content of the editor into an SVG file
        :param update_conf_file_after_gen:
        :return:
        """
        logger.info(f"Design filename is {self.design_filename}, result will be saved in {self.dir_name}")

        input_file_dir, input_file_name = os.path.split(self.design_filename)
        self.output_file_name = f"{self.dir_name}{input_file_name}.svg"

        override = True
        if Path(self.output_file_name).exists():
            override = askyesno(title='Confirmation',
                                message=f'The file:\n{self.output_file_name}\nalready exists, overwrite it?')

        generate_design = True
        if override:
            if Path(self.output_file_name).exists():
                Path(self.output_file_name).unlink(True)
        else:
            showinfo("Feedback", "Ok, Nothing was generated")
            generate_design = False

        if generate_design:
            # Check if image width is valid
            width_as_string = self.output_image_width_entry.get()
            try:
                width_as_int = int(width_as_string)
            except ValueError:
                messagebox.showerror(title="Width Error", message="Image width should be an integer")
                return

            if 200 < width_as_int < 2500:
                pass
            else:
                messagebox.showerror(title="Width Error", message="Image width should be an integer between 200 and "
                                                                  "2,500")
                return

            parser = SwimlaneParser()
            diagram = parser.load_file(self.design_filename)
            generator = SVGRenderer(diagram, width_as_int, template=template)  # TODO add template as a parameter
            with open(self.output_file_name, 'w') as f:
                f.write(generator.get_svg_string())
                if update_conf_file_after_gen:
                    self.update_config_file()

    def draw_window(self, template: Template) -> None:
        """
        Draw the window
        :return:
        """

        # initialize tkinter
        self.root = Tk()

        # set window props
        self.root.wm_title("Swimlanes Diagram")
        self.root.resizable(True, True)
        self.root.geometry("800x500")

        paned_window = PanedWindow(self.root, orient=HORIZONTAL, showhandle=True)
        paned_window.pack(fill=BOTH, expand=1)

        # Text area - User Input
        editor_frame = Frame()
        editor_frame.pack(fill=BOTH, expand=True)
        paned_window.add(editor_frame)

        # Text area - Help Window
        editor_help_frame = Frame(paned_window)
        editor_help_frame.pack(fill=BOTH, expand=True)
        paned_window.add(editor_help_frame)

        # Output Image Width Label +  Text
        output_image_size_frame = Frame(editor_frame)
        output_image_size_frame.pack(fill=X)

        output_image_width_label = Label(output_image_size_frame, text="Image Width:", width=15, anchor='w')
        output_image_width_label.pack(side=LEFT, padx=5, pady=5)

        self.output_image_width_entry = Entry(output_image_size_frame)
        self.output_image_width_entry.pack(fill=X, padx=5, expand=True)
        self.output_image_width_entry.insert(END, "800")  # Default entry

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
        self.text = Text(editor_frame, wrap=NONE, undo=True, xscrollcommand=x_scrollbar.set,
                         yscrollcommand=y_scrollbar.set, borderwidth=3)
        self.text.pack(expand=True, fill='both')

        # Help Widget
        text_help = Text(editor_help_frame, wrap=NONE, undo=True, xscrollcommand=x_scrollbar.set,
                         yscrollcommand=y_scrollbar.set,
                         borderwidth=3)

        # Load the example file
        example_file_name = f"{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}example_flow.txt"
        if Path(example_file_name).exists():
            with open(example_file_name, 'r') as f:
                text_help.insert(1.0, f.read())
                if self.debug:
                    # It's faster to debug the app when the text area is already filled with an example
                    self.text.insert(1.0, text_help.get(1.0, END))

        text_help.pack(expand=True, fill='both')
        text_help.config(state=DISABLED)

        # Configure the scrollbars
        x_scrollbar.config(command=self.text.xview)
        y_scrollbar.config(command=self.text.yview)

        x_scrollbar_help.config(command=text_help.xview)
        y_scrollbar_help.config(command=text_help.yview)

        button_frame = Frame(self.root)
        button_frame.pack(fill=X)

        generate_svg_button = Button(button_frame, text="Generate and View SVG", command=self.generate_and_view)
        generate_svg_button.pack(side=RIGHT, padx=5, pady=5)

        self.label_design_file = Label(button_frame)
        self.label_design_file.pack(side=LEFT, padx=5, pady=5)

        # Menu
        menu_bar = Menu(self.root)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=lambda: self.text.delete(1.0, END))
        file_menu.add_command(label="Open", command=self.select_and_load_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save as...", command=self.save_file_as)
        file_menu.add_command(label="Close", command=self.on_closing)
        menu_bar.add_cascade(label="File", menu=file_menu)

        self.create_settings_dir_if_needed()
        self.text.focus_set()

        # show window
        self.root.config(menu=menu_bar)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_template_file_name = sys.argv[1]
        logger.info(f"Using template {json_template_file_name}")
    else:
        json_template_file_name = (f"{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}"
                                   f"../templates/default-template.json")
        logger.info("Using default template."
                    "Start the program with a template file name if you want to use a custom template")
    template = FileTemplate(json_template_file_name)
    MainUI().draw_window(template)
