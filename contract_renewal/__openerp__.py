# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

{
    'name': 'Card and Contract Management with automatic renewal',
    'version': '4.4.7.7',
    'category': 'Tools',
    'description': """
Create recurring contracts.
===========================

This module allows to create new contracts that can renew automatically.

NOTE: This module will work only with "Mission" documents. 
    """,
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'l10n_it_base',
        'sale',
    ],
    'external_dependancies': {
        'bin': [
            'postfix'
        ]
    },
    'data': [
        #'security/security.xml',
        'security/ir.model.access.csv',
        'contract_view.xml',
        'contract_workflow.xml',
        'partner_view.xml',
        'cron.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
