import genanki
from wanikani_api.client import Client
from typing import List
from dataclasses import dataclass
from wanikani_to_anki.MyNote import MyNote
from wanikani_to_anki.Card import Card
from wanikani_to_anki.Factory import Factory
from wanikani_to_anki.model import wanikani_model
import glob
import os
import asyncio

DECK_ID = 1854033380


async def main():
    v2_api_key = get_api_key()
    client = Client(v2_api_key)
    index = 1
    my_deck = genanki.Deck(
        DECK_ID, "Wanikani3 - This time its updatable"
    )
    factory = Factory("media.pkl")
    wani_card = factory.new_card()
    for i in range(1,11):
        print(f"Lesson: {i}")
        level_subjects = client.subjects(levels=i)
        cards: List[Card] = []
        for subject in level_subjects:
            card = wani_card.from_api(subject)
            cards.append(card)
        cards.sort(key=Card.sort())
        coros = [card.to_anki_note(index+i) for i, card in enumerate(cards)]
        res_cards = await asyncio.gather(*coros)
        
        for card in res_cards:
            
            new_note = MyNote(model = wanikani_model,
                              fields= card,
                              tags=[f"Lesson_{i}",f"{card[2]}"],
                              due=index)
            index += 1
            my_deck.add_note(new_note)
        factory.save_store()
    
    my_package = genanki.Package(my_deck)
    my_package.media_files = get_media_from_file("./files/*")
    my_package.write_to_file("wanikani3.apkg")

    return 0

def get_media_from_file(path):
    return glob.glob(path)


def dump_pickle():
    from wanikani_to_anki.FileStore import FileStore
    file_store = FileStore.load('media.pkl')
    file_store.dump("dump.txt")

def get_api_key():
    return os.environ.get("WANIKANI_API")

if __name__ == '__main__':
    asyncio.run(main())
    dump_pickle()


