# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 - TODAY Denero Team. (<http://www.deneroteam.com>)
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
##############################################################################
from openerp.osv import orm, fields

class res_partner_title(orm.Model):
    _inherit = "res.partner.title"
    _order = "sequence"
    _columns = {
        'sequence': fields.integer('Sequence'),
    }
    _defaults = {
        'sequence': 1,
    }


class res_contact_function(orm.Model):
    _name = "res.contact.function"
    _description = "Contact Function"
    _order = "name"
    _columns = {
        'name': fields.char('Name', size=32),
    }

