from unittest import TestCase

from DiscordHelperFunctions import get_nickname


class TestGet_nickname(TestCase):
    def test_get_nickname(self):
        class test:
            def __init__(self):
                self.display_name = 'dootb.in ꙩ ⃤'
                self.nick = 'dootb.in ꙩ ⃤'

        tmp = test()
        self.assertEqual(get_nickname(tmp), 'aeskdar')
