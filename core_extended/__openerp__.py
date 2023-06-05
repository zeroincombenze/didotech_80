# -*- coding: utf-8 -*-
# © 2014-2017 Andrei Levin - Didotech srl (www.didotech.com)

{
    'name': 'Core Extended',
    'version': '4.0.5.0',
    'category': 'core',
    'description': """
Extends Core Functionality
==========================

    This module extends core functionality:
        color - add Color class

        odf_to_array - class that permits reading of Open Document spreadsheet

        file_manipulation - contains function that recognise Excel, Open Document and CSV documents
            and return them as list of rows

    """,
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base',
    ],
    #'external_dependancies': {
    #    'bin': [
    #        'postfix'
    #    ]
    #},
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}