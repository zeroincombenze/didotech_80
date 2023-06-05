# -*- coding: utf-8 -*-

{
    'name': 'Bank Gateway Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Bank Gateway Implementation',
    'version': '1.0',
    'description': """Bank Gateway Payment Acquirer

    NOTE: This module was created to work with Vampi Store eCommerce. It was never tested as Odoo acquirer.

    """,
    'author': 'Didotech srl',
    'depends': [
        'payment'
    ],
    'data': [
        # 'views/gateway.xml',
        'views/gateway_acquirer.xml',
        # 'data/gateway.xml',
    ],
    'installable': True,
    'auto_install': True,
}
