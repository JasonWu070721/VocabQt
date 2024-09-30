from PyQt5.QtCore import QThread, pyqtSignal

from retrieve_dictionary import (
    get_dictionary_response,
    get_tradionnal_chinese,
    get_mp3_url_html,
    save_mp3,
    check_mp3_exists,
)

from controller.word import (
    add_word,
    add_word,
    check_word_exists,
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

                        if check_word_exists(word):
                            print(str(word) + " already exists.")

                            if not check_mp3_exists(word):

                                response = get_dictionary_response(word)
                                mp3_url = get_mp3_url_html(response)
                                if mp3_url is None:
                                    print("No MP3 URL found.")

                                if mp3_url != None and word != None:
                                    save_mp3(mp3_url, word)

                            progress = int((index + 1) / total_lines * 100)
                            self.progress_changed.emit(progress)

                            continue

                        if response == None:
                            response = get_dictionary_response(word)

                        if response != None:
                            cht = get_tradionnal_chinese(response)
                            print(str(word) + " ," + str(cht))

                            if mp3_url == None:
                                mp3_url = get_mp3_url_html(response)
                                if mp3_url is None:
                                    print("No MP3 URL found.")

                            if not check_mp3_exists(word) and mp3_url != None:
                                save_mp3(mp3_url, word)

                        else:
                            print("No response.")

                        if mp3_url != None and cht != None:
                            print(word, cht, mp3_url, int(self.input_file_id))
                            add_word(word, cht, mp3_url, int(self.input_file_id))

                    progress = int((index + 1) / total_lines * 100)
                    self.progress_changed.emit(progress)

        except Exception as e:
            print(f"Failed to read file: {e}")
