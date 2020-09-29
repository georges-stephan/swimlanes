import unittest

from PIL import ImageFont

from svg.FontFunctions import split_text


class MyTestCase(unittest.TestCase):

    def test_something(self):

        font = ImageFont.truetype('arial.ttf', 14)
        size = font.getsize("Lorem ipsum dolor sit amet, ")
        print(size)

        print(" Dear how are you today  ".strip())

        text_lines = split_text("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec ante ex, luctus "
                                "non purus vitae, laoreet congue dolor. ", "arial", 193, 50, 14)
        print(text_lines)
        print(f'Text will be split into {len(text_lines)} lines.')


if __name__ == '__main__':
    unittest.main()
