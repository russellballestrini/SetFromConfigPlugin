TicketFieldConfigPlugin
========================

We wrote this Trac plugin because we needed a way to provision and maintain multiple Trac instances via configuration management like salt-stack or puppet.  This Trac plugin extends the trac-admin utility to provide the 'set fields from config' command.  

This command makes it possibly to declare ticket priority, severity, resolution, ticket\_type, and component options in the Trac config (trac.ini) instead of using the interactive admin web panel or trac-admin tools.

This plugin requires a section labeled *[ticket-field-config]* in the projects trac.ini.
If this section is missing, this plugin will not perform any changes.

The following shows a complete and valid configuration snippet:

.. code-block::

 [ticket-field-config]

 priority = P1,P2,P3,P4,P90x
 severity = High,Medium,Low,Blocker
 resolution = fixed,wont-fix,cancelled,invalid,works-for-me,release,
 ticket_type = task,bug,project,ad-hoc,request,qa

 component_owner = username 
 component = webapp/www,webapp/blog,iphone/buttons,iphone/fonts

If an option, like severity, is missing from the configuration section, it is skipped.
Any options added to this section that are not mentioned above will be ignored.

Warning:
 Always back up your database before trying new plugins.
 This plugin alters the Trac project's database to reflect the options listed.

 If an option entry is:

 * in the database but not in the configuration, it will be removed.
 * not in the database but is in the configuration, it will be added.
 * in the wrong "order" position, it will be corrected

Install
----------

create an egg from this source code

.. code-block:: bash

 python setup.py bdist_egg

copy the egg from dist into your Trac projects plugins directory

Tests
-------

This plugin has great test coverage.  : ) 

Before running tests you need to install trac.

Use a virtualenv, and run this command:

.. code-block:: bash

 pip install trac

Now run tests with this:

.. code-block:: bash

 nosetests


