import hashlib


class SwimlaneEditorModel:

    def __init__(self, editor_content: str):
        self.editor_content = editor_content

    def is_needs_saving(self, current_editor_content: str, encoding='utf-8'):
        loaded_text_checksum = hashlib.md5(self.editor_content.encode(encoding)).hexdigest()
        current_text_checksum = hashlib.md5(current_editor_content.encode(encoding)).hexdigest()

        if loaded_text_checksum == current_text_checksum:
            return False

        return True
