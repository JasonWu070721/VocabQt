from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import datetime

Base = declarative_base()


class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    cht = Column(String, nullable=False)
    mp3_url = Column(String, nullable=False)
    input_file_id = Column(Integer, nullable=False)
    familiarity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False,
    )


engine = create_engine("sqlite:///db/words.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_word(word, cht, mp3_url, input_file_id):
    new_word = Word(word=word, cht=cht, mp3_url=mp3_url, input_file_id=input_file_id)
    session.add(new_word)
    session.commit()
    return new_word


def increase_familiarity(word_id):
    if type(word_id) is not int or word_id < 0:
        return False

    word = session.query(Word).filter_by(id=word_id).first()

    if word:
        word.familiarity = (word.familiarity or 0) + 1
        session.commit()

    return True


def update_word(word_id, new_word, new_cht, new_mp3_url, input_file_id, familiarity):
    word_to_update = session.query(Word).filter_by(id=word_id).first()

    if word_to_update:
        word_to_update.word = new_word
        word_to_update.cht = new_cht
        word_to_update.mp3_url = new_mp3_url
        word_to_update.input_file_id = input_file_id
        word_to_update.familiarity = familiarity
        word_to_update.updated_at = datetime.datetime.now()
        session.commit()
        return word_to_update
    return None


def delete_word(word_id):
    word_to_delete = session.query(Word).filter_by(id=word_id).first()
    if word_to_delete:
        session.delete(word_to_delete)
        session.commit()
        return True
    return False


def get_all_words():
    words = session.query(Word).all()
    word_list = [[word.id, word.word, word.cht, word.mp3_url] for word in words]

    return word_list


def get_input_file_words(input_file_id):
    words = session.query(Word).filter_by(input_file_id=input_file_id).all()
    word_list = [[word.id, word.word, word.cht, word.mp3_url] for word in words]

    return word_list


def get_random_words(input_file_id, random_num=10):

    if input_file_id == 1:
        sql_query = text(
            f"""SELECT id, word, cht, mp3_url, familiarity
            FROM words
            ORDER BY RANDOM()
            """
        )
    else:
        sql_query = text(
            f"""SELECT id, word, cht, mp3_url, familiarity
            FROM words
            WHERE input_file_id = {input_file_id}
            ORDER BY RANDOM()
            """
        )

    result = session.execute(sql_query)

    words = result.fetchall()

    # Sort the words by familiarity after fetching
    words_sorted_by_familiarity = sorted(words, key=lambda x: x[4])

    if random_num > len(words_sorted_by_familiarity):
        random_num = len(words_sorted_by_familiarity)

    return words_sorted_by_familiarity[:random_num]
