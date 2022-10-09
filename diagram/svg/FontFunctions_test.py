import unittest

from PIL import ImageFont

from diagram.svg.FontFunctions import split_text


class MyTestCase(unittest.TestCase):

    def test_something(self):
        font = ImageFont.truetype('arial.ttf', 14)
        size = font.getsize("Lorem ipsum dolor sit amet, ")
        print(size)

        print("Test #1")
        print(" Dear how are you today  ".strip())

        print("Test #2")
        text_lines = split_text("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante ex, luctus "
                                "non purus vitae, laoreet congue dolor. ", "arial", 193, 14)
        print(text_lines)
        print(f'Text will be split into {len(text_lines)} lines.')

        print("Test #3")
        text_lines_size = split_text(
            "Adds item specific features such as Author for books, memory for computers, etc.", "arial", 320, 14)
        print(f"The box height will be {text_lines_size}")


if __name__ == '__main__':
    unittest.main()
