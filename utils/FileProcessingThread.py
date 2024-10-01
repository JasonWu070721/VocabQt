from PyQt5.QtCore import QThread, pyqtSignal

from retrieve_dictionary import (
    get_dictionary_response,
    get_translation_chinese,
    get_mp3_url_html,
    save_mp3,
    check_mp3_exists,
)

from controller.word import (
    add_word,
    get_word,
)


class FileProcessingThread(QThread):
    progress_changed = pyqtSignal(int)

    def __init__(self, file_path, input_file_id):
        super().__init__()
        self.file_path = file_path
        self.input_file_id = input_file_id

    def run(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                total_lines = len(lines)

                for index, line in enumerate(lines):
                    mp3_url = None
                    cht = None
                    response = None

                    file_name_split = line.split(",")
                    if len(file_name_split) >= 2:

                        word = file_name_split[0].strip()

                        word_row = get_word(word)

                        if word_row == None:

                            response = get_dictionary_response(word)

                            if response != None:

                                cht = get_translation_chinese(response)
                                mp3_url = get_mp3_url_html(response)

                                if mp3_url != None and cht != None:
                                    add_word(
                                        word, cht, mp3_url, int(self.input_file_id)
                                    )
                            else:
                                print("No response.")

                        if not check_mp3_exists(word):

                            if word_row == None:
                                word_row = get_word(word)

                            if word_row != None:
                                if word_row.word != None and word_row.word != None:
                                    save_mp3(word_row.mp3_url, word_row.word)
                            else:
                                print("No mp3_url found.")

                    progress = int((index + 1) / total_lines * 100)
                    self.progress_changed.emit(progress)

        except Exception as e:
            print(f"Failed to read file: {e}")
