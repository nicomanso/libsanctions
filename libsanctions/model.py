import logging
import countrynames
from collections import OrderedDict
from normality import stringify, collapse_spaces
from dalet import parse_date
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, Unicode
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import ForeignKey

from libsanctions.config import DATABASE_URI
from libsanctions.util import clean_obj

log = logging.getLogger(__name__)
Base = declarative_base()
engine = create_engine(DATABASE_URI)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)


class Stringify(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        return stringify(value)


class Date(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return parse_date(value)


class JsonRowMixIn(object):

    def to_row(self):
        data = OrderedDict()
        data['entity_id'] = self.entity_id
        data.update(self.to_json())
        return data


class NameMixIn(object):
    _name = Column('name', Stringify, nullable=True)
    title = Column(Stringify, nullable=True)
    first_name = Column(Stringify, nullable=True)
    second_name = Column(Stringify, nullable=True)
    third_name = Column(Stringify, nullable=True)
    last_name = Column(Stringify, nullable=True)

    @hybrid_property
    def name(self):
        if self._name is not None:
            return self._name
        names = (self.first_name, self.second_name,
                 self.third_name, self.last_name)
        names = [n for n in names if n is not None]
        if len(names):
            return collapse_spaces(' '.join(names))

    @name.setter
    def name(self, name):
        name = stringify(name)
        if name is not None:
            name = collapse_spaces(name)
        self._name = name

    def to_name_dict(self):
        data = OrderedDict()
        data['name'] = self.name
        data['first_name'] = self.first_name
        data['second_name'] = self.second_name
        data['third_name'] = self.third_name
        data['last_name'] = self.last_name
        data['title'] = self.title
        return data


class CountryMixIn(object):
    country_name = Column(Stringify, nullable=True)
    country_code = Column(Stringify, nullable=True)

    @property
    def country(self):
        return self.country_code or self.country_name

    @country.setter
    def country(self, name):
        self.country_name = name
        self.country_code = countrynames.to_code(name)

    def to_country_dict(self):
        data = OrderedDict()
        data['country'] = self.country_name
        data['country_code'] = self.country_code
        return data


class Alias(Base, NameMixIn, JsonRowMixIn):
    """An alternate name for an indivdual."""
    __tablename__ = 'alias'

    QUALITY_WEAK = 'weak'
    QUALITY_STRONG = 'strong'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Unicode, ForeignKey('data.id'))
    entity = relationship("Entity", backref="aliases")
    type = Column(Stringify, nullable=True)
    quality = Column(Stringify, nullable=True)
    description = Column(Stringify, nullable=True)

    def __init__(self, entity_id, name=None):
        self.entity_id = entity_id
        self.name = name

    def to_json(self):
        data = self.to_name_dict()
        data['type'] = self.type
        data['quality'] = self.quality
        data['description'] = self.description
        return data


class Address(Base, CountryMixIn, JsonRowMixIn):
    """An address associated with an entity."""
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String, ForeignKey('data.id'))
    entity = relationship("Entity", backref="addresses")
    text = Column(Stringify, nullable=True)
    note = Column(Stringify, nullable=True)
    street = Column(Stringify, nullable=True)
    street_2 = Column(Stringify, nullable=True)
    postal_code = Column(Stringify, nullable=True)
    city = Column(Stringify, nullable=True)
    region = Column(Stringify, nullable=True)

    def __init__(self, entity_id):
        self.entity_id = entity_id

    def to_json(self):
        data = self.to_country_dict()
        data.update({
            'text': self.text,
            'note': self.note,
            'street': self.street,
            'street_2': self.street_2,
            'postal_code': self.postal_code,
            'city': self.city,
            'region': self.region,
        })
        return data


class Identifier(Base, CountryMixIn, JsonRowMixIn):
    """A document issued to an entity."""
    __tablename__ = 'identifier'

    TYPE_PASSPORT = u'passport'
    TYPE_NATIONALID = u'nationalid'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String, ForeignKey('data.id'))
    entity = relationship("Entity", backref="identifiers")
    type = Column(Stringify, nullable=True)
    description = Column(Stringify, nullable=True)
    number = Column(Stringify, nullable=True)
    issued_at = Column(Date, nullable=True)

    def __init__(self, entity_id):
        self.entity_id = entity_id

    def to_json(self):
        data = OrderedDict()
        data['type'] = self.type
        data['number'] = self.number
        data.update(self.to_country_dict())
        data['issued_at'] = self.issued_at
        data['description'] = self.description
        return data


class Nationality(Base, CountryMixIn, JsonRowMixIn):
    """A nationality associated with an entity."""
    __tablename__ = 'nationality'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String, ForeignKey('data.id'))
    entity = relationship("Entity", backref="nationalities")

    def __init__(self, entity_id):
        self.entity_id = entity_id

    def to_json(self):
        return self.to_country_dict()


class Birth(Base, CountryMixIn, JsonRowMixIn):
    """Details regarding the birth of an entity."""
    __tablename__ = 'birth'

    TYPE_EXACT = 'exact'
    TYPE_APPROXIMATE = 'approximate'

    id = Column(Integer, primary_key=True)
    entity_id = Column(String, ForeignKey('data.id'))
    entity = relationship("Entity", backref="births")
    type = Column(Stringify, nullable=True)
    date = Column(Date, nullable=True)
    place = Column(Stringify, nullable=True)
    description = Column(Stringify, nullable=True)

    def __init__(self, entity_id):
        self.entity_id = entity_id

    def to_json(self):
        data = OrderedDict()
        data['type'] = self.type
        data['date'] = self.date
        data.update(self.to_country_dict())
        data['place'] = self.place
        data['description'] = self.description
        return data


class Entity(Base, NameMixIn):
    """A company or person that is subject to a sanction."""
    __tablename__ = 'data'

    TYPE_ENTITY = 'entity'
    TYPE_INDIVIDUAL = 'individual'

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    type = Column(String, nullable=True)
    summary = Column(Stringify, nullable=True)
    function = Column(Stringify, nullable=True)
    program = Column(Stringify, nullable=True)
    listed_at = Column(Date, nullable=True)
    updated_at = Column(Date, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, source, id):
        self.source = source
        self.id = id
        self.timestamp = datetime.utcnow()

    def create_alias(self, name=None):
        alias = Alias(self.id, name=name)
        session.add(alias)
        return alias

    def create_address(self):
        address = Address(self.id)
        session.add(address)
        return address

    def create_identifier(self):
        identifier = Identifier(self.id)
        session.add(identifier)
        return identifier

    def create_nationality(self):
        nationality = Nationality(self.id)
        session.add(nationality)
        return nationality

    def create_birth(self):
        birth = Birth(self.id)
        session.add(birth)
        return birth

    def save(self):
        self.timestamp = datetime.utcnow()
        session.commit()
        log.info("[%s]: %s", self.id, self.name)
        # from pprint import pprint
        # pprint(self.to_json())

    def to_row(self):
        data = OrderedDict()
        data['id'] = self.id
        data['source'] = self.source
        data['type'] = self.type
        data.update(self.to_name_dict())
        data['program'] = self.program
        data['function'] = self.function
        data['summary'] = self.summary
        data['listed_at'] = self.listed_at
        data['updated_at'] = self.updated_at
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self):
        data = self.to_row()
        data['aliases'] = [a.to_json() for a in self.aliases]
        data['addresses'] = [a.to_json() for a in self.addresses]
        data['identifiers'] = [i.to_json() for i in self.identifiers]
        data['nationalities'] = [n.to_json() for n in self.nationalities]
        data['births'] = [b.to_json() for b in self.births]
        return clean_obj(data)
