.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Contract Extended
=================


Goal
----
This module improve usability of the Analytic module.


Set Contracts to change their state to "To Renew" when remains less than X days to the end of the recurring contract
--------------------------------------------------------------------------------------------------------------------

Settings -> Technical -> Automation -> Automated Actions

Create::

    Conditions:
        Document Model: Analytic Account
        When ro Run: Based on Timed Conditions
        Filter: *Auto Invoice Creation
        Trigger Date: Date of Next Invoice
        Delay After Trigger Date: -X Days


    Actions:
        Server actions to run
            Action Name: Set Contract state to "To Renew"
            Base Model: Analytic Account
            Action To Do: Execute Python Code
            Python Code:
                obj.set_pending()



*Auto Invoice Creation::

    Filter Name: Auto Invoice Creation
    Model: Analytic Account
    Domain: [('recurring_invoices', '=', True)]


Settings -> Technical -> Automation -> Scheduled Actions -> Check Action Rules
shows the time of the next Action run.

.. note::  When debugging remember to set "last_run" in the Base Action Rule table
   to the day before now


Credits
=======

Contributors
------------

* Andrei Levin <andrei.levin@didotech.com>

Maintainer
----------

Didotech srl

To contribute to this module, please contact Didotech <info@didotech.com>
