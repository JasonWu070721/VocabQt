from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import datetime

Base = declarative_base()


class InputFile(Base):
    __tablename__ = "input_files"
    id = Column(Integer, primary_key=True)
    file_name = Column(Integer, nullable=False, default=0)
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


def add_input_file(file_name):
    new_file_name = InputFile(file_name=file_name)
    session.add(new_file_name)
    session.commit()
    return new_file_name


def update_input_file(id, file_name):
    update_session = session.query(InputFile).filter_by(id=id).first()

    if update_session:
        update_session.file_name = file_name
        update_session.updated_at = datetime.datetime.now()
        session.commit()
        return update_session
    return None


def delete_input_file(id):
    delete_session = session.query(InputFile).filter_by(id=id).first()
    if delete_session:
        session.delete(delete_session)
        session.commit()
        return True
    return False


def get_all_input_file():
    get_session = session.query(InputFile).all()
    word_list = [[input_file.id, input_file.file_name] for input_file in get_session]

    return word_list
