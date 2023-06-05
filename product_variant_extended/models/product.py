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

from openerp import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    all_product_variant_count = fields.Integer(compute='_get_all_product_variant_count',)

    @api.one
    def _get_all_product_variant_count(self):
        self.all_product_variant_count = len(self.env['product.product'].search([
            ('product_tmpl_id', '=', self.id),
            '|', ('active', '=', False), ('active', '=', True)
        ]))
