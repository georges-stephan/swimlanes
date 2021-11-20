import os
import sys

from parsing import SwimlaneParser
import svg
from svg.SVGGenerator import SVGRenderer
from os.path import exists
from pathlib import Path


def run_cli():
    input_file, output_file = check_paths()
    parse_in_file(input_file, output_file)


def check_paths():
    input_file_full_path_name = input("Enter the full path and name of source file:")
    file_exists = exists(input_file_full_path_name)

    if not file_exists:
        print(f"File {file_exists} could not be found, exiting.")
        sys.exit()

    input_file_dir, input_file_name = os.path.split(input_file_full_path_name)

    output_dir_name = input("Enter output directory name:")

    if output_dir_name == "":
        output_dir_name = f"{input_file_dir}\\"

    output_dir = Path(output_dir_name)

    if not output_dir.is_dir():
        print(f"Directory {output_dir_name} could not be found, exiting.")
        sys.exit()

    output_file_name = f"{output_dir_name}{input_file_name}.svg"
    output_file = Path(output_file_name)

    if output_file.exists():
        overwrite_decision = input(f"Output file {output_file} already exists, overwrite? Y=Yes.")
        if overwrite_decision != 'Y':
            sys.exit()
        else:
            output_file.unlink(True)

    return input_file_full_path_name, output_file_name


def parse_in_file(input_file: str, output_file: str):
    print(dir(svg))
    diagram = SwimlaneParser.load_file(input_file)

    generator = SVGRenderer(diagram, 2, 2)
    with open(output_file, 'w') as f:
        f.write(generator.get_svg_string())
    print("Done")


if __name__ == '__main__':
    run_cli()
