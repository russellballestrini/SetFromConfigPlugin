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

"""
This plugin does nothing unless you create a section
in your trac.ini that called [trac-admin-ini]

Valid options for this section:

* priority = coma,separated,list,of,values
* severity = coma,separated,list,of,values
* resolution = coma,separated,list,of,values
* ticket_type = coma,separated,list,of,values
* component = coma,separated,list,of,values
* component_owner = username 

All other options will be ignored.
"""


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
        yield ('priority set from config', None,
               'Set ticket priorities from config',
               None, self._set_priority_from_config)
        yield ('severity set from config', None,
               'Set ticket severities from config',
               None, self._set_severity_from_config)
        yield ('resolution set from config', None,
               'Set ticket resolutions from config',
               None, self._set_resolution_from_config)
        yield ('ticket_type set from config', None,
               'Set ticket types from config',
               None, self._set_ticket_type_from_config)
        #yield ('component set from config', None,
        #       'Set components from config',
        #       None, self._set_component_from_config)
        #yield ('set all from config', None,
        #       'set all from config',
        #       None, self._set_all_from_config)

    # the following functions set various enums from config (trac.ini)
  
    def _set_priority_from_config(self):
        panel = PriorityAdminPanel(self.env)
        self._set_enum_from_config(panel)
     
    def _set_severity_from_config(self):
        panel = SeverityAdminPanel(self.env)
        self._set_enum_from_config(panel)
     
    def _set_resolution_from_config(self):
        panel = ResolutionAdminPanel(self.env)
        self._set_enum_from_config(panel)
     
    def _set_ticket_type_from_config(self):
        panel = TicketTypeAdminPanel(self.env)
        self._set_enum_from_config(panel)
 
    #def _set_component_from_config(self):
    #    panel = ComponentAdminPanel(self.env)
    #    current_items = panel.get_component_list()
    #                 #panel._do_add(config_item,section.get('component_owner'))
    #    changes = self._set_enum_from_config('component', panel)
    #    if changes: 
    #        printout(json.dumps({'changed':True, 'comment':changes}))
 

    def _get_config_items(self, option_name):
        """
        Accept an option_name, fetch and return config_items from config (trac.ini)
        Raise TracError and exit if section not found!
        TODO: Raise TracError and exit if option not found!
        """
        # check if section exists in trac.ini
        if self.section_name not in self.config:
            message = 'section %s not found in config' % self.section_name
            printout(message)
            raise TracError(_(message))

        # from config object, from section object, return list for enum
        return self.config[self.section_name].getlist(option_name)

           
    def _set_enum_from_config(self, panel, stdout=True):
        """
        Accept panel object
        Fetch config_items from config (trac.ini)
        Fetch current_items from database
        * Remove items from database not present in config (trac.ini)
        * Add items from config (trac.ini) not present in database
        Return dictionary of changes
        If stdout == True print changes as json
        """
        # get config_items from Trac config (trac.ini)
        enum_type = getattr(panel,'_command_type', panel._type)
        config_items = self._get_config_items(enum_type)

        # get current_items from Trac database
        current_items = panel.get_enum_list()

        # keep track of what we change
        changes = {}

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
        
        if stdout and changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
 
        return changes

