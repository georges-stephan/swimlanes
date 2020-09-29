import unittest

from parsing import SwimlaneParser
import svg
from svg.SVGGenerator import SVGRenderer


class TestParser(unittest.TestCase):

    def test_parser(self):
        print(dir(svg))
        diagram = SwimlaneParser.load_file("C:\\Users\\georges\\PycharmProjects\\SwimlanesDiagram\\in\\simple_swimlane.txt")
        print(f"Diagram is {str(diagram)}")

        generator = SVGRenderer(diagram, 800, 682)
        with open("../out/simple.svg", 'w') as f:
            f.write(generator.get_svg_string())
        print("Done")