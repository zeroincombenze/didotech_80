# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Didotech Srl (<http://www.didotech.com>)
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

from openerp import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    due_dates = fields.One2many('account.move.line', compute='_get_due_dates', string=_('Due Dates'))

    @api.one
    def _get_due_dates(self):
        if self.number:
            moves = self.env['account.move'].search([('name', '=', self.number)])
            if moves:
                partner_id = self.partner_id.parent_id and self.partner_id.parent_id.id or self.partner_id.id
                payments = self.env['account.move.line'].search([('move_id', '=', moves.id), ('partner_id', '=', partner_id), ('debit', '!=', 0.0)], order='date_maturity asc')
                self.due_dates = payments.ids
            else:
                self.due_dates = []
        else:
            self.due_dates = []
