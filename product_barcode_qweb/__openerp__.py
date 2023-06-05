# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (c) 2016 Didotech SRL (info at didotech.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Barcode QWeb',
    'version': '3.0.4.0',
    'category': 'Barcode',
    'sequence': 6,
    'summary': 'Barcode label for products',
    'description': """
Print Barcode label for products
================================

module creates a wizard under "Warehouse/Product" to select
products and prints the barcode labels.

This is intended for barcode label printers using rolls of labels.
Sample is configured to print three columns of labels, one row per page.
    """,
    'author': 'CYSFuturo S.A.',
    'images': [
    ],
    'depends': ['product'],
    'data': [
        'wizard/product_barcode_print.xml',
        'views/report_paperformat.xml',
        'report/product_barcode_qweb_report.xml',
        'views/report_product_barcode.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    #'qweb': ['static/src/xml/pos.xml'],
    'website': 'https://www.cysfuturo.com',
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
