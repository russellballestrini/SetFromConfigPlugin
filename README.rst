SetFromConfigPlugin
===================

This is a Trac plugin which extends the trac-admin utility to provide the 'set from config' command.  This command makes it possibly to specify ticket priority, severity, resolution, ticket\_type, and component lists in the Trac config (trac.ini) instead of trac-admin commands.

We wrote this plugin because we needed a method to deploy and maintain Trac instances via configuration management like salt-stack or puppet.

This plugin will do nothing if the *[trac-admin-ini]* section is not created in trac.ini.

Here is an example configuration snippet:

.. code-block::

 [trac-admin-ini]

 priority = P1,P2,P3,P4,P90x
 severity = High,Medium,Low,Blocker
 resolution = fixed,wont-fix,cancelled,invalid,works-for-me,release,
 ticket_type = task,bug,project,ad-hoc,request,qa

 component_owner = username 
 component = webapp/www,webapp/blog,iphone/buttons,iphone/fonts

Warning:
 This plugin will remove items in your database if not present 
 in the configuration option list.

Note:
 All other options will be ignored.

Note:
 If a option is missing it is skipped.

