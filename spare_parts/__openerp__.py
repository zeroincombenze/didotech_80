# -*- coding: utf-8 -*-
# © 2015-2017 Didotech srl (http://www.didotech.com).
# © Andrei Levin <andrei.levin@didotech.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Spare Parts',
    'version': '3.3.15.12',
    'category': 'Generic Modules/Service',
    'summary': 'Spare Parts Shop',
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'product',
        'sale',
        'product_quant'
    ],
    'data': [
        'views/product_view.xml',
        'views/sale_view.xml',
        'security/ir.model.access.csv',
        'views/stock_view.xml'
    ],
    'test': [],
    'installable': True,
    'active': False,
}
