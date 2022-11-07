from peewee import *

db = SqliteDatabase("ao3.db")

class BaseModel(Model):
    class Meta:
        database = db

class TagType(BaseModel):
    name = CharField(primary_key=True)

class Tag(BaseModel):
    _id = IntegerField(primary_key=True)
    cat = ForeignKeyField(TagType)
    name = CharField()
    canon = BooleanField()
    count = IntegerField()
    merge = IntegerField(null=True)

class Work(BaseModel):
    _id = IntegerField(primary_key=True)
    created = DateField()
    lang = CharField()
    restricted = BooleanField()
    complete = BooleanField()
    word_count = IntegerField()

class WorkTag(BaseModel):
    _id = AutoField(primary_key=True)
    work_id = ForeignKeyField(Work, backref="work_tags")
    tag_id = ForeignKeyField(Tag)

db.create_tables([Tag, TagType, Work, WorkTag])
