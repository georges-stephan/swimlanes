import hashlib

import unicodedata


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


class SwimlaneEditorModel:

    def __init__(self, editor_content: str):
        self.editor_content = remove_control_characters(editor_content)

    def is_needs_saving(self, current_editor_content: str, encoding='utf-8'):
        loaded_text_checksum = hashlib.md5(self.editor_content.encode(encoding)).hexdigest()
        current_text_checksum = hashlib.md5(
            remove_control_characters(current_editor_content).encode(encoding)).hexdigest()

        if loaded_text_checksum == current_text_checksum:
            return False

        return True

    @classmethod
    def remove_control_characters(cls, s):
        return remove_control_characters(s)

