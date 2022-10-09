from diagram.parsing.ParseError import ParsingUnknownStateError
from diagram.svg.text.StyledText import StyledText


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
        index: int
        index = -1
        for c in self.text_to_parse:
            index += 1
            match state:
                case 1:
                    match c:
                        case '*':
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            style = "italic"
                            state = 5
                        case '~':
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            style = "strike-through"
                            state = 2
                        case '`':
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            style = "code"
                            state = 9
                        case _:
                            state = 1
                            style = "normal"
                            text_buffer += c
                case 2:
                    match c:
                        case '~':
                            state = 4
                            style = "strike-through"
                        case _:
                            style = "normal"
                            state = 1
                            text_buffer += c
                case 3:
                    match c:
                        case '*':
                            # italic
                            style = "italic"
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                            style = "normal"
                        case _:
                            style = "italic"
                            state = 3
                            text_buffer += c
                case 4:
                    match c:
                        case '~':
                            style = "strike-through"
                            state = 6
                        case _:
                            state = 4
                            style = "strike-through"
                            text_buffer += c
                case 5:
                    match c:
                        case '*':
                            style = "bold"
                            state = 7
                        case _:
                            style = "italic"
                            state = 3
                            text_buffer += c
                case 6:
                    match c:
                        case '~':
                            style = "strike-through"
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                            style = "normal"
                        case _:
                            state = 4
                            style = "strike-through"
                            text_buffer += c
                case 7:
                    match c:
                        case '*':
                            style = "bold"
                            state = 8
                        case _:
                            style = "bold"
                            state = 7
                            text_buffer += c
                case 8:
                    match c:
                        case '*':
                            # bold
                            style = "bold"
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            state = 1
                            style = "normal"
                        case _:
                            state = 7
                            style = "bold"
                            text_buffer += c
                case 9:
                    match c:
                        case '`':
                            style = "code"
                            st = StyledText(text_buffer, [style])
                            self.styled_texts.append(st)
                            text_buffer = ""
                            style = "normal"
                            state = 1
                        case _:
                            state = 9
                            style = "code"
                            text_buffer += c
                case _:
                    raise ParsingUnknownStateError(state_number=state)

    def get_styled_words_count(self):
        return len(self.styled_texts)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Text to style is:{self.text_to_parse}.The styles are: {self.styled_texts}"