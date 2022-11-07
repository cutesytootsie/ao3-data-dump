import pandas as pd
import random

from database_utility import BaseModel
from database_utility import Tag
from database_utility import TagType
from database_utility import Work
from database_utility import WorkTag

TAG_TYPES = [
    "Media",
    "Rating",
    "ArchiveWarning",
    "Category",
    "Character",
    "Fandom",
    "Relationship",
    "Freeform",
    "UnsortedTag",
    ]

def initiate_database():
    count = 0
    for t in TAG_TYPES:
        exists = TagType.get_or_none(TagType.name==t)
        if not exists:
            count += 1
            new_tag = TagType.create(name=t)
            print(f"created new tag category: {t}")
    print(f"### {count} new tag categories created ###")

def import_tags(filename, limit=1, my_tags=[]):
    print("reading csv file ...")
    tags_iterator = pd.read_csv(filename)
    batch = []
    batch_count = 0
    last_record = _get_last(Tag)
    for index, tag_data in tags_iterator.iterrows():
        if index <= last_record:
            continue
        batch, batch_count = _process_batch(batch, batch_count, Tag)
        if len(batch) == 0:
            if batch_count > limit:
                print(f"\nbatch limit of {limit} reached, finishing ...")
                break
        new_tag = Tag(
            _id=tag_data.id,
            cat=tag_data.type,
            name=tag_data.name,
            canon=tag_data.canonical,
            count=tag_data.cached_count,
            merge=tag_data.merger_id
            )
        if any([new_tag.id in my_tags, new_tag.merge in my_tags]):
            print("★", end="")
#        else:
#            print("·", end="")
        batch.append(new_tag)

def _process_batch(batch, batch_count, db_class: BaseModel):
    if len(batch) > 300:
        print(f"-{batch_count}-", end="")
        db_class.bulk_create(batch)
        batch = []
        batch_count += 1
    return batch, batch_count

def _get_last(db_class: BaseModel):
    try:
        last_record = db_class.select().objects()[-1]._id
        print(f"### last index in database: {last_record} ###")
        return last_record
    except IndexError:
        return 0

def import_fics(filename, limit=1, my_tags=[]):
    print("reading csv file ...")
    works_iterator = pd.read_csv(filename)
    work_batch, tag_batch = [], []
    batch_count = 0
    relevant_tags = Tag.select().where(
        (Tag._id.in_((my_tags))) | (Tag.merge.in_((my_tags)))
        ).objects()
    last_record = _get_last(Work)
    for index, work_data in works_iterator.iterrows():
        if index <= last_record:
            continue
        tag_batch, batch_count = _process_batch(tag_batch, batch_count, WorkTag)
        if len(tag_batch) == 0:
            Work.bulk_create(work_batch)
            work_batch = []
            if batch_count > limit:
                print(f"\nbatch limit of {limit} reached, finishing ...")
                break
        created, lang, restr, compl, words, tags, xx = work_data
        tags = tags.split("+")
        if not _is_fic(words, tags):
            continue
        if len(relevant_tags) > 0 and not _is_relevant(tags, relevant_tags):
            continue
        this_work = Work(
            _id=index,
            created=created,
            lang=lang,
            restricted=bool(restr),
            complete=bool(compl),
            word_count=int(words),
            )
        print("·", end="")
        work_batch.append(this_work)
        for tag_id in tags:
            this_tag = WorkTag(work_id=index, tag_id=int(tag_id))
            tag_batch.append(this_tag)
    print("DONE! ✪")

def _is_fic(word_count, tags):
    if any([x != x for x in [word_count, tags]]):
        return False
    if word_count == 0:
        return False
    return True

def _is_relevant(tags_to_filter, relevant_tags):
    for tag in relevant_tags:
        if str(tag._id) in tags_to_filter:
            return True
    return False

def test_for_dupes():
    errors = 0
    print("random checking for dupes...")
    all_works = Work.select().objects()
    for i in range(20):
        s = random.choice(range(0,len(all_works)))
        w = all_works[s]
        dupes = Work.select().where(
            (Work.word_count==w.word_count) & 
            (Work.tags == w.tags) &
            (Work.created == w.created) &
            (Work.language == w.language)
            ).objects()
        for dupe in dupes:
            if dupe._id != w._id:
                print(f"⚠ {w._id} != {dupe._id}")
                errors+=1
    return errors
