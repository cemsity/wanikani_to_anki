from dataclasses import astuple, dataclass, field
from pickle import Unpickler, Pickler
import pickle
from typing import Dict, List, Optional
from enum import Enum
from itertools import chain

class FileType(Enum):
    IMAGE = 10
    AUDIO = 20

    def as_string(self):
        return str(self.name).lower()


@dataclass 
class File:
    url: str
    file_name: str
    file_obj: bytes
    file_type: Optional[FileType] = None

    def __init__(self, url: str, file_name: str, file_obj: bytes):
        self.url = url
        self.file_name = file_name
        self.file_obj = file_obj
        self.file_type = File._detect_type(file_name)  
    
    @staticmethod
    def _detect_type(file_name: str) -> FileType:
        if ".svg" in file_name:
            return FileType.IMAGE
        else:
            return FileType.AUDIO

    def __repr__(self):
        return f"""File{{
        'url': {self.url},
        'file_name': {self.file_name},
        'file_type': {self.file_type},
        'file_obj': {True if self.file_type is not None else False}
        }}"""

class FileStore():
    store: Dict[int, List[File]]
    def __init__(self):
        self.store = {}

    def add(self, id:int, file:File):
        if id in self.store:
            self.store[id].append(file)
        else:
            self.store[id] = [file]
    
    def get(self, id:int) -> Optional[List[File]]:
        file_wpr = self.store.get(id)
        if file_wpr is None:
            return None
        return file_wpr

    def save(self, filepath):
        Pickler(open(filepath, 'wb')).dump(self.store)
    
    def dump(self, file_out):
        with open(file_out, "w") as f:
            for k, v in self.store.items():
                f.write(f"{k} : {v} \n")

    @staticmethod
    def load(filepath):
        fs = FileStore()
        if filepath is None:
            return fs
        fs.store = Unpickler(open(filepath,"rb")).load()
        return fs