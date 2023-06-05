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


class WizardSelectTemplate(models.TransientModel):
    _name = 'wizard.select.template'

    order_id = fields.Many2one('sale.order', _('Connect to existent Sale Order'), required=False)
    template_id = fields.Many2one('transfer.template', _('Template'), required=True)

    @api.multi
    def action_set_details(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        quotation_lines = map(lambda line: (0, 0, {
            'product_id': line.product_id.id,
            'itinerary_id': line.itinerary_id and line.itinerary_id.id or False,
            'template_line_id': line.id
        }), self.template_id.template_line_ids)
        quotation = self.env['wizard.create.quotation'].create({
            'template_id': self.template_id.id,
            'quotation_line_ids': quotation_lines,
            'order_id': self.order_id.id,
            'partner_id': self.order_id.partner_id.id,
            'descriptive_itinerary_id': self.template_id.descriptive_itinerary_id and self.template_id.descriptive_itinerary_id.id,
        })

        return {
            'name': _('Create Quotation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.create.quotation',
            'view_id': False,
            'target': 'new',
            'res_id': quotation.id,
            'context': "{'from_sale_order': True}"
        }
