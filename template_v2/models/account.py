# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015-2016 Didotech srl (<http://www.didotech.com>)
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

from openerp import api, models, fields, _
import re


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    origin_orders = fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id', string=_('Orders'))

    @staticmethod
    def italian_number(number, precision=2, no_zero=False):
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        ## Requires Python >= 2.7:
        # before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        ## Works with Python 2.6:
        if precision:
            before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')
        else:
            before = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')[0]
            after = ''
        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))

        if no_zero and int(number) == float(number) or precision == 0:
            return sign + before
        else:
            return sign + before + ',' + after

    def italian_price(self, number, precision=2, no_zero=False):
        return '€ ' + self.env['account.invoice'].italian_number(number, precision, no_zero)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tax_digits = fields.Char(compute="get_tax_digits", string=_("Tax Digits"))

    # @api.one
    # def get_tax_digits(self):
    #     taxes = ', '.join([tax.name for tax in self.invoice_line_tax_id])
    #     if taxes:
    #         self.tax_digits = re.search(r'[0-9]+', taxes).group()
    #     else:
    #         self.tax_digits = ''

    @api.one
    def get_tax_digits(self):
        if self.invoice_line_tax_id:
            self.tax_digits = str(int(self.invoice_line_tax_id[0].amount * 100))
        else:
            self.tax_digits = ''

    def italian_price(self, number, precision=2, no_zero=False):
        return '€ ' + self.env['account.invoice'].italian_number(number, precision, no_zero)
