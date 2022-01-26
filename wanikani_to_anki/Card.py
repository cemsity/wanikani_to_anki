from datetime import datetime
from wanikani_api.models import Subject, Meaning, AuxiliaryMeaning, Reading
from typing import Callable, Iterator, List, Optional, Dict
from dataclasses import dataclass, asdict
import httpx
from httpx import Response
import urllib.parse
import re
import html
import glob
from os.path import exists
from itertools import filterfalse
from wanikani_to_anki.ComponentStore import Components, ComponentStore
from wanikani_to_anki.FileStore import FileStore, File
from wanikani_to_anki.Dataclasses import Context, MeaningList, ReadingData, Mnemonic

#Constants
IMAGE_FILE = "image/svg+xml"
AUDIO_FILE = "audio/mpeg"
FILES = glob.glob("files/*")


class Card(object):
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
    level: int
    lesson_position: int
    date_created: datetime
    date_updated: datetime
    file_store: FileStore
    component_store: ComponentStore

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
                level: int, 
                lesson_position: int, 
                audio_url: Optional[List[str]],
                image_url: Optional[List[str]],
                date_created: datetime,
                date_updated: datetime,
                ):
        self.wk_id = wk_id
        self.characters = characters
        self.object_type = object_type
        self.component_ids = component_ids
        self.components = components
        self.meanings = meanings
        self.aux_meanings = aux_meanings
        self.readings = readings 
        self.part_of_speech = part_of_speech
        self.context = context
        self.mnemonic = mnemonic
        self.audio_url = audio_url
        self.image_url = image_url #Radicals that do not have a characters
        self.level = level
        self.lesson_position = lesson_position
        self.date_created= date_created
        self.date_updated= date_updated

    @classmethod
    def from_api(cls, subject:Subject):

        mnemonic = Mnemonic.from_api(subject)
        cls.save_to_store(subject)
        return cls(
            wk_id = subject.id,
            characters = subject.characters,
            object_type = subject.resource,
            component_ids = (None if subject.resource == "radical" else subject.component_subject_ids),
            components = None, 
            meanings = subject.meanings,
            aux_meanings = subject.auxiliary_meanings,
            readings = (None if cls._is_radical(subject) else subject.readings),
            part_of_speech = cls._get_part_of_speech(subject),
            context = cls._get_context(subject),
            mnemonic = mnemonic,
            audio_url = cls._get_audio_url(subject),
            image_url = cls._get_image_url(subject),
            level = subject.level,
            lesson_position= subject._resource["lesson_position"],
            date_created = datetime.now(),
            date_updated = datetime.now(),
        )

    async def to_anki_note(self, index, download=True):
        
        components: Components  = self.get_components()
        meanings: str = self.get_meanings()
        meanings_list: MeaningList = self.get_meaning_lists()
        readings: ReadingData = self.get_readings()
        audio: str = await self.get_audio()        
        image: str = await self.get_image()
        print(f"Returning: {self.wk_id} : {self.get_primary_meaning()}")
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
            html.escape(self.get_context(1).ja),
            html.escape(self.get_context(1).en),
            html.escape(self.get_context(2).ja),
            html.escape(self.get_context(2).en),
            (self.mnemonic.meaning or ""),
            (self.mnemonic.meaning_info or ""),
            (self.mnemonic.reading or ""),
            (self.mnemonic.reading_info or ""),
            html.escape(audio),
            image,
            str(index), 
            "-"
        ]      
        return out 

    def get_context(self, index):
        list_get = lambda l, x, d=None: d if not l[x:x+1] else l[x]
        return list_get(self.context, index, Context("",""))

    def none_to_blank(self, input: str) -> str:
        return ("" if input == None else input)

    def get_characters(self) -> str:
        return self.none_to_blank(self.characters)

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

    def get_primary_reading(self) -> str:
        if self.readings is not None:
            reading = next(filter(lambda reading: reading.primary, self.readings))
            return reading.reading
        return "NO_READING"

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
    
    async def get_audio(self) -> str:
        if self.audio_url == None:
            return ""
        files = Card.file_store.get(self.wk_id)
        if files is not None:
            return await self.audio_field(self.get_file_from_store, files)
        return await self.audio_field(self.get_file_from_internet, self.audio_url)

    async def audio_field(self, func: Callable, src: List[File]):
        files = [f"[sound:{await func(j)}]" for j in src]
        primary = sorted(filter(lambda x: self.get_primary_reading() in x, files))
        non = sorted(filterfalse(lambda x: self.get_primary_reading() in x, files))
        return f"{''.join(primary)}{''.join(non)}"

    async def get_image(self) -> str:
        if self.image_url == None or self.image_url == []:
            return ""
        if self.characters is not None:
            return ""
        file = Card.file_store.get(self.wk_id)
        if file is not None:
            return await self.image_field(self.get_file_from_store, file[0])
        return await self.image_field(self.get_file_from_internet, self.image_url[0])
        
    async def image_field(self, func, src):
        return f"<img id=\"quest-img\"src={await func(src)}>"

    async def get_file_from_internet(self, url) -> str:
        async with httpx.AsyncClient() as client:
            r: Response  = await client.get(url, follow_redirects=True)
        name = re.findall("filename\*=(.+)", r.headers["content-disposition"])
        name = urllib.parse.unquote(name[0]).removeprefix("UTF-8''")
        open(f"files/{name}", 'wb').write(r.content)
        file = File(url, name, r.content)
        Card.file_store.add(self.wk_id, file)
        return name

    async def get_file_from_store(self, file:File):
        if file.file_name in FILES:
            return file.file_name
        else:
            open(f"files/{file.file_name}", "wb").write(file.file_obj)
            return file.file_name    

    def is_vocab(self):
        return True if self.object_type == "vocabulary" else False
    
    def is_radical(self):
        return True if self.object_type == "radical" else False
    
    def is_kanji(self):
        return True if self.object_type == "kanji" else False
    
    def get_components(self) -> Components:
        if self.is_radical():
            return Components("", "", "")
        else: 
            components = Card.component_store.get(self.wk_id)
            return Components(
                characters=", ".join([component.characters for component in components]),
                names=", ".join([component.names for component in components]),
                types=", ".join([component.types for component in components])
            )

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
    def save_to_store(subject: Subject):
        if Card._is_vocab(subject):
            return True
        else: 
            primary_meaning = [meaning.meaning for meaning in subject.meanings if meaning.primary == True ][0]
            characters = subject.characters or ""
            component = Components(characters, primary_meaning, subject.resource)
            for i in subject.amalgamation_subject_ids:
                Card.component_store.add(i, component)

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

    @classmethod 
    def sort(cls):
        return lambda cls: (cls.level, cls.lesson_position) 

    @staticmethod
    def _get_context(subject) -> List[Context]:
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
            "component_ids": self.component_ids,
            "components": asdict(self.get_components()),
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
            "meaning_mnemonic": self.mnemonic.meaning,
            "meaning_mnemonic_info": self.mnemonic.meaning_info,
            "reading_mnemonic": self.mnemonic.reading,
            "reading_mnemonic_info": self.mnemonic.reading_info,
            "audio_url": self.audio_url,
            "image_url": self.image_url
        }  
        return out 

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
