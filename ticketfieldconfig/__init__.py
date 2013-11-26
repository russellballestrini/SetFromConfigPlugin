from trac.core import TracError
from trac.core import Component
from trac.core import implements
from trac.admin import IAdminCommandProvider

from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import ResolutionAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ComponentAdminPanel

# Trac suggests using printout over print
from trac.util.text import printout

import json


class TicketFieldConfigCommand(Component):
    """
    The TicketFieldConfigCommand class is a Trac component (plugin) class which
    provides an admin command to Trac administrators for setting the standard
    ticket field values which are usually controlled through the admin web panel
    via the Trac config file.

    Once this plugin is enabled in may be used through the trac-admin command
    it exposes which is:

    trac-admin set fields from config

    Issuing this command will cause Trac to apply any changes neccessary to
    bring the current Trac standard ticket field values in line with what is
    defined declaratively in the Trac config file.
    """
    implements(IAdminCommandProvider)

    COMPONENT_FIELD_NAME = 'component'
    COMPONENT_OWNER_FIELD = 'component_owner'
    SECTION_NAME = 'ticket-field-config'

    def __init__(self):
        self.panels = {
           'priority': PriorityAdminPanel(self.env),
           'severity': SeverityAdminPanel(self.env),
           'resolution': ResolutionAdminPanel(self.env),
           'ticket_type': TicketTypeAdminPanel(self.env),
           'component': ComponentAdminPanel(self.env),
         }

    def get_admin_commands(self):
        """
        We have to implement get_admin_commands in order to expose the
        functionality of this plugin through the Trac admin tool.
        """
        yield ('set fields from config', None,
               """set all option values from configuration (trac.ini)

               priority, severity, resolution, ticket_type, and component""",
               None, self.set_fields_from_config)

    def set_fields_from_config(self):
        """
        Update the ticket field option values stored in the trac database with
        the values defined in the config (.ini) file.
        """
        changes = {}

        field_values = self._get_field_values()
        for field_name, values in field_values.items():
            field_changes = self._set_field_values_from_config(field_name,
                                                               values)
            if field_changes is not None:
                changes[field_name] = field_changes

        if changes != {}:
            printout(json.dumps({'changed': True, 'comment': changes}))

    def _get_field_values(self):
        """
        Get a lookup of the field values for each option in the relavent section
        of the config file.
        """
        field_values = {}

        self._check_section_present()
        self._check_component_owner()

        config_section = self.config[self.SECTION_NAME]

        for config_option in config_section:
            if config_option in self.panels:
                field_values[config_option] = config_section.getlist(
                                                                config_option)

        return field_values

    def _check_section_present(self):
        """
        Check that the section for this plugin is present.
        If not raise TracError exception.
        """
        if self.SECTION_NAME not in self.config:
            msg = 'Section %s not found in config' % self.SECTION_NAME
            raise TracError(msg)

    def _check_component_owner(self):
        """
        Check that if a component option exists in the relavent section of the
        config file a component_owner is also specified.
        """
        config_section = self.config[self.SECTION_NAME]

        if (len(config_section.get(self.COMPONENT_FIELD_NAME)) > 0 and
                config_section.get(self.COMPONENT_OWNER_FIELD) == ''):
            msg = "Components are present but component_owner \
                   is missing in config"
            raise TracError(msg)

    def _set_field_values_from_config(self, field_name, config_field_values):
        """
        Set the field values for given field name in the trac database based
        on what is defined in the config file adding and removing field values
        as neccessary.

        Returns a dictionary of the changes made during this process.
        """
        field_changes = None

        db_field_values = self._get_current_field_values(field_name)

        values_to_remove = set(db_field_values) - set(config_field_values)
        values_to_add = set(config_field_values) - set(db_field_values)

        self._remove_values_from_database(field_name, values_to_remove)
        self._add_values_to_database(field_name, values_to_add)

        diff_order = self._reorder_field_values(field_name, config_field_values)

        if len(values_to_add) > 0 or len(values_to_remove) > 0 or diff_order is not None:
            field_changes = {
                'Added'   : list(values_to_add),
                'Removed' : list(values_to_remove),
                'Reordered' : diff_order
            }

        return field_changes

    def _get_current_field_values(self, field_name):
        """
        The the current values for a given ticket field that exist in the
        Trac environment database.  For enum that are not components, this
        will be an ordered list by enum.value position.
        """
        if field_name == self.COMPONENT_FIELD_NAME:
            field_values = self.panels[field_name].get_component_list()
        else:
            # get_enum_list() returns a list of enums ORDER BY value.
            field_values = self.panels[field_name].get_enum_list()

        return field_values

    def _remove_values_from_database(self, field_name, field_values):
        """
        Remove a list of field values from the trac environement database.
        """
        for value in field_values:
            self.panels[field_name]._do_remove(value)

    def _add_values_to_database(self, field_name, field_values):
        """
        Add a list of field values to the trac environement database.
        """
        for value in field_values:
            if field_name == self.COMPONENT_FIELD_NAME:
                self.panels[field_name]._do_add(value,
                    self.config[field_name].get(self.COMPONENT_OWNER_FIELD))
            else:
                self.panels[field_name]._do_add(value)

    def get_enums_from_panel(self, panel_name):
        """
        Return a list of all enum objects for a given panel_name
        """
        return self.panels[panel_name]._enum_cls.select(self.env)

    def _reorder_values_in_db(self, panel_name, desired_order):
        """
        Order the field values by the order in the configuration file
        """
        enums = self.get_enums_from_panel(panel_name)

        for enum in enums:
            proper_position = desired_order.index(enum.name) + 1
            if enum.value != proper_position:
                enum.value = proper_position
                enum.update()

    def _reorder_field_values(self, panel_name, desired_field_order):
        diff_order = None
        if panel_name != self.COMPONENT_FIELD_NAME:
            db_field_order = self._get_current_field_values(panel_name)

            if desired_field_order != db_field_order:
                # we need to reorder enums
                diff_order = "{} -> {}".format(db_field_order, desired_field_order)
                self._reorder_values_in_db(panel_name, desired_field_order)
        return diff_order
        

