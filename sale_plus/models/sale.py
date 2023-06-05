# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Didotech srl (http://www.didotech.com)
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

from openerp import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delay = fields.Float(required=False, default=1, invisible=True)
    name = fields.Text(string=_('Name'))
    description = fields.Text(_('Description'))

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        values = super(SaleOrderLine, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        if line.description:
            values['description'] = line.description
        return values
