import sys

from diagram.parsing import SwimlaneParser
from diagram.svg.SVGGenerator import SVGRenderer


def load_file(instruction_file_full_path: str, image_width, image_height, svg_output_file='out.SVG'):
    diagram = SwimlaneParser.load_file(instruction_file_full_path)

    generator = SVGRenderer(diagram, image_width, image_height)  # TODO which resolution to choose?
    with open(svg_output_file, 'w') as f:
        f.write(generator.get_svg_string())


def print_usage(error_message: str = ""):
    if len(error_message) > 1:
        print(f"Error:{str}")
    print("Usage:\r\npython DrawSwimlaneDiagram instruction_file_path image_width image_height [output_file_path]")
    print("Example:\r\n")
    print("python DrawSwimlaneDiagram diagram.txt 800 682 folder\\out.svg")


if __name__ == "__main__":
    number_of_argument = len(sys.argv)

    if number_of_argument != 3 and number_of_argument != 4:
        print_usage()

    try:
        p_image_width = int(sys.argv[1])
    except ValueError:
        print_usage("Invalid width")
        sys.exit(-1)

    try:
        p_image_height = int(sys.argv[2])
    except ValueError:
        print_usage("Invalid height")
        sys.exit(-1)

    if number_of_argument == 3:
        load_file(sys.argv[0], p_image_width, p_image_height)
        print("Completed. Out file saved in the current run dir as 'out.csv'.")
    elif number_of_argument == 4:
        load_file(sys.argv[0], p_image_width, p_image_height, sys.argv[1])
        print(f"Completed. Out file saved in the current run dir as '{sys.argv[1]}'.")
    else:
        print_usage()
