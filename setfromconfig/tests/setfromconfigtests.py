#!/usr/bin/env python

import unittest

from trac.test import EnvironmentStub

from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import ResolutionAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ComponentAdminPanel

from trac.core import TracError

from setfromconfig.setfromconfig import SetFromConfigAdminCommand

class SetFromConfigTestCase(unittest.TestCase):

    def setUp(self):
        """Create Trac env with default_data and our component enabled"""
        self.env = EnvironmentStub(default_data=True,
                                   enable=['setfromconfig.*'])

        # this is the default data that is in the test Trac database
        self.default = {
          'priority':['blocker', 'critical', 'major', 'minor', 'trivial'],
          'severity':[],
          'resolution': ['fixed','invalid','wontfix','duplicate','worksforme'],
          'ticket_type':['defect', 'enhancement', 'task'],
          'component':['component1', 'component2'],
        }

        # this is the new data we plan to put in configuration
        self.new = {
          'priority': ['P1','P2','P3'],
          'severity': ['High','Medium','Low'],
          'resolution': ['Fixed','Invalid','Cancelled'],
          'ticket_type': ['Bug','Release','Project'],
          'component': ['new/blog','new/site','old/blog','old/site'],
        }

    def priority_gets_set_successfully_test(self):
        """
        When we add custom priority enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac environments priority enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values 
        panel = PriorityAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['priority'])

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'priority',
                            ','.join(self.new['priority']))

        admin_command = SetFromConfigAdminCommand(self.env)

        # run our plugin
        admin_command.set_all_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['priority'])

    def severity_gets_set_successfully_test(self):
        """
        When we add custom severity enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac environments severity enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values 
        panel = SeverityAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['severity'])

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'severity',
                            ','.join(self.new['severity']))

        admin_command = SetFromConfigAdminCommand(self.env)

        # run our plugin
        admin_command.set_all_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['severity'])

    def resolution_gets_set_successfully_test(self):
        """
        When we add custom resolution enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac environments resolution enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values 
        panel = ResolutionAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['resolution'])

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'resolution',
                            ','.join(self.new['resolution']))

        admin_command = SetFromConfigAdminCommand(self.env)

        # run our plugin
        admin_command.set_all_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['resolution'])

    def ticket_type_gets_set_successfully_test(self):
        """
        When we add custom ticket_type enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac environments ticket_type enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values 
        panel = TicketTypeAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['ticket_type'])

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'ticket_type',
                            ','.join(self.new['ticket_type']))

        admin_command = SetFromConfigAdminCommand(self.env)

        # run our plugin
        admin_command.set_all_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['ticket_type'])

    def component_gets_set_successfully_test(self):
        """
        When we add custom component enum values to the config
        and call SetFromConfigAdminCommand.set_all_from_config()
        we expect the Trac environments component enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values 
        panel = ComponentAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_component_list(), self.default['component'])

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'component',
                            ','.join(self.new['component']))

        admin_command = SetFromConfigAdminCommand(self.env)

        # run our plugin
        admin_command.set_all_from_config()

        self.assertItemsEqual(panel.get_component_list(), self.new['component'])

    def test_unconfigured_options_do_not_alter_database(self):
        """missing section options should not alter the database"""
 
        panels = {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

        # Check the environment initially contains the default values.
        for name, panel in panels.items():
            if name == 'component':
                self.assertItemsEqual(
                  panel.get_component_list(),
                  self.default[name]
                )
            else:
                self.assertItemsEqual(
                  panel.get_enum_list(),
                  self.default[name]
                )

        # create the section, option, and values in configuration
        self.env.config.set('set-from-config-plugin', 'ticket_type',
                            ','.join(self.new['ticket_type']))

        # run our plugin
        admin_command = SetFromConfigAdminCommand(self.env)
        admin_command.set_all_from_config()

        # verify that specified configuration options altered database
        self.assertItemsEqual(
          panels['ticket_type'].get_enum_list(),
          self.new['ticket_type']
        )

        # verify that unspecified configuration options do not alter database
        for name, panel in panels.items():
            if name == 'ticket_type':
                continue # skipping because we changed this on purpose
            if name == 'component':
                self.assertItemsEqual(
                  panel.get_component_list(),
                  self.default[name]
                )
            else:
                self.assertItemsEqual(
                  panel.get_enum_list(),
                  self.default[name]
                )

        

    def test_missing_section(self):
        """missing section should not alter the database"""

        panels = {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

        # run our plugin
        admin_command = SetFromConfigAdminCommand(self.env)

        # TracError when [set-from-config-plugin] missing and admin cmd invoked
        self.assertRaises(TracError, admin_command.set_all_from_config)

        # verify that the present section but missing options does not alter db
        for name, panel in panels.items():
            if name == 'component':
                self.assertItemsEqual(
                  panel.get_component_list(),
                  self.default[name]
                )
            else:
                self.assertItemsEqual(
                  panel.get_enum_list(),
                  self.default[name]
                )
 
    def test_no_options_in_section(self):
        """present section but missing options should not alter the database"""

        panels = {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

        # create the section, but no options or values in configuration
        self.env.config.set('set-from-config-plugin','','')

        # run our plugin
        admin_command = SetFromConfigAdminCommand(self.env)
        admin_command.set_all_from_config()

        # verify that present section but missing options does not alter db
        for name, panel in panels.items():
            if name == 'component':
                self.assertItemsEqual(
                  panel.get_component_list(),
                  self.default[name]
                )
            else:
                self.assertItemsEqual(
                  panel.get_enum_list(),
                  self.default[name]
                )

    def test_invalid_option_in_section(self):
        """invalid options in section should not alter the database"""

        panels = {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

        # create the section with invalid option and values in configuration
        self.env.config.set('set-from-config-plugin','nintendo','mario,pacman')

        # run our plugin
        admin_command = SetFromConfigAdminCommand(self.env)
        admin_command.set_all_from_config()

        # verify that present section but missing options does not alter db
        for name, panel in panels.items():
            if name == 'component':
                self.assertItemsEqual(
                  panel.get_component_list(),
                  self.default[name]
                )
            else:
                self.assertItemsEqual(
                  panel.get_enum_list(),
                  self.default[name]
                )

