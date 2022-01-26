from dataclasses import dataclass, asdict
from wanikani_api.models import Subject


@dataclass
class Context:
    en: str = ""
    ja: str = ""

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
    meaning: str
    meaning_info: str
    reading: str
    reading_info: str
    
    @classmethod
    def from_api(cls, subject:Subject):
        meaning = subject._resource.get("meaning_mnemonic", "")
        meaning_info = subject._resource.get("meaning_hint","")
        reading = subject._resource.get("reading_mnemonic", "")
        reading_info = subject._resource.get("reading_hint", "")
        return cls(
            meaning = meaning,
            meaning_info = meaning_info,
            reading = reading,
            reading_info = reading_info,
        )
