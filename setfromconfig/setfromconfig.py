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


class SetFromConfigAdminCommandProvider(Component):
    implements(IAdminCommandProvider)
   
    # section_name in config (trac.ini) that we will look for
    # TODO: what should the config section be named? 
    section_name = 'trac-admin-ini'
 
    # IAdminCommandProvider methods

    def get_admin_commands(self):

        # set from trac.ini config
        #yield ('command regex', '<arg>',
        #       'trac-admin help text',
        #       self.tab_complete_callback, self.command_callback)
        yield ('set from config', None,
               'set priority, severity, resolution, ticket_type, component, from trac.ini',
               None, self.set_all_from_config)

    def get_panels(self):
        """return a dict of panels"""
        return {
          'priority':    PriorityAdminPanel(self.env),
          'severity':    SeverityAdminPanel(self.env),
          'resolution':  ResolutionAdminPanel(self.env),
          'ticket_type': TicketTypeAdminPanel(self.env),
          'component':   ComponentAdminPanel(self.env),
        } 
 
    def set_all_from_config(self):
        """make database reflect trac.ini config"""
        # keep track of changes
        changes = {}
        changed = False

        panels = self.get_panels()
       
        for name,panel in panels.items():
            if name == "component":
                change = self._set_component_from_config(panel)
            else:
                change = self._set_enum_from_config(panel, name)
            if change:
                changes[name] = change
                changed = True

        if changed:
            printout(json.dumps({'changed':changed, 'comment':changes}))


    def _get_config_items(self, option_name):
        """
        Accept an option_name, fetch and return config_items from config (trac.ini)
        Raise TracError and exit if section not found!
        """
        # check if section exists in trac.ini
        if self.section_name not in self.config:
            message = 'section %s not found in config' % self.section_name
            printout(message)
            raise TracError(_(message))

        # from config object, from section object, return list for enum
        return self.config[self.section_name].getlist(option_name)
           
    def _set_enum_from_config(self, panel, enum_name):
        """
        Accept panel object
        Fetch config_items from config (trac.ini)
        Fetch current_items from database
        * Remove items from database not present in config (trac.ini)
        * Add items from config (trac.ini) not present in database
        Return dictionary of changes
        """
        # keep track of what we change
        changes = {}

        # get config_items from Trac config (trac.ini)
        config_items = self._get_config_items(enum_name)
        if not config_items:
            return changes

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

    def _set_component_from_config(self, panel):
        """
        similar to _set_enum_from_config however components
        have a different method to get list and also have owners
        """
        # keep track of what we change
        changes = {}

        # get config_items (components) from Trac config (trac.ini)
        config_items = self._get_config_items('component')
        if not config_items:
            return changes

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

