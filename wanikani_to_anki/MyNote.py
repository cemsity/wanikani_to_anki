from genanki import Note
from genanki.util import guid_for


class MyNote(Note):
    @property
    def guid(self):
        return guid_for(self.fields[0],self.fields[27])

