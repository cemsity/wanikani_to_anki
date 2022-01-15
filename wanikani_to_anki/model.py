from genanki import Model

RADICAL_MODEL_ID = 1401057364
FIELDS=[
    {"name": "wanikani_id"},
    {"name": "Characters"},
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
    {"name": "Do_Not_Modify"},
] 

FRONT_file = open("templates/front.html", 'r')
FRONT = FRONT_file.read()
FRONT_file.close()

BACK_file = open("templates/back.html", 'r')
BACK = BACK_file.read()
BACK_file.close()

CSS_FILE = open("templates/styling.css", 'r')
CSS = CSS_FILE.read()
CSS_FILE.close()

wanikani_model = Model(
    model_id=RADICAL_MODEL_ID,
    name="Wanikani",
    fields=FIELDS,
    templates=[
        {
            "name":"Meaning",
            "qfmt":f"{FRONT}",
            "afmt":f"{BACK}",
        },
        {
            "name":"Reading",
            "qfmt":"{{#Reading}}\n" + FRONT +"{{/Reading}}",
            "afmt":"{{#Reading}}\n" + BACK + "{{/Reading}}", 
        }
    ],
    css = CSS,
    sort_field_index=28
    )
