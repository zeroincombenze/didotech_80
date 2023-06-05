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
#    GNU Affero General Public License for more summary.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from Code128 import Code128
import base64
from StringIO import StringIO

import time
import math
from openerp.osv import osv
from openerp.report import report_sxw


class product_barcode_print(report_sxw.rml_parse):
    def get_taxed_price(self, cr, uid, product):
        return self.pool['account.tax'].compute_all(cr, uid, product.taxes_id, product.list_price, 1)['total_included']

    def _get_label_rows(self, form):
        data = []

        labels_in_row = form['labels_in_row']
        product_ids = form['product_ids']
        if not product_ids:
            return {}

        for product in self.pool['product.product'].browse(self.cr, self.uid, product_ids):
            label_row = []

            product_price = self.get_taxed_price(self.cr, self.uid, product)

            for row in range(0, labels_in_row):
                label_data = {
                    'name': product.name[:25],
                    'name2': len(product.name) > 25 and product.name[25:50] or '',
                    'default_code': product.default_code,
                    'price': product_price,
                }
                label_row.append(label_data)

            for product_row in range(int(math.ceil(float(form['qty']) / labels_in_row))):
                data.append(label_row)
            
        if data:
            return data
        else:
            return {}

    def _generate_barcode(self, barcode_string):  #, height, width):
        fp = StringIO()
        #generate('CODE39', barcode_string, writer=ImageWriter(), add_checksum=False, output=fp)
        #barcode_data = base64.b64encode(fp.getvalue())
        #return '<img style="width: 25mm;height: 7mm;" src="data:image/png;base64,%s" />'%(barcode_data)
        #return barcode_data

        Code128().getImage(barcode_string, path="/tmp/").save(fp, "PNG")
        barcode_data = base64.b64encode(fp.getvalue())
        return barcode_data

    def __init__(self, cr, uid, name, context):
        super(product_barcode_print, self).__init__(cr, uid, name, context=context)
        self.total = 0.0
        self.qty = 0.0
        self.total_invoiced = 0.0
        self.discount = 0.0
        self.total_discount = 0.0
        self.localcontext.update({
            'time': time,
            'getLabelRows': self._get_label_rows,
            'generateBarcode': self._generate_barcode
        })


class report_product_barcode_print(osv.AbstractModel):
    _name = 'report.product_barcode_qweb.report_product_barcode'
    _inherit = 'report.abstract_report'
    _template = 'product_barcode_qweb.report_product_barcode'
    _wrapped_report_class = product_barcode_print

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
