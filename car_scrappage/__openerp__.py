# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015-2017 Didotech srl (<http://www.didotech.com>)
#
#                       All Rights Reserved
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
# #############################################################################

{
    'name': 'Vertical For Car Scrappage',
    'version': '3.5.11.12',
    'category': 'Generic Modules/Service',
    'summary': 'Spare Parts Shop',
    'description': """
Verticalization For Car Scrappage
=================================

    """,
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'project',
        'survey'
    ],
    'data': [
        'security/ir.model.access.csv',
        'project_data.xml',
        'views/project_view.xml',
        'views/company_view.xml'
    ],
    'test': [],
    'installable': True,
    'active': False,
}
