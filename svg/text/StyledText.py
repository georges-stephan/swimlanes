class StyledText:

    def __init__(self, text: str, styles: [str]):
        self.text = text
        self.styles = []

        for style in styles:
            # FIXME allow writing multiple times the same entry
            match style.lower():
                case "bold":
                    self.styles.append(style.lower())
                case "italic":
                    self.styles.append(style.lower())
                case "code":
                    self.styles.append(style.lower())
                case "strike-through":
                    self.styles.append(style.lower())
                case "normal":
                    self.styles.append(style.lower())
                case _:
                    raise Exception(f"Un-supported style {style}.")

    def __str__(self):
        return f"{self.styles} applied to {self.text}"

    def __repr__(self):
        return f"{self.styles} applied to {self.text}"
