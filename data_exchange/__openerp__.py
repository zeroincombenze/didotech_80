# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>)
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
# #############################################################################

{
    'name': 'Data Exchange',
    'version': '4.0.1.2',
    'category': 'Generic Modules/Service',
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        # 'views/exchange_view.xml'
        'views/partner_view.xml',
        'wizard/export_partner.xml'
    ],
    'test': [],
    'installable': True,
    'active': False,
    'external_dependancies': {
        'python': [
            'jsonrpclib'
        ]
    },
}
