# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (http://www.didotech.com)
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
    'name': 'Sale Plus',
    'version': '4.1.2.4',
    'category': 'Sales Management',
    'description': """
        Modify Sale Order Line in a separate view
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'sale',
        'sale_stock'
    ],
    'data': [
        "views/sale_view.xml",
        # 'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {}
}
