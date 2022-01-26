from wanikani_to_anki.FileStore import FileStore
from wanikani_to_anki.ComponentStore import Components, ComponentStore
from wanikani_to_anki.Card import Card
from os.path import exists


class Factory():
    file_store: FileStore
    component_store: ComponentStore
    file_filepath: str

    def __init__(self, file_filepath=None):
        if file_filepath is not None and exists(file_filepath):
            self.file_store = FileStore.load(file_filepath)
            self.file_filepath = file_filepath
        else: 
            self.file_store = FileStore()
            self.file_filepath = file_filepath if file_filepath is not None else "files.pkl" 
           
        self.component_store = ComponentStore()
        Card.file_store = self.file_store
        Card.component_store = self.component_store


    def new_card(self):
        return Card

    def save_store(self):
        self.file_store.save(self.file_filepath)