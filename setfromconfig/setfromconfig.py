from trac.core import *
from trac.admin import IAdminCommandProvider
from trac.util.text import printout

# needed to dumps
import json

# import each of the panels we would like to support
from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import ResolutionAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ComponentAdminPanel


class SetFromConfigAdminCommand(Component):
    implements(IAdminCommandProvider)

    # section_name in config (trac.ini) that we will look for
    section_name = 'set-from-config-plugin'

    # IAdminCommandProvider methods

    def get_admin_commands(self):

        # set from trac.ini config
        #yield ('command regex', '<arg>',
        #       'trac-admin help text',
        #       self.tab_complete_callback, self.command_callback)
        yield ('set from config', None,
               """set all option values from configuration (trac.ini)

               priority, severity, resolution, ticket_type, and component""",
               None, self.set_all_from_config)

    def _get_panels(self):
        """return a dict of panels"""
        return {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        }

    def _get_config_options(self, option_names):
        """
        Accept list of valid option names, return a dict of option lists.
        TracError if plugin section not found.
        TracError if component option present and component_owner option missing
        """
        # make sure section exists in trac.ini, else error out
        if self.section_name not in self.config:
            msg = 'section %s not found in config' % self.section_name
            printout(msg)
            raise TracError(msg)

        # get all options, missing options will be set to empty lists
        config_options = {}
        for option_name in option_names:
            config_options[option_name] = self.config[self.section_name].getlist(option_name)

        # if component is not empty
        if config_options['component']:
            # then component_owner must be set, else TracError
            if not self.config[self.section_name].get('component_owner'):
                msg = 'component present but component_owner missing in config'
                printout(msg)
                raise TracError(msg)

        return config_options
        

    def set_all_from_config(self):
        """make database reflect trac.ini config"""
        # keep track of changes
        changes = {}
        changed = False

        panels = self._get_panels()

        config_options = self._get_config_options(panels.keys())

        for name,panel in panels.items():
            if name == 'component':
                change = self._set_component_from_config(panel, config_options[name])
            else:
                change = self._set_enum_from_config(panel, config_options[name])
            if change:
                changes[name] = change
                changed = True

        if changed:
            printout(json.dumps({'changed':changed, 'comment':changes}))


    def _set_enum_from_config(self, panel, config_items):
        """
        Accept panel object and config_items
        Fetch current_items from database
        * Remove items from database not present in config_items (trac.ini)
        * Add items from config_items (trac.ini) not present in database
        Return dictionary of changes
        """
        # keep track of what we change
        changes = {}

        # get current_items from Trac database
        current_items = panel.get_enum_list()

        # remove items from database not present in config (trac.ini)
        for current_item in current_items:
            if current_item not in config_items:
                panel._do_remove(current_item)
                changes[current_item] = 'Removed'

        # add items from config (trac.ini) not present in database
        for config_item in config_items:
            if config_item not in current_items:
                panel._do_add(config_item)
                changes[config_item] = 'Added'

        return changes

    def _set_component_from_config(self, panel, config_items):
        """
        similar to _set_enum_from_config however components
        have a different method to get list and also have owners
        """
        # keep track of what we change
        changes = {}

        # component_owner
        component_owner = self.config[self.section_name].get('component_owner')

        # database comonenets
        current_items = panel.get_component_list()

        # remove items from database not present in config (trac.ini)
        for current_item in current_items:
            if current_item not in config_items:
                panel._do_remove(current_item)
                changes[current_item] = 'Removed'

        # add items from config (trac.ini) not present in database
        for config_item in config_items:
            if config_item not in current_items:
                panel._do_add(config_item, component_owner)
                changes[config_item] = 'Added'

        return changes

