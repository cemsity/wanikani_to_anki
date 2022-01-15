import html
from typing import OrderedDict
import genanki
from wanikani_api.client import Client
from typing import List, Optional
from dataclasses import dataclass
from wanikani_to_anki.MyNote import MyNote
from wanikani_to_anki.flashcard import Card
from wanikani_to_anki.model import wanikani_model
import glob
from  wanikani_to_anki.db import sqlite_db as db
from wanikani_to_anki.FlashcardDB import Subject, Meanings, Components, Readings, PartOfSpeech, Context, Audio, Image
import json

DECK_ID = 1854033380

def main():
    v2_api_key = "0633ea52-d04e-4f1c-8767-f6acef3b6aad"
    client = Client(v2_api_key)
    # user_information = client.user_information()
    # print(user_information.preferences)
    # all_radicals = client.subjects(levels=[1])
    # print(len(all_radicals))
    index = 1
    my_deck = genanki.Deck(
        DECK_ID, "Wanikani Test"
    )
    
    for i in range(60):
        level_subjects = client.subjects(levels=i, types=["radical"])
        cards: List[Card] = []
        for subject in level_subjects:
            card = Card(subject)
            cards.append(card)
        cards.sort(key=Card.sort())
        for card in cards:
            new_card = card.to_anki_note(index)
            new_note = MyNote(model = wanikani_model,
                              fields= new_card,
                              tags=[f"Lesson_{i}",f"{card.object_type.lower()}"])
            index += 1
            my_deck.add_note(new_note)
            print(new_card)
    
    my_package = genanki.Package(my_deck)
    my_package.media_files = get_media_from_file("./files/*")
    my_package.write_to_file("test.apkg")

    return 0
def get_radicals():
    v2_api_key = "0633ea52-d04e-4f1c-8767-f6acef3b6aad"
    client = Client(v2_api_key)
    # user_information = client.user_information()
    # print(user_information.preferences)
    # all_radicals = client.subjects(levels=[1])
    # print(len(all_radicals))
    index = 1
    my_deck = genanki.Deck(
        DECK_ID, "Wanikani Test"
    )
    level_subjects = client.subjects( types=["radical"])
    cards: List[Card] = []
    for subject in level_subjects:
        card = Card(subject)
        cards.append(card)
    cards.sort(key=Card.sort())
    for card in cards:
        new_card = card.to_anki_note(index)
        new_note = MyNote(model = wanikani_model,
                            fields= new_card,
                            tags=[f"Lesson_{card.level}",f"{card.object_type.lower()}"])
        index += 1
        my_deck.add_note(new_note)
        print(new_card)

    my_package = genanki.Package(my_deck)
    my_package.media_files = get_media_from_file("./files/*")
    my_package.write_to_file("test.apkg")

def get_media_from_file(path):
    return glob.glob(path)

def test():
    v2_api_key = "0633ea52-d04e-4f1c-8767-f6acef3b6aad"
    client = Client(v2_api_key)
    user_information = client.user_information()
    print(user_information) 

def test_db():
    
if __name__ == '__main__':
    test_db()


