# -*- coding: utf-8 -*-
# © 2016-2017 Didotech srl (<http://www.didotech.com>).
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Broker Order',
    'version': '4.26.102.41',
    'category': 'Generic Modules/Service',
    "author": "Didotech SRL",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'product',
        'delivery'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
        'views/broker_view.xml',
        'views/broker_sequence.xml',
        'views/account_view.xml',
        'views/delivery_view.xml',
        'wizard/update_invoice_view.xml',
        'views/invoice_view.xml',
        'wizard/distribution_list_view.xml',
        'wizard/confirm_orders.xml',
        'wizard/import_purchase_order_view.xml',
        'cron.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': [
            'xlwt'
        ]
    }
}
