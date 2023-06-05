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

from openerp import models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def children_search(self, parents, offset=0, limit=0, order=None, count=False):
        children = super(ProductCategory, self).search([('parent_id', 'in', parents.ids)])
        if children:
            return children + self.children_search(children, offset=offset, limit=limit, order=order, count=count)
        else:
            return children

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        categories = super(ProductCategory, self).search(args, offset=offset, limit=limit, order=order, count=count)
        if args and categories:
            categories += self.children_search(categories, offset=offset, limit=limit, order=order, count=count)
        return categories
