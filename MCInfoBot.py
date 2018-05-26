import enum
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker

TOKEN = ''
command_prefix = '?'
description = '''
Geoffrey started his life as inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your bases are.

Please respect Geoffrey, the bot is very sensitive.
'''

bad_error_message = 'OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The admins at our ' \
                        'headquarters are working VEWY HAWD to fix this! (Error in command {})'

engine = create_engine('sqlite:///:memory:', echo=True)
SQL_Base = declarative_base()

bot = commands.Bot(command_prefix=command_prefix, description=description, case_insensitive=True)


class DataBaseError(Exception):
    '''Base class for exceptions in this module.'''
    pass


class LocationInitError(DataBaseError):
    '''Error in initializing Location'''


class LocationLookUpError(DataBaseError) :
    '''Error in finding location in database'''


class TunnelDirection(enum.Enum):
    North = 'green'
    East = 'blue'
    South = 'red'
    West = 'yellow'


class Player(SQL_Base):
    __tablename__ = 'Players'

    id = Column(Integer, primary_key=True)
    in_game_name = Column(String)

    def __init__(self, name):
        self.in_game_name = name


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    tunnelNumber = Column(Integer)
    direction = Column(Enum(TunnelDirection))
    owner = Column(String, ForeignKey('Players.in_game_name'))

    def __init__(self, name, x, y, z, owner, args):
        try:
            self.name = name
            self.x = x
            self.y = y
            self.z = z
            self.owner = owner

            if len(args) > 0:
                self.direction = strToTunnelDirection(args[0])
                self.tunnelNumber = int(args[1])

        except (ValueError, IndexError):
            raise LocationInitError

    def pos_to_str(self):
        return '(x= {}, y= {}, z= {})'.format(self.x, self.y, self.z)

    def nether_tunnel_addr_to_str(self):
        return '{} {}'.format(self.direction.value.title(), self.tunnelNumber)

    def __str__(self):
        if self.direction is not None:
            return "Name: {}, Position: {}, Tunnel: {}".format(self.name, self.pos_to_str(), self.nether_tunnel_addr_to_str())
        else:
            return "Name: {}, Position: {}".format(self.name, self.pos_to_str())


SQL_Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def strToTunnelDirection(arg):
    arg = arg.lower()
    if (arg == TunnelDirection.North.value):
        return TunnelDirection.North
    elif (arg == TunnelDirection.East.value):
        return TunnelDirection.East
    elif (arg == TunnelDirection.South.value):
        return TunnelDirection.South
    elif (arg == TunnelDirection.West.value):
        return TunnelDirection.West
    else:
        raise ValueError


# Bot Commands ******************************************************************
@bot.event
async def on_ready():
    print('GeoffreyBot')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        error_str = 'Command not found, please use ?help to see all the commands this bot can do.'
    elif isinstance(error, commands.UserInputError) :
        error_str = 'Invalid syntax for {}, please read ?help {}.'.format(ctx.invoked_with, ctx.invoked_with)
    else:
        error_str = bad_error_message.format(ctx.invoked_with)
        print(error)

    await bot.send_message(ctx.message.channel, error_str)


@bot.command()
async def test():
    '''
    Checks if the bot is alive.
    '''
    await bot.say('I\'m here you ding dong')


@bot.command(pass_context=True)
async def addbase(ctx, name: str, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Add your base to the database.
     The tunnel address is optional.
     ?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color] [Tunnel Position]
    '''

    owner = Player(str(ctx.message.author.nick))
    base = Location(name, x_pos, y_pos, z_pos, owner.in_game_name, args)

    session.add(owner)
    session.add(base)

    await bot.say('{}, your base named {} located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def findbase(ctx, name: str):
    '''
    Finds a base in the database.
        ?findbase [Player name]
    '''

    base_list = session.query(Location).filter_by(owner=name).all()

    if len(base_list) != 0:
        base_string = base_list_string(base_list, '{} \n{}')

        await bot.say('{}, {} has {} base(s): \n {}'.format(ctx.message.author.mention, name, len(base_list),
                                                            base_string))
    else:
        await bot.say('{}, the player {} is not in the database'.format(ctx.message.author.mention, name))


def base_list_string(base_list, str_format):
    base_string = ''

    for base in base_list:
        base_string = str_format.format(base_string, base)

    return base_string

@bot.command(pass_context=True)
async def deletebase(ctx, name: str):
    '''
    Deletes a base from the database.
        ?deletebase [Base name]
    '''

    user = str(ctx.message.author.nick)
    base = session.query(Location).filter_by(owner=user, name=name)

    if base.first() is not None:
        base.delete()
        await bot.say('{}, your base named "{}" has been deleted.'.format(ctx.message.author.mention, name))
    else:
        await bot.say('{}, you do not have a base named "{}".'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def findbasearound(ctx, x_pos: int, z_pos: int, * args):
    '''
        Finds all the base around a certain point that are registered in the database
        The Radius argument defaults to 200 blocks if no value is given
            ?findbasearound [X Coordinate] [Z Coordinate] [Radius]
    '''

    radius = 200
    if len(args) > 0:
        try :
            radius = int(args[0])
        except ValueError:
            raise commands.UserInputError

    base_list = session.query(Location).filter(
        Location.x < x_pos + radius, Location.x > x_pos - radius, Location.z < z_pos + radius, Location.z > z_pos
        - radius).all()

    if len(base_list) != 0:
        base_string = base_list_string(base_list, '{} \n{}')

        await bot.say('{}, there are {} base(s) within {} 15 blocks of that point: \n {}'.format(
            ctx.message.author.mention, len(base_list), radius, base_string))
    else:
        await bot.say('{}, there are no base within {} of that point'.format(ctx.message.author.mention, radius))




# Bot Startup ******************************************************************

try:
    file = open('token.dat', 'r')
    TOKEN = file.read()
except FileNotFoundError:
    print('token.dat not found.')
except IOError:
    print('Error reading token.dat')

bot.run(TOKEN)
