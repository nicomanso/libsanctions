import logging
from normality import stringify
from pprint import pprint  # noqa

from libsanctions.model import engine, session, Base
from libsanctions.model import Entity


log = logging.getLogger(__name__)


class Source(object):

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(name)
        self.entity_count = 0
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def create_entity(self, *keys):
        keys = [stringify(k) for k in keys]
        entity_id = ':'.join([k for k in keys if k is not None])
        entity = Entity(entity_id)
        session.add(entity)
        self.entity_count += 1
        return entity

    def finish(self):
        self.log.info("Parsed %s entities", self.entity_count)
