# -*- coding: utf-8 -*-
# #############################################################################
#
#    Copyright (C) 2015 Didotech srl (<http://www.didotech.com>)
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

from openerp import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    auto_create_task = fields.Boolean(_('Create Task Automatically'), help="Tick this option if you want to create a task automatically each time this product is sold")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    template_ids = fields.One2many('transfer.template', 'product_id', string=_('Transfer Templates'))


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def get_or_create(self, name):
        categories = self.search([('name', '=', name)])
        if categories:
            return categories[0]
        else:
            return self.create({
                'name': name,
                'type': 'normal'
            })
