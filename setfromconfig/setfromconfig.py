from trac.core import *
from trac.admin import IAdminCommandProvider
from trac.util.text import printout

# needed to dumps
import json

# import each of the panels we would like to support
from trac.ticket.admin import ComponentAdminPanel
from trac.ticket.admin import PriorityAdminPanel
from trac.ticket.admin import SeverityAdminPanel
from trac.ticket.admin import TicketTypeAdminPanel
from trac.ticket.admin import ResolutionAdminPanel

# Need the following to create list of [(component,owner),...]
from trac.ticket.model import Component as TicketComponent
from trac.util.translation import _

class JsonAdminCommandProvider(Component):
    implements(IAdminCommandProvider)
    
    # IAdminCommandProvider methods

    def get_admin_commands(self):

        # json lists
        yield ('priority json list', None,
               'Show possible ticket priorities in json',
               None, self._list_priority_in_json)
        yield ('severity json list', None,
               'Show possible ticket severities in json',
               None, self._list_severity_in_json)
        yield ('resolution json list', None,
               'Show possible ticket resolutions in json',
               None, self._list_resolution_in_json)
        yield ('ticket_type json list', None,
               'Show possible ticket types in json',
               None, self._list_ticket_type_in_json)
        yield ('component json list', None,
               'Show available components in json',
               None, self._list_component_in_json)

        # set from trac.ini config
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
        yield ('component set from config', None,
               'Set components from config',
               None, self._set_component_from_config)

    # the following methods list various enums in json

    def _list_priority_in_json(self):
        self._do_json_list('priority')
     
    def _list_severity_in_json(self):
        self._do_json_list('severity')
     
    def _list_resolution_in_json(self):
        self._do_json_list('resolution')
     
    def _list_ticket_type_in_json(self):
        self._do_json_list('ticket_type')
     
    def _list_component_in_json(self):
        self._do_json_list('component')
   
    # the following functions set various enums from config (trac.ini)
  
    def _set_priority_from_config(self):
        changes = self._do_set_from_config('priority')
        if changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
     
    def _set_severity_from_config(self):
        changes = self._do_set_from_config('severity')
        if changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
     
    def _set_resolution_from_config(self):
        changes = self._do_set_from_config('resolution')
        if changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
     
    def _set_ticket_type_from_config(self):
        changes = self._do_set_from_config('ticket_type')
        if changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
 
    def _set_component_from_config(self):
        changes = self._do_set_from_config('component')
        if changes: 
            printout(json.dumps({'changed':True, 'comment':changes}))
 

    def _get_panel(self, enum):
        """accept an enum, return panel or None"""
        if enum == 'priority':
            return PriorityAdminPanel(self.env)
        elif enum == 'severity':
            return SeverityAdminPanel(self.env)
        elif enum == 'resolution':
            return ResolutionAdminPanel(self.env)
        elif enum == 'ticket_type':
            return TicketTypeAdminPanel(self.env)
        elif enum == 'component':
            return ComponentAdminPanel(self.env)
        else:
            return None

    def _do_json_list(self, enum):
        """accept an enum, print current state in json"""
        panel = self._get_panel(enum)
        if panel:
            if enum == 'component':
                # stolen from trac.ticket.admin.py format: [(component,owner)]
                components = [(c.name, c.owner) for c in TicketComponent.select(self.env)], [_('Name'), _('Owner')]
                printout(json.dumps(components))
            else:
                printout(json.dumps(panel.get_enum_list()))
           
    def _do_set_from_config(self, enum):
        """
        Accept an enum
        Fetch items from config (trac.ini)
        Fetch items from database
        * Remove items from database not present in config (trac.ini)
        * Add items from config (trac.ini) not present in database
        Return dictionary of changes
        """
        # keep track of what we change
        changes = {}

        panel = self._get_panel(enum)
        if not panel:
            raise TracError(_('%s is not a valid panel') % enum )
            return changes 

        # TODO: what should the config section be named? 
        section = self.config['trac-admin-ini']
        if not section: # this is always true because
            # a section object is always created ...
            raise TracError(_('section not found'))
            return changes 

        # get config_items from trac.ini
        config_items = section.getlist(enum)

        # get current_items from Trac database
        if enum == 'component':
            current_items = panel.get_component_list()
        else:
            current_items = panel.get_enum_list()

        # remove items from database not present in config (trac.ini)
        for current_item in current_items:
            if current_item not in config_items:
                panel._do_remove(current_item) 
                changes[current_item] = 'Removed'
   
        # add items from config (trac.ini) not present in database
        for config_item in config_items:
            if config_item not in current_items:
                if enum == 'component':
                    panel._do_add(config_item,section.get('component_owner'))
                else: 
                    panel._do_add(config_item)
                changes[config_item] = 'Added'
   
        return changes

