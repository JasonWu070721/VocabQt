import sys
import sqlite3
import random
import os
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
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QColor


class WordTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Table")
        self.setGeometry(100, 100, 1024, 640)

        self.conn = sqlite3.connect("db/words.db")
        self.create_table()

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

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(
            6
        )  # Display six columns, including ID, play button, and remove button
        self.table_widget.setHorizontalHeaderLabels(
            ["ID", "Word", "CHT", "MP3 URL", "Play", "Remove"]
        )
        self.word_list_layout.addWidget(self.table_widget)

        # Hide the ID column
        self.table_widget.setColumnHidden(0, True)

        self.load_data()

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

        self.random_table_widget = QTableWidget()
        self.random_table_widget.setColumnCount(
            6
        )  # Display six columns, including ID, play button, and remove button
        self.random_table_widget.setHorizontalHeaderLabels(
            ["ID", "Word", "CHT", "MP3 URL", "Play", "Remove"]
        )
        self.random_words_layout.addWidget(self.random_table_widget)

        # Hide the ID column
        self.random_table_widget.setColumnHidden(0, True)

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

        self.load_random_words()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS words
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          word TEXT,
                          cht TEXT,
                          mp3_url TEXT)"""
        )
        self.conn.commit()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, word, cht, mp3_url FROM words")
        records = cursor.fetchall()

        self.table_widget.setRowCount(len(records))
        for i, (id, word, cht, mp3_url) in enumerate(records):
            self.table_widget.setItem(i, 0, QTableWidgetItem(str(id)))
            self.table_widget.setItem(i, 1, QTableWidgetItem(word))
            self.table_widget.setItem(i, 2, QTableWidgetItem(cht))
            self.table_widget.setItem(i, 3, QTableWidgetItem(mp3_url))
            play_button = QPushButton("Play")
            play_button.clicked.connect(lambda _, w=word: self.play_sound(w))
            self.table_widget.setCellWidget(i, 4, play_button)
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, row=i: self.remove_row(row))
            self.table_widget.setCellWidget(i, 5, remove_button)

    def add_entry(self):
        word = self.word_input.text()
        cht = self.cht_input.text()
        mp3_url = self.mp3_url_input.text()

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO words (word, cht, mp3_url) VALUES (?, ?, ?)",
            (word, cht, mp3_url),
        )
        self.conn.commit()

        self.load_data()

    def update_entry(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            return

        word = self.word_input.text()
        cht = self.cht_input.text()
        mp3_url = self.mp3_url_input.text()

        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE words SET word = ?, cht = ?, mp3_url = ? WHERE id = ?",
            (word, cht, mp3_url, int(self.table_widget.item(current_row, 0).text())),
        )
        self.conn.commit()

        self.load_data()

    def delete_entry(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            return

        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM words WHERE id = ?",
            (int(self.table_widget.item(current_row, 0).text()),),
        )
        self.conn.commit()

        self.load_data()

    def load_random_words(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, word, cht, mp3_url FROM words ORDER BY RANDOM() LIMIT 10"
        )
        records = cursor.fetchall()

        self.random_table_widget.setRowCount(len(records))
        self.random_words = []

        for i, (id, word, cht, mp3_url) in enumerate(records):
            self.random_table_widget.setItem(i, 0, QTableWidgetItem(str(id)))
            self.random_table_widget.setItem(i, 1, QTableWidgetItem(word))
            self.random_table_widget.setItem(i, 2, QTableWidgetItem(cht))
            self.random_table_widget.setItem(i, 3, QTableWidgetItem(mp3_url))
            play_button = QPushButton("Play")
            play_button.clicked.connect(lambda _, w=word: self.play_sound(w))
            self.random_table_widget.setCellWidget(i, 4, play_button)
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda _, row=i: self.remove_random_row(row))
            self.random_table_widget.setCellWidget(i, 5, remove_button)
            self.random_words.append(word)

    def refill_random_words(self):
        # If the number of words in the table is less than 10, then add random words to make up the difference
        current_row_count = self.random_table_widget.rowCount()
        if current_row_count < 10:
            cursor = self.conn.cursor()
            cursor.execute(
                f"SELECT id, word, cht, mp3_url FROM words ORDER BY RANDOM() LIMIT {10 - current_row_count}"
            )
            records = cursor.fetchall()

            for id, word, cht, mp3_url in records:
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
                    lambda _, row=row_position: self.remove_random_row(row)
                )
                self.random_table_widget.setCellWidget(row_position, 5, remove_button)

    def remove_row(self, row):
        # Remove the row and delete it from the database
        id = int(self.table_widget.item(row, 0).text())
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM words WHERE id = ?", (id,))
        self.conn.commit()
        self.table_widget.removeRow(row)

    def remove_random_row(self, row):
        # Remove rows from the random word table
        self.random_table_widget.removeRow(row)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordTableApp()
    window.show()
    sys.exit(app.exec_())
