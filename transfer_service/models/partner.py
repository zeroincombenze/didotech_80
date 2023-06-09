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

from openerp import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        if self._context.get('default_service_supplier_id'):
            values['parent_id'] = self._context['default_service_supplier_id']

        partner = super(ResPartner, self).create(values)

        if self._context.get('default_product_id'):
            product = self.env['product.product'].browse(self._context['default_product_id'])
            self.env['product.supplierinfo'].create({
                'name': partner.id,
                'product_tmpl_id': product.product_tmpl_id.id
            })

        return partner
