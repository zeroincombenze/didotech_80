# -*- coding: utf-8 -*-
# © 2017 Didotech (www.didotech.com).

{
    'name': 'Mail Threads',
    'version': '3.3.11.2',
    'category': 'Tools',
    "author": "Didotech srl",
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
        'mail',
        'crm'
    ],
    'data': [
        'security/ir.model.access.csv',
        "views/mail_view.xml",
        "wizard/test_pattern_view.xml"
    ],
    'test': [],
    'installable': True,
    'auto_install': True,
}
