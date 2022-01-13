from genanki import Model
from MyNote import MyNote

RADICAL_MODEL_ID = 1401057364
FIELDS=[{"name": "Characters"},
        {"name": "Object_Type"},
        {"name": "Components"},
        {"name": "Component_Names"},
        {"name": "Component_Types"},
        {"name": "Meaning"},
        {"name": "Meaning_Whitelist"},
        {"name": "Meaning_Blacklist"},
        {"name": "Reading_Onyomi"},
        {"name": "Reading_Kunyomi"},
        {"name": "Reading_Nanori"},
        {"name": "Reading"},
        {"name": "Reading_Whitelist"},
        {"name": "Reading_Blacklist"},
        {"name": "Speech_Type"}, # Part_of_speach
        {"name": "Context_jp"},
        {"name": "Context_en"},
        {"name": "Context_jp_2"},
        {"name": "Context_en_2"},
        {"name": "Context_jp_3"},
        {"name": "Context_en_3"},
        {"name": "Meaning_Mnemonic"},
        {"name": "Meaning_Info"},
        {"name": "Reading_Mnemonic"},
        {"name": "Reading_Info"},
        {"name": "Audio"},
        {"name": "Image"}, # only for radicals that do not have a valid character 
        {"name": "sort_id"},
        {"name": "wanikani_id"}, 
        {"name": "Do_Not_Modify"}] 

wanikani_model = Model(
    model_id=RADICAL_MODEL_ID,
    name="Wanikani",
    fields=FIELDS,
    templates=[
        {
            "name":"Meaning",
            "qfmt":"{{Characters}}",
            "afmt":"{{Meaning}}",
        },
        {
            "name":"Reading",
            "qfmt":"{{Characters}}",
            "afmt":"{{Reading}}", 
        }
    ],
    sort_field_index=26
    )
