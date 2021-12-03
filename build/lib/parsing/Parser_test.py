import unittest

from parsing import SwimlaneParser
import svg
from svg.SVGGenerator import SVGRenderer


class TestParser(unittest.TestCase):

    def test_parser(self):
        print(dir(svg))
        diagram = SwimlaneParser.load_file("../examples/swimlanes-search-integration.txt")
        print(f"Diagram is {str(diagram)}")

        generator = SVGRenderer(diagram, 800, 702)
        with open("../out/search_integration.svg", 'w') as f:
            f.write(generator.get_svg_string())
        print("Done")