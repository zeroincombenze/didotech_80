# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013-2015 Didotech SRL (info at didotech.com)
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
    'name': 'Module adds sub account for accounting in res.partner.',
    'version': '4.0.6.1',
    'category': 'Generic Modules',
    'description': """A module for res.partner. email's contacts of reference """,
    "author": "Didotech SRL.",
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'view/account_invoice_workflow.xml',
        'view/company_view.xml',
        'view/ref_sequences.xml',
        'view/res_partner_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'test': ['test/partner_create_modify.yml'],
    'installable': True,
    'active': False,
}
