#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from trac.ticket.admin import PriorityAdminPanel

from trac.test import EnvironmentStub
import tempfile

from setfromconfig.setfromconfig import SetFromConfigAdminCommand


class SetFromConfigTestCase(unittest.TestCase):

    def priority_gets_set_successfully_test(self):
        """
        Given a Trac enviroment with our component enabled and the default
        priority enums, when we add custom priority enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac enviroments priority enums to be updated with our
        custom values and removal of the default values.
        """
        default_priorities = ['blocker', 'critical', 'major', 'minor',
                              'trivial']
        new_priorities = ['P1', 'P2', 'P3']

        # We need to setup a "test" trac enviroment with default settings
        self.env = EnvironmentStub(default_data=True,
                                   enable=['setfromconfig.*'])

        # We create an instance of the panel so we can check the priorities
        priority_panel = PriorityAdminPanel(self.env)

        # Check the enviroment initially contains the default values.
        self.assertItemsEqual(priority_panel.get_enum_list(),
                              default_priorities)

        self.env.config.set('set-from-config-plugin', 'priority',
                            ','.join(new_priorities))

        admin_command = SetFromConfigAdminCommand(self.env)

        admin_command.set_all_from_config()

        self.assertItemsEqual(priority_panel.get_enum_list(), new_priorities)


    def test_something(self):
        self.assertTrue(True)
