from svg.text.StyledText import StyledText


class ParseStyles:

    def __init__(self, text_to_parse: str):
        self.text_to_parse = text_to_parse
        self.styled_texts = [StyledText]

    def parse(self):

        state = 1
        text_buffer: str
        style = "normal"
        c: str

        text_buffer = ""
        for c in self.text_to_parse:
            match state:
                case 1:
                    match c:
                        case '*':
                            state = 5
                        case '~':
                            state = 2
                        case '`':
                            case = 0
                        case _:
                            case = 1
                            text_buffer += c
                case 2:
                    match c:
                        case '~':
                            state = 3
                        case _:
                            state = 1
                            text_buffer += c
                case 3:
                    match c:
                        case '~':
                            state = 4
                        case _:
                            state = 3
                            text_buffer += c
                case 4:
                    match c:
                        case '~':
                            st = StyledText(text_buffer, ["strike-through"])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                        case _:
                            state = 3
                            text_buffer += c
                case 5:
                    match c:
                        case '*':
                            state = 7
                        case _:
                            state = 6
                            text_buffer += c
                case 6:
                    match c:
                        case '*':
                            st = StyledText(text_buffer, ["italic"])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                        case _:
                            state = 6
                            text_buffer += c
                case 7:
                    match c:
                        case '*':
                            state = 8
                        case _:
                            text_buffer += c
                case 8:
                    match c:
                        case '*':
                            st = StyledText(text_buffer, ["bold"])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                        case _:
                            state = 7
                            text_buffer += c
                case 9:
                    match c:
                        case '`':
                            st = StyledText(text_buffer, ["code"])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                        case _:
                            state = 9
                            text_buffer += c
                case _:
                    raise Exception(f"Unknown state {state}.")

    def get_styled_words_count(self):
        return len(self.styled_texts)

    def __str__(self):
        return f"Text is:{self.text_to_parse}, styles are {self.styled_texts}"

    def __repr__(self):
        return f"Text is:{self.text_to_parse}, styles are {self.styled_texts}"