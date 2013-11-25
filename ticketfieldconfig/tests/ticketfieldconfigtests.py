#!/usr/bin/env python

import unittest

from trac.test import EnvironmentStub

from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import ResolutionAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ComponentAdminPanel

from trac.core import TracError

from ticketfieldconfig import TicketFieldConfigCommand

class TicketFieldConfigCommandTests(unittest.TestCase):

    def setUp(self):
        """Create Trac env with default_data and our component enabled"""
        self.env = EnvironmentStub(default_data=True,
                                   enable=['ticket-field-config.*'])

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
          'resolution': ['fixed','wontfix','invalid','duplicate','worksforme'],
          'ticket_type': ['Bug','Release','Project'],
          'component': ['new/blog','new/site','old/blog','old/site'],
        }

    def test_priority_set_successful(self):
        """
        When we add custom priority enum values to the config
        and call TicketFieldConfigCommand.set_fields_from_config()
        we expect the Trac environments priority enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values
        panel = PriorityAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['priority'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'priority',
                            ','.join(self.new['priority']))

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['priority'])

    def test_severity_set_successful(self):
        """
        When we add custom severity enum values to the config
        and call TicketFieldConfigCommand.set_fields_from_config()
        we expect the Trac environments severity enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values
        panel = SeverityAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['severity'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'severity',
                            ','.join(self.new['severity']))

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['severity'])

    def test_resolution_set_successful(self):
        """
        When we add custom resolution enum values to the config
        and call TicketFieldConfigCommand.set_fields_from_config()
        we expect the Trac environments resolution enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values
        panel = ResolutionAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['resolution'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'resolution',
                            ','.join(self.new['resolution']))

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['resolution'])

    def test_ticket_type_set_successful(self):
        """
        When we add custom ticket_type enum values to the config
        and call TicketFieldConfigCommand.set_fields_from_config()
        we expect the Trac environments ticket_type enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values
        panel = TicketTypeAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_enum_list(), self.default['ticket_type'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'ticket_type',
                            ','.join(self.new['ticket_type']))

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        self.assertItemsEqual(panel.get_enum_list(), self.new['ticket_type'])

    def test_component_set_successful(self):
        """
        When we add custom component enum values to the config
        and call TicketFieldConfigCommand.set_fields_from_config()
        we expect the Trac environments component enums to be updated with our
        custom values and removal of the default values.
        """
        # We create an instance of the panel so we can check existing values
        panel = ComponentAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_component_list(), self.default['component'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'component',
                            ','.join(self.new['component']))
        # create component_owner option
        self.env.config.set('ticket-field-config','component_owner','test')

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        self.assertItemsEqual(panel.get_component_list(), self.new['component'])

    def test_component_without_owner_is_trac_error(self):
        """component_owner must be specified"""
        # We create an instance of the panel so we can check existing values
        panel = ComponentAdminPanel(self.env)

        # Check the environment initially contains the default values.
        self.assertItemsEqual(panel.get_component_list(), self.default['component'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'component',
                            ','.join(self.new['component']))

        # we purposely forget to add component_owner to config
        # and run the plugin expecting a TracError
        admin_command = TicketFieldConfigCommand(self.env)
        self.assertRaises(TracError,admin_command.set_fields_from_config)


    def test_unconfigured_options_do_not_alter_database(self):
        """unconfigured options should not alter the database"""

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
        self.env.config.set('ticket-field-config', 'ticket_type',
                            ','.join(self.new['ticket_type']))

        # run our plugin
        admin_command = TicketFieldConfigCommand(self.env)
        admin_command.set_fields_from_config()

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

    def test_missing_section_is_trac_error(self):
        """a missing section should not alter the database"""

        panels = {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

        # run our plugin
        admin_command = TicketFieldConfigCommand(self.env)

        # TracError when [set-from-config-plugin] missing and admin cmd invoked
        self.assertRaises(TracError, admin_command.set_fields_from_config)

        # verify that the missing section does not alter db
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
        self.env.config.set('ticket-field-config','','')

        # run our plugin
        admin_command = TicketFieldConfigCommand(self.env)
        admin_command.set_fields_from_config()

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
        self.env.config.set('ticket-field-config','nintendo','mario,pacman')

        # run our plugin
        admin_command = TicketFieldConfigCommand(self.env)
        admin_command.set_fields_from_config()

        # verify that invalid options in section does not alter db
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
        panel = PriorityAdminPanel(self.env)

    def test_get_current_order(self):
        """
        Test that get_current_order() method returns a list of enum names
        ordered by enum values or empty list if panel_name is component
        """

        #create instance of our plugin
        admin_command = TicketFieldConfigCommand(self.env)

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'resolution',
                            ','.join(self.new['resolution']))

        # test before plugin, enum_names == self.default['resolution']
        enum_names = admin_command.get_current_order('resolution')
        self.assertEqual(enum_names, self.default['resolution'])

        # run our plugin
        admin_command.set_fields_from_config()

        # test after plugin, enum_names == self.new['resolution']
        enum_names = admin_command.get_current_order('resolution')
        self.assertEqual(enum_names, self.new['resolution'])

        # test panel_name == 'component' == []
        enum_names = admin_command.get_current_order('component')
        self.assertEqual(enum_names, [])

    def test_reorder_field_values(self):
        """
        test that field values are reordered to match configuration
        """
        # We create an instance of the panel so we can check existing values
        panel = ResolutionAdminPanel(self.env)

        # Check the environment initially contains the default values
        self.assertItemsEqual(panel.get_enum_list(), self.default['resolution'])

        # create the section, option, and values in configuration
        self.env.config.set('ticket-field-config', 'resolution',
                            ','.join(self.new['resolution']))

        admin_command = TicketFieldConfigCommand(self.env)

        # run our plugin
        admin_command.set_fields_from_config()

        # assert order was adjusted
        self.assertEqual(panel.get_enum_list(), self.new['resolution'])


