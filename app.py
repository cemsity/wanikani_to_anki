import enum
import pprint
from typing import OrderedDict
import genanki
from wanikani_api.client import Client
from typing import List, Optional
from dataclasses import dataclass
from wanikani_to_anki.MyNote import MyNote
from wanikani_to_anki.flashcard import Card
import wanikani_to_anki.MyNote
import json
@dataclass
class Context:
    en: str
    jp: str


def main():
    v2_api_key = "0633ea52-d04e-4f1c-8767-f6acef3b6aad"
    client = Client(v2_api_key)
    # user_information = client.user_information()
    # print(user_information.preferences)
    all_radicals = client.subjects(levels=[1])
    # print(len(all_radicals))
    index = 1
    cards: List[Card] = []
    for radical in all_radicals:
        card = Card(radical)
        cards.append(card)
    cards.sort(key=Card.sort())
    for card in cards:
        print(card.to_anki_note(index))
        index += 1
    return 0

    
    # def _get_audio_url(subject):


if __name__ == '__main__':
    main()


