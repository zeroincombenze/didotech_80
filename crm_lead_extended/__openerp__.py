# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2014 Didotech SRL (info at didotech.com)
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    'name': 'Module corrects a bug in crm_lead, when creating a partner. Parameter customer is True.',
    'version': '3.1.11.7',
    'category': 'Customer Relationship Management',
    'description': """
CRM Extended
============

    A module for crm. Extended by Didotech
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'crm',
        'l10n_base',
        'base_address_contacts',
        'sale'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'crm_lead_view.xml',
        'crm_lead_menu.xml',
        'crm_opportunity_view.xml',
        'crm_case_categ_view.xml',
        'crm_lead_sequence.xml',
        'crm_lead_data.xml',
    ],
    'installable': True,
    'active': False,
}
