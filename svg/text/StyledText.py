class StyledText:

    def __init__(self, text: str, styles: [str]):
        self.text = text
        self.styles = {}

        for style in styles:
            match style.lower():
                case "bold":
                    # self.text = text[2: -2]
                    self.styles[style.lower()] = style.lower()
                case "italic":
                    self.styles[style.lower()] = style.lower()
                case "code":
                    self.styles[style.lower()] = style.lower()
                case "strike-through":
                    self.styles[style.lower()] = style.lower()
                case "normal":
                    self.styles[style.lower()] = style.lower()
                case _:
                    raise Exception(f"Un-supported style {style}.")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"The style {self.styles} is applied to \"{self.text}\""
