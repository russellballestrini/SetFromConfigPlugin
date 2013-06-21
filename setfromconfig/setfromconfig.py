# Normally trac plugins do this: 
#   from trac.core import *
# but we feel this is bad practice

# We only raise TracError in this code
from trac.core import TracError

# All Trac plugins inherit from Component object
from trac.core import Component

# Interface registry
from trac.core import implements

# Interface which lets us create trac-admin commands
from trac.admin import IAdminCommandProvider

# Import each of the panels we would like to support
from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import ResolutionAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ComponentAdminPanel

# Trac suggests using printout over print
from trac.util.text import printout

# Dump changes dict to json
import json


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
        """return a dict of panel objects"""
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
        TODO: possibly move error checks out
        """
        if self.section_name not in self.config:
            msg = 'section %s not found in config' % self.section_name
            printout(msg)
            raise TracError(msg)

        config_options = {}
        for option_name in option_names:
            config_options[option_name] = self.config[self.section_name].getlist(option_name)

        
        if len(config_options['component']) > 0:
            # the component_owner must be set or TracError
            if self.config[self.section_name].get('component_owner') == '':
                msg = 'component present but component_owner missing in config'
                printout(msg)
                raise TracError(msg)

        return config_options
        

    def set_all_from_config(self):
        """Make database reflect trac.ini config, print any changes"""
        changes = {}

        panels = self._get_panels()

        config_options = self._get_config_options(panels.keys())

        for name,panel in panels.items():
            if len(config_options[name]) > 0:
                if name == 'component':
                    change = self._set_component_from_config(panel, config_options[name])
                else:
                    change = self._set_enum_from_config(panel, config_options[name])
                if change != {}:
                    changes[name] = change

        if changes != {}:
            printout(json.dumps({'changed':True, 'comment':changes}))


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
        todo: refactor and possibly intersection of lists
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

