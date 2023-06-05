# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Didotech srl (http://www.didotech.com)
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
    'name': 'Image Acquire',
    'version': '4.2.8.5',
    'category': 'Other',
    'description': """
        Receive images from external RPC call.
    """,
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'dt_web_tree_image',
        'project',
        'stock',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/select_destination.xml',
        'wizard/select_image.xml',
        'views/image_view.xml',
        'views/project_view.xml',
        'views/web_assets.xml',
        'views/stock_view.xml',
        'views/image_menu.xml'
    ],
    'qweb': [
        'static/src/xml/widget_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    # 'application': True,
    'auto_install': False,
    # 'external_dependencies': {
    #     'python': []
    # }
}
