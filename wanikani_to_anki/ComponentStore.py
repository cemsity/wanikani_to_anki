from dataclasses import dataclass
from typing import Dict, List
from pickle import Unpickler, Pickler

@dataclass
class Components:
    characters: str
    names: str
    types: str

class ComponentStore():
    store: Dict[int, List[Components]]
    def __init__(self):
        self.store = {}
    def add(self, id: int, component: Components):
        if id not in self.store:
            self.store[id] = [component]
        else:
            self.store[id].append(component)
    def get(self, id: int):
        return self.store.get(id, [Components(characters=f"FAILED: {id}", names="", types="")])

    def save(self, filepath):
        Pickler(open(filepath, 'wb')).dump(self.store)

    @staticmethod
    def load(filepath):
        fs = ComponentStore()
        if filepath is None:
            return fs
        fs.store = Unpickler(open(filepath,"rb")).load()
        return fs