import logging
from normality import slugify
from pprint import pprint  # noqa
from morphium import Archive

from libsanctions.model import Entity, Base, engine, session
from libsanctions.export import export_csv_tables, export_ijson
from libsanctions.config import BUCKET


log = logging.getLogger(__name__)


class Source(object):

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(name)
        prefix = 'v1/sources/%s' % name
        self.archive = Archive(bucket=BUCKET, prefix=prefix)
        self.entity_count = 0
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def create_entity(self, *keys):
        keys = [slugify(k, sep='-') for k in keys]
        entity_id = '-'.join([k for k in keys if k is not None])
        entity = Entity.by_id(self.name, entity_id)
        if entity is None:
            entity = Entity(self.name, entity_id)
            session.add(entity)
        self.entity_count += 1
        return entity

    def finish(self):
        self.log.info("Parsed %s entities", self.entity_count)
        export_csv_tables(self.archive)
        export_ijson(self.archive, self.name)
