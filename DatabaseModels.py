from sqlalchemy import Column, Integer, String, ForeignKey, Enum, create_engine, exists
from sqlalchemy.orm import relationship, column_property, sessionmaker
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
import enum
from difflib import SequenceMatcher

from BotErrors import *
from MinecraftAccountInfoGrabber import *

SQL_Base = declarative_base()


def check_similarity(a, b):
    ratio = SequenceMatcher(None, a, b).ratio()

    if (ratio > 0.6) or (a[0] == b[0]):
        return True
    else:
        return False


class GeoffreyDatabase:

    def __init__(self, engine_arg):
        self.engine = create_engine(engine_arg, echo=True, pool_recycle=3600, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        SQL_Base.metadata.create_all(self.engine)

    def clear_all(self, session):
        session.query(Tunnel).delete()
        session.query(ItemListing).delete()
        session.query(Shop).delete()
        session.query(Location).delete()
        session.query(Player).delete()
        session.commit()

    def add_object(self, session, obj):
        try:
            ret = session.query(exists().where(type(obj).id == obj.id))
            if ret:
                session.add(obj)
                session.commit()
        except IntegrityError:
            session.rollback()
            raise EntryNameNotUniqueError
        except DataError:
            session.rollback()
            raise DatabaseValueError
        except:
            session.rollback()

    def query_by_filter(self, session, obj_type, * args):
        filter_value = self.combine_filter(args)
        return session.query(obj_type).filter(filter_value).all()

    def delete_entry(self, session, obj_type, * args):

        filter_value = self.combine_filter(args)
        entry = session.query(obj_type).filter(filter_value)

        if entry.first() is not None:
            entry.delete()
        else:
            raise DeleteEntryError

        session.commit()

    def print_database(self, session, obj_type):
        obj_list = session.query(obj_type).all()

        s = ''

        for obj in obj_list:
                s = s + '\n' + obj.id
        return s

    def combine_filter(self, filter_value):
        return expression.and_(filter_value[0])


class TunnelDirection(enum.Enum):
    North = 'green'
    East = 'blue'
    South = 'red'
    West = 'yellow'

    def str_to_tunnel_dir(arg):
        arg = arg.lower()

        if check_similarity(TunnelDirection.North.value, arg):
            return TunnelDirection.North
        elif check_similarity(TunnelDirection.East.value, arg):
            return TunnelDirection.East
        elif check_similarity(TunnelDirection.South.value, arg):
            return TunnelDirection.South
        elif check_similarity(TunnelDirection.West.value, arg):
            return TunnelDirection.West
        else:
            raise InvalidTunnelError


class Dimension(enum.Enum):
    overworld = 'overworld'
    nether = 'nether'
    end = 'end'

    def str_to_dimension(arg):
        arg = arg.lower()
        if check_similarity(Dimension.overworld.value, arg):
            return Dimension.overworld
        elif check_similarity(Dimension.nether.value, arg):
            return Dimension.nether
        elif check_similarity(Dimension.end.value, arg):
            return Dimension.end
        else:
            raise InvalidDimError


class Player(SQL_Base):
    __tablename__ = 'Players'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mc_uuid = Column(String(128))
    discord_uuid = Column(String(128))
    name = Column(String(128))

    locations = relationship("Location", back_populates="owner", lazy='dynamic',
                             cascade="save-update, merge, delete, delete-orphan", single_parent=True)

    tunnels = relationship("Tunnel", back_populates="owner", lazy='dynamic',
                           cascade="save-update, merge, delete, delete-orphan")

    def __init__(self, name, discord_id=None):
        self.mc_uuid = grab_UUID(name)
        self.discord_uuid = discord_id
        self.name = name


class Tunnel(SQL_Base):
    __tablename__ = 'Tunnels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tunnel_number = Column(Integer)
    tunnel_direction = Column(Enum(TunnelDirection))
    owner_id = Column(Integer, ForeignKey('Players.id'))
    owner = relationship("Player", back_populates="tunnels", cascade="save-update, merge, delete")
    location_id = Column(Integer, ForeignKey('Locations.id', ondelete='CASCADE'))
    location = relationship("Location", back_populates="tunnel", lazy="joined")

    def __init__(self, owner, tunnel_color, tunnel_number, location=None):
        try:
            self.owner = owner
            self.location = location
            self.tunnel_direction = TunnelDirection.str_to_tunnel_dir(tunnel_color)
            self.tunnel_number = tunnel_number
        except (ValueError, IndexError):
            raise TunnelInitError

    def full_str(self):
        return 'Owner: **{}** Tunnel: **{}**'.format(self.owner.name, self.__str__())

    def __str__(self):
        return '{} {}'.format(self.tunnel_direction.value.title(), self.tunnel_number)


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True)
    x = Column(Integer)
    z = Column(Integer)

    tunnel = relationship("Tunnel",  uselist=False, cascade="all, delete-orphan")
    dimension = Column(Enum(Dimension))

    owner_id = Column(Integer, ForeignKey('Players.id', ondelete='CASCADE'))
    owner = relationship("Player", back_populates="locations", cascade="all, delete-orphan", single_parent=True)
    type = Column(String(128))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'Location'
    }

    def __init__(self, name, x, z, owner, dimension):
        try:
            self.name = name
            self.x = x
            self.z = z
            self.owner = owner

            if self.dimension is not None:
                self.dimension = self.dimension = Dimension.str_to_dimension(dimension)
            else:
                self.dimension = Dimension.overworld

        except (ValueError, IndexError):
            raise LocationInitError

    def dynmap_link(self):
        return '<http://24carrotcraft.com:8123/?worldname=season3&mapname=surface&zoom=4&x={}&y=65&z={}>'.\
            format(self.x, self.z)

    def pos_to_str(self):
        return '(x= {}, z= {}) in the {}'.format(self.x, self.z, self.dimension.value.title())

    def info_str(self):
        return "Name: **{}**, Type: **{}**, Owner: **{}** Position: **{}**".format(self.name, self.type,
                                                                                   self.owner.name, self.pos_to_str())

    def full_str(self):
        return self.__str__() + '\n' + self.dynmap_link()

    def __str__(self):
        if self.tunnel is not None:
            return "{}, Tunnel: **{}**".format(self.info_str(), self.tunnel)
        else:
            return self.info_str()


class Shop(Location):
    __tablename__ = 'Shops'
    shop_id = Column(Integer, ForeignKey('Locations.id', ondelete='CASCADE'), primary_key=True)
    name = column_property(Column(String(128)), Location.name)
    inventory = relationship('ItemListing', back_populates='shop', cascade='all, delete-orphan', lazy='dynamic')
    __mapper_args__ = {
        'polymorphic_identity': 'Shop',
    }

    def inv_to_str(self):

        if len(self.inventory.all()) != 0:
            inv = '\n**Inventory**:'
            str_format = '{}\n{}'

            for item in self.inventory:
                inv = str_format.format(inv, item.listing_str())

            return inv
        else:
            return ''

    def full_str(self):
        return Location.full_str(self) + self.inv_to_str()

    def __str__(self):
        return Location.__str__(self)

    def __init__(self, name, x, z, owner, dimension=None):
        Location.__init__(self, name, x, z, owner, dimension)


class ItemListing(SQL_Base):
    __tablename__ = 'Items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128))
    price = Column(Integer)
    amount = Column(Integer)

    shop_id = Column(Integer, ForeignKey('Shops.shop_id', ondelete='CASCADE'))
    shop = relationship("Shop", back_populates="inventory", single_parent=True)

    def __init__(self, name, price, amount, shop):
        self.name = name
        self.price = price
        self.amount = amount
        self.shop = shop

    def listing_str(self):
        return 'Item: **{}**, Price: **{}** for **{}**D'.format(self.name, self.amount, self.price)

    def __str__(self):
        return 'Shop: **{}**, {}'.format(self.shop.name, self.listing_str())


