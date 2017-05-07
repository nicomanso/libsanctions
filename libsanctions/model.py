import countrynames
from dalet import parse_date
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Unicode, Integer, DateTime
from sqlalchemy import ForeignKey

from libsanctions.config import DATABASE_URI

Base = declarative_base()
engine = create_engine(DATABASE_URI)
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)


class NameMixIn(object):
    name = Column(Unicode, nullable=True)
    first_name = Column(Unicode, nullable=True)
    second_name = Column(Unicode, nullable=True)
    third_name = Column(Unicode, nullable=True)
    last_name = Column(Unicode, nullable=True)


class Alias(Base, NameMixIn):
    """An alternate name for an indivdual."""
    __tablename__ = 'alias'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Unicode, ForeignKey('data.id'))
    quality = Column(Unicode, nullable=True)
    type = Column(Unicode, nullable=True)

    def __init__(self, entity_id, name=None):
        self.entity_id = entity_id
        self.name = name


class Address(Base):
    """An address associated with an entity."""
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    entity_id = Column(Unicode, ForeignKey('data.id'))
    text = Column(Unicode, nullable=True)
    note = Column(Unicode, nullable=True)
    street = Column(Unicode, nullable=True)
    street_2 = Column(Unicode, nullable=True)
    postal_code = Column(Unicode, nullable=True)
    city = Column(Unicode, nullable=True)
    region = Column(Unicode, nullable=True)
    country_name = Column(Unicode, nullable=True)
    country_code = Column(Unicode, nullable=True)

    @property
    def country(self):
        return self.country_code or self.country_name

    @country.setter
    def country(self, name):
        self.country_name = name
        self.country_code = countrynames.to_code(name)

    def __init__(self, entity_id):
        self.entity_id = entity_id


class Entity(Base, NameMixIn):
    """A company or person that is subject to a sanction."""
    __tablename__ = 'data'

    TYPE_ENTITY = 'entity'
    TYPE_INDIVIDUAL = 'individual'

    id = Column(Unicode, primary_key=True)
    type = Column(Unicode, nullable=True)
    summary = Column(Unicode, nullable=True)
    function = Column(Unicode, nullable=True)
    program = Column(Unicode, nullable=True)
    listed_at = Column(Unicode, nullable=True)
    updated_at = Column(Unicode, nullable=True)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, id):
        self.id = id
        self.timestamp = datetime.utcnow()

    @validates('listed_at')
    @validates('updated_at')
    def validate_date(self, key, date):
        return parse_date(date)

    def create_alias(self, name=None):
        alias = Alias(self.id, name=name)
        session.add(alias)
        return alias

    def create_address(self):
        address = Address(self.id)
        session.add(address)
        return address

    def save(self):
        self.timestamp = datetime.utcnow()
        session.commit()
