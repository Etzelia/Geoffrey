from unittest import TestCase

from Commands import *


class TestCommands(TestCase):
    def setUp(self):

        self.commands = Commands(bot_config.config['SQL']['test_args'])
        self.session = self.commands.interface.database.Session()
        self.commands.interface.database.clear_all(self.session)
        self.session.close()

    def test_get_player(self):
        session = self.commands.interface.database.Session()
        self.commands.interface.add_player(session, 'ZeroHD', discord_uuid='143072699567177728')

        player = self.commands.get_player(session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'ZeroHD')
        self.session.close()

    def test_register(self):
        self.commands.register('ZeroHD', '143072699567177728')

        player = self.commands.get_player(self.session, discord_uuid='143072699567177728')

        self.assertEqual(player.name, 'ZeroHD')

    def test_addbase(self):
        player_name = self.commands.register('ZeroHD', '143072699567177728')
        base = self.commands.add_base(0, 0, discord_uuid='143072699567177728')

        if player_name not in base:
            self.fail()
        else:
            pass

    def test_addshop(self):
        player_name = self.commands.register('ZeroHD', '143072699567177728')
        shop = self.commands.add_shop(0, 0, discord_uuid='143072699567177728')

        if player_name not in shop:
            self.fail()
        else:
            pass

    def test_addtunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        tunnel2 = self.commands.add_tunnel(bot_config.east_tunnel, 50, location_name='test_shop',
                                           discord_uuid='143072699567177728')

        if bot_config.east_tunnel not in tunnel2:
            self.fail()

        self.assertRaises(LocationHasTunnelError, self.commands.add_tunnel, bot_config.east_tunnel, 50,
                          location_name='test_shop', discord_uuid='143072699567177728')

    def test_find(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')
        self.commands.add_base(0, 0, 'heck', discord_uuid='143072699567177728')

        result = self.commands.find('zerohd')

        if ('frick' in result) & ('heck' in result):
            pass
        else:
            self.fail()

    def test_delete(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.delete('frick', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.find, 'zerohd')

    def test_findaround(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.find_around(0, 0)

        if 'frick' in result:
            pass
        else:
            self.fail()

    def test_additem(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, discord_uuid='143072699567177728')

        result = self.commands.add_item('dirt', 5, 5, None, discord_uuid='143072699567177728')

        if 'dirt' in result:
            pass
        else:
            self.fail()

        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.add_item('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_selling(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_item('cool', 5, 5, shop_name='frick', discord_uuid='143072699567177728')

        result = self.commands.selling('cool')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_info(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='frick', discord_uuid='143072699567177728')

        self.commands.add_tunnel(bot_config.north_tunnel, 50, location_name='frick', discord_uuid='143072699567177728')

        result = self.commands.info('frick')

        if bot_config.north_tunnel in result:
            pass
        else:
            self.fail()

    def test_tunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.add_tunnel(bot_config.south_tunnel, 50, None, discord_uuid='143072699567177728')

        result = self.commands.tunnel('ZeroHD')

        if bot_config.south_tunnel in result:
            pass
        else:
            self.fail()

    def test_edit_name(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_name('cool shop', 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('cool shop')

        if 'cool' in result:
            pass
        else:
            self.fail()

    def test_edit_pos(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_pos(500, 500, 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('test shop')

        if '500' in result:
            pass
        else:
            self.fail()

        self.commands.edit_pos(500, 500, None, discord_uuid='143072699567177728')

        if '500' in result:
            pass
        else:
            self.fail()

        self.commands.delete(name='test shop', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.edit_pos, 5, 5, None,
                          discord_uuid='143072699567177728')

    def test_edit_tunnel(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.edit_tunnel(bot_config.east_tunnel, 500, 'test shop', discord_uuid='143072699567177728')

        result = self.commands.info('test shop')

        if bot_config.east_tunnel in result:
            pass
        else:
            self.fail()

    def test_delete_item(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        self.commands.add_item('dirt', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')
        self.commands.add_item('wood', 5, 5, shop_name='test shop', discord_uuid='143072699567177728')

        result = self.commands.delete_item('dirt', None, discord_uuid='143072699567177728')

        if ('dirt' not in result) & ('wood' in result):
            pass
        else:
            self.fail()

        self.commands.add_shop(0, 0, shop_name='test shop2', discord_uuid='143072699567177728')
        self.assertRaises(EntryNameNotUniqueError, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')

        self.commands.delete('test shop', discord_uuid='143072699567177728')
        self.commands.delete('test shop2', discord_uuid='143072699567177728')

        self.assertRaises(LocationLookUpError, self.commands.delete_item, 'wood', None,
                          discord_uuid='143072699567177728')

    def test_me(self):
        self.commands.register('ZeroHD', '143072699567177728')
        self.commands.add_shop(0, 0, shop_name='test shop', discord_uuid='143072699567177728')

        result = self.commands.me(discord_uuid='143072699567177728')

        if 'test shop' in result:
            pass
        else:
            self.fail()

    def test_update_mc_uuid(self):
        self.commands.register('ZeroHD', '143072699567177728')

        self.commands.update_mc_uuid('0', '143072699567177728')

        self.assertRaises(PlayerNotFound, self.commands.add_shop, 0, 0, shop_name='test shop',
                          mc_uuid='fe7e84132570458892032b69ff188bc3')

    def test_update_mc_name(self):
        self.commands.register('ZeroHD', '143072699567177728')

        self.commands.update_mc_name('143072699567177728')

    def test_update_discord_uuid(self):
        self.commands.register('ZeroHD', '143072699567177728')

        self.commands.update_discord_uuid('143072699567177728', '0')

        self.assertRaises(PlayerNotFound, self.commands.add_shop, 0, 0, shop_name='test shop',
                          discord_uuid='143072699567177728')
