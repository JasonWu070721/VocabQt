import requests
from pydub import AudioSegment
from pydub.playback import play
from bs4 import BeautifulSoup
import os
import random
import sqlite3
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
}


def get_men_mp3_url(word):
    mp3_url = "https://s.yimg.com/bg/dict/dreye/live/m/" + word + ".mp3"
    return mp3_url


def get_dictionary_response(word):

    try:
        response = requests.get(
            "https://tw.dictionary.search.yahoo.com/search?p=" + word,
            headers=headers,
            verify=None,
            timeout=5,
        )
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        return None

    return response


def get_tradionnal_chinese(response):

    soup = BeautifulSoup(response.text, "html.parser")

    titles = soup.find_all("div", class_="fz-16 fl-l dictionaryExplanation")
    for title in titles:
        return title.text


def get_mp3_url_html(response):

    content = response.content.decode()

    mp3_links = re.findall(r"https?:\\/\\/\S+\.mp3", content)

    if len(mp3_links) > 0:
        mp3_url = mp3_links[0].replace("\\", "")

        return mp3_url

    return None


def play_mp3(word):

    audio = AudioSegment.from_file("audio/" + word + ".mp3", format="mp3")

    play(audio)


def save_mp3(mp3_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }

    try:
        response = requests.get(mp3_url, headers=headers, verify=None)
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        return False

    if response.status_code != 200:
        print("Failed to download the MP3 file.")
        return

    with open("audio/" + word + ".mp3", "wb") as file:
        file.write(response.content)

    return True


def check_mp3_exists(word):

    if os.path.exists("audio/" + word + ".mp3"):
        return True
    else:
        return False


def load_quizlet(filename):
    all_lines = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            line_array = line.split(",")

            all_lines.append(line_array)

    return all_lines


if __name__ == "__main__":

    if os.path.isdir("./db") == False:
        os.mkdir("./db")

    if os.path.isdir("./audio") == False:
        os.mkdir("./audio")

    conn = sqlite3.connect("db/words.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY,
        word TEXT,
        cht TEXT,
        mp3_url TEXT
    )
    """
    )

    all_words = load_quizlet("quizlet_level4.txt")

    words_len = len(all_words)

    random_index = random.randint(0, len(all_words) - 1)
    # random_index = 0

    print(words_len)
    print(random_index)

    for word_index, all_word in enumerate(all_words):

        word_index = (word_index + random_index) % words_len
        word = all_words[word_index][0]

        cursor.execute("SELECT word, cht, mp3_url FROM words WHERE word = ?", (word,))

        result = cursor.fetchone()

        if result:
            word, cht, mp3_url = result
            print(f"The word '{word}' exists in the table.")
            print(f"Data: word={word}, cht={cht}, mp3_url={mp3_url}")

        else:
            response = get_dictionary_response(word)
            cht = get_tradionnal_chinese(response)
            print(str(word) + " ," + str(cht))

            if response == None:
                print("No response.")
                continue

            mp3_url = get_mp3_url_html(response)

            if mp3_url is None:
                print("No MP3 URL found.")
                continue

            if not check_mp3_exists(word):
                save_mp3(mp3_url)

            cursor.execute(
                """
                    INSERT INTO words (word, cht, mp3_url)
                    VALUES
                        (?, ?, ?)
                """,
                (word, cht, mp3_url),
            )

            conn.commit()

            if check_mp3_exists(word):
                play_mp3(word)
