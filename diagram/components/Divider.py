from diagram.components.DiagramItems import DiagramItem
from diagram.components.StyleError import StyleError


def check_style(style: str):
    switcher = {"regular": 1, "dashed": 2, "bold": 3, "thin": 4, "delay": 5}
    i = switcher.get(style.lower(), 0)
    if i > 0:
        return True
    else:
        return False


class Divider(DiagramItem):

    def __init__(self, label: str, style="Regular"):
        self.label = label
        if check_style(style):
            pass
        else:
            raise StyleError(f"Un-supported style {style}. The supported styles are"
                             f" 'Regular', 'Dashed', 'Thin','Bold' and 'Delay'.")

        self.style = style
