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

from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import re


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_date = fields.Char(compute='get_order_date', store=False)
    proforma = fields.Boolean(string='Proforma')

    @api.one
    def get_order_date(self):
        order_date = datetime.strptime(self.date_order, DEFAULT_SERVER_DATETIME_FORMAT).date()
        self.order_date = order_date.strftime("%d.%m.%Y")

    def italian_price(self, number, precision=2, no_zero=False):
        return '€ ' + self.env['account.invoice'].italian_number(number, precision, no_zero)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_digits = fields.Char(compute="get_tax_digits", string=_("Tax Digits"))

    @api.one
    def get_tax_digits(self):
        taxes = ', '.join([tax.name for tax in self.tax_id])
        if taxes:
            self.tax_digits = re.search(r'[0-9]+', taxes).group()
        else:
            self.tax_digits = ''

    def italian_price(self, number, precision=2, no_zero=False):
        return '€ ' + self.env['account.invoice'].italian_number(number, precision, no_zero)
