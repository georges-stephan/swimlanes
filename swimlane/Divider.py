import io
from swimlane.DiagramItems import DiagramItem


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
            raise TypeError(f"Un-supported style {style}."
                            f" Supported styles are 'Regular', 'Dashed', 'Thin','Bold' and 'Delay'.")

        self.style = style
