from copy import Error
from datetime import datetime
from wanikani_api.models import Subject, Meaning, AuxiliaryMeaning, Reading
from typing import List, Optional
from dataclasses import dataclass
import requests
from requests import Response
import urllib.parse
import re
import html
import wanikani_to_anki.FlashcardDB as FDB
from  wanikani_to_anki.db import sqlite_db as db


#Constants
IMAGE_FILE = "image/svg+xml"
AUDIO_FILE = "audio/mpeg"

@dataclass
class Context:
    en: str = ""
    ja: str = ""

@dataclass
class Components:
    characters: str
    names: str
    types: str

@dataclass
class MeaningList:
    white: str
    black: str

@dataclass
class ReadingData: 
    onyomi: str
    kunyomi: str
    nanori: str
    accepted: str
    whitelist: str
    blacklist: str

@dataclass
class Mnemonic:
    meaning_mnemonic: str
    meaning_mnemonic_info: str
    reading_mnemonic:str
    reading_mnemonic_info: str

    def __init__(self, meaning_mem, meaning_mnemonic_info, reading_mnemonic, reading_mnemonic_info):
        self.meaning_mnemonic = meaning_mem
        self.meaning_mnemonic_info = meaning_mnemonic_info,
        self.reading_mnemonic = reading_mnemonic,
        self.reading_mnemonic_info = reading_mnemonic_info
    
    @staticmethod
    def from_api(subject:Subject):
        return Mnemonic(
            meaning_mnemonic = subject._resource["meaning_mnemonic"],
            meaning_mnemonic_info = (subject._resource["meaning_hint"] if subject.resource == "kanji" else None),
            reading_mnemonic = (None if  Card._is_radical(subject) else subject._resource["reading_mnemonic"]),
            reading_mnemonic_info = (subject._resource["reading_hint"] if subject.resource == 'kanji' else None),
        )
@dataclass
class Position:
    level: int
    lesson_position: int



class Card():
    wk_id : int
    characters: str
    object_type: str
    component_ids: Optional[List[int]]
    components: Optional[List[Components]] 
    meanings: List[Meaning]
    aux_meanings: List[AuxiliaryMeaning] 
    readings: Optional[List[Reading]] 
    part_of_speech: Optional[List[str]]
    context: Optional[List[Context]]
    mnemonic: Mnemonic
    audio_url: Optional[List[str]]
    image_url: Optional[List[str]] 
    position: Position
    date_created: datetime.datetime
    date_updated: datetime.datetime

    def __init__(self,
                wk_id: int,
                characters: str,
                object_type: str,
                component_ids: Optional[List[int]],
                components: Optional[List[Components]],
                meanings: List[Meaning],
                aux_meanings: List[AuxiliaryMeaning],
                readings: Optional[List[Reading]],
                part_of_speech: Optional[List[str]],
                context: Optional[List[Context]],
                mnemonic: Mnemonic,
                position: Position,
                audio_url: Optional[List[str]],
                image_url: Optional[List[str]],
                date_created: datetime,
                date_updated: datetime,
                ):
        self.wk_id = wk_id
        self.characters = characters
        self.object_type = object_type
        self.components_id = component_ids
        self.components = components
        self.meanings = meanings
        self.aux_meanings = aux_meanings
        self.readings = readings 
        self.part_of_speech = part_of_speech
        self.context = context
        self.mnemonic = mnemonic
        self.audio_url = audio_url
        self.image_url = image_url #Radicals that do not have a characters
        self.position = position
        self.date_created= date_created
        self.date_updated= date_updated

    # def __init__(self, subject:Subject ):
    #     self.wk_id = subject.id
    #     self.characters = subject.characters
    #     self.object_type = subject.resource
    #     self.components = (None if subject.resource == "radical" else subject.component_subject_ids)
    #     self.meanings = subject.meanings
    #     self.aux_meanings = subject.auxiliary_meanings
    #     self.readings = (None if self._is_radical(subject) else subject.readings) 
    #     self.part_of_speech = self._get_part_of_speech(subject)
    #     self.context = self._get_context(subject)
    #     self.meaning_mnemonic = subject._resource["meaning_mnemonic"]
    #     self.meaning_mnemonic_info = (subject._resource["meaning_hint"] if subject.resource == "kanji" else None)
    #     self.reading_mnemonic = (None if self._is_radical(subject) else subject._resource["reading_mnemonic"])
    #     self.reading_mnemonic_info = (subject._resource["reading_hint"] if subject.resource == 'kanji' else None)
    #     self.audio_url = self._get_audio_url(subject)
    #     self.image_url = self._get_image_url(subject) #Radicals that do not have a characters
    #     self.level = subject.level
    #     self.lesson_position = subject._resource["lesson_position"]
    @staticmethod
    def from_api(subject:Subject):

        mnemonic = Mnemonic(
                            meaning_mnemonic = subject._resource["meaning_mnemonic"],
                            meaning_mnemonic_info = (subject._resource["meaning_hint"] if subject.resource == "kanji" else None),
                            reading_mnemonic = (None if  Card._is_radical(subject) else subject._resource["reading_mnemonic"]),
                            reading_mnemonic_info = (subject._resource["reading_hint"] if subject.resource == 'kanji' else None),
        )
        position = Position(level= subject.level, lesson_position= subject._resource["lesson_position"])
        
        return Card(
            wk_id = subject.id,
            characters = subject.characters,
            object_type = subject.resource,
            component_ids = (None if subject.resource == "radical" else subject.component_subject_ids),
            components = None, 
            meanings = subject.meanings,
            aux_meanings = subject.aux_meanings,
            readings = (None if Card._is_radical(subject) else subject.readings),
            part_of_speech = Card._get_part_of_speech(subject),
            context = Card._get_context(subject),
            mnemonic = mnemonic,
            audio_url = Card._get_audio_url(subject),
            image_url = Card._get_audio_url(subject),
            position = position,
            date_created = datetime.now(),
            date_updated = datetime.now(),
        )

    @staticmethod
    def from_db():
        """
        Return Card type from the database. 
        """
        
        pass


    def to_anki_note(self, index, download=True):
        
        components: Components  = self.get_components()
        meanings: str = self.get_meanings()
        meanings_list: MeaningList = self.get_meaning_lists()
        readings: ReadingData = self.get_readings()
        audio: str = self.get_audio()        
        image: str = self.get_image()

        out: List[str] = [
            str(self.wk_id),
            html.escape(self.none_to_blank(self.characters)), 
            html.escape(self.object_type.capitalize()),
            html.escape(components.characters),
            html.escape(components.names),
            html.escape(components.types),
            html.escape(meanings),
            html.escape(meanings_list.white),
            html.escape(meanings_list.black),
            html.escape(readings.onyomi),
            html.escape(readings.kunyomi),
            html.escape(readings.nanori),
            html.escape(readings.accepted),
            html.escape(readings.whitelist),
            html.escape(readings.blacklist),
            html.escape(self.none_to_blank(self.part_of_speech)),
            html.escape(self.context[0].ja),
            html.escape(self.context[0].en),
            html.escape(self.context[1].ja),
            html.escape(self.context[1].en),
            html.escape(self.context[2].ja),
            html.escape(self.context[2].en),
            (self.meaning_mnemonic or ""),
            (self.meaning_mnemonic_info or ""),
            (self.reading_mnemonic or ""),
            (self.reading_mnemonic_info or ""),
            html.escape(audio),
            image,
            str(index), 
            "-"
        ]      
        return out 

    def save(self):
        try:
            with db.atomic():
                subject = FDB.Subject.create(
                    wk_id = self.wk_id,
                    characters = self.get_characters(),
                    object_type = self.object_type,
                    meaning_mnemonic = self.mnemonic.meaning_mnemonic

                    )
        except Error as e:
            print(e)
    def none_to_blank(self, input: str) -> str:
        return ("" if input == None else input)

    def get_characters(self) -> str:
        return self.none_to_blank(self.characters)

    def get_image(self) -> str:
        if self.image_url == None or self.image_url == []:
            return ""
        if self.characters == "":
            return ""
        return f"<img id=\"quest-img\"src={self.get_file(self.image_url[0])}>"

    def get_primary_meaning(self) -> str:
        return [meaning.meaning for meaning in self.meanings if meaning.primary == True][0]

    def get_meanings(self) -> str:
        return ", ".join([meaning.meaning 
                          for meaning in self.meanings 
                          if meaning.accepted_answer == True])
    
    def get_meaning_lists(self) -> MeaningList:
        white = self._get_list_of_meanings_as_string("whitelist")
        return MeaningList(white = f"{self.get_meanings()}, {white}".removesuffix(", "), 
                           black = self._get_list_of_meanings_as_string("blacklist"))

    def get_readings(self) -> ReadingData:
        if self.readings == None:
            return ReadingData(onyomi= "",
                           kunyomi= "",
                           nanori= "",
                           accepted= "",
                           whitelist="",
                           blacklist= "")

        return ReadingData(onyomi= ", ".join([reading.reading for reading in self.readings if reading.type == "onyomi"]),
                           kunyomi= ", ".join([reading.reading for reading in self.readings if reading.type == "kunyomi"]),
                           nanori= ", ".join([reading.reading for reading in self.readings if reading.type == "nanori"]),
                           accepted= ", ".join([reading.reading for reading in self.readings if reading.accepted_answer == True]),
                           whitelist=", ".join([reading.reading for reading in self.readings if reading.accepted_answer == True]),
                           blacklist= ", ".join([reading.reading for reading in self.readings if reading.accepted_answer == False]))
    
    def get_audio(self) -> str:
        if self.audio_url == None:
            return ""
        return "".join([f"[sound:{self.get_file(url)}]" for url in self.audio_url])
        

    def get_file(self, url) -> str:
        r: Response  = requests.get(url, allow_redirects=True)
        name = re.findall("filename\*=(.+)", r.headers["content-disposition"])
        name = urllib.parse.unquote(name[0]).removeprefix("UTF-8''")
        open(f"files/{name}", 'wb').write(r.content)
        return name

    def is_vocab(self):
        if self.object_type == "vocabulary":
            return True
        return False
    
    def is_radical(self):
        if self.object_type == "radical":
            return True
        return False
    
    def is_kanji(self):
        if self.object_type == "kanji":
            return True
        return False
    
    def get_components(self):
        return Components("","", "")

    def _get_list_of_meanings_as_string(self, type:str) -> str:
        return ", ".join([meaning.meaning 
                          for meaning in self.aux_meanings 
                          if meaning.type == type])
    
    @staticmethod
    def _is_vocab(subject):
        if (subject.resource == "vocabulary"):
            return True
        return False
    
    @staticmethod
    def _is_radical(subject):
        if (subject.resource == "radical"):
            return True
        return False
    
    @staticmethod
    def _is_kanji(subject):
        if (subject.resource == "kanji"):
            return True
        return False

    @staticmethod
    def _get_part_of_speech(subject):
        if(Card._is_vocab(subject)):
            return ", ".join(subject.parts_of_speech)
        return None
    
    @staticmethod
    def _get_audio_url( subject) -> Optional[List[str]]:
        if(Card._is_vocab(subject)):
            audios = subject._resource["pronunciation_audios"]
            return [audio["url"] for audio in audios if audio['content_type'] == AUDIO_FILE]
        return None
    
    @staticmethod
    def _get_image_url(subject) -> Optional[List[str]]: 
        if(Card._is_radical(subject)):
            images = subject._resource["character_images"]
            return [image["url"] for image in images if image['content_type'] == IMAGE_FILE and image["metadata"]["inline_styles"] == True]
        return None

    @staticmethod
    def _get_context(subject) -> Optional[List[Context]]:
        if (Card._is_vocab(subject)):
            contexts = subject._resource["context_sentences"]
            return [Context(con["en"],con["ja"]) for con in contexts]
        return [Context("","") for _ in range(3)]

    def _as_small_dict(self):
        return {
            "wk_id": self.wk_id,
            "type": self.object_type,
            "characters": self.characters,
            "meaning": ([meaning.meaning for meaning in self.meanings if meaning.primary == True][0]),
            "level": self.level,
            "lesson_position": self.lesson_position
        }

    def _as_dict(self):
        out = {
            "wk_id": self.wk_id,
            "characters": self.characters,
            "object_type": self.object_type,
            "components": self.components,
            "meanings": ([dict(
                                meaning=meaning.meaning,
                                primary=meaning.primary,
                                accepted_answer=meaning.accepted_answer
                              ) for meaning in self.meanings] if self.meanings else None),
            "aux_meanings": ([dict(
                                meaning=meaning.meaning,
                                type=meaning.type,
                              ) for meaning in self.aux_meanings] if self.aux_meanings else None),
            "readings": ([dict(
                                reading=reading.reading,
                                primary=reading.primary,
                                accepted_answer=reading.accepted_answer, 
                                type=reading.type
                              ) for reading in self.readings] if self.readings else None),
            "part_of_speech": self.part_of_speech,
            "context": ([{"en":context.en,"ja":context.ja} for context in self.context] if self.context else None),
            "meaning_mnemonic": self.meaning_mnemonic,
            "meaning_mnemonic_info": self.meaning_mnemonic_info,
            "reading_mnemonic": self.reading_mnemonic,
            "reading_mnemonic_info": self.reading_mnemonic_info,
            "audio_url": self.audio_url,
            "image_url": self.image_url
        }  
        return out 
    @classmethod 
    def sort(cls):
        return lambda cls: (cls.level, cls.lesson_position) 

    def __repr__(self):
         return f"""
            'wk_id':{self.wk_id},
            'characters':{self.characters},
            'object_type':{self.object_type},
            'components':{self.components},
            'meanings':{[meaning.meaning for meaning in self.meanings]},
            'aux_meanings':{[meaning.meaning for meaning in self.aux_meanings]},
            'readings':{[reading.reading for reading in self.readings]},
            'part_of_speech':{self.part_of_speech},
            'context':{self.context},
            'meaning_mnemonic':{self.meaning_mnemonic},
            'meaning_mnemonic_info':{self.meaning_mnemonic_info},
            'reading_mnemonic':{self.reading_mnemonic},
            'reading_mnemonic_info':{self.reading_mnemonic_info},
            'audio_url':{self.audio_url},
            'image_url':{self.image_url}
"""
