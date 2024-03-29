from PIL import ImageFont

# from diagram.templates.DefaultTemplate import DefaultTemplate

import logging

logger = logging.getLogger(__name__)


def get_text_height(text: str, font_file_name: str, font_size: int, box_width: int):
    """
    A function to return the estimated height of  a text
    :param text: the text to be rendered
    :param font_file_name: the filename of the font
    :param font_size: the size of the font
    :param box_width: the width of the box to contain the text
    :param template: the template to use
    :return: the height of the text given the text, box width, font name and size
    """
    lines = split_text(text, font_file_name, box_width, font_size)
    font = ImageFont.truetype(f'{font_file_name}.ttf', font_size)

    logger.debug(f'Text will split over {len(lines)} lines. Text height is {font.getbbox(text)[3]},'
                 f' text width is {font.getbbox(text)[2]}. Box width={box_width}')

    return font.getbbox(text)[3] * len(lines)


def split_text(text: str, font_file_name: str, box_width: int, font_size: int):
    """
    Splits a given line of text into multiple lines
    :param text: The text to split
    :param font_file_name: The file name of the font (Ex. Arial.ttf)
    :param box_width: the with of the area where the text should fit
    :param font_size: The size of the font in points
    :return: An array of tuples each storing: A substring of the given text representing a line, the text width and the
     text height
    """
    lines = []
    font = ImageFont.truetype(f'{font_file_name}.ttf', font_size)
    size = font.getbbox(text)
    rendered_font_width = size[2]
    rendered_font_height = size[3]

    # Best case scenario, the rendered text fits
    if box_width > rendered_font_width:
        lines.append((text, rendered_font_width, rendered_font_height))
        return lines

    space_width = font.getbbox(' ')[2]

    words = text.split()  # Split a line of text into words
    remaining_words_count = len(words)

    current_string = ""
    current_string_font_width = 0
    current_string_font_height = 0
    while remaining_words_count > 0:
        for word in words:
            size_current_string = font.getbbox(current_string)
            current_string_font_width = size_current_string[2]
            current_string_font_height = size_current_string[3]

            size_new_word = font.getbbox(word.strip())
            new_word_font_width = size_new_word[2]

            if (new_word_font_width + space_width + current_string_font_width) < box_width:
                # The word can be added to the current line
                if len(current_string) < 1:
                    current_string = word.strip()
                else:
                    current_string = current_string + ' ' + word.strip()
            else:
                # Let's have new line
                lines.append((current_string, current_string_font_width, current_string_font_height))
                current_string = word.strip() + ' '

            remaining_words_count -= 1
    if len(current_string) > 0:
        lines.append((current_string, current_string_font_width, current_string_font_height))
    return lines
