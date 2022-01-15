from peewee import Model
from playhouse.sqlite_ext import SqliteExtDatabase

sqlite_db = SqliteExtDatabase('wanikani.db', pragmas=(
    ('cache_size', -1024 * 64),
    ('journal_mode', 'wal'),
    ('foreign_keys', 1),
) )

class BaseModel(Model):
    """A base modle that will use the Sqllite database"""
    class Meta:
        database = sqlite_db

