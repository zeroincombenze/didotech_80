# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-2016 Didotech Srl - Odoo 7 and 8 migration by Matmoz d.o.o.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields
from openerp.tools.translate import _


class ResCountry(models.Model):
    _inherit = 'res.country'

    enable_province = fields.Boolean(_('Show Province?'))
    enable_region = fields.Boolean(_('Show Region?'))
    enable_state = fields.Boolean(_('Show State?'))
