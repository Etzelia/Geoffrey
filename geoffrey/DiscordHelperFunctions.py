from itertools import zip_longest

from geoffrey.BotConfig import bot_config


def get_name(args):
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = None

    return name


def get_nickname(discord_user):
    if discord_user.nick is None:
        name = discord_user.display_name
    else:
        name = discord_user.nick

    if name in bot_config.special_name_list:
        return bot_config.special_name_list[name]
    else:
        return name


def get_args_dict(args):
    if len(args) != 0:
        return dict(zip_longest(*[iter(args)] * 2, fillvalue=" "))
    else:
        return {}
