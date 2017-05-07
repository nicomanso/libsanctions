import logging
from normality import slugify
from pprint import pprint  # noqa
from datetime import datetime

from libsanctions.model import engine, session, Base
from libsanctions.model import Entity, Address, Alias
from libsanctions.model import Identifier, Birth, Nationality
from libsanctions.export import export_csv_table
from libsanctions.archive import get_bucket, upload_csv


log = logging.getLogger(__name__)

CSV_EXPORTS = (
    (Entity, 'entities'),
    (Address, 'addresses'),
    (Alias, 'aliases'),
    (Identifier, 'identifiers'),
    (Birth, 'births'),
    (Nationality, 'nationalities')
)


class Source(object):

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(name)
        self.run = datetime.utcnow().date().isoformat()
        self.bucket = get_bucket()
        self.entity_count = 0
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def create_entity(self, *keys):
        keys = [slugify(k, sep='-') for k in keys]
        entity_id = '-'.join([k for k in keys if k is not None])
        entity = Entity(self.name, entity_id)
        session.add(entity)
        self.entity_count += 1
        return entity

    def generate_csv(self):
        for model, file_name in CSV_EXPORTS:
            file_path = export_csv_table(model, file_name)
            if self.bucket is not None and file_path is not None:
                upload_csv(self.bucket, self.name, self.run, file_path)

    def finish(self):
        self.log.info("Parsed %s entities", self.entity_count)
        self.generate_csv()
