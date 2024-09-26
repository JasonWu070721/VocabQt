import sys
import os
import yaml
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QPushButton,
    QWidget,
    QLineEdit,
    QHBoxLayout,
    QTabWidget,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QProgressBar,
)


from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor
from controller.word import (
    Word,
    add_word,
    get_random_words,
    add_word,
    update_word,
    delete_word,
    increase_familiarity,
    get_all_words,
    get_input_file_words,
)


from controller.input_file import (
    get_all_input_file,
    add_input_file,
    get_all_input_file,
)

import utils.config as config
from retrieve_dictionary import (
    get_dictionary_response,
    get_tradionnal_chinese,
    get_mp3_url_html,
    save_mp3,
    check_mp3_exists,
)


class FileProcessingThread(QThread):
    progress_changed = pyqtSignal(int)  # 自定義信號，用於更新進度條

    def __init__(self, file_path, input_file_id):
        super().__init__()
        self.file_path = file_path
        self.input_file_id = input_file_id

    def run(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                total_lines = len(lines)
                mp3_url = None
                cht = None

                for index, line in enumerate(lines):
                    file_name_split = line.split(",")
                    if len(file_name_split) >= 2:

                        word = file_name_split[0].strip()

                        response = get_dictionary_response(word)

                        if response != None:
                            cht = get_tradionnal_chinese(response)
                            print(str(word) + " ," + str(cht))

                            if not check_mp3_exists(word):
                                mp3_url = get_mp3_url_html(response)

                                if mp3_url is None:
                                    print("No MP3 URL found.")
                                else:
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


class WordTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.random_word_count = 10
        self.auto_refill = True
        self.input_file_index = 0

        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("Word Table")
        self.setGeometry(100, 100, 1024, 640)

        self.word_db = Word()

        # Initialize media player and timer
        self.player = QMediaPlayer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_next_word)
        self.current_word_index = 0
        self.is_looping = False

        # Setup TabWidget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab 1: Word List
        self.word_list_tab = QWidget()
        self.word_list_layout = QVBoxLayout()
        self.word_list_tab.setLayout(self.word_list_layout)

        self.input_file_combo = QComboBox(self)

        self.input_file_combo.currentIndexChanged.connect(self.input_file_changed)

        upload_button = QPushButton("Upload File", self)
        upload_button.clicked.connect(self.upload_file)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.input_file_combo)
        combo_layout.addWidget(upload_button)
        self.word_list_layout.addLayout(combo_layout)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 50, 300, 30)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(
            6
        )  # Display six columns, including ID, play button, and remove button
        self.table_widget.setHorizontalHeaderLabels(
            ["ID", "Word", "CHT", "MP3 URL", "Play", "Remove"]
        )
        self.word_list_layout.addWidget(self.progress_bar)
        self.word_list_layout.addWidget(self.table_widget)

        # Set the column widths
        self.table_widget.setColumnWidth(1, 150)
        self.table_widget.setColumnWidth(2, 500)

        # Hide the ID column
        self.table_widget.setColumnHidden(0, True)

        # Hide the MP3 URL column
        self.table_widget.setColumnHidden(3, True)

        self.table_widget.cellClicked.connect(self.on_table_row_clicked)

        # Input fields and buttons for word list tab
        self.word_input = QLineEdit(self)
        self.cht_input = QLineEdit(self)
        self.mp3_url_input = QLineEdit(self)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.word_input)
        input_layout.addWidget(self.cht_input)
        input_layout.addWidget(self.mp3_url_input)

        self.word_list_layout.addLayout(input_layout)

        add_button = QPushButton("Add", self)
        add_button.clicked.connect(self.add_entry)
        update_button = QPushButton("Update", self)
        update_button.clicked.connect(self.update_entry)
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.delete_entry)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)

        self.word_list_layout.addLayout(button_layout)

        # Tab 2: Random Words
        self.random_words_tab = QWidget()
        self.random_words_layout = QVBoxLayout()
        self.random_words_tab.setLayout(self.random_words_layout)

        self.word_count_combo = QComboBox(self)
        self.word_count_combo.addItems(["10", "20", "30", "50"])
        self.word_count_combo.currentIndexChanged.connect(self.word_count_changed)
        self.random_words_layout.addWidget(self.word_count_combo)

        self.auto_refill_checkbox = QCheckBox("Auto Refill", self)
        self.auto_refill_checkbox.stateChanged.connect(self.auto_refill_toggled)
        self.random_words_layout.addWidget(self.auto_refill_checkbox)

        self.random_table_widget = QTableWidget()
        self.random_table_widget.setColumnCount(
            6
        )  # Display six columns, including ID, play button, and remove button
        self.random_table_widget.setHorizontalHeaderLabels(
            ["ID", "Word", "CHT", "MP3 URL", "Play", "Remove"]
        )
        self.random_words_layout.addWidget(self.random_table_widget)

        # Set the column widths
        self.random_table_widget.setColumnWidth(1, 150)
        self.random_table_widget.setColumnWidth(2, 500)

        # Hide the ID column
        self.random_table_widget.setColumnHidden(0, True)

        # Hide the MP3 URL column
        self.random_table_widget.setColumnHidden(3, True)

        self.random_table_widget.cellClicked.connect(self.on_random_table_row_clicked)

        load_random_button = QPushButton("Load Random Words", self)
        load_random_button.clicked.connect(self.load_random_words)
        self.random_words_layout.addWidget(load_random_button)

        # Add buttons for looping playback
        self.start_loop_button = QPushButton("Start Loop Playback", self)
        self.start_loop_button.clicked.connect(self.start_loop_playback)
        self.stop_loop_button = QPushButton("Stop Loop Playback", self)
        self.stop_loop_button.clicked.connect(self.stop_loop_playback)

        # Add buttons for removing and refilling rows
        refill_button = QPushButton("Refill to 10 Words", self)
        refill_button.clicked.connect(self.refill_random_words)
        self.random_words_layout.addWidget(refill_button)

        self.random_words_layout.addWidget(self.start_loop_button)
        self.random_words_layout.addWidget(self.stop_loop_button)

        # Add tabs to TabWidget
        self.tab_widget.addTab(self.word_list_tab, "Word List")
        self.tab_widget.addTab(self.random_words_tab, "Random Words")

        self.load_input_file_combo()
        self.load_data()
        self.load_random_words()

    def load_input_file_combo(self):
        all_data = get_all_input_file()

        for i in range(len(all_data)):
            self.input_file_combo.addItem(all_data[i][1], int(all_data[i][0]))

    def on_table_row_clicked(self, row, _):

        word = self.table_widget.item(row, 1).text()
        if word:
            self.play_sound(word)

    def on_random_table_row_clicked(self, row, _):

        word = self.random_table_widget.item(row, 1).text()
        if word:
            self.play_sound(word)

    def load_config(self):
        if not os.path.exists("config"):
            return None

        with open(config.config_file, "r") as file:
            configuration = yaml.safe_load(file)
            if "setting" in configuration:
                if "random_word_count" in configuration["setting"]:
                    self.word_count_combo.setCurrentText(
                        str(configuration["setting"]["random_word_count"])
                    )

                if "auto_refill" in configuration["setting"]:
                    self.auto_refill_checkbox.setChecked(
                        configuration["setting"]["auto_refill"]
                    )

    def word_count_changed(self):
        self.random_word_count = int(self.word_count_combo.currentText())
        self.save_config()
        # Handle event for changing word count, e.g., reload table with selected count
        self.load_random_words()

    def input_file_changed(self):
        self.input_file_index = self.input_file_combo.currentData()
        self.load_data(self.input_file_index)

    def auto_refill_toggled(self, state):
        if state == Qt.Checked:
            # Enable auto-refill functionality
            self.auto_refill = True
        else:
            # Disable auto-refill functionality
            self.auto_refill = False
        self.save_config()

    def save_config(self):

        config_data = {
            "app": {"name": "VocabQt", "version": 1.0, "debug": True},
            "setting": {
                "auto_refill": self.auto_refill,
                "random_word_count": self.random_word_count,
            },
        }

        with open(config.config_file, "w") as file:
            yaml.dump(config_data, file, default_flow_style=False)

    def load_data(self, input_file_index=1):

        if input_file_index == 1:
            records = get_all_words()
        else:
            records = get_input_file_words(input_file_index)

        self.table_widget.setRowCount(len(records))
        for i, (id, word, cht, mp3_url) in enumerate(records):

            id_item = QTableWidgetItem(str(id))
            word_item = QTableWidgetItem(word)
            cht_item = QTableWidgetItem(cht)
            mp3_url_item = QTableWidgetItem(mp3_url)

            id_item.setToolTip(f"{id}")
            word_item.setToolTip(f"{word}")
            cht_item.setToolTip(f"{cht}")
            mp3_url_item.setToolTip(f"{mp3_url}")

            self.table_widget.setItem(i, 0, id_item)
            self.table_widget.setItem(i, 1, word_item)
            self.table_widget.setItem(i, 2, cht_item)
            self.table_widget.setItem(i, 3, mp3_url_item)
            play_button = QPushButton("Play")
            play_button.clicked.connect(lambda _, w=word: self.play_sound(w))
            self.table_widget.setCellWidget(i, 4, play_button)
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, _id=id: self.remove_row(_id))
            self.table_widget.setCellWidget(i, 5, remove_button)

    def add_entry(self):
        word = self.word_input.text()
        cht = self.cht_input.text()
        mp3_url = self.mp3_url_input.text()
        input_file_id = 0

        add_word(word, cht, mp3_url, input_file_id)

        self.load_data()

    def update_entry(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            return

        id = int(self.table_widget.item(current_row, 0).text())
        word = self.word_input.text()
        cht = self.cht_input.text()
        mp3_url = self.mp3_url_input.text()

        update_word(id, word, cht, mp3_url)

        self.load_data()

    def delete_entry(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            return

        id = int(self.table_widget.item(current_row, 0).text())
        delete_word(id)

        self.load_data()

    def load_random_words(self):

        records = get_random_words(self.input_file_index, self.random_word_count)

        self.random_table_widget.setRowCount(len(records))
        self.random_words = []

        for i, (id, word, cht, mp3_url, _) in enumerate(records):

            id_item = QTableWidgetItem(str(id))
            word_item = QTableWidgetItem(word)
            cht_item = QTableWidgetItem(cht)
            mp3_url_item = QTableWidgetItem(mp3_url)

            id_item.setToolTip(f"{id}")
            word_item.setToolTip(f"{word}")
            cht_item.setToolTip(f"{cht}")
            mp3_url_item.setToolTip(f"{mp3_url}")

            self.random_table_widget.setItem(i, 0, id_item)
            self.random_table_widget.setItem(i, 1, word_item)
            self.random_table_widget.setItem(i, 2, cht_item)
            self.random_table_widget.setItem(i, 3, mp3_url_item)

            play_button = QPushButton("Play")
            play_button.clicked.connect(lambda _, w=word: self.play_sound(w))
            self.random_table_widget.setCellWidget(i, 4, play_button)
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, _id=id: self.remove_random_row(_id))
            self.random_table_widget.setCellWidget(i, 5, remove_button)
            self.random_words.append(word)

    def refill_random_words(self):
        # If the number of words in the table is less than 10, then add random words to make up the difference
        current_row_count = self.random_table_widget.rowCount()
        if current_row_count < self.random_word_count:

            records = get_random_words(
                self.input_file_index, self.random_word_count - current_row_count
            )

            for id, word, cht, mp3_url, _ in records:
                self.random_words.append(word)

                row_position = self.random_table_widget.rowCount()
                self.random_table_widget.insertRow(row_position)
                self.random_table_widget.setItem(
                    row_position, 0, QTableWidgetItem(str(id))
                )
                self.random_table_widget.setItem(
                    row_position, 1, QTableWidgetItem(word)
                )
                self.random_table_widget.setItem(row_position, 2, QTableWidgetItem(cht))
                self.random_table_widget.setItem(
                    row_position, 3, QTableWidgetItem(mp3_url)
                )
                play_button = QPushButton("Play")
                play_button.clicked.connect(lambda _, w=word: self.play_sound(w))
                self.random_table_widget.setCellWidget(row_position, 4, play_button)
                remove_button = QPushButton("Remove")
                remove_button.clicked.connect(
                    lambda _, _id=id: self.remove_random_row(_id)
                )
                self.random_table_widget.setCellWidget(row_position, 5, remove_button)

    def remove_row(self, id):

        delete_word(id)

        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            if item is not None and int(item.text()) == id:
                self.table_widget.removeRow(row)
                break

    def remove_random_row(self, id):
        for row in range(self.random_table_widget.rowCount()):
            random_id = self.random_table_widget.item(row, 0)

            if random_id is not None and int(random_id.text()) == id:
                select_word = self.random_table_widget.item(row, 1)
                self.random_words.remove(select_word.text())

                increase_familiarity(int(id))
                # Remove rows from the random word table
                self.random_table_widget.removeRow(row)
                break

        if self.auto_refill:
            self.refill_random_words()

    def play_sound(self, word):
        mp3_path = f"audio/{word}.mp3"
        if os.path.exists(mp3_path):
            url = QUrl.fromLocalFile(mp3_path)
            content = QMediaContent(url)
            self.player.setMedia(content)
            self.player.play()
        else:
            print(f"File {mp3_path} does not exist.")

    def start_loop_playback(self):
        self.is_looping = True
        self.current_word_index = 0
        self.timer.start(2000)  # Play one word every 2 seconds

    def stop_loop_playback(self):

        for i in range(self.random_table_widget.rowCount()):
            for j in range(self.random_table_widget.columnCount()):
                item = self.random_table_widget.item(i, j)
                if item is not None:
                    item.setBackground(self.palette().base())

        self.is_looping = False
        self.timer.stop()

    def play_next_word(self):
        if self.is_looping and self.current_word_index < len(self.random_words):
            self.play_sound(self.random_words[self.current_word_index])

            # First, reset the colors of all rows
            for i in range(self.random_table_widget.rowCount()):
                for j in range(self.random_table_widget.columnCount()):
                    item = self.random_table_widget.item(i, j)
                    if item is not None:
                        item.setBackground(self.palette().base())

            # Set the currently playing row to light blue
            for j in range(self.random_table_widget.columnCount()):
                item = self.random_table_widget.item(self.current_word_index, j)
                if item is not None:
                    item.setBackground(QColor(173, 216, 230))

            self.current_word_index += 1
            if self.current_word_index >= len(self.random_words):
                self.current_word_index = 0  # Loop playback

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def upload_file(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload File", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            file_name = os.path.basename(file_path)

            input_files = get_all_input_file()

            for input_file in input_files:
                if len(input_file) >= 2:

                    if input_file[1] == file_name:
                        print("File already exists.")
                        return

            input_file = add_input_file(file_name)

            self.thread = FileProcessingThread(file_path, input_file.id)
            self.thread.progress_changed.connect(self.update_progress)
            self.thread.start()


if __name__ == "__main__":

    config.init_config()

    app = QApplication(sys.argv)
    window = WordTableApp()
    window.show()
    sys.exit(app.exec_())
