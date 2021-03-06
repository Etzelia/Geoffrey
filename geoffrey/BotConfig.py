import codecs
import configparser
import os


def create_config(config, path):
    config['Discord'] = {'Token': '',
                         'Status': '',
                         'Prefix': '?',
                         'Bot_Mod': '',
                         'Error_Users': ''
                         }
    config['SQL'] = {'Dialect+Driver': 'mysql+mysqldb',
                     'Username': '',
                     'Password': '',
                     'Host': '',
                     'Port': '',
                     'Database': ''
                     }
    config['Minecraft'] = {'Dynmap_Url': '',
                           'World_Name': '',
                           'North_Tunnel': 'North',
                           "East_Tunnel": 'South',
                           "South_Tunnel": 'East',
                           "West_Tunnel": 'West'
                           }
    config['Logging'] = {'Count': '7',
                         'Rotation_Duration': '1'
                         }
    config['Special Names'] = {}

    with open('{}/GeoffreyConfig.ini'.format(path), 'w') as configfile:
        config.write(configfile)


def read_config():
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.abspath(__file__))
    config.read_file(codecs.open("{}/GeoffreyConfig.ini".format(path), "r", "utf8"))

    if len(config.sections()) == 0:
        create_config(config, path)
        print("GeoffreyConfig.ini generated.")
        quit(0)

    return config


class Config:

    def __init__(self):
        try:
            self.config = read_config()
            self.engine_args = self.read_engine_arg()

            self.token = self.config['Discord']['Token']
            self.world_name = self.config['Minecraft']['World_Name']
            self.status = self.config['Discord']['Status']
            self.prefix = self.config['Discord']['Prefix']
            self.bot_mod = self.config['Discord']['Bot_Mod'].split(',')
            self.error_users = self.config['Discord']['Error_Users'].split(',')

            self.dynmap_url = self.config['Minecraft']['Dynmap_Url']
            self.north_tunnel = self.config['Minecraft']['North_Tunnel']
            self.east_tunnel = self.config['Minecraft']['East_Tunnel']
            self.south_tunnel = self.config['Minecraft']['South_Tunnel']
            self.west_tunnel = self.config['Minecraft']['West_Tunnel']


            self.count = int(self.config['Logging']['Count'])
            self.rotation_duration = int(self.config['Logging']['Rotation_Duration'])
            self.special_name_list = dict(self.config.items('Special Names'))
        except Exception as e:
            print("Invalid config file, missing {}.".format(e))
            quit(1)

    def read_engine_arg(self):
        driver = self.config['SQL']['Dialect+Driver']
        username = self.config['SQL']['Username']
        password = self.config['SQL']['Password']
        host = self.config['SQL']['Host']
        port = self.config['SQL']['Port']
        database_name = self.config['SQL']['Database']

        engine_args = '{}://{}:{}@{}:{}/{}?charset=utf8mb4&use_unicode=1'

        return engine_args.format(driver, username, password, host, port, database_name)

bot_config = Config()
