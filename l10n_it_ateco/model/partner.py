# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract
#    (<http://abstract.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import models
from openerp import fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    ateco_category_ids = fields.Many2many(
        'ateco.category',
        'ateco_category_partner_rel',
        'partner_id',
        'ateco_id',
        'Ateco categories'
    )
