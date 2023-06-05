# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
#
#                       All Rights Reserved
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

from openerp import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_destination = fields.Many2one(
        'product.category', _('Destination'), domain="[('child_id', '=', False), ('spareparts', '=', True)]"
    )


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     @api.one
#     def action_check_spareparts_category(self):
#         from datetime import datetime
#         categories = self.env['product.category'].search([('parent_id', '=', False), ('spareparts', '=', True)])
#         print datetime.now()
#         self.check_spareparts_category(categories, spareparts=True)
#         categories = self.env['product.category'].search([('parent_id', '=', False), ('spareparts', '=', False)])
#         self.check_spareparts_category(categories, spareparts=False)
#         print datetime.now()
#
#     def check_spareparts_category(self, categories, spareparts):
#         for category in categories:
#             category.spareparts = spareparts
#             if category.child_id:
#                 self.check_spareparts_category(category.child_id, spareparts)
