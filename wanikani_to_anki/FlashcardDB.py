from peewee import BlobField, BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField, TextField
from wanikani_to_anki.db import BaseModel


class Subject(BaseModel):
    """
    Subject Model for anki.
    """
    wk_id = IntegerField(primary_key=True)
    characters = CharField()
    object_type = CharField()
    meaning_mnemonic = TextField()
    meaning_mnemonic_info = TextField()
    reading_mnemonic = TextField()
    reading_mnemonic_info = TextField()
    level = IntegerField()
    lesson_position = IntegerField()
    date_created = DateTimeField()
    date_updated = DateTimeField()
    
class Meaning(BaseModel):
    meaning = CharField()
    accepted_answer = BooleanField()
    primary = BooleanField()
    type = CharField()
    subject = ForeignKeyField(Subject, backref="meaning")

class Component(BaseModel):
    main = ForeignKeyField(Subject)
    sub = ForeignKeyField(Subject, backref="components")

class Reading(BaseModel):
    type = CharField()
    primary = BooleanField()
    reading = CharField()
    answer = BooleanField()
    subject = ForeignKeyField(Subject, backref='readings')

class PartOfSpeech(BaseModel):
    subject= ForeignKeyField(Subject, backref="pos")
    pos = CharField()

class Context(BaseModel):
    en = TextField()
    ja = TextField()
    subject = ForeignKeyField(Subject, backref="contexts")

class Audio(BaseModel):
    file_name = CharField()
    file = BlobField()
    subject= ForeignKeyField(Subject, backref="audio")

class Image(BaseModel):
    file_name = CharField()
    file = BlobField()
    subject= ForeignKeyField(Subject, backref="image")
